import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import { Layout } from './components/Layout'
import { ProtectedRoute } from './components/ProtectedRoute'
import { ProtectedAdminRoute } from './components/ProtectedAdminRoute'
import { Login } from './components/Login'
import { Register } from './components/Register'
import { Home } from './pages/Home'
import { Dashboard } from './pages/Dashboard'
import { Crops } from './pages/Crops'
import { CropDetail } from './pages/CropDetail'
import { Calendar } from './pages/Calendar'
import { Tasks } from './pages/Tasks'
import { AdminDashboard } from './pages/AdminDashboard'
import { AdminUsers } from './pages/AdminUsers'
import { AdminCrops } from './pages/AdminCrops'
import { AdminTasks } from './pages/AdminTasks'

/**
 * Componente principal de la aplicación con enrutamiento.
 */
function App() {
  const { loading } = useAuth()

  if (loading) {
    return <div style={{ padding: '2rem', textAlign: 'center' }}>Cargando aplicación...</div>
  }

  return (
    <Routes>
      {/* Rutas públicas */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* Rutas con layout */}
      <Route element={<Layout />}>
        <Route path="/" element={<Home />} />

        {/* Rutas protegidas usuario */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/crops"
          element={
            <ProtectedRoute>
              <Crops />
            </ProtectedRoute>
          }
        />
        <Route
          path="/crops/:id"
          element={
            <ProtectedRoute>
              <CropDetail />
            </ProtectedRoute>
          }
        />
        <Route
          path="/catalog"
          element={
            <ProtectedRoute>
              <Crops />
            </ProtectedRoute>
          }
        />
        <Route
          path="/calendar"
          element={
            <ProtectedRoute>
              <Calendar />
            </ProtectedRoute>
          }
        />
        <Route
          path="/tasks"
          element={
            <ProtectedRoute>
              <Tasks />
            </ProtectedRoute>
          }
        />

        {/* Rutas protegidas admin */}
        <Route
          path="/admin/dashboard"
          element={
            <ProtectedAdminRoute>
              <AdminDashboard />
            </ProtectedAdminRoute>
          }
        />
        <Route
          path="/admin/users"
          element={
            <ProtectedAdminRoute>
              <AdminUsers />
            </ProtectedAdminRoute>
          }
        />
        <Route
          path="/admin/crops"
          element={
            <ProtectedAdminRoute>
              <AdminCrops />
            </ProtectedAdminRoute>
          }
        />
        <Route
          path="/admin/tasks"
          element={
            <ProtectedAdminRoute>
              <AdminTasks />
            </ProtectedAdminRoute>
          }
        />
        <Route
          path="/admin"
          element={
            <ProtectedAdminRoute>
              <AdminDashboard />
            </ProtectedAdminRoute>
          }
        />
      </Route>

      {/* Ruta por defecto */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App

