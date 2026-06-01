import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { apiGet, normalizeList } from '../api/api';

export default function MyCrops() {
  const [crops, setCrops] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function load() {
      try {
        const data = await apiGet('/crops/my');
        setCrops(normalizeList(data));
      } catch (err) {
        setError(err.message || 'Error al cargar cultivos');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) return <div style={{ padding: '2rem', textAlign: 'center' }}>Cargando cultivos...</div>;
  if (error) return <div style={{ padding: '2rem', color: 'red' }}>Error: {error}</div>;

  return (
    <div style={{ padding: '1.5rem', maxWidth: 1000, margin: '0 auto' }}>
      <h2 style={{ color: '#1a6b3c', marginBottom: '1.5rem' }}>Mis Cultivos</h2>
      {crops.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: '#888' }}>
          <p>No tienes cultivos aún.</p>
          <p>Visita el <Link to="/catalog" style={{ color: '#1a6b3c' }}>catálogo público</Link> para añadir cultivos.</p>
        </div>
      ) : (
        <div style={{ display: 'grid', gap: '1rem' }}>
          {crops.map((crop) => (
            <div key={crop.id} style={{
              background: '#fff', borderRadius: 8, padding: '1rem',
              boxShadow: '0 1px 4px rgba(0,0,0,0.1)',
              display: 'flex', justifyContent: 'space-between', alignItems: 'center'
            }}>
              <div>
                <Link to={`/crops/${crop.id}`} style={{ color: '#1a6b3c', textDecoration: 'none', fontWeight: 600 }}>
                  {crop.name}
                </Link>
                {crop.scientific_name && (
                  <span style={{ color: '#888', fontStyle: 'italic', marginLeft: '0.5rem', fontSize: '0.875rem' }}>
                    {crop.scientific_name}
                  </span>
                )}
                <div style={{ fontSize: '0.875rem', color: '#666', marginTop: '0.25rem' }}>
                  {crop.category && <span>Categoría: {crop.category}</span>}
                  {crop.is_public && <span style={{ marginLeft: '0.5rem', background: '#e8f5e9', padding: '0.1rem 0.4rem', borderRadius: 4, fontSize: '0.75rem' }}>Público</span>}
                  {crop.copied_from_id && <span style={{ marginLeft: '0.5rem', color: '#888', fontSize: '0.75rem' }}>Copia de catálogo</span>}
                </div>
              </div>
              <Link to={`/crops/${crop.id}`} style={{
                background: '#1a6b3c', color: '#fff', textDecoration: 'none',
                padding: '0.4rem 0.8rem', borderRadius: 4, fontSize: '0.875rem'
              }}>
                Ver detalle
              </Link>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}