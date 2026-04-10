# Rapport d'audit : Securite

**Release** : 0.3.1
**Date** : 2026-04-10
**Auditeur** : claude-code

---

## Score de compliance

| Metrique | Valeur |
|----------|--------|
| Items conformes | 13 / 14 |
| Score | 97 / 100 |
| Ecarts CRITICAL | 0 |
| Ecarts MAJOR | 0 |
| Ecarts MINOR | 1 |
| Ecarts INFO | 1 |

---

## Ecarts constates

### [MIN] `python-multipart>=0.0.12` sans borne superieure

- **Localisation** : `document-parser/requirements.txt`
- **Constat** : `python-multipart>=0.0.12` n'a pas de borne superieure, contrairement aux autres dependances.
- **Regle violee** : 8.5.2 — Les versions des dependances sont epinglees
- **Remediation** : Ajouter `<1.0.0` pour la coherence.

### [INFO] Mismatch nginx `client_max_body_size 5M` vs `MAX_FILE_SIZE_MB=50`

- **Localisation** : `nginx.conf`, `frontend/nginx.conf`, `infra/settings.py`
- **Constat** : Nginx rejette les uploads > 5MB avant que le backend (configure a 50MB par defaut) ne les voie. Pas un probleme de securite (plus restrictif), mais un probleme de coherence fonctionnelle.
- **Remediation** : Aligner nginx `client_max_body_size` avec `MAX_FILE_SIZE_MB` ou rendre configurable.

---

## Points positifs

- Zero secret hardcode dans le code source — tout via env vars
- `.env` dans `.gitignore` (+ `.env.local`, `.env.production`)
- Secrets Docker passes via `environment:`, pas `build: args:`
- Toutes les entrees validees par schemas Pydantic avec validators
- `MAX_FILE_SIZE_MB` enforce en double couche (eager check + streaming check)
- Validation de contenu PDF par magic bytes, pas seulement par extension
- SQL parametrise partout (`?` placeholders), zero f-string SQL
- Zero `eval()`, `exec()`, `os.system()` dans le code
- DOMPurify utilise sur l'unique `v-html` (MarkdownViewer)
- CORS explicitement configure, pas de wildcard `*`
- Rate limiter actif sur tous les endpoints sauf `/api/health`
- Nginx sans `autoindex`, avec headers de securite
- Dependances recentes sans CVE critiques connues

---

## Verdict partiel : GO
