/**
 * Cliente API centralizado con Fetch API.
 * - Incluye automáticamente Authorization header si hay token.
 * - Maneja 401 limpiando sesión y redirigiendo a login.
 * - Normaliza respuestas de listas para evitar errores .map / .filter.
 * - Fallback entre localhost:8000 y 127.0.0.1:8000 para compatibilidad Windows.
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Obtiene el token del localStorage.
 */
function getToken() {
  return localStorage.getItem('access_token');
}

/**
 * Limpia sesión y redirige a login.
 */
function clearSession() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user');
  window.location.href = '/login';
}

/**
 * Normaliza una respuesta que podría ser array directo u objeto paginado.
 * Retorna siempre un array.
 */
export function normalizeList(data) {
  if (data === null || data === undefined) return [];
  if (Array.isArray(data)) return data;
  if (data.items && Array.isArray(data.items)) return data.items;
  if (data.data && Array.isArray(data.data)) return data.data;
  if (data.crops && Array.isArray(data.crops)) return data.crops;
  if (data.tasks && Array.isArray(data.tasks)) return data.tasks;
  if (data.results && Array.isArray(data.results)) return data.results;
  if (data.events && Array.isArray(data.events)) return data.events;
  if (data.calendars && Array.isArray(data.calendars)) return data.calendars;
  if (data.users && Array.isArray(data.users)) return data.users;
  return [];
}

/**
 * Realiza una petición fetch con manejo de errores unificado.
 * - HTTP 401: limpia sesión y redirige a login.
 * - HTTP 403: lanza error con mensaje de permisos.
 * - HTTP 500+: incluye detail del servidor si existe.
 * - Errores de red: intenta fallback a 127.0.0.1 si localhost falla.
 */
export async function apiRequest(endpoint, options = {}, auth = true) {
  const url = `${API_BASE}${endpoint}`;
  const headers = { ...options.headers };

  if (options.body && !(options.body instanceof FormData) && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }

  if (auth) {
    const token = getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
  }

  try {
    const response = await fetch(url, { ...options, headers });

    if (response.status === 204) {
      return null;
    }

    let data;
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      data = await response.json();
    } else {
      const text = await response.text();
      data = text || null;
    }

    if (!response.ok) {
      // 401 -> sesión inválida, redirigir a login
      if (response.status === 401) {
        clearSession();
        throw new Error('Sesión expirada. Redirigiendo a login...');
      }

      // 403 -> permisos insuficientes
      if (response.status === 403) {
        const detail = data?.detail || 'No tienes permisos de administrador';
        const error = new Error(`[403] ${endpoint}: ${detail}`);
        error.status = 403;
        error.data = data;
        throw error;
      }

      const detail = data?.detail || `Error HTTP ${response.status}`;
      const error = new Error(`[${response.status}] ${endpoint}: ${detail}`);
      error.status = response.status;
      error.data = data;
      throw error;
    }

    return data;
  } catch (error) {
    // Si ya es un error HTTP con status, propagarlo
    if (error.status) throw error;

    // Error de red: intentar con 127.0.0.1 como fallback si no se usó ya
    if (API_BASE === 'http://localhost:8000' && endpoint.startsWith('/dashboard/')) {
      const fallbackUrl = `http://127.0.0.1:8000${endpoint}`;
      try {
        const response = await fetch(fallbackUrl, { ...options, headers });
        if (response.status === 204) return null;
        let data;
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
          data = await response.json();
        } else {
          data = await response.text();
        }
        if (!response.ok) {
          if (response.status === 401) {
            clearSession();
            throw new Error('Sesión expirada.');
          }
          const detail = data?.detail || `Error HTTP ${response.status}`;
          const err = new Error(`[${response.status}] ${endpoint}: ${detail}`);
          err.status = response.status;
          err.data = data;
          throw err;
        }
        return data;
      } catch (fallbackError) {
        if (fallbackError.status) throw fallbackError;
        const msg = `No se pudo conectar con el backend (${API_BASE} ni http://127.0.0.1:8000). ¿Está el servidor encendido?`;
        const err2 = new Error(`${msg} (${endpoint})`);
        err2.status = 0;
        throw err2;
      }
    }

    const networkError = new Error(`No se pudo conectar con el backend en ${API_BASE}${endpoint}. Verifica que el servidor esté encendido.`);
    networkError.status = 0;
    throw networkError;
  }
}

export function apiGet(endpoint, auth = true) {
  return apiRequest(endpoint, { method: 'GET' }, auth);
}

export function apiPost(endpoint, body = null, auth = true) {
  return apiRequest(endpoint, {
    method: 'POST',
    body: body ? JSON.stringify(body) : null,
  }, auth);
}

export function apiPut(endpoint, body = null, auth = true) {
  return apiRequest(endpoint, {
    method: 'PUT',
    body: body ? JSON.stringify(body) : null,
  }, auth);
}

export function apiPatch(endpoint, body = null, auth = true) {
  return apiRequest(endpoint, {
    method: 'PATCH',
    body: body ? JSON.stringify(body) : null,
  }, auth);
}

export function apiDelete(endpoint, auth = true) {
  return apiRequest(endpoint, { method: 'DELETE' }, auth);
}

// ──────────────────────────────────────────
//  Admin API functions
// ──────────────────────────────────────────

export function getAdminSummary() {
  return apiGet('/admin/summary');
}

export function getAdminUsers() {
  return apiGet('/admin/users');
}

export function getAdminUser(userId) {
  return apiGet(`/admin/users/${userId}`);
}

export function updateAdminUser(userId, data) {
  return apiPatch(`/admin/users/${userId}`, data);
}

export function deleteAdminUser(userId) {
  return apiDelete(`/admin/users/${userId}`);
}

export function getAdminCrops() {
  return apiGet('/admin/crops');
}

export function getAdminCrop(cropId) {
  return apiGet(`/admin/crops/${cropId}`);
}

export function updateAdminCrop(cropId, data) {
  return apiPatch(`/admin/crops/${cropId}`, data);
}

export function deleteAdminCrop(cropId) {
  return apiDelete(`/admin/crops/${cropId}`);
}

export function getAdminTasks() {
  return apiGet('/admin/tasks');
}

export function getAdminTask(taskId) {
  return apiGet(`/admin/tasks/${taskId}`);
}

export function updateAdminTask(taskId, data) {
  return apiPatch(`/admin/tasks/${taskId}`, data);
}

export function deleteAdminTask(taskId) {
  return apiDelete(`/admin/tasks/${taskId}`);
}

export { API_BASE, getToken, clearSession };