package com.docling.studio.document;

import com.docling.studio.config.DocumentParserProperties;
import org.springframework.core.io.FileSystemResource;
import org.springframework.http.MediaType;
import org.springframework.http.client.MultipartBodyBuilder;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.BodyInserters;
import org.springframework.web.reactive.function.client.WebClient;

import java.nio.file.Path;
import java.util.Map;

@Component
public class DocumentParserClient {

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

        return webClient.post()
                .uri("/parse")
                .body(BodyInserters.fromMultipartData(builder.build()))
                .retrieve()
                .bodyToMono(Map.class)
                .block();
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
                    .block();
        } catch (Exception e) {
            return null;
        }
    }
}
