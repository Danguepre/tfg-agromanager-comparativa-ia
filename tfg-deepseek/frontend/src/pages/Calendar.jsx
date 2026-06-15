import { useState, useEffect } from 'react';
import { apiGet, apiPost, apiPut, apiDelete, normalizeList } from '../api/api';

export default function CalendarPage() {
  const [calendars, setCalendars] = useState([]);
  const [events, setEvents] = useState([]);
  const [userCrops, setUserCrops] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  // Create form state
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [createForm, setCreateForm] = useState({
    crop_id: '',
    planting_start: '',
    planting_end: '',
    transplant_start: '',
    transplant_end: '',
    harvest_start: '',
    harvest_end: '',
    notes: '',
  });
  const [creating, setCreating] = useState(false);

  // Edit form state
  const [editingId, setEditingId] = useState(null);
  const [editForm, setEditForm] = useState({});

  const PHASE_LABELS = ['Siembra', 'Trasplante', 'Cosecha'];

  async function load() {
    try {
      let calData = [];
      let evtData = [];
      let cropsData = [];

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

      try {
        cropsData = await apiGet('/crops/my');
        cropsData = normalizeList(cropsData);
      } catch (e) {
        // Puede no haber cultivos
      }

      setCalendars(calData);
      setEvents(evtData);
      setUserCrops(cropsData);
      setError('');
    } catch (err) {
      setError(err.message || 'Error al cargar datos');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  function getCropName(cropId) {
    const crop = userCrops.find(c => c.id === cropId);
    return crop ? crop.name : `Cultivo #${cropId}`;
  }

  // ── Create ──

  function resetCreateForm() {
    setCreateForm({
      crop_id: '',
      planting_start: '',
      planting_end: '',
      transplant_start: '',
      transplant_end: '',
      harvest_start: '',
      harvest_end: '',
      notes: '',
    });
    setShowCreateForm(false);
  }

  async function handleCreate() {
    setError('');
    setSuccessMsg('');
    setCreating(true);

    const selectedCropId = parseInt(createForm.crop_id, 10);
    if (isNaN(selectedCropId)) {
      setError('Debes seleccionar un cultivo');
      setCreating(false);
      return;
    }

    // Build payload: only send non-empty fields, send null for empty date strings
    const payload = {
      crop_id: selectedCropId,
    };

    if (createForm.planting_start) payload.planting_start = createForm.planting_start;
    if (createForm.planting_end) payload.planting_end = createForm.planting_end;
    if (createForm.transplant_start) payload.transplant_start = createForm.transplant_start;
    if (createForm.transplant_end) payload.transplant_end = createForm.transplant_end;
    if (createForm.harvest_start) payload.harvest_start = createForm.harvest_start;
    if (createForm.harvest_end) payload.harvest_end = createForm.harvest_end;
    if (createForm.notes) payload.notes = createForm.notes;

    try {
      await apiPost('/calendar/', payload);
      setSuccessMsg('Calendario creado correctamente');
      resetCreateForm();
      load();
    } catch (err) {
      // FastAPI 422 errors often have detail in the error message
      setError(err.message || 'Error al crear calendario');
    } finally {
      setCreating(false);
    }
  }

  // ── Edit ──

  function startEdit(cal) {
    setEditingId(cal.id);
    setEditForm({
      planting_start: cal.planting_start || '',
      planting_end: cal.planting_end || '',
      transplant_start: cal.transplant_start || '',
      transplant_end: cal.transplant_end || '',
      harvest_start: cal.harvest_start || '',
      harvest_end: cal.harvest_end || '',
      notes: cal.notes || '',
    });
  }

  function cancelEdit() {
    setEditingId(null);
    setEditForm({});
  }

  async function handleSaveEdit(cal) {
    setError('');
    setSuccessMsg('');

    const payload = {};
    if (editForm.planting_start !== cal.planting_start) {
      payload.planting_start = editForm.planting_start || null;
    }
    if (editForm.planting_end !== cal.planting_end) {
      payload.planting_end = editForm.planting_end || null;
    }
    if (editForm.transplant_start !== cal.transplant_start) {
      payload.transplant_start = editForm.transplant_start || null;
    }
    if (editForm.transplant_end !== cal.transplant_end) {
      payload.transplant_end = editForm.transplant_end || null;
    }
    if (editForm.harvest_start !== cal.harvest_start) {
      payload.harvest_start = editForm.harvest_start || null;
    }
    if (editForm.harvest_end !== cal.harvest_end) {
      payload.harvest_end = editForm.harvest_end || null;
    }
    if (editForm.notes !== (cal.notes || '')) {
      payload.notes = editForm.notes || null;
    }

    try {
      await apiPut(`/calendar/${cal.id}`, payload);
      setSuccessMsg('Calendario actualizado correctamente');
      setEditingId(null);
      setEditForm({});
      load();
    } catch (err) {
      setError(err.message || 'Error al actualizar calendario');
    }
  }

  // ── Activate ──

  async function handleActivate(cal) {
    setError('');
    setSuccessMsg('');
    try {
      await apiPost(`/calendar/crop/${cal.crop_id}/activate`);
      setSuccessMsg('Calendario activado correctamente');
      load();
    } catch (err) {
      setError(err.message || 'Error al activar calendario');
    }
  }

  // ── Advance phase ──

  async function handleAdvance(cal) {
    setError('');
    setSuccessMsg('');
    try {
      await apiPost(`/calendar/crop/${cal.crop_id}/advance`);
      setSuccessMsg('Fase avanzada correctamente');
      load();
    } catch (err) {
      setError(err.message || 'Error al avanzar fase');
    }
  }

  // ── Delete ──

  async function handleDelete(cal) {
    if (!window.confirm(`¿Eliminar calendario de "${getCropName(cal.crop_id)}"? Esta acción no se puede deshacer.`)) {
      return;
    }
    setError('');
    setSuccessMsg('');
    try {
      await apiDelete(`/calendar/${cal.id}`);
      setSuccessMsg('Calendario eliminado correctamente');
      load();
    } catch (err) {
      setError(err.message || 'Error al eliminar calendario');
    }
  }

  // ── Helpers ──

  function statusBadge(cal) {
    let bg, color;
    if (cal.status === 'completed') {
      bg = '#d4edda'; color = '#155724';
    } else if (cal.is_active) {
      bg = '#cce5ff'; color = '#004085';
    } else {
      bg = '#f5f5f5'; color = '#888';
    }
    return { background: bg, color, padding: '0.15rem 0.5rem', borderRadius: 4, fontSize: '0.75rem', fontWeight: 600 };
  }

  function phaseColor(index) {
    if (index === 0) return '#4caf50';
    if (index === 1) return '#ff9800';
    return '#f44336';
  }

  const hasCropsWithoutCalendar = userCrops.some(
    crop => !calendars.some(cal => cal.crop_id === crop.id)
  );

  // ── Render ──

  if (loading) return <div style={{ padding: '2rem', textAlign: 'center' }}>Cargando calendario...</div>;

  return (
    <div style={{ padding: '1.5rem', maxWidth: 1000, margin: '0 auto' }}>
      <h2 style={{ color: '#1a6b3c', marginBottom: '1.5rem' }}>Calendario Agrícola</h2>

      {successMsg && (
        <div style={{ background: '#d4edda', color: '#155724', padding: '0.75rem', borderRadius: 4, marginBottom: '1rem' }}>
          {successMsg}
        </div>
      )}

      {error && (
        <div style={{ background: '#f8d7da', color: '#721c24', padding: '0.75rem', borderRadius: 4, marginBottom: '1rem', wordBreak: 'break-word' }}>
          {error}
          <button onClick={() => setError('')} style={{ marginLeft: '1rem', background: 'none', border: 'none', cursor: 'pointer', color: '#721c24', float: 'right' }}>✕</button>
        </div>
      )}

      {/* Create form */}
      {showCreateForm && (
        <div style={{
          background: '#fff', borderRadius: 8, padding: '1rem', marginBottom: '1.5rem',
          boxShadow: '0 1px 4px rgba(0,0,0,0.1)',
        }}>
          <h3 style={{ color: '#1a6b3c', marginBottom: '0.75rem' }}>Nuevo Calendario</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <div>
              <label style={{ ...labelStyle }}>Cultivo obligatorio:</label>
              <select
                value={createForm.crop_id}
                onChange={e => setCreateForm({ ...createForm, crop_id: e.target.value })}
                style={{ ...inputStyle, minWidth: 250 }}
              >
                <option value="">-- Seleccionar cultivo --</option>
                {userCrops.map(crop => (
                  <option key={crop.id} value={crop.id}
                    disabled={calendars.some(cal => cal.crop_id === crop.id)}
                  >
                    {crop.name} {calendars.some(cal => cal.crop_id === crop.id) ? '(ya tiene calendario)' : ''}
                  </option>
                ))}
              </select>
            </div>
            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', alignItems: 'center' }}>
              <label style={labelStyle}>Siembra inicio:</label>
              <input type="date" style={dateInputStyle} value={createForm.planting_start}
                onChange={e => setCreateForm({ ...createForm, planting_start: e.target.value })} />
              <label style={labelStyle}>Siembra fin:</label>
              <input type="date" style={dateInputStyle} value={createForm.planting_end}
                onChange={e => setCreateForm({ ...createForm, planting_end: e.target.value })} />
            </div>
            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', alignItems: 'center' }}>
              <label style={labelStyle}>Trasplante inicio:</label>
              <input type="date" style={dateInputStyle} value={createForm.transplant_start}
                onChange={e => setCreateForm({ ...createForm, transplant_start: e.target.value })} />
              <label style={labelStyle}>Trasplante fin:</label>
              <input type="date" style={dateInputStyle} value={createForm.transplant_end}
                onChange={e => setCreateForm({ ...createForm, transplant_end: e.target.value })} />
            </div>
            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', alignItems: 'center' }}>
              <label style={labelStyle}>Cosecha inicio:</label>
              <input type="date" style={dateInputStyle} value={createForm.harvest_start}
                onChange={e => setCreateForm({ ...createForm, harvest_start: e.target.value })} />
              <label style={labelStyle}>Cosecha fin:</label>
              <input type="date" style={dateInputStyle} value={createForm.harvest_end}
                onChange={e => setCreateForm({ ...createForm, harvest_end: e.target.value })} />
            </div>
            <div>
              <label style={labelStyle}>Notas:</label>
              <textarea style={{ ...inputStyle, minHeight: 50, resize: 'vertical' }} value={createForm.notes}
                onChange={e => setCreateForm({ ...createForm, notes: e.target.value })} />
            </div>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button onClick={handleCreate} disabled={creating || !createForm.crop_id} style={{
                ...baseBtn, background: '#28a745', color: '#fff',
                opacity: (creating || !createForm.crop_id) ? 0.6 : 1,
              }}>
                {creating ? 'Creando...' : 'Crear calendario'}
              </button>
              <button onClick={resetCreateForm} style={{ ...baseBtn, background: '#6c757d', color: '#fff' }}>
                Cancelar
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Calendar list */}
      {calendars.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: '#888' }}>
          <p>No hay calendarios agrícolas.</p>
          <p>Crea un calendario para empezar a gestionar el ciclo de tus cultivos.</p>
          {userCrops.length === 0 ? (
            <p>Primero necesitas tener <a href="/crops" style={{ color: '#1a6b3c' }}>cultivos propios</a>.</p>
          ) : (
            <button onClick={() => setShowCreateForm(true)} style={{
              ...baseBtn, background: '#1a6b3c', color: '#fff', marginTop: '0.5rem',
            }}>
              + Crear calendario
            </button>
          )}
        </div>
      ) : (
        <>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h3 style={{ margin: 0 }}>Calendarios ({calendars.length})</h3>
            {hasCropsWithoutCalendar && (
              <button onClick={() => {
                resetCreateForm();
                setShowCreateForm(true);
              }} style={{
                ...baseBtn, background: '#1a6b3c', color: '#fff',
              }}>
                + Nuevo calendario
              </button>
            )}
          </div>

          <div style={{ display: 'grid', gap: '1rem' }}>
            {calendars.map((cal) => (
              <div key={cal.id} style={{
                background: '#fff', borderRadius: 8, padding: '1rem',
                boxShadow: '0 1px 4px rgba(0,0,0,0.1)',
              }}>
                {editingId === cal.id ? (
                  /* ── Edit mode ── */
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', alignItems: 'center' }}>
                      <label style={labelStyle}>Siembra inicio:</label>
                      <input type="date" style={dateInputStyle} value={editForm.planting_start || ''}
                        onChange={e => setEditForm({ ...editForm, planting_start: e.target.value })} />
                      <label style={labelStyle}>Siembra fin:</label>
                      <input type="date" style={dateInputStyle} value={editForm.planting_end || ''}
                        onChange={e => setEditForm({ ...editForm, planting_end: e.target.value })} />
                    </div>
                    <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', alignItems: 'center' }}>
                      <label style={labelStyle}>Trasplante inicio:</label>
                      <input type="date" style={dateInputStyle} value={editForm.transplant_start || ''}
                        onChange={e => setEditForm({ ...editForm, transplant_start: e.target.value })} />
                      <label style={labelStyle}>Trasplante fin:</label>
                      <input type="date" style={dateInputStyle} value={editForm.transplant_end || ''}
                        onChange={e => setEditForm({ ...editForm, transplant_end: e.target.value })} />
                    </div>
                    <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', alignItems: 'center' }}>
                      <label style={labelStyle}>Cosecha inicio:</label>
                      <input type="date" style={dateInputStyle} value={editForm.harvest_start || ''}
                        onChange={e => setEditForm({ ...editForm, harvest_start: e.target.value })} />
                      <label style={labelStyle}>Cosecha fin:</label>
                      <input type="date" style={dateInputStyle} value={editForm.harvest_end || ''}
                        onChange={e => setEditForm({ ...editForm, harvest_end: e.target.value })} />
                    </div>
                    <div>
                      <label style={labelStyle}>Notas:</label>
                      <textarea style={{ ...inputStyle, minHeight: 50, resize: 'vertical' }} value={editForm.notes || ''}
                        onChange={e => setEditForm({ ...editForm, notes: e.target.value })} />
                    </div>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <button onClick={() => handleSaveEdit(cal)} style={{ ...baseBtn, background: '#28a745', color: '#fff' }}>
                        Guardar cambios
                      </button>
                      <button onClick={cancelEdit} style={{ ...baseBtn, background: '#6c757d', color: '#fff' }}>
                        Cancelar
                      </button>
                    </div>
                  </div>
                ) : (
                  /* ── View mode ── */
                  <>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '0.5rem' }}>
                      <div>
                        <strong style={{ color: '#1a6b3c', fontSize: '1.05rem' }}>
                          {getCropName(cal.crop_id)}
                        </strong>
                        <span style={statusBadge(cal)}>
                          {cal.status === 'completed' ? 'Completado' : cal.is_active ? 'Activo' : 'Borrador'}
                        </span>
                        {cal.status === 'active' && (
                          <span style={{
                            marginLeft: '0.5rem', padding: '0.15rem 0.5rem', borderRadius: 4,
                            fontSize: '0.75rem', fontWeight: 600,
                            background: phaseColor(cal.current_phase_index) + '22',
                            color: phaseColor(cal.current_phase_index),
                          }}>
                            {PHASE_LABELS[cal.current_phase_index] || 'Fase ' + cal.current_phase_index}
                          </span>
                        )}
                      </div>
                      <div style={{ display: 'flex', gap: '0.35rem', flexWrap: 'wrap' }}>
                        <button onClick={() => startEdit(cal)} style={{ ...baseBtn, background: '#007bff', color: '#fff' }}>
                          Editar fechas
                        </button>
                        {cal.status === 'draft' && (
                          <button onClick={() => handleActivate(cal)} style={{ ...baseBtn, background: '#28a745', color: '#fff' }}>
                            Activar
                          </button>
                        )}
                        {cal.is_active && cal.status !== 'completed' && (
                          <button onClick={() => handleAdvance(cal)} style={{ ...baseBtn, background: '#ff9800', color: '#fff' }}>
                            {cal.current_phase_index < 2
                              ? `Avanzar a ${PHASE_LABELS[cal.current_phase_index + 1]}`
                              : 'Completar'}
                          </button>
                        )}
                        <button onClick={() => handleDelete(cal)} style={{ ...baseBtn, background: '#dc3545', color: '#fff' }}>
                          Eliminar
                        </button>
                      </div>
                    </div>

                    <div style={{ marginTop: '0.75rem', display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '0.5rem', fontSize: '0.9rem' }}>
                      <div style={{ background: '#f9f9f9', padding: '0.5rem', borderRadius: 6, borderLeft: `3px solid ${phaseColor(0)}` }}>
                        <div style={{ fontWeight: 600, fontSize: '0.8rem', color: '#666', marginBottom: '0.2rem' }}>🌱 Siembra</div>
                        {cal.planting_start ? (
                          <span>{cal.planting_start} → {cal.planting_end || '—'}</span>
                        ) : (
                          <span style={{ color: '#aaa' }}>No definida</span>
                        )}
                      </div>
                      <div style={{ background: '#f9f9f9', padding: '0.5rem', borderRadius: 6, borderLeft: `3px solid ${phaseColor(1)}` }}>
                        <div style={{ fontWeight: 600, fontSize: '0.8rem', color: '#666', marginBottom: '0.2rem' }}>🌿 Trasplante</div>
                        {cal.transplant_start ? (
                          <span>{cal.transplant_start} → {cal.transplant_end || '—'}</span>
                        ) : (
                          <span style={{ color: '#aaa' }}>No definido</span>
                        )}
                      </div>
                      <div style={{ background: '#f9f9f9', padding: '0.5rem', borderRadius: 6, borderLeft: `3px solid ${phaseColor(2)}` }}>
                        <div style={{ fontWeight: 600, fontSize: '0.8rem', color: '#666', marginBottom: '0.2rem' }}>🧺 Cosecha</div>
                        {cal.harvest_start ? (
                          <span>{cal.harvest_start} → {cal.harvest_end || '—'}</span>
                        ) : (
                          <span style={{ color: '#aaa' }}>No definida</span>
                        )}
                      </div>
                    </div>

                    {cal.notes && (
                      <p style={{ fontSize: '0.85rem', color: '#888', marginTop: '0.5rem', fontStyle: 'italic' }}>
                        📝 {cal.notes}
                      </p>
                    )}
                  </>
                )}
              </div>
            ))}
          </div>

          {/* Events section */}
          {events.length > 0 && (
            <section style={{ marginTop: '2rem' }}>
              <h3>Eventos activos ({events.length})</h3>
              <div style={{ display: 'grid', gap: '0.5rem', marginTop: '0.5rem' }}>
                {events.map((evt, idx) => (
                  <div key={idx} style={{
                    background: '#fff', borderRadius: 8, padding: '0.75rem 1rem',
                    boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
                    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  }}>
                    <span>
                      <span style={{
                        display: 'inline-block', width: 8, height: 8, borderRadius: '50%',
                        background: phaseColor(evt.phase_index),
                        marginRight: 8,
                      }} />
                      {evt.label || `${evt.phase} - ${evt.fortnight === 1 ? '1ª' : '2ª'} quincena`}
                    </span>
                    <span style={{ fontSize: '0.875rem', color: '#888' }}>
                      {evt.month === 1 ? 'Enero' : evt.month === 2 ? 'Febrero' : evt.month === 3 ? 'Marzo' :
                       evt.month === 4 ? 'Abril' : evt.month === 5 ? 'Mayo' : evt.month === 6 ? 'Junio' :
                       evt.month === 7 ? 'Julio' : evt.month === 8 ? 'Agosto' : evt.month === 9 ? 'Septiembre' :
                       evt.month === 10 ? 'Octubre' : evt.month === 11 ? 'Noviembre' : 'Diciembre'}
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

// ── Shared styles ──

const baseBtn = { border: 'none', borderRadius: 4, padding: '0.35rem 0.8rem', cursor: 'pointer', fontSize: '0.875rem', textDecoration: 'none', display: 'inline-block' };
const labelStyle = { fontSize: '0.8rem', fontWeight: 600, color: '#555', minWidth: 95 };
const inputStyle = {
  padding: '0.35rem 0.6rem', border: '1px solid #ccc', borderRadius: 4,
  fontSize: '0.875rem', minWidth: 200, boxSizing: 'border-box',
};
const dateInputStyle = {
  padding: '0.35rem 0.6rem', border: '1px solid #ccc', borderRadius: 4,
  fontSize: '0.875rem', minWidth: 140, boxSizing: 'border-box',
};