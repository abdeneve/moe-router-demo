from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .metrics_service import MetricRecord


class MetricsStorage:
    '''SQLite storage facade for router metrics.'''

    def __init__(self, db_path: str | Path | None = None) -> None:
        default_path = Path(__file__).resolve().parent / 'metrics.sqlite'
        self.db_path = Path(db_path) if db_path else default_path
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                '''
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    provider TEXT NOT NULL,
                    model TEXT NOT NULL,
                    latency_ms INTEGER NOT NULL,
                    cost_usd REAL NOT NULL,
                    score REAL NOT NULL,
                    rationale TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                '''
            )
            connection.commit()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def save(self, record: 'MetricRecord') -> None:
        with self._connect() as connection:
            connection.execute(
                '''
                INSERT INTO metrics (provider, model, latency_ms, cost_usd, score, rationale, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    record.provider,
                    record.model,
                    record.latency_ms,
                    record.cost_usd,
                    record.score,
                    record.rationale,
                    record.created_at.isoformat(),
                ),
            )
            connection.commit()

    def fetch_last(self, limit: int = 20) -> List['MetricRecord']:
        with self._connect() as connection:
            cursor = connection.execute(
                '''
                SELECT provider, model, latency_ms, cost_usd, score, rationale, created_at
                FROM metrics
                ORDER BY id DESC
                LIMIT ?
                ''',
                (limit,),
            )
            rows = cursor.fetchall()

        from .metrics_service import MetricRecord

        results: List[MetricRecord] = []
        for provider, model, latency_ms, cost_usd, score, rationale, created_at in rows:
            results.append(
                MetricRecord(
                    provider=provider,
                    model=model,
                    latency_ms=latency_ms,
                    cost_usd=cost_usd,
                    score=score,
                    rationale=rationale,
                    created_at=datetime.fromisoformat(created_at),
                )
            )
        return list(reversed(results))
