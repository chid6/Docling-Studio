"""Pydantic schemas — API request/response DTOs.

All responses use camelCase serialization to match the existing frontend contract
(originally served by the Spring Boot backend).
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


def _to_camel(name: str) -> str:
    parts = name.split("_")
    return parts[0] + "".join(w.capitalize() for w in parts[1:])


class _CamelModel(BaseModel):
    """Base model that serializes field names to camelCase."""
    model_config = ConfigDict(
        alias_generator=_to_camel,
        populate_by_name=True,
        serialize_by_alias=True,
    )


class DocumentResponse(_CamelModel):
    id: str
    filename: str
    content_type: str | None = None
    file_size: int | None = None
    page_count: int | None = None
    created_at: str | datetime


class AnalysisResponse(_CamelModel):
    id: str
    document_id: str = ""
    document_filename: str | None = None
    status: str
    content_markdown: str | None = None
    content_html: str | None = None
    pages_json: str | None = None
    error_message: str | None = None
    started_at: str | datetime | None = None
    completed_at: str | datetime | None = None
    created_at: str | datetime


class CreateAnalysisRequest(BaseModel):
    documentId: str  # camelCase to match existing frontend contract
