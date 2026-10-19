export const apiBaseUrl = import.meta.env?.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api'

export class ApiError extends Error {
  constructor(message, status) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

export async function apiRequest(path, options = {}, fetchImpl = fetch) {
  const response = await fetchImpl(`${apiBaseUrl}${path}`, {
    ...options,
    credentials: 'include',
    headers: {
      ...(options.body ? { 'Content-Type': 'application/json' } : {}),
      ...options.headers,
    },
  })
  if (response.status === 204) return null
  const data = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new ApiError(data.detail ?? '요청을 처리하지 못했습니다.', response.status)
  }
  return data
}
