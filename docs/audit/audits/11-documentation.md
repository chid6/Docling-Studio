# Audit 11 — Documentation & Changelog

**Objectif** : verifier que la release est correctement documentee et versionnee.

**Cible** : `CHANGELOG.md`, `frontend/package.json`, `docs/`, code source

---

## Checklist

### 11.1 Changelog

| # | Item | Poids |
|---|------|-------|
| 11.1.1 | La section `[Unreleased]` a ete renommee en `[X.Y.Z] - YYYY-MM-DD` | 3 |
| 11.1.2 | Toutes les modifications significatives de la release sont listees dans le changelog | 2 |
| 11.1.3 | Les breaking changes sont clairement identifies | 3 |
| 11.1.4 | Le format respecte [Keep a Changelog](https://keepachangelog.com/) | 1 |

### 11.2 Versioning

| # | Item | Poids |
|---|------|-------|
| 11.2.1 | `frontend/package.json` contient la bonne version X.Y.Z | 2 |
| 11.2.2 | La version suit le Semantic Versioning | 2 |

### 11.3 Code propre

| # | Item | Poids |
|---|------|-------|
| 11.3.1 | Les `TODO` et `FIXME` restants sont volontaires et documentes (pas de TODO orphelin) | 1 |
| 11.3.2 | Pas de `console.log` de debug laisse dans le code frontend | 2 |
| 11.3.3 | Pas de `print()` de debug laisse dans le code backend (hors logging structure) | 2 |

---

## Commandes de verification

```bash
# 11.1.1 — Section Unreleased encore presente
grep -n "Unreleased" CHANGELOG.md

# 11.2.1 — Version dans package.json
grep '"version"' frontend/package.json

# 11.3.1 — TODOs restants
grep -rn "TODO\|FIXME\|HACK\|XXX" document-parser --include="*.py" --exclude-dir=.venv --exclude-dir=__pycache__
grep -rn "TODO\|FIXME\|HACK\|XXX" frontend/src --include="*.ts" --include="*.vue"

# 11.3.2 — console.log de debug
grep -rn "console\.log\|console\.debug\|console\.warn" frontend/src/ --include="*.ts" --include="*.vue" | grep -v "node_modules"

# 11.3.3 — print() de debug
grep -rn "^\s*print(" document-parser --include="*.py" --exclude-dir=.venv --exclude-dir=tests --exclude-dir=__pycache__
```

---

## Regles de notation

- Tout item de poids 3 non conforme = ecart `[CRIT]`
- Tout item de poids 2 non conforme = ecart `[MAJ]`
- Tout item de poids 1 non conforme = ecart `[MIN]`
