"""Document repository — SQLite CRUD for documents table."""

from __future__ import annotations

from domain.models import Document
from persistence.database import get_db


def _row_to_document(row) -> Document:
    return Document(
        id=row["id"],
        filename=row["filename"],
        content_type=row["content_type"],
        file_size=row["file_size"],
        page_count=row["page_count"],
        storage_path=row["storage_path"],
        created_at=row["created_at"],
    )


async def insert(doc: Document) -> None:
    db = await get_db()
    try:
        await db.execute(
            """INSERT INTO documents (id, filename, content_type, file_size, page_count, storage_path, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (doc.id, doc.filename, doc.content_type, doc.file_size,
             doc.page_count, doc.storage_path, str(doc.created_at)),
        )
        await db.commit()
    finally:
        await db.close()


async def find_all() -> list[Document]:
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM documents ORDER BY created_at DESC"
        )
        rows = await cursor.fetchall()
        return [_row_to_document(r) for r in rows]
    finally:
        await db.close()


async def find_by_id(doc_id: str) -> Document | None:
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
        row = await cursor.fetchone()
        return _row_to_document(row) if row else None
    finally:
        await db.close()


async def update_page_count(doc_id: str, page_count: int) -> None:
    db = await get_db()
    try:
        await db.execute(
            "UPDATE documents SET page_count = ? WHERE id = ?",
            (page_count, doc_id),
        )
        await db.commit()
    finally:
        await db.close()


async def delete(doc_id: str) -> bool:
    db = await get_db()
    try:
        cursor = await db.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        await db.commit()
        return cursor.rowcount > 0
    finally:
        await db.close()
