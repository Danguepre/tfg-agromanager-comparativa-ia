import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getAdminSummary } from '../../api/api';

export default function AdminDashboard() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function load() {
      try {
        const data = await getAdminSummary();
        setSummary(data);
      } catch (err) {
        setError(err.message || 'Error al cargar resumen admin');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) return <div style={{ padding: '2rem', textAlign: 'center' }}>Cargando resumen admin...</div>;
  if (error) return <div style={{ padding: '2rem', color: 'red' }}>Error: {error}</div>;
  if (!summary) return <div style={{ padding: '2rem' }}>No hay datos disponibles.</div>;

  return (
    <div style={{ padding: '1.5rem', maxWidth: 1000, margin: '0 auto' }}>
      <h2 style={{ color: '#1a6b3c', marginBottom: '1rem' }}>Panel de Administración</h2>
      <p style={{ color: '#666', marginBottom: '1.5rem' }}>Resumen global del sistema</p>

      {/* Tarjetas de resumen */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
        <AdminCard label="Usuarios totales" value={summary.total_users ?? 0} />
        <AdminCard label="Cultivos totales" value={summary.total_crops ?? 0} />
        <AdminCard label="Cultivos públicos" value={summary.total_public_crops ?? 0} />
        <AdminCard label="Tareas totales" value={summary.total_tasks ?? 0} />
        <AdminCard label="Tareas pendientes" value={summary.tasks_pending ?? 0} />
        <AdminCard label="Tareas completadas" value={summary.tasks_completed ?? 0} />
        <AdminCard label="Calendarios activos" value={summary.total_active_calendars ?? 0} />
        <AdminCard label="Calendarios completados" value={summary.total_completed_calendars ?? 0} />
      </div>

      {/* Acciones de gestión */}
      <h3 style={{ color: '#1a6b3c', marginBottom: '1rem' }}>Gestión</h3>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: '1rem' }}>
        <Link to="/admin/users" style={{ textDecoration: 'none' }}>
          <ActionCard
            icon="👥"
            title="Gestionar usuarios"
            description={`${summary.total_users ?? 0} usuarios registrados`}
          />
        </Link>
        <Link to="/admin/crops" style={{ textDecoration: 'none' }}>
          <ActionCard
            icon="🌾"
            title="Gestionar cultivos"
            description={`${summary.total_crops ?? 0} cultivos (${summary.total_public_crops ?? 0} públicos)`}
          />
        </Link>
        <Link to="/admin/tasks" style={{ textDecoration: 'none' }}>
          <ActionCard
            icon="📋"
            title="Gestionar tareas"
            description={`${summary.total_tasks ?? 0} tareas (${summary.tasks_pending ?? 0} pendientes)`}
          />
        </Link>
      </div>
    </div>
  );
}

function AdminCard({ label, value }) {
  return (
    <div style={{
      background: '#fff', borderRadius: 8, padding: '1.25rem',
      boxShadow: '0 1px 4px rgba(0,0,0,0.1)', textAlign: 'center'
    }}>
      <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#1a6b3c' }}>{value}</div>
      <div style={{ color: '#666', fontSize: '0.875rem', marginTop: '0.25rem' }}>{label}</div>
    </div>
  );
}

function ActionCard({ icon, title, description }) {
  return (
    <div style={{
      background: '#fff', borderRadius: 8, padding: '1.25rem',
      boxShadow: '0 2px 6px rgba(0,0,0,0.12)',
      textAlign: 'center', cursor: 'pointer',
      transition: 'transform 0.15s, box-shadow 0.15s',
      border: '2px solid #e8f5e9',
    }}
    onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-2px)'; e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.18)'; }}
    onMouseLeave={e => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = '0 2px 6px rgba(0,0,0,0.12)'; }}
    >
      <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>{icon}</div>
      <div style={{ fontWeight: 'bold', color: '#1a6b3c', fontSize: '1.05rem', marginBottom: '0.3rem' }}>{title}</div>
      <div style={{ color: '#888', fontSize: '0.85rem' }}>{description}</div>
    </div>
  );
}