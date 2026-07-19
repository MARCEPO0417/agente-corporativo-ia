from pathlib import Path

import openpyxl

from .base import DocumentoIngestado, construir_metadata


def load(ruta: str | Path) -> DocumentoIngestado:
    ruta = Path(ruta)
    libro = openpyxl.load_workbook(ruta, data_only=True)

    bloques = []
    for hoja in libro.worksheets:
        lineas = [f"## Hoja: {hoja.title}"]
        for fila in hoja.iter_rows(values_only=True):
            valores = [str(v) for v in fila if v is not None]
            if valores:
                lineas.append(" | ".join(valores))
        if len(lineas) > 1:
            bloques.append("\n".join(lineas))

    texto = "\n\n".join(bloques).strip()
    return DocumentoIngestado(texto=texto, metadata=construir_metadata(ruta, "xlsx"))
