import { apiFetch } from '../../shared/api/http.js'

export function fetchAnalyses() {
  return apiFetch('/api/analyses')
}

export function deleteAnalysis(id) {
  return apiFetch(`/api/analyses/${id}`, { method: 'DELETE' })
}
