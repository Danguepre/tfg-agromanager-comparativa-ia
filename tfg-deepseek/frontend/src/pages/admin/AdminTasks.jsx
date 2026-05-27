import { useState, useEffect } from 'react';
import { getAdminTasks, updateAdminTask, deleteAdminTask } from '../../api/api';

export default function AdminTasks() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [editingId, setEditingId] = useState(null);
  const [editForm, setEditForm] = useState({});
  const [deleteConfirm, setDeleteConfirm] = useState(null);
  const [successMsg, setSuccessMsg] = useState('');

  async function loadTasks() {
    try {
      setLoading(true);
      const data = await getAdminTasks();
      setTasks(Array.isArray(data) ? data : []);
      setError('');
    } catch (err) {
      setError(err.message || 'Error al cargar tareas');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { loadTasks(); }, []);

  function startEdit(task) {
    setEditingId(task.id);
    setEditForm({
      title: task.title || '',
      description: task.description || '',
      status: task.status || 'pending',
      is_completed: task.is_completed || false,
      due_date: task.due_date || '',
    });
  }

  function cancelEdit() {
    setEditingId(null);
    setEditForm({});
  }

  async function saveEdit(taskId) {
    try {
      const payload = {};
      if (editForm.title !== undefined) payload.title = editForm.title;
      if (editForm.description !== undefined) payload.description = editForm.description;
      if (editForm.status !== undefined) payload.status = editForm.status;
      if (editForm.is_completed !== undefined) payload.is_completed = editForm.is_completed;
      if (editForm.due_date !== undefined && editForm.due_date) {
        payload.due_date = editForm.due_date;
      }

      await updateAdminTask(taskId, payload);
      setSuccessMsg('Tarea actualizada correctamente');
      setEditingId(null);
      setEditForm({});
      setTimeout(() => setSuccessMsg(''), 3000);
      loadTasks();
    } catch (err) {
      setError(err.message || 'Error al actualizar tarea');
    }
  }

  async function confirmDelete(taskId) {
    try {
      await deleteAdminTask(taskId);
      setSuccessMsg('Tarea eliminada correctamente');
      setDeleteConfirm(null);
      setTimeout(() => setSuccessMsg(''), 3000);
      loadTasks();
    } catch (err) {
      setError(err.message || 'Error al eliminar tarea');
    }
  }

  function toggleCompleted(task) {
    const newCompleted = !task.is_completed;
    const newStatus = newCompleted ? 'completed' : 'pending';
    updateAdminTask(task.id, { is_completed: newCompleted, status: newStatus })
      .then(() => {
        setSuccessMsg(`Tarea marcada como ${newCompleted ? 'completada' : 'pendiente'}`);
        setTimeout(() => setSuccessMsg(''), 3000);
        loadTasks();
      })
      .catch(err => setError(err.message || 'Error al cambiar estado'));
  }

  return (
    <div style={{ padding: '1.5rem', maxWidth: 1200, margin: '0 auto' }}>
      <h2 style={{ color: '#1a6b3c', marginBottom: '1rem' }}>Administrar Tareas</h2>

      {successMsg && (
        <div style={{ background: '#d4edda', color: '#155724', padding: '0.75rem', borderRadius: 4, marginBottom: '1rem' }}>
          {successMsg}
        </div>
      )}

      {error && (
        <div style={{ background: '#f8d7da', color: '#721c24', padding: '0.75rem', borderRadius: 4, marginBottom: '1rem' }}>
          {error}
          <button onClick={() => setError('')} style={{ marginLeft: '1rem', background: 'none', border: 'none', cursor: 'pointer', color: '#721c24' }}>✕</button>
        </div>
      )}

      {loading ? (
        <div style={{ textAlign: 'center', padding: '2rem' }}>Cargando tareas...</div>
      ) : tasks.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '2rem', color: '#888' }}>No hay tareas registradas.</div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', background: '#fff', borderRadius: 8, boxShadow: '0 1px 4px rgba(0,0,0,0.1)' }}>
            <thead>
              <tr style={{ background: '#1a6b3c', color: '#fff' }}>
                <th style={thStyle}>ID</th>
                <th style={thStyle}>Título</th>
                <th style={thStyle}>Descripción</th>
                <th style={thStyle}>Estado</th>
                <th style={thStyle}>Completada</th>
                <th style={thStyle}>Vencimiento</th>
                <th style={thStyle}>Propietario</th>
                <th style={thStyle}>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {tasks.map((task, idx) => (
                <tr key={task.id} style={{ background: idx % 2 === 0 ? '#f9f9f9' : '#fff' }}>
                  {editingId === task.id ? (
                    <>
                      <td style={tdStyle}>{task.id}</td>
                      <td style={tdStyle}>
                        <input
                          style={inputStyle}
                          value={editForm.title || ''}
                          onChange={e => setEditForm({ ...editForm, title: e.target.value })}
                        />
                      </td>
                      <td style={tdStyle}>
                        <input
                          style={inputStyle}
                          value={editForm.description || ''}
                          onChange={e => setEditForm({ ...editForm, description: e.target.value })}
                        />
                      </td>
                      <td style={tdStyle}>
                        <select
                          style={inputStyle}
                          value={editForm.status || 'pending'}
                          onChange={e => setEditForm({ ...editForm, status: e.target.value })}
                        >
                          <option value="pending">Pendiente</option>
                          <option value="in_progress">En progreso</option>
                          <option value="completed">Completada</option>
                        </select>
                      </td>
                      <td style={tdStyle}>
                        <select
                          style={inputStyle}
                          value={editForm.is_completed ? 'true' : 'false'}
                          onChange={e => setEditForm({ ...editForm, is_completed: e.target.value === 'true' })}
                        >
                          <option value="true">Sí</option>
                          <option value="false">No</option>
                        </select>
                      </td>
                      <td style={tdStyle}>
                        <input
                          style={inputStyle}
                          type="date"
                          value={editForm.due_date ? editForm.due_date.substring(0, 10) : ''}
                          onChange={e => setEditForm({ ...editForm, due_date: e.target.value })}
                        />
                      </td>
                      <td style={tdStyle}>{task.owner_id || '-'}</td>
                      <td style={tdStyle}>
                        <button onClick={() => saveEdit(task.id)} style={saveBtnStyle}>Guardar</button>
                        <button onClick={cancelEdit} style={cancelBtnStyle}>Cancelar</button>
                      </td>
                    </>
                  ) : (
                    <>
                      <td style={tdStyle}>{task.id}</td>
                      <td style={tdStyle}>{task.title}</td>
                      <td style={tdStyle}>{task.description ? task.description.substring(0, 50) + (task.description.length > 50 ? '...' : '') : '-'}</td>
                      <td style={tdStyle}>
                        <span style={{
                          color: task.status === 'completed' ? '#28a745' : task.status === 'in_progress' ? '#007bff' : '#b8860b'
                        }}>
                          {task.status || 'pending'}
                        </span>
                      </td>
                      <td style={tdStyle}>
                        <button
                          onClick={() => toggleCompleted(task)}
                          style={{
                            background: task.is_completed ? '#28a745' : '#6c757d',
                            color: '#fff',
                            border: 'none',
                            borderRadius: 4,
                            padding: '0.25rem 0.5rem',
                            cursor: 'pointer',
                            fontSize: '0.8rem',
                          }}
                        >
                          {task.is_completed ? 'Completada' : 'Pendiente'}
                        </button>
                      </td>
                      <td style={tdStyle}>
                        {task.due_date ? new Date(task.due_date).toLocaleDateString() : '-'}
                      </td>
                      <td style={tdStyle}>{task.owner_id || '-'}</td>
                      <td style={tdStyle}>
                        <button onClick={() => startEdit(task)} style={editBtnStyle}>Editar</button>
                        {deleteConfirm === task.id ? (
                          <>
                            <button onClick={() => confirmDelete(task.id)} style={confirmDelBtnStyle}>Confirmar</button>
                            <button onClick={() => setDeleteConfirm(null)} style={cancelBtnStyle}>No</button>
                          </>
                        ) : (
                          <button onClick={() => setDeleteConfirm(task.id)} style={delBtnStyle}>Eliminar</button>
                        )}
                      </td>
                    </>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

const baseBtn = { border: 'none', borderRadius: 4, padding: '0.25rem 0.75rem', cursor: 'pointer', fontSize: '0.8rem' };
const thStyle = { padding: '0.75rem', textAlign: 'left', fontSize: '0.875rem' };
const tdStyle = { padding: '0.5rem 0.75rem', borderBottom: '1px solid #eaeaea', fontSize: '0.875rem' };
const inputStyle = {
  padding: '0.25rem 0.5rem',
  border: '1px solid #ccc',
  borderRadius: 4,
  fontSize: '0.875rem',
  width: '100%',
  boxSizing: 'border-box',
};
const editBtnStyle = { ...baseBtn, background: '#007bff', color: '#fff', marginRight: '0.25rem' };
const delBtnStyle = { ...baseBtn, background: '#dc3545', color: '#fff' };
const confirmDelBtnStyle = { ...baseBtn, background: '#dc3545', color: '#fff', marginRight: '0.25rem' };
const cancelBtnStyle = { ...baseBtn, background: '#6c757d', color: '#fff', marginLeft: '0.25rem' };
const saveBtnStyle = { ...baseBtn, background: '#28a745', color: '#fff' };