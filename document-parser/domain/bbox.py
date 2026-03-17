"""Bounding box coordinate normalization for Docling output.

Docling's BoundingBox uses two possible coordinate origins:
- TOPLEFT:    y=0 at top,    t < b  (t is smaller, closer to origin)
- BOTTOMLEFT: y=0 at bottom, t > b  (t is larger, further from origin)

The frontend canvas uses TOPLEFT coordinates. This module ensures all
bboxes are normalized to TOPLEFT [left, top, right, bottom] before
being sent to the frontend.
"""

from docling_core.types.doc.base import BoundingBox


def to_topleft_list(bbox: BoundingBox, page_height: float) -> list[float]:
    """Convert a Docling BoundingBox to a [l, t, r, b] list in TOPLEFT origin.

    Args:
        bbox: Docling BoundingBox (any origin).
        page_height: Height of the page (needed for BOTTOMLEFT conversion).

    Returns:
        [left, top, right, bottom] in TOPLEFT coordinates.
    """
    normalized = bbox.to_top_left_origin(page_height)
    return [normalized.l, normalized.t, normalized.r, normalized.b]
