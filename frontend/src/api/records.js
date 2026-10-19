import { apiRequest } from './client.js'

export const listStudies = (q = '', fetchImpl) => apiRequest(`/studies?q=${encodeURIComponent(q)}`, {}, fetchImpl)
export const createStudy = (input, fetchImpl) => apiRequest('/studies', { method: 'POST', body: JSON.stringify(input) }, fetchImpl)
export const updateStudy = (id, input, fetchImpl) => apiRequest(`/studies/${id}`, { method: 'PUT', body: JSON.stringify(input) }, fetchImpl)
export const deleteStudy = (id, fetchImpl) => apiRequest(`/studies/${id}`, { method: 'DELETE' }, fetchImpl)

export const listTodos = (state = 'all', fetchImpl) => apiRequest(`/todos?state=${state}`, {}, fetchImpl)
export const createTodo = (input, fetchImpl) => apiRequest('/todos', { method: 'POST', body: JSON.stringify(input) }, fetchImpl)
export const updateTodo = (id, input, fetchImpl) => apiRequest(`/todos/${id}`, { method: 'PUT', body: JSON.stringify(input) }, fetchImpl)
export const toggleTodo = (id, isCompleted, fetchImpl) => apiRequest(`/todos/${id}/completion`, { method: 'PATCH', body: JSON.stringify({ is_completed: isCompleted }) }, fetchImpl)
export const deleteTodo = (id, fetchImpl) => apiRequest(`/todos/${id}`, { method: 'DELETE' }, fetchImpl)

export const listErrors = (state = 'all', q = '', fetchImpl) => apiRequest(`/errors?state=${state}&q=${encodeURIComponent(q)}`, {}, fetchImpl)
export const createErrorLog = (input, fetchImpl) => apiRequest('/errors', { method: 'POST', body: JSON.stringify(input) }, fetchImpl)
export const updateErrorLog = (id, input, fetchImpl) => apiRequest(`/errors/${id}`, { method: 'PUT', body: JSON.stringify(input) }, fetchImpl)
export const deleteErrorLog = (id, fetchImpl) => apiRequest(`/errors/${id}`, { method: 'DELETE' }, fetchImpl)

export const setVisibility = (type, id, isPublic, fetchImpl) => apiRequest(`/${type}/${id}/visibility`, { method: 'PATCH', body: JSON.stringify({ is_public: isPublic }) }, fetchImpl)
export const listPublicRecords = (type = 'all', q = '', fetchImpl) => apiRequest(`/public-records?record_type=${type}&q=${encodeURIComponent(q)}`, {}, fetchImpl)
export const getRecord = (type, id, fetchImpl) => apiRequest(`/${type}/${id}`, {}, fetchImpl)

export const listComments = (type, id, fetchImpl) => apiRequest(`/${type}/${id}/comments`, {}, fetchImpl)
export const createComment = (type, id, content, fetchImpl) => apiRequest(`/${type}/${id}/comments`, { method: 'POST', body: JSON.stringify({ content }) }, fetchImpl)
export const updateComment = (id, content, fetchImpl) => apiRequest(`/comments/${id}`, { method: 'PUT', body: JSON.stringify({ content }) }, fetchImpl)
export const deleteComment = (id, fetchImpl) => apiRequest(`/comments/${id}`, { method: 'DELETE' }, fetchImpl)
export const getLike = (type, id, fetchImpl) => apiRequest(`/${type}/${id}/like`, {}, fetchImpl)
export const addLike = (type, id, fetchImpl) => apiRequest(`/${type}/${id}/like`, { method: 'POST' }, fetchImpl)
export const removeLike = (type, id, fetchImpl) => apiRequest(`/${type}/${id}/like`, { method: 'DELETE' }, fetchImpl)
export const createReport = (targetType, targetId, reason, fetchImpl) => apiRequest('/reports', { method: 'POST', body: JSON.stringify({ target_type: targetType, target_id: targetId, reason }) }, fetchImpl)
export const listReports = (fetchImpl) => apiRequest('/admin/reports', {}, fetchImpl)
