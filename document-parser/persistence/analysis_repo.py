"""Analysis job repository — SQLite CRUD for analysis_jobs table."""

from __future__ import annotations

from domain.models import AnalysisJob, AnalysisStatus
from persistence.database import get_db


def _row_to_job(row) -> AnalysisJob:
    return AnalysisJob(
        id=row["id"],
        document_id=row["document_id"],
        status=AnalysisStatus(row["status"]),
        content_markdown=row["content_markdown"],
        content_html=row["content_html"],
        pages_json=row["pages_json"],
        error_message=row["error_message"],
        started_at=row["started_at"],
        completed_at=row["completed_at"],
        created_at=row["created_at"],
        document_filename=row["filename"] if "filename" in row.keys() else None,
    )


_SELECT_WITH_DOC = """
    SELECT aj.*, d.filename
    FROM analysis_jobs aj
    JOIN documents d ON d.id = aj.document_id
"""


async def insert(job: AnalysisJob) -> None:
    db = await get_db()
    try:
        await db.execute(
            """INSERT INTO analysis_jobs (id, document_id, status, created_at)
               VALUES (?, ?, ?, ?)""",
            (job.id, job.document_id, job.status.value, str(job.created_at)),
        )
        await db.commit()
    finally:
        await db.close()


async def find_all() -> list[AnalysisJob]:
    db = await get_db()
    try:
        cursor = await db.execute(
            f"{_SELECT_WITH_DOC} ORDER BY aj.created_at DESC"
        )
        rows = await cursor.fetchall()
        return [_row_to_job(r) for r in rows]
    finally:
        await db.close()


async def find_by_id(job_id: str) -> AnalysisJob | None:
    db = await get_db()
    try:
        cursor = await db.execute(
            f"{_SELECT_WITH_DOC} WHERE aj.id = ?", (job_id,)
        )
        row = await cursor.fetchone()
        return _row_to_job(row) if row else None
    finally:
        await db.close()


async def update_status(job: AnalysisJob) -> None:
    db = await get_db()
    try:
        await db.execute(
            """UPDATE analysis_jobs
               SET status = ?, content_markdown = ?, content_html = ?,
                   pages_json = ?, error_message = ?, started_at = ?, completed_at = ?
               WHERE id = ?""",
            (job.status.value, job.content_markdown, job.content_html,
             job.pages_json, job.error_message,
             str(job.started_at) if job.started_at else None,
             str(job.completed_at) if job.completed_at else None,
             job.id),
        )
        await db.commit()
    finally:
        await db.close()


async def delete(job_id: str) -> bool:
    db = await get_db()
    try:
        cursor = await db.execute("DELETE FROM analysis_jobs WHERE id = ?", (job_id,))
        await db.commit()
        return cursor.rowcount > 0
    finally:
        await db.close()


async def delete_by_document(document_id: str) -> int:
    """Delete all analysis jobs for a given document. Returns count deleted."""
    db = await get_db()
    try:
        cursor = await db.execute(
            "DELETE FROM analysis_jobs WHERE document_id = ?", (document_id,)
        )
        await db.commit()
        return cursor.rowcount
    finally:
        await db.close()
