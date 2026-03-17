import { apiFetch } from '../../shared/api/http.js'

export function createAnalysis(documentId) {
  return apiFetch('/api/analyses', {
    method: 'POST',
    body: JSON.stringify({ documentId })
  })
}

export function fetchAnalyses() {
  return apiFetch('/api/analyses')
}

export function fetchAnalysis(id) {
  return apiFetch(`/api/analyses/${id}`)
}

export function deleteAnalysis(id) {
  return apiFetch(`/api/analyses/${id}`, { method: 'DELETE' })
}
