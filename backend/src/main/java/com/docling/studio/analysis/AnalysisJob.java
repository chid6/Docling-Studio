package com.docling.studio.analysis;

import com.docling.studio.document.Document;
import jakarta.persistence.*;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "analysis_jobs")
public class AnalysisJob {

    public enum Status { PENDING, RUNNING, COMPLETED, FAILED }

    @Id
    private UUID id;

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "document_id", nullable = false)
    private Document document;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Status status;

    @Column(columnDefinition = "text")
    private String contentMarkdown;

    @Column(columnDefinition = "text")
    private String contentHtml;

    @Column(columnDefinition = "text")
    private String pagesJson;

    private String errorMessage;

    private Instant startedAt;
    private Instant completedAt;
    private Instant createdAt;

    protected AnalysisJob() {}

    public AnalysisJob(Document document) {
        this.id = UUID.randomUUID();
        this.document = document;
        this.status = Status.PENDING;
        this.createdAt = Instant.now();
    }

    public void markRunning() {
        this.status = Status.RUNNING;
        this.startedAt = Instant.now();
    }

    public void markCompleted(String markdown, String html, String pagesJson) {
        this.status = Status.COMPLETED;
        this.contentMarkdown = markdown;
        this.contentHtml = html;
        this.pagesJson = pagesJson;
        this.completedAt = Instant.now();
    }

    public void markFailed(String error) {
        this.status = Status.FAILED;
        this.errorMessage = error;
        this.completedAt = Instant.now();
    }

    public UUID getId() { return id; }
    public Document getDocument() { return document; }
    public Status getStatus() { return status; }
    public String getContentMarkdown() { return contentMarkdown; }
    public String getContentHtml() { return contentHtml; }
    public String getPagesJson() { return pagesJson; }
    public String getErrorMessage() { return errorMessage; }
    public Instant getStartedAt() { return startedAt; }
    public Instant getCompletedAt() { return completedAt; }
    public Instant getCreatedAt() { return createdAt; }
}
