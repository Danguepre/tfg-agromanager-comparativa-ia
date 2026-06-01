import { useState, useEffect } from 'react';
import { getAdminCrops, updateAdminCrop, deleteAdminCrop } from '../../api/api';

export default function AdminCrops() {
  const [crops, setCrops] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [editingId, setEditingId] = useState(null);
  const [editForm, setEditForm] = useState({});
  const [deleteConfirm, setDeleteConfirm] = useState(null);
  const [successMsg, setSuccessMsg] = useState('');

  async function loadCrops() {
    try {
      setLoading(true);
      const data = await getAdminCrops();
      setCrops(Array.isArray(data) ? data : []);
      setError('');
    } catch (err) {
      setError(err.message || 'Error al cargar cultivos');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { loadCrops(); }, []);

  function startEdit(crop) {
    setEditingId(crop.id);
    setEditForm({
      name: crop.name || '',
      description: crop.description || '',
      category: crop.category || '',
      is_public: crop.is_public,
    });
  }

  function cancelEdit() {
    setEditingId(null);
    setEditForm({});
  }

  async function saveEdit(cropId) {
    try {
      const payload = {};
      if (editForm.name !== undefined) payload.name = editForm.name;
      if (editForm.description !== undefined) payload.description = editForm.description;
      if (editForm.category !== undefined) payload.category = editForm.category;
      if (editForm.is_public !== undefined) payload.is_public = editForm.is_public;

      await updateAdminCrop(cropId, payload);
      setSuccessMsg('Cultivo actualizado correctamente');
      setEditingId(null);
      setEditForm({});
      setTimeout(() => setSuccessMsg(''), 3000);
      loadCrops();
    } catch (err) {
      setError(err.message || 'Error al actualizar cultivo');
    }
  }

  async function confirmDelete(cropId) {
    try {
      await deleteAdminCrop(cropId);
      setSuccessMsg('Cultivo eliminado correctamente');
      setDeleteConfirm(null);
      setTimeout(() => setSuccessMsg(''), 3000);
      loadCrops();
    } catch (err) {
      setError(err.message || 'Error al eliminar cultivo');
    }
  }

  return (
    <div style={{ padding: '1.5rem', maxWidth: 1200, margin: '0 auto' }}>
      <h2 style={{ color: '#1a6b3c', marginBottom: '1rem' }}>Administrar Cultivos</h2>

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

      {loading ? (
        <div style={{ textAlign: 'center', padding: '2rem' }}>Cargando cultivos...</div>
      ) : crops.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '2rem', color: '#888' }}>No hay cultivos registrados.</div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', background: '#fff', borderRadius: 8, boxShadow: '0 1px 4px rgba(0,0,0,0.1)' }}>
            <thead>
              <tr style={{ background: '#1a6b3c', color: '#fff' }}>
                <th style={thStyle}>ID</th>
                <th style={thStyle}>Nombre</th>
                <th style={thStyle}>Descripción</th>
                <th style={thStyle}>Tipo</th>
                <th style={thStyle}>Público</th>
                <th style={thStyle}>Propietario</th>
                <th style={thStyle}>Creado</th>
                <th style={thStyle}>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {crops.map((crop, idx) => (
                <tr key={crop.id} style={{ background: idx % 2 === 0 ? '#f9f9f9' : '#fff' }}>
                  {editingId === crop.id ? (
                    <>
                      <td style={tdStyle}>{crop.id}</td>
                      <td style={tdStyle}>
                        <input
                          style={inputStyle}
                          value={editForm.name || ''}
                          onChange={e => setEditForm({ ...editForm, name: e.target.value })}
                        />
                      </td>
                      <td style={tdStyle}>
                        <input
                          style={inputStyle}
                          value={editForm.description || ''}
                          onChange={e => setEditForm({ ...editForm, description: e.target.value })}
                        />
                      </td>
                      <td style={tdStyle}>
                        <input
                          style={inputStyle}
                          value={editForm.category || ''}
                          onChange={e => setEditForm({ ...editForm, category: e.target.value })}
                        />
                      </td>
                      <td style={tdStyle}>
                        <select
                          style={inputStyle}
                          value={editForm.is_public ? 'true' : 'false'}
                          onChange={e => setEditForm({ ...editForm, is_public: e.target.value === 'true' })}
                        >
                          <option value="true">Sí</option>
                          <option value="false">No</option>
                        </select>
                      </td>
                      <td style={tdStyle}>{crop.owner_id || '-'}</td>
                      <td style={tdStyle}>{crop.created_at ? new Date(crop.created_at).toLocaleDateString() : '-'}</td>
                      <td style={tdStyle}>
                        <button onClick={() => saveEdit(crop.id)} style={saveBtnStyle}>Guardar</button>
                        <button onClick={cancelEdit} style={cancelBtnStyle}>Cancelar</button>
                      </td>
                    </>
                  ) : (
                    <>
                      <td style={tdStyle}>{crop.id}</td>
                      <td style={tdStyle}>{crop.name}</td>
                      <td style={tdStyle}>{crop.description ? crop.description.substring(0, 50) + (crop.description.length > 50 ? '...' : '') : '-'}</td>
                      <td style={tdStyle}>{crop.category || '-'}</td>
                      <td style={tdStyle}>
                        <span style={{ color: crop.is_public ? '#28a745' : '#dc3545' }}>
                          {crop.is_public ? 'Sí' : 'No'}
                        </span>
                      </td>
                      <td style={tdStyle}>{crop.owner_id || '-'}</td>
                      <td style={tdStyle}>{crop.created_at ? new Date(crop.created_at).toLocaleDateString() : '-'}</td>
                      <td style={tdStyle}>
                        <button onClick={() => startEdit(crop)} style={editBtnStyle}>Editar</button>
                        {deleteConfirm === crop.id ? (
                          <>
                            <button onClick={() => confirmDelete(crop.id)} style={confirmDelBtnStyle}>Confirmar</button>
                            <button onClick={() => setDeleteConfirm(null)} style={cancelBtnStyle}>No</button>
                          </>
                        ) : (
                          <button onClick={() => setDeleteConfirm(crop.id)} style={delBtnStyle}>Eliminar</button>
                        )}
                      </td>
                    </>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

const baseBtn = { border: 'none', borderRadius: 4, padding: '0.25rem 0.75rem', cursor: 'pointer', fontSize: '0.8rem' };
const thStyle = { padding: '0.75rem', textAlign: 'left', fontSize: '0.875rem' };
const tdStyle = { padding: '0.5rem 0.75rem', borderBottom: '1px solid #eaeaea', fontSize: '0.875rem' };
const inputStyle = {
  padding: '0.25rem 0.5rem',
  border: '1px solid #ccc',
  borderRadius: 4,
  fontSize: '0.875rem',
  width: '100%',
  boxSizing: 'border-box',
};
const editBtnStyle = { ...baseBtn, background: '#007bff', color: '#fff', marginRight: '0.25rem' };
const delBtnStyle = { ...baseBtn, background: '#dc3545', color: '#fff' };
const confirmDelBtnStyle = { ...baseBtn, background: '#dc3545', color: '#fff', marginRight: '0.25rem' };
const cancelBtnStyle = { ...baseBtn, background: '#6c757d', color: '#fff', marginLeft: '0.25rem' };
const saveBtnStyle = { ...baseBtn, background: '#28a745', color: '#fff' };