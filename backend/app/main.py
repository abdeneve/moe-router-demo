"""
CONTEXTO PARA CODEX (main.py)

Rol de este archivo:
- Definir la aplicación FastAPI para la demo del MoE Router.
- Exponer un endpoint POST `/api/route` que reciba:
  - user_query: str
  - importance_precision: float (0.0 a 1.0)
  - importance_latency: float (0.0 a 1.0)
  - importance_cost: float (0.0 a 1.0)
- Llamar al RouterEngine y devolver un objeto JSON serializable
  con:
  - output_text: str
  - chosen_model: str
  - latency_ms: float
  - cost_usd: float
  - quality_score: float
  - routing_explanation: str

Requisitos:
- Usar FastAPI.
- Incluir un objeto `app = FastAPI(...)`.
- Utilizar modelos Pydantic definidos en `app/models/schemas.py`.
- Manejar errores básicos (por ejemplo, query vacía).

No implementes la lógica del router aquí, solo orquestra:
- Instanciar RouterEngine desde `app.core.router_engine`.
"""

from fastapi import FastAPI, HTTPException

from .core.router_engine import RouterEngine, RouterResult
from .metrics.metrics_service import MetricsService
from .models.schemas import RouteRequest, RouteResponse

app = FastAPI(title='MOE Router Backend', version='0.1.0')

router_engine = RouterEngine()
metrics_service = MetricsService()


@app.get('/healthz')
async def health_check() -> dict[str, str]:
    return {'status': 'ok'}


@app.post('/route', response_model=RouteResponse)
async def route(payload: RouteRequest) -> RouteResponse:
    try:
        result: RouterResult = await router_engine.route(payload)
    except KeyError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    metrics_service.record_from_result(result)
    return result.to_response()
