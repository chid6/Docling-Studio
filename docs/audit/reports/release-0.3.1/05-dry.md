# Rapport d'audit : DRY (Don't Repeat Yourself)

**Release** : 0.3.1
**Date** : 2026-04-10
**Auditeur** : claude-code

---

## Score de compliance

| Metrique | Valeur |
|----------|--------|
| Items conformes | 6 / 7 |
| Score | 83 / 100 |
| Ecarts CRITICAL | 0 |
| Ecarts MAJOR | 1 |
| Ecarts MINOR | 0 |
| Ecarts INFO | 0 |

---

## Ecarts constates

### [MAJ] Magic numbers 612.0 / 792.0 dupliques dans `serve_converter.py`

- **Localisation** : `infra/serve_converter.py:195,196,223,224`
- **Constat** : Les dimensions US Letter (612.0, 792.0) sont utilisees comme litteraux bruts 4 fois, alors que `local_converter.py` definit correctement les constantes nommees `_DEFAULT_PAGE_WIDTH` et `_DEFAULT_PAGE_HEIGHT`.
- **Regle violee** : 5.3 — Pas de magic numbers eparpilles
- **Remediation** : Extraire ces constantes dans un module partage ou les importer depuis `local_converter.py`.

---

## Points positifs

- Aucun bloc de code identique n'apparait 3+ fois sans factorisation
- Types partages centralises dans `shared/types.ts` (frontend) et `domain/models.py` + `domain/value_objects.py` (backend)
- Logique reactive partagee dans `shared/composables/usePagination.ts`
- Appels API centralises via `apiFetch` dans `shared/api/http.ts` — zero fuite de `fetch()` brut
- Schemas Pydantic transforment les modeles domaine, ne les redefinissent pas
- Regles de validation definies en un seul endroit (backend = source de verite, frontend = UX optimization)

---

## Verdict partiel : GO
