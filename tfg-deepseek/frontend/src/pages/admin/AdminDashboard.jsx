import { useState, useEffect } from 'react';
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

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '1rem' }}>
        <AdminCard label="Usuarios totales" value={summary.total_users ?? 0} />
        <AdminCard label="Cultivos totales" value={summary.total_crops ?? 0} />
        <AdminCard label="Cultivos públicos" value={summary.total_public_crops ?? 0} />
        <AdminCard label="Tareas totales" value={summary.total_tasks ?? 0} />
        <AdminCard label="Tareas pendientes" value={summary.tasks_pending ?? 0} />
        <AdminCard label="Tareas completadas" value={summary.tasks_completed ?? 0} />
        <AdminCard label="Calendarios activos" value={summary.total_active_calendars ?? 0} />
        <AdminCard label="Calendarios completados" value={summary.total_completed_calendars ?? 0} />
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