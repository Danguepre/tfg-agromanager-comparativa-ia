import { useState, useEffect } from 'react';
import { apiGet, normalizeList } from '../api/api';

export default function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function load() {
      try {
        const data = await apiGet('/dashboard/summary');
        setSummary(data);
      } catch (err) {
        setError(err.message || 'Error al cargar dashboard');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) return <div style={{ padding: '2rem', textAlign: 'center' }}>Cargando dashboard...</div>;
  if (error) return <div style={{ padding: '2rem', color: 'red' }}>Error: {error}</div>;
  if (!summary) return <div style={{ padding: '2rem' }}>No hay datos disponibles.</div>;

  return (
    <div style={{ padding: '1.5rem', maxWidth: 1000, margin: '0 auto' }}>
      <h2 style={{ color: '#1a6b3c', marginBottom: '1.5rem' }}>Dashboard</h2>

      {/* Tarjetas de resumen */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
        <SummaryCard label="Cultivos propios" value={summary.total_personal_crops ?? 0} />
        <SummaryCard label="Catálogo público" value={summary.total_public_crops ?? 0} />
        <SummaryCard label="Tareas pendientes" value={summary.tasks_pending ?? 0} />
        <SummaryCard label="Tareas completadas" value={summary.tasks_completed ?? 0} />
        <SummaryCard label="Calendarios activos" value={summary.active_calendars ?? 0} />
        <SummaryCard label="Calendarios completados" value={summary.completed_calendars ?? 0} />
      </div>

      {/* Próximas tareas */}
      {summary.upcoming_tasks && summary.upcoming_tasks.length > 0 && (
        <section style={{ marginBottom: '2rem' }}>
          <h3>Próximas tareas</h3>
          <div style={{ background: '#f9f9f9', borderRadius: 8, padding: '1rem' }}>
            {summary.upcoming_tasks.slice(0, 5).map((t) => (
              <div key={t.id} style={{ padding: '0.5rem 0', borderBottom: '1px solid #eaeaea', display: 'flex', justifyContent: 'space-between' }}>
                <span>{t.title}</span>
                <span style={{ color: t.is_completed ? 'green' : '#b8860b', fontSize: '0.875rem' }}>
                  {t.is_completed ? 'Completada' : t.status || 'Pendiente'}
                </span>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Eventos de calendario */}
      {summary.upcoming_calendar_events && summary.upcoming_calendar_events.length > 0 && (
        <section style={{ marginBottom: '2rem' }}>
          <h3>Eventos de calendario activos</h3>
          <div style={{ background: '#f9f9f9', borderRadius: 8, padding: '1rem' }}>
            {summary.upcoming_calendar_events.slice(0, 5).map((evt) => (
              <div key={evt.id} style={{ padding: '0.5rem 0', borderBottom: '1px solid #eaeaea' }}>
                <strong>{evt.crop_name}</strong> — {evt.phase_name}
                {evt.start_date && <span style={{ color: '#666', marginLeft: '0.5rem' }}>desde {evt.start_date}</span>}
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Resumen de riego */}
      {summary.irrigation_summary && summary.irrigation_summary.length > 0 && (
        <section style={{ marginBottom: '2rem' }}>
          <h3>Resumen de riego</h3>
          <div style={{ background: '#f9f9f9', borderRadius: 8, padding: '1rem' }}>
            {summary.irrigation_summary.slice(0, 5).map((irr) => (
              <div key={irr.crop_id} style={{ padding: '0.5rem 0', borderBottom: '1px solid #eaeaea' }}>
                <strong>{irr.crop_name}</strong> — cada {irr.frequency_days ?? '?'} días, {irr.water_needed_mm ?? '?'} mm
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Resumen ambiental */}
      {summary.environmental_summary && summary.environmental_summary.length > 0 && (
        <section style={{ marginBottom: '2rem' }}>
          <h3>Requisitos ambientales</h3>
          <div style={{ background: '#f9f9f9', borderRadius: 8, padding: '1rem' }}>
            {summary.environmental_summary.slice(0, 5).map((env) => (
              <div key={env.crop_id} style={{ padding: '0.5rem 0', borderBottom: '1px solid #eaeaea' }}>
                <strong>{env.crop_name}</strong> — Temp: {env.min_temperature ?? '?'}°C / {env.max_temperature ?? '?'}°C, Sol: {env.sunlight_hours ?? '?'}h
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Si no hay nada */}
      {(!summary.upcoming_tasks || summary.upcoming_tasks.length === 0) &&
       (!summary.upcoming_calendar_events || summary.upcoming_calendar_events.length === 0) &&
       (!summary.irrigation_summary || summary.irrigation_summary.length === 0) &&
       (!summary.environmental_summary || summary.environmental_summary.length === 0) && (
        <div style={{ textAlign: 'center', padding: '3rem', color: '#888' }}>
          No hay datos detallados disponibles. Comienza añadiendo cultivos desde el catálogo.
        </div>
      )}
    </div>
  );
}

function SummaryCard({ label, value }) {
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