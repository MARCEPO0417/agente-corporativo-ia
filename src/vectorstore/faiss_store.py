import json
import os
import re
import time
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path

import faiss
import numpy as np
from cohere.errors.too_many_requests_error import TooManyRequestsError
from dotenv import load_dotenv

from src.embeddings.provider_base import LLMProvider
from src.ingestion.base import DocumentoIngestado

from .chunking import chunkear_texto

load_dotenv()

_RAIZ_PROYECTO = Path(__file__).resolve().parent.parent.parent

TAMANO_CHUNK_TOKENS = 500
OVERLAP_TOKENS = 50
TAMANO_LOTE_EMBED = 90  # margen bajo el límite de ~96 textos por llamada de Cohere
MAX_REINTENTOS = 5
ESPERA_INICIAL_SEGUNDOS = 2

# Boost léxico sumado al score de coseno: los chunks cortos/tabulares (ej.
# filas de una tabla de precios) a veces embeben débil semánticamente aunque
# contengan literalmente las palabras de la pregunta. Sin esto, ese tipo de
# contenido puede quedar fuera del top-k pese a ser la respuesta correcta.
PESO_LEXICO = 0.25
_STOPWORDS = {
    "que", "los", "las", "del", "con", "por", "para", "una", "uno", "como",
    "cual", "cuales", "cuanto", "cuantos", "cuanta", "cuantas", "tiene",
    "tienen", "son", "esta", "este", "estos", "estas", "donde", "cuando",
    "sobre", "segun", "cada", "desde", "hasta", "entre", "sin", "mas", "muy",
    "the", "and", "for",
}


def _normalizar(texto: str) -> set[str]:
    """Tokeniza, quita tildes y recorta a 4 caracteres (stemming simple) para
    tolerar plurales/variantes (plan/planes, precio/precios)."""
    texto = unicodedata.normalize("NFKD", texto.lower())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    palabras = re.findall(r"[a-z0-9]+", texto)
    return {p[:4] for p in palabras if len(p) > 3 and p not in _STOPWORDS}


def _score_lexico(palabras_query: set[str], texto_chunk: str) -> float:
    if not palabras_query:
        return 0.0
    interseccion = palabras_query & _normalizar(texto_chunk)
    return len(interseccion) / len(palabras_query)


@dataclass
class ChunkAlmacenado:
    texto: str
    metadata: dict


def _embed_con_reintento(proveedor: LLMProvider, textos: list[str], input_type: str) -> list[list[float]]:
    espera = ESPERA_INICIAL_SEGUNDOS
    for intento in range(1, MAX_REINTENTOS + 1):
        try:
            return proveedor.embed(textos, input_type=input_type)
        except TooManyRequestsError:
            if intento == MAX_REINTENTOS:
                raise
            time.sleep(espera)
            espera *= 2
    raise RuntimeError("No se pudo obtener embeddings tras varios reintentos")


class FAISSVectorStore:
    """Wrapper de FAISS: chunking + embeddings (vía LLMProvider) + persistencia + búsqueda."""

    def __init__(self, proveedor: LLMProvider, ruta_indice: str | Path | None = None):
        self._proveedor = proveedor

        ruta = Path(ruta_indice or os.getenv("VECTORSTORE_PATH", "./data/vectorstore"))
        # Rutas relativas se resuelven contra la raíz del repo, no contra el
        # cwd del proceso (Streamlit u otros entrypoints pueden arrancar
        # desde un directorio distinto y romper "./data/vectorstore").
        self._ruta_indice = ruta if ruta.is_absolute() else _RAIZ_PROYECTO / ruta

        self._indice: faiss.Index | None = None
        self._chunks: list[ChunkAlmacenado] = []

    def indexar_documentos(self, documentos: list[DocumentoIngestado]) -> None:
        self._chunks = []
        for documento in documentos:
            fragmentos = chunkear_texto(documento.texto, TAMANO_CHUNK_TOKENS, OVERLAP_TOKENS)
            for indice_chunk, fragmento in enumerate(fragmentos):
                metadata_chunk = {
                    **documento.metadata,
                    "chunk_index": indice_chunk,
                    "total_chunks": len(fragmentos),
                }
                self._chunks.append(ChunkAlmacenado(texto=fragmento, metadata=metadata_chunk))

        if not self._chunks:
            raise ValueError("No se generaron chunks: la lista de documentos está vacía o sin texto")

        textos = [chunk.texto for chunk in self._chunks]
        vectores: list[list[float]] = []
        for inicio in range(0, len(textos), TAMANO_LOTE_EMBED):
            lote = textos[inicio : inicio + TAMANO_LOTE_EMBED]
            vectores.extend(_embed_con_reintento(self._proveedor, lote, "search_document"))

        matriz = np.array(vectores, dtype="float32")
        faiss.normalize_L2(matriz)
        self._indice = faiss.IndexFlatIP(matriz.shape[1])
        self._indice.add(matriz)
        self._guardar_en_disco()

    def search(self, query: str, k: int = 4) -> list[dict]:
        if self._indice is None:
            self._cargar_desde_disco()

        vector_query = _embed_con_reintento(self._proveedor, [query], "search_query")
        matriz_query = np.array(vector_query, dtype="float32")
        faiss.normalize_L2(matriz_query)

        # Se rankea contra TODos los chunks (dataset pequeño, barato) para
        # poder combinar el score de coseno con el boost léxico antes de
        # cortar a los top-k finales.
        total_chunks = len(self._chunks)
        distancias, indices = self._indice.search(matriz_query, total_chunks)

        palabras_query = _normalizar(query)
        candidatos = []
        for score_coseno, idx in zip(distancias[0], indices[0]):
            if idx == -1:
                continue
            chunk = self._chunks[idx]
            score_final = float(score_coseno) + PESO_LEXICO * _score_lexico(palabras_query, chunk.texto)
            candidatos.append((score_final, chunk))

        candidatos.sort(key=lambda par: par[0], reverse=True)

        resultados = []
        for score_final, chunk in candidatos[:k]:
            resultados.append({"texto": chunk.texto, "metadata": chunk.metadata, "score": score_final})
        return resultados

    @classmethod
    def cargar(cls, proveedor: LLMProvider, ruta_indice: str | Path | None = None) -> "FAISSVectorStore":
        instancia = cls(proveedor, ruta_indice)
        instancia._cargar_desde_disco()
        return instancia

    def _guardar_en_disco(self) -> None:
        self._ruta_indice.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self._indice, str(self._ruta_indice / "index.faiss"))
        payload = [asdict(chunk) for chunk in self._chunks]
        (self._ruta_indice / "chunks.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def _cargar_desde_disco(self) -> None:
        ruta_index = self._ruta_indice / "index.faiss"
        ruta_chunks = self._ruta_indice / "chunks.json"
        if not ruta_index.exists() or not ruta_chunks.exists():
            raise FileNotFoundError(
                f"No hay índice guardado en {self._ruta_indice}. Ejecuta indexar_documentos() primero."
            )
        self._indice = faiss.read_index(str(ruta_index))
        datos = json.loads(ruta_chunks.read_text(encoding="utf-8"))
        self._chunks = [ChunkAlmacenado(**d) for d in datos]
