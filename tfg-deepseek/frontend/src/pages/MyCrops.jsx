import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { apiGet, apiDelete, apiRequest, normalizeList } from '../api/api';

export default function MyCrops() {
  const [crops, setCrops] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  const [editingId, setEditingId] = useState(null);
  const [editForm, setEditForm] = useState({});

  async function load() {
    try {
      const data = await apiGet('/crops/my');
      setCrops(normalizeList(data));
      setError('');
    } catch (err) {
      setError(err.message || 'Error al cargar cultivos');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  // ── Edición inline ──

  function startEdit(crop) {
    setEditingId(crop.id);
    setEditForm({
      name: crop.name || '',
      scientific_name: crop.scientific_name || '',
      description: crop.description || '',
      category: crop.category || '',
    });
  }

  function cancelEdit() {
    setEditingId(null);
    setEditForm({});
  }

  async function saveEdit(cropId) {
    try {
      // El endpoint PUT /crops/{crop_id} espera multipart/form-data (Form params)
      const formData = new FormData();
      if (editForm.name !== undefined) formData.append('name', editForm.name);
      if (editForm.scientific_name !== undefined) formData.append('scientific_name', editForm.scientific_name);
      if (editForm.description !== undefined) formData.append('description', editForm.description);
      if (editForm.category !== undefined) formData.append('category', editForm.category);

      await apiRequest(`/crops/${cropId}`, { method: 'PUT', body: formData });
      setSuccessMsg('Cultivo actualizado correctamente');
      setEditingId(null);
      setEditForm({});
      setTimeout(() => setSuccessMsg(''), 3000);
      load();
    } catch (err) {
      setError(err.message || 'Error al actualizar cultivo');
    }
  }

  // ── Eliminación con confirm ──

  async function handleDelete(cropId, cropName) {
    if (!window.confirm(`¿Eliminar "${cropName}"? Esta acción no se puede deshacer.`)) {
      return;
    }
    try {
      await apiDelete(`/crops/${cropId}`);
      setSuccessMsg(`"${cropName}" eliminado correctamente`);
      setTimeout(() => setSuccessMsg(''), 3000);
      load();
    } catch (err) {
      setError(err.message || 'Error al eliminar cultivo');
    }
  }

  // ── Render ──

  if (loading) return <div style={{ padding: '2rem', textAlign: 'center' }}>Cargando cultivos...</div>;
  if (error) return <div style={{ padding: '2rem', color: 'red' }}>Error: {error}</div>;

  return (
    <div style={{ padding: '1.5rem', maxWidth: 1000, margin: '0 auto' }}>
      <h2 style={{ color: '#1a6b3c', marginBottom: '1.5rem' }}>Mis Cultivos</h2>

      {successMsg && (
        <div style={{ background: '#d4edda', color: '#155724', padding: '0.75rem', borderRadius: 4, marginBottom: '1rem' }}>
          {successMsg}
        </div>
      )}

      {error && (
        <div style={{ background: '#f8d7da', color: '#721c24', padding: '0.75rem', borderRadius: 4, marginBottom: '1rem' }}>
          {error}
          <button onClick={() => setError('')} style={{ marginLeft: '1rem', background: 'none', border: 'none', cursor: 'pointer', color: '#721c24' }}>✕</button>
        </div>
      )}

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
            }}>
              {editingId === crop.id ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', flexWrap: 'wrap' }}>
                    <label style={labelStyle}>Nombre:</label>
                    <input style={inputStyle} value={editForm.name || ''}
                      onChange={e => setEditForm({ ...editForm, name: e.target.value })} />
                  </div>
                  <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', flexWrap: 'wrap' }}>
                    <label style={labelStyle}>Nombre científico:</label>
                    <input style={inputStyle} value={editForm.scientific_name || ''}
                      onChange={e => setEditForm({ ...editForm, scientific_name: e.target.value })} />
                  </div>
                  <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', flexWrap: 'wrap' }}>
                    <label style={labelStyle}>Descripción:</label>
                    <textarea style={{ ...inputStyle, minHeight: 60, resize: 'vertical' }} value={editForm.description || ''}
                      onChange={e => setEditForm({ ...editForm, description: e.target.value })} />
                  </div>
                  <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', flexWrap: 'wrap' }}>
                    <label style={labelStyle}>Categoría:</label>
                    <input style={inputStyle} value={editForm.category || ''}
                      onChange={e => setEditForm({ ...editForm, category: e.target.value })} />
                  </div>
                  <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.25rem' }}>
                    <button onClick={() => saveEdit(crop.id)} style={saveBtnStyle}>Guardar</button>
                    <button onClick={cancelEdit} style={cancelBtnStyle}>Cancelar</button>
                  </div>
                </div>
              ) : (
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
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
                  <div style={{ display: 'flex', gap: '0.35rem', alignItems: 'center' }}>
                    <button onClick={() => startEdit(crop)} style={editBtnStyle}>Editar</button>
                    <button onClick={() => handleDelete(crop.id, crop.name)} style={delBtnStyle}>Eliminar</button>
                    <Link to={`/crops/${crop.id}`} style={viewBtnStyle}>Ver detalle</Link>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ── Estilos compartidos ──

const baseBtn = { border: 'none', borderRadius: 4, padding: '0.35rem 0.8rem', cursor: 'pointer', fontSize: '0.875rem', textDecoration: 'none', display: 'inline-block' };

const labelStyle = { fontSize: '0.875rem', fontWeight: 600, color: '#555', minWidth: 110 };
const inputStyle = {
  padding: '0.35rem 0.6rem', border: '1px solid #ccc', borderRadius: 4,
  fontSize: '0.875rem', flex: 1, minWidth: 200, boxSizing: 'border-box',
};

const editBtnStyle = { ...baseBtn, background: '#007bff', color: '#fff' };
const delBtnStyle = { ...baseBtn, background: '#dc3545', color: '#fff' };
const viewBtnStyle = { ...baseBtn, background: '#1a6b3c', color: '#fff' };
const saveBtnStyle = { ...baseBtn, background: '#28a745', color: '#fff' };
const cancelBtnStyle = { ...baseBtn, background: '#6c757d', color: '#fff' };