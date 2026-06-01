import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { apiGet } from '../api/api';

export default function CropDetail() {
  const { id } = useParams();
  const [crop, setCrop] = useState(null);
  const [irrigation, setIrrigation] = useState(null);
  const [environmental, setEnvironmental] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function load() {
      try {
        const cropData = await apiGet(`/crops/${id}`);
        setCrop(cropData);

        // Intentar cargar riego y ambientales
        try {
          const irrData = await apiGet(`/irrigation/crop/${id}`);
          setIrrigation(irrData);
        } catch (e) {
          // No hay riego o error
        }

        try {
          const envData = await apiGet(`/environmental/crop/${id}`);
          setEnvironmental(envData);
        } catch (e) {
          // No hay ambientales o error
        }
      } catch (err) {
        setError(err.message || 'Error al cargar detalle del cultivo');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id]);

  if (loading) return <div style={{ padding: '2rem', textAlign: 'center' }}>Cargando detalle...</div>;
  if (error) return <div style={{ padding: '2rem', color: 'red' }}>Error: {error}</div>;
  if (!crop) return <div style={{ padding: '2rem' }}>Cultivo no encontrado.</div>;

  return (
    <div style={{ padding: '1.5rem', maxWidth: 800, margin: '0 auto' }}>
      <Link to="/crops" style={{ color: '#1a6b3c', textDecoration: 'none', marginBottom: '1rem', display: 'inline-block' }}>
        &larr; Volver a mis cultivos
      </Link>

      <h2 style={{ color: '#1a6b3c', marginBottom: '0.5rem' }}>{crop.name}</h2>
      {crop.scientific_name && (
        <p style={{ fontStyle: 'italic', color: '#666', marginBottom: '0.5rem' }}>{crop.scientific_name}</p>
      )}

      <div style={{ background: '#fff', borderRadius: 8, padding: '1.5rem', boxShadow: '0 1px 4px rgba(0,0,0,0.1)', marginBottom: '1.5rem' }}>
        <h3>Información general</h3>
        {crop.description && <p style={{ marginTop: '0.5rem' }}>{crop.description}</p>}
        <table style={{ width: '100%', marginTop: '1rem', borderCollapse: 'collapse' }}>
          <tbody>
            {crop.category && (
              <tr><td style={{ padding: '0.5rem', borderBottom: '1px solid #eaeaea', fontWeight: 500, width: 180 }}>Categoría</td><td style={{ padding: '0.5rem', borderBottom: '1px solid #eaeaea' }}>{crop.category}</td></tr>
            )}
            <tr><td style={{ padding: '0.5rem', borderBottom: '1px solid #eaeaea', fontWeight: 500 }}>Público</td><td style={{ padding: '0.5rem', borderBottom: '1px solid #eaeaea' }}>{crop.is_public ? 'Sí' : 'No'}</td></tr>
            {crop.copied_from_id && (
              <tr><td style={{ padding: '0.5rem', borderBottom: '1px solid #eaeaea', fontWeight: 500 }}>Copia de</td><td style={{ padding: '0.5rem', borderBottom: '1px solid #eaeaea' }}>Catálogo público (ID: {crop.copied_from_id})</td></tr>
            )}
            {crop.created_at && (
              <tr><td style={{ padding: '0.5rem', borderBottom: '1px solid #eaeaea', fontWeight: 500 }}>Creado</td><td style={{ padding: '0.5rem', borderBottom: '1px solid #eaeaea' }}>{new Date(crop.created_at).toLocaleDateString()}</td></tr>
            )}
          </tbody>
        </table>
      </div>

      {irrigation && (
        <div style={{ background: '#fff', borderRadius: 8, padding: '1.5rem', boxShadow: '0 1px 4px rgba(0,0,0,0.1)', marginBottom: '1.5rem' }}>
          <h3>Riego</h3>
          <table style={{ width: '100%', marginTop: '0.5rem', borderCollapse: 'collapse' }}>
            <tbody>
              <tr><td style={{ padding: '0.5rem', borderBottom: '1px solid #eaeaea', fontWeight: 500, width: 180 }}>Frecuencia</td><td style={{ padding: '0.5rem', borderBottom: '1px solid #eaeaea' }}>{irrigation.frequency_days ?? '?'} días</td></tr>
              <tr><td style={{ padding: '0.5rem', borderBottom: '1px solid #eaeaea', fontWeight: 500 }}>Agua necesaria</td><td style={{ padding: '0.5rem', borderBottom: '1px solid #eaeaea' }}>{irrigation.water_needed_mm ?? '?'} mm</td></tr>
              {irrigation.irrigation_method && (
                <tr><td style={{ padding: '0.5rem', borderBottom: '1px solid #eaeaea', fontWeight: 500 }}>Método</td><td style={{ padding: '0.5rem', borderBottom: '1px solid #eaeaea' }}>{irrigation.irrigation_method}</td></tr>
              )}
              {irrigation.notes && (
                <tr><td style={{ padding: '0.5rem', borderBottom: '1px solid #eaeaea', fontWeight: 500 }}>Notas</td><td style={{ padding: '0.5rem', borderBottom: '1px solid #eaeaea' }}>{irrigation.notes}</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {environmental && (
        <div style={{ background: '#fff', borderRadius: 8, padding: '1.5rem', boxShadow: '0 1px 4px rgba(0,0,0,0.1)', marginBottom: '1.5rem' }}>
          <h3>Requisitos Ambientales</h3>
          <table style={{ width: '100%', marginTop: '0.5rem', borderCollapse: 'collapse' }}>
            <tbody>
              <tr><td style={{ padding: '0.5rem', borderBottom: '1px solid #eaeaea', fontWeight: 500, width: 180 }}>Temperatura mínima</td><td style={{ padding: '0.5rem', borderBottom: '1px solid #eaeaea' }}>{environmental.min_temperature ?? '?'} °C</td></tr>
              <tr><td style={{ padding: '0.5rem', borderBottom: '1px solid #eaeaea', fontWeight: 500 }}>Temperatura máxima</td><td style={{ padding: '0.5rem', borderBottom: '1px solid #eaeaea' }}>{environmental.max_temperature ?? '?'} °C</td></tr>
              <tr><td style={{ padding: '0.5rem', borderBottom: '1px solid #eaeaea', fontWeight: 500 }}>Temperatura óptima</td><td style={{ padding: '0.5rem', borderBottom: '1px solid #eaeaea' }}>{environmental.optimal_temperature ?? '?'} °C</td></tr>
              <tr><td style={{ padding: '0.5rem', borderBottom: '1px solid #eaeaea', fontWeight: 500 }}>pH mínimo</td><td style={{ padding: '0.5rem', borderBottom: '1px solid #eaeaea' }}>{environmental.min_ph ?? '?'}</td></tr>
              <tr><td style={{ padding: '0.5rem', borderBottom: '1px solid #eaeaea', fontWeight: 500 }}>pH máximo</td><td style={{ padding: '0.5rem', borderBottom: '1px solid #eaeaea' }}>{environmental.max_ph ?? '?'}</td></tr>
              <tr><td style={{ padding: '0.5rem', borderBottom: '1px solid #eaeaea', fontWeight: 500 }}>Horas de sol</td><td style={{ padding: '0.5rem', borderBottom: '1px solid #eaeaea' }}>{environmental.sunlight_hours ?? '?'} h/día</td></tr>
              {environmental.humidity_percent && (
                <tr><td style={{ padding: '0.5rem', borderBottom: '1px solid #eaeaea', fontWeight: 500 }}>Humedad</td><td style={{ padding: '0.5rem', borderBottom: '1px solid #eaeaea' }}>{environmental.humidity_percent}%</td></tr>
              )}
              {environmental.notes && (
                <tr><td style={{ padding: '0.5rem', borderBottom: '1px solid #eaeaea', fontWeight: 500 }}>Notas</td><td style={{ padding: '0.5rem', borderBottom: '1px solid #eaeaea' }}>{environmental.notes}</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {!irrigation && !environmental && (
        <div style={{ textAlign: 'center', padding: '2rem', color: '#888' }}>
          No hay datos adicionales de riego o ambientales para este cultivo.
        </div>
      )}
    </div>
  );
}