# Demo: MoE Router en vivo (precisión vs latencia vs costo)

## Objetivo de la demo (10 minutos)

- Misma entrada de usuario pasa por un **router**.
- El router decide, según reglas + heurísticas + feedback:
  - Algunas queries van a **GPT-4o-mini** (cloud, más costoso, mejor calidad).
  - Otras van a **Llama local** (más barato, menor latencia en algunas configs).
  - Otras van a una **API especializada** (por ejemplo, búsqueda o cálculo).
- Al final se muestra una **tabla de métricas**:
  - tiempo total,
  - costo estimado,
  - "score" de calidad (proxy simple: por ahora heurístico / user rating simulado).

## Stack propuesto

- **Backend (Python)**:
  - Framework web: FastAPI.
  - Router: módulo `core/router_engine.py` + `core/decision_rules.py`.
  - Proveedores: módulo `providers/`.
  - Métricas: módulo `metrics/`.

- **Frontend (React)**:
  - Form de input.
  - Tabla de métricas.
  - Card con la decisión del router y el modelo usado.

## Flujo de alto nivel

1. Frontend envía `POST /api/route` con `{ user_query, importance_precision, importance_latency, importance_cost }`.
2. Backend:
   - Usa `decision_rules` para elegir el modelo.
   - Llama al cliente adecuado en `providers/`.
   - Mide tiempo y costo estimado.
   - Devuelve `{ output_text, chosen_model, latency_ms, cost_usd, quality_score }`.
3. Frontend renderiza:
   - Respuesta del modelo.
   - Tabla comparativa de métricas (para cada request).
