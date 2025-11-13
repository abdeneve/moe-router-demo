"""
CONTEXTO PARA CODEX (base_client.py)

Rol:
- Definir una interfaz/base para los clientes de modelos.

Diseño sugerido:
- Clase abstracta `BaseLLMClient` con método:
  - `generate(prompt: str) -> tuple[str, float, float]`
    - retorna (output_text, latency_ms, cost_usd)

Subclases:
- OpenAIClient (usa GPT-4o-mini)
- LocalLlamaClient
- SpecializedApiClient

Para la demo:
- Puedes simular las respuestas en vez de llamar APIs reales.
"""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod

from ..models.schemas import RouterRequest


class LlmProviderClient(ABC):
    '''Lightweight async client interface for LLM providers.'''

    name: str
    default_model: str

    @abstractmethod
    async def generate(self, payload: RouterRequest, *, model: str | None = None) -> str:
        '''Return the provider response for the given payload.'''

    async def _simulate_latency(self, milliseconds: int = 40) -> None:
        await asyncio.sleep(milliseconds / 1000)

    def _short_prompt(self, prompt: str) -> str:
        compact = ' '.join(prompt.split())
        return compact[:60] + ('...' if len(compact) > 60 else '')
