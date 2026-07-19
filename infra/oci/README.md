# Despliegue en Oracle Cloud Infrastructure (OCI)

_Pendiente de completar en la fase de despliegue (Fase 6 del plan)._

## Plan de despliegue

1. Crear una instancia **Compute** en el tier Always Free (forma `VM.Standard.A1.Flex`, Ampere ARM).
2. Instalar Docker en la instancia.
3. Construir la imagen del agente con el `Dockerfile` en la raíz de `infra/`.
4. Configurar reglas de seguridad (security list / NSG) para exponer el puerto de Streamlit (8501).
5. Configurar credenciales de **OCI Generative AI** mediante Instance Principal (evita exponer claves API en el contenedor).
6. Levantar el contenedor y validar acceso público vía IP o dominio.
7. Documentar aquí los comandos exactos utilizados y capturar evidencia (screenshot/video) para el README principal.

## Comandos de referencia (a completar con los valores reales del despliegue)

```bash
# Build de la imagen
docker build -t agente-corporativo-ia -f infra/Dockerfile .

# Ejecución local de prueba
docker run -p 8501:8501 --env-file .env agente-corporativo-ia

# En la instancia OCI (tras copiar el proyecto o clonar el repo)
git clone <URL_DEL_REPO>
cd agente-corporativo-ia
docker build -t agente-corporativo-ia -f infra/Dockerfile .
docker run -d -p 8501:8501 --env-file .env agente-corporativo-ia
```
