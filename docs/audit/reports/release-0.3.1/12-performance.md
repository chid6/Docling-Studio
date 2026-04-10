# Rapport d'audit : Performance & Ressources

**Release** : 0.3.1
**Date** : 2026-04-10
**Auditeur** : claude-code

---

## Score de compliance

| Metrique | Valeur |
|----------|--------|
| Items conformes | 10 / 13 |
| Score | 86 / 100 |
| Ecarts CRITICAL | 0 |
| Ecarts MAJOR | 0 |
| Ecarts MINOR | 3 |
| Ecarts INFO | 0 |

---

## Ecarts constates

### [MIN] Pas de mecanisme d'annulation/debounce sur les requetes API frontend

- **Localisation** : `frontend/src/shared/api/http.ts`, `frontend/src/features/analysis/store.ts`
- **Constat** : `apiFetch` utilise `fetch()` brut sans support `AbortController`. Les requetes de polling peuvent se chevaucher.
- **Regle violee** : 12.2.3 — Les requetes API ont un mecanisme d'annulation ou de debounce
- **Remediation** : Ajouter le support `AbortController` dans `apiFetch`.

### [MIN] Logo de 879 KB non optimise

- **Localisation** : `frontend/src/assets/logo.png`
- **Constat** : Le logo fait 879 KB, excessif pour une image de logo (devrait etre < 50 KB).
- **Regle violee** : 12.2.5 — Les assets lourds sont optimises
- **Remediation** : Convertir en SVG ou WebP, ou compresser significativement.

### [MIN] Nginx sans configuration de cache pour les fichiers statiques

- **Localisation** : `nginx.conf`, `frontend/nginx.conf`
- **Constat** : Aucune directive `expires`, `Cache-Control` ou `add_header Cache-Control` pour les assets statiques. Vite produit des noms hashes qui sont safe a cacher agressivement.
- **Regle violee** : 12.3.1 — Nginx a une configuration de cache pour les fichiers statiques
- **Remediation** : Ajouter `location ~* \.(js|css|png|svg|ico|woff2?)$ { expires 1y; add_header Cache-Control "public, immutable"; }`

---

## Points positifs

- Zero requete N+1 : queries optimisees avec JOIN, LIMIT/OFFSET
- Fichiers uploades correctement geres (persistants, nettoyes a la suppression avec protection path-traversal)
- `MAX_CONCURRENT_ANALYSES` configure et respecte via semaphore asyncio
- Conversion Docling correctement deplacee hors event loop via `asyncio.to_thread()`
- Upload en streaming (chunks de 64 KB)
- Watchers Vue automatiquement nettoyes par le lifecycle des composants
- Event listeners supprimes dans `onBeforeUnmount` (mousemove, mouseup, ResizeObserver)
- Polling avec `stopPolling()` qui clear interval et timeout
- `computed` utilises correctement plutot que des fonctions dans les templates
- Reponses API de taille raisonnable (`has_document_json: bool` au lieu du blob complet)
- Health check leger (`SELECT 1`)

---

## Verdict partiel : GO
