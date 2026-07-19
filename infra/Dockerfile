# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app

# Dependencias primero para aprovechar el cache de capas de Docker.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código + documentos fuente + índice FAISS ya construido.
#
# El índice (data/vectorstore) se construye ANTES de este build, en local,
# con `python -m src.vectorstore.build_index` (requiere COHERE_API_KEY).
# A propósito NO se construye durante `docker build`: eso obligaría a pasar
# la API key como build-arg, y quedaría grabada en el historial de capas de
# la imagen para siempre. Las credenciales solo entran en runtime vía
# `docker run --env-file .env` (nunca hardcodeadas aquí).
#
# Si data/vectorstore no existe todavía, correr primero:
#   python -m src.vectorstore.build_index
COPY src/ ./src/
COPY docs/ ./docs/
COPY data/ ./data/

EXPOSE 8501

CMD ["streamlit", "run", "src/app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
