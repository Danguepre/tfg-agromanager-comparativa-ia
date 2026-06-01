export const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const handleResponse = async (res, fallbackMessage) => {
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || fallbackMessage);
  }
  return res.json();
};

export const getCrops = async (token) => {
  const res = await fetch(`${API_URL}/crops/`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return handleResponse(res, "Error al obtener cultivos");
};

export const getMyCrops = async (token, params = {}) => {
  const searchParams = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && String(value).trim() !== "") {
      searchParams.append(key, String(value).trim());
    }
  });

  const query = searchParams.toString();
  const res = await fetch(`${API_URL}/crops/my${query ? `?${query}` : ""}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return handleResponse(res, "Error al obtener mis cultivos");
};

export const getPublishedCrops = async (token, params = {}) => {
  const searchParams = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && String(value).trim() !== "") {
      searchParams.append(key, String(value).trim());
    }
  });

  const query = searchParams.toString();
  const res = await fetch(`${API_URL}/crops/published${query ? `?${query}` : ""}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return handleResponse(res, "Error al obtener cultivos del catalogo");
};

export const addPublishedCropToMyCrops = async (token, cropId) => {
  const res = await fetch(`${API_URL}/crops/${cropId}/add-to-my-crops`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return handleResponse(res, "Error al anadir cultivo a mis cultivos");
};

export const getCropById = async (token, id) => {
  const res = await fetch(`${API_URL}/crops/${id}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return handleResponse(res, "Error al obtener cultivo");
};

export const createCrop = async (token, cropData) => {
  if (!(cropData instanceof FormData)) {
    throw new Error("createCrop expects FormData");
  }

  const res = await fetch(`${API_URL}/crops/`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: cropData,
  });
  return handleResponse(res, "Error al crear cultivo");
};

export const updateCrop = async (token, cropId, cropData) => {
  const res = await fetch(`${API_URL}/crops/${cropId}`, {
    method: "PUT",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(cropData),
  });
  return handleResponse(res, "Error al actualizar cultivo");
};

export const deleteCrop = async (token, cropId) => {
  const res = await fetch(`${API_URL}/crops/${cropId}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return handleResponse(res, "Error al quitar cultivo de mis cultivos");
};

export const getTasks = async (token) => {
  const res = await fetch(`${API_URL}/tasks/`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return handleResponse(res, "Error al obtener tareas");
};

export const getIrrigationByCrop = async (token, cropId) => {
  const res = await fetch(`${API_URL}/irrigation/crop/${cropId}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return res.ok ? res.json() : null;
};

export const createIrrigation = async (token, data) => {
  const res = await fetch(`${API_URL}/irrigation/`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
  return handleResponse(res, "Error al crear datos de riego");
};

export const updateIrrigation = async (token, irrigationId, data) => {
  const res = await fetch(`${API_URL}/irrigation/${irrigationId}`, {
    method: "PUT",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
  return handleResponse(res, "Error al actualizar datos de riego");
};

export const getEnvironmentalByCrop = async (token, cropId) => {
  const res = await fetch(`${API_URL}/environmental/crop/${cropId}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return res.ok ? res.json() : null;
};

export const createEnvironmental = async (token, data) => {
  const res = await fetch(`${API_URL}/environmental/`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
  return handleResponse(res, "Error al crear requisitos ambientales");
};

export const updateEnvironmental = async (token, environmentalId, data) => {
  const res = await fetch(`${API_URL}/environmental/${environmentalId}`, {
    method: "PUT",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
  return handleResponse(res, "Error al actualizar requisitos ambientales");
};

export const getCalendarByCrop = async (token, cropId) => {
  const res = await fetch(`${API_URL}/calendar/crop/${cropId}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return res.ok ? res.json() : null;
};

export const upsertCalendarByCrop = async (token, cropId, data) => {
  const res = await fetch(`${API_URL}/calendar/crop/${cropId}`, {
    method: "PUT",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ ...data, crop_id: cropId }),
  });
  return handleResponse(res, "Error al guardar calendario del cultivo");
};

export const activateCalendarByCrop = async (token, cropId) => {
  const res = await fetch(`${API_URL}/calendar/crop/${cropId}/activate`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return handleResponse(res, "Error al anadir cultivo al calendario");
};

export const advanceCalendarCropPhase = async (token, cropId) => {
  const res = await fetch(`${API_URL}/calendar/crop/${cropId}/advance`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return handleResponse(res, "Error al avanzar fase del cultivo");
};

export const getMyCalendarEvents = async (token) => {
  const res = await fetch(`${API_URL}/calendar/events`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return handleResponse(res, "Error al obtener eventos de calendario");
};

export const getDashboardSummary = async (token) => {
  const res = await fetch(`${API_URL}/dashboard/summary`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return handleResponse(res, "Error al obtener resumen personal");
};

export const getCalendarEvents = async (token, calendarId) => {
  const res = await fetch(`${API_URL}/calendar/${calendarId}/events`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return handleResponse(res, "Error al obtener eventos de calendario");
};

export const getCropTasks = async (token, cropId) => {
  const res = await fetch(`${API_URL}/tasks/crop/${cropId}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return res.ok ? res.json() : [];
};

export const createTask = async (token, taskData) => {
  const res = await fetch(`${API_URL}/tasks/`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(taskData),
  });
  return handleResponse(res, "Error al crear tarea");
};

export const assignTaskToCrop = async (token, taskId, cropId) => {
  const res = await fetch(`${API_URL}/tasks/assign`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ task_id: taskId, crop_id: cropId }),
  });
  return handleResponse(res, "Error al asignar tarea al cultivo");
};

export const deleteTask = async (token, taskId) => {
  const res = await fetch(`${API_URL}/tasks/${taskId}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return handleResponse(res, "Error al eliminar tarea");
};

export const updateTaskStatus = async (token, taskId, status) => {
  const res = await fetch(`${API_URL}/tasks/${taskId}`, {
    method: "PATCH",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ status }),
  });
  return handleResponse(res, "Error al actualizar estado de tarea");
};

const buildQuery = (params = {}) => {
  const searchParams = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && String(value).trim() !== "") {
      searchParams.append(key, String(value).trim());
    }
  });

  const query = searchParams.toString();
  return query ? `?${query}` : "";
};

export const getAdminSummary = async (token) => {
  const res = await fetch(`${API_URL}/admin/summary`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return handleResponse(res, "Error al obtener resumen de admin");
};

export const getAdminUsers = async (token, params = {}) => {
  const res = await fetch(`${API_URL}/admin/users${buildQuery(params)}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return handleResponse(res, "Error al obtener usuarios");
};

export const createAdminUser = async (token, userData) => {
  const res = await fetch(`${API_URL}/admin/users`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(userData),
  });
  return handleResponse(res, "Error al crear usuario");
};

export const updateAdminUser = async (token, userId, userData) => {
  const res = await fetch(`${API_URL}/admin/users/${userId}`, {
    method: "PUT",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(userData),
  });
  return handleResponse(res, "Error al actualizar usuario");
};

export const deleteAdminUser = async (token, userId) => {
  const res = await fetch(`${API_URL}/admin/users/${userId}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  });
  return handleResponse(res, "Error al eliminar usuario");
};

export const getAdminCrops = async (token, params = {}) => {
  const res = await fetch(`${API_URL}/admin/crops${buildQuery(params)}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return handleResponse(res, "Error al obtener cultivos de admin");
};

export const createAdminCrop = async (token, cropData) => {
  const res = await fetch(`${API_URL}/admin/crops`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(cropData),
  });
  return handleResponse(res, "Error al crear cultivo");
};

export const updateAdminCrop = async (token, cropId, cropData) => {
  const res = await fetch(`${API_URL}/admin/crops/${cropId}`, {
    method: "PUT",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(cropData),
  });
  return handleResponse(res, "Error al actualizar cultivo");
};

export const deleteAdminCrop = async (token, cropId) => {
  const res = await fetch(`${API_URL}/admin/crops/${cropId}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  });
  return handleResponse(res, "Error al eliminar cultivo");
};
