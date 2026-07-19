"""Validación manual de OCIGenAIProvider: compara el pipeline RAG completo
usando OCI Generative AI vs Cohere, reutilizando la MISMA función
responder() (RAG core) y las mismas 10 preguntas de
test_rag_preguntas_reales.py — así la comparación prueba que el adapter
pattern funciona (swap de proveedor sin tocar el resto del pipeline), no
una reimplementación paralela de la lógica de RAG.

No es un test de pytest con asserts: requiere credenciales OCI reales,
construye un índice FAISS nuevo (separado del índice Cohere, en
data/vectorstore_oci/) y hace ~20 llamadas reales de embeddings + chat.
Se ejecuta a mano:

    python tests/test_oci_provider_manual.py
"""

from pathlib import Path

from src.embeddings import CohereProvider, OCIGenAIProvider
from src.ingestion import cargar_documento
from src.rag.core import responder
from src.vectorstore import FAISSVectorStore
from tests.test_rag_preguntas_reales import CASOS

DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"
RUTA_INDICE_OCI = Path(__file__).resolve().parent.parent / "data" / "vectorstore_oci"


def construir_indice_oci() -> tuple[OCIGenAIProvider, FAISSVectorStore]:
    documentos = [cargar_documento(ruta) for ruta in sorted(DOCS_DIR.iterdir()) if ruta.is_file()]
    proveedor = OCIGenAIProvider()
    store = FAISSVectorStore(proveedor, ruta_indice=RUTA_INDICE_OCI)
    store.indexar_documentos(documentos)
    return proveedor, store


def main() -> None:
    print(f"Construyendo índice OCI en {RUTA_INDICE_OCI} (no toca el índice Cohere)...")
    proveedor_oci, store_oci = construir_indice_oci()
    print(f"Índice OCI listo: {len(store_oci._chunks)} chunks.\n")

    proveedor_cohere = CohereProvider()
    store_cohere = FAISSVectorStore.cargar(proveedor_cohere)

    for caso in CASOS:
        print("=" * 100)
        print(f"[{caso.tipo.upper()}] {caso.pregunta}")
        print("-" * 100)

        resultado_cohere = responder(caso.pregunta, proveedor=proveedor_cohere, vectorstore=store_cohere)
        resultado_oci = responder(caso.pregunta, proveedor=proveedor_oci, vectorstore=store_oci)

        print("COHERE :", resultado_cohere["respuesta"])
        print("  fuentes:", resultado_cohere["fuentes"])
        print()
        print("OCI    :", resultado_oci["respuesta"])
        print("  fuentes:", resultado_oci["fuentes"])
        print()


if __name__ == "__main__":
    main()
