import { useCallback, useEffect, useMemo, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import {
  createAdminCrop,
  createAdminUser,
  deleteAdminCrop,
  deleteAdminUser,
  getAdminCrops,
  getAdminSummary,
  getAdminUsers,
  updateAdminCrop,
  updateAdminUser,
} from "../api/api";
import { parseJwt } from "../utils/auth";

const PAGE_SIZE = 25;

const emptyUserForm = {
  name: "",
  email: "",
  location: "",
  role: "user",
  password: "",
};

const emptyCropForm = {
  name: "",
  type: "",
  life_cycle: "anual",
  image_url: "",
  user_id: "",
  is_public: false,
  source_crop_id: "",
  irrigation: {
    watering_frequency: "daily",
    water_amount: 1,
    recommendations: "",
  },
  environmental: {
    sun_exposure: "full_sun",
    min_temp: 15,
    max_temp: 30,
    frost_tolerance: false,
  },
  calendar: {
    planting_start: "",
    planting_end: "",
    transplant_start: "",
    transplant_end: "",
    harvest_start: "",
    harvest_end: "",
    is_active: false,
    current_phase_index: 0,
    status: "draft",
  },
};

const toInputDate = (value) => (value ? String(value).slice(0, 10) : "");

const normalizeCropForm = (crop) => ({
  name: crop.name || "",
  type: crop.type || "",
  life_cycle: crop.life_cycle || "anual",
  image_url: crop.image_url || "",
  user_id: crop.user_id ?? "",
  is_public: Boolean(crop.is_public),
  source_crop_id: crop.source_crop_id ?? "",
  irrigation: {
    watering_frequency: crop.irrigation?.watering_frequency || "daily",
    water_amount: crop.irrigation?.water_amount ?? 1,
    recommendations: crop.irrigation?.recommendations || "",
  },
  environmental: {
    sun_exposure: crop.environmental?.sun_exposure || "full_sun",
    min_temp: crop.environmental?.min_temp ?? 15,
    max_temp: crop.environmental?.max_temp ?? 30,
    frost_tolerance: Boolean(crop.environmental?.frost_tolerance),
  },
  calendar: {
    planting_start: toInputDate(crop.calendar?.planting_start),
    planting_end: toInputDate(crop.calendar?.planting_end),
    transplant_start: toInputDate(crop.calendar?.transplant_start),
    transplant_end: toInputDate(crop.calendar?.transplant_end),
    harvest_start: toInputDate(crop.calendar?.harvest_start),
    harvest_end: toInputDate(crop.calendar?.harvest_end),
    is_active: Boolean(crop.calendar?.is_active),
    current_phase_index: crop.calendar?.current_phase_index ?? 0,
    status: crop.calendar?.status || "draft",
  },
});

const toNullableNumber = (value) => {
  if (value === "" || value === null || value === undefined) return null;
  return Number(value);
};

const toNullableDate = (value) => value || null;

const buildCropPayload = (form) => ({
  name: form.name.trim(),
  type: form.type.trim(),
  life_cycle: form.life_cycle,
  image_url: form.image_url.trim() || null,
  user_id: toNullableNumber(form.user_id),
  is_public: Boolean(form.is_public),
  source_crop_id: toNullableNumber(form.source_crop_id),
  irrigation: {
    watering_frequency: form.irrigation.watering_frequency,
    water_amount: Number(form.irrigation.water_amount || 0),
    recommendations: form.irrigation.recommendations,
  },
  environmental: {
    sun_exposure: form.environmental.sun_exposure,
    min_temp: Number(form.environmental.min_temp || 0),
    max_temp: Number(form.environmental.max_temp || 0),
    frost_tolerance: Boolean(form.environmental.frost_tolerance),
  },
  calendar: {
    planting_start: toNullableDate(form.calendar.planting_start),
    planting_end: toNullableDate(form.calendar.planting_end),
    transplant_start: toNullableDate(form.calendar.transplant_start),
    transplant_end: toNullableDate(form.calendar.transplant_end),
    harvest_start: toNullableDate(form.calendar.harvest_start),
    harvest_end: toNullableDate(form.calendar.harvest_end),
    is_active: Boolean(form.calendar.is_active),
    current_phase_index: Number(form.calendar.current_phase_index || 0),
    status: form.calendar.status || "draft",
  },
});

export default function Admin({ token }) {
  const location = useLocation();
  const navigate = useNavigate();
  const currentUser = useMemo(() => parseJwt(token), [token]);
  const view = location.pathname.includes("/admin/users")
    ? "users"
    : location.pathname.includes("/admin/crops")
      ? "crops"
      : "dashboard";

  const [summary, setSummary] = useState(null);
  const [users, setUsers] = useState([]);
  const [crops, setCrops] = useState([]);
  const [types, setTypes] = useState([]);
  const [userPage, setUserPage] = useState(1);
  const [cropPage, setCropPage] = useState(1);
  const [userPagination, setUserPagination] = useState({ total: 0, page: 1, total_pages: 1 });
  const [cropPagination, setCropPagination] = useState({ total: 0, page: 1, total_pages: 1 });
  const [userFilters, setUserFilters] = useState({ search: "", role: "" });
  const [cropFilters, setCropFilters] = useState({ name: "", type: "", user_id: "", kind: "" });
  const [userForm, setUserForm] = useState(emptyUserForm);
  const [cropForm, setCropForm] = useState(emptyCropForm);
  const [editingUserId, setEditingUserId] = useState(null);
  const [editingCropId, setEditingCropId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);

  const loadSummary = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setSummary(await getAdminSummary(token));
    } catch (err) {
      setError(err.message || "No se pudo cargar el resumen");
    } finally {
      setLoading(false);
    }
  }, [token]);

  const loadUsers = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getAdminUsers(token, { ...userFilters, page: userPage, page_size: PAGE_SIZE });
      setUsers(data.items || []);
      setUserPagination({ total: data.total || 0, page: data.page || 1, total_pages: data.total_pages || 1 });
    } catch (err) {
      setError(err.message || "No se pudieron cargar los usuarios");
    } finally {
      setLoading(false);
    }
  }, [token, userFilters, userPage]);

  const loadCrops = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getAdminCrops(token, { ...cropFilters, page: cropPage, page_size: PAGE_SIZE });
      setCrops(data.items || []);
      setTypes(data.types || []);
      setCropPagination({ total: data.total || 0, page: data.page || 1, total_pages: data.total_pages || 1 });
    } catch (err) {
      setError(err.message || "No se pudieron cargar los cultivos");
    } finally {
      setLoading(false);
    }
  }, [token, cropFilters, cropPage]);

  useEffect(() => {
    setMessage(null);
    if (view === "dashboard") loadSummary();
    if (view === "users") loadUsers();
    if (view === "crops") loadCrops();
  }, [view, loadSummary, loadUsers, loadCrops]);

  const updateUserFilter = (key, value) => {
    setUserFilters((prev) => ({ ...prev, [key]: value }));
    setUserPage(1);
  };

  const updateCropFilter = (key, value) => {
    setCropFilters((prev) => ({ ...prev, [key]: value }));
    setCropPage(1);
  };

  const startEditUser = (user) => {
    setEditingUserId(user.id);
    setUserForm({
      name: user.name || "",
      email: user.email || "",
      location: user.location || "",
      role: user.role || "user",
      password: "",
    });
    setMessage(null);
    setError(null);
  };

  const resetUserForm = () => {
    setEditingUserId(null);
    setUserForm(emptyUserForm);
  };

  const saveUser = async (event) => {
    event.preventDefault();
    setSaving(true);
    setError(null);
    setMessage(null);
    try {
      if (editingUserId) {
        await updateAdminUser(token, editingUserId, {
          name: userForm.name,
          email: userForm.email,
          location: userForm.location,
          role: userForm.role,
        });
        setMessage("Usuario actualizado correctamente");
      } else {
        await createAdminUser(token, userForm);
        setMessage("Usuario creado correctamente");
      }
      resetUserForm();
      await loadUsers();
    } catch (err) {
      setError(err.message || "No se pudo guardar el usuario");
    } finally {
      setSaving(false);
    }
  };

  const removeUser = async (user) => {
    if (!window.confirm(`¿Eliminar el usuario ${user.email}? Sus cultivos se conservaran sin propietario.`)) return;
    setSaving(true);
    setError(null);
    setMessage(null);
    try {
      await deleteAdminUser(token, user.id);
      setMessage("Usuario eliminado correctamente");
      await loadUsers();
    } catch (err) {
      setError(err.message || "No se pudo eliminar el usuario");
    } finally {
      setSaving(false);
    }
  };

  const startEditCrop = (crop) => {
    setEditingCropId(crop.id);
    setCropForm(normalizeCropForm(crop));
    setMessage(null);
    setError(null);
  };

  const resetCropForm = () => {
    setEditingCropId(null);
    setCropForm(emptyCropForm);
  };

  const updateCropForm = (key, value) => setCropForm((prev) => ({ ...prev, [key]: value }));
  const updateCropGroup = (group, key, value) =>
    setCropForm((prev) => ({ ...prev, [group]: { ...prev[group], [key]: value } }));

  const saveCrop = async (event) => {
    event.preventDefault();
    setSaving(true);
    setError(null);
    setMessage(null);
    try {
      const payload = buildCropPayload(cropForm);
      if (editingCropId) {
        await updateAdminCrop(token, editingCropId, payload);
        setMessage("Cultivo actualizado correctamente");
      } else {
        await createAdminCrop(token, payload);
        setMessage("Cultivo creado correctamente");
      }
      resetCropForm();
      await loadCrops();
    } catch (err) {
      setError(err.message || "No se pudo guardar el cultivo");
    } finally {
      setSaving(false);
    }
  };

  const removeCrop = async (crop) => {
    if (!window.confirm(`¿Eliminar definitivamente el cultivo ${crop.name}?`)) return;
    setSaving(true);
    setError(null);
    setMessage(null);
    try {
      await deleteAdminCrop(token, crop.id);
      setMessage("Cultivo eliminado correctamente");
      await loadCrops();
    } catch (err) {
      setError(err.message || "No se pudo eliminar el cultivo");
    } finally {
      setSaving(false);
    }
  };

  if (currentUser?.role !== "admin") {
    return (
      <main style={page}>
        <section style={panel}>
          <h1 style={title}>No autorizado</h1>
          <p style={muted}>Necesitas permisos de administrador para acceder a esta zona.</p>
          <button style={primaryButton} onClick={() => navigate("/dashboard")}>Volver</button>
        </section>
      </main>
    );
  }

  return (
    <main style={page}>
      <header style={header}>
        <div>
          <h1 style={title}>Administracion</h1>
          <p style={muted}>Gestion de usuarios, catalogo y cultivos asociados a usuarios.</p>
        </div>
        <nav style={tabs}>
          <Link style={tab(view === "dashboard")} to="/admin">Resumen</Link>
          <Link style={tab(view === "users")} to="/admin/users">Usuarios</Link>
          <Link style={tab(view === "crops")} to="/admin/crops">Cultivos</Link>
        </nav>
      </header>

      {message && <p style={success}>{message}</p>}
      {error && <p style={errorStyle}>{error}</p>}
      {loading && <p style={muted}>Cargando...</p>}

      {view === "dashboard" && (
        <section style={statsGrid}>
          {[
            ["Usuarios", summary?.total_users ?? 0],
            ["Cultivos totales", summary?.total_crops ?? 0],
            ["En catalogo", summary?.catalog_crops ?? 0],
            ["Asociados a usuarios", summary?.user_crops ?? 0],
          ].map(([label, value]) => (
            <article key={label} style={statCard}>
              <span style={muted}>{label}</span>
              <strong style={statNumber}>{value}</strong>
            </article>
          ))}
        </section>
      )}

      {view === "users" && (
        <section style={layout}>
          <form style={panel} onSubmit={saveUser}>
            <h2 style={sectionTitle}>{editingUserId ? "Editar usuario" : "Crear usuario"}</h2>
            <input style={input} placeholder="Nombre" value={userForm.name} onChange={(e) => setUserForm({ ...userForm, name: e.target.value })} required />
            <input style={input} type="email" placeholder="Email" value={userForm.email} onChange={(e) => setUserForm({ ...userForm, email: e.target.value })} required />
            <input style={input} placeholder="Ubicacion" value={userForm.location} onChange={(e) => setUserForm({ ...userForm, location: e.target.value })} />
            <select style={input} value={userForm.role} onChange={(e) => setUserForm({ ...userForm, role: e.target.value })}>
              <option value="user">Usuario</option>
              <option value="admin">Admin</option>
            </select>
            {!editingUserId && (
              <input style={input} type="password" placeholder="Password inicial" value={userForm.password} onChange={(e) => setUserForm({ ...userForm, password: e.target.value })} required minLength={4} />
            )}
            <div style={actions}>
              <button style={primaryButton} disabled={saving}>{saving ? "Guardando..." : "Guardar"}</button>
              {editingUserId && <button type="button" style={secondaryButton} onClick={resetUserForm}>Cancelar</button>}
            </div>
          </form>

          <section style={panelWide}>
            <div style={filters}>
              <input style={input} placeholder="Buscar usuario" value={userFilters.search} onChange={(e) => updateUserFilter("search", e.target.value)} />
              <select style={input} value={userFilters.role} onChange={(e) => updateUserFilter("role", e.target.value)}>
                <option value="">Todos los roles</option>
                <option value="user">Usuarios</option>
                <option value="admin">Admins</option>
              </select>
            </div>
            <div style={tableWrap}>
              <table style={table}>
                <thead><tr><th>ID</th><th>Nombre</th><th>Email</th><th>Rol</th><th>Creado</th><th>Acciones</th></tr></thead>
                <tbody>
                  {users.map((user) => (
                    <tr key={user.id}>
                      <td>{user.id}</td>
                      <td>{user.name}</td>
                      <td>{user.email}</td>
                      <td>{user.role}</td>
                      <td>{String(user.created_at).slice(0, 10)}</td>
                      <td style={rowActions}>
                        <button style={smallButton} onClick={() => startEditUser(user)}>Editar</button>
                        <button style={dangerSmallButton} onClick={() => removeUser(user)} disabled={saving || user.id === currentUser.user_id}>Eliminar</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <Pagination page={userPagination.page} totalPages={userPagination.total_pages} onPrev={() => setUserPage((p) => Math.max(p - 1, 1))} onNext={() => setUserPage((p) => Math.min(p + 1, userPagination.total_pages))} />
          </section>
        </section>
      )}

      {view === "crops" && (
        <section style={layout}>
          <form style={panel} onSubmit={saveCrop}>
            <h2 style={sectionTitle}>{editingCropId ? "Editar cultivo" : "Crear cultivo"}</h2>
            <input style={input} placeholder="Nombre" value={cropForm.name} onChange={(e) => updateCropForm("name", e.target.value)} required />
            <input style={input} placeholder="Tipo" value={cropForm.type} onChange={(e) => updateCropForm("type", e.target.value)} required />
            <select style={input} value={cropForm.life_cycle} onChange={(e) => updateCropForm("life_cycle", e.target.value)}>
              <option value="anual">Anual</option>
              <option value="bienal">Bienal</option>
              <option value="perenne">Perenne</option>
            </select>
            <input style={input} placeholder="URL imagen" value={cropForm.image_url} onChange={(e) => updateCropForm("image_url", e.target.value)} />
            <input style={input} type="number" placeholder="ID propietario vacio = global" value={cropForm.user_id} onChange={(e) => updateCropForm("user_id", e.target.value)} />
            <input style={input} type="number" placeholder="ID cultivo origen si es copia" value={cropForm.source_crop_id} onChange={(e) => updateCropForm("source_crop_id", e.target.value)} />
            <label style={checkLabel}><input type="checkbox" checked={cropForm.is_public} onChange={(e) => updateCropForm("is_public", e.target.checked)} /> En catalogo</label>

            <h3 style={miniTitle}>Riego y ambiente</h3>
            <select style={input} value={cropForm.irrigation.watering_frequency} onChange={(e) => updateCropGroup("irrigation", "watering_frequency", e.target.value)}>
              <option value="daily">Diario</option>
              <option value="2 times/week">2 veces por semana</option>
              <option value="3 times/week">3 veces por semana</option>
              <option value="weekly">Semanal</option>
            </select>
            <input style={input} type="number" step="0.1" placeholder="Agua" value={cropForm.irrigation.water_amount} onChange={(e) => updateCropGroup("irrigation", "water_amount", e.target.value)} />
            <textarea style={textarea} placeholder="Recomendaciones" value={cropForm.irrigation.recommendations} onChange={(e) => updateCropGroup("irrigation", "recommendations", e.target.value)} />
            <select style={input} value={cropForm.environmental.sun_exposure} onChange={(e) => updateCropGroup("environmental", "sun_exposure", e.target.value)}>
              <option value="full_sun">Sol pleno</option>
              <option value="partial">Sombra parcial</option>
              <option value="shade">Sombra</option>
            </select>
            <div style={twoCols}>
              <input style={input} type="number" placeholder="Temp min" value={cropForm.environmental.min_temp} onChange={(e) => updateCropGroup("environmental", "min_temp", e.target.value)} />
              <input style={input} type="number" placeholder="Temp max" value={cropForm.environmental.max_temp} onChange={(e) => updateCropGroup("environmental", "max_temp", e.target.value)} />
            </div>
            <label style={checkLabel}><input type="checkbox" checked={cropForm.environmental.frost_tolerance} onChange={(e) => updateCropGroup("environmental", "frost_tolerance", e.target.checked)} /> Tolerante a heladas</label>

            <h3 style={miniTitle}>Fases</h3>
            <div style={twoCols}>
              <input style={input} type="date" value={cropForm.calendar.planting_start} onChange={(e) => updateCropGroup("calendar", "planting_start", e.target.value)} />
              <input style={input} type="date" value={cropForm.calendar.transplant_start} onChange={(e) => updateCropGroup("calendar", "transplant_start", e.target.value)} />
              <input style={input} type="date" value={cropForm.calendar.harvest_start} onChange={(e) => updateCropGroup("calendar", "harvest_start", e.target.value)} />
              <select style={input} value={cropForm.calendar.status} onChange={(e) => updateCropGroup("calendar", "status", e.target.value)}>
                <option value="draft">Draft</option>
                <option value="active">Activo</option>
                <option value="completed">Completado</option>
              </select>
            </div>
            <p style={hint}>Para mantener la logica actual, el ano de las fases solo sirve como soporte tecnico; la app usa mes y quincena.</p>

            <div style={actions}>
              <button style={primaryButton} disabled={saving}>{saving ? "Guardando..." : "Guardar"}</button>
              {editingCropId && <button type="button" style={secondaryButton} onClick={resetCropForm}>Cancelar</button>}
            </div>
          </form>

          <section style={panelWide}>
            <div style={filters}>
              <input style={input} placeholder="Nombre" value={cropFilters.name} onChange={(e) => updateCropFilter("name", e.target.value)} />
              <select style={input} value={cropFilters.type} onChange={(e) => updateCropFilter("type", e.target.value)}>
                <option value="">Todos los tipos</option>
                {types.map((type) => <option key={type} value={type}>{type}</option>)}
              </select>
              <input style={input} type="number" placeholder="Propietario ID" value={cropFilters.user_id} onChange={(e) => updateCropFilter("user_id", e.target.value)} />
              <select style={input} value={cropFilters.kind} onChange={(e) => updateCropFilter("kind", e.target.value)}>
                <option value="">Todos</option>
                <option value="catalog">Catalogo</option>
                <option value="user">Usuario original</option>
                <option value="copy">Copia</option>
                <option value="global">Global sin propietario</option>
              </select>
            </div>
            <div style={cardsGrid}>
              {crops.map((crop) => (
                <article key={crop.id} style={cropCard}>
                  <h3 style={cropTitle}>{crop.name}</h3>
                  <p style={muted}>ID {crop.id} · {crop.type} · {crop.life_cycle}</p>
                  <p style={muted}>Propietario: {crop.user_id ?? "Global"} · Origen: {crop.source_crop_id ?? "Original"}</p>
                  <p style={muted}>{crop.is_public ? "Visible en catalogo" : "No publicado"}</p>
                  <div style={rowActions}>
                    <button style={smallButton} onClick={() => startEditCrop(crop)}>Editar</button>
                    <button style={dangerSmallButton} onClick={() => removeCrop(crop)} disabled={saving}>Eliminar</button>
                  </div>
                </article>
              ))}
            </div>
            <Pagination page={cropPagination.page} totalPages={cropPagination.total_pages} onPrev={() => setCropPage((p) => Math.max(p - 1, 1))} onNext={() => setCropPage((p) => Math.min(p + 1, cropPagination.total_pages))} />
          </section>
        </section>
      )}
    </main>
  );
}

function Pagination({ page, totalPages, onPrev, onNext }) {
  return (
    <div style={paginationBar}>
      <button type="button" style={secondaryButton} onClick={onPrev} disabled={page <= 1}>Anterior</button>
      <strong style={pageIndicator}>{page} / {totalPages}</strong>
      <button type="button" style={secondaryButton} onClick={onNext} disabled={page >= totalPages}>Siguiente</button>
    </div>
  );
}

const page = { minHeight: "100vh", padding: "32px", background: "#F4FBF6", fontFamily: "Inter, Arial, sans-serif" };
const header = { display: "flex", justifyContent: "space-between", gap: "20px", alignItems: "center", marginBottom: "24px", flexWrap: "wrap" };
const title = { margin: 0, color: "#1E4E2E", fontSize: "2.2rem" };
const sectionTitle = { margin: "0 0 14px", color: "#264F37" };
const miniTitle = { margin: "8px 0 0", color: "#2E593F", fontSize: "1rem" };
const muted = { color: "#4D6A5E", margin: "6px 0" };
const hint = { color: "#6B7F72", margin: 0, fontSize: "0.9rem" };
const tabs = { display: "flex", gap: "10px", flexWrap: "wrap" };
const tab = (active) => ({ padding: "10px 14px", borderRadius: "12px", textDecoration: "none", color: active ? "white" : "#2E7D32", background: active ? "#2E7D32" : "white", border: "1px solid #C8D8CB", fontWeight: 700 });
const layout = { display: "grid", gridTemplateColumns: "minmax(280px, 360px) 1fr", gap: "22px", alignItems: "start" };
const panel = { background: "white", borderRadius: "18px", padding: "22px", boxShadow: "0 14px 34px rgba(15, 23, 42, 0.08)", display: "flex", flexDirection: "column", gap: "12px" };
const panelWide = { ...panel, minWidth: 0 };
const statsGrid = { display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "18px" };
const statCard = { ...panel, gap: "8px" };
const statNumber = { color: "#1E4E2E", fontSize: "2rem" };
const input = { width: "100%", padding: "12px 14px", borderRadius: "12px", border: "1px solid #D7E7D8", background: "#F8FBF8", color: "#1F3D2E", boxSizing: "border-box" };
const textarea = { ...input, minHeight: "76px", resize: "vertical" };
const checkLabel = { display: "flex", gap: "8px", alignItems: "center", color: "#2E593F", fontWeight: 700 };
const actions = { display: "flex", gap: "10px", flexWrap: "wrap" };
const primaryButton = { padding: "12px 18px", borderRadius: "14px", border: "none", background: "#2F8F4C", color: "white", cursor: "pointer", fontWeight: 700 };
const secondaryButton = { padding: "10px 16px", borderRadius: "14px", border: "1px solid #C8D8CB", background: "white", color: "#2E7D32", cursor: "pointer", fontWeight: 700 };
const smallButton = { ...secondaryButton, padding: "8px 12px" };
const dangerSmallButton = { ...smallButton, color: "#B42318", border: "1px solid #F3B8B8", background: "#FFF7F7" };
const filters = { display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "12px", marginBottom: "16px" };
const tableWrap = { overflowX: "auto" };
const table = { width: "100%", borderCollapse: "collapse", color: "#1F3D2E" };
const rowActions = { display: "flex", gap: "8px", flexWrap: "wrap" };
const cardsGrid = { display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))", gap: "14px" };
const cropCard = { border: "1px solid #D7E7D8", borderRadius: "14px", padding: "16px", background: "#FBFEFB" };
const cropTitle = { margin: 0, color: "#15452A" };
const twoCols = { display: "grid", gridTemplateColumns: "repeat(2, minmax(0, 1fr))", gap: "10px" };
const paginationBar = { marginTop: "18px", display: "flex", justifyContent: "center", alignItems: "center", gap: "12px" };
const pageIndicator = { color: "#2E593F" };
const success = { color: "#2E7D32", fontWeight: 700 };
const errorStyle = { color: "#9B2C2C", fontWeight: 700 };
