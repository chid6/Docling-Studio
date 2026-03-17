package com.docling.studio.document;

import com.docling.studio.config.DocumentParserProperties;
import com.docling.studio.shared.exception.ServiceException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.core.io.FileSystemResource;
import org.springframework.http.MediaType;
import org.springframework.http.client.MultipartBodyBuilder;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.BodyInserters;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientResponseException;

import java.nio.file.Path;
import java.time.Duration;
import java.util.Map;

@Component
public class DocumentParserClient {

    private static final Logger log = LoggerFactory.getLogger(DocumentParserClient.class);

    private final WebClient webClient;

    public DocumentParserClient(DocumentParserProperties props) {
        this.webClient = WebClient.builder()
                .baseUrl(props.getBaseUrl())
                .codecs(config -> config.defaultCodecs().maxInMemorySize(50 * 1024 * 1024))
                .build();
    }

    @SuppressWarnings("unchecked")
    public Map<String, Object> parse(Path filePath, String filename) {
        MultipartBodyBuilder builder = new MultipartBodyBuilder();
        builder.part("file", new FileSystemResource(filePath))
                .filename(filename)
                .contentType(MediaType.APPLICATION_PDF);

        try {
            return webClient.post()
                    .uri("/parse")
                    .body(BodyInserters.fromMultipartData(builder.build()))
                    .retrieve()
                    .bodyToMono(Map.class)
                    .block(Duration.ofMinutes(10));
        } catch (WebClientResponseException e) {
            log.error("Parser returned HTTP {}: {}", e.getStatusCode().value(), e.getResponseBodyAsString());
            throw new ServiceException("Document parser error: " + extractDetail(e));
        } catch (java.lang.IllegalStateException e) {
            if (e.getMessage() != null && e.getMessage().contains("Timeout")) {
                log.error("Parser timed out after 10 minutes for file: {}", filename);
                throw new ServiceException("Document parsing timed out. The document may be too large or complex.");
            }
            throw new ServiceException("Document parser error: " + e.getMessage());
        } catch (Exception e) {
            log.error("Failed to reach document parser", e);
            throw new ServiceException("Document parser unavailable: " + e.getMessage());
        }
    }

    public byte[] preview(Path filePath, String filename, int page, int dpi) {
        MultipartBodyBuilder builder = new MultipartBodyBuilder();
        builder.part("file", new FileSystemResource(filePath))
                .filename(filename)
                .contentType(MediaType.APPLICATION_PDF);

        try {
            return webClient.post()
                    .uri(uri -> uri.path("/preview")
                            .queryParam("page", page)
                            .queryParam("dpi", dpi)
                            .build())
                    .body(BodyInserters.fromMultipartData(builder.build()))
                    .retrieve()
                    .bodyToMono(byte[].class)
                    .block(Duration.ofSeconds(30));
        } catch (Exception e) {
            log.warn("Preview generation failed for page {}: {}", page, e.getMessage());
            return null;
        }
    }

    /** Extract the "detail" field from a FastAPI error response, or fall back to the raw body. */
    private String extractDetail(WebClientResponseException e) {
        String body = e.getResponseBodyAsString();
        try {
            var tree = new com.fasterxml.jackson.databind.ObjectMapper().readTree(body);
            if (tree.has("detail")) {
                return tree.get("detail").asText();
            }
        } catch (Exception ignored) {
            // Not valid JSON — fall through to raw body
        }
        return body.length() > 200 ? body.substring(0, 200) : body;
    }
}
