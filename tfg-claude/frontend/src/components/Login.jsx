import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { authLogin, parseJwt } from '../api/api'
import { useAuth } from '../context/AuthContext'
import './Auth.css'

export function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const { login } = useAuth()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      const response = await authLogin(email, password)
      const token = response.access_token

      // Decodificar JWT para extraer user_id y role
      const decoded = parseJwt(token)
      if (!decoded) {
        throw new Error('Error decodificando token JWT')
      }

      // Construir usuario con datos del JWT + email del formulario
      const user = {
        id: decoded.user_id,
        email: email,
        role: decoded.role,
        name: email.split('@')[0], // Usar parte del email como nombre
      }

      login(user, token)
      navigate('/dashboard')
    } catch (err) {
      setError(err.data?.detail || err.message || 'Error en login')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-box">
        <h1>AgroManager</h1>
        <h2>Iniciar Sesión</h2>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Contraseña</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button type="submit" disabled={loading}>
            {loading ? 'Iniciando...' : 'Iniciar Sesión'}
          </button>
        </form>

        <p className="auth-link">
          ¿No tienes cuenta? <Link to="/register">Regístrate aquí</Link>
        </p>
      </div>
    </div>
  )
}
