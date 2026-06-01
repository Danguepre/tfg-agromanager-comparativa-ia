import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(username, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.message || 'Error al iniciar sesión');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 400, margin: '3rem auto', padding: '0 1rem' }}>
      <h2 style={{ color: '#1a6b3c' }}>Iniciar Sesión</h2>
      {error && (
        <div style={{
          background: '#fde8e8', color: '#c53030', padding: '0.75rem',
          borderRadius: 6, marginBottom: '1rem', border: '1px solid #fcc5c5'
        }}>
          {error}
        </div>
      )}
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '1rem' }}>
          <label style={{ display: 'block', marginBottom: '0.25rem', fontWeight: 500 }}>Usuario</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            style={{ width: '100%', padding: '0.5rem', borderRadius: 4, border: '1px solid #ccc' }}
          />
        </div>
        <div style={{ marginBottom: '1rem' }}>
          <label style={{ display: 'block', marginBottom: '0.25rem', fontWeight: 500 }}>Contraseña</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{ width: '100%', padding: '0.5rem', borderRadius: 4, border: '1px solid #ccc' }}
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          style={{
            width: '100%', padding: '0.75rem', background: '#1a6b3c',
            color: '#fff', border: 'none', borderRadius: 4,
            cursor: loading ? 'not-allowed' : 'pointer', fontSize: '1rem'
          }}
        >
          {loading ? 'Ingresando...' : 'Iniciar sesión'}
        </button>
      </form>
      <p style={{ marginTop: '1rem', textAlign: 'center' }}>
        ¿No tienes cuenta? <Link to="/register" style={{ color: '#1a6b3c' }}>Regístrate</Link>
      </p>
    </div>
  );
}