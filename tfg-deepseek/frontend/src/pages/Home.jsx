import { Link } from 'react-router-dom';
import { getToken } from '../api/api';

export default function Home() {
  const isLoggedIn = !!getToken();

  return (
    <div style={{ padding: '2rem', maxWidth: 600, margin: '3rem auto', textAlign: 'center' }}>
      <h1 style={{ color: '#1a6b3c', fontSize: '2.5rem', marginBottom: '1rem' }}>🌱 AgroManager</h1>
      <p style={{ color: '#555', fontSize: '1.1rem', marginBottom: '2rem' }}>
        Sistema de gestión agrícola inteligente.
        Administra tus cultivos, tareas, calendarios y más desde un solo lugar.
      </p>
      {isLoggedIn ? (
        <div>
          <Link to="/dashboard" style={{
            display: 'inline-block', background: '#1a6b3c', color: '#fff',
            padding: '0.75rem 2rem', borderRadius: 6, textDecoration: 'none',
            fontSize: '1.1rem', marginBottom: '0.75rem'
          }}>
            Ir al Dashboard
          </Link>
        </div>
      ) : (
        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
          <Link to="/login" style={{
            display: 'inline-block', background: '#1a6b3c', color: '#fff',
            padding: '0.75rem 2rem', borderRadius: 6, textDecoration: 'none', fontSize: '1.1rem'
          }}>
            Iniciar sesión
          </Link>
          <Link to="/register" style={{
            display: 'inline-block', background: '#fff', color: '#1a6b3c',
            padding: '0.75rem 2rem', borderRadius: 6, textDecoration: 'none', fontSize: '1.1rem',
            border: '2px solid #1a6b3c'
          }}>
            Crear cuenta
          </Link>
        </div>
      )}
    </div>
  );
}