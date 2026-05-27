import React from 'react'
import { Link } from 'react-router-dom'
import './Pages.css'

/**
 * Página de inicio / landing.
 */
export function Home() {
  return (
    <div className="home-page">
      <div className="hero">
        <h1>🌱 Bienvenido a AgroManager</h1>
        <p>La plataforma todo-en-uno para gestionar tus cultivos, tareas y calendarios agrícolas.</p>

        <div className="hero-buttons">
          <Link to="/login" className="btn btn-primary">
            Iniciar Sesión
          </Link>
          <Link to="/register" className="btn btn-secondary">
            Crear Cuenta
          </Link>
        </div>
      </div>

      <section className="features">
        <h2>Características Principales</h2>
        <div className="features-grid">
          <div className="feature-card">
            <h3>📊 Dashboard</h3>
            <p>Visualiza un resumen completo de tus cultivos, tareas y calendarios.</p>
          </div>

          <div className="feature-card">
            <h3>🌾 Gestión de Cultivos</h3>
            <p>Administra tus cultivos personales y descubre cultivos del catálogo público.</p>
          </div>

          <div className="feature-card">
            <h3>📅 Calendario Agrícola</h3>
            <p>Registra y monitorea las fases de crecimiento de tus cultivos.</p>
          </div>

          <div className="feature-card">
            <h3>✅ Gestión de Tareas</h3>
            <p>Crea, asigna y completa tareas para mantener tus cultivos al día.</p>
          </div>

          <div className="feature-card">
            <h3>💧 Riego</h3>
            <p>Optimiza el riego con información específica por cultivo.</p>
          </div>

          <div className="feature-card">
            <h3>🌡️ Requisitos Ambientales</h3>
            <p>Monitorea temperatura, humedad y luz necesarias para cada cultivo.</p>
          </div>
        </div>
      </section>

      <section className="cta">
        <h2>¿Listo para empezar?</h2>
        <p>Crea una cuenta ahora y comienza a gestionar tus cultivos de forma inteligente.</p>
        <Link to="/register" className="btn btn-primary btn-large">
          Registrarse Ahora
        </Link>
      </section>
    </div>
  )
}
