# Audit 04 — KISS (Keep It Simple, Stupid)

**Objectif** : verifier que le code reste simple et ne contient pas de sur-ingenierie.

**Cible** : `document-parser/` (hors `.venv/`, `__pycache__/`), `frontend/src/`

---

## Checklist

| # | Item | Poids |
|---|------|-------|
| 4.1 | Pas de design pattern complexe la ou un simple `if` ou une fonction suffit (factory, strategy, observer superflus) | 2 |
| 4.2 | Le code resout le probleme actuel, pas un probleme hypothetique futur (pas de genericite prematuree) | 2 |
| 4.3 | Pas de fonction wrapper qui ne fait qu'appeler une autre fonction sans valeur ajoutee | 1 |
| 4.4 | Utilisation des outils standard (Python stdlib, Vue composables natifs) avant de creer des solutions maison | 1 |
| 4.5 | Configuration simple — pas de systeme de config complexe la ou une variable d'env suffit | 1 |
| 4.6 | Pas d'indirection inutile — le chemin d'execution d'une requete ne traverse pas plus de couches que necessaire | 2 |
| 4.7 | Pas de meta-programmation ou de magie (decorateurs complexes, metaclasses) sauf necessite avere | 2 |
| 4.8 | Les structures de donnees utilisees sont les plus simples possibles (liste plutot que arbre si la liste suffit) | 1 |

---

## Commandes de verification

```bash
# 4.1 — Patterns potentiellement superflus
grep -rn "class.*Factory\|class.*Strategy\|class.*Observer\|class.*Builder\|class.*Singleton" document-parser --include="*.py" --exclude-dir=.venv

# 4.7 — Meta-programmation
grep -rn "__metaclass__\|type(.*,.*,.*)\|__init_subclass__\|__class_getitem__" document-parser --include="*.py" --exclude-dir=.venv

# 4.3 — Fonctions tres courtes (potentiels wrappers inutiles, < 3 lignes)
# Verification manuelle recommandee sur les fonctions identifiees
```

---

## Regles de notation

- Tout item de poids 3 non conforme = ecart `[CRIT]`
- Tout item de poids 2 non conforme = ecart `[MAJ]`
- Tout item de poids 1 non conforme = ecart `[MIN]`
