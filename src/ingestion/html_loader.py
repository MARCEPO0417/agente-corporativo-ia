from pathlib import Path

from bs4 import BeautifulSoup

from .base import DocumentoIngestado, construir_metadata


def load(ruta: str | Path) -> DocumentoIngestado:
    ruta = Path(ruta)
    contenido = ruta.read_text(encoding="utf-8")
    sopa = BeautifulSoup(contenido, "lxml")

    for etiqueta in sopa(["script", "style"]):
        etiqueta.decompose()

    texto = sopa.get_text(separator="\n")
    texto = "\n".join(linea.strip() for linea in texto.splitlines() if linea.strip())
    return DocumentoIngestado(texto=texto, metadata=construir_metadata(ruta, "html"))
