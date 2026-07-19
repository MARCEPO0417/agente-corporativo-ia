from pathlib import Path

import markdown
from bs4 import BeautifulSoup

from .base import DocumentoIngestado, construir_metadata


def load(ruta: str | Path) -> DocumentoIngestado:
    ruta = Path(ruta)
    contenido_md = ruta.read_text(encoding="utf-8")
    html = markdown.markdown(contenido_md, extensions=["tables"])
    texto = BeautifulSoup(html, "lxml").get_text(separator="\n")
    texto = "\n".join(linea.strip() for linea in texto.splitlines() if linea.strip())
    return DocumentoIngestado(texto=texto, metadata=construir_metadata(ruta, "md"))
