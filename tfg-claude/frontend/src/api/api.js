/**
 * Cliente HTTP centralizado.
 * Usa Fetch API.
 */

import { normalizeListResponse } from './normalizers'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

/**
 * Decodifica un JWT sin dependencias externas.
 * Extrae el payload (segunda parte) y lo parsea.
 * Retorna null si hay error.
 */
export function parseJwt(token) {
  try {
    if (!token || typeof token !== 'string') {
      return null
    }

    const parts = token.split('.')
    if (parts.length !== 3) {
      console.error('Invalid JWT format')
      return null
    }

    // Decodificar payload (segunda parte)
    const payload = parts[1]
    const decoded = JSON.parse(atob(payload))
    return decoded
  } catch (error) {
    console.error('Error parsing JWT:', error)
    return null
  }
}

/**
 * Realiza una petición HTTP.
 */
async function apiCall(endpoint, options = {}) {
  const {
    method = 'GET',
    headers = {},
    body = null,
    token = null,
  } = options

  const finalHeaders = {
    'Content-Type': 'application/json',
    ...headers,
  }

  // Agregar token si existe
  if (token) {
    finalHeaders['Authorization'] = `Bearer ${token}`
  }

  const config = {
    method,
    headers: finalHeaders,
  }

  if (body) {
    config.body = JSON.stringify(body)
  }

  const url = `${API_BASE_URL}${endpoint}`

  try {
    const response = await fetch(url, config)

    // Parsear respuesta
    const data = response.status === 204 ? null : await response.json()

    if (!response.ok) {
      const error = new Error(data?.detail || `HTTP ${response.status}`)
      error.status = response.status
      error.data = data
      throw error
    }

    return data
  } catch (error) {
    console.error(`API Error (${method} ${endpoint}):`, error)
    throw error
  }
}

/**
 * GET
 */
export function apiGet(endpoint, { token } = {}) {
  return apiCall(endpoint, { method: 'GET', token })
}

/**
 * POST
 */
export function apiPost(endpoint, body, { token } = {}) {
  return apiCall(endpoint, { method: 'POST', body, token })
}

/**
 * PUT
 */
export function apiPut(endpoint, body, { token } = {}) {
  return apiCall(endpoint, { method: 'PUT', body, token })
}

/**
 * PATCH
 */
export function apiPatch(endpoint, body, { token } = {}) {
  return apiCall(endpoint, { method: 'PATCH', body, token })
}

/**
 * DELETE
 */
export function apiDelete(endpoint, { token } = {}) {
  return apiCall(endpoint, { method: 'DELETE', token })
}

// ============ AUTH ENDPOINTS ============

/**
 * Registra un nuevo usuario.
 */
export function authRegister(email, password, name) {
  return apiPost('/auth/register', { email, password, name })
}

/**
 * Login.
 */
export function authLogin(email, password) {
  return apiPost('/auth/login', { email, password })
}

/**
 * Obtiene datos del usuario actual (desde token).
 */
export function getCurrentUser(token) {
  return apiGet('/users/me', { token })
}

/**
 * Obtiene datos de un usuario específico.
 */
export function getUserProfile(userId, token) {
  return apiGet(`/users/${userId}`, { token })
}

/**
 * Actualiza perfil del usuario.
 */
export function updateUserProfile(userId, data, token) {
  return apiPut(`/users/${userId}`, data, { token })
}

// ============ DASHBOARD ENDPOINTS ============

/**
 * Obtiene resumen del dashboard del usuario.
 */
export function getDashboardSummary(token) {
  return apiGet('/dashboard/summary', { token })
}

/**
 * Obtiene cultivos del usuario en dashboard.
 */
export async function getDashboardCrops(token) {
  const response = await apiGet('/dashboard/crops', { token })
  return normalizeListResponse(response)
}

/**
 * Obtiene tareas del usuario en dashboard.
 */
export async function getDashboardTasks(token) {
  const response = await apiGet('/dashboard/tasks', { token })
  return normalizeListResponse(response)
}

/**
 * Obtiene calendarios en dashboard.
 */
export function getDashboardCalendars(token) {
  return apiGet('/dashboard/calendar', { token })
}

/**
 * Obtiene resumen de riego en dashboard.
 */
export async function getDashboardIrrigation(token) {
  const response = await apiGet('/dashboard/irrigation', { token })
  return normalizeListResponse(response)
}

/**
 * Obtiene requisitos ambientales en dashboard.
 */
export async function getDashboardEnvironmental(token) {
  const response = await apiGet('/dashboard/environmental', { token })
  return normalizeListResponse(response)
}

// ============ CROPS ENDPOINTS ============

/**
 * Obtiene cultivos propios del usuario.
 * Backend devuelve: { total, skip, limit, items: [...] }
 * Frontend recibe: [...]
 */
export async function getMycrops(token) {
  try {
    const response = await apiGet('/crops/my', { token })
    const crops = normalizeListResponse(response)
    console.log('getMycrops: normalized', crops.length, 'items')
    return crops
  } catch (err) {
    console.error('getMycrops error:', err)
    throw err
  }
}

/**
 * Obtiene cultivos publicados (catálogo).
 * Backend devuelve: { total, skip, limit, items: [...] }
 * Frontend recibe: [...]
 */
export async function getPublishedcrops(token, name = null) {
  try {
    const query = name ? `?name=${encodeURIComponent(name)}` : ''
    const response = await apiGet(`/crops/published${query}`, { token })
    const crops = normalizeListResponse(response)
    console.log('getPublishedcrops: normalized', crops.length, 'items')
    return crops
  } catch (err) {
    console.error('getPublishedcrops error:', err)
    throw err
  }
}

/**
 * Obtiene detalles de un cultivo específico.
 */
export function getCropDetails(cropId, token) {
  return apiGet(`/crops/${cropId}`, { token })
}

/**
 * Crea un nuevo cultivo.
 */
export function createCrop(data, token) {
  return apiPost('/crops/', data, { token })
}

/**
 * Actualiza un cultivo.
 */
export function updateCrop(cropId, data, token) {
  return apiPut(`/crops/${cropId}`, data, { token })
}

/**
 * Elimina un cultivo.
 */
export function deleteCrop(cropId, token) {
  return apiDelete(`/crops/${cropId}`, { token })
}

/**
 * Añade un cultivo del catálogo a mis cultivos.
 */
export function addCropToMyCrops(cropId, token) {
  return apiPost(`/crops/${cropId}/add-to-my-crops`, {}, { token })
}

// ============ CALENDAR ENDPOINTS ============

/**
 * Obtiene calendarios del usuario.
 */
export async function getCalendars(token) {
  const response = await apiGet('/calendar', { token })
  return normalizeListResponse(response)
}

/**
 * Obtiene eventos del calendario.
 */
export async function getCalendarEvents(token) {
  const response = await apiGet('/calendar/events', { token })
  return normalizeListResponse(response)
}

/**
 * Crea un nuevo calendario.
 * El crop_id debe ir como query parameter, no en el body.
 * El body contiene solo las fechas opcionales.
 */
export function createCalendar(data, token) {
  if (!data.crop_id) {
    throw new Error('crop_id es requerido')
  }
  const { crop_id, ...bodyData } = data
  return apiPost(`/calendar?crop_id=${crop_id}`, bodyData, { token })
}

/**
 * Obtiene detalles de un calendario.
 */
export function getCalendarDetails(calendarId, token) {
  return apiGet(`/calendar/${calendarId}`, { token })
}

/**
 * Actualiza un calendario.
 */
export function updateCalendar(calendarId, data, token) {
  return apiPut(`/calendar/${calendarId}`, data, { token })
}

/**
 * Obtiene el calendario de un cultivo específico.
 */
export function getCalendarForCrop(cropId, token) {
  return apiGet(`/calendar/crop/${cropId}`, { token })
}

/**
 * Actualiza el calendario de un cultivo.
 */
export function updateCalendarForCrop(cropId, data, token) {
  return apiPut(`/calendar/crop/${cropId}`, data, { token })
}

/**
 * Elimina un calendario.
 */
export function deleteCalendar(calendarId, token) {
  return apiDelete(`/calendar/${calendarId}`, { token })
}

/**
 * Activa un calendario.
 */
export function activateCalendar(calendarId, token) {
  return apiPost(`/calendar/${calendarId}/activate`, {}, { token })
}

/**
 * Avanza a la siguiente fase de un calendario.
 */
export function advancePhase(calendarId, token) {
  return apiPost(`/calendar/${calendarId}/advance`, {}, { token })
}

/**
 * Obtiene eventos de un calendario específico.
 */
export function getCalendarEventsForCalendar(calendarId, token) {
  return apiGet(`/calendar/${calendarId}/events`, { token })
}

// ============ TASKS ENDPOINTS ============

/**
 * Obtiene todas las tareas del usuario.
 * Backend devuelve: { total, skip, limit, items: [...] } o array directo
 * Frontend recibe: [...]
 */
export async function getTasks(token) {
  try {
    const response = await apiGet('/tasks/', { token })
    const tasks = normalizeListResponse(response)
    console.log('getTasks: normalized', tasks.length, 'items')
    return tasks
  } catch (err) {
    console.error('getTasks error:', err)
    throw err
  }
}

/**
 * Crea una nueva tarea.
 */
export function createTask(data, token) {
  return apiPost('/tasks/', data, { token })
}

/**
 * Obtiene detalles de una tarea.
 */
export function getTaskDetails(taskId, token) {
  return apiGet(`/tasks/${taskId}`, { token })
}

/**
 * Actualiza una tarea.
 */
export function updateTask(taskId, data, token) {
  return apiPatch(`/tasks/${taskId}`, data, { token })
}

/**
 * Elimina una tarea.
 */
export function deleteTask(taskId, token) {
  return apiDelete(`/tasks/${taskId}`, { token })
}

// ============ ADMIN ENDPOINTS ============

/**
 * Obtiene resumen del panel admin.
 */
export function getAdminSummary(token) {
  return apiGet('/admin/summary', { token })
}

/**
 * Obtiene lista de usuarios (admin).
 */
export async function getAdminUsers(token, skip = 0, limit = 50) {
  try {
    const response = await apiGet(`/admin/users?skip=${skip}&limit=${limit}`, { token })
    return normalizeListResponse(response)
  } catch (err) {
    console.error('getAdminUsers error:', err)
    throw err
  }
}

/**
 * Obtiene detalles de un usuario (admin).
 */
export function getAdminUser(userId, token) {
  return apiGet(`/admin/users/${userId}`, { token })
}

/**
 * Actualiza un usuario (admin).
 */
export function updateAdminUser(userId, data, token) {
  return apiPatch(`/admin/users/${userId}`, data, { token })
}

/**
 * Elimina un usuario (admin).
 */
export function deleteAdminUser(userId, token) {
  return apiDelete(`/admin/users/${userId}`, { token })
}

/**
 * Obtiene lista de cultivos (admin).
 */
export async function getAdminCrops(token, skip = 0, limit = 50) {
  try {
    const response = await apiGet(`/admin/crops?skip=${skip}&limit=${limit}`, { token })
    return normalizeListResponse(response)
  } catch (err) {
    console.error('getAdminCrops error:', err)
    throw err
  }
}

/**
 * Obtiene detalles de un cultivo (admin).
 */
export function getAdminCrop(cropId, token) {
  return apiGet(`/admin/crops/${cropId}`, { token })
}

/**
 * Actualiza un cultivo (admin).
 */
export function updateAdminCrop(cropId, data, token) {
  return apiPatch(`/admin/crops/${cropId}`, data, { token })
}

/**
 * Elimina un cultivo (admin).
 */
export function deleteAdminCrop(cropId, token) {
  return apiDelete(`/admin/crops/${cropId}`, { token })
}

/**
 * Obtiene lista de tareas (admin).
 */
export async function getAdminTasks(token, skip = 0, limit = 50) {
  try {
    const response = await apiGet(`/admin/tasks?skip=${skip}&limit=${limit}`, { token })
    return normalizeListResponse(response)
  } catch (err) {
    console.error('getAdminTasks error:', err)
    throw err
  }
}

/**
 * Obtiene detalles de una tarea (admin).
 */
export function getAdminTask(taskId, token) {
  return apiGet(`/admin/tasks/${taskId}`, { token })
}

/**
 * Actualiza una tarea (admin).
 */
export function updateAdminTask(taskId, data, token) {
  return apiPatch(`/admin/tasks/${taskId}`, data, { token })
}

/**
 * Elimina una tarea (admin).
 */
export function deleteAdminTask(taskId, token) {
  return apiDelete(`/admin/tasks/${taskId}`, { token })
}
