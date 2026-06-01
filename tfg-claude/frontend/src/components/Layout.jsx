import React from 'react'
import { Outlet } from 'react-router-dom'
import { Navbar } from './Navbar'
import './Layout.css'

/**
 * Layout principal de la aplicación.
 */
export function Layout() {
  return (
    <div className="layout">
      <Navbar />
      <main className="layout-main">
        <Outlet />
      </main>
      <footer className="layout-footer">
        <p>&copy; 2026 AgroManager. Todos los derechos reservados.</p>
      </footer>
    </div>
  )
}
