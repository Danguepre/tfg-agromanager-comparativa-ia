import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { getMycrops, getPublishedcrops, addCropToMyCrops } from '../api/api'
import './Pages.css'

/**
 * Página de gestión de cultivos propios y catálogo.
 */
export function Crops() {
  const { token } = useAuth()
  const [myCrops, setMyCrops] = useState([])
  const [published, setPublished] = useState([])
  const [activeTab, setActiveTab] = useState('mine')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    const fetchCrops = async () => {
      try {
        setLoading(true)
        const [my, pub] = await Promise.all([
          getMycrops(token),
          getPublishedcrops(token),
        ])
        // La normalización ya ocurre en api.js, pero hacemos defensive
        const safeMycrops = Array.isArray(my) ? my : []
        const safePublished = Array.isArray(pub) ? pub : []
        
        setMyCrops(safeMycrops)
        setPublished(safePublished)
        setError(null)
      } catch (err) {
        console.error('Error fetching crops:', err)
        setError(`Error al cargar cultivos: ${err.message}`)
      } finally {
        setLoading(false)
      }
    }

    if (token) {
      fetchCrops()
    }
  }, [token])

  const handleAddCrop = async (cropId) => {
    try {
      await addCropToMyCrops(cropId, token)
      // Recargar cultivos propios
      const updated = await getMycrops(token)
      const safeUpdated = Array.isArray(updated) ? updated : []
      setMyCrops(safeUpdated)
    } catch (err) {
      console.error('Error adding crop:', err)
      alert(`Error al añadir cultivo: ${err.message}`)
    }
  }

  // Asegurar que published es un array antes de filter
  const safePublished = Array.isArray(published) ? published : []
  const filteredPublished = safePublished.filter(
    (crop) =>
      crop.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      crop.crop_type?.toLowerCase().includes(searchTerm.toLowerCase())
  )

  if (loading) return <div className="loading">Cargando cultivos...</div>
  if (error) return <div className="error">Error: {error}</div>

  return (
    <div className="crops-page">
      <h1>Cultivos</h1>

      <div className="tabs">
        <button
          className={`tab ${activeTab === 'mine' ? 'active' : ''}`}
          onClick={() => setActiveTab('mine')}
        >
          Mis Cultivos ({myCrops.length})
        </button>
        <button
          className={`tab ${activeTab === 'catalog' ? 'active' : ''}`}
          onClick={() => setActiveTab('catalog')}
        >
          Catálogo Público ({published.length})
        </button>
      </div>

      {activeTab === 'mine' ? (
        <div className="crops-section">
          {myCrops.length === 0 ? (
            <p>No tienes cultivos aún. Añade algunos del catálogo.</p>
          ) : (
            <div className="crops-grid">
              {myCrops.map((crop) => (
                <Link
                  key={crop.id}
                  to={`/crops/${crop.id}`}
                  className="crop-card"
                >
                  <h3>{crop.name}</h3>
                  <p className="crop-type">{crop.crop_type}</p>
                  {crop.description && <p>{crop.description}</p>}
                </Link>
              ))}
            </div>
          )}
        </div>
      ) : (
        <div className="crops-section">
          <input
            type="text"
            placeholder="Buscar por nombre o tipo..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />

          {filteredPublished.length === 0 ? (
            <p>No se encontraron cultivos en el catálogo.</p>
          ) : (
            <div className="crops-grid">
              {filteredPublished.map((crop) => (
                <div key={crop.id} className="catalog-crop-card">
                  <div className="crop-info">
                    <h3>{crop.name}</h3>
                    <p className="crop-type">{crop.crop_type}</p>
                    {crop.description && <p>{crop.description}</p>}
                  </div>
                  <button
                    className="add-crop-btn"
                    onClick={(e) => {
                      e.preventDefault()
                      handleAddCrop(crop.id)
                    }}
                  >
                    + Añadir a Mis Cultivos
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
