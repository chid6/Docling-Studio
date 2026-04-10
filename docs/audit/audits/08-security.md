# Audit 08 — Securite

**Objectif** : verifier l'absence de vulnerabilites courantes (OWASP Top 10) et le respect des bonnes pratiques de securite.

**Cible** : tout le projet

---

## Checklist

### 8.1 Secrets et credentials

| # | Item | Poids |
|---|------|-------|
| 8.1.1 | Aucune cle API, token, ou mot de passe en dur dans le code source | 3 |
| 8.1.2 | Les fichiers `.env` sont dans `.gitignore` | 3 |
| 8.1.3 | Les secrets Docker sont passes par variables d'environnement, pas en build args | 2 |

### 8.2 Validation des entrees

| # | Item | Poids |
|---|------|-------|
| 8.2.1 | Toutes les entrees utilisateur sont validees par des schemas Pydantic | 3 |
| 8.2.2 | `MAX_FILE_SIZE_MB` est configuree et appliquee a l'upload | 3 |
| 8.2.3 | Les types de fichiers acceptes sont valides (pas d'upload de `.exe`, `.sh`, etc.) | 2 |

### 8.3 Injection

| # | Item | Poids |
|---|------|-------|
| 8.3.1 | Les requetes SQL utilisent des parametres lies (`?`), jamais de string formatting/f-strings | 3 |
| 8.3.2 | Pas de `eval()`, `exec()`, ou `os.system()` avec des entrees utilisateur | 3 |
| 8.3.3 | Le frontend utilise DOMPurify pour tout rendu de contenu HTML/Markdown | 3 |

### 8.4 CORS et reseau

| # | Item | Poids |
|---|------|-------|
| 8.4.1 | Les origines CORS autorisees sont configurees explicitement, pas de `*` en production | 3 |
| 8.4.2 | Le rate limiter est actif sur tous les endpoints sauf `/api/health` | 2 |
| 8.4.3 | Nginx ne sert que les fichiers statiques prevus — pas de directory listing | 2 |

### 8.5 Dependances

| # | Item | Poids |
|---|------|-------|
| 8.5.1 | Pas de dependance avec des CVE critiques connues | 3 |
| 8.5.2 | Les versions des dependances sont epinglees (pas de `>=` sans borne superieure) | 1 |

---

## Commandes de verification

```bash
# 8.1.1 — Secrets potentiels dans le code
grep -rni "password\s*=\|secret\s*=\|api_key\s*=\|token\s*=" document-parser --include="*.py" --exclude-dir=.venv --exclude-dir=tests
grep -rni "password\|secret\|api.key\|token" frontend/src/ --include="*.ts" --include="*.vue"

# 8.1.2 — .env dans gitignore
grep "\.env" .gitignore

# 8.3.1 — SQL injection (f-strings dans les requetes)
grep -rn 'f".*SELECT\|f".*INSERT\|f".*UPDATE\|f".*DELETE\|f".*DROP' document-parser --include="*.py" --exclude-dir=.venv

# 8.3.2 — eval/exec/os.system
grep -rn "eval(\|exec(\|os\.system(\|subprocess\.call(" document-parser --include="*.py" --exclude-dir=.venv

# 8.3.3 — DOMPurify usage
grep -rn "DOMPurify\|v-html\|innerHTML" frontend/src/ --include="*.vue" --include="*.ts"

# 8.4.1 — CORS wildcard
grep -rn 'allow_origins.*\*\|"*"' document-parser --include="*.py" --exclude-dir=.venv

# 8.5.1 — Audit npm
cd frontend && npm audit --production 2>&1 | tail -10

# 8.5.1 — Audit pip (si pip-audit installe)
cd document-parser && pip-audit 2>&1 | tail -10
```

---

## Regles de notation

- Tout item de poids 3 non conforme = ecart `[CRIT]`
- Tout item de poids 2 non conforme = ecart `[MAJ]`
- Tout item de poids 1 non conforme = ecart `[MIN]`
