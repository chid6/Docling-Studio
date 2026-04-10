"""Tests for the embedding client adapter (infra.embedding_client).

Mock httpx to validate adapter logic without running the embedding service.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from domain.ports import EmbeddingService
from infra.embedding_client import _MAX_BATCH, EmbeddingClient

# -- Protocol satisfaction -----------------------------------------------------


class TestProtocolSatisfaction:
    def test_satisfies_embedding_service_protocol(self) -> None:
        client = EmbeddingClient("http://localhost:8001")
        assert isinstance(client, EmbeddingService)


# -- embed ---------------------------------------------------------------------


class TestEmbed:
    async def test_returns_empty_for_empty_input(self) -> None:
        client = EmbeddingClient("http://localhost:8001")
        result = await client.embed([])
        assert result == []

    async def test_calls_service_and_returns_embeddings(self) -> None:
        client = EmbeddingClient("http://localhost:8001")
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "embeddings": [[0.1, 0.2], [0.3, 0.4]],
            "model": "all-MiniLM-L6-v2",
            "dimension": 2,
        }

        mock_http_client = AsyncMock()
        mock_http_client.post.return_value = mock_response
        mock_http_client.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_http_client.__aexit__ = AsyncMock(return_value=False)

        with patch("infra.embedding_client.httpx.AsyncClient", return_value=mock_http_client):
            result = await client.embed(["hello", "world"])

        assert result == [[0.1, 0.2], [0.3, 0.4]]
        mock_http_client.post.assert_awaited_once_with(
            "http://localhost:8001/embed",
            json={"texts": ["hello", "world"]},
        )

    async def test_strips_trailing_slash_from_base_url(self) -> None:
        client = EmbeddingClient("http://localhost:8001/")
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"embeddings": [[0.1]], "model": "m", "dimension": 1}

        mock_http_client = AsyncMock()
        mock_http_client.post.return_value = mock_response
        mock_http_client.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_http_client.__aexit__ = AsyncMock(return_value=False)

        with patch("infra.embedding_client.httpx.AsyncClient", return_value=mock_http_client):
            await client.embed(["test"])

        mock_http_client.post.assert_awaited_once_with(
            "http://localhost:8001/embed",
            json={"texts": ["test"]},
        )

    async def test_splits_large_batches(self) -> None:
        client = EmbeddingClient("http://localhost:8001")
        texts = [f"text_{i}" for i in range(_MAX_BATCH + 10)]

        call_count = 0

        def make_response(batch_size: int) -> MagicMock:
            resp = MagicMock()
            resp.raise_for_status = MagicMock()
            resp.json.return_value = {
                "embeddings": [[0.1]] * batch_size,
                "model": "m",
                "dimension": 1,
            }
            return resp

        async def mock_post(url: str, json: dict) -> MagicMock:
            nonlocal call_count
            call_count += 1
            return make_response(len(json["texts"]))

        mock_http_client = AsyncMock()
        mock_http_client.post = mock_post
        mock_http_client.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_http_client.__aexit__ = AsyncMock(return_value=False)

        with patch("infra.embedding_client.httpx.AsyncClient", return_value=mock_http_client):
            result = await client.embed(texts)

        assert len(result) == _MAX_BATCH + 10
        assert call_count == 2  # _MAX_BATCH + 10 remaining


# -- max batch constant --------------------------------------------------------


class TestMaxBatch:
    def test_max_batch_is_256(self) -> None:
        assert _MAX_BATCH == 256
