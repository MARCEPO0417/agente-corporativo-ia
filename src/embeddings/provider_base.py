from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Contrato común para proveedores de embeddings + generación.

    Permite intercambiar el proveedor (Cohere hoy, OCI Generative AI mañana)
    sin tocar el resto del pipeline RAG.
    """

    @abstractmethod
    def embed(self, textos: list[str]) -> list[list[float]]:
        """Devuelve un vector de embedding por cada texto de entrada."""

    @abstractmethod
    def generar(self, prompt: str, contexto: str) -> str:
        """Genera una respuesta a `prompt` usando `contexto` como guía/instrucción del sistema."""
