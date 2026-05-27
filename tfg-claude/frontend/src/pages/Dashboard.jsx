import React, { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import {
  getDashboardSummary,
} from '../api/api'
import './Pages.css'

/**
 * Página de dashboard del usuario.
 */
export function Dashboard() {
  const { token } = useAuth()
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await getDashboardSummary(token)
        setSummary(data)
        setError(null)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [token])

  if (loading) return <div className="loading">Cargando dashboard...</div>
  if (error) return <div className="error">Error: {error}</div>
  if (!summary) return <div className="error">No se pudo cargar el dashboard</div>

  return (
    <div className="dashboard">
      <h1>Dashboard</h1>

      <div className="summary-grid">
        <div className="summary-card">
          <h3>Cultivos Personales</h3>
          <p className="big-number">{summary.total_personal_crops || 0}</p>
        </div>

        <div className="summary-card">
          <h3>Tareas Pendientes</h3>
          <p className="big-number">{summary.total_tasks_pending || 0}</p>
        </div>

        <div className="summary-card">
          <h3>Tareas Completadas</h3>
          <p className="big-number">{summary.total_tasks_completed || 0}</p>
        </div>

        <div className="summary-card">
          <h3>Calendarios Activos</h3>
          <p className="big-number">{summary.total_active_calendars || 0}</p>
        </div>

        <div className="summary-card">
          <h3>Cultivos Públicos Disponibles</h3>
          <p className="big-number">{summary.total_public_crops_available || 0}</p>
        </div>
      </div>

      {summary.upcoming_tasks && summary.upcoming_tasks.length > 0 && (
        <section className="dashboard-section">
          <h2>Próximas Tareas</h2>
          <ul className="task-list">
            {summary.upcoming_tasks.slice(0, 5).map((task) => (
              <li key={task.id} className="task-item">
                <strong>{task.title}</strong>
                <span className="due-date">
                  {task.due_date ? new Date(task.due_date).toLocaleDateString('es-ES') : 'Sin fecha'}
                </span>
              </li>
            ))}
          </ul>
        </section>
      )}

      {summary.active_calendar_phases && summary.active_calendar_phases.length > 0 && (
        <section className="dashboard-section">
          <h2>Fases de Calendario Activas</h2>
          <ul className="phase-list">
            {summary.active_calendar_phases.slice(0, 5).map((phase) => (
              <li key={phase.calendar_id} className="phase-item">
                <strong>{phase.crop_name}</strong>
                <span className="phase-name">Fase: {phase.current_phase}</span>
                <span className="phase-status">Estado: {phase.status}</span>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  )
}
