"""HTTP client adapter for the embedding microservice.

Satisfies the ``EmbeddingService`` Protocol defined in ``domain.ports``.
Calls the embedding-service REST API (POST /embed).
"""

from __future__ import annotations

import logging

import httpx

logger = logging.getLogger(__name__)

# Maximum texts per request to avoid payload / memory issues on the server.
_MAX_BATCH = 256


class EmbeddingClient:
    """Remote embedding adapter backed by the embedding-service microservice.

    Args:
        base_url: Embedding service URL (e.g. ``http://localhost:8001``).
        timeout: HTTP request timeout in seconds.
    """

    def __init__(self, base_url: str, *, timeout: float = 120.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings by calling the remote service.

        Automatically splits large batches into sub-batches of ``_MAX_BATCH``.
        """
        if not texts:
            return []

        all_embeddings: list[list[float]] = []
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            for start in range(0, len(texts), _MAX_BATCH):
                batch = texts[start : start + _MAX_BATCH]
                resp = await client.post(
                    f"{self._base_url}/embed",
                    json={"texts": batch},
                )
                resp.raise_for_status()
                data = resp.json()
                all_embeddings.extend(data["embeddings"])

        return all_embeddings
