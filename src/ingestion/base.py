from dataclasses import dataclass
from pathlib import Path

# Basado en la tabla de docs/ del README: cada archivo empieza con un
# prefijo que identifica su categoría de negocio.
CATEGORIAS_POR_PREFIJO = {
    "rh": "Recursos Humanos",
    "financiero": "Financiero y Contable",
    "operacional": "Operacional",
    "estrategico": "Estratégico",
    "legal": "Legal y Compliance",
    "marketing": "Marketing y Comercial",
    "datos": "Datos y Sistemas",
    "id": "Investigación y Desarrollo",
    "comunicacion": "Comunicación Interna",
}

CATEGORIA_DESCONOCIDA = "Sin categoría"


@dataclass
class DocumentoIngestado:
    texto: str
    metadata: dict


def inferir_categoria(nombre_archivo: str) -> str:
    prefijo = nombre_archivo.split("_")[0].lower()
    return CATEGORIAS_POR_PREFIJO.get(prefijo, CATEGORIA_DESCONOCIDA)


def construir_metadata(ruta: Path, formato: str) -> dict:
    return {
        "nombre_archivo": ruta.name,
        "categoria": inferir_categoria(ruta.stem),
        "formato": formato,
    }
