# Agente Corporativo de IA — NovaTech Solutions

Agente de inteligencia artificial (RAG) que responde preguntas de los colaboradores de **NovaTech Solutions** (empresa ficticia, SaaS de gestión de proyectos para pymes de Latinoamérica) con base en documentos internos reales de la organización, cubriendo múltiples formatos y dominios.

> Proyecto desarrollado para el desafío **Alura + Oracle — Agentes de IA**.

## 📌 Estado del proyecto

- [x] Definición del caso de uso y documentos fuente
- [ ] Pipeline de ingesta multi-formato
- [ ] Pipeline RAG (embeddings + vector store + LLM)
- [ ] Interfaz de chat
- [ ] Despliegue en Oracle Cloud Infrastructure (OCI)
- [ ] Evidencia de despliegue (imagen/video) — **pendiente**

## 🏢 Contexto: la empresa ficticia

**NovaTech Solutions** es una empresa SaaS (producto: **NovaFlow**, plataforma de gestión de proyectos) con sede en Bogotá y operaciones en México, Perú y Chile, ~140 colaboradores. Los documentos en `docs/` son su base de conocimiento interna.

## 📂 Documentos incluidos (`docs/`)

| Categoría | Documento | Formato |
|---|---|---|
| Recursos Humanos | Manual de onboarding y beneficios | `.docx` |
| Financiero y Contable | Estado de resultados 2025 + presupuesto 2026 | `.xlsx` |
| Operacional | Manual de procedimientos (incidentes, SLA, despliegues, soporte) | `.pdf` |
| Estratégico | Roadmap 2026 y OKRs | `.pptx` |
| Legal y Compliance | Política de privacidad y protección de datos | `.md` |
| Marketing y Comercial | Tabla de precios y planes | `.csv` |
| Datos y Sistemas | Documentación de la API interna de NovaFlow | `.json` |
| Investigación y Desarrollo | Estudio de mercado para expansión regional | `.pdf` |
| Comunicación Interna | Newsletter interno | `.html` |

## 🏗️ Arquitectura

```
Documentos (pdf/docx/xlsx/pptx/md/csv/json/html)
        │
   Ingesta y parsing (loader específico por formato)
        │
   Chunking de texto
        │
   Embeddings — OCI Generative AI (servicio OCI)
        │
   Vector Store — FAISS / ChromaDB
        │
   Retriever + LLM — OCI Generative AI (Cohere Command R / Llama)
        │
   Interfaz de chat — Streamlit
        │
   Despliegue — OCI Compute (Always Free / Container Instances)
```

## 📁 Estructura del repositorio

```
agente-corporativo-ia/
├── docs/                  # documentos fuente de la empresa ficticia
├── src/
│   ├── ingestion/          # loaders por formato de archivo
│   ├── embeddings/         # cliente de embeddings (OCI Generative AI)
│   ├── vectorstore/        # wrapper de FAISS/Chroma
│   ├── rag/                # retriever + prompt + orquestación
│   └── app/                # interfaz de chat (Streamlit)
├── infra/
│   ├── Dockerfile
│   └── oci/                # scripts de despliegue en OCI
├── tests/
├── requirements.txt
└── .env.example
```

## 🚀 Cómo ejecutar (local)

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # completar credenciales de OCI
streamlit run src/app/main.py
```

## ☁️ Despliegue en Oracle Cloud Infrastructure

Servicio(s) OCI utilizados: **OCI Generative AI** (embeddings + generación) y **OCI Compute** (hospedaje de la aplicación).
Detalles del despliegue en [`infra/oci/README.md`](infra/oci/README.md).

## 🎥 Evidencia de ejecución en la nube

> _Pendiente: insertar aquí una captura de pantalla o video corto del agente respondiendo preguntas desde la URL pública desplegada en OCI._

## 🛠️ Stack técnico

- Python 3.11+
- LangChain (orquestación RAG)
- FAISS / ChromaDB (vector store)
- OCI Generative AI SDK
- Streamlit (interfaz)
- Docker (contenedorización)

## 📄 Licencia

Proyecto educativo desarrollado para el desafío Alura + Oracle. Todos los documentos de la empresa "NovaTech Solutions" son ficticios.
