import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { getTasks, getCrops, createTask, assignTaskToCrop, deleteTask, updateTaskStatus } from "../api/api";

const parseJwt = (token) => {
  try {
    const payload = token.split(".")[1];
    const decoded = atob(payload.replace(/-/g, "+").replace(/_/g, "/"));
    return JSON.parse(decoded);
  } catch {
    return null;
  }
};

const STATUS_META = {
  pending: {
    label: "Pendiente",
    background: "#FFF4E5",
    color: "#9A5B00",
    dot: "#F59E0B",
  },
  completed: {
    label: "Completada",
    background: "#EAF8EE",
    color: "#1E6B3A",
    dot: "#22C55E",
  },
  in_progress: {
    label: "En progreso",
    background: "#E8F1FF",
    color: "#1D4ED8",
    dot: "#3B82F6",
  },
};

const normalizeStatus = (status) => {
  if (!status) return "unknown";
  return String(status).trim().toLowerCase().replace(/\s+/g, "_");
};

const getStatusMeta = (status) => {
  const normalized = normalizeStatus(status);
  return (
    STATUS_META[normalized] || {
      label: status || "Sin estado",
      background: "#EEF2F7",
      color: "#475569",
      dot: "#94A3B8",
    }
  );
};

export default function Tasks({ token }) {
  const [searchParams] = useSearchParams();
  const cropIdFromUrl = searchParams.get("cropId");
  
  const [tasks, setTasks] = useState([]);
  const [crops, setCrops] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [statusFilter, setStatusFilter] = useState("all");
  const [showCreateForm, setShowCreateForm] = useState(!!cropIdFromUrl);
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState(null);

  const [taskName, setTaskName] = useState("");
  const [taskDesc, setTaskDesc] = useState("");
  const [taskStatus, setTaskStatus] = useState("pending");
  const [selectedCropId, setSelectedCropId] = useState(cropIdFromUrl || "");

  const currentUser = useMemo(() => parseJwt(token), [token]);

  const handleCreateTask = async () => {
    if (!taskName.trim() || !taskDesc.trim() || !selectedCropId) {
      setCreateError("Nombre, descripción y cultivo son obligatorios");
      return;
    }

    setCreating(true);
    setCreateError(null);

    try {
      const newTask = await createTask(token, {
        user_id: currentUser?.user_id,
        name: taskName,
        description: taskDesc,
        status: taskStatus,
      });

      await assignTaskToCrop(token, newTask.id, selectedCropId);

      const updatedTasks = await getTasks(token);
      setTasks(Array.isArray(updatedTasks) ? updatedTasks : []);

      setTaskName("");
      setTaskDesc("");
      setTaskStatus("pending");
      if (!cropIdFromUrl) {
        setSelectedCropId("");
      }
      setShowCreateForm(false);
    } catch (err) {
      setCreateError(err.message || "Error al crear tarea");
    } finally {
      setCreating(false);
    }
  };

  const handleDeleteTask = async (taskId) => {
    if (!window.confirm("¿Estás seguro de que deseas eliminar esta tarea?")) return;

    try {
      await deleteTask(token, taskId);
      const updatedTasks = await getTasks(token);
      setTasks(Array.isArray(updatedTasks) ? updatedTasks : []);
    } catch (err) {
      setError(err.message || "Error al eliminar tarea");
    }
  };

  const handleToggleStatus = async (task) => {
    const newStatus = task.status === "completed" ? "pending" : "completed";
    try {
      await updateTaskStatus(token, task.id, newStatus);
      const updatedTasks = await getTasks(token);
      setTasks(Array.isArray(updatedTasks) ? updatedTasks : []);
    } catch (err) {
      setError(err.message || "Error al actualizar estado");
    }
  };

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      setError(null);

      try {
        const [tasksData, cropsData] = await Promise.all([
          getTasks(token),
          getCrops(token)
        ]);
        setTasks(Array.isArray(tasksData) ? tasksData : []);
        setCrops(Array.isArray(cropsData) ? cropsData : []);
      } catch (err) {
        setError(err.message || "No se pudieron cargar los datos");
        setTasks([]);
        setCrops([]);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [token]);

  const availableStatuses = useMemo(() => {
    const uniqueStatuses = Array.from(
      new Set(tasks.map((task) => normalizeStatus(task.status)).filter(Boolean))
    );
    return uniqueStatuses;
  }, [tasks]);

  const filteredTasks = useMemo(() => {
    if (statusFilter === "all") return tasks;
    return tasks.filter((task) => normalizeStatus(task.status) === normalizeStatus(statusFilter));
  }, [tasks, statusFilter]);

  if (loading) {
    return (
      <main style={page}>
        <section style={heroSection}>
          <span style={eyebrow}>Tareas agrícolas</span>
          <h1 style={title}>Cargando tus tareas</h1>
          <p style={description}>
            Estamos recuperando la planificación registrada en el backend.
          </p>
        </section>

        <section style={contentSection}>
          <div style={feedbackCard}>
            <div style={spinner}></div>
            <p style={feedbackText}>Cargando datos...</p>
          </div>
        </section>
      </main>
    );
  }

  if (error) {
    return (
      <main style={page}>
        <section style={heroSection}>
          <span style={eyebrow}>Tareas agrícolas</span>
          <h1 style={title}>Error al cargar</h1>
          <p style={description}>
            Hubo un problema al recuperar tus tareas.
          </p>
        </section>

        <section style={contentSection}>
          <div style={errorCard}>
            <h3 style={errorTitle}>Error</h3>
            <p style={errorMessage}>{error}</p>
          </div>
        </section>
      </main>
    );
  }

  return (
    <main style={page}>
      <section style={heroSection}>
        <div style={heroTopRow}>
          <div>
            <span style={eyebrow}>Tareas agrícolas</span>
            <h1 style={title}>Gestiona tus tareas</h1>
            <p style={description}>
              Planifica, organiza y completa tus tareas agrícolas de forma eficiente.
            </p>
          </div>
        </div>
      </section>

      {showCreateForm && (
        <section style={createFormSection}>
          <h3 style={formTitle}>Crear Nueva Tarea</h3>
          
          {createError && <div style={errorBanner}>{createError}</div>}

          <div style={formGrid}>
            <input
              type="text"
              placeholder="Nombre de la tarea"
              value={taskName}
              onChange={(e) => setTaskName(e.target.value)}
              style={formInput}
            />
            <select
              value={selectedCropId}
              onChange={(e) => setSelectedCropId(e.target.value)}
              style={formInput}
              disabled={!!cropIdFromUrl}
            >
              <option value="">Selecciona un cultivo</option>
              {crops.map((crop) => (
                <option key={crop.id} value={crop.id}>
                  {crop.name}
                </option>
              ))}
            </select>
            <select
              value={taskStatus}
              onChange={(e) => setTaskStatus(e.target.value)}
              style={formInput}
            >
              <option value="pending">Pendiente</option>
              <option value="in_progress">En Progreso</option>
              <option value="completed">Completada</option>
            </select>
          </div>

          <textarea
            placeholder="Descripción de la tarea"
            value={taskDesc}
            onChange={(e) => setTaskDesc(e.target.value)}
            style={{ ...formInput, minHeight: "120px", resize: "vertical" }}
          />

          <button
            onClick={handleCreateTask}
            disabled={creating}
            style={{
              ...submitButton,
              opacity: creating ? 0.6 : 1,
              cursor: creating ? "not-allowed" : "pointer",
            }}
          >
            {creating ? "Creando..." : "Crear Tarea"}
          </button>
        </section>
      )}

      <section style={contentSection}>
        <div style={toolbar}>
          <button
            onClick={() => setStatusFilter("all")}
            style={{
              ...filterButton,
              ...(statusFilter === "all" ? activeFilterButton : {}),
            }}
          >
            📊 Todas
          </button>
          {availableStatuses.map((status) => (
            <button
              key={status}
              onClick={() => setStatusFilter(status)}
              style={{
                ...filterButton,
                ...(statusFilter === status ? activeFilterButton : {}),
              }}
            >
              {getStatusMeta(status).label}
            </button>
          ))}
          <button
            onClick={() => setShowCreateForm(!showCreateForm)}
            style={{
              ...filterButton,
              ...activeFilterButton,
              marginLeft: "auto",
              backgroundColor: showCreateForm ? "#EF4444" : "#10B981",
            }}
          >
            {showCreateForm ? "❌ Cancelar" : "➕ Nueva Tarea"}
          </button>
        </div>

        {filteredTasks.length === 0 ? (
          <div style={emptyState}>
            <h3 style={emptyTitle}>No hay tareas</h3>
            <p style={emptyText}>Crea una nueva tarea para comenzar.</p>
          </div>
        ) : (
          <div style={grid}>
            {filteredTasks.map((task) => {
              const taskCrop = crops.find((c) => c.id === task.crop_id);
              const meta = getStatusMeta(task.status);
              return (
                <article key={task.id} style={card}>
                  <div style={cardHeader}>
                    <div>
                      <div style={{ ...statusBadge, background: meta.background, color: meta.color }}>
                        <div style={{ ...statusDot, backgroundColor: meta.dot }}></div>
                        {meta.label}
                      </div>
                      <p style={taskId}>ID: {task.id}</p>
                    </div>
                  </div>

                  <div style={cardBody}>
                    <h3 style={taskTitle}>{task.name}</h3>
                    <p style={taskDescription}>{task.description}</p>
                  </div>

                  <div style={cardFooter}>
                    <div style={metaBlock}>
                      <span style={metaLabel}>Cultivo</span>
                      <span style={metaValue}>{taskCrop?.name || "No asignado"}</span>
                    </div>
                    <div style={metaBlock}>
                      <span style={metaLabel}>Estado</span>
                      <span style={metaValue}>{meta.label}</span>
                    </div>
                  </div>

                  <div style={actionButtonsContainer}>
                    <button
                      onClick={() => handleToggleStatus(task)}
                      style={{
                        ...actionButton,
                        backgroundColor: task.status === "completed" ? "#FFA500" : "#22C55E",
                      }}
                    >
                      {task.status === "completed" ? "↩️ Deshacer" : "✓ Completar"}
                    </button>
                    <button
                      onClick={() => handleDeleteTask(task.id)}
                      style={{ ...actionButton, backgroundColor: "#EF4444" }}
                    >
                      🗑️ Eliminar
                    </button>
                  </div>
                </article>
              );
            })}
          </div>
        )}
      </section>

      <style>{`
        @keyframes spin {
          to {
            transform: rotate(360deg);
          }
        }
      `}</style>
    </main>
  );
}

const page = {
  minHeight: "100vh",
  padding: "32px",
  background:
    "radial-gradient(circle at top left, rgba(114, 180, 120, 0.12), transparent 28%), linear-gradient(180deg, #F5FBF6 0%, #EEF7F1 100%)",
  fontFamily: "Inter, Arial, sans-serif",
  color: "#163326",
};

const heroSection = {
  marginBottom: "28px",
  padding: "32px",
  borderRadius: "28px",
  background: "linear-gradient(135deg, #F3FAF4 0%, #FFFFFF 100%)",
  boxShadow: "0 22px 50px rgba(15, 23, 42, 0.08)",
};

const heroTopRow = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "flex-start",
  gap: "24px",
  flexWrap: "wrap",
};

const eyebrow = {
  display: "inline-flex",
  padding: "10px 16px",
  borderRadius: "999px",
  background: "#E8F6EA",
  color: "#2E7D32",
  fontWeight: 700,
  fontSize: "0.92rem",
  marginBottom: "18px",
};

const title = {
  margin: 0,
  fontSize: "clamp(2rem, 4vw, 3.3rem)",
  lineHeight: 1.03,
  color: "#133824",
};

const description = {
  marginTop: "16px",
  maxWidth: "760px",
  fontSize: "1.02rem",
  lineHeight: 1.8,
  color: "#4A6356",
};

const toolbar = {
  display: "flex",
  gap: "12px",
  flexWrap: "wrap",
  marginBottom: "26px",
};

const filterButton = {
  padding: "12px 18px",
  borderRadius: "999px",
  border: "1px solid #D5E5D7",
  background: "white",
  color: "#2E593F",
  cursor: "pointer",
  fontWeight: 700,
  boxShadow: "0 8px 18px rgba(15, 23, 42, 0.05)",
};

const activeFilterButton = {
  background: "#2F8F4C",
  color: "white",
  border: "1px solid #2F8F4C",
  boxShadow: "0 14px 28px rgba(47, 143, 76, 0.18)",
};

const contentSection = {
  maxWidth: "1200px",
  margin: "0 auto",
};

const grid = {
  display: "grid",
  gap: "22px",
  gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
};

const card = {
  background: "white",
  borderRadius: "26px",
  padding: "24px",
  boxShadow: "0 24px 48px rgba(15, 23, 42, 0.08)",
  border: "1px solid rgba(126, 186, 137, 0.12)",
  display: "flex",
  flexDirection: "column",
  gap: "20px",
};

const cardHeader = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  gap: "12px",
};

const statusBadge = {
  display: "inline-flex",
  alignItems: "center",
  gap: "10px",
  padding: "9px 14px",
  borderRadius: "999px",
  fontWeight: 700,
  fontSize: "0.92rem",
};

const statusDot = {
  width: "10px",
  height: "10px",
  borderRadius: "999px",
  flexShrink: 0,
};

const taskId = {
  color: "#6B7D71",
  fontSize: "0.92rem",
  fontWeight: 700,
};

const cardBody = {
  display: "flex",
  flexDirection: "column",
  gap: "12px",
};

const taskTitle = {
  margin: 0,
  fontSize: "1.35rem",
  lineHeight: 1.25,
  color: "#173E2A",
};

const taskDescription = {
  margin: 0,
  color: "#587063",
  lineHeight: 1.75,
  fontSize: "0.98rem",
};

const cardFooter = {
  display: "grid",
  gap: "14px",
  gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))",
};

const metaBlock = {
  padding: "16px",
  borderRadius: "18px",
  background: "#F7FBF7",
  border: "1px solid #E3EFE4",
  display: "flex",
  flexDirection: "column",
  gap: "8px",
};

const metaLabel = {
  color: "#6A7B70",
  fontSize: "0.84rem",
  fontWeight: 700,
  textTransform: "uppercase",
  letterSpacing: "0.04em",
};

const metaValue = {
  color: "#254735",
  fontWeight: 600,
  lineHeight: 1.5,
};

const emptyState = {
  padding: "42px 28px",
  borderRadius: "24px",
  background: "white",
  boxShadow: "0 18px 40px rgba(15, 23, 42, 0.06)",
  textAlign: "center",
};

const emptyTitle = {
  margin: 0,
  color: "#244635",
  fontSize: "1.2rem",
  fontWeight: 700,
};

const emptyText = {
  margin: "12px 0 0 0",
  color: "#6A7A70",
  lineHeight: 1.7,
};

const feedbackCard = {
  display: "flex",
  alignItems: "center",
  gap: "16px",
  padding: "24px",
  borderRadius: "24px",
  background: "white",
  boxShadow: "0 18px 40px rgba(15, 23, 42, 0.06)",
};

const spinner = {
  width: "22px",
  height: "22px",
  borderRadius: "999px",
  border: "3px solid #D8E9DB",
  borderTopColor: "#2F8F4C",
  animation: "spin 0.9s linear infinite",
};

const feedbackText = {
  margin: 0,
  color: "#4C6458",
  fontWeight: 600,
};

const errorCard = {
  padding: "24px",
  borderRadius: "24px",
  background: "#FFF5F5",
  border: "1px solid #F4CACA",
  boxShadow: "0 18px 40px rgba(127, 29, 29, 0.05)",
};

const errorTitle = {
  margin: 0,
  color: "#8B1E1E",
  fontWeight: 800,
  fontSize: "1.05rem",
};

const errorMessage = {
  margin: "10px 0 0 0",
  color: "#9F2D2D",
  lineHeight: 1.7,
};

const createFormSection = {
  marginBottom: "32px",
  padding: "28px",
  borderRadius: "24px",
  background: "linear-gradient(135deg, #F3FAF4 0%, #FFFFFF 100%)",
  boxShadow: "0 22px 50px rgba(15, 23, 42, 0.08)",
  border: "1px solid rgba(126, 186, 137, 0.16)",
};

const formTitle = {
  margin: "0 0 1.5rem 0",
  fontSize: "1.3rem",
  fontWeight: 700,
  color: "#133824",
};

const formGrid = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
  gap: "16px",
  marginBottom: "16px",
};

const formInput = {
  padding: "12px 16px",
  borderRadius: "12px",
  border: "1px solid #D7E7D8",
  background: "white",
  color: "#1F3D2E",
  fontSize: "0.95rem",
  fontFamily: "inherit",
  width: "100%",
  boxSizing: "border-box",
};

const submitButton = {
  padding: "12px 24px",
  borderRadius: "12px",
  border: "none",
  background: "linear-gradient(135deg, #2F8F4C 0%, #5CAF75 100%)",
  color: "white",
  fontWeight: 700,
  cursor: "pointer",
  marginTop: "1rem",
};

const errorBanner = {
  padding: "12px 16px",
  backgroundColor: "#FEE2E2",
  color: "#B91C1C",
  borderRadius: "8px",
  marginBottom: "1rem",
  fontSize: "0.9rem",
};

const actionButtonsContainer = {
  display: "flex",
  gap: "12px",
  marginTop: "12px",
};

const actionButton = {
  flex: 1,
  padding: "10px 12px",
  color: "white",
  border: "none",
  borderRadius: "8px",
  cursor: "pointer",
  fontSize: "0.9rem",
  fontWeight: "600",
  transition: "opacity 0.2s",
};
