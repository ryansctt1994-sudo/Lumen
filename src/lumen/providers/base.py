"""Provider mesh base interfaces.

The provider mesh keeps model access outside the authority layer. Providers may
produce text, embeddings, tool calls, or streams, but they do not authorize
execution.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Dict, List, Optional


@dataclass(frozen=True)
class ProviderRequest:
    prompt: str
    model: Optional[str] = None
    system: Optional[str] = None
    tools: Optional[List[Dict[str, Any]]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProviderResponse:
    text: str
    model: str
    provider: str
    usage: Dict[str, Any] = field(default_factory=dict)
    raw: Optional[Dict[str, Any]] = None


@dataclass(frozen=True)
class ProviderHealth:
    provider: str
    ok: bool
    detail: str = ""
    latency_ms: Optional[float] = None


class Provider(ABC):
    """Abstract provider interface for local and cloud model backends."""

    name: str

    @abstractmethod
    async def generate(self, request: ProviderRequest) -> ProviderResponse:
        """Generate a response for a prompt."""

    async def stream(self, request: ProviderRequest) -> AsyncIterator[str]:
        response = await self.generate(request)
        yield response.text

    async def embed(self, text: str, *, model: Optional[str] = None) -> List[float]:
        raise NotImplementedError("embed is not implemented for this provider")

    async def tools(self) -> List[Dict[str, Any]]:
        return []

    @abstractmethod
    async def health_check(self) -> ProviderHealth:
        """Return provider health without creating authority claims."""
