from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class RouteRequest(BaseModel):
    '''Parametros usados por el router para balancear objetivos.'''

    user_query: str = Field(..., min_length=1, description='Peticion original del usuario')
    importance_precision: float = Field(
        ..., ge=0.0, le=1.0, description='Peso relativo para precision'
    )
    importance_latency: float = Field(
        ..., ge=0.0, le=1.0, description='Peso relativo para latencia'
    )
    importance_cost: float = Field(
        ..., ge=0.0, le=1.0, description='Peso relativo para costo'
    )


class RouteResponse(BaseModel):
    '''Respuesta detallada del router.'''

    output_text: str = Field(..., min_length=1)
    chosen_model: str = Field(..., min_length=1)
    latency_ms: float = Field(..., ge=0.0)
    cost_usd: float = Field(..., ge=0.0)
    quality_score: float = Field(..., ge=0.0, le=1.0)
    routing_explanation: str = Field(..., min_length=1)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class RouterRequest(BaseModel):
    '''Entrada principal del router.'''

    query: str = Field(..., min_length=1, description='Prompt enviado por el usuario')
    modality: Literal['text', 'image'] = 'text'
    user_tier: Literal['free', 'pro', 'enterprise'] = 'free'
    priority: Literal['low', 'normal', 'high'] = 'normal'
    max_tokens: int | None = Field(None, ge=1, le=4096)
    temperature: float = Field(0.2, ge=0.0, le=2.0)
