from pathlib import Path

import pdfplumber

from .base import DocumentoIngestado, construir_metadata


def load(ruta: str | Path) -> DocumentoIngestado:
    ruta = Path(ruta)
    paginas = []
    with pdfplumber.open(ruta) as pdf:
        for pagina in pdf.pages:
            paginas.append(pagina.extract_text() or "")
    texto = "\n\n".join(p.strip() for p in paginas if p.strip())
    return DocumentoIngestado(texto=texto, metadata=construir_metadata(ruta, "pdf"))
