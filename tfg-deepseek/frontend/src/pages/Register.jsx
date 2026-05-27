import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    username: '',
    email: '',
    password: '',
    full_name: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await register({
        username: form.username,
        email: form.email,
        password: form.password,
        full_name: form.full_name || undefined,
      });
      navigate('/login');
    } catch (err) {
      setError(err.message || 'Error al registrarse');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 400, margin: '3rem auto', padding: '0 1rem' }}>
      <h2 style={{ color: '#1a6b3c' }}>Crear Cuenta</h2>
      {error && (
        <div style={{
          background: '#fde8e8', color: '#c53030', padding: '0.75rem',
          borderRadius: 6, marginBottom: '1rem', border: '1px solid #fcc5c5'
        }}>
          {error}
        </div>
      )}
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '0.75rem' }}>
          <label style={{ display: 'block', marginBottom: '0.25rem', fontWeight: 500 }}>Usuario *</label>
          <input type="text" name="username" value={form.username} onChange={handleChange} required
            style={{ width: '100%', padding: '0.5rem', borderRadius: 4, border: '1px solid #ccc' }} />
        </div>
        <div style={{ marginBottom: '0.75rem' }}>
          <label style={{ display: 'block', marginBottom: '0.25rem', fontWeight: 500 }}>Email *</label>
          <input type="email" name="email" value={form.email} onChange={handleChange} required
            style={{ width: '100%', padding: '0.5rem', borderRadius: 4, border: '1px solid #ccc' }} />
        </div>
        <div style={{ marginBottom: '0.75rem' }}>
          <label style={{ display: 'block', marginBottom: '0.25rem', fontWeight: 500 }}>Contraseña *</label>
          <input type="password" name="password" value={form.password} onChange={handleChange} required minLength={6}
            style={{ width: '100%', padding: '0.5rem', borderRadius: 4, border: '1px solid #ccc' }} />
        </div>
        <div style={{ marginBottom: '1rem' }}>
          <label style={{ display: 'block', marginBottom: '0.25rem', fontWeight: 500 }}>Nombre completo</label>
          <input type="text" name="full_name" value={form.full_name} onChange={handleChange}
            style={{ width: '100%', padding: '0.5rem', borderRadius: 4, border: '1px solid #ccc' }} />
        </div>
        <button type="submit" disabled={loading}
          style={{
            width: '100%', padding: '0.75rem', background: '#1a6b3c',
            color: '#fff', border: 'none', borderRadius: 4,
            cursor: loading ? 'not-allowed' : 'pointer', fontSize: '1rem'
          }}
        >
          {loading ? 'Registrando...' : 'Crear cuenta'}
        </button>
      </form>
      <p style={{ marginTop: '1rem', textAlign: 'center' }}>
        ¿Ya tienes cuenta? <Link to="/login" style={{ color: '#1a6b3c' }}>Inicia sesión</Link>
      </p>
    </div>
  );
}