# Audit 12 — Performance & Ressources

**Objectif** : verifier l'absence de problemes de performance evidents et la bonne gestion des ressources.

**Cible** : `document-parser/` (hors `.venv/`), `frontend/src/`

---

## Checklist

### 12.1 Backend

| # | Item | Poids |
|---|------|-------|
| 12.1.1 | Pas de requete N+1 — les acces DB sont optimises (pas de boucle avec requete unitaire) | 2 |
| 12.1.2 | Les fichiers uploades temporaires sont supprimes apres traitement | 2 |
| 12.1.3 | `MAX_CONCURRENT_ANALYSES` est configuree et respectee (semaphore) | 2 |
| 12.1.4 | Les operations longues (conversion Docling) sont asynchrones et ne bloquent pas l'event loop | 3 |
| 12.1.5 | Pas de chargement de fichier entier en memoire sans necesssite (streaming si possible) | 2 |

### 12.2 Frontend

| # | Item | Poids |
|---|------|-------|
| 12.2.1 | Les watchers Vue ont leur cleanup (pas de memory leak) | 2 |
| 12.2.2 | Les event listeners sont supprimes dans `onUnmounted` | 2 |
| 12.2.3 | Les requetes API ont un mecanisme d'annulation ou de debounce quand pertinent | 1 |
| 12.2.4 | Pas de re-render excessif — les computed sont utilises plutot que des fonctions dans le template | 1 |
| 12.2.5 | Les assets lourds (images, fonts) sont optimises | 1 |

### 12.3 Infrastructure

| # | Item | Poids |
|---|------|-------|
| 12.3.1 | Nginx a une configuration de cache pour les fichiers statiques | 1 |
| 12.3.2 | Les reponses API sont de taille raisonnable (pas d'envoi de donnees inutiles) | 1 |
| 12.3.3 | Le health check est leger et ne charge pas le systeme | 1 |

---

## Commandes de verification

```bash
# 12.1.1 — Pattern N+1 (boucle avec requete DB)
grep -rn -A5 "for.*in.*:" document-parser/persistence/ --include="*.py" | grep -i "select\|fetch\|execute"

# 12.1.4 — Appels bloquants dans du code async
grep -rn "time\.sleep\|open(" document-parser/services/ --include="*.py"

# 12.2.1 + 12.2.2 — Watchers et listeners sans cleanup
grep -rn "addEventListener\|watch(\|watchEffect(" frontend/src/ --include="*.vue" --include="*.ts" | grep -v "node_modules"
grep -rn "onUnmounted\|onBeforeUnmount\|removeEventListener" frontend/src/ --include="*.vue" | grep -v "node_modules"
```

---

## Regles de notation

- Tout item de poids 3 non conforme = ecart `[CRIT]`
- Tout item de poids 2 non conforme = ecart `[MAJ]`
- Tout item de poids 1 non conforme = ecart `[MIN]`
