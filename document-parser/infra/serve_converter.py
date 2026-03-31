"""Remote Docling Serve converter — delegates conversion via HTTP.

This adapter implements the DocumentConverter port by calling a remote
Docling Serve instance's REST API. It supports both synchronous and
asynchronous conversion endpoints.
"""

from __future__ import annotations

import logging
import mimetypes
from pathlib import Path

import httpx

from domain.value_objects import (
    ConversionOptions,
    ConversionResult,
    PageDetail,
    PageElement,
)

logger = logging.getLogger(__name__)

# Docling Serve API base path
_API_PREFIX = "/v1"

# Default timeout for HTTP requests (seconds)
_DEFAULT_TIMEOUT = 600.0


class ServeConverter:
    """Adapter that delegates document conversion to a remote Docling Serve instance."""

    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        timeout: float = _DEFAULT_TIMEOUT,
    ):
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._timeout = timeout

    def _headers(self) -> dict[str, str]:
        headers: dict[str, str] = {}
        if self._api_key:
            headers["X-Api-Key"] = self._api_key
        return headers

    def _build_conversion_options(self, options: ConversionOptions) -> dict:
        """Map our ConversionOptions to Docling Serve's expected format."""
        opts: dict = {
            "to_formats": ["md", "html"],
            "do_ocr": options.do_ocr,
            "do_table_structure": options.do_table_structure,
            "table_mode": options.table_mode,
            "do_code_enrichment": options.do_code_enrichment,
            "do_formula_enrichment": options.do_formula_enrichment,
            "do_picture_classification": options.do_picture_classification,
            "do_picture_description": options.do_picture_description,
            "images_scale": options.images_scale,
        }
        return opts

    async def convert(
        self, file_path: str, options: ConversionOptions,
    ) -> ConversionResult:
        """Convert a document by uploading it to Docling Serve."""
        path = Path(file_path)
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"

        conversion_opts = self._build_conversion_options(options)

        url = f"{self._base_url}{_API_PREFIX}/convert/file"

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            with open(path, "rb") as f:
                files = {"files": (path.name, f, content_type)}
                data = {"options": _serialize_options(conversion_opts)}

                logger.info("Sending conversion request to %s", url)
                response = await client.post(
                    url,
                    files=files,
                    data=data,
                    headers=self._headers(),
                )

            response.raise_for_status()
            result_data = response.json()

        return _parse_response(result_data)

    async def health_check(self) -> bool:
        """Check if Docling Serve is reachable."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"{self._base_url}/version",
                    headers=self._headers(),
                )
                return resp.status_code == 200
        except httpx.HTTPError:
            return False


def _serialize_options(opts: dict) -> str:
    """Serialize conversion options to JSON string for multipart form."""
    import json
    return json.dumps(opts)


def _parse_response(data: dict) -> ConversionResult:
    """Parse Docling Serve JSON response into our domain ConversionResult.

    Docling Serve returns a DoclingDocument structure. The response format
    contains document content and page-level information with bounding boxes.
    """
    document = data.get("document", data)

    # Extract markdown and HTML content
    content_md = ""
    content_html = ""

    # Docling Serve may return content in different formats
    if "md_content" in document:
        content_md = document["md_content"]
    elif "export_to_markdown" in document:
        content_md = document["export_to_markdown"]

    if "html_content" in document:
        content_html = document["html_content"]
    elif "export_to_html" in document:
        content_html = document["export_to_html"]

    # Parse pages
    pages = _extract_pages(document)
    page_count = len(pages) if pages else 1

    return ConversionResult(
        page_count=page_count,
        content_markdown=content_md,
        content_html=content_html,
        pages=pages,
    )


def _extract_pages(document: dict) -> list[PageDetail]:
    """Extract page details with elements from Docling Serve response."""
    pages_dict: dict[int, PageDetail] = {}

    # Extract page dimensions from pages metadata
    raw_pages = document.get("pages", {})
    for page_key, page_data in raw_pages.items():
        page_no = int(page_key)
        size = page_data.get("size", {})
        pages_dict[page_no] = PageDetail(
            page_number=page_no,
            width=size.get("width", 612.0),
            height=size.get("height", 792.0),
        )

    # Extract elements from the document body
    body = document.get("body", document.get("main_text", []))
    if isinstance(body, list):
        for item in body:
            _process_serve_item(item, pages_dict, document)

    return sorted(pages_dict.values(), key=lambda p: p.page_number)


def _process_serve_item(
    item: dict, pages: dict[int, PageDetail], document: dict,
) -> None:
    """Process a single item from Docling Serve response body."""
    prov_list = item.get("prov", [])
    if not prov_list:
        return

    item_type = _map_item_type(item)
    content = item.get("text", "")
    level = item.get("level", 0)

    for prov in prov_list:
        page_no = prov.get("page_no", prov.get("page", 1))
        if page_no not in pages:
            pages[page_no] = PageDetail(
                page_number=page_no, width=612.0, height=792.0,
            )

        bbox_data = prov.get("bbox", {})
        if isinstance(bbox_data, dict):
            bbox = [
                bbox_data.get("l", 0.0),
                bbox_data.get("t", 0.0),
                bbox_data.get("r", 0.0),
                bbox_data.get("b", 0.0),
            ]
        elif isinstance(bbox_data, list) and len(bbox_data) == 4:
            bbox = [float(v) for v in bbox_data]
        else:
            bbox = [0.0, 0.0, 0.0, 0.0]

        pages[page_no].elements.append(
            PageElement(type=item_type, bbox=bbox, content=content, level=level)
        )


def _map_item_type(item: dict) -> str:
    """Map Docling Serve item type to our element type string."""
    item_type = item.get("type", item.get("obj_type", "text"))
    type_mapping = {
        "table": "table",
        "picture": "picture",
        "figure": "picture",
        "title": "title",
        "section_header": "section_header",
        "section-header": "section_header",
        "list_item": "list",
        "list": "list",
        "formula": "formula",
        "equation": "formula",
        "code": "code",
        "floating": "floating",
        "text": "text",
        "paragraph": "text",
    }
    return type_mapping.get(item_type.lower(), "text") if item_type else "text"
