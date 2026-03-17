"""Tests for bbox coordinate normalization."""

import pytest
from docling_core.types.doc.base import BoundingBox, CoordOrigin

from domain.bbox import to_topleft_list


class TestToTopleftList:
    """Tests for to_topleft_list conversion."""

    def test_topleft_origin_unchanged(self):
        """TOPLEFT bbox should pass through unchanged."""
        bbox = BoundingBox(l=10, t=20, r=100, b=80, coord_origin=CoordOrigin.TOPLEFT)
        result = to_topleft_list(bbox, page_height=792.0)
        assert result == [10, 20, 100, 80]

    def test_bottomleft_origin_converted(self):
        """BOTTOMLEFT bbox should have y-coordinates flipped."""
        # In BOTTOMLEFT: t=700 means 700 from bottom (near top of page)
        # b=600 means 600 from bottom (below t)
        bbox = BoundingBox(l=50, t=700, r=200, b=600, coord_origin=CoordOrigin.BOTTOMLEFT)
        result = to_topleft_list(bbox, page_height=792.0)

        # After conversion: new_t = 792 - 700 = 92, new_b = 792 - 600 = 192
        assert result[0] == 50       # l unchanged
        assert result[1] == pytest.approx(92.0)   # t = page_height - old_t
        assert result[2] == 200      # r unchanged
        assert result[3] == pytest.approx(192.0)   # b = page_height - old_b

    def test_result_has_positive_dimensions(self):
        """Converted bbox should always have b > t (positive height)."""
        bbox = BoundingBox(l=10, t=500, r=300, b=100, coord_origin=CoordOrigin.BOTTOMLEFT)
        result = to_topleft_list(bbox, page_height=800.0)

        l, t, r, b = result
        assert r > l, "width should be positive"
        assert b > t, "height should be positive"

    def test_full_page_bbox_bottomleft(self):
        """A bbox covering the full page in BOTTOMLEFT origin."""
        bbox = BoundingBox(l=0, t=792, r=612, b=0, coord_origin=CoordOrigin.BOTTOMLEFT)
        result = to_topleft_list(bbox, page_height=792.0)
        assert result == [0, 0, 612, 792]

    def test_full_page_bbox_topleft(self):
        """A bbox covering the full page in TOPLEFT origin."""
        bbox = BoundingBox(l=0, t=0, r=612, b=792, coord_origin=CoordOrigin.TOPLEFT)
        result = to_topleft_list(bbox, page_height=792.0)
        assert result == [0, 0, 612, 792]
