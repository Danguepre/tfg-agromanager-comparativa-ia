import React, { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { getTasks, createTask, updateTask, deleteTask } from '../api/api'
import './Pages.css'

/**
 * Página de tareas del usuario.
 */
export function Tasks() {
  const { token } = useAuth()
  const [tasks, setTasks] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [newTaskTitle, setNewTaskTitle] = useState('')
  const [newTaskDescription, setNewTaskDescription] = useState('')
  const [newTaskDueDate, setNewTaskDueDate] = useState('')

  useEffect(() => {
    fetchTasks()
  }, [token])

  const fetchTasks = async () => {
    try {
      setLoading(true)
      const data = await getTasks(token)
      setTasks(Array.isArray(data) ? data : data.tasks || [])
      setError(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleAddTask = async (e) => {
    e.preventDefault()
    if (!newTaskTitle.trim()) return

    try {
      await createTask(
        {
          title: newTaskTitle,
          description: newTaskDescription || null,
          due_date: newTaskDueDate || null,
        },
        token
      )
      setNewTaskTitle('')
      setNewTaskDescription('')
      setNewTaskDueDate('')
      fetchTasks()
    } catch (err) {
      alert(`Error al crear tarea: ${err.message}`)
    }
  }

  const handleCompleteTask = async (taskId, currentStatus) => {
    try {
      const newStatus = currentStatus === 'pending' ? 'completed' : 'pending'
      await updateTask(taskId, { status: newStatus }, token)
      fetchTasks()
    } catch (err) {
      alert(`Error al actualizar tarea: ${err.message}`)
    }
  }

  const handleDeleteTask = async (taskId) => {
    if (!window.confirm('¿Estás seguro de que deseas eliminar esta tarea?')) return

    try {
      await deleteTask(taskId, token)
      fetchTasks()
    } catch (err) {
      alert(`Error al eliminar tarea: ${err.message}`)
    }
  }

  if (loading) return <div className="loading">Cargando tareas...</div>
  if (error) return <div className="error">Error: {error}</div>

  const pendingTasks = tasks.filter((t) => t.status === 'pending')
  const completedTasks = tasks.filter((t) => t.status === 'completed')

  return (
    <div className="tasks-page">
      <h1>Tareas</h1>

      <section className="new-task-section">
        <h2>Crear Nueva Tarea</h2>
        <form onSubmit={handleAddTask} className="new-task-form">
          <div className="form-group">
            <input
              type="text"
              placeholder="Título de la tarea"
              value={newTaskTitle}
              onChange={(e) => setNewTaskTitle(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <textarea
              placeholder="Descripción (opcional)"
              value={newTaskDescription}
              onChange={(e) => setNewTaskDescription(e.target.value)}
              rows="2"
            />
          </div>

          <div className="form-group">
            <input
              type="date"
              value={newTaskDueDate}
              onChange={(e) => setNewTaskDueDate(e.target.value)}
            />
          </div>

          <button type="submit" className="primary-btn">
            Crear Tarea
          </button>
        </form>
      </section>

      <section className="tasks-section">
        <h2>Tareas Pendientes ({pendingTasks.length})</h2>
        {pendingTasks.length === 0 ? (
          <p>No tienes tareas pendientes.</p>
        ) : (
          <div className="tasks-list">
            {pendingTasks.map((task) => (
              <div key={task.id} className="task-card">
                <div className="task-content">
                  <h3>{task.title}</h3>
                  {task.description && <p>{task.description}</p>}
                  {task.due_date && (
                    <p className="due-date">
                      Vencimiento: {new Date(task.due_date).toLocaleDateString('es-ES')}
                    </p>
                  )}
                </div>
                <div className="task-actions">
                  <button
                    className="complete-btn"
                    onClick={() => handleCompleteTask(task.id, task.status)}
                  >
                    ✓ Completar
                  </button>
                  <button
                    className="delete-btn"
                    onClick={() => handleDeleteTask(task.id)}
                  >
                    🗑 Eliminar
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {completedTasks.length > 0 && (
        <section className="tasks-section">
          <h2>Tareas Completadas ({completedTasks.length})</h2>
          <div className="tasks-list">
            {completedTasks.map((task) => (
              <div key={task.id} className="task-card completed">
                <div className="task-content">
                  <h3 className="completed-title">{task.title}</h3>
                  {task.description && <p>{task.description}</p>}
                </div>
                <div className="task-actions">
                  <button
                    className="reopen-btn"
                    onClick={() => handleCompleteTask(task.id, task.status)}
                  >
                    ↻ Reabrir
                  </button>
                  <button
                    className="delete-btn"
                    onClick={() => handleDeleteTask(task.id)}
                  >
                    🗑 Eliminar
                  </button>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  )
}
