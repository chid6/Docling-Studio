"""Tests for the ServeConverter adapter (Docling Serve HTTP client)."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, mock_open, patch

import httpx
import pytest

from domain.value_objects import ConversionOptions, ConversionResult, PageDetail, PageElement
from infra.serve_converter import (
    ServeConverter,
    _extract_pages,
    _map_item_type,
    _parse_response,
)


# ---------------------------------------------------------------------------
# Unit tests — response parsing
# ---------------------------------------------------------------------------

class TestParseResponse:
    """Verify _parse_response correctly maps Docling Serve JSON to ConversionResult."""

    def test_minimal_response(self):
        data = {
            "document": {
                "md_content": "# Hello",
                "html_content": "<h1>Hello</h1>",
                "pages": {"1": {"size": {"width": 612.0, "height": 792.0}}},
            }
        }

        result = _parse_response(data)

        assert isinstance(result, ConversionResult)
        assert result.content_markdown == "# Hello"
        assert result.content_html == "<h1>Hello</h1>"
        assert result.page_count == 1
        assert len(result.pages) == 1
        assert result.pages[0].width == 612.0
        assert result.pages[0].height == 792.0

    def test_multi_page_response(self):
        data = {
            "document": {
                "md_content": "text",
                "html_content": "<p>text</p>",
                "pages": {
                    "1": {"size": {"width": 612.0, "height": 792.0}},
                    "2": {"size": {"width": 595.0, "height": 842.0}},
                },
            }
        }

        result = _parse_response(data)
        assert result.page_count == 2
        assert result.pages[0].page_number == 1
        assert result.pages[1].page_number == 2
        assert result.pages[1].width == 595.0  # A4

    def test_response_with_body_elements(self):
        data = {
            "document": {
                "md_content": "# Title\nSome text",
                "html_content": "<h1>Title</h1><p>Some text</p>",
                "pages": {"1": {"size": {"width": 612.0, "height": 792.0}}},
                "body": [
                    {
                        "type": "title",
                        "text": "Title",
                        "level": 1,
                        "prov": [{"page_no": 1, "bbox": {"l": 10, "t": 20, "r": 200, "b": 40}}],
                    },
                    {
                        "type": "text",
                        "text": "Some text",
                        "level": 0,
                        "prov": [{"page_no": 1, "bbox": {"l": 10, "t": 50, "r": 200, "b": 70}}],
                    },
                ],
            }
        }

        result = _parse_response(data)
        assert len(result.pages[0].elements) == 2
        assert result.pages[0].elements[0].type == "title"
        assert result.pages[0].elements[0].content == "Title"
        assert result.pages[0].elements[0].bbox == [10, 20, 200, 40]
        assert result.pages[0].elements[1].type == "text"

    def test_empty_response(self):
        data = {"document": {"pages": {}}}
        result = _parse_response(data)
        assert result.content_markdown == ""
        assert result.content_html == ""
        assert result.page_count == 1  # fallback minimum

    def test_bbox_as_list(self):
        data = {
            "document": {
                "md_content": "",
                "html_content": "",
                "pages": {"1": {"size": {"width": 612.0, "height": 792.0}}},
                "body": [
                    {
                        "type": "text",
                        "text": "hello",
                        "prov": [{"page_no": 1, "bbox": [10.0, 20.0, 200.0, 40.0]}],
                    },
                ],
            }
        }
        result = _parse_response(data)
        assert result.pages[0].elements[0].bbox == [10.0, 20.0, 200.0, 40.0]


# ---------------------------------------------------------------------------
# Unit tests — item type mapping
# ---------------------------------------------------------------------------

class TestMapItemType:
    @pytest.mark.parametrize("input_type,expected", [
        ("table", "table"),
        ("picture", "picture"),
        ("figure", "picture"),
        ("title", "title"),
        ("section_header", "section_header"),
        ("section-header", "section_header"),
        ("list_item", "list"),
        ("formula", "formula"),
        ("equation", "formula"),
        ("code", "code"),
        ("text", "text"),
        ("paragraph", "text"),
        ("unknown_type", "text"),
    ])
    def test_type_mapping(self, input_type, expected):
        assert _map_item_type({"type": input_type}) == expected

    def test_missing_type_defaults_to_text(self):
        assert _map_item_type({}) == "text"


# ---------------------------------------------------------------------------
# Unit tests — ServeConverter
# ---------------------------------------------------------------------------

class TestServeConverter:
    def test_headers_with_api_key(self):
        conv = ServeConverter(base_url="http://localhost:5001", api_key="secret")
        assert conv._headers() == {"X-Api-Key": "secret"}

    def test_headers_without_api_key(self):
        conv = ServeConverter(base_url="http://localhost:5001")
        assert conv._headers() == {}

    def test_build_conversion_options(self):
        conv = ServeConverter(base_url="http://localhost:5001")
        opts = ConversionOptions(do_ocr=False, table_mode="fast", images_scale=2.0)

        result = conv._build_conversion_options(opts)

        assert result["do_ocr"] is False
        assert result["table_mode"] == "fast"
        assert result["images_scale"] == 2.0
        assert result["to_formats"] == ["md", "html"]

    def test_base_url_trailing_slash_stripped(self):
        conv = ServeConverter(base_url="http://localhost:5001/")
        assert conv._base_url == "http://localhost:5001"


# ---------------------------------------------------------------------------
# Integration tests — HTTP calls (mocked)
# ---------------------------------------------------------------------------

class TestServeConverterConvert:
    @pytest.mark.asyncio
    async def test_successful_conversion(self, tmp_path):
        # Create a temp file to "upload"
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"%PDF-1.4 fake content")

        serve_response = {
            "document": {
                "md_content": "# Converted",
                "html_content": "<h1>Converted</h1>",
                "pages": {"1": {"size": {"width": 612.0, "height": 792.0}}},
                "body": [
                    {
                        "type": "title",
                        "text": "Converted",
                        "prov": [{"page_no": 1, "bbox": {"l": 10, "t": 20, "r": 200, "b": 40}}],
                    },
                ],
            }
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = serve_response
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        conv = ServeConverter(base_url="http://localhost:5001", api_key="test-key")

        with patch("infra.serve_converter.httpx.AsyncClient", return_value=mock_client):
            result = await conv.convert(str(test_file), ConversionOptions())

        assert isinstance(result, ConversionResult)
        assert result.content_markdown == "# Converted"
        assert result.page_count == 1
        assert len(result.pages[0].elements) == 1

        # Verify the HTTP call
        mock_client.post.assert_called_once()
        call_kwargs = mock_client.post.call_args
        assert "/v1/convert/file" in call_kwargs[0][0]

    @pytest.mark.asyncio
    async def test_http_error_raises(self, tmp_path):
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"%PDF-1.4 fake content")

        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Server Error", request=MagicMock(), response=MagicMock(status_code=500),
        )

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        conv = ServeConverter(base_url="http://localhost:5001")

        with patch("infra.serve_converter.httpx.AsyncClient", return_value=mock_client):
            with pytest.raises(httpx.HTTPStatusError):
                await conv.convert(str(test_file), ConversionOptions())

    @pytest.mark.asyncio
    async def test_health_check_success(self):
        mock_response = MagicMock()
        mock_response.status_code = 200

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        conv = ServeConverter(base_url="http://localhost:5001")

        with patch("infra.serve_converter.httpx.AsyncClient", return_value=mock_client):
            assert await conv.health_check() is True

    @pytest.mark.asyncio
    async def test_health_check_failure(self):
        mock_client = AsyncMock()
        mock_client.get.side_effect = httpx.ConnectError("Connection refused")
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        conv = ServeConverter(base_url="http://localhost:5001")

        with patch("infra.serve_converter.httpx.AsyncClient", return_value=mock_client):
            assert await conv.health_check() is False


# ---------------------------------------------------------------------------
# Integration — converter wiring in main.py
# ---------------------------------------------------------------------------

class TestConverterWiring:
    def test_local_engine_builds_local_converter(self):
        from infra.local_converter import LocalConverter
        from infra.settings import Settings
        from main import _build_converter

        with patch("main.settings", Settings(conversion_engine="local")):
            converter = _build_converter()
        assert isinstance(converter, LocalConverter)

    def test_remote_engine_builds_serve_converter(self):
        from infra.settings import Settings
        from main import _build_converter

        with patch("main.settings", Settings(conversion_engine="remote", docling_serve_url="http://serve:5001")):
            converter = _build_converter()
        assert isinstance(converter, ServeConverter)
        assert converter._base_url == "http://serve:5001"

    def test_remote_engine_passes_api_key(self):
        from infra.settings import Settings
        from main import _build_converter

        with patch("main.settings", Settings(conversion_engine="remote", docling_serve_url="http://serve:5001", docling_serve_api_key="my-key")):
            converter = _build_converter()
        assert isinstance(converter, ServeConverter)
        assert converter._api_key == "my-key"
