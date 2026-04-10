# Rapport d'audit : CI / Build

**Release** : 0.3.1
**Date** : 2026-04-10
**Auditeur** : claude-code

---

## Score de compliance

| Metrique | Valeur |
|----------|--------|
| Items conformes | 9 / 11 |
| Score | 90 / 100 |
| Ecarts CRITICAL | 0 |
| Ecarts MAJOR | 0 |
| Ecarts MINOR | 2 |
| Ecarts INFO | 0 |

---

## Ecarts constates

### [MIN] ESLint n'enforce pas zero warnings

- **Localisation** : `.github/workflows/ci.yml:69`, `.github/workflows/release-gate.yml:53`
- **Constat** : `npx eslint src/` est invoque sans `--max-warnings 0`. Les warnings passent silencieusement.
- **Regle violee** : 10.1.2 — Les warnings ESLint sont resolus (0 warning)
- **Remediation** : Ajouter `--max-warnings 0` a la commande ESLint dans les deux workflows.

### [MIN] Checks de formatting absents du CI

- **Localisation** : `.github/workflows/` (tous les workflows)
- **Constat** : Ni `ruff format --check` ni `prettier --check` ne sont executes dans les workflows CI.
- **Regle violee** : 10.1.5 — Le formatting est conforme
- **Remediation** : Ajouter les steps `ruff format --check .` et `npx prettier --check src/` aux jobs lint.

---

## Points positifs

- Pipeline CI comprehensive : `ci.yml` (push/PR), `release-gate.yml` (4 phases), `release.yml` (multi-arch), `docling-compat.yml` (cron daily)
- Ruff check enforce (zero tolerance par defaut)
- Type-check frontend via `vue-tsc --noEmit` dans CI
- Docker build des deux variantes (local/remote) via matrix strategy
- Smoke test automatise : demarrage container + validation `/api/health` (status, engine)
- Trivy security scan + check taille image
- `.dockerignore` complet (git, tests, docs, dev artifacts exclus)
- Nginx route correctement `/api/*` -> backend, `/` -> frontend
- Variables d'environnement documentees dans `.env.example` avec defaults coherents
- Multi-stage Dockerfile optimise (node build, python runtime, non-root user)

---

## Verdict partiel : GO
