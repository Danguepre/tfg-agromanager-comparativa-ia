import React, { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { getAdminUsers, updateAdminUser, deleteAdminUser } from '../api/api'
import './AdminPages.css'

/**
 * Página de gestión de usuarios (admin).
 */
export function AdminUsers() {
  const { token } = useAuth()
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [editingId, setEditingId] = useState(null)
  const [editData, setEditData] = useState({})

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const data = await getAdminUsers(token)
        setUsers(data || [])
        setError(null)
      } catch (err) {
        console.error('Error fetching admin users:', err)
        setError(err.message)
        setUsers([])
      } finally {
        setLoading(false)
      }
    }

    fetchUsers()
  }, [token])

  const handleEdit = (user) => {
    setEditingId(user.id)
    setEditData({ ...user })
  }

  const handleCancelEdit = () => {
    setEditingId(null)
    setEditData({})
  }

  const handleSaveEdit = async (userId) => {
    try {
      const updatePayload = {
        name: editData.name,
        email: editData.email,
        role: editData.role,
        is_active: editData.is_active,
      }
      await updateAdminUser(userId, updatePayload, token)
      
      // Actualizar lista
      setUsers(users.map(u => u.id === userId ? { ...u, ...updatePayload } : u))
      setEditingId(null)
      setEditData({})
    } catch (err) {
      console.error('Error updating user:', err)
      alert(`Error: ${err.message}`)
    }
  }

  const handleDelete = async (userId) => {
    if (!window.confirm('¿Eliminar este usuario?')) return

    try {
      await deleteAdminUser(userId, token)
      setUsers(users.filter(u => u.id !== userId))
    } catch (err) {
      console.error('Error deleting user:', err)
      alert(`Error: ${err.message}`)
    }
  }

  if (loading) return <div className="loading">Cargando usuarios...</div>
  if (error) return <div className="error">Error: {error}</div>

  return (
    <div className="admin-page">
      <h1>👥 Gestión de Usuarios</h1>

      {users.length === 0 ? (
        <p className="empty">No hay usuarios</p>
      ) : (
        <table className="admin-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Email</th>
              <th>Nombre</th>
              <th>Rol</th>
              <th>Activo</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id} className={editingId === user.id ? 'editing' : ''}>
                <td>{user.id}</td>
                <td>
                  {editingId === user.id ? (
                    <input
                      type="email"
                      value={editData.email || ''}
                      onChange={(e) => setEditData({ ...editData, email: e.target.value })}
                    />
                  ) : (
                    user.email
                  )}
                </td>
                <td>
                  {editingId === user.id ? (
                    <input
                      type="text"
                      value={editData.name || ''}
                      onChange={(e) => setEditData({ ...editData, name: e.target.value })}
                    />
                  ) : (
                    user.name
                  )}
                </td>
                <td>
                  {editingId === user.id ? (
                    <select
                      value={editData.role || 'user'}
                      onChange={(e) => setEditData({ ...editData, role: e.target.value })}
                    >
                      <option value="user">user</option>
                      <option value="admin">admin</option>
                    </select>
                  ) : (
                    user.role
                  )}
                </td>
                <td>
                  {editingId === user.id ? (
                    <input
                      type="checkbox"
                      checked={editData.is_active || false}
                      onChange={(e) => setEditData({ ...editData, is_active: e.target.checked })}
                    />
                  ) : (
                    user.is_active ? '✓' : '✗'
                  )}
                </td>
                <td className="actions">
                  {editingId === user.id ? (
                    <>
                      <button
                        className="btn-save"
                        onClick={() => handleSaveEdit(user.id)}
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
                        onClick={() => handleEdit(user)}
                      >
                        Editar
                      </button>
                      <button
                        className="btn-delete"
                        onClick={() => handleDelete(user.id)}
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
