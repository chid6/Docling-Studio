export async function apiFetch(url, options = {}) {
  const headers = { ...options.headers }

  if (!options.skipContentType) {
    headers['Content-Type'] = 'application/json'
  }

  const response = await fetch(url, {
    ...options,
    headers
  })
  if (!response.ok) throw new Error(`API error: ${response.status}`)
  if (response.status === 204) return null
  return response.json()
}
