import React, { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { getAdminSummary } from '../api/api'
import './Pages.css'

/**
 * Página de dashboard admin.
 * Muestra resumen global del sistema.
 */
export function AdminDashboard() {
  const { token } = useAuth()
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await getAdminSummary(token)
        setSummary(data)
        setError(null)
      } catch (err) {
        console.error('Error fetching admin summary:', err)
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [token])

  if (loading) return <div className="loading">Cargando dashboard admin...</div>
  if (error) return <div className="error">Error: {error}</div>
  if (!summary) return <div className="error">No se pudo cargar el resumen</div>

  return (
    <div className="admin-dashboard">
      <h1>🔧 Panel Admin</h1>

      <div className="summary-grid">
        <div className="summary-card">
          <h3>Usuarios Totales</h3>
          <p className="big-number">{summary.total_users || 0}</p>
        </div>

        <div className="summary-card">
          <h3>Cultivos Globales</h3>
          <p className="big-number">{summary.total_crops || 0}</p>
        </div>

        <div className="summary-card">
          <h3>Cultivos Públicos</h3>
          <p className="big-number">{summary.total_public_crops || 0}</p>
        </div>

        <div className="summary-card">
          <h3>Tareas Globales</h3>
          <p className="big-number">{summary.total_tasks || 0}</p>
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
          <h3>Calendarios Completados</h3>
          <p className="big-number">{summary.total_completed_calendars || 0}</p>
        </div>
      </div>

      <div className="admin-links">
        <a href="/admin/users" className="admin-link">
          👥 Gestionar Usuarios
        </a>
        <a href="/admin/crops" className="admin-link">
          🌾 Gestionar Cultivos
        </a>
        <a href="/admin/tasks" className="admin-link">
          ✅ Gestionar Tareas
        </a>
      </div>
    </div>
  )
}
