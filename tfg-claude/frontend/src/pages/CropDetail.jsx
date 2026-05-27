import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { getCropDetails } from '../api/api'
import './Pages.css'

/**
 * Página de detalles de un cultivo específico.
 */
export function CropDetail() {
  const { id } = useParams()
  const { token } = useAuth()
  const navigate = useNavigate()
  const [crop, setCrop] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchCrop = async () => {
      try {
        const data = await getCropDetails(id, token)
        setCrop(data)
        setError(null)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchCrop()
  }, [id, token])

  if (loading) return <div className="loading">Cargando cultivo...</div>
  if (error) return <div className="error">Error: {error}</div>
  if (!crop) return <div className="error">Cultivo no encontrado</div>

  return (
    <div className="crop-detail">
      <button className="back-btn" onClick={() => navigate('/crops')}>
        ← Volver a Cultivos
      </button>

      <h1>{crop.name}</h1>
      <p className="crop-type">{crop.crop_type}</p>

      {crop.description && (
        <section className="detail-section">
          <h2>Descripción</h2>
          <p>{crop.description}</p>
        </section>
      )}

      {crop.is_public && (
        <div className="badge">Cultivo Público</div>
      )}

      <section className="detail-section">
        <h2>Información Básica</h2>
        <dl>
          {crop.created_at && (
            <>
              <dt>Creado:</dt>
              <dd>{new Date(crop.created_at).toLocaleDateString('es-ES')}</dd>
            </>
          )}
          {crop.updated_at && (
            <>
              <dt>Actualizado:</dt>
              <dd>{new Date(crop.updated_at).toLocaleDateString('es-ES')}</dd>
            </>
          )}
        </dl>
      </section>

      <section className="detail-section">
        <p className="info-text">
          Para ver detalles de riego y requisitos ambientales, consulta el
          dashboard o la sección correspondiente.
        </p>
      </section>
    </div>
  )
}
