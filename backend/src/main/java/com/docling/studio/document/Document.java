package com.docling.studio.document;

import jakarta.persistence.*;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "documents")
public class Document {

    @Id
    private UUID id;

    @Column(nullable = false)
    private String filename;

    private String contentType;

    private Long fileSize;

    private Integer pageCount;

    @Column(nullable = false)
    private String storagePath;

    private Instant createdAt;

    protected Document() {}

    public Document(String filename, String contentType, Long fileSize, String storagePath) {
        this.id = UUID.randomUUID();
        this.filename = filename;
        this.contentType = contentType;
        this.fileSize = fileSize;
        this.storagePath = storagePath;
        this.createdAt = Instant.now();
    }

    public UUID getId() { return id; }
    public String getFilename() { return filename; }
    public String getContentType() { return contentType; }
    public Long getFileSize() { return fileSize; }
    public Integer getPageCount() { return pageCount; }
    public void setPageCount(Integer pageCount) { this.pageCount = pageCount; }
    public String getStoragePath() { return storagePath; }
    public Instant getCreatedAt() { return createdAt; }
}
