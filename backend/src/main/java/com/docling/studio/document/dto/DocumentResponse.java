package com.docling.studio.document.dto;

import com.docling.studio.document.Document;
import java.time.Instant;
import java.util.UUID;

public record DocumentResponse(
        UUID id,
        String filename,
        String contentType,
        Long fileSize,
        Integer pageCount,
        Instant createdAt
) {
    public static DocumentResponse from(Document doc) {
        return new DocumentResponse(
                doc.getId(), doc.getFilename(), doc.getContentType(),
                doc.getFileSize(), doc.getPageCount(), doc.getCreatedAt()
        );
    }
}
