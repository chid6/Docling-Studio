# Docling Studio

A visual document analysis studio powered by [Docling](https://github.com/DS4SD/docling).
Upload a PDF, configure the extraction pipeline, and visualize the results — text, tables, images, formulas, bounding boxes — all from your browser.

![Docling Studio — Visual Mode](docs/screenshots/visual-mode.png)

## Features

- **PDF viewer** with page navigation and visual overlay toggle
- **Configurable Docling pipeline** — OCR on/off, table extraction mode (fast/accurate)
- **Bounding box visualization** — overlay extracted elements directly on the PDF with color-coded types
- **Per-page results** — right panel syncs with the current PDF page
- **Document hierarchy** — heading levels and structure preserved from Docling's `iterate_items()` API
- **Markdown & HTML export** of extracted content
- **Analysis history** — re-visit past analyses

<details>
<summary>More screenshots</summary>

| Import | Configure | Results |
|--------|-----------|---------|
| ![Import](docs/screenshots/import.png) | ![Configure](docs/screenshots/configure.png) | ![Results](docs/screenshots/results.png) |

</details>

## Architecture

```
┌────────────┐     ┌──────────────┐     ┌──────────────────┐
│  Frontend   │────▶│   Backend    │────▶│ Document Parser   │
│  Vue 3      │     │ Spring Boot  │     │ FastAPI + Docling  │
│  port 3000  │     │  port 8081   │     │   port 8000        │
└────────────┘     └──────┬───────┘     └──────────────────┘
                          │
                   ┌──────▼───────┐
                   │  PostgreSQL  │
                   │  port 5432   │
                   └──────────────┘
```

| Service | Stack | Role |
|---------|-------|------|
| **frontend** | Vue 3, Vite, Pinia | UI, PDF viewer, results display |
| **backend** | Spring Boot 3.3, Java 21, Liquibase | REST API, storage, orchestration |
| **document-parser** | FastAPI, Docling, pdf2image | PDF parsing with configurable pipeline |
| **postgres** | PostgreSQL 16 | Documents & analysis persistence |

## Quick Start

### Docker Compose (recommended)

```bash
# Clone the repo
git clone https://github.com/pjmalandrino/docling-studio.git
cd docling-studio

# (Optional) customize credentials
cp .env.example .env

# Start all services
docker compose up --build
```

Open [http://localhost:3000](http://localhost:3000)

> **Note:** First analysis may take a few minutes as Docling downloads its ML models (~40 MB) on first run.

### Local Development

Start only PostgreSQL via Docker:

```bash
docker compose -f docker-compose.dev.yml up -d
```

Then run each service locally:

**Document Parser** (Python 3.12+):
```bash
cd document-parser
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Backend** (Java 21+):
```bash
cd backend
./mvnw spring-boot:run
```

**Frontend** (Node 20+):
```bash
cd frontend
npm install
npm run dev
```

## Docling Integration

The document parser wraps [Docling](https://github.com/DS4SD/docling) with configurable pipeline options exposed as query parameters on the `/parse` endpoint:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `do_ocr` | `true` | Enable OCR for scanned documents |
| `do_table_structure` | `true` | Enable table structure extraction |
| `table_mode` | `accurate` | Table extraction mode: `accurate` or `fast` |

Element types are detected using `isinstance()` checks against Docling's type hierarchy (`TextItem`, `TableItem`, `PictureItem`, `SectionHeaderItem`, etc.) and the document tree depth from `iterate_items()` is preserved for heading-level reconstruction.

## Configuration

All configuration is done via environment variables. See [`.env.example`](.env.example) for available options.

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_USER` | `app` | Database user |
| `POSTGRES_PASSWORD` | `app` | Database password |
| `POSTGRES_DB` | `docling_studio` | Database name |
| `APP_CORS_ALLOWED_ORIGINS` | `http://localhost:3000,...` | CORS allowed origins (comma-separated) |
| `APP_DOCUMENT-PARSER_BASE-URL` | `http://localhost:8000` | Document parser URL |
| `APP_STORAGE_PATH` | `./uploads` | File storage directory |

## Performance & System Requirements

Docling runs ML models (layout analysis, OCR, table structure) on **CPU by default**. Processing time depends on document size and complexity.

| Document type | Pages | Approx. time (CPU) |
|---------------|-------|---------------------|
| Simple report | 5-10  | 1-3 min |
| Research paper | 15-30 | 5-10 min |
| Dense PDF with tables | 30+  | 10-20 min |

### Docker Desktop settings

The document parser needs **at least 4 GB of RAM**. Recommended Docker Desktop allocation:

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| Memory   | 6 GB    | 8 GB+       |
| CPUs     | 4       | 8+          |

> On **macOS**: Docker Desktop > Settings > Resources
> On **Windows**: Docker Desktop > Settings > Resources > WSL 2

### Platform support

All Docker images are **multi-arch** (linux/amd64 + linux/arm64). Works natively on:

| Platform | Architecture | GPU acceleration |
|----------|-------------|-----------------|
| **macOS Apple Silicon** (M1/M2/M3) | arm64 | Not in Docker (MPS unavailable). Run parser locally for GPU. |
| **macOS Intel** | amd64 | N/A |
| **Linux x86_64** | amd64 | NVIDIA GPU via `docker compose --profile gpu` (coming soon) |
| **Linux ARM** (Raspberry Pi 5, Ampere) | arm64 | CPU only |
| **Windows + WSL2** | amd64 | NVIDIA GPU passthrough supported |

> **Tip for Mac users:** For faster processing, run the document parser **locally** (outside Docker) to leverage Apple Silicon's MPS acceleration when supported by PyTorch/Docling.

## Tech Stack

- **Frontend**: Vue 3 + Vite + Pinia
- **Backend**: Spring Boot 3.3 + Java 21 + Liquibase + PDFBox
- **Parser**: FastAPI + Docling 2.x + PyTorch + pdf2image
- **Database**: PostgreSQL 16
- **Infra**: Docker Compose + Nginx

## Contributing

Contributions are welcome! Please open an issue first to discuss what you'd like to change.

## License

[MIT](LICENSE) — Pier-Jean Malandrino
