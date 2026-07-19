from pathlib import Path

from src.embeddings import CohereProvider
from src.ingestion import cargar_documento

from .faiss_store import FAISSVectorStore

DOCS_DIR = Path(__file__).resolve().parent.parent.parent / "docs"


def construir_indice() -> FAISSVectorStore:
    documentos = [cargar_documento(ruta) for ruta in sorted(DOCS_DIR.iterdir()) if ruta.is_file()]
    proveedor = CohereProvider()
    store = FAISSVectorStore(proveedor)
    store.indexar_documentos(documentos)
    return store


if __name__ == "__main__":
    store = construir_indice()
    print(f"Índice construido con {len(store._chunks)} chunks en {store._ruta_indice}")
