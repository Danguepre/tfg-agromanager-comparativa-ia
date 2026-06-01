/**
 * Utilidades para normalizar respuestas de la API.
 * El backend devuelve estructuras paginadas { total, skip, limit, items }
 * pero el frontend a veces espera arrays directos.
 */

/**
 * Normaliza respuesta de lista para asegurar que siempre es un array.
 * Acepta:
 * - Array directo: [...]
 * - Objeto paginado: { items: [...] }
 * - Objeto paginado: { crops: [...] }
 * - Objeto paginado: { data: [...] }
 * - Objeto paginado: { total, skip, limit, items }
 *
 * @param {any} response - Respuesta del API
 * @returns {Array} Array normalizado (vacío si no se puede extraer)
 */
export function normalizeListResponse(response) {
  if (!response) {
    return []
  }

  // Si ya es un array, devolverlo
  if (Array.isArray(response)) {
    return response
  }

  // Si es un objeto, buscar propiedades comunes que contengan arrays
  if (typeof response === 'object') {
    if (Array.isArray(response.items)) {
      return response.items
    }
    if (Array.isArray(response.crops)) {
      return response.crops
    }
    if (Array.isArray(response.data)) {
      return response.data
    }
    if (Array.isArray(response.results)) {
      return response.results
    }
  }

  // Si no se puede extraer, retornar array vacío
  console.warn('normalizeListResponse: Could not extract array from response', response)
  return []
}

/**
 * Normaliza respuesta de detalle (single item).
 * Acepta:
 * - Objeto directo: { id, name, ... }
 * - Objeto envuelto: { item: { id, name, ... } }
 * - Objeto envuelto: { crop: { id, name, ... } }
 * - Objeto envuelto: { data: { id, name, ... } }
 *
 * @param {any} response - Respuesta del API
 * @returns {object} Objeto normalizado (vacío si no se puede extraer)
 */
export function normalizeDetailResponse(response) {
  if (!response) {
    return {}
  }

  // Si es un objeto directo con propiedades esperadas, es probablemente un detalle
  if (typeof response === 'object' && !Array.isArray(response)) {
    // Verificar si tiene propiedades esperadas (heurística)
    if (response.id !== undefined || response.name !== undefined) {
      return response
    }

    // Si tiene propiedades envueltas, desenvueltas
    if (response.item && typeof response.item === 'object') {
      return response.item
    }
    if (response.crop && typeof response.crop === 'object') {
      return response.crop
    }
    if (response.data && typeof response.data === 'object' && !Array.isArray(response.data)) {
      return response.data
    }
  }

  // Si no se puede extraer, retornar objeto vacío
  console.warn('normalizeDetailResponse: Could not extract object from response', response)
  return {}
}

/**
 * Seguramente extrae el total de una respuesta paginada.
 *
 * @param {any} response - Respuesta del API
 * @returns {number} Total de items
 */
export function extractTotal(response) {
  if (!response || typeof response !== 'object') {
    return 0
  }
  return response.total || 0
}

/**
 * Seguramente extrae un valor específico con fallback.
 *
 * @param {any} obj - Objeto
 * @param {string} key - Clave
 * @param {any} defaultValue - Valor por defecto
 * @returns {any} Valor extraído o por defecto
 */
export function safeGet(obj, key, defaultValue = null) {
  if (!obj || typeof obj !== 'object') {
    return defaultValue
  }
  return obj[key] !== undefined ? obj[key] : defaultValue
}
