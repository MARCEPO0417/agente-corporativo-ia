import os

import cohere
from dotenv import load_dotenv

from .provider_base import LLMProvider

load_dotenv()

EMBED_MODEL = "embed-multilingual-v3.0"
# "command-r" fue descontinuado por Cohere en sept. 2025; command-a-03-2025
# es el modelo de chat de propósito general vigente (default endpoint chat).
CHAT_MODEL = "command-a-03-2025"


class CohereProvider(LLMProvider):
    """Adapter de Cohere (trial) para embeddings + generación."""

    def __init__(self, api_key: str | None = None):
        api_key = api_key or os.getenv("COHERE_API_KEY")
        if not api_key:
            raise ValueError(
                "COHERE_API_KEY no está definida. Agrégala a tu archivo .env "
                "(ver .env.example)."
            )
        self._cliente = cohere.Client(api_key)

    def embed(self, textos: list[str], input_type: str = "search_document") -> list[list[float]]:
        """input_type: 'search_document' al indexar, 'search_query' al buscar."""
        respuesta = self._cliente.embed(
            texts=textos,
            model=EMBED_MODEL,
            input_type=input_type,
        )
        return respuesta.embeddings

    def generar(self, prompt: str, contexto: str) -> str:
        """`contexto` se usa como preamble (instrucciones + chunks recuperados),
        `prompt` es la pregunta del usuario."""
        respuesta = self._cliente.chat(
            model=CHAT_MODEL,
            message=prompt,
            preamble=contexto,
            temperature=0.2,
        )
        return respuesta.text
