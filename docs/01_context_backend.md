# Contexto para generación de backend (Codex)

## Estilo

- UV: manejador de pacotes uv
- Python 3.12
- Framework: FastAPI.
- Tipado estático razonable (type hints).
- Código simple y didáctico para demo en vivo, no "enterprise" extremo.

## Módulos clave

- `app/main.py`
  - Arrancar FastAPI.
  - Definir ruta `POST /api/route`.
  - Inyectar o instanciar el `RouterEngine`.

- `app/core/router_engine.py`
  - Clase principal `RouterEngine`.
  - Exponer método `route(query: str, routing_preferences: RoutingPreferences) -> RouterResult`.

- `app/core/decision_rules.py`
  - Implementar funciones puras que, dado:
    - tipo de query (longitud, palabras clave),
    - preferencias (peso precisión/latencia/costo),
  - devuelvan `ProviderId` (por ejemplo `"gpt-4o-mini" | "gemini-2.5-pro" | "gemini-2.5-flash-image"`).
    - gpt-4o-mini: para respuestas rapidas
    - gemini-2.5-pro: para respuestas pensadas, tomando mas tiempo
    - gemini-2.5-flash-image: para generar imagenes

- `app/providers/*_client.py`
  - Encapsular llamadas a cada modelo/API.
  - Usar APIs reales.

- `app/metrics/metrics_service.py`
  - Función para registrar y devolver métricas en formato amigable para el frontend.

## Supuestos

- Para la demo basta un almacenamiento en SQLite para las métricas.
- Para el cálculo de costo: Usar un estimador simple (tokens aproximados).
