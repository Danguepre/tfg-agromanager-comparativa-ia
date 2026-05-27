import { useState, useEffect } from 'react';
import { apiGet, apiPost, apiPatch, apiDelete, normalizeList } from '../api/api';

export default function Tasks() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [newTitle, setNewTitle] = useState('');
  const [newDescription, setNewDescription] = useState('');
  const [newPriority, setNewPriority] = useState('medium');
  const [showCreate, setShowCreate] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  async function loadTasks() {
    setLoading(true);
    try {
      const data = await apiGet('/tasks/');
      setTasks(normalizeList(data));
    } catch (err) {
      setError(err.message || 'Error al cargar tareas');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadTasks();
  }, []);

  async function handleCreate(e) {
    e.preventDefault();
    if (!newTitle.trim()) return;
    setSubmitting(true);
    setError('');
    try {
      await apiPost('/tasks/', {
        title: newTitle.trim(),
        description: newDescription.trim() || null,
        priority: newPriority,
        status: 'pending',
      });
      setNewTitle('');
      setNewDescription('');
      setNewPriority('medium');
      setShowCreate(false);
      await loadTasks();
    } catch (err) {
      setError(err.message || 'Error al crear tarea');
    } finally {
      setSubmitting(false);
    }
  }

  async function handleToggle(task) {
    try {
      setError('');
      await apiPatch(`/tasks/${task.id}`, {
        is_completed: !task.is_completed,
      });
      await loadTasks();
    } catch (err) {
      setError(err.message || 'Error al actualizar tarea');
    }
  }

  async function handleDelete(taskId) {
    if (!window.confirm('¿Eliminar esta tarea?')) return;
    try {
      setError('');
      await apiDelete(`/tasks/${taskId}`);
      await loadTasks();
    } catch (err) {
      setError(err.message || 'Error al eliminar tarea');
    }
  }

  const pendingTasks = tasks.filter((t) => !t.is_completed);
  const completedTasks = tasks.filter((t) => t.is_completed);

  if (loading && tasks.length === 0) return <div style={{ padding: '2rem', textAlign: 'center' }}>Cargando tareas...</div>;

  return (
    <div style={{ padding: '1.5rem', maxWidth: 800, margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h2 style={{ color: '#1a6b3c', margin: 0 }}>Tareas</h2>
        <button
          onClick={() => setShowCreate(!showCreate)}
          style={{
            background: '#1a6b3c', color: '#fff', border: 'none',
            borderRadius: 4, padding: '0.5rem 1rem', cursor: 'pointer'
          }}
        >
          {showCreate ? 'Cancelar' : 'Nueva tarea'}
        </button>
      </div>

      {error && (
        <div style={{
          background: '#fde8e8', color: '#c53030', padding: '0.75rem',
          borderRadius: 6, marginBottom: '1rem', border: '1px solid #fcc5c5'
        }}>
          {error}
        </div>
      )}

      {showCreate && (
        <form onSubmit={handleCreate} style={{
          background: '#f9f9f9', borderRadius: 8, padding: '1rem',
          marginBottom: '1.5rem'
        }}>
          <h3 style={{ marginTop: 0 }}>Nueva tarea</h3>
          <div style={{ marginBottom: '0.75rem' }}>
            <label style={{ display: 'block', fontWeight: 500, marginBottom: '0.25rem' }}>Título *</label>
            <input
              type="text" value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              required
              style={{ width: '100%', padding: '0.5rem', borderRadius: 4, border: '1px solid #ccc' }}
            />
          </div>
          <div style={{ marginBottom: '0.75rem' }}>
            <label style={{ display: 'block', fontWeight: 500, marginBottom: '0.25rem' }}>Descripción</label>
            <textarea
              value={newDescription}
              onChange={(e) => setNewDescription(e.target.value)}
              rows={2}
              style={{ width: '100%', padding: '0.5rem', borderRadius: 4, border: '1px solid #ccc' }}
            />
          </div>
          <div style={{ marginBottom: '0.75rem' }}>
            <label style={{ display: 'block', fontWeight: 500, marginBottom: '0.25rem' }}>Prioridad</label>
            <select
              value={newPriority}
              onChange={(e) => setNewPriority(e.target.value)}
              style={{ width: '100%', padding: '0.5rem', borderRadius: 4, border: '1px solid #ccc' }}
            >
              <option value="low">Baja</option>
              <option value="medium">Media</option>
              <option value="high">Alta</option>
            </select>
          </div>
          <button type="submit" disabled={submitting || !newTitle.trim()}
            style={{
              background: '#1a6b3c', color: '#fff', border: 'none',
              borderRadius: 4, padding: '0.5rem 1rem', cursor: submitting ? 'not-allowed' : 'pointer'
            }}
          >
            {submitting ? 'Creando...' : 'Crear tarea'}
          </button>
        </form>
      )}

      {tasks.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: '#888' }}>
          No hay tareas. Crea una nueva tarea para empezar.
        </div>
      ) : (
        <>
          <section style={{ marginBottom: '2rem' }}>
            <h3>Pendientes ({pendingTasks.length})</h3>
            {pendingTasks.length === 0 ? (
              <p style={{ color: '#888' }}>No hay tareas pendientes.</p>
            ) : (
              <div style={{ display: 'grid', gap: '0.5rem' }}>
                {pendingTasks.map((task) => (
                  <TaskCard
                    key={task.id}
                    task={task}
                    onToggle={handleToggle}
                    onDelete={handleDelete}
                  />
                ))}
              </div>
            )}
          </section>

          <section>
            <h3>Completadas ({completedTasks.length})</h3>
            {completedTasks.length === 0 ? (
              <p style={{ color: '#888' }}>No hay tareas completadas.</p>
            ) : (
              <div style={{ display: 'grid', gap: '0.5rem' }}>
                {completedTasks.map((task) => (
                  <TaskCard
                    key={task.id}
                    task={task}
                    onToggle={handleToggle}
                    onDelete={handleDelete}
                  />
                ))}
              </div>
            )}
          </section>
        </>
      )}
    </div>
  );
}

function TaskCard({ task, onToggle, onDelete }) {
  const priorityColors = {
    low: '#4caf50',
    medium: '#ff9800',
    high: '#f44336',
  };

  return (
    <div style={{
      background: '#fff', borderRadius: 8, padding: '0.75rem 1rem',
      boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
      display: 'flex', justifyContent: 'space-between', alignItems: 'center',
      opacity: task.is_completed ? 0.7 : 1
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flex: 1 }}>
        <input
          type="checkbox"
          checked={task.is_completed}
          onChange={() => onToggle(task)}
          style={{ width: 18, height: 18, cursor: 'pointer' }}
        />
        <div>
          <div style={{
            fontWeight: 500,
            textDecoration: task.is_completed ? 'line-through' : 'none',
            color: task.is_completed ? '#888' : '#333'
          }}>
            {task.title}
          </div>
          {task.description && (
            <div style={{ fontSize: '0.875rem', color: '#666', marginTop: '0.15rem' }}>
              {task.description}
            </div>
          )}
          <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.25rem' }}>
            <span style={{
              fontSize: '0.75rem', padding: '0.1rem 0.4rem', borderRadius: 4,
              background: priorityColors[task.priority] || '#888', color: '#fff'
            }}>
              {task.priority || 'media'}
            </span>
            {task.due_date && (
              <span style={{ fontSize: '0.75rem', color: '#888' }}>
                {new Date(task.due_date).toLocaleDateString()}
              </span>
            )}
          </div>
        </div>
      </div>
      <button
        onClick={() => onDelete(task.id)}
        style={{
          background: 'transparent', color: '#c53030', border: '1px solid #fcc5c5',
          borderRadius: 4, padding: '0.25rem 0.5rem', cursor: 'pointer',
          fontSize: '0.8rem', marginLeft: '0.5rem'
        }}
      >
        Eliminar
      </button>
    </div>
  );
}