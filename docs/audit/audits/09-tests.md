# Audit 09 — Tests

**Objectif** : verifier la couverture, la qualite et la fiabilite de la suite de tests.

**Cible** : `document-parser/tests/`, `frontend/src/**/*.test.*`, `e2e/`

---

## Checklist

### 9.1 Execution

| # | Item | Poids |
|---|------|-------|
| 9.1.1 | Tous les tests backend passent (`pytest tests/ -v`) | 3 |
| 9.1.2 | Tous les tests frontend passent (`npm run test:run`) | 3 |
| 9.1.3 | Les tests e2e Karate UI passent | 2 |

### 9.2 Couverture

| # | Item | Poids |
|---|------|-------|
| 9.2.1 | Chaque endpoint API a au moins un test (happy path) | 2 |
| 9.2.2 | Les cas d'erreur des endpoints sont testes (400, 404, 413, 429) | 2 |
| 9.2.3 | Les services ont des tests unitaires couvrant la logique d'orchestration | 2 |
| 9.2.4 | Les fonctions du domain (bbox, value objects) sont testees | 1 |
| 9.2.5 | Les composants Vue critiques ont des tests (stores, composables) | 2 |

### 9.3 Qualite des tests

| # | Item | Poids |
|---|------|-------|
| 9.3.1 | Pas de `.only` ou `fdescribe` ou `fit` laisse par accident | 3 |
| 9.3.2 | Pas de `@pytest.mark.skip` ou `.skip()` sans justification en commentaire | 1 |
| 9.3.3 | Les tests sont deterministes — pas de dependance a l'heure, au reseau, ou a l'ordre d'execution | 2 |
| 9.3.4 | Les tests d'integration testent le flux reel, pas un mock complet | 2 |
| 9.3.5 | Les assertions sont specifiques (pas juste `assert result is not None`) | 1 |
| 9.3.6 | Chaque test a un nom explicite qui decrit le comportement teste | 1 |

---

## Commandes de verification

```bash
# 9.1.1 — Tests backend
cd document-parser && python -m pytest tests/ -v --tb=short 2>&1 | tail -30

# 9.1.2 — Tests frontend
cd frontend && npm run test:run 2>&1 | tail -30

# 9.3.1 — .only / fdescribe / fit
grep -rn "\.only\|fdescribe\|fit(" frontend/src/ --include="*.test.*"

# 9.3.2 — Skip sans commentaire
grep -rn -B1 "@pytest.mark.skip\|\.skip(" document-parser/tests/ frontend/src/

# 9.3.5 — Assertions vagues
grep -rn "assert.*is not None$\|assert.*!= None$\|expect.*toBeTruthy()$" document-parser/tests/ frontend/src/ --include="*.test.*" --include="*.py"
```

---

## Regles de notation

- Tout item de poids 3 non conforme = ecart `[CRIT]`
- Tout item de poids 2 non conforme = ecart `[MAJ]`
- Tout item de poids 1 non conforme = ecart `[MIN]`
