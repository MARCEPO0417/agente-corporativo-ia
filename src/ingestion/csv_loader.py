from pathlib import Path

import pandas as pd

from .base import DocumentoIngestado, construir_metadata


def load(ruta: str | Path) -> DocumentoIngestado:
    ruta = Path(ruta)
    df = pd.read_csv(ruta)

    lineas = [" | ".join(df.columns.astype(str))]
    for _, fila in df.iterrows():
        lineas.append(" | ".join(str(v) for v in fila.values))

    texto = "\n".join(lineas).strip()
    return DocumentoIngestado(texto=texto, metadata=construir_metadata(ruta, "csv"))
