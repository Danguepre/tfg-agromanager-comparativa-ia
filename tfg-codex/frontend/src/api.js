const API_URL = (import.meta.env.VITE_API_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
const TOKEN_KEY = "agromanager_access_token";
const USER_KEY = "agromanager_user";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function getStoredUser() {
  const raw = localStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export function saveSession(token, user = null) {
  localStorage.setItem(TOKEN_KEY, token);
  if (user) localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function clearSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

export function normalizeList(payload) {
  if (Array.isArray(payload)) return payload;
  if (!payload || typeof payload !== "object") return [];

  const keys = ["items", "data", "users", "crops", "tasks", "calendars", "events", "results"];
  for (const key of keys) {
    if (Array.isArray(payload[key])) return payload[key];
  }

  return [];
}

function buildUrl(path, query) {
  const url = new URL(path.startsWith("http") ? path : `${API_URL}${path}`);
  Object.entries(query || {}).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") url.searchParams.set(key, value);
  });
  return url.toString();
}

async function parseResponse(response) {
  if (response.status === 204) return null;

  const text = await response.text();
  if (!text) return null;

  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

function errorMessage(payload, fallback) {
  if (!payload) return fallback;
  if (typeof payload === "string") return payload;
  if (typeof payload.detail === "string") return payload.detail;
  if (Array.isArray(payload.detail)) {
    return payload.detail.map((item) => item.msg || item.message || "Error de validacion").join(". ");
  }
  return payload.message || fallback;
}

export async function apiRequest(path, options = {}) {
  const { query, auth = true, body, headers = {}, ...rest } = options;
  const requestHeaders = new Headers(headers);
  const token = getToken();

  let requestBody = body;
  if (body && !(body instanceof FormData) && !(body instanceof URLSearchParams)) {
    requestHeaders.set("Content-Type", "application/json");
    requestBody = JSON.stringify(body);
  }

  if (auth && token) requestHeaders.set("Authorization", `Bearer ${token}`);

  const response = await fetch(buildUrl(path, query), {
    ...rest,
    headers: requestHeaders,
    body: requestBody,
  });
  const payload = await parseResponse(response);

  if (response.status === 401) {
    clearSession();
    if (!window.location.pathname.startsWith("/login")) {
      window.dispatchEvent(new CustomEvent("agromanager:unauthorized"));
    }
  }

  if (!response.ok) {
    if (response.status === 403) throw new Error("No tienes permisos de administrador");
    const fallback = `Error HTTP ${response.status}`;
    throw new Error(errorMessage(payload, fallback));
  }

  return payload;
}

export async function loginRequest(email, password) {
  const form = new URLSearchParams();
  form.set("username", email);
  form.set("password", password);
  return apiRequest("/auth/login", {
    method: "POST",
    body: form,
    auth: false,
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
}

export async function registerRequest(payload) {
  return apiRequest("/users/", { method: "POST", body: payload, auth: false });
}

export function getAdminSummary() {
  return apiRequest("/admin/summary");
}

export function getAdminUsers() {
  return apiRequest("/admin/users");
}

export function getAdminUser(userId) {
  return apiRequest(`/admin/users/${userId}`);
}

export function updateAdminUser(userId, payload) {
  return apiRequest(`/admin/users/${userId}`, { method: "PATCH", body: payload });
}

export function deleteAdminUser(userId) {
  return apiRequest(`/admin/users/${userId}`, { method: "DELETE" });
}

export function getAdminCrops() {
  return apiRequest("/admin/crops");
}

export function getAdminCrop(cropId) {
  return apiRequest(`/admin/crops/${cropId}`);
}

export function updateAdminCrop(cropId, payload) {
  return apiRequest(`/admin/crops/${cropId}`, { method: "PATCH", body: payload });
}

export function deleteAdminCrop(cropId) {
  return apiRequest(`/admin/crops/${cropId}`, { method: "DELETE" });
}

export function getAdminTasks() {
  return apiRequest("/admin/tasks");
}

export function getAdminTask(taskId) {
  return apiRequest(`/admin/tasks/${taskId}`);
}

export function updateAdminTask(taskId, payload) {
  return apiRequest(`/admin/tasks/${taskId}`, { method: "PATCH", body: payload });
}

export function deleteAdminTask(taskId) {
  return apiRequest(`/admin/tasks/${taskId}`, { method: "DELETE" });
}
