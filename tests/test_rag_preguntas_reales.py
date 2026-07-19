"""Validación bloqueante del Paso 4: 10 preguntas reales contra el RAG completo.

Cubre las 9 categorías de docs/ (8 preguntas legítimas + 1 pregunta cuyo
tema vive en un documento que ya tiene otra pregunta legítima), mezclando
dificultad (directas, que combinan 2 datos del mismo documento, y una con
fraseo coloquial/indirecto), más 1 pregunta "trampa" (cercana pero no
documentada) y 1 completamente fuera de dominio.

No usa mocks: pega contra Cohere de verdad y contra el índice FAISS real
construido sobre docs/. Requiere COHERE_API_KEY en .env y el índice ya
construido (python -m src.vectorstore.build_index).
"""

from dataclasses import dataclass

import pytest

from src.rag import responder

RECHAZO_ESPERADO = "No encuentro esa información en la documentación disponible."


@dataclass
class CasoPrueba:
    id: str
    tipo: str  # directa | combinada | coloquial | trampa | fuera_de_dominio
    pregunta: str
    documento_esperado: str | None  # None => se espera rechazo (fuentes vacías)
    fragmentos_esperados: tuple[str, ...] = ()  # substrings que deben aparecer (case-insensitive)


CASOS = [
    CasoPrueba(
        id="legal_arco",
        tipo="directa",
        pregunta="¿Cuánto tiempo tiene el equipo de Legal para responder una solicitud de derechos ARCO?",
        documento_esperado="legal_politica_privacidad.md",
        fragmentos_esperados=("15 días",),
    ),
    CasoPrueba(
        id="operacional_sev1",
        tipo="directa",
        pregunta="¿Cuál es el tiempo de respuesta objetivo cuando hay un incidente SEV-1?",
        documento_esperado="operacional_manual_procedimientos.pdf",
        fragmentos_esperados=("15 minutos",),
    ),
    CasoPrueba(
        id="api_limite_business",
        tipo="directa",
        pregunta="¿Cuántas solicitudes por hora puede hacer un cliente del plan Business según la API interna de NovaFlow?",
        documento_esperado="datos_api_interna.json",
        fragmentos_esperados=("5000",),
    ),
    CasoPrueba(
        id="newsletter_clientes_q2",
        tipo="directa",
        pregunta="¿Cuántos clientes empresariales nuevos se sumaron en el segundo trimestre según el boletín interno de junio?",
        documento_esperado="comunicacion_newsletter_junio2026.html",
        fragmentos_esperados=("142",),
    ),
    CasoPrueba(
        id="rh_remoto_antiguedad",
        tipo="combinada",
        pregunta=(
            "Si soy colaborador remoto y llevo 3 años en la empresa, "
            "¿qué beneficios adicionales tengo por mi modalidad de trabajo y por mi antigüedad?"
        ),
        documento_esperado="rh_manual_onboarding.docx",
        fragmentos_esperados=("30", "conectividad"),
    ),
    CasoPrueba(
        id="financiero_ebit_primer_mes_positivo",
        tipo="combinada",
        pregunta=(
            "¿Cuál fue la utilidad operativa (EBIT) total del año 2025 y en qué mes del año "
            "pasó a ser positiva por primera vez?"
        ),
        documento_esperado="financiero_estado_resultados.xlsx",
        fragmentos_esperados=("30", "junio"),
    ),
    CasoPrueba(
        id="estrategico_okrs_q3",
        tipo="combinada",
        pregunta=(
            "Según los OKRs de Q3 2026, ¿a cuántos clientes activos quiere llegar NovaTech y "
            "a qué porcentaje de churn mensual apunta ese mismo trimestre?"
        ),
        documento_esperado="estrategico_roadmap_2026.pptx",
        fragmentos_esperados=("4200", "2.6%"),
    ),
    CasoPrueba(
        id="marketing_precio_coloquial",
        tipo="coloquial",
        pregunta=(
            "Necesito un plan con soporte prioritario por chat y correo, 250 GB de almacenamiento "
            "y proyectos ilimitados. ¿Cuánto me costaría al mes?"
        ),
        documento_esperado="marketing_tabla_precios.csv",
        fragmentos_esperados=("29",),
    ),
    CasoPrueba(
        id="trampa_licencia_paternidad",
        tipo="trampa",
        pregunta="¿Cuántos días de licencia de paternidad ofrece NovaTech Solutions a los nuevos padres?",
        documento_esperado=None,
    ),
    CasoPrueba(
        id="fuera_de_dominio_capital_francia",
        tipo="fuera_de_dominio",
        pregunta="¿Cuál es la capital de Francia?",
        documento_esperado=None,
    ),
]


@pytest.mark.parametrize("caso", CASOS, ids=[c.id for c in CASOS])
def test_pregunta_real(caso: CasoPrueba):
    resultado = responder(caso.pregunta)

    print(f"\n{'=' * 90}")
    print(f"[{caso.tipo.upper()}] {caso.pregunta}")
    print("-" * 90)
    print("RESPUESTA:", resultado["respuesta"])
    print("FUENTES:", resultado["fuentes"])

    if caso.documento_esperado is None:
        assert resultado["respuesta"].strip() == RECHAZO_ESPERADO, (
            f"Se esperaba el rechazo exacto, pero el modelo respondió: {resultado['respuesta']!r}"
        )
        assert resultado["fuentes"] == [], f"No debería citar fuentes en un rechazo: {resultado['fuentes']}"
        return

    assert resultado["respuesta"].strip() != RECHAZO_ESPERADO, "El modelo rechazó una pregunta que sí tiene respuesta en docs/"
    assert caso.documento_esperado in resultado["fuentes"], (
        f"Se esperaba {caso.documento_esperado} en fuentes, se obtuvo: {resultado['fuentes']}"
    )

    # Sin comas para no fallar por formato (5000 vs 5,000)
    respuesta_normalizada = resultado["respuesta"].lower().replace(",", "")
    for fragmento in caso.fragmentos_esperados:
        assert fragmento.lower().replace(",", "") in respuesta_normalizada, (
            f"No se encontró '{fragmento}' en la respuesta: {resultado['respuesta']!r}"
        )
