package com.docling.studio.analysis;

import com.docling.studio.analysis.dto.AnalysisResponse;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/analyses")
public class AnalysisController {

    private final AnalysisService service;

    public AnalysisController(AnalysisService service) {
        this.service = service;
    }

    @PostMapping
    public AnalysisResponse create(@RequestBody Map<String, String> body) {
        UUID documentId = UUID.fromString(body.get("documentId"));
        AnalysisJob job = service.create(documentId);
        return AnalysisResponse.from(job);
    }

    @GetMapping
    public List<AnalysisResponse> list() {
        return service.findAll().stream().map(AnalysisResponse::from).toList();
    }

    @GetMapping("/{id}")
    public AnalysisResponse get(@PathVariable UUID id) {
        return AnalysisResponse.from(service.findById(id));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable UUID id) {
        service.delete(id);
        return ResponseEntity.noContent().build();
    }
}
