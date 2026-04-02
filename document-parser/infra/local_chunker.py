"""Local Docling chunker — runs chunking in-process using docling-core.

This adapter implements the DocumentChunker port. It deserializes a
DoclingDocument from JSON, applies the requested chunker, and returns
domain ChunkResult objects.
"""

from __future__ import annotations

import asyncio
import json
import logging

from docling_core.transforms.chunker import HierarchicalChunker
from docling_core.transforms.chunker.hybrid_chunker import HybridChunker
from docling_core.types.doc.document import DoclingDocument

from domain.value_objects import ChunkingOptions, ChunkResult

logger = logging.getLogger(__name__)


def _chunk_sync(document_json: str, options: ChunkingOptions) -> list[ChunkResult]:
    if not document_json or not document_json.strip():
        raise ValueError("Empty document JSON — nothing to chunk")

    try:
        doc_data = json.loads(document_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Malformed document JSON: {e}") from e

    doc = DoclingDocument.model_validate(doc_data)

    chunker = _build_chunker(options)
    results: list[ChunkResult] = []

    for chunk in chunker.chunk(doc):
        source_page = None
        token_count = 0

        if hasattr(chunk, "meta") and chunk.meta and chunk.meta.doc_items:
            for doc_item in chunk.meta.doc_items:
                if hasattr(doc_item, "prov") and doc_item.prov:
                    source_page = doc_item.prov[0].page_no
                    break

        if hasattr(chunker, "tokenizer") and chunker.tokenizer:
            token_count = chunker.tokenizer.count_tokens(chunk.text)

        headings = list(chunk.meta.headings) if chunk.meta and chunk.meta.headings else []

        results.append(
            ChunkResult(
                text=chunk.text,
                headings=headings,
                source_page=source_page,
                token_count=token_count,
            )
        )

    logger.info("Chunked document into %d chunks (chunker=%s)", len(results), options.chunker_type)
    return results


def _build_chunker(options: ChunkingOptions) -> HierarchicalChunker | HybridChunker:
    if options.chunker_type == "hierarchical":
        return HierarchicalChunker()

    return HybridChunker(
        max_tokens=options.max_tokens,
        merge_peers=options.merge_peers,
        repeat_table_header=options.repeat_table_header,
    )


class LocalChunker:
    """Adapter that runs docling-core chunking locally."""

    async def chunk(
        self,
        document_json: str,
        options: ChunkingOptions,
    ) -> list[ChunkResult]:
        return await asyncio.to_thread(_chunk_sync, document_json, options)
