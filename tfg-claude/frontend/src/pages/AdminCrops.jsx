import React, { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { getAdminCrops, updateAdminCrop, deleteAdminCrop } from '../api/api'
import './AdminPages.css'

/**
 * Página de gestión de cultivos (admin).
 */
export function AdminCrops() {
  const { token } = useAuth()
  const [crops, setCrops] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [editingId, setEditingId] = useState(null)
  const [editData, setEditData] = useState({})

  useEffect(() => {
    const fetchCrops = async () => {
      try {
        const data = await getAdminCrops(token)
        setCrops(data || [])
        setError(null)
      } catch (err) {
        console.error('Error fetching admin crops:', err)
        setError(err.message)
        setCrops([])
      } finally {
        setLoading(false)
      }
    }

    fetchCrops()
  }, [token])

  const handleEdit = (crop) => {
    setEditingId(crop.id)
    setEditData({ ...crop })
  }

  const handleCancelEdit = () => {
    setEditingId(null)
    setEditData({})
  }

  const handleSaveEdit = async (cropId) => {
    try {
      const updatePayload = {
        name: editData.name,
        description: editData.description,
        crop_type: editData.crop_type,
        is_public: editData.is_public,
      }
      await updateAdminCrop(cropId, updatePayload, token)
      
      // Actualizar lista
      setCrops(crops.map(c => c.id === cropId ? { ...c, ...updatePayload } : c))
      setEditingId(null)
      setEditData({})
    } catch (err) {
      console.error('Error updating crop:', err)
      alert(`Error: ${err.message}`)
    }
  }

  const handleDelete = async (cropId) => {
    if (!window.confirm('¿Eliminar este cultivo?')) return

    try {
      await deleteAdminCrop(cropId, token)
      setCrops(crops.filter(c => c.id !== cropId))
    } catch (err) {
      console.error('Error deleting crop:', err)
      alert(`Error: ${err.message}`)
    }
  }

  if (loading) return <div className="loading">Cargando cultivos...</div>
  if (error) return <div className="error">Error: {error}</div>

  return (
    <div className="admin-page">
      <h1>🌾 Gestión de Cultivos</h1>

      {crops.length === 0 ? (
        <p className="empty">No hay cultivos</p>
      ) : (
        <table className="admin-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Nombre</th>
              <th>Tipo</th>
              <th>Público</th>
              <th>Descripción</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {crops.map((crop) => (
              <tr key={crop.id} className={editingId === crop.id ? 'editing' : ''}>
                <td>{crop.id}</td>
                <td>
                  {editingId === crop.id ? (
                    <input
                      type="text"
                      value={editData.name || ''}
                      onChange={(e) => setEditData({ ...editData, name: e.target.value })}
                    />
                  ) : (
                    crop.name
                  )}
                </td>
                <td>
                  {editingId === crop.id ? (
                    <input
                      type="text"
                      value={editData.crop_type || ''}
                      onChange={(e) => setEditData({ ...editData, crop_type: e.target.value })}
                    />
                  ) : (
                    crop.crop_type
                  )}
                </td>
                <td>
                  {editingId === crop.id ? (
                    <input
                      type="checkbox"
                      checked={editData.is_public || false}
                      onChange={(e) => setEditData({ ...editData, is_public: e.target.checked })}
                    />
                  ) : (
                    crop.is_public ? '✓' : '✗'
                  )}
                </td>
                <td>
                  {editingId === crop.id ? (
                    <textarea
                      value={editData.description || ''}
                      onChange={(e) => setEditData({ ...editData, description: e.target.value })}
                      style={{ maxWidth: '200px' }}
                    />
                  ) : (
                    (crop.description || '').substring(0, 50)
                  )}
                </td>
                <td className="actions">
                  {editingId === crop.id ? (
                    <>
                      <button
                        className="btn-save"
                        onClick={() => handleSaveEdit(crop.id)}
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
                        onClick={() => handleEdit(crop)}
                      >
                        Editar
                      </button>
                      <button
                        className="btn-delete"
                        onClick={() => handleDelete(crop.id)}
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
