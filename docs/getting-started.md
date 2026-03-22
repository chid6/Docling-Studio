# Getting Started

## Docker Compose (recommended)

```bash
git clone https://github.com/scub-france/Docling-Studio.git
cd Docling-Studio
docker compose up --build
```

Open [http://localhost:3000](http://localhost:3000).

## Local Development

### Backend (Python 3.12+)

```bash
cd document-parser
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend (Node 20+)

```bash
cd frontend
npm install
npm run dev
```

The frontend runs on `http://localhost:3000` and proxies API calls to `http://localhost:8000`.

## Running Tests

=== "Backend"

    ```bash
    cd document-parser
    pip install pytest pytest-asyncio httpx
    pytest tests/ -v
    ```

=== "Frontend"

    ```bash
    cd frontend
    npm run test:run
    ```

## Pipeline Options

These options map directly to Docling's [`PdfPipelineOptions`](https://docling-project.github.io/docling/usage/).

| Option | Default | Description |
|--------|---------|-------------|
| `do_ocr` | `true` | OCR for scanned pages and embedded images |
| `do_table_structure` | `true` | Table detection and row/column reconstruction |
| `table_mode` | `accurate` | `accurate` (TableFormer) or `fast` |
| `do_code_enrichment` | `false` | Specialized OCR for code blocks |
| `do_formula_enrichment` | `false` | Math formula recognition (LaTeX output) |
| `do_picture_classification` | `false` | Classify images by type |
| `do_picture_description` | `false` | Generate image descriptions via VLM |
| `generate_picture_images` | `false` | Extract detected images as separate files |
| `generate_page_images` | `false` | Rasterize each page as an image |
| `images_scale` | `1.0` | Scale factor for generated images (0.1–10) |

## Configuration

All configuration is done via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `CORS_ORIGINS` | `http://localhost:3000,...` | CORS allowed origins |
| `UPLOAD_DIR` | `./uploads` | File storage directory |
| `DB_PATH` | `./data/docling_studio.db` | SQLite database path |
| `CONVERSION_TIMEOUT` | `600` | Max seconds per Docling conversion |

## System Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| Memory   | 6 GB    | 8 GB+       |
| CPUs     | 4       | 8+          |

All Docker images are multi-arch (`linux/amd64` + `linux/arm64`). No GPU required.
