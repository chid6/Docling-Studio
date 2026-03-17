package com.docling.studio.analysis;

import com.docling.studio.document.Document;
import com.docling.studio.document.DocumentParserClient;
import com.docling.studio.document.DocumentService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Component;

import java.nio.file.Path;
import java.util.Map;
import java.util.UUID;

/**
 * Separated from AnalysisService so that Spring's @Async proxy works correctly.
 * (Self-invocation within the same class bypasses the AOP proxy.)
 */
@Component
public class AnalysisRunner {

    private static final Logger log = LoggerFactory.getLogger(AnalysisRunner.class);

    private final AnalysisJobRepository repository;
    private final DocumentService documentService;
    private final DocumentParserClient parserClient;
    private final ObjectMapper objectMapper;

    public AnalysisRunner(
            AnalysisJobRepository repository,
            DocumentService documentService,
            DocumentParserClient parserClient,
            ObjectMapper objectMapper
    ) {
        this.repository = repository;
        this.documentService = documentService;
        this.parserClient = parserClient;
        this.objectMapper = objectMapper;
    }

    @Async("analysisExecutor")
    public void runAnalysis(UUID jobId) {
        AnalysisJob job = repository.findById(jobId).orElseThrow();
        job.markRunning();
        repository.save(job);

        log.info("Starting analysis for document: {}", job.getDocument().getFilename());

        try {
            Path filePath = documentService.getFilePath(job.getDocument().getId());
            Map<String, Object> result = parserClient.parse(filePath, job.getDocument().getFilename());

            String markdown = (String) result.getOrDefault("content_markdown", "");
            String html = (String) result.getOrDefault("content_html", "");
            Object pages = result.get("pages");
            String pagesJson = pages != null ? objectMapper.writeValueAsString(pages) : "[]";

            // Update page count on document if available
            Object pageCount = result.get("page_count");
            if (pageCount instanceof Number n && n.intValue() > 0) {
                Document doc = job.getDocument();
                doc.setPageCount(n.intValue());
                documentService.save(doc);
            }

            job.markCompleted(markdown, html, pagesJson);
            repository.save(job);

            log.info("Analysis completed for document: {}", job.getDocument().getFilename());

        } catch (Exception e) {
            log.error("Analysis failed for document: {}", job.getDocument().getFilename(), e);
            job.markFailed(e.getMessage());
            repository.save(job);
        }
    }
}
