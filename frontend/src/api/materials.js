import { ApiError, apiBaseUrl, apiRequest } from './client.js'


export function createMaterial({ title, memo, file }, fetchImpl) {
  const body = new FormData()
  body.append('title', title)
  if (memo) body.append('memo', memo)
  body.append('file', file)
  return apiRequest('/materials', { method: 'POST', body }, fetchImpl)
}


export function listMaterials(fetchImpl) {
  return apiRequest('/materials', { method: 'GET' }, fetchImpl)
}


export function deleteMaterial(id, fetchImpl) {
  return apiRequest(`/materials/${id}`, { method: 'DELETE' }, fetchImpl)
}


export function getMaterialFileUrl(id) {
  return `${apiBaseUrl}/materials/${encodeURIComponent(id)}/file`
}


function filenameFromDisposition(value) {
  if (!value) return ''
  const encoded = value.match(/filename\*=UTF-8''([^;]+)/i)?.[1]
  if (encoded) {
    try {
      return decodeURIComponent(encoded)
    } catch {
      return ''
    }
  }
  return value.match(/filename="?([^";]+)"?/i)?.[1] ?? ''
}


export async function fetchMaterialFile(id, fetchImpl = fetch) {
  const response = await fetchImpl(`${apiBaseUrl}/materials/${id}/file`, {
    method: 'GET',
    credentials: 'include',
  })
  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    throw new ApiError(data.detail ?? '원본 파일을 열지 못했습니다.', response.status)
  }
  return {
    blob: await response.blob(),
    filename: filenameFromDisposition(response.headers.get('content-disposition')),
  }
}
