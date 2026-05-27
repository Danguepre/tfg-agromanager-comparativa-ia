import React, { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { getDashboardCalendars } from '../api/api'
import './Pages.css'

/**
 * Página de calendario agrícola.
 */
export function Calendar() {
  const { token } = useAuth()
  const [calendars, setCalendars] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchCalendars = async () => {
      try {
        const data = await getDashboardCalendars(token)
        setCalendars(data)
        setError(null)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchCalendars()
  }, [token])

  if (loading) return <div className="loading">Cargando calendarios...</div>
  if (error) return <div className="error">Error: {error}</div>
  if (!calendars) return <div className="error">No se pudo cargar el calendario</div>

  const activeCalendars = calendars.active_calendars || []
  const completedCalendars = calendars.completed_calendars || []

  return (
    <div className="calendar-page">
      <h1>Calendario Agrícola</h1>

      {activeCalendars.length > 0 && (
        <section className="calendar-section">
          <h2>Calendarios Activos</h2>
          <div className="calendars-list">
            {activeCalendars.map((cal) => (
              <div key={cal.id} className="calendar-card">
                <h3>{cal.crop_name}</h3>
                <p className="calendar-status">Estado: {cal.status}</p>
                {cal.current_phase && (
                  <p className="calendar-phase">Fase Actual: {cal.current_phase}</p>
                )}
                {cal.phase_index !== undefined && (
                  <p className="calendar-phase-index">Índice de Fase: {cal.phase_index}</p>
                )}
              </div>
            ))}
          </div>
        </section>
      )}

      {completedCalendars.length > 0 && (
        <section className="calendar-section">
          <h2>Calendarios Completados</h2>
          <div className="calendars-list">
            {completedCalendars.map((cal) => (
              <div key={cal.id} className="calendar-card completed">
                <h3>{cal.crop_name}</h3>
                <p className="calendar-status">Estado: {cal.status}</p>
                {cal.current_phase && (
                  <p className="calendar-phase">Fase Final: {cal.current_phase}</p>
                )}
              </div>
            ))}
          </div>
        </section>
      )}

      {activeCalendars.length === 0 && completedCalendars.length === 0 && (
        <p>No tienes calendarios registrados.</p>
      )}
    </div>
  )
}
