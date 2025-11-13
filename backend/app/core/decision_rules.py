"""
CONTEXTO PARA CODEX (decision_rules.py)

Rol:
- Contener la lógica pura de decisión del router (sin llamadas a red).
- Dado un conjunto de señales, devolver el id del proveedor a usar.

Entradas típicas:
- query_length: int
- has_keywords_analytical: bool
- importance_precision: float
- importance_latency: float
- importance_cost: float

Salida:
- provider_id: str
# (por ejemplo `"gpt-4o-mini" | "gemini-2.5-pro" | "gemini-2.5-flash-image"`).
#     - gpt-4o-mini: para respuestas rapidas
#     - gemini-2.5-pro: para respuestas pensadas, tomando mas tiempo
#     - gemini-2.5-flash-image: para generar imagenes

Reglas de ejemplo (pueden ser simples):
- Si importance_precision es alta (> 0.7), preferir "gpt4o".
- Si importance_cost es alta y query es corta, preferir "llama".
- Si contiene ciertas keywords, usar "specialized_api".

Requisitos:
- Implementar funciones puras para facilitar test.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from ..models.schemas import RouterRequest


@dataclass
class RoutingDecision:
    provider: str
    model: str
    rationale: str
    estimated_cost_usd: float
    estimated_latency_ms: int
    score: float


class DecisionRules:
    '''Deterministic heuristics that emulate the MoE router reasoning.'''

    ANALYTICAL_KEYWORDS: Final[tuple[str, ...]] = (
        'analiza',
        'analysis',
        'analytical',
        'compare',
        'compara',
        'benchmark',
        'estrategia',
        'strategy',
        'plan',
        'roadmap',
        'evalu',
        'justify',
        'razona',
        'explica',
        'explain why',
        'investiga',
        'research',
    )
    VISUAL_KEYWORDS: Final[tuple[str, ...]] = (
        'image',
        'imagen',
        'picture',
        'photo',
        'foto',
        'render',
        'draw',
        'dibuja',
        'sketch',
        'diagram',
        'ilustr',
        'logo',
        'mockup',
        'storyboard',
        'poster',
    )

    def __init__(self) -> None:
        self.catalog = {
            'openai': {
                'model': 'gpt-4o-mini',
                'cost': 0.0015,
                'latency': 850,
                'score': 0.82,
            },
            'gemini_pro': {
                'model': 'gemini-2.5-pro',
                'cost': 0.0028,
                'latency': 900,
                'score': 0.91,
            },
            'gemini_flash_image': {
                'model': 'gemini-2.5-flash-image',
                'cost': 0.0035,
                'latency': 980,
                'score': 0.88,
            },
        }

    def select(self, payload: RouterRequest) -> RoutingDecision:
        signals = self._extract_signals(payload)
        provider_key, rationale_parts = self._choose_provider(payload, signals)
        config = self.catalog[provider_key]

        cost = self._adjust_cost(config['cost'], payload, signals)
        latency = self._adjust_latency(config['latency'], payload, signals)
        score = self._adjust_score(config['score'], provider_key, payload, signals)

        return RoutingDecision(
            provider=provider_key,
            model=config['model'],
            rationale=' '.join(rationale_parts),
            estimated_cost_usd=round(cost, 5),
            estimated_latency_ms=int(latency),
            score=round(min(score, 0.99), 2),
        )

    def _extract_signals(self, payload: RouterRequest) -> 'RuleSignals':
        query = payload.query.strip().lower()
        word_count = len(query.split()) or 1
        has_analytical = any(keyword in query for keyword in self.ANALYTICAL_KEYWORDS)
        has_visual = payload.modality == 'image' or any(
            keyword in query for keyword in self.VISUAL_KEYWORDS
        )

        precision = self._map_priority_to_precision(payload.priority)
        latency = self._map_tokens_to_latency(payload.max_tokens)
        cost = self._map_tier_to_cost(payload.user_tier)

        return RuleSignals(
            query_length=word_count,
            has_analytical_keywords=has_analytical,
            has_visual_cues=has_visual,
            importance_precision=precision,
            importance_latency=latency,
            importance_cost=cost,
        )

    def _choose_provider(
        self, payload: RouterRequest, signals: 'RuleSignals'
    ) -> tuple[str, list[str]]:
        if signals.has_visual_cues:
            rationale = [
                'Se detecto intencion visual en la query, por lo que se deriva a Gemini Flash Image.'
            ]
            if payload.modality != 'image':
                rationale.append('La inferencia se realizo aun con modalidad text para asegurar cobertura.')
            return 'gemini_flash_image', rationale

        if signals.importance_precision >= 0.75:
            rationale = [
                'Peso de precision > 0.70, se prioriza GPT-4o-mini.',
                self._describe_signals(signals),
            ]
            return 'openai', rationale

        if signals.has_analytical_keywords or signals.query_length >= 150:
            rationale = [
                'La query es analitica o extensa, se prefiere Gemini 2.5 Pro para razonamientos largos.',
                self._describe_signals(signals),
            ]
            return 'gemini_pro', rationale

        if signals.importance_cost >= 0.7 and signals.query_length <= 80:
            rationale = [
                'Sensibilidad alta a costo y prompt corto favorecen GPT-4o-mini.',
                self._describe_signals(signals),
            ]
            return 'openai', rationale

        if signals.importance_latency >= 0.7 and signals.query_length <= 120:
            rationale = [
                'Preferencia fuerte por baja latencia dirige el trafico a GPT-4o-mini.',
                self._describe_signals(signals),
            ]
            return 'openai', rationale

        openai_score, openai_reasons = self._score_openai(signals)
        gemini_score, gemini_reasons = self._score_gemini_pro(signals)

        if gemini_score > openai_score:
            gemini_reasons.append(self._describe_signals(signals))
            return 'gemini_pro', gemini_reasons

        openai_reasons.append(self._describe_signals(signals))
        return 'openai', openai_reasons

    def _score_openai(self, signals: 'RuleSignals') -> tuple[float, list[str]]:
        score = self.catalog['openai']['score']
        rationale = ['GPT-4o-mini equilibra costo y velocidad para prompts generales.']

        if signals.importance_precision >= 0.7:
            score += 0.08
            rationale.append(
                f'La precision requerida ({signals.importance_precision:.2f}) supera el umbral de 0.70.'
            )
        if signals.importance_latency >= 0.7:
            score += 0.05
            rationale.append('Se prioriza latencia baja, afin a GPT-4o-mini.')
        if signals.importance_cost >= 0.65 and signals.query_length <= 80:
            score += 0.04
            rationale.append(
                f'Query corta ({signals.query_length} palabras) y sensibilidad a costo permiten un modelo ligero.'
            )
        if signals.query_length > 180 and signals.importance_precision < 0.6:
            score -= 0.04

        return score, rationale

    def _score_gemini_pro(self, signals: 'RuleSignals') -> tuple[float, list[str]]:
        score = self.catalog['gemini_pro']['score']
        rationale = ['Gemini 2.5 Pro se usa para respuestas mas pensadas.']

        if signals.has_analytical_keywords:
            score += 0.08
            rationale.append('Se detectaron palabras clave analiticas.')
        if signals.query_length >= 120:
            score += 0.05
            rationale.append(f'Prompt largo ({signals.query_length} palabras) sugiere analisis profundo.')
        if signals.importance_precision >= 0.6 and signals.importance_latency < 0.7:
            score += 0.03
            rationale.append('Se busca precision sostenida sin urgencia extrema de latencia.')
        if signals.importance_latency >= 0.75:
            score -= 0.05
        if signals.importance_cost >= 0.7 and signals.query_length <= 80:
            score -= 0.04
        if signals.query_length <= 60:
            score -= 0.02

        return score, rationale

    def _adjust_cost(
        self, base_cost: float, payload: RouterRequest, signals: 'RuleSignals'
    ) -> float:
        length_factor = 1 + min(0.35, signals.query_length / 800)
        if payload.modality == 'image':
            length_factor += 0.15

        tier_factor = {
            'free': 0.9,
            'pro': 1.0,
            'enterprise': 1.08,
        }[payload.user_tier]

        budget_factor = 1 - (signals.importance_cost - 0.5) * 0.15
        return base_cost * length_factor * tier_factor * budget_factor

    def _adjust_latency(
        self, base_latency: int, payload: RouterRequest, signals: 'RuleSignals'
    ) -> float:
        latency = float(base_latency)

        if payload.priority == 'high':
            latency *= 0.85
        elif payload.priority == 'low':
            latency *= 1.1

        if signals.importance_latency >= 0.75:
            latency *= 0.9
        elif signals.importance_latency <= 0.35:
            latency *= 1.12

        if signals.query_length >= 180 and payload.modality == 'text':
            latency *= 1.05

        if payload.user_tier == 'enterprise':
            latency *= 0.9
        elif payload.user_tier == 'free':
            latency *= 1.03

        minimum = 250 if payload.modality == 'image' else 150
        return max(minimum, latency)

    def _adjust_score(
        self,
        base_score: float,
        provider_key: str,
        payload: RouterRequest,
        signals: 'RuleSignals',
    ) -> float:
        score = base_score
        score += (signals.importance_precision - 0.5) * 0.12

        if provider_key == 'gemini_pro' and (
            signals.has_analytical_keywords or signals.query_length >= 150
        ):
            score += 0.03

        if provider_key == 'openai' and signals.importance_latency >= 0.7:
            score += 0.02

        if provider_key == 'gemini_flash_image' and signals.has_visual_cues:
            score += 0.04

        if payload.user_tier == 'free' and provider_key == 'gemini_pro':
            score -= 0.02

        return score

    @staticmethod
    def _map_priority_to_precision(priority: str) -> float:
        mapping = {'high': 0.85, 'normal': 0.55, 'low': 0.25}
        return mapping.get(priority, 0.55)

    @staticmethod
    def _map_tokens_to_latency(max_tokens: int | None) -> float:
        if not max_tokens:
            return 0.5
        if max_tokens <= 256:
            return 0.85
        if max_tokens <= 512:
            return 0.65
        if max_tokens <= 768:
            return 0.45
        return 0.3

    @staticmethod
    def _map_tier_to_cost(tier: str) -> float:
        mapping = {'free': 0.85, 'pro': 0.55, 'enterprise': 0.3}
        return mapping.get(tier, 0.55)

    @staticmethod
    def _describe_signals(signals: 'RuleSignals') -> str:
        return (
            f'Senales -> precision:{signals.importance_precision:.2f}, '
            f'latencia:{signals.importance_latency:.2f}, '
            f'costo:{signals.importance_cost:.2f}, '
            f'longitud:{signals.query_length} palabras.'
        )


@dataclass(frozen=True)
class RuleSignals:
    query_length: int
    has_analytical_keywords: bool
    has_visual_cues: bool
    importance_precision: float
    importance_latency: float
    importance_cost: float
