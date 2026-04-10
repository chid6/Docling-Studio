# Audit 05 — DRY (Don't Repeat Yourself)

**Objectif** : verifier l'absence de duplication significative dans le code.

**Cible** : `document-parser/` (hors `.venv/`, `__pycache__/`), `frontend/src/`

---

## Checklist

| # | Item | Poids |
|---|------|-------|
| 5.1 | Aucun bloc de code identique ou quasi-identique n'apparait 3+ fois sans etre factorise | 2 |
| 5.2 | Les interfaces/types partages sont centralises dans `shared/types.ts` (frontend) et `domain/models.py` (backend) | 2 |
| 5.3 | Pas de magic numbers ou magic strings eparpilles — les constantes sont nommees et centralisees | 2 |
| 5.4 | La logique reactive partagee est dans `shared/composables/` (frontend) | 1 |
| 5.5 | Les appels API ne dupliquent pas la config HTTP (base URL, headers) — centralises dans `shared/api/http.ts` | 2 |
| 5.6 | Les schemas Pydantic ne dupliquent pas les modeles du domain — ils transforment, ils ne redefinissent pas | 2 |
| 5.7 | Les regles de validation ne sont definies qu'a un seul endroit (schema Pydantic OU frontend, pas les deux en desaccord) | 1 |

---

## Commandes de verification

```bash
# 5.3 — Magic numbers (backend)
grep -rn "[^a-zA-Z_\"'][0-9]\{3,\}[^a-zA-Z_\"']" document-parser --include="*.py" --exclude-dir=.venv --exclude-dir=tests --exclude-dir=__pycache__

# 5.3 — Magic strings repetees (backend)
grep -rohn '"[a-z_]\{5,\}"' document-parser --include="*.py" --exclude-dir=.venv --exclude-dir=tests | sort | uniq -c | sort -rn | head -20

# 5.5 — Appels fetch en dehors du client HTTP centralise
grep -rn "fetch(" frontend/src/ --include="*.ts" --include="*.vue" | grep -v "http.ts\|api.ts\|node_modules"

# 5.6 — Champs dupliques entre schemas et models
diff <(grep -o "[a-z_]*:" document-parser/api/schemas.py | sort -u) <(grep -o "[a-z_]*:" document-parser/domain/models.py | sort -u)
```

---

## Regles de notation

- Tout item de poids 3 non conforme = ecart `[CRIT]`
- Tout item de poids 2 non conforme = ecart `[MAJ]`
- Tout item de poids 1 non conforme = ecart `[MIN]`
