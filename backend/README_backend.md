# MOE Router Backend

Este directorio reune el backend FastAPI del demo Mixture-of-Experts (MoE) Router descrito en `docs/03_estructura_general.md`.

## Estructura
- `app/main.py`: punto de entrada FastAPI y definicion de rutas.
- `app/config`: carga de configuraciones basada en Pydantic Settings.
- `app/core`: motor de enrutamiento y reglas heuristicas.
- `app/providers`: clientes para OpenAI y Gemini.
- `app/models`: esquemas compartidos para request y response.
- `app/metrics`: registro de latencia, costo y score en SQLite.

## Primeros pasos
1. `python -m venv .venv`
2. `.\.venv\Scripts\activate`
3. `pip install -e .[dev]`
4. `uvicorn app.main:app --reload`

Ajusta las reglas dentro de `app/core` y los clientes dentro de `app/providers` para conectar con APIs reales o mejorar la logica del router.
