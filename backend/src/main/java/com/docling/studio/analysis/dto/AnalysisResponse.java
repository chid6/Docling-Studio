package com.docling.studio.analysis.dto;

import com.docling.studio.analysis.AnalysisJob;
import java.time.Instant;
import java.util.UUID;

public record AnalysisResponse(
        UUID id,
        UUID documentId,
        String documentFilename,
        String status,
        String contentMarkdown,
        String contentHtml,
        String pagesJson,
        String errorMessage,
        Instant startedAt,
        Instant completedAt,
        Instant createdAt
) {
    public static AnalysisResponse from(AnalysisJob job) {
        return new AnalysisResponse(
                job.getId(),
                job.getDocument().getId(),
                job.getDocument().getFilename(),
                job.getStatus().name(),
                job.getContentMarkdown(),
                job.getContentHtml(),
                job.getPagesJson(),
                job.getErrorMessage(),
                job.getStartedAt(),
                job.getCompletedAt(),
                job.getCreatedAt()
        );
    }
}
