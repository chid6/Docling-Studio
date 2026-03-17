package com.docling.studio.analysis;

import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface AnalysisJobRepository extends JpaRepository<AnalysisJob, UUID> {
    List<AnalysisJob> findAllByOrderByCreatedAtDesc();
    List<AnalysisJob> findByDocumentIdOrderByCreatedAtDesc(UUID documentId);
}
