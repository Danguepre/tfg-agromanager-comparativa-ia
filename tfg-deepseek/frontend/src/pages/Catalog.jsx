import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiGet, apiPost, normalizeList } from '../api/api';

export default function Catalog() {
  const [crops, setCrops] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const [adding, setAdding] = useState(null);
  const navigate = useNavigate();

  async function loadCrops(name) {
    setLoading(true);
    setError('');
    try {
      const params = name ? `?name=${encodeURIComponent(name)}` : '';
      const data = await apiGet(`/crops/published${params}`);
      setCrops(normalizeList(data));
    } catch (err) {
      setError(err.message || 'Error al cargar catálogo');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadCrops();
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    loadCrops(search);
  };

  const handleAdd = async (cropId) => {
    setAdding(cropId);
    try {
      await apiPost(`/crops/${cropId}/add-to-my-crops`);
      navigate('/crops');
    } catch (err) {
      setError(err.message || 'Error al añadir cultivo');
      setAdding(null);
    }
  };

  if (loading && crops.length === 0) return <div style={{ padding: '2rem', textAlign: 'center' }}>Cargando catálogo...</div>;

  return (
    <div style={{ padding: '1.5rem', maxWidth: 1000, margin: '0 auto' }}>
      <h2 style={{ color: '#1a6b3c', marginBottom: '1rem' }}>Catálogo de Cultivos</h2>

      <form onSubmit={handleSearch} style={{ marginBottom: '1.5rem', display: 'flex', gap: '0.5rem' }}>
        <input
          type="text"
          placeholder="Buscar por nombre..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ flex: 1, padding: '0.5rem', borderRadius: 4, border: '1px solid #ccc' }}
        />
        <button type="submit" style={{
          padding: '0.5rem 1rem', background: '#1a6b3c', color: '#fff',
          border: 'none', borderRadius: 4, cursor: 'pointer'
        }}>
          Buscar
        </button>
        {search && (
          <button type="button" onClick={() => { setSearch(''); loadCrops(); }} style={{
            padding: '0.5rem 1rem', background: '#666', color: '#fff',
            border: 'none', borderRadius: 4, cursor: 'pointer'
          }}>
            Limpiar
          </button>
        )}
      </form>

      {error && (
        <div style={{
          background: '#fde8e8', color: '#c53030', padding: '0.75rem',
          borderRadius: 6, marginBottom: '1rem', border: '1px solid #fcc5c5'
        }}>
          {error}
        </div>
      )}

      {crops.length === 0 && !loading ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: '#888' }}>
          {search ? 'No se encontraron cultivos con ese nombre.' : 'No hay cultivos públicos disponibles.'}
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
                <div style={{ fontWeight: 600, color: '#1a6b3c' }}>{crop.name}</div>
                {crop.scientific_name && (
                  <span style={{ color: '#888', fontStyle: 'italic', fontSize: '0.875rem' }}>{crop.scientific_name}</span>
                )}
                {crop.description && (
                  <p style={{ color: '#666', fontSize: '0.875rem', marginTop: '0.25rem', maxWidth: 500 }}>
                    {crop.description.length > 120 ? crop.description.substring(0, 120) + '...' : crop.description}
                  </p>
                )}
              </div>
              <button
                onClick={() => handleAdd(crop.id)}
                disabled={adding === crop.id}
                style={{
                  background: adding === crop.id ? '#888' : '#1a6b3c',
                  color: '#fff', border: 'none', borderRadius: 4,
                  padding: '0.4rem 0.8rem', cursor: adding === crop.id ? 'not-allowed' : 'pointer',
                  fontSize: '0.875rem', whiteSpace: 'nowrap'
                }}
              >
                {adding === crop.id ? 'Añadiendo...' : 'Añadir a mis cultivos'}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}