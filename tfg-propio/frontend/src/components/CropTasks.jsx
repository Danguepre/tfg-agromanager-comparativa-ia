import { useCallback, useEffect, useState } from "react";
import { getCropTasks, createTask, assignTaskToCrop, deleteTask, updateTaskStatus } from "../api/api";

const STATUS_STYLES = {
  pending: { color: "#9A5B00", bg: "#FFF4E5" },
  completed: { color: "#1E6B3A", bg: "#EAF8EE" },
  in_progress: { color: "#1D4ED8", bg: "#E8F1FF" },
};

export default function CropTasks({ cropId, userId, token }) {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  
  const [taskName, setTaskName] = useState("");
  const [taskDesc, setTaskDesc] = useState("");
  const [taskStatus, setTaskStatus] = useState("pending");
  const [saving, setSaving] = useState(false);

  const loadTasks = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getCropTasks(token, cropId);
      setTasks(data || []);
    } catch (err) {
      setError(err.message || "Error al cargar tareas");
    } finally {
      setLoading(false);
    }
  }, [cropId, token]);

  useEffect(() => {
    loadTasks();
  }, [loadTasks]);

  const handleCreateTask = async () => {
    if (!taskName.trim() || !taskDesc.trim()) {
      setError("Nombre y descripción son obligatorios");
      return;
    }

    setSaving(true);
    setError(null);
    setSuccess(null);

    try {
      const newTask = await createTask(token, {
        user_id: userId,
        name: taskName,
        description: taskDesc,
        status: taskStatus,
      });

      await assignTaskToCrop(token, newTask.id, cropId);

      await loadTasks();

      setTaskName("");
      setTaskDesc("");
      setTaskStatus("pending");
      setShowForm(false);
      setSuccess("✅ Tarea creada exitosamente");
    } catch (err) {
      setError(err.message || "Error al crear tarea");
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteTask = async (taskId) => {
    if (!window.confirm("¿Estás seguro de que deseas eliminar esta tarea?")) return;

    try {
      await deleteTask(token, taskId);
      setSuccess("✅ Tarea eliminada exitosamente");
      await loadTasks();
    } catch (err) {
      setError(err.message || "Error al eliminar tarea");
    }
  };

  const handleToggleStatus = async (task) => {
    const newStatus = task.status === "completed" ? "pending" : "completed";
    try {
      await updateTaskStatus(token, task.id, newStatus);
      await loadTasks();
    } catch (err) {
      setError(err.message || "Error al actualizar estado");
    }
  };

  const getStatusStyle = (status) => {
    const normalized = String(status || "").toLowerCase().replace(/\s+/g, "_");
    return STATUS_STYLES[normalized] || { color: "#475569", bg: "#EEF2F7" };
  };

  return (
    <section style={containerStyle}>
      <div style={headerStyle}>
        <h3 style={titleStyle}>📋 Tareas del Cultivo</h3>
        <button
          onClick={() => setShowForm(!showForm)}
          style={buttonStyle}
        >
          {showForm ? "❌ Cancelar" : "➕ Nueva Tarea"}
        </button>
      </div>

      {error && <div style={errorStyle}>{error}</div>}
      {success && <div style={successStyle}>{success}</div>}

      {showForm && (
        <form style={formStyle} onSubmit={(e) => { e.preventDefault(); handleCreateTask(); }}>
          <input
            type="text"
            placeholder="Nombre de la tarea"
            value={taskName}
            onChange={(e) => setTaskName(e.target.value)}
            style={inputStyle}
          />
          <textarea
            placeholder="Descripción"
            value={taskDesc}
            onChange={(e) => setTaskDesc(e.target.value)}
            style={{ ...inputStyle, minHeight: "100px", resize: "vertical" }}
          />
          <select
            value={taskStatus}
            onChange={(e) => setTaskStatus(e.target.value)}
            style={inputStyle}
          >
            <option value="pending">Pendiente</option>
            <option value="in_progress">En Progreso</option>
            <option value="completed">Completada</option>
          </select>
          <button
            type="submit"
            disabled={saving}
            style={{
              ...submitButtonStyle,
              opacity: saving ? 0.6 : 1,
              cursor: saving ? "not-allowed" : "pointer",
            }}
          >
            {saving ? "Guardando..." : "Crear Tarea"}
          </button>
        </form>
      )}

      {loading ? (
        <p style={loadingStyle}>Cargando tareas...</p>
      ) : tasks.length === 0 ? (
        <p style={emptyStyle}>No hay tareas para este cultivo</p>
      ) : (
        <div style={tasksListStyle}>
          {tasks.map((task) => (
            <div key={task.id} style={taskCardStyle}>
              <div style={taskHeaderStyle}>
                <h4 style={taskNameStyle}>{task.name}</h4>
                <span
                  style={{
                    ...statusBadgeStyle,
                    color: getStatusStyle(task.status).color,
                    backgroundColor: getStatusStyle(task.status).bg,
                  }}
                >
                  {String(task.status || "").charAt(0).toUpperCase() + String(task.status || "").slice(1)}
                </span>
              </div>
              <p style={taskDescStyle}>{task.description}</p>
              <div style={taskActionsStyle}>
                <button
                  onClick={() => handleToggleStatus(task)}
                  style={{
                    ...actionButtonStyle,
                    backgroundColor: task.status === "completed" ? "#FFA500" : "#22C55E",
                  }}
                >
                  {task.status === "completed" ? "↩️ Deshacer" : "✓ Completar"}
                </button>
                <button
                  onClick={() => handleDeleteTask(task.id)}
                  style={{ ...actionButtonStyle, backgroundColor: "#EF4444" }}
                >
                  🗑️ Eliminar
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

const containerStyle = {
  marginTop: "2rem",
  padding: "1.5rem",
  backgroundColor: "#FAFAFA",
  borderRadius: "0.75rem",
  border: "1px solid #E5E7EB",
};

const headerStyle = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  marginBottom: "1rem",
};

const titleStyle = {
  fontSize: "1.25rem",
  fontWeight: "600",
  margin: 0,
  color: "#1F2937",
};

const buttonStyle = {
  padding: "0.5rem 1rem",
  backgroundColor: "#3B82F6",
  color: "white",
  border: "none",
  borderRadius: "0.5rem",
  cursor: "pointer",
  fontSize: "0.9rem",
  fontWeight: "500",
  transition: "background-color 0.2s",
};

const formStyle = {
  display: "flex",
  flexDirection: "column",
  gap: "1rem",
  marginBottom: "1.5rem",
  padding: "1rem",
  backgroundColor: "white",
  borderRadius: "0.5rem",
  border: "1px solid #E5E7EB",
};

const inputStyle = {
  padding: "0.75rem",
  border: "1px solid #D1D5DB",
  borderRadius: "0.375rem",
  fontSize: "0.9rem",
  fontFamily: "inherit",
};

const submitButtonStyle = {
  padding: "0.75rem",
  backgroundColor: "#10B981",
  color: "white",
  border: "none",
  borderRadius: "0.375rem",
  cursor: "pointer",
  fontWeight: "600",
};

const errorStyle = {
  padding: "0.75rem",
  backgroundColor: "#FEE2E2",
  color: "#B91C1C",
  borderRadius: "0.375rem",
  marginBottom: "1rem",
};

const successStyle = {
  padding: "0.75rem",
  backgroundColor: "#DCFCE7",
  color: "#166534",
  borderRadius: "0.375rem",
  marginBottom: "1rem",
};

const loadingStyle = {
  textAlign: "center",
  color: "#6B7280",
  padding: "1rem",
};

const emptyStyle = {
  textAlign: "center",
  color: "#9CA3AF",
  padding: "2rem",
  fontSize: "0.95rem",
};

const tasksListStyle = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))",
  gap: "1rem",
};

const taskCardStyle = {
  padding: "1rem",
  backgroundColor: "white",
  borderRadius: "0.5rem",
  border: "1px solid #E5E7EB",
  boxShadow: "0 1px 2px rgba(0,0,0,0.05)",
};

const taskHeaderStyle = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "flex-start",
  marginBottom: "0.5rem",
};

const taskNameStyle = {
  margin: 0,
  fontSize: "1rem",
  fontWeight: "600",
  color: "#1F2937",
};

const statusBadgeStyle = {
  padding: "0.25rem 0.75rem",
  borderRadius: "0.25rem",
  fontSize: "0.8rem",
  fontWeight: "500",
};

const taskDescStyle = {
  margin: "0.5rem 0",
  color: "#6B7280",
  fontSize: "0.9rem",
  lineHeight: "1.4",
};

const taskActionsStyle = {
  display: "flex",
  gap: "0.5rem",
  marginTop: "1rem",
};

const actionButtonStyle = {
  flex: 1,
  padding: "0.5rem",
  color: "white",
  border: "none",
  borderRadius: "0.375rem",
  cursor: "pointer",
  fontSize: "0.85rem",
  fontWeight: "500",
  transition: "opacity 0.2s",
};
