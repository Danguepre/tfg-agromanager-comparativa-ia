import { useState, useEffect } from 'react';
import { getAdminUsers, updateAdminUser, deleteAdminUser } from '../../api/api';

export default function AdminUsers() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [editingId, setEditingId] = useState(null);
  const [editForm, setEditForm] = useState({});
  const [deleteConfirm, setDeleteConfirm] = useState(null);
  const [successMsg, setSuccessMsg] = useState('');

  async function loadUsers() {
    try {
      setLoading(true);
      const data = await getAdminUsers();
      setUsers(Array.isArray(data) ? data : []);
      setError('');
    } catch (err) {
      setError(err.message || 'Error al cargar usuarios');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { loadUsers(); }, []);

  function startEdit(user) {
    setEditingId(user.id);
    setEditForm({
      email: user.email || '',
      username: user.username || '',
      full_name: user.full_name || '',
      role: user.role || 'user',
      is_active: user.is_active,
    });
  }

  function cancelEdit() {
    setEditingId(null);
    setEditForm({});
  }

  async function saveEdit(userId) {
    try {
      const payload = {};
      if (editForm.email !== undefined) payload.email = editForm.email;
      if (editForm.username !== undefined) payload.username = editForm.username;
      if (editForm.full_name !== undefined) payload.full_name = editForm.full_name;
      if (editForm.role !== undefined) payload.role = editForm.role;
      if (editForm.is_active !== undefined) payload.is_active = editForm.is_active;

      await updateAdminUser(userId, payload);
      setSuccessMsg('Usuario actualizado correctamente');
      setEditingId(null);
      setEditForm({});
      setTimeout(() => setSuccessMsg(''), 3000);
      loadUsers();
    } catch (err) {
      setError(err.message || 'Error al actualizar usuario');
    }
  }

  async function confirmDelete(userId) {
    try {
      await deleteAdminUser(userId);
      setSuccessMsg('Usuario eliminado correctamente');
      setDeleteConfirm(null);
      setTimeout(() => setSuccessMsg(''), 3000);
      loadUsers();
    } catch (err) {
      setError(err.message || 'Error al eliminar usuario');
    }
  }

  function toggleActive(user) {
    startEdit(user);
    setEditForm(prev => ({
      ...prev,
      is_active: !user.is_active,
    }));
    // Save immediately
    setTimeout(async () => {
      try {
        await updateAdminUser(user.id, { is_active: !user.is_active });
        setSuccessMsg(`Usuario ${user.is_active ? 'desactivado' : 'activado'} correctamente`);
        setTimeout(() => setSuccessMsg(''), 3000);
        loadUsers();
      } catch (err) {
        setError(err.message || 'Error al cambiar estado');
      }
      setEditingId(null);
      setEditForm({});
    }, 100);
  }

  return (
    <div style={{ padding: '1.5rem', maxWidth: 1200, margin: '0 auto' }}>
      <h2 style={{ color: '#1a6b3c', marginBottom: '1rem' }}>Administrar Usuarios</h2>

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
        <div style={{ textAlign: 'center', padding: '2rem' }}>Cargando usuarios...</div>
      ) : users.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '2rem', color: '#888' }}>No hay usuarios registrados.</div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', background: '#fff', borderRadius: 8, boxShadow: '0 1px 4px rgba(0,0,0,0.1)' }}>
            <thead>
              <tr style={{ background: '#1a6b3c', color: '#fff' }}>
                <th style={thStyle}>ID</th>
                <th style={thStyle}>Email</th>
                <th style={thStyle}>Username</th>
                <th style={thStyle}>Nombre</th>
                <th style={thStyle}>Rol</th>
                <th style={thStyle}>Activo</th>
                <th style={thStyle}>Creado</th>
                <th style={thStyle}>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user, idx) => (
                <tr key={user.id} style={{ background: idx % 2 === 0 ? '#f9f9f9' : '#fff' }}>
                  {editingId === user.id ? (
                    <>
                      <td style={tdStyle}>{user.id}</td>
                      <td style={tdStyle}>
                        <input
                          style={inputStyle}
                          value={editForm.email || ''}
                          onChange={e => setEditForm({ ...editForm, email: e.target.value })}
                        />
                      </td>
                      <td style={tdStyle}>
                        <input
                          style={inputStyle}
                          value={editForm.username || ''}
                          onChange={e => setEditForm({ ...editForm, username: e.target.value })}
                        />
                      </td>
                      <td style={tdStyle}>
                        <input
                          style={inputStyle}
                          value={editForm.full_name || ''}
                          onChange={e => setEditForm({ ...editForm, full_name: e.target.value })}
                        />
                      </td>
                      <td style={tdStyle}>
                        <select
                          style={inputStyle}
                          value={editForm.role || 'user'}
                          onChange={e => setEditForm({ ...editForm, role: e.target.value })}
                        >
                          <option value="user">user</option>
                          <option value="admin">admin</option>
                        </select>
                      </td>
                      <td style={tdStyle}>
                        <select
                          style={inputStyle}
                          value={editForm.is_active ? 'true' : 'false'}
                          onChange={e => setEditForm({ ...editForm, is_active: e.target.value === 'true' })}
                        >
                          <option value="true">Sí</option>
                          <option value="false">No</option>
                        </select>
                      </td>
                      <td style={tdStyle}>{user.created_at ? new Date(user.created_at).toLocaleDateString() : '-'}</td>
                      <td style={tdStyle}>
                        <button onClick={() => saveEdit(user.id)} style={saveBtnStyle}>Guardar</button>
                        <button onClick={cancelEdit} style={cancelBtnStyle}>Cancelar</button>
                      </td>
                    </>
                  ) : (
                    <>
                      <td style={tdStyle}>{user.id}</td>
                      <td style={tdStyle}>{user.email}</td>
                      <td style={tdStyle}>{user.username}</td>
                      <td style={tdStyle}>{user.full_name || '-'}</td>
                      <td style={tdStyle}>{user.role}</td>
                      <td style={tdStyle}>
                        <button
                          onClick={() => toggleActive(user)}
                          style={{
                            background: user.is_active ? '#28a745' : '#dc3545',
                            color: '#fff',
                            border: 'none',
                            borderRadius: 4,
                            padding: '0.25rem 0.5rem',
                            cursor: 'pointer',
                            fontSize: '0.8rem',
                          }}
                        >
                          {user.is_active ? 'Activo' : 'Inactivo'}
                        </button>
                      </td>
                      <td style={tdStyle}>{user.created_at ? new Date(user.created_at).toLocaleDateString() : '-'}</td>
                      <td style={tdStyle}>
                        <button onClick={() => startEdit(user)} style={editBtnStyle}>Editar</button>
                        {deleteConfirm === user.id ? (
                          <>
                            <button onClick={() => confirmDelete(user.id)} style={confirmDelBtnStyle}>Confirmar</button>
                            <button onClick={() => setDeleteConfirm(null)} style={cancelBtnStyle}>No</button>
                          </>
                        ) : (
                          <button onClick={() => setDeleteConfirm(user.id)} style={delBtnStyle}>Eliminar</button>
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
const editBtnStyle = { background: '#007bff', color: '#fff', border: 'none', borderRadius: 4, padding: '0.25rem 0.75rem', cursor: 'pointer', fontSize: '0.8rem', marginRight: '0.25rem' };
const delBtnStyle = { background: '#dc3545', color: '#fff', border: 'none', borderRadius: 4, padding: '0.25rem 0.75rem', cursor: 'pointer', fontSize: '0.8rem' };
const confirmDelBtnStyle = { background: '#dc3545', color: '#fff', border: 'none', borderRadius: 4, padding: '0.25rem 0.75rem', cursor: 'pointer', fontSize: '0.8rem', marginRight: '0.25rem' };
const cancelBtnStyle = { background: '#6c757d', color: '#fff', border: 'none', borderRadius: 4, padding: '0.25rem 0.75rem', cursor: 'pointer', fontSize: '0.8rem', marginLeft: '0.25rem' };
const saveBtnStyle = { background: '#28a745', color: '#fff', border: 'none', borderRadius: 4, padding: '0.25rem 0.75rem', cursor: 'pointer', fontSize: '0.8rem' };