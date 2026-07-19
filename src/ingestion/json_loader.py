import json
from pathlib import Path

from .base import DocumentoIngestado, construir_metadata


def _aplanar(valor, prefijo: str = "") -> list[str]:
    if isinstance(valor, dict):
        lineas = []
        for clave, sub_valor in valor.items():
            ruta_clave = f"{prefijo}.{clave}" if prefijo else str(clave)
            lineas.extend(_aplanar(sub_valor, ruta_clave))
        return lineas

    if isinstance(valor, list):
        lineas = []
        for indice, item in enumerate(valor):
            lineas.extend(_aplanar(item, f"{prefijo}[{indice}]"))
        return lineas

    return [f"{prefijo}: {valor}"]


def load(ruta: str | Path) -> DocumentoIngestado:
    ruta = Path(ruta)
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    texto = "\n".join(_aplanar(datos))
    return DocumentoIngestado(texto=texto, metadata=construir_metadata(ruta, "json"))
