import React, { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import {
  getMycrops,
  getCalendars,
  getCalendarDetails,
  createCalendar,
  updateCalendar,
  deleteCalendar,
  activateCalendar,
  advancePhase,
  getCalendarForCrop,
} from '../api/api'
import './Pages.css'

/**
 * Página de calendario agrícola mejorada.
 * Permite crear, editar, activar, avanzar fase y eliminar calendarios.
 */
export function Calendar() {
  const { token } = useAuth()
  const [calendars, setCalendars] = useState([])
  const [myCrops, setMyCrops] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  
  // Modal de creación/edición
  const [showModal, setShowModal] = useState(false)
  const [modalMode, setModalMode] = useState('create') // 'create' o 'edit'
  const [editingCalendar, setEditingCalendar] = useState(null)
  const [formData, setFormData] = useState({
    crop_id: '',
    planting_start: '',
    planting_end: '',
    transplant_start: '',
    transplant_end: '',
    harvest_start: '',
    harvest_end: '',
  })
  const [formError, setFormError] = useState(null)

  // Cargar calendarios y cultivos al montar
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        setError(null)
        
        // Cargar calendarios
        const calsData = await getCalendars(token)
        const calsList = Array.isArray(calsData) ? calsData : (calsData?.items || [])
        
        // Cargar cultivos propios
        const cropsData = await getMycrops(token)
        const cropsList = Array.isArray(cropsData) ? cropsData : (cropsData?.items || [])
        
        setCalendars(calsList)
        setMyCrops(cropsList)
      } catch (err) {
        console.error('Error fetching data:', err)
        setError(`Error: ${err.message}`)
      } finally {
        setLoading(false)
      }
    }

    if (token) {
      fetchData()
    }
  }, [token])

  const handleOpenCreateModal = () => {
    setModalMode('create')
    setFormData({
      crop_id: '',
      planting_start: '',
      planting_end: '',
      transplant_start: '',
      transplant_end: '',
      harvest_start: '',
      harvest_end: '',
    })
    setFormError(null)
    setShowModal(true)
  }

  const handleOpenEditModal = (calendar) => {
    setModalMode('edit')
    setEditingCalendar(calendar)
    setFormData({
      crop_id: calendar.crop_id,
      planting_start: calendar.planting_start || '',
      planting_end: calendar.planting_end || '',
      transplant_start: calendar.transplant_start || '',
      transplant_end: calendar.transplant_end || '',
      harvest_start: calendar.harvest_start || '',
      harvest_end: calendar.harvest_end || '',
    })
    setFormError(null)
    setShowModal(true)
  }

  const handleCloseModal = () => {
    setShowModal(false)
    setEditingCalendar(null)
    setFormError(null)
  }

  const handleSaveCalendar = async (e) => {
    e.preventDefault()
    try {
      setFormError(null)

      if (modalMode === 'create') {
        if (!formData.crop_id) {
          setFormError('Debes seleccionar un cultivo')
          return
        }

        // Crear calendario - convertir crop_id a número
        const calendarPayload = {
          crop_id: parseInt(formData.crop_id, 10),
          planting_start: formData.planting_start || null,
          planting_end: formData.planting_end || null,
          transplant_start: formData.transplant_start || null,
          transplant_end: formData.transplant_end || null,
          harvest_start: formData.harvest_start || null,
          harvest_end: formData.harvest_end || null,
        }
        const newCalendar = await createCalendar(calendarPayload, token)
        setCalendars([...calendars, newCalendar])
        setSuccess('Calendario creado exitosamente')
      } else if (modalMode === 'edit') {
        // Actualizar calendario - no incluir crop_id
        const updatePayload = {
          planting_start: formData.planting_start || null,
          planting_end: formData.planting_end || null,
          transplant_start: formData.transplant_start || null,
          transplant_end: formData.transplant_end || null,
          harvest_start: formData.harvest_start || null,
          harvest_end: formData.harvest_end || null,
        }
        const updated = await updateCalendar(editingCalendar.id, updatePayload, token)
        setCalendars(calendars.map(c => c.id === editingCalendar.id ? updated : c))
        setSuccess('Calendario actualizado exitosamente')
      }

      handleCloseModal()
      setTimeout(() => setSuccess(null), 3000)
    } catch (err) {
      console.error('Error saving calendar:', err)
      // Mostrar el detail específico del error si está disponible
      const errorMessage = err.data?.detail || err.message || 'Error desconocido'
      setFormError(`Error: ${errorMessage}`)
    }
  }

  const handleActivate = async (calendarId) => {
    try {
      setError(null)
      const updated = await activateCalendar(calendarId, token)
      setCalendars(calendars.map(c => c.id === calendarId ? updated : c))
      setSuccess('Calendario activado exitosamente')
      setTimeout(() => setSuccess(null), 3000)
    } catch (err) {
      console.error('Error activating calendar:', err)
      setError(`Error al activar: ${err.message}`)
    }
  }

  const handleAdvancePhase = async (calendarId) => {
    try {
      setError(null)
      const updated = await advancePhase(calendarId, token)
      setCalendars(calendars.map(c => c.id === calendarId ? updated : c))
      setSuccess('Fase avanzada exitosamente')
      setTimeout(() => setSuccess(null), 3000)
    } catch (err) {
      console.error('Error advancing phase:', err)
      setError(`Error al avanzar fase: ${err.message}`)
    }
  }

  const handleDelete = async (calendarId) => {
    if (!window.confirm('¿Eliminar este calendario?')) return

    try {
      setError(null)
      await deleteCalendar(calendarId, token)
      setCalendars(calendars.filter(c => c.id !== calendarId))
      setSuccess('Calendario eliminado exitosamente')
      setTimeout(() => setSuccess(null), 3000)
    } catch (err) {
      console.error('Error deleting calendar:', err)
      setError(`Error al eliminar: ${err.message}`)
    }
  }

  const getCropName = (cropId) => {
    const crop = myCrops.find(c => c.id === cropId)
    return crop ? crop.name : `Cultivo #${cropId}`
  }

  const getPhaseNameByIndex = (index) => {
    const phases = ['Siembra', 'Trasplante', 'Cosecha']
    return phases[index] || 'Desconocida'
  }

  const formatDate = (dateStr) => {
    if (!dateStr) return '-'
    try {
      const date = new Date(dateStr)
      return date.toLocaleDateString('es-ES')
    } catch {
      return dateStr
    }
  }

  if (loading) return <div className="loading">Cargando calendario...</div>
  if (error && !calendars.length) return <div className="error">Error: {error}</div>

  const activeCalendars = calendars.filter(c => c.status === 'active')
  const draftCalendars = calendars.filter(c => c.status === 'draft')
  const completedCalendars = calendars.filter(c => c.status === 'completed')

  return (
    <div className="calendar-page">
      <h1>📅 Calendario Agrícola</h1>

      {success && <div className="success-message">{success}</div>}
      {error && <div className="error">{error}</div>}

      <div style={{ marginBottom: '2rem' }}>
        <button onClick={handleOpenCreateModal} className="primary-btn">
          + Crear Calendario
        </button>
      </div>

      {/* Modal de creación/edición */}
      {showModal && (
        <div className="modal-overlay">
          <div className="modal">
            <h2>{modalMode === 'create' ? 'Crear Calendario' : 'Editar Calendario'}</h2>
            {formError && <div className="error" style={{ marginBottom: '1rem' }}>{formError}</div>}
            
            <form onSubmit={handleSaveCalendar}>
              <div className="form-group">
                <label>Cultivo</label>
                <select
                  value={formData.crop_id}
                  onChange={(e) => setFormData({ ...formData, crop_id: e.target.value })}
                  disabled={modalMode === 'edit'}
                >
                  <option value="">Selecciona un cultivo</option>
                  {myCrops.map(crop => (
                    <option key={crop.id} value={crop.id}>{crop.name}</option>
                  ))}
                </select>
              </div>

              <fieldset>
                <legend>Fechas de Siembra</legend>
                <div className="form-row">
                  <div className="form-group">
                    <label>Inicio</label>
                    <input
                      type="date"
                      value={formData.planting_start}
                      onChange={(e) => setFormData({ ...formData, planting_start: e.target.value })}
                    />
                  </div>
                  <div className="form-group">
                    <label>Fin</label>
                    <input
                      type="date"
                      value={formData.planting_end}
                      onChange={(e) => setFormData({ ...formData, planting_end: e.target.value })}
                    />
                  </div>
                </div>
              </fieldset>

              <fieldset>
                <legend>Fechas de Trasplante</legend>
                <div className="form-row">
                  <div className="form-group">
                    <label>Inicio</label>
                    <input
                      type="date"
                      value={formData.transplant_start}
                      onChange={(e) => setFormData({ ...formData, transplant_start: e.target.value })}
                    />
                  </div>
                  <div className="form-group">
                    <label>Fin</label>
                    <input
                      type="date"
                      value={formData.transplant_end}
                      onChange={(e) => setFormData({ ...formData, transplant_end: e.target.value })}
                    />
                  </div>
                </div>
              </fieldset>

              <fieldset>
                <legend>Fechas de Cosecha</legend>
                <div className="form-row">
                  <div className="form-group">
                    <label>Inicio</label>
                    <input
                      type="date"
                      value={formData.harvest_start}
                      onChange={(e) => setFormData({ ...formData, harvest_start: e.target.value })}
                    />
                  </div>
                  <div className="form-group">
                    <label>Fin</label>
                    <input
                      type="date"
                      value={formData.harvest_end}
                      onChange={(e) => setFormData({ ...formData, harvest_end: e.target.value })}
                    />
                  </div>
                </div>
              </fieldset>

              <div className="modal-buttons">
                <button type="submit" className="btn-save">Guardar</button>
                <button type="button" className="btn-cancel" onClick={handleCloseModal}>Cancelar</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Calendarios Activos */}
      {activeCalendars.length > 0 && (
        <section className="calendar-section">
          <h2>📍 Calendarios Activos ({activeCalendars.length})</h2>
          <div className="calendars-list">
            {activeCalendars.map((cal) => (
              <div key={cal.id} className="calendar-card active">
                <div className="calendar-header">
                  <h3>{getCropName(cal.crop_id)}</h3>
                  <span className="status-badge active">Activo</span>
                </div>
                
                <div className="calendar-details">
                  <p><strong>Fase Actual:</strong> {getPhaseNameByIndex(cal.current_phase_index)}</p>
                  <p><strong>Estado:</strong> {cal.status.toUpperCase()}</p>
                  
                  {cal.planting_start && (
                    <div className="phase-info">
                      <h4>🌱 Siembra</h4>
                      <p>{formatDate(cal.planting_start)} - {formatDate(cal.planting_end)}</p>
                    </div>
                  )}
                  
                  {cal.transplant_start && (
                    <div className="phase-info">
                      <h4>🌿 Trasplante</h4>
                      <p>{formatDate(cal.transplant_start)} - {formatDate(cal.transplant_end)}</p>
                    </div>
                  )}
                  
                  {cal.harvest_start && (
                    <div className="phase-info">
                      <h4>🌾 Cosecha</h4>
                      <p>{formatDate(cal.harvest_start)} - {formatDate(cal.harvest_end)}</p>
                    </div>
                  )}
                </div>

                <div className="calendar-actions">
                  <button onClick={() => handleOpenEditModal(cal)} className="btn-edit" title="Editar">
                    ✏️ Editar
                  </button>
                  <button onClick={() => handleAdvancePhase(cal.id)} className="btn-advance" title="Avanzar fase">
                    ⏭️ Avanzar
                  </button>
                  <button onClick={() => handleDelete(cal.id)} className="btn-delete" title="Eliminar">
                    🗑️ Eliminar
                  </button>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Calendarios en Borrador */}
      {draftCalendars.length > 0 && (
        <section className="calendar-section">
          <h2>📝 Calendarios en Borrador ({draftCalendars.length})</h2>
          <div className="calendars-list">
            {draftCalendars.map((cal) => (
              <div key={cal.id} className="calendar-card draft">
                <div className="calendar-header">
                  <h3>{getCropName(cal.crop_id)}</h3>
                  <span className="status-badge draft">Borrador</span>
                </div>
                
                <div className="calendar-details">
                  <p><strong>Estado:</strong> {cal.status.toUpperCase()}</p>
                  
                  {cal.planting_start && (
                    <div className="phase-info">
                      <h4>🌱 Siembra</h4>
                      <p>{formatDate(cal.planting_start)} - {formatDate(cal.planting_end)}</p>
                    </div>
                  )}
                  
                  {cal.transplant_start && (
                    <div className="phase-info">
                      <h4>🌿 Trasplante</h4>
                      <p>{formatDate(cal.transplant_start)} - {formatDate(cal.transplant_end)}</p>
                    </div>
                  )}
                  
                  {cal.harvest_start && (
                    <div className="phase-info">
                      <h4>🌾 Cosecha</h4>
                      <p>{formatDate(cal.harvest_start)} - {formatDate(cal.harvest_end)}</p>
                    </div>
                  )}
                </div>

                <div className="calendar-actions">
                  <button onClick={() => handleOpenEditModal(cal)} className="btn-edit" title="Editar">
                    ✏️ Editar
                  </button>
                  <button onClick={() => handleActivate(cal.id)} className="btn-activate" title="Activar">
                    ▶️ Activar
                  </button>
                  <button onClick={() => handleDelete(cal.id)} className="btn-delete" title="Eliminar">
                    🗑️ Eliminar
                  </button>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Calendarios Completados */}
      {completedCalendars.length > 0 && (
        <section className="calendar-section">
          <h2>✅ Calendarios Completados ({completedCalendars.length})</h2>
          <div className="calendars-list">
            {completedCalendars.map((cal) => (
              <div key={cal.id} className="calendar-card completed">
                <div className="calendar-header">
                  <h3>{getCropName(cal.crop_id)}</h3>
                  <span className="status-badge completed">Completado</span>
                </div>
                
                <div className="calendar-details">
                  <p><strong>Última Fase:</strong> {getPhaseNameByIndex(cal.current_phase_index)}</p>
                  <p><strong>Estado:</strong> {cal.status.toUpperCase()}</p>
                  
                  {cal.harvest_start && (
                    <div className="phase-info">
                      <h4>🌾 Cosecha</h4>
                      <p>{formatDate(cal.harvest_start)} - {formatDate(cal.harvest_end)}</p>
                    </div>
                  )}
                </div>

                <div className="calendar-actions">
                  <button onClick={() => handleDelete(cal.id)} className="btn-delete" title="Eliminar">
                    🗑️ Eliminar
                  </button>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {calendars.length === 0 && (
        <div style={{ textAlign: 'center', padding: '2rem' }}>
          <p style={{ fontSize: '1.1rem', color: '#666', marginBottom: '1rem' }}>
            No tienes calendarios registrados.
          </p>
          <p style={{ color: '#999', marginBottom: '1.5rem' }}>
            Crea un calendario para rastrear el ciclo agrícola de tus cultivos.
          </p>
          <button onClick={handleOpenCreateModal} className="primary-btn">
            + Crear Primer Calendario
          </button>
        </div>
      )}
    </div>
  )
}
