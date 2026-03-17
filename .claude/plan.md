# Plan : Architecture Simplification — 2 services (Vue + FastAPI/SQLite)

## Objectif
Supprimer le backend Spring Boot (passe-plat) et PostgreSQL. Le document-parser Python absorbe toute la logique backend. On passe de **4 services** à **2 services** : Vue frontend + FastAPI Python.

## Architecture Python — Clean Architecture légère

```
document-parser/
├── main.py                     # FastAPI app, CORS, lifespan, routers mount
├── bbox.py                     # (existant) coord conversion
├── test_bbox.py                # (existant) bbox tests
├── requirements.txt            # + aiosqlite, aiofiles
├── Dockerfile                  # (adapté)
├── .dockerignore               # (existant)
│
├── domain/                     # 🧠 Modèles métier purs (pas de dépendance framework)
│   ├── __init__.py
│   ├── models.py               # Document, AnalysisJob, Status (dataclasses/Pydantic)
│   └── parsing.py              # Logique d'extraction Docling (déplacée depuis main.py)
│
├── api/                        # 🌐 Couche HTTP (FastAPI routers)
│   ├── __init__.py
│   ├── schemas.py              # Pydantic request/response schemas (DTOs)
│   ├── documents.py            # Router /api/documents (CRUD + upload + preview)
│   └── analyses.py             # Router /api/analyses (CRUD + async processing)
│
├── persistence/                # 💾 Couche données (SQLite via aiosqlite)
│   ├── __init__.py
│   ├── database.py             # SQLite connection, init schema, get_db()
│   ├── document_repo.py        # CRUD documents
│   └── analysis_repo.py        # CRUD analysis jobs
│
└── services/                   # ⚙️ Orchestration (use cases)
    ├── __init__.py
    ├── document_service.py     # Upload, delete, preview (file I/O + persistence)
    └── analysis_service.py     # Create job, background parse, update status
```

### Pourquoi cette structure plutôt qu'hexagonale ?
- **domain/** : modèles purs, testables, zéro import framework → l'esprit de l'hexagonale
- **api/** : adaptateur HTTP (port entrant)
- **persistence/** : adaptateur stockage (port sortant)
- **services/** : orchestration des use cases
- Pas de ports/adapters formels (interfaces abstraites) → overkill pour le scope
- Un mec de Docling voit ça, il comprend en 5 secondes. Clean, pas over-engineered.

## Endpoints conservés (contrat API identique)

Le frontend ne change quasiment pas — mêmes URLs, mêmes payloads :

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/documents/upload` | Upload PDF (multipart) |
| GET | `/api/documents` | List documents |
| GET | `/api/documents/{id}` | Get document |
| DELETE | `/api/documents/{id}` | Delete document + file |
| GET | `/api/documents/{id}/preview?page=&dpi=` | Page preview PNG |
| POST | `/api/analyses` | Create analysis (body: {documentId}) |
| GET | `/api/analyses` | List analyses |
| GET | `/api/analyses/{id}` | Get analysis (polling) |
| DELETE | `/api/analyses/{id}` | Delete analysis |
| GET | `/health` | Health check |

## Détails d'implémentation

### 1. SQLite (persistence/database.py)
- `aiosqlite` pour async natif avec FastAPI
- Schema identique au Liquibase actuel (2 tables: documents, analysis_jobs)
- DB file dans volume Docker : `/app/data/docling_studio.db`
- Init schema au startup (CREATE TABLE IF NOT EXISTS)
- Pas besoin d'Alembic pour un projet de cette taille

### 2. File storage
- Même logique : `./uploads/{uuid}_{filename}`
- Volume Docker monté sur `/app/uploads`

### 3. Async analysis (services/analysis_service.py)
- `asyncio.create_task()` pour le background processing (pas besoin de Celery)
- Status polling identique : PENDING → RUNNING → COMPLETED | FAILED
- Le parse Docling tourne dans un thread via `asyncio.to_thread()` (car bloquant + lock)

### 4. CORS
- `fastapi.middleware.cors.CORSMiddleware` dans main.py
- Origins configurables via env var

### 5. domain/parsing.py
- Déplace depuis main.py : `_build_converter()`, `_get_element_type()`, `extract_pages_detail()`, `_process_content_item()`
- Le converter et le lock restent globaux (singleton pattern)

## Changements Frontend

Minimes — seulement la configuration :

1. **vite.config.js** : proxy target change `8081` → `8000`
2. **frontend/Dockerfile** (nginx) : proxy_pass change `backend:8081` → `document-parser:8000`
3. **api.js** : AUCUN changement (mêmes paths `/api/...`)
4. **stores** : AUCUN changement

## docker-compose.yml simplifié

```yaml
services:
  document-parser:
    build: ./document-parser
    ports:
      - "8000:8000"
    volumes:
      - uploads_data:/app/uploads
      - db_data:/app/data
    deploy:
      resources:
        limits:
          memory: 4g

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - document-parser

volumes:
  uploads_data:
  db_data:
```

→ **Plus de postgres, plus de backend Java.** 2 services, clean.

## Étapes d'exécution

1. **Créer la structure Python** (domain/, api/, persistence/, services/)
2. **persistence/database.py** — SQLite async init + schema
3. **persistence/document_repo.py** — CRUD documents
4. **persistence/analysis_repo.py** — CRUD analyses
5. **domain/models.py** — Dataclasses Document, AnalysisJob, Status
6. **domain/parsing.py** — Extraire la logique Docling depuis main.py
7. **api/schemas.py** — Pydantic DTOs (DocumentResponse, AnalysisResponse, etc.)
8. **services/document_service.py** — Upload, delete, preview, list, get
9. **services/analysis_service.py** — Create, run background, status tracking
10. **api/documents.py** — Router documents (5 endpoints)
11. **api/analyses.py** — Router analyses (4 endpoints)
12. **main.py** — Réécrire : CORS, lifespan (DB init), mount routers
13. **requirements.txt** — Ajouter aiosqlite, aiofiles
14. **docker-compose.yml** — Simplifier (2 services)
15. **frontend/vite.config.js** — Changer proxy target
16. **frontend/Dockerfile** — Changer nginx proxy_pass
17. **Supprimer le dossier backend/** entier
18. **Mettre à jour README.md** — Nouvelle architecture

## Ce qu'on ne touche PAS
- bbox.py, test_bbox.py (inchangés)
- Toute la logique Vue (stores, components, pages)
- Logique Docling (parsing, extraction) — juste déplacée
- Dockerfile du parser (juste adapter le CMD si nécessaire)
