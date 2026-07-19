import sys
from pathlib import Path

# Asegura que la raíz del repo esté en sys.path al correr `streamlit run src/app/main.py`.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st

from src.rag import responder

st.title("Agente Corporativo — NovaTech Solutions")
st.caption("Preguntas sobre los documentos internos de la empresa (RAG con Cohere).")

if "historial" not in st.session_state:
    st.session_state.historial = []

for turno in st.session_state.historial:
    with st.chat_message("user"):
        st.write(turno["pregunta"])
    with st.chat_message("assistant"):
        st.write(turno["respuesta"])
        if turno["fuentes"]:
            with st.expander("Ver fuentes"):
                st.caption(", ".join(turno["fuentes"]))

pregunta = st.chat_input("Escribe tu pregunta...")

if pregunta:
    with st.chat_message("user"):
        st.write(pregunta)

    with st.chat_message("assistant"):
        respuesta = None
        fuentes = []
        try:
            with st.spinner("Consultando los documentos..."):
                resultado = responder(pregunta)
            respuesta = resultado["respuesta"]
            fuentes = resultado["fuentes"]
            st.write(respuesta)
            if fuentes:
                with st.expander("Ver fuentes"):
                    st.caption(", ".join(fuentes))
        except Exception as error:
            st.error(
                f"No se pudo obtener una respuesta en este momento ({error}). "
                "Intenta de nuevo en unos segundos."
            )

    if respuesta is not None:
        st.session_state.historial.append(
            {"pregunta": pregunta, "respuesta": respuesta, "fuentes": fuentes}
        )
