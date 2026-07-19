from pathlib import Path

import openpyxl

from .base import DocumentoIngestado, construir_metadata


def _indice_fila_encabezado(filas: list[tuple]) -> int | None:
    """La primera fila con más de una celda no vacía se asume encabezado
    (filas anteriores con una sola celda suelen ser títulos de la hoja)."""
    for indice, fila in enumerate(filas):
        if sum(valor is not None for valor in fila) > 1:
            return indice
    return None


def load(ruta: str | Path) -> DocumentoIngestado:
    ruta = Path(ruta)
    libro = openpyxl.load_workbook(ruta, data_only=True)

    # Cada fila de datos se guarda como su propio bloque (separado por línea
    # en blanco) para que el chunker la trate como una unidad independiente,
    # en vez de mezclar varias filas en un mismo chunk.
    bloques = []
    for hoja in libro.worksheets:
        filas = list(hoja.iter_rows(values_only=True))
        indice_encabezado = _indice_fila_encabezado(filas)
        prefijo_hoja = f"## Hoja: {hoja.title}"

        if indice_encabezado is None:
            for fila in filas:
                valores = [str(v) for v in fila if v is not None]
                if valores:
                    bloques.append(f"{prefijo_hoja}\n" + " | ".join(valores))
            continue

        titulo = [str(v) for fila in filas[:indice_encabezado] for v in fila if v is not None]
        prefijo = prefijo_hoja + (f"\n{' '.join(titulo)}" if titulo else "")

        encabezado = [str(v) if v is not None else "" for v in filas[indice_encabezado]]
        for fila in filas[indice_encabezado + 1 :]:
            pares = [
                f"{encabezado[i]}: {valor}"
                for i, valor in enumerate(fila)
                if valor is not None and i < len(encabezado) and encabezado[i]
            ]
            if pares:
                bloques.append(f"{prefijo}\n" + ", ".join(pares))

    texto = "\n\n".join(bloques).strip()
    return DocumentoIngestado(texto=texto, metadata=construir_metadata(ruta, "xlsx"))
