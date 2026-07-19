import re

from src.embeddings import CohereProvider
from src.embeddings.provider_base import LLMProvider
from src.vectorstore import FAISSVectorStore

from .prompts import SYSTEM_PROMPT

_proveedor: LLMProvider | None = None
_vectorstore: FAISSVectorStore | None = None

_PATRON_FUENTES_USADAS = re.compile(r"^FUENTES_USADAS\s*:\s*(.*)$", re.MULTILINE | re.IGNORECASE)


def _obtener_vectorstore() -> FAISSVectorStore:
    global _proveedor, _vectorstore
    if _vectorstore is None:
        _proveedor = CohereProvider()
        _vectorstore = FAISSVectorStore.cargar(_proveedor)
    return _vectorstore


def _formatear_contexto(chunks: list[dict]) -> str:
    bloques = []
    for chunk in chunks:
        meta = chunk["metadata"]
        encabezado = f"[Fuente: {meta['nombre_archivo']} — categoría: {meta['categoria']}]"
        bloques.append(f"{encabezado}\n{chunk['texto']}")
    return "\n\n".join(bloques)


def _extraer_fuentes_usadas(respuesta_cruda: str) -> tuple[str, list[str]]:
    """Separa la línea FUENTES_USADAS del texto visible y devuelve los
    nombres que el modelo dice haber usado (sin validar todavía)."""
    match = _PATRON_FUENTES_USADAS.search(respuesta_cruda)
    if not match:
        return respuesta_cruda.strip(), []

    nombres = [n.strip().rstrip(".") for n in match.group(1).split(",") if n.strip()]
    texto_visible = _PATRON_FUENTES_USADAS.sub("", respuesta_cruda).strip()
    return texto_visible, nombres


def responder(pregunta: str, top_k: int = 6) -> dict:
    # top_k=6 (no 4): con este corpus, chunks que solo MENCIONAN un tema
    # (p. ej. el manual operacional refiriéndose a "la tabla de precios")
    # a veces superan en score al chunk que de verdad tiene el dato (la fila
    # de precios), tanto por similitud semántica como léxica. k=4 los dejaba
    # fuera del contexto; k=6 los incluye de forma consistente en las
    # pruebas del Paso 4. Ver FAISSVectorStore.search (boost léxico) para el
    # resto del ajuste.
    vectorstore = _obtener_vectorstore()
    chunks = vectorstore.search(pregunta, k=top_k)

    contexto = _formatear_contexto(chunks)
    prompt = SYSTEM_PROMPT + pregunta

    respuesta_cruda = _proveedor.generar(prompt, contexto)
    respuesta_visible, nombres_citados = _extraer_fuentes_usadas(respuesta_cruda)

    # Whitelist: un nombre solo cuenta como fuente si el LLM lo citó en
    # FUENTES_USADAS Y además existe realmente en la metadata de los chunks
    # recuperados. Si el modelo inventa un nombre que no estaba en el
    # contexto, se descarta en vez de colarse como cita.
    nombres_disponibles = {chunk["metadata"]["nombre_archivo"] for chunk in chunks}
    fuentes = [nombre for nombre in dict.fromkeys(nombres_citados) if nombre in nombres_disponibles]

    return {
        "respuesta": respuesta_visible,
        "fuentes": fuentes,
        "chunks_usados": [chunk["texto"] for chunk in chunks],
    }
