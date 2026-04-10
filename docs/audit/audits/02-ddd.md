# Audit 02 — Domain-Driven Design (DDD)

**Objectif** : verifier que le code respecte les principes DDD — bounded contexts clairs, entites et value objects bien definis, ubiquitous language coherent, et separation des responsabilites metier.

**Cible** : `document-parser/domain/`, `document-parser/services/`, `frontend/src/features/`, `frontend/src/shared/types.ts`

---

## Checklist

### 2.1 Bounded Contexts

| # | Item | Poids |
|---|------|-------|
| 2.1.1 | Les contextes metier sont clairement identifies et isoles (document, analysis, chunking) | 3 |
| 2.1.2 | Chaque contexte a ses propres modeles — pas de modele "god object" partage entre contextes | 3 |
| 2.1.3 | Les frontieres entre contextes sont explicites — la communication passe par des contrats definis (DTOs, events), pas par des imports directs de modeles internes d'un autre contexte | 2 |
| 2.1.4 | Le frontend respecte les memes bounded contexts (features = contextes) | 2 |

### 2.2 Entites et Value Objects

| # | Item | Poids |
|---|------|-------|
| 2.2.1 | Les entites ont une identite unique (`id`) et un cycle de vie (Document, AnalysisJob) | 2 |
| 2.2.2 | Les value objects sont immutables et definis par leurs attributs, pas par une identite (ConversionResult, ChunkingOptions, BoundingBox) | 2 |
| 2.2.3 | Les value objects ne contiennent pas de logique de persistence (pas de `save()`, `update()`) | 3 |
| 2.2.4 | Les entites ne sont pas de simples "sacs de donnees" — elles portent du comportement metier quand c'est pertinent | 1 |

### 2.3 Ubiquitous Language

| # | Item | Poids |
|---|------|-------|
| 2.3.1 | Le vocabulaire metier est coherent entre domain, services, API et frontend (ex: "analysis" partout, pas "job" d'un cote et "analysis" de l'autre) | 2 |
| 2.3.2 | Les noms de classes/fonctions/variables refletent le langage du domaine, pas des termes techniques generiques (pas de `DataProcessor`, `Handler`, `Manager` sans contexte) | 1 |
| 2.3.3 | Les statuts metier utilisent un vocabulaire explicite (PENDING, RUNNING, COMPLETED, FAILED) | 1 |

### 2.4 Agregats et invariants

| # | Item | Poids |
|---|------|-------|
| 2.4.1 | Chaque agregat a une racine claire (Document est la racine de son agregat, AnalysisJob de son agregat) | 2 |
| 2.4.2 | Les invariants metier sont proteges dans le domaine — pas de creation d'etats invalides depuis l'exterieur | 3 |
| 2.4.3 | Les modifications d'un agregat passent par sa racine, pas par manipulation directe de ses composants internes | 2 |

### 2.5 Repositories et anti-corruption

| # | Item | Poids |
|---|------|-------|
| 2.5.1 | Les repositories (`persistence/`) manipulent des entites du domaine, pas des dictionnaires bruts ou des Row objects | 2 |
| 2.5.2 | La couche anti-corruption (schemas Pydantic) transforme les donnees externes (HTTP) en objets du domaine | 2 |
| 2.5.3 | Les adaptateurs infra (`infra/`) ne leakent pas leurs types internes vers les services (pas de types Docling exposes aux services) | 3 |

---

## Commandes de verification

```bash
# 2.1.2 — Chercher un modele omniscient
wc -l document-parser/domain/models.py

# 2.2.2 — Value objects mutables (setters, attributs reassignes)
grep -rn "\..*=" document-parser/domain/value_objects.py | grep -v "self\." | grep -v "__"

# 2.3.1 — Incoherences de vocabulaire (job vs analysis)
grep -rni "\bjob\b" document-parser/api/ document-parser/services/ --include="*.py" | grep -v "AnalysisJob"
grep -rni "\bjob\b" frontend/src/ --include="*.ts" --include="*.vue" | grep -v "node_modules"

# 2.5.3 — Types Docling qui leakent vers services
grep -rn "from docling\|import docling" document-parser/services/ --include="*.py"
```

---

## Regles de notation

- Tout item de poids 3 non conforme = ecart `[CRIT]`
- Tout item de poids 2 non conforme = ecart `[MAJ]`
- Tout item de poids 1 non conforme = ecart `[MIN]`
