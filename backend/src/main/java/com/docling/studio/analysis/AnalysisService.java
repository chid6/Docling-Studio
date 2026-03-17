package com.docling.studio.analysis;

import com.docling.studio.document.Document;
import com.docling.studio.document.DocumentService;
import com.docling.studio.shared.exception.ResourceNotFoundException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.UUID;

@Service
public class AnalysisService {

    private final AnalysisJobRepository repository;
    private final DocumentService documentService;
    private final AnalysisRunner runner;

    public AnalysisService(
            AnalysisJobRepository repository,
            DocumentService documentService,
            AnalysisRunner runner
    ) {
        this.repository = repository;
        this.documentService = documentService;
        this.runner = runner;
    }

    @Transactional
    public AnalysisJob create(UUID documentId) {
        Document doc = documentService.findById(documentId);
        AnalysisJob job = new AnalysisJob(doc);
        repository.save(job);
        // Delegate to a separate bean so @Async proxy works (no self-invocation)
        runner.runAnalysis(job.getId());
        return job;
    }

    @Transactional(readOnly = true)
    public AnalysisJob findById(UUID id) {
        return repository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Analysis not found: " + id));
    }

    @Transactional(readOnly = true)
    public List<AnalysisJob> findAll() {
        return repository.findAllByOrderByCreatedAtDesc();
    }

    @Transactional
    public void delete(UUID id) {
        AnalysisJob job = findById(id);
        repository.delete(job);
    }
}
