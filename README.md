# Docling Studio

A professional document analysis studio powered by [Docling](https://github.com/DS4SD/docling), inspired by MistralAI Studio.

## Architecture

```
frontend/          → Vue 3 + Vite + Pinia (port 3000)
backend/           → Spring Boot 3.3.5 / Java 21 (port 8081)
document-parser/   → FastAPI + Docling (port 8000)
```

## Quick Start

### Docker Compose (recommended)

```bash
docker-compose up --build
```

Open [http://localhost:3000](http://localhost:3000)

### Local Development

**Document Parser:**
```bash
cd document-parser
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Backend:**
```bash
cd backend
./mvnw spring-boot:run
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Features

- PDF upload and document analysis via Docling
- Extracted content viewing (Markdown, HTML)
- Document structure visualization with bounding boxes
- Image detection
- Analysis history
