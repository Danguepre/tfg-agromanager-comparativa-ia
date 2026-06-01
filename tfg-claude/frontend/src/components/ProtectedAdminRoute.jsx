import React from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

/**
 * Componente para proteger rutas de administrador.
 * Solo accesibles por usuarios con rol 'admin'.
 */
export function ProtectedAdminRoute({ children }) {
  const { user, token, loading } = useAuth()

  if (loading) {
    return <div style={{ padding: '2rem', textAlign: 'center' }}>Cargando...</div>
  }

  if (!token) {
    return <Navigate to="/login" replace />
  }

  if (user?.role !== 'admin') {
    return (
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <h2>Acceso Denegado</h2>
        <p>No tienes permisos de administrador para acceder a esta sección.</p>
        <a href="/">Volver al inicio</a>
      </div>
    )
  }

  return children
}
