"""
CONTEXTO PARA CODEX (metrics_service.py)

Rol:
- Almacenar en memoria un pequeño histórico de llamadas del router.
- Exponer funciones para:
  - registrar una nueva métrica.
  - obtener las últimas N métricas para mostrar en el frontend.

Modelo de métrica:
- timestamp: datetime
- chosen_model: str
- latency_ms: float
- cost_usd: float
- quality_score: float

Para simplificar:
- Usar una lista global en SQLite.
- Persistir en BD SQLite para esta demo.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from threading import Lock
from typing import Deque, List

from ..config.settings import get_settings
from ..core.router_engine import RouterResult
from .storage import MetricsStorage


@dataclass(slots=True)
class MetricRecord:
    provider: str
    model: str
    latency_ms: int
    cost_usd: float
    score: float
    rationale: str
    created_at: datetime

    @classmethod
    def from_result(cls, result: RouterResult) -> 'MetricRecord':
        return cls(
            provider=result.provider,
            model=result.chosen_model,
            latency_ms=int(result.latency_ms),
            cost_usd=result.cost_usd,
            score=result.quality_score,
            rationale=result.routing_explanation,
            created_at=datetime.now(timezone.utc),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            'provider': self.provider,
            'model': self.model,
            'latency_ms': self.latency_ms,
            'cost_usd': self.cost_usd,
            'score': self.score,
            'rationale': self.rationale,
            'created_at': self.created_at.isoformat(),
        }


class MetricsService:
    '''Coordinates conversion of router responses into persisted metrics.'''

    def __init__(self, storage: MetricsStorage | None = None, *, history_limit: int = 50) -> None:
        if storage is None:
            settings = get_settings()
            storage = MetricsStorage(settings.sqlite_path)

        self.storage = storage
        self.history_limit = max(1, history_limit)
        self._history: Deque[MetricRecord] = deque(maxlen=self.history_limit)
        self._lock = Lock()
        self._preload_cache()

    def record_from_result(self, result: RouterResult) -> MetricRecord:
        record = MetricRecord.from_result(result)
        self._append_to_cache(record)
        self.storage.save(record)
        return record

    def recent(self, limit: int = 20) -> List[MetricRecord]:
        if limit <= 0:
            return []

        if limit <= self.history_limit and len(self._history) >= limit:
            with self._lock:
                return list(self._history)[-limit:]

        return self.storage.fetch_last(limit)

    def recent_as_dicts(self, limit: int = 20) -> List[dict[str, object]]:
        return [record.to_dict() for record in self.recent(limit)]

    def _preload_cache(self) -> None:
        cached = self.storage.fetch_last(self.history_limit)
        for record in cached:
            self._history.append(record)

    def _append_to_cache(self, record: MetricRecord) -> None:
        with self._lock:
            self._history.append(record)
