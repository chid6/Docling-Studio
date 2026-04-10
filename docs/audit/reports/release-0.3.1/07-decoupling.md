# Rapport d'audit : Decouplage

**Release** : 0.3.1
**Date** : 2026-04-10
**Auditeur** : claude-code
**Derniere mise a jour** : 2026-04-10 (re-audit post PR #144)

---

## Score de compliance

| Metrique | Valeur |
|----------|--------|
| Items conformes | 16 / 16 |
| Score | 100 / 100 |
| Ecarts CRITICAL | 0 |
| Ecarts MAJOR | 0 |
| Ecarts MINOR | 0 |
| Ecarts INFO | 0 |

---

## Ecarts resolus (PR #144 — fix/decoupling-audit)

### [CRIT — RESOLU] Imports croises entre features frontend

- **Localisation** : `features/history/store.ts`, `features/chunking/`, `features/document/store.ts`, `shared/i18n.ts`
- **Resolution** :
  - `shared/appConfig.ts` cree comme pont reactif neutre (`appLocale`, `appMaxFileSizeMb`, `appMaxPageCount`).
  - `shared/i18n.ts` lit `appLocale` depuis `shared/appConfig` — plus d'import depuis `features/`.
  - `features/document/store.ts` lit `appMaxFileSizeMb` depuis `shared/appConfig` — plus d'import de `useFeatureFlagStore`.
  - `features/feature-flags/store.ts` ecrit dans `appConfig` lors du chargement.
  - `features/settings/store.ts` ecrit `appLocale` lors du changement de langue.

### [MAJ — RESOLU] Features `chunking` et `history` sans store/API propres

- **Resolution** :
  - `features/chunking/api.ts` cree avec `rechunkAnalysis()`.
  - `features/chunking/store.ts` cree avec `useChunkingStore` (state: `rechunking`, `error`; action: `rechunk()`).
  - `features/history/api.ts` cree avec `fetchHistory()` et `deleteHistoryEntry()`.
  - `features/history/store.ts` reecrit comme store Pinia distinct (state: `analyses`, `error`; actions: `load()`, `remove()`).

### [MAJ — RESOLU] Collapse d'identite store history/analysis

- **Resolution** : `useHistoryStore` est desormais un store Pinia independant avec son propre state et ses propres appels API. Plus de re-export vers `useAnalysisStore`.

### [MAJ — RESOLU] Health endpoint sans schema Pydantic

- **Resolution** : `HealthResponse` schema Pydantic cree dans `api/schemas.py`. Le endpoint `/api/health` retourne `HealthResponse` avec `response_model=HealthResponse`.

### [MIN — RESOLU] Pas de format de reponse API coherent

- **Resolution** : Le schema `HealthResponse` etablit le pattern type pour les endpoints systeme. Les erreurs fonctionnelles utilisent le format standard FastAPI `HTTPException` de facon coherente.

---

## Points positifs

- Decouplage frontend/backend exemplaire via API REST, nginx proxy, et services Docker separes
- Contrat API stable : types TypeScript alignes sur les schemas Pydantic avec serialisation camelCase
- Backend pleinement testable sans frontend (TestClient)
- Repos retournent des objets domaine, pas de dicts ou Row SQLite
- Les adaptateurs infra ne leakent pas les types Docling vers les services
- Changement de DB ne necessiterait de modifier que `persistence/`
- Ports avec signatures claires utilisant des types du domaine
- Features frontend isolees : chaque feature possede son store, son API client et ses composants UI
- `shared/appConfig.ts` pattern : pont reactif sans couplage de feature a feature

---

## Verdict : GO

Score 100/100 — 0 ecart critique. Toutes les non-conformites precedentes resolues via PR #144.
