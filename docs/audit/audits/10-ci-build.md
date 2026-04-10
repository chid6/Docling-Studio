# Audit 10 — CI / Build

**Objectif** : verifier que la pipeline CI est verte, que le build Docker fonctionne, et que les outils de qualite sont actifs.

**Cible** : `.github/`, `Dockerfile`, `docker-compose.yml`, `nginx.conf`

---

## Checklist

### 10.1 Pipeline CI

| # | Item | Poids |
|---|------|-------|
| 10.1.1 | Toutes les GitHub Actions passent sur la branche de release | 3 |
| 10.1.2 | Les warnings ESLint sont resolus (0 warning) | 1 |
| 10.1.3 | Les warnings Ruff sont resolus (0 warning) | 1 |
| 10.1.4 | Le type-check frontend passe (`vue-tsc --noEmit`) | 2 |
| 10.1.5 | Le formatting est conforme (`ruff format --check`, `prettier --check`) | 1 |

### 10.2 Build Docker

| # | Item | Poids |
|---|------|-------|
| 10.2.1 | `docker compose build` reussit sans erreur | 3 |
| 10.2.2 | Le container demarre et repond sur `/api/health` | 3 |
| 10.2.3 | Les deux variantes (local/remote) buildent correctement | 2 |
| 10.2.4 | Pas de fichier inutile dans l'image (node_modules frontend, .venv, .git) — `.dockerignore` est a jour | 1 |

### 10.3 Configuration

| # | Item | Poids |
|---|------|-------|
| 10.3.1 | Nginx route correctement `/api/*` vers le backend et sert le frontend sur `/` | 2 |
| 10.3.2 | Les variables d'environnement sont documentees et ont des valeurs par defaut coherentes | 1 |

---

## Commandes de verification

```bash
# 10.1.2 + 10.1.3 — Lint
cd document-parser && ruff check . 2>&1 | tail -5
cd frontend && npx eslint src/ 2>&1 | tail -5

# 10.1.4 — Type check
cd frontend && npx vue-tsc --noEmit 2>&1 | tail -5

# 10.1.5 — Formatting
cd document-parser && ruff format --check . 2>&1 | tail -5
cd frontend && npx prettier --check src/ 2>&1 | tail -5

# 10.2.1 — Build Docker
docker compose build 2>&1 | tail -10

# 10.2.4 — .dockerignore
cat .dockerignore 2>/dev/null || echo "ABSENT"
```

---

## Regles de notation

- Tout item de poids 3 non conforme = ecart `[CRIT]`
- Tout item de poids 2 non conforme = ecart `[MAJ]`
- Tout item de poids 1 non conforme = ecart `[MIN]`
