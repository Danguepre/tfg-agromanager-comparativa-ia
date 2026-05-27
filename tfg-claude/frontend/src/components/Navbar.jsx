import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import './Navbar.css'

/**
 * Componente de navegación principal.
 */
export function Navbar() {
  const { user, logout } = useAuth()
  const location = useLocation()

  const isActive = (path) => location.pathname === path

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">
          <h1>🌱 AgroManager</h1>
        </Link>

        {user ? (
          <div className="navbar-menu">
            <div className="nav-links">
              <Link
                to="/dashboard"
                className={`nav-link ${isActive('/dashboard') ? 'active' : ''}`}
              >
                Dashboard
              </Link>
              <Link
                to="/crops"
                className={`nav-link ${isActive('/crops') ? 'active' : ''}`}
              >
                Mis Cultivos
              </Link>
              <Link
                to="/catalog"
                className={`nav-link ${isActive('/catalog') ? 'active' : ''}`}
              >
                Catálogo
              </Link>
              <Link
                to="/calendar"
                className={`nav-link ${isActive('/calendar') ? 'active' : ''}`}
              >
                Calendario
              </Link>
              <Link
                to="/tasks"
                className={`nav-link ${isActive('/tasks') ? 'active' : ''}`}
              >
                Tareas
              </Link>
            </div>

            <div className="navbar-user">
              <span className="user-name">{user.name || user.email}</span>
              <button className="logout-btn" onClick={logout}>
                Logout
              </button>
            </div>
          </div>
        ) : (
          <div className="navbar-auth">
            <Link to="/login" className="nav-link">
              Login
            </Link>
            <Link to="/register" className="nav-link primary">
              Registrarse
            </Link>
          </div>
        )}
      </div>
    </nav>
  )
}

