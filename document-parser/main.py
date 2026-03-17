"""Docling Studio — Document Parser service.

A FastAPI microservice wrapping the Docling library for structured document
extraction. Provides parse (full extraction) and preview (page image) endpoints
with configurable pipeline options.
"""

import io
import logging
import os
import tempfile
import threading
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, UploadFile, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from pdf2image import convert_from_bytes

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
    TableFormerMode,
    TableStructureOptions,
)
from docling_core.types.doc import (
    CodeItem,
    FloatingItem,
    FormulaItem,
    GroupItem,
    ListItem,
    PictureItem,
    SectionHeaderItem,
    TableItem,
    TextItem,
    TitleItem,
)

from bbox import to_topleft_list

logger = logging.getLogger(__name__)

app = FastAPI(title="Docling Studio — Document Parser")

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

# Thread lock for converter — DocumentConverter is not thread-safe
_converter_lock = threading.Lock()


# ---------------------------------------------------------------------------
# Pipeline factory
# ---------------------------------------------------------------------------

def _build_converter(
    do_ocr: bool = True,
    do_table_structure: bool = True,
    table_mode: str = "accurate",
) -> DocumentConverter:
    """Build a DocumentConverter with the given pipeline options.

    Only exposes options that work out of the box (no extra model downloads).
    """
    table_options = TableStructureOptions(
        do_cell_matching=True,
        mode=TableFormerMode.ACCURATE if table_mode == "accurate" else TableFormerMode.FAST,
    )

    pipeline_options = PdfPipelineOptions(
        do_ocr=do_ocr,
        do_table_structure=do_table_structure,
        table_structure_options=table_options,
        # These require VLM model downloads — disabled by default
        do_code_enrichment=False,
        do_formula_enrichment=False,
        do_picture_classification=False,
        do_picture_description=False,
        # Page images are handled by pdf2image in /preview, not needed here
        generate_page_images=False,
        generate_picture_images=False,
    )

    return DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options),
        }
    )


# Default converter (lazy-init on first request)
_default_converter: Optional[DocumentConverter] = None


def _get_default_converter() -> DocumentConverter:
    global _default_converter
    if _default_converter is None:
        _default_converter = _build_converter()
    return _default_converter


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------

class PageElement(BaseModel):
    type: str
    bbox: list[float]
    content: str
    level: int = 0  # Hierarchy depth from iterate_items()


class PageDetail(BaseModel):
    page_number: int
    width: float
    height: float
    elements: list[PageElement]


class ParseResponse(BaseModel):
    filename: str
    page_count: int
    content_markdown: str
    content_html: str
    pages: list[PageDetail]
    skipped_items: int = 0  # Transparency on extraction failures


# ---------------------------------------------------------------------------
# Element type detection — isinstance-based (no string matching)
# ---------------------------------------------------------------------------

def _get_element_type(item) -> str:
    """Determine the element type using isinstance checks on Docling classes.

    Order matters: more specific types are checked before their parent classes.
    """
    if isinstance(item, TableItem):
        return "table"
    if isinstance(item, PictureItem):
        return "picture"
    if isinstance(item, TitleItem):
        return "title"
    if isinstance(item, SectionHeaderItem):
        return "section_header"
    if isinstance(item, ListItem):
        return "list"
    if isinstance(item, FormulaItem):
        return "formula"
    if isinstance(item, CodeItem):
        return "code"
    if isinstance(item, FloatingItem):
        return "floating"
    if isinstance(item, GroupItem):
        return "group"
    if isinstance(item, TextItem):
        return "text"
    return "text"


# ---------------------------------------------------------------------------
# Page extraction
# ---------------------------------------------------------------------------

def extract_pages_detail(doc_result) -> tuple[list[PageDetail], int]:
    """Extract per-page element details with bounding boxes from Docling result.

    Returns (pages, skipped_count) for transparent error reporting.
    """
    pages: dict[int, PageDetail] = {}
    document = doc_result.document
    skipped = 0

    # Populate page dimensions from document metadata
    if hasattr(document, "pages") and document.pages:
        for page_key, page_obj in document.pages.items():
            page_no = int(page_key) if isinstance(page_key, str) else page_key
            width = page_obj.size.width if hasattr(page_obj, "size") and page_obj.size else 612.0
            height = page_obj.size.height if hasattr(page_obj, "size") and page_obj.size else 792.0
            pages[page_no] = PageDetail(
                page_number=page_no, width=width, height=height, elements=[]
            )

    # Use iterate_items() — the Docling v2 API that yields (item, level)
    if hasattr(document, "iterate_items"):
        for item, level in document.iterate_items():
            ok = _process_content_item(item, level, pages)
            if not ok:
                skipped += 1
    elif hasattr(document, "texts"):
        for text_item in document.texts:
            ok = _process_content_item(text_item, 0, pages)
            if not ok:
                skipped += 1

    sorted_pages = sorted(pages.values(), key=lambda p: p.page_number)
    return sorted_pages, skipped


def _process_content_item(item, level: int, pages: dict[int, PageDetail]) -> bool:
    """Process a single content item and add it to the appropriate page.

    Returns True on success, False if the item was skipped.
    """
    # Skip groups and items without provenance
    if isinstance(item, GroupItem):
        return True  # Groups are structural, not content — not an error
    if not hasattr(item, "prov") or not item.prov:
        return False

    for prov in item.prov:
        try:
            page_no = prov.page_no if hasattr(prov, "page_no") else 1

            if page_no not in pages:
                pages[page_no] = PageDetail(
                    page_number=page_no, width=612.0, height=792.0, elements=[]
                )

            page_height = pages[page_no].height

            bbox = [0.0, 0.0, 0.0, 0.0]
            if hasattr(prov, "bbox") and prov.bbox:
                b = prov.bbox
                if hasattr(b, "l"):
                    bbox = to_topleft_list(b, page_height)
                elif isinstance(b, (list, tuple)) and len(b) >= 4:
                    bbox = list(b[:4])

            element_type = _get_element_type(item)

            content = ""
            if hasattr(item, "text"):
                content = item.text or ""
            # For tables, try to export structured content
            if isinstance(item, TableItem) and hasattr(item, "export_to_markdown"):
                try:
                    content = item.export_to_markdown()
                except Exception:
                    pass  # Fall back to .text

            pages[page_no].elements.append(
                PageElement(
                    type=element_type,
                    bbox=bbox,
                    content=content,
                    level=level,
                )
            )
        except Exception:
            logger.warning(
                "Skipping item %s on page %s",
                type(item).__name__,
                getattr(prov, "page_no", "?"),
                exc_info=True,
            )
            return False

    return True


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.post("/parse", response_model=ParseResponse)
async def parse(
    file: UploadFile,
    do_ocr: bool = Query(True, description="Enable OCR for scanned documents"),
    do_table_structure: bool = Query(True, description="Enable table structure extraction"),
    table_mode: str = Query("accurate", regex="^(accurate|fast)$", description="Table extraction mode"),
):
    """Parse a document and return structured content with per-page elements."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 50 MB)")

    suffix = Path(file.filename).suffix
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(file_content)
            tmp_path = tmp.name

        # Build converter with requested options (or reuse default)
        if do_ocr and do_table_structure and table_mode == "accurate":
            conv = _get_default_converter()
        else:
            conv = _build_converter(
                do_ocr=do_ocr,
                do_table_structure=do_table_structure,
                table_mode=table_mode,
            )

        with _converter_lock:
            result = conv.convert(tmp_path)

        doc = result.document

        content_markdown = doc.export_to_markdown()
        content_html = doc.export_to_html() if hasattr(doc, "export_to_html") else ""

        page_count = len(doc.pages) if hasattr(doc, "pages") and doc.pages else 0

        pages_detail, skipped = extract_pages_detail(result)

        # Ensure we have page entries even if no elements were extracted
        if not pages_detail and page_count > 0:
            pages_detail = [
                PageDetail(page_number=i + 1, width=612.0, height=792.0, elements=[])
                for i in range(page_count)
            ]

        if skipped > 0:
            logger.info(
                "Parsed %s: %d pages, %d items skipped",
                file.filename,
                page_count,
                skipped,
            )

        return ParseResponse(
            filename=file.filename,
            page_count=page_count or len(pages_detail) or 1,
            content_markdown=content_markdown,
            content_html=content_html,
            pages=pages_detail,
            skipped_items=skipped,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to parse document: %s", file.filename)
        raise HTTPException(status_code=422, detail=f"Failed to parse document: {e}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except OSError:
                logger.warning("Could not delete temp file: %s", tmp_path)


@app.post("/preview")
async def preview(
    file: UploadFile,
    page: int = Query(1, ge=1),
    dpi: int = Query(150, ge=72, le=300),
):
    """Generate a PNG preview of a specific PDF page."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 50 MB)")

    try:
        images = convert_from_bytes(file_content, first_page=page, last_page=page, dpi=dpi)
        if not images:
            raise HTTPException(status_code=404, detail=f"Page {page} not found")

        buf = io.BytesIO()
        images[0].save(buf, format="PNG")
        buf.seek(0)
        return StreamingResponse(buf, media_type="image/png")

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to generate preview for page %d", page)
        raise HTTPException(status_code=422, detail=f"Failed to generate preview: {e}")


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}
