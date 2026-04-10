# Audit 06 — SOLID

**Objectif** : verifier le respect des 5 principes SOLID.

**Cible** : `document-parser/` (hors `.venv/`, `__pycache__/`), `frontend/src/`

---

## Checklist

### 6.1 S — Single Responsibility Principle

| # | Item | Poids |
|---|------|-------|
| 6.1.1 | Chaque service a une responsabilite unique (`document_service` = documents, `analysis_service` = analyses) | 2 |
| 6.1.2 | Chaque store Pinia gere un seul feature | 2 |
| 6.1.3 | Les routes API sont groupees par ressource (`documents.py`, `analyses.py`) | 1 |
| 6.1.4 | Aucune classe ou module ne cumule des responsabilites heterogenes (ex: un service qui fait du parsing ET de la persistence) | 2 |

### 6.2 O — Open/Closed Principle

| # | Item | Poids |
|---|------|-------|
| 6.2.1 | Les ports (`domain/ports.py`) permettent d'ajouter de nouveaux adaptateurs sans modifier le code existant | 2 |
| 6.2.2 | Le systeme local/remote est extensible via `_build_converter()` sans modifier les services | 2 |
| 6.2.3 | L'ajout d'un nouveau format d'export ne necessite pas de modifier les endpoints existants | 1 |

### 6.3 L — Liskov Substitution Principle

| # | Item | Poids |
|---|------|-------|
| 6.3.1 | `LocalConverter` et `ServeConverter` sont interchangeables (meme protocole, meme contrat de retour) | 3 |
| 6.3.2 | Les implementations de ports ne lancent pas d'exceptions non prevues par le contrat | 2 |
| 6.3.3 | Pas de `isinstance()` ou `type()` check pour differencier les implementations | 2 |

### 6.4 I — Interface Segregation Principle

| # | Item | Poids |
|---|------|-------|
| 6.4.1 | `DocumentConverter` et `DocumentChunker` sont des ports separes (pas une "god interface") | 2 |
| 6.4.2 | Aucun port ne force une implementation a definir des methodes qu'elle n'utilise pas | 2 |

### 6.5 D — Dependency Inversion Principle

| # | Item | Poids |
|---|------|-------|
| 6.5.1 | Les services dependent de protocoles abstraits (ports), pas d'implementations concretes | 3 |
| 6.5.2 | L'injection se fait dans `main.py` (composition root) | 2 |
| 6.5.3 | Pas d'instanciation directe d'adaptateurs dans les services (`LocalConverter()` dans un service = violation) | 3 |

---

## Commandes de verification

```bash
# 6.3.3 — isinstance checks sur les adaptateurs
grep -rn "isinstance\|type(" document-parser/services/ --include="*.py"

# 6.5.3 — Instanciation directe d'adaptateurs dans services
grep -rn "LocalConverter\|ServeConverter\|LocalChunker" document-parser/services/ --include="*.py"

# 6.5.1 — Imports directs d'infra dans services
grep -rn "from infra\.\|import infra\." document-parser/services/ --include="*.py"
```

---

## Regles de notation

- Tout item de poids 3 non conforme = ecart `[CRIT]`
- Tout item de poids 2 non conforme = ecart `[MAJ]`
- Tout item de poids 1 non conforme = ecart `[MIN]`
