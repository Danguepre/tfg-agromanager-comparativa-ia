import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { authRegister, authLogin, parseJwt } from '../api/api'
import { useAuth } from '../context/AuthContext'
import './Auth.css'

export function Register() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const { login } = useAuth()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      // Registrar usuario
      await authRegister(email, password, name)

      // Login automático después del registro
      const response = await authLogin(email, password)
      const token = response.access_token

      // Decodificar JWT para extraer user_id y role
      const decoded = parseJwt(token)
      if (!decoded) {
        throw new Error('Error decodificando token JWT')
      }

      // Construir usuario con datos del JWT + nombre del formulario
      const user = {
        id: decoded.user_id,
        email: email,
        role: decoded.role,
        name: name,
      }

      login(user, token)
      navigate('/dashboard')
    } catch (err) {
      setError(err.data?.detail || err.message || 'Error en registro')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-box">
        <h1>AgroManager</h1>
        <h2>Crear Cuenta</h2>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="name">Nombre</label>
            <input
              id="name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>

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
            {loading ? 'Creando cuenta...' : 'Registrarse'}
          </button>
        </form>

        <p className="auth-link">
          ¿Ya tienes cuenta? <Link to="/login">Inicia sesión aquí</Link>
        </p>
      </div>
    </div>
  )
}
