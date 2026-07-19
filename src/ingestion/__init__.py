from pathlib import Path

from . import (
    csv_loader,
    docx_loader,
    html_loader,
    json_loader,
    md_loader,
    pdf_loader,
    pptx_loader,
    xlsx_loader,
)
from .base import DocumentoIngestado

_LOADERS_POR_EXTENSION = {
    ".pdf": pdf_loader.load,
    ".docx": docx_loader.load,
    ".xlsx": xlsx_loader.load,
    ".pptx": pptx_loader.load,
    ".md": md_loader.load,
    ".csv": csv_loader.load,
    ".json": json_loader.load,
    ".html": html_loader.load,
    ".htm": html_loader.load,
}


def cargar_documento(ruta: str | Path) -> DocumentoIngestado:
    ruta = Path(ruta)
    loader = _LOADERS_POR_EXTENSION.get(ruta.suffix.lower())
    if loader is None:
        raise ValueError(f"Formato no soportado: {ruta.suffix!r} ({ruta.name})")
    return loader(ruta)


__all__ = ["DocumentoIngestado", "cargar_documento"]
