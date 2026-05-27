import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { user, logout, isAuthenticated, isAdmin } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!isAuthenticated) {
    return null;
  }

  return (
    <nav style={{
      background: '#1a6b3c',
      color: '#fff',
      padding: '0.75rem 1.5rem',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      flexWrap: 'wrap',
      gap: '0.5rem',
    }}>
      <Link to="/" style={{ color: '#fff', textDecoration: 'none', fontSize: '1.25rem', fontWeight: 'bold' }}>
        🌱 AgroManager
      </Link>
      <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', flexWrap: 'wrap' }}>
        <Link to="/dashboard" style={{ color: '#fff', textDecoration: 'none' }}>Dashboard</Link>
        <Link to="/crops" style={{ color: '#fff', textDecoration: 'none' }}>Mis Cultivos</Link>
        <Link to="/catalog" style={{ color: '#fff', textDecoration: 'none' }}>Catálogo</Link>
        <Link to="/calendar" style={{ color: '#fff', textDecoration: 'none' }}>Calendario</Link>
        <Link to="/tasks" style={{ color: '#fff', textDecoration: 'none' }}>Tareas</Link>
        {isAdmin && (
          <Link to="/admin/dashboard" style={{ color: '#ffd700', textDecoration: 'none', fontWeight: 'bold' }}>
            Admin ⚙️
          </Link>
        )}
        {user && (
          <span style={{ opacity: 0.8, fontSize: '0.875rem' }}>
            {user.username || user.email || 'Usuario'}
          </span>
        )}
        <button
          onClick={handleLogout}
          style={{
            background: 'rgba(255,255,255,0.15)',
            color: '#fff',
            border: '1px solid rgba(255,255,255,0.3)',
            borderRadius: '4px',
            padding: '0.25rem 0.75rem',
            cursor: 'pointer',
            fontSize: '0.875rem',
          }}
        >
          Cerrar sesión
        </button>
      </div>
    </nav>
  );
}
