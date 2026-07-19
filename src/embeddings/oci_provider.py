import os

import oci
from dotenv import load_dotenv

from .provider_base import LLMProvider

load_dotenv()

# embed-multilingual-v3.0 quedó deprecado en OCI (retiro 2026-09-30);
# embed-v4.0 es el modelo de embeddings multilingüe vigente sin fecha de
# deprecación. command-a-03-2025 es el mismo modelo de chat que usamos con
# el proveedor Cohere directo, para mantener comportamiento equivalente.
EMBED_MODEL_ID = os.getenv("OCI_GENAI_EMBEDDING_MODEL_ID", "cohere.embed-v4.0")
CHAT_MODEL_ID = os.getenv("OCI_GENAI_CHAT_MODEL_ID", "cohere.command-a-03-2025")


class OCIGenAIProvider(LLMProvider):
    """Adapter de OCI Generative AI (mismo contrato que CohereProvider)."""

    def __init__(
        self,
        compartment_id: str | None = None,
        endpoint: str | None = None,
        config_file: str | None = None,
        config_profile: str | None = None,
    ):
        self._compartment_id = compartment_id or os.getenv("OCI_COMPARTMENT_ID")
        if not self._compartment_id:
            raise ValueError(
                "OCI_COMPARTMENT_ID no está definido. Agrégalo a tu archivo .env "
                "(el compartment raíz de la tenancy sirve como valor)."
            )

        config_file = config_file or os.getenv("OCI_CONFIG_FILE", "~/.oci/config")
        config_profile = config_profile or os.getenv("OCI_CONFIG_PROFILE", "DEFAULT")
        config = oci.config.from_file(file_location=config_file, profile_name=config_profile)

        endpoint = endpoint or os.getenv("OCI_GENAI_ENDPOINT")
        if not endpoint:
            raise ValueError(
                "OCI_GENAI_ENDPOINT no está definido. Agrégalo a tu archivo .env "
                "(ver .env.example)."
            )

        self._cliente = oci.generative_ai_inference.GenerativeAiInferenceClient(
            config, service_endpoint=endpoint
        )

    def embed(self, textos: list[str], input_type: str = "search_document") -> list[list[float]]:
        """input_type: 'search_document' al indexar, 'search_query' al buscar."""
        tipo_oci = (
            oci.generative_ai_inference.models.EmbedTextDetails.INPUT_TYPE_SEARCH_QUERY
            if input_type == "search_query"
            else oci.generative_ai_inference.models.EmbedTextDetails.INPUT_TYPE_SEARCH_DOCUMENT
        )

        detalles = oci.generative_ai_inference.models.EmbedTextDetails(
            inputs=textos,
            serving_mode=oci.generative_ai_inference.models.OnDemandServingMode(
                serving_type=oci.generative_ai_inference.models.OnDemandServingMode.SERVING_TYPE_ON_DEMAND,
                model_id=EMBED_MODEL_ID,
            ),
            compartment_id=self._compartment_id,
            input_type=tipo_oci,
            truncate=oci.generative_ai_inference.models.EmbedTextDetails.TRUNCATE_END,
        )
        respuesta = self._cliente.embed_text(detalles)
        return respuesta.data.embeddings

    def generar(self, prompt: str, contexto: str) -> str:
        """`contexto` se usa como preamble_override (instrucciones + chunks recuperados),
        `prompt` es la pregunta del usuario. Misma lógica que CohereProvider.generar."""
        detalles = oci.generative_ai_inference.models.ChatDetails(
            compartment_id=self._compartment_id,
            serving_mode=oci.generative_ai_inference.models.OnDemandServingMode(
                serving_type=oci.generative_ai_inference.models.OnDemandServingMode.SERVING_TYPE_ON_DEMAND,
                model_id=CHAT_MODEL_ID,
            ),
            chat_request=oci.generative_ai_inference.models.CohereChatRequest(
                api_format=oci.generative_ai_inference.models.CohereChatRequest.API_FORMAT_COHERE,
                message=prompt,
                preamble_override=contexto,
                temperature=0.2,
                # El default de OCI es muy bajo (~20-30 tokens) y corta la
                # respuesta a la mitad, incluso antes de la línea
                # FUENTES_USADAS. Cohere directo no tiene este problema
                # porque su propio default es mucho más generoso.
                max_tokens=600,
            ),
        )
        respuesta = self._cliente.chat(detalles)
        return respuesta.data.chat_response.text
