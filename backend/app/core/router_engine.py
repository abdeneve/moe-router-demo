'''High-level router orchestration built on top of decision rules and providers.'''

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from ..models.schemas import RouteRequest, RouteResponse, RouterRequest
from ..providers.base_client import LlmProviderClient
from ..providers.gemini_flash_image_client import GeminiFlashImageClient
from ..providers.gemini_pro_client import GeminiProClient
from ..providers.openai_client import OpenAIClient
from .decision_rules import DecisionRules, RoutingDecision

IMAGE_KEYWORDS: Final[tuple[str, ...]] = (
    'image',
    'imagen',
    'picture',
    'photo',
    'render',
    'draw',
    'dibuja',
    'generate an image',
)


@dataclass(slots=True)
class RouterResult:
    '''Domain object returned by the router before serialisation.'''

    provider: str
    chosen_model: str
    output_text: str
    latency_ms: float
    cost_usd: float
    quality_score: float
    routing_explanation: str

    def to_response(self) -> RouteResponse:
        return RouteResponse(
            output_text=self.output_text,
            chosen_model=self.chosen_model,
            latency_ms=self.latency_ms,
            cost_usd=self.cost_usd,
            quality_score=self.quality_score,
            routing_explanation=self.routing_explanation,
        )


class RouterEngine:
    '''Main entry point that coordinates routing decisions and provider calls.'''

    def __init__(self, providers: dict[str, LlmProviderClient] | None = None) -> None:
        self.rules = DecisionRules()
        self.providers = providers or {
            'openai': OpenAIClient(),
            'gemini_pro': GeminiProClient(),
            'gemini_flash_image': GeminiFlashImageClient(),
        }

    async def route(self, payload: RouteRequest) -> RouterResult:
        internal_payload = self._to_internal_payload(payload)
        decision = self.rules.select(internal_payload)
        client = self.providers.get(decision.provider)

        if client is None:
            raise KeyError(f'Provider {decision.provider!r} is not configured')

        output = await client.generate(internal_payload, model=decision.model)
        latency_ms = self._derive_latency(payload.importance_latency, decision)
        cost_usd = self._derive_cost(payload.user_query, decision)
        quality_score = self._derive_quality(payload.importance_precision, decision)
        explanation = self._compose_rationale(payload, decision)

        return RouterResult(
            provider=decision.provider,
            chosen_model=decision.model,
            output_text=output,
            latency_ms=latency_ms,
            cost_usd=cost_usd,
            quality_score=quality_score,
            routing_explanation=explanation,
        )

    def _to_internal_payload(self, payload: RouteRequest) -> RouterRequest:
        query = payload.user_query.strip()
        modality = self._infer_modality(query)
        priority = self._resolve_priority(payload.importance_precision)
        user_tier = self._resolve_tier(payload.importance_cost)
        temperature = self._resolve_temperature(payload)
        max_tokens = self._estimate_max_tokens(payload, len(query.split()))

        return RouterRequest(
            query=query,
            modality=modality,
            user_tier=user_tier,
            priority=priority,
            max_tokens=max_tokens,
            temperature=temperature,
        )

    def _infer_modality(self, query: str) -> str:
        lowered = query.lower()
        return 'image' if any(keyword in lowered for keyword in IMAGE_KEYWORDS) else 'text'

    def _resolve_priority(self, precision_weight: float) -> str:
        if precision_weight >= 0.75:
            return 'high'
        if precision_weight <= 0.25:
            return 'low'
        return 'normal'

    def _resolve_tier(self, cost_weight: float) -> str:
        if cost_weight >= 0.75:
            return 'free'
        if cost_weight <= 0.25:
            return 'enterprise'
        return 'pro'

    def _resolve_temperature(self, payload: RouteRequest) -> float:
        temperature = 0.2 + (1 - payload.importance_precision) * 0.5
        if payload.importance_latency >= 0.7:
            temperature = max(0.15, temperature - 0.05)
        return round(min(1.2, max(0.1, temperature)), 2)

    def _estimate_max_tokens(self, payload: RouteRequest, word_count: int) -> int:
        base = 512
        if payload.importance_latency >= 0.7:
            base = 256
        elif payload.importance_precision >= 0.8:
            base = 768

        tokens = base + word_count * 4
        return min(4096, max(256, tokens))

    def _derive_latency(self, latency_weight: float, decision: RoutingDecision) -> float:
        if latency_weight >= 0.75:
            factor = 0.85
        elif latency_weight <= 0.25:
            factor = 1.1
        else:
            factor = 1.0
        return round(decision.estimated_latency_ms * factor, 2)

    def _derive_cost(self, query: str, decision: RoutingDecision) -> float:
        token_estimate = max(1, len(query.split()) * 4)
        token_factor = min(1.4, 0.65 + token_estimate / 2000)
        if 'image' in decision.model:
            token_factor += 0.1
        return round(decision.estimated_cost_usd * token_factor, 5)

    def _derive_quality(self, precision_weight: float, decision: RoutingDecision) -> float:
        adjustment = (precision_weight - 0.5) * 0.25
        return round(min(0.99, max(0.5, decision.score + adjustment)), 2)

    def _compose_rationale(self, payload: RouteRequest, decision: RoutingDecision) -> str:
        parts = [decision.rationale]

        if payload.importance_precision >= 0.75:
            parts.append('Se priorizo precision.')
        elif payload.importance_cost >= 0.75:
            parts.append('Se favorecieron opciones de menor costo.')
        elif payload.importance_latency >= 0.75:
            parts.append('Preferencia clara por baja latencia.')

        if decision.model.startswith('gemini') and payload.importance_precision >= 0.6:
            parts.append('Gemini ofrece mayor rigor analitico.')

        if self._infer_modality(payload.user_query) == 'image':
            parts.append('La query describe contenido visual.')

        return ' '.join(parts)
