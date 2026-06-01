import React from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

/**
 * Componente para proteger rutas privadas.
 */
export function ProtectedRoute({ children }) {
  const { token, loading } = useAuth()

  if (loading) {
    return <div style={{ padding: '2rem', textAlign: 'center' }}>Cargando...</div>
  }

  if (!token) {
    return <Navigate to="/login" replace />
  }

  return children
}
