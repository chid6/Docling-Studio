import { apiFetch } from '../../shared/api/http.js'

export function fetchDocuments() {
  return apiFetch('/api/documents')
}

export function fetchDocument(id) {
  return apiFetch(`/api/documents/${id}`)
}

export async function uploadDocument(file) {
  const formData = new FormData()
  formData.append('file', file)
  return apiFetch('/api/documents/upload', {
    method: 'POST',
    body: formData,
    skipContentType: true
  })
}

export function deleteDocument(id) {
  return apiFetch(`/api/documents/${id}`, { method: 'DELETE' })
}

export function getPreviewUrl(id, page = 1, dpi = 150) {
  return `/api/documents/${id}/preview?page=${page}&dpi=${dpi}`
}
