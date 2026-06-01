import React, { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { getAdminTasks, updateAdminTask, deleteAdminTask } from '../api/api'
import './AdminPages.css'

/**
 * Página de gestión de tareas (admin).
 */
export function AdminTasks() {
  const { token } = useAuth()
  const [tasks, setTasks] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [editingId, setEditingId] = useState(null)
  const [editData, setEditData] = useState({})

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        const data = await getAdminTasks(token)
        setTasks(data || [])
        setError(null)
      } catch (err) {
        console.error('Error fetching admin tasks:', err)
        setError(err.message)
        setTasks([])
      } finally {
        setLoading(false)
      }
    }

    fetchTasks()
  }, [token])

  const handleEdit = (task) => {
    setEditingId(task.id)
    setEditData({ ...task })
  }

  const handleCancelEdit = () => {
    setEditingId(null)
    setEditData({})
  }

  const handleSaveEdit = async (taskId) => {
    try {
      const updatePayload = {
        title: editData.title,
        description: editData.description,
        status: editData.status,
        due_date: editData.due_date,
      }
      await updateAdminTask(taskId, updatePayload, token)
      
      // Actualizar lista
      setTasks(tasks.map(t => t.id === taskId ? { ...t, ...updatePayload } : t))
      setEditingId(null)
      setEditData({})
    } catch (err) {
      console.error('Error updating task:', err)
      alert(`Error: ${err.message}`)
    }
  }

  const handleDelete = async (taskId) => {
    if (!window.confirm('¿Eliminar esta tarea?')) return

    try {
      await deleteAdminTask(taskId, token)
      setTasks(tasks.filter(t => t.id !== taskId))
    } catch (err) {
      console.error('Error deleting task:', err)
      alert(`Error: ${err.message}`)
    }
  }

  if (loading) return <div className="loading">Cargando tareas...</div>
  if (error) return <div className="error">Error: {error}</div>

  return (
    <div className="admin-page">
      <h1>✅ Gestión de Tareas</h1>

      {tasks.length === 0 ? (
        <p className="empty">No hay tareas</p>
      ) : (
        <table className="admin-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Título</th>
              <th>Estado</th>
              <th>Fecha Vencimiento</th>
              <th>Descripción</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {tasks.map((task) => (
              <tr key={task.id} className={editingId === task.id ? 'editing' : ''}>
                <td>{task.id}</td>
                <td>
                  {editingId === task.id ? (
                    <input
                      type="text"
                      value={editData.title || ''}
                      onChange={(e) => setEditData({ ...editData, title: e.target.value })}
                    />
                  ) : (
                    task.title
                  )}
                </td>
                <td>
                  {editingId === task.id ? (
                    <select
                      value={editData.status || 'pending'}
                      onChange={(e) => setEditData({ ...editData, status: e.target.value })}
                    >
                      <option value="pending">pending</option>
                      <option value="completed">completed</option>
                    </select>
                  ) : (
                    task.status
                  )}
                </td>
                <td>
                  {editingId === task.id ? (
                    <input
                      type="date"
                      value={editData.due_date || ''}
                      onChange={(e) => setEditData({ ...editData, due_date: e.target.value })}
                    />
                  ) : (
                    task.due_date ? new Date(task.due_date).toLocaleDateString('es-ES') : '-'
                  )}
                </td>
                <td>
                  {editingId === task.id ? (
                    <textarea
                      value={editData.description || ''}
                      onChange={(e) => setEditData({ ...editData, description: e.target.value })}
                      style={{ maxWidth: '200px' }}
                    />
                  ) : (
                    (task.description || '').substring(0, 50)
                  )}
                </td>
                <td className="actions">
                  {editingId === task.id ? (
                    <>
                      <button
                        className="btn-save"
                        onClick={() => handleSaveEdit(task.id)}
                      >
                        Guardar
                      </button>
                      <button
                        className="btn-cancel"
                        onClick={handleCancelEdit}
                      >
                        Cancelar
                      </button>
                    </>
                  ) : (
                    <>
                      <button
                        className="btn-edit"
                        onClick={() => handleEdit(task)}
                      >
                        Editar
                      </button>
                      <button
                        className="btn-delete"
                        onClick={() => handleDelete(task.id)}
                      >
                        Eliminar
                      </button>
                    </>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
