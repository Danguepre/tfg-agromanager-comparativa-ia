import { useState, useEffect } from 'react';
import { apiGet, normalizeList } from '../api/api';

export default function CalendarPage() {
  const [calendars, setCalendars] = useState([]);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function load() {
      try {
        // Cargar calendarios y eventos
        let calData = [];
        let evtData = [];

        try {
          calData = await apiGet('/calendar/');
          calData = normalizeList(calData);
        } catch (e) {
          // Puede no haber calendarios
        }

        try {
          evtData = await apiGet('/calendar/events');
          evtData = normalizeList(evtData);
        } catch (e) {
          // Puede no haber eventos
        }

        setCalendars(calData);
        setEvents(evtData);
      } catch (err) {
        setError(err.message || 'Error al cargar calendario');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) return <div style={{ padding: '2rem', textAlign: 'center' }}>Cargando calendario...</div>;
  if (error) return <div style={{ padding: '2rem', color: 'red' }}>Error: {error}</div>;

  const hasData = calendars.length > 0 || events.length > 0;

  return (
    <div style={{ padding: '1.5rem', maxWidth: 1000, margin: '0 auto' }}>
      <h2 style={{ color: '#1a6b3c', marginBottom: '1.5rem' }}>Calendario Agrícola</h2>

      {!hasData ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: '#888' }}>
          <p>No hay calendarios agrícolas activos.</p>
          <p>Para crear un calendario, primero añade un cultivo desde el catálogo y luego configúralo desde la vista de detalle.</p>
        </div>
      ) : (
        <>
          {/* Calendarios */}
          {calendars.length > 0 && (
            <section style={{ marginBottom: '2rem' }}>
              <h3>Calendarios ({calendars.length})</h3>
              <div style={{ display: 'grid', gap: '0.75rem', marginTop: '0.5rem' }}>
                {calendars.map((cal) => (
                  <div key={cal.id} style={{
                    background: '#fff', borderRadius: 8, padding: '1rem',
                    boxShadow: '0 1px 4px rgba(0,0,0,0.1)'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div>
                        <strong>Cultivo ID: {cal.crop_id}</strong>
                        <span style={{
                          marginLeft: '0.75rem', fontSize: '0.75rem',
                          padding: '0.15rem 0.5rem', borderRadius: 4,
                          background: cal.is_active ? '#e8f5e9' : '#f5f5f5',
                          color: cal.is_active ? '#2e7d32' : '#888'
                        }}>
                          {cal.is_active ? 'Activo' : 'Inactivo'}
                        </span>
                        {cal.status && (
                          <span style={{ marginLeft: '0.5rem', fontSize: '0.75rem', color: '#666' }}>
                            {cal.status}
                          </span>
                        )}
                      </div>
                      <div style={{ fontSize: '0.875rem', color: '#666' }}>
                        {cal.current_phase_index !== undefined && (
                          <span>Fase actual: {['Siembra', 'Trasplante', 'Cosecha'][cal.current_phase_index] || cal.current_phase_index}</span>
                        )}
                      </div>
                    </div>
                    <div style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: '#666', display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                      {cal.planting_start && <span>Siembra: {cal.planting_start} - {cal.planting_end}</span>}
                      {cal.transplant_start && <span>Trasplante: {cal.transplant_start} - {cal.transplant_end}</span>}
                      {cal.harvest_start && <span>Cosecha: {cal.harvest_start} - {cal.harvest_end}</span>}
                    </div>
                    {cal.notes && <p style={{ fontSize: '0.875rem', color: '#888', marginTop: '0.25rem' }}>{cal.notes}</p>}
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Eventos */}
          {events.length > 0 && (
            <section>
              <h3>Eventos activos ({events.length})</h3>
              <div style={{ display: 'grid', gap: '0.5rem', marginTop: '0.5rem' }}>
                {events.map((evt, idx) => (
                  <div key={idx} style={{
                    background: '#fff', borderRadius: 8, padding: '0.75rem 1rem',
                    boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
                    display: 'flex', justifyContent: 'space-between', alignItems: 'center'
                  }}>
                    <span>
                      <span style={{
                        display: 'inline-block', width: 8, height: 8, borderRadius: '50%',
                        background: evt.phase_index === 0 ? '#4caf50' : evt.phase_index === 1 ? '#ff9800' : '#f44336',
                        marginRight: 8
                      }} />
                      {evt.label || `${evt.phase} - ${evt.fortnight === 1 ? '1ª' : '2ª'} quincena`}
                    </span>
                    <span style={{ fontSize: '0.875rem', color: '#888' }}>
                      Mes {evt.month}
                    </span>
                  </div>
                ))}
              </div>
            </section>
          )}
        </>
      )}
    </div>
  );
}