from pathlib import Path

import pytest

from src.ingestion import cargar_documento

DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"

# (nombre_archivo, formato_esperado, categoria_esperada)
CASOS = [
    ("rh_manual_onboarding.docx", "docx", "Recursos Humanos"),
    ("financiero_estado_resultados.xlsx", "xlsx", "Financiero y Contable"),
    ("operacional_manual_procedimientos.pdf", "pdf", "Operacional"),
    ("estrategico_roadmap_2026.pptx", "pptx", "Estratégico"),
    ("legal_politica_privacidad.md", "md", "Legal y Compliance"),
    ("marketing_tabla_precios.csv", "csv", "Marketing y Comercial"),
    ("datos_api_interna.json", "json", "Datos y Sistemas"),
    ("id_estudio_mercado.pdf", "pdf", "Investigación y Desarrollo"),
    ("comunicacion_newsletter_junio2026.html", "html", "Comunicación Interna"),
]


@pytest.mark.parametrize("nombre_archivo, formato_esperado, categoria_esperada", CASOS)
def test_loader_extrae_texto_y_metadata(nombre_archivo, formato_esperado, categoria_esperada):
    ruta = DOCS_DIR / nombre_archivo
    documento = cargar_documento(ruta)

    assert documento.texto.strip() != ""
    assert documento.metadata == {
        "nombre_archivo": nombre_archivo,
        "categoria": categoria_esperada,
        "formato": formato_esperado,
    }


def test_formato_no_soportado_lanza_error():
    with pytest.raises(ValueError):
        cargar_documento(DOCS_DIR / "inexistente.txt")
