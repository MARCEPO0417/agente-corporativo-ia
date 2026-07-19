from .provider_base import LLMProvider


class OCIGenAIProvider(LLMProvider):
    """Adapter de OCI Generative AI — pendiente de credenciales reales.

    Para completar esta implementación se necesita:
      - OCI_COMPARTMENT_ID: compartment donde está habilitado el servicio Generative AI.
      - OCI_GENAI_ENDPOINT: endpoint regional de inferencia (ver .env.example).
      - OCI_GENAI_EMBEDDING_MODEL_ID / OCI_GENAI_CHAT_MODEL_ID: OCIDs de los modelos.
      - Autenticación: OCI_CONFIG_FILE + OCI_CONFIG_PROFILE (perfil local) o
        OCI_USE_INSTANCE_PRINCIPAL=true al correr dentro de OCI Compute.
      - SDK: oci.generative_ai_inference.GenerativeAiInferenceClient, usando
        EmbedTextDetails para embed() y ChatDetails (Cohere o Generic chat request)
        para generar().
    """

    def embed(self, textos: list[str]) -> list[list[float]]:
        raise NotImplementedError(
            "OCIGenAIProvider.embed no está implementado todavía: falta la cuenta "
            "OCI y sus credenciales. Usa CohereProvider mientras tanto."
        )

    def generar(self, prompt: str, contexto: str) -> str:
        raise NotImplementedError(
            "OCIGenAIProvider.generar no está implementado todavía: falta la cuenta "
            "OCI y sus credenciales. Usa CohereProvider mientras tanto."
        )
