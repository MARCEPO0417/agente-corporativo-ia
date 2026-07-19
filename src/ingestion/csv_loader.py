from pathlib import Path

import pandas as pd

from .base import DocumentoIngestado, construir_metadata


def load(ruta: str | Path) -> DocumentoIngestado:
    ruta = Path(ruta)
    df = pd.read_csv(ruta)

    # Prefijo derivado del nombre del archivo: cada fila queda aislada como
    # su propio chunk (ver chunking.py), y sin esto pierde el contexto de a
    # qué documento/tema pertenece (p. ej. una fila nunca menciona "NovaFlow"
    # por sí sola aunque el archivo completo sí sea sobre NovaFlow).
    contexto_documento = ruta.stem.replace("_", " ")

    # "columna: valor" por fila (en vez de tabla con "|") para que el texto
    # se parezca más a lenguaje natural y embeba mejor semánticamente.
    bloques = []
    for _, fila in df.iterrows():
        pares = [f"{columna}: {valor}" for columna, valor in fila.items() if pd.notna(valor)]
        bloques.append(f"## {contexto_documento}\n" + ", ".join(pares))

    texto = "\n\n".join(bloques).strip()
    return DocumentoIngestado(texto=texto, metadata=construir_metadata(ruta, "csv"))
