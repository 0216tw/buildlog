import { ApiError, apiRequest } from './client.js'

export { ApiError }


export function signupUser(input, fetchImpl) {
  return apiRequest(
    '/auth/signup',
    { method: 'POST', body: JSON.stringify(input) },
    fetchImpl,
  )
}


export function loginUser(input, fetchImpl) {
  return apiRequest(
    '/auth/login',
    { method: 'POST', body: JSON.stringify(input) },
    fetchImpl,
  )
}


export function getCurrentUser(fetchImpl) {
  return apiRequest('/auth/me', { method: 'GET' }, fetchImpl)
}


export function updateNickname(nickname, fetchImpl) {
  return apiRequest(
    '/users/me/nickname',
    { method: 'PATCH', body: JSON.stringify({ nickname }) },
    fetchImpl,
  )
}
