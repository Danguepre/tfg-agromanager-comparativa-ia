import { Navigate } from 'react-router-dom';
import { getToken } from '../api/api';
import { useAuth } from '../context/AuthContext';

export default function AdminRoute({ children }) {
  const { user, loading } = useAuth();
  const token = getToken();

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  if (loading) {
    return <div style={{ padding: '2rem', textAlign: 'center' }}>Verificando permisos...</div>;
  }

  if (!user || user.role !== 'admin') {
    return (
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <div style={{ color: '#b8860b', fontSize: '1.5rem', marginBottom: '1rem' }}>⛔ Acceso restringido</div>
        <p>No tienes permisos de administrador para acceder a esta sección.</p>
        <a href="/dashboard" style={{ color: '#1a6b3c' }}>Volver al Dashboard</a>
      </div>
    );
  }

  return children;
}