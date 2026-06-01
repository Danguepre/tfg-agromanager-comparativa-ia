import React, { createContext, useContext, useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  apiRequest,
  clearSession,
  deleteAdminCrop,
  deleteAdminTask,
  deleteAdminUser,
  getAdminCrop,
  getAdminCrops,
  getAdminSummary,
  getAdminTask,
  getAdminTasks,
  getAdminUser,
  getAdminUsers,
  getStoredUser,
  getToken,
  loginRequest,
  normalizeList,
  registerRequest,
  saveSession,
  updateAdminCrop,
  updateAdminTask,
  updateAdminUser,
} from "./api";
import "./styles.css";

const AuthContext = createContext(null);

const routes = {
  "/": "Dashboard",
  "/crops": "Mis cultivos",
  "/catalog": "Catalogo",
  "/calendar": "Calendario",
  "/tasks": "Tareas",
  "/profile": "Sesion",
};

const adminRoutes = {
  "/admin/dashboard": "Panel admin",
  "/admin/users": "Usuarios",
  "/admin/crops": "Cultivos",
  "/admin/tasks": "Tareas admin",
};

function navigate(path) {
  window.history.pushState({}, "", path);
  window.dispatchEvent(new PopStateEvent("popstate"));
}

function usePath() {
  const [path, setPath] = useState(window.location.pathname);
  useEffect(() => {
    const onChange = () => setPath(window.location.pathname);
    window.addEventListener("popstate", onChange);
    return () => window.removeEventListener("popstate", onChange);
  }, []);
  return path;
}

function useAuth() {
  return useContext(AuthContext);
}

function userFromToken(token) {
  if (!token) return null;
  try {
    const payloadPart = token.split(".")[1];
    const normalized = payloadPart.replace(/-/g, "+").replace(/_/g, "/");
    const payload = JSON.parse(window.atob(normalized.padEnd(Math.ceil(normalized.length / 4) * 4, "=")));
    return { id: Number(payload.sub), role: payload.role };
  } catch {
    return null;
  }
}

function AuthProvider({ children }) {
  const [token, setToken] = useState(getToken());
  const [user, setUser] = useState(() => getStoredUser() || userFromToken(getToken()));

  useEffect(() => {
    const onUnauthorized = () => {
      setToken(null);
      setUser(null);
      navigate("/login");
    };
    window.addEventListener("agromanager:unauthorized", onUnauthorized);
    return () => window.removeEventListener("agromanager:unauthorized", onUnauthorized);
  }, []);

  useEffect(() => {
    if (!token || user?.role) return;
    let active = true;
    apiRequest("/users/")
      .then((payload) => {
        if (!active) return;
        const tokenUser = userFromToken(token);
        const users = normalizeList(payload);
        const currentUser = users.find((item) => item.id === tokenUser?.id) || users[0] || tokenUser || null;
        if (currentUser) {
          localStorage.setItem("agromanager_user", JSON.stringify(currentUser));
          setUser(currentUser);
        }
      })
      .catch(() => {
        if (active && !user) setUser(null);
      });
    return () => {
      active = false;
    };
  }, [token, user]);

  const value = useMemo(
    () => ({
      token,
      user,
      isAuthenticated: Boolean(token),
      isAdmin: user?.role === "admin",
      roleKnown: !token || Boolean(user?.role),
      setSession(nextToken, nextUser = null) {
        saveSession(nextToken, nextUser);
        setToken(nextToken);
        setUser(nextUser);
      },
      setUser(nextUser) {
        if (nextUser) localStorage.setItem("agromanager_user", JSON.stringify(nextUser));
        setUser(nextUser);
      },
      logout() {
        clearSession();
        setToken(null);
        setUser(null);
        navigate("/login");
      },
    }),
    [token, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

function useApiData(loader, deps = []) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError("");
    loader()
      .then((payload) => {
        if (active) setData(payload);
      })
      .catch((err) => {
        if (active) setError(err.message || "No se pudo cargar la informacion");
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, deps);

  return { data, setData, loading, error, setError };
}

function App() {
  return (
    <AuthProvider>
      <Router />
    </AuthProvider>
  );
}

function Router() {
  const path = usePath();
  const auth = useAuth();
  const publicRoute = path === "/login" || path === "/register";
  const adminRoute = path === "/admin" || path.startsWith("/admin/");

  useEffect(() => {
    if (!auth.isAuthenticated && !publicRoute) navigate("/login");
    if (auth.isAuthenticated && publicRoute) navigate("/");
  }, [auth.isAuthenticated, publicRoute]);

  if (!auth.isAuthenticated && !publicRoute) return null;
  if (auth.isAuthenticated && adminRoute && !auth.roleKnown) return <Shell><p className="state">Comprobando permisos de administrador...</p></Shell>;

  if (path === "/login") return <LoginPage />;
  if (path === "/register") return <RegisterPage />;

  return (
    <Shell>
      {adminRoute && !auth.isAdmin && <AdminForbidden />}
      {auth.isAdmin && path === "/admin" && <AdminDashboardPage />}
      {auth.isAdmin && path === "/admin/dashboard" && <AdminDashboardPage />}
      {auth.isAdmin && path === "/admin/users" && <AdminUsersPage />}
      {auth.isAdmin && path === "/admin/crops" && <AdminCropsPage />}
      {auth.isAdmin && path === "/admin/tasks" && <AdminTasksPage />}
      {!adminRoute && (
        <>
      {path === "/" && <DashboardPage />}
      {path === "/crops" && <MyCropsPage />}
      {path === "/catalog" && <CatalogPage />}
      {path.startsWith("/crops/") && <CropDetailPage cropId={Number(path.split("/")[2])} />}
      {path === "/calendar" && <CalendarPage />}
      {path === "/tasks" && <TasksPage />}
      {path === "/profile" && <ProfilePage />}
      {!routes[path] && !path.startsWith("/crops/") && <NotFoundPage />}
        </>
      )}
      {adminRoute && auth.isAdmin && !adminRoutes[path] && path !== "/admin" && <NotFoundPage />}
    </Shell>
  );
}

function Shell({ children }) {
  const auth = useAuth();
  return (
    <div className="app-layout">
      <aside className="sidebar">
        <button className="brand" type="button" onClick={() => navigate("/")}>
          <span>AgroManager</span>
        </button>
        <nav className="nav-list">
          {Object.entries(routes).map(([path, label]) => (
            <button key={path} type="button" onClick={() => navigate(path)}>
              {label}
            </button>
          ))}
          {auth.isAdmin && (
            <button type="button" onClick={() => navigate("/admin/dashboard")}>
              Admin
            </button>
          )}
        </nav>
        <button className="logout-button" type="button" onClick={auth.logout}>
          Cerrar sesion
        </button>
      </aside>
      <main className="content">{children}</main>
    </div>
  );
}

function AuthCard({ title, subtitle, children }) {
  return (
    <main className="auth-page">
      <section className="auth-card">
        <p className="eyebrow">AgroManager</p>
        <h1>{title}</h1>
        <p className="muted">{subtitle}</p>
        {children}
      </section>
    </main>
  );
}

function LoginPage() {
  const auth = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function onSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const token = await loginRequest(email, password);
      const tokenUser = userFromToken(token.access_token);
      auth.setSession(token.access_token, tokenUser);
      try {
        const users = normalizeList(await apiRequest("/users/"));
        auth.setUser(users.find((item) => item.id === tokenUser?.id) || users[0] || tokenUser);
      } catch {
        auth.setUser({ ...tokenUser, email });
      }
      navigate("/");
    } catch (err) {
      setError(err.message || "No se pudo iniciar sesion");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthCard title="Iniciar sesion" subtitle="Accede con el email y la contrasena de tu cuenta.">
      <form className="form" onSubmit={onSubmit}>
        <label>
          Email
          <input value={email} onChange={(event) => setEmail(event.target.value)} type="email" required />
        </label>
        <label>
          Contrasena
          <input value={password} onChange={(event) => setPassword(event.target.value)} type="password" required />
        </label>
        {error && <p className="alert">{error}</p>}
        <button className="primary-button" type="submit" disabled={loading}>
          {loading ? "Entrando..." : "Entrar"}
        </button>
      </form>
      <button className="link-button" type="button" onClick={() => navigate("/register")}>
        Crear cuenta
      </button>
    </AuthCard>
  );
}

function RegisterPage() {
  const [form, setForm] = useState({ username: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function update(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function onSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      await registerRequest({ ...form, role: "user" });
      navigate("/login");
    } catch (err) {
      setError(err.message || "No se pudo crear la cuenta");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthCard title="Crear cuenta" subtitle="Registra una cuenta de usuario para gestionar tus cultivos.">
      <form className="form" onSubmit={onSubmit}>
        <label>
          Nombre de usuario
          <input value={form.username} onChange={(event) => update("username", event.target.value)} required minLength={3} />
        </label>
        <label>
          Email
          <input value={form.email} onChange={(event) => update("email", event.target.value)} type="email" required />
        </label>
        <label>
          Contrasena
          <input value={form.password} onChange={(event) => update("password", event.target.value)} type="password" required minLength={8} />
        </label>
        {error && <p className="alert">{error}</p>}
        <button className="primary-button" type="submit" disabled={loading}>
          {loading ? "Creando..." : "Registrarme"}
        </button>
      </form>
      <button className="link-button" type="button" onClick={() => navigate("/login")}>
        Ya tengo cuenta
      </button>
    </AuthCard>
  );
}

function PageHeader({ title, description, action }) {
  return (
    <header className="page-header">
      <div>
        <h1>{title}</h1>
        {description && <p>{description}</p>}
      </div>
      {action}
    </header>
  );
}

function StateBlock({ loading, error, empty, children }) {
  if (loading) return <p className="state">Cargando...</p>;
  if (error) return <p className="alert">{error}</p>;
  if (empty) return <p className="state">Todavia no hay datos para mostrar.</p>;
  return children;
}

function DashboardPage() {
  const { data, loading, error } = useApiData(() => apiRequest("/dashboard/summary"), []);
  const tasks = data?.tasks_by_status || { pending: 0, completed: 0 };
  const events = normalizeList(data?.upcoming_calendar_events);

  return (
    <>
      <PageHeader title="Dashboard" description="Resumen operativo de tus cultivos, tareas y calendarios." />
      <StateBlock loading={loading} error={error} empty={!data}>
        <section className="metric-grid">
          <Metric label="Cultivos" value={data?.total_personal_crops ?? 0} />
          <Metric label="Tareas pendientes" value={tasks.pending ?? 0} />
          <Metric label="Tareas completadas" value={tasks.completed ?? 0} />
          <Metric label="Calendarios activos" value={data?.active_calendars_total ?? 0} />
          <Metric label="Publicos" value={data?.total_public_crops ?? 0} />
          <Metric label="Copias" value={data?.total_copied_crops ?? 0} />
        </section>
        <section className="section">
          <h2>Proximos eventos</h2>
          {events.length === 0 ? (
            <p className="state">No hay eventos activos.</p>
          ) : (
            <div className="list">
              {events.map((event) => (
                <article className="list-item" key={`${event.calendar_id}-${event.phase_index}`}>
                  <strong>{event.crop_name}</strong>
                  <span>{event.phase}</span>
                  <small>
                    Mes {event.start_month}, quincena {event.start_fortnight} a mes {event.end_month}, quincena {event.end_fortnight}
                  </small>
                </article>
              ))}
            </div>
          )}
        </section>
      </StateBlock>
    </>
  );
}

function Metric({ label, value }) {
  return (
    <article className="metric">
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
  );
}

function CropCard({ crop, action }) {
  return (
    <article className="item-card">
      <div>
        <h3>{crop.name}</h3>
        <p>{crop.crop_type || "Sin tipo definido"}</p>
      </div>
      {crop.description && <p className="muted">{crop.description}</p>}
      <div className="button-row">
        <button type="button" onClick={() => navigate(`/crops/${crop.id}`)}>
          Ver detalle
        </button>
        {action}
      </div>
    </article>
  );
}

function MyCropsPage() {
  const { data, loading, error } = useApiData(() => apiRequest("/crops/my"), []);
  const crops = normalizeList(data);
  return (
    <>
      <PageHeader title="Mis cultivos" description="Cultivos asociados a tu cuenta." />
      <StateBlock loading={loading} error={error} empty={crops.length === 0}>
        <section className="card-grid">
          {crops.map((crop) => (
            <CropCard crop={crop} key={crop.id} />
          ))}
        </section>
      </StateBlock>
    </>
  );
}

function CatalogPage() {
  const [name, setName] = useState("");
  const [refresh, setRefresh] = useState(0);
  const [message, setMessage] = useState("");
  const { data, loading, error } = useApiData(() => apiRequest("/crops/published", { auth: false, query: { name } }), [refresh]);
  const crops = normalizeList(data);

  async function addCrop(cropId) {
    setMessage("");
    try {
      await apiRequest(`/crops/${cropId}/add-to-my-crops`, { method: "POST" });
      setMessage("Cultivo anadido a tus cultivos.");
    } catch (err) {
      setMessage(err.message || "No se pudo anadir el cultivo");
    }
  }

  return (
    <>
      <PageHeader title="Catalogo" description="Cultivos publicos disponibles para copiar a tu espacio." />
      <form className="toolbar" onSubmit={(event) => { event.preventDefault(); setRefresh((value) => value + 1); }}>
        <input value={name} onChange={(event) => setName(event.target.value)} placeholder="Filtrar por nombre" />
        <button type="submit">Buscar</button>
      </form>
      {message && <p className="state">{message}</p>}
      <StateBlock loading={loading} error={error} empty={crops.length === 0}>
        <section className="card-grid">
          {crops.map((crop) => (
            <CropCard
              crop={crop}
              key={crop.id}
              action={<button type="button" onClick={() => addCrop(crop.id)}>Anadir</button>}
            />
          ))}
        </section>
      </StateBlock>
    </>
  );
}

function CropDetailPage({ cropId }) {
  const { data: crop, loading, error } = useApiData(() => apiRequest(`/crops/${cropId}`), [cropId]);
  const irrigation = crop?.irrigation_attributes;
  const environmental = crop?.environmental_requirements;

  return (
    <>
      <PageHeader title={crop?.name || "Detalle de cultivo"} description={crop?.description || "Informacion basica del cultivo."} />
      <StateBlock loading={loading} error={error} empty={!crop}>
        <section className="detail-grid">
          <InfoBox title="Cultivo" rows={[["Tipo", crop?.crop_type], ["Publico", crop?.is_public ? "Si" : "No"]]} />
          <InfoBox title="Riego" rows={[["Necesidad", irrigation?.water_needs], ["Frecuencia", irrigation?.watering_frequency || irrigation?.frequency_days], ["Cantidad", irrigation?.water_amount]]} />
          <InfoBox title="Ambiente" rows={[["Clima", environmental?.climate], ["Suelo", environmental?.soil_type], ["Sol", environmental?.sun_exposure], ["Temperatura", formatTemp(environmental)]]} />
        </section>
      </StateBlock>
    </>
  );
}

function formatTemp(environmental) {
  if (!environmental) return null;
  if (environmental.min_temperature_c == null && environmental.max_temperature_c == null) return null;
  return `${environmental.min_temperature_c ?? "-"} / ${environmental.max_temperature_c ?? "-"} C`;
}

function InfoBox({ title, rows }) {
  return (
    <article className="item-card">
      <h3>{title}</h3>
      <dl className="info-list">
        {rows.map(([label, value]) => (
          <div key={label}>
            <dt>{label}</dt>
            <dd>{value || "No disponible"}</dd>
          </div>
        ))}
      </dl>
    </article>
  );
}

function CalendarPage() {
  const { data, loading, error } = useApiData(async () => {
    const [calendars, events] = await Promise.all([apiRequest("/calendar/"), apiRequest("/calendar/events")]);
    return { calendars: normalizeList(calendars), events: normalizeList(events) };
  }, []);

  return (
    <>
      <PageHeader title="Calendario" description="Calendarios y fases activas de tus cultivos." />
      <StateBlock loading={loading} error={error} empty={!data || data.calendars.length === 0}>
        <section className="section">
          <h2>Eventos activos</h2>
          {data?.events.length ? (
            <div className="list">
              {data.events.map((event) => (
                <article className="list-item" key={`${event.calendar_id}-${event.phase_index}`}>
                  <strong>{event.crop_name}</strong>
                  <span>{event.phase}</span>
                  <small>Mes {event.start_month} a mes {event.end_month}</small>
                </article>
              ))}
            </div>
          ) : (
            <p className="state">No hay eventos activos.</p>
          )}
        </section>
        <section className="card-grid">
          {data?.calendars.map((calendar) => (
            <article className="item-card" key={calendar.id}>
              <h3>Calendario #{calendar.id}</h3>
              <p>Cultivo #{calendar.crop_id}</p>
              <span className={`badge ${calendar.is_active ? "success" : ""}`}>{calendar.status}</span>
              <small>Fase actual: {calendar.current_phase_index}</small>
            </article>
          ))}
        </section>
      </StateBlock>
    </>
  );
}

function TasksPage() {
  const [refresh, setRefresh] = useState(0);
  const [form, setForm] = useState({ name: "", description: "" });
  const { data, loading, error, setError } = useApiData(() => apiRequest("/tasks/"), [refresh]);
  const tasks = normalizeList(data);
  const pending = tasks.filter((task) => task.status === "pending");
  const completed = tasks.filter((task) => task.status === "completed");

  async function createTask(event) {
    event.preventDefault();
    setError("");
    try {
      await apiRequest("/tasks/", { method: "POST", body: { ...form, status: "pending", crop_ids: [] } });
      setForm({ name: "", description: "" });
      setRefresh((value) => value + 1);
    } catch (err) {
      setError(err.message || "No se pudo crear la tarea");
    }
  }

  async function updateStatus(task) {
    setError("");
    try {
      await apiRequest(`/tasks/${task.id}`, {
        method: "PATCH",
        body: { status: task.status === "completed" ? "pending" : "completed" },
      });
      setRefresh((value) => value + 1);
    } catch (err) {
      setError(err.message || "No se pudo actualizar la tarea");
    }
  }

  async function deleteTask(taskId) {
    setError("");
    try {
      await apiRequest(`/tasks/${taskId}`, { method: "DELETE" });
      setRefresh((value) => value + 1);
    } catch (err) {
      setError(err.message || "No se pudo eliminar la tarea");
    }
  }

  return (
    <>
      <PageHeader title="Tareas" description="Gestiona tareas pendientes y completadas." />
      <form className="task-form" onSubmit={createTask}>
        <input value={form.name} onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))} placeholder="Nueva tarea" required />
        <input value={form.description} onChange={(event) => setForm((current) => ({ ...current, description: event.target.value }))} placeholder="Descripcion opcional" />
        <button type="submit">Crear</button>
      </form>
      <StateBlock loading={loading} error={error} empty={tasks.length === 0}>
        <TaskGroup title="Pendientes" tasks={pending} onToggle={updateStatus} onDelete={deleteTask} />
        <TaskGroup title="Completadas" tasks={completed} onToggle={updateStatus} onDelete={deleteTask} />
      </StateBlock>
    </>
  );
}

function TaskGroup({ title, tasks, onToggle, onDelete }) {
  return (
    <section className="section">
      <h2>{title}</h2>
      {tasks.length === 0 ? (
        <p className="state">Sin tareas en esta seccion.</p>
      ) : (
        <div className="list">
          {tasks.map((task) => (
            <article className="list-item task-item" key={task.id}>
              <div>
                <strong>{task.name}</strong>
                {task.description && <span>{task.description}</span>}
              </div>
              <div className="button-row">
                <button type="button" onClick={() => onToggle(task)}>
                  {task.status === "completed" ? "Reabrir" : "Completar"}
                </button>
                <button type="button" className="danger" onClick={() => onDelete(task.id)}>
                  Eliminar
                </button>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}

function AdminForbidden() {
  return (
    <>
      <PageHeader title="Acceso restringido" description="No tienes permisos de administrador para acceder a este panel." />
      <button type="button" onClick={() => navigate("/")}>
        Volver al dashboard
      </button>
    </>
  );
}

function AdminTabs() {
  return (
    <nav className="admin-tabs" aria-label="Secciones admin">
      {Object.entries(adminRoutes).map(([path, label]) => (
        <button key={path} type="button" onClick={() => navigate(path)}>
          {label}
        </button>
      ))}
    </nav>
  );
}

function AdminDashboardPage() {
  const { data, loading, error } = useApiData(() => getAdminSummary(), []);
  return (
    <>
      <PageHeader title="Panel admin" description="Resumen global de AgroManager." />
      <AdminTabs />
      <StateBlock loading={loading} error={error} empty={!data}>
        <section className="metric-grid">
          <Metric label="Usuarios" value={data?.total_users ?? 0} />
          <Metric label="Cultivos" value={data?.total_crops ?? 0} />
          <Metric label="Cultivos publicos" value={data?.total_public_crops ?? 0} />
          <Metric label="Tareas" value={data?.total_tasks ?? 0} />
          <Metric label="Tareas pendientes" value={data?.pending_tasks ?? 0} />
          <Metric label="Tareas completadas" value={data?.completed_tasks ?? 0} />
          <Metric label="Calendarios activos" value={data?.total_active_calendars ?? data?.active_calendars_total ?? 0} />
          <Metric label="Calendarios completados" value={data?.total_completed_calendars ?? data?.completed_calendars_total ?? 0} />
        </section>
      </StateBlock>
    </>
  );
}

function AdminUsersPage() {
  return (
    <AdminManagePage
      title="Usuarios"
      description="Gestion global de cuentas."
      loader={getAdminUsers}
      detailLoader={getAdminUser}
      updater={updateAdminUser}
      deleter={deleteAdminUser}
      entityName="usuario"
      columns={[
        ["ID", (user) => user.id],
        ["Email", (user) => user.email],
        ["Nombre", (user) => user.username || user.name],
        ["Rol", (user) => user.role || "user"],
        ["Activo", (user) => (Object.prototype.hasOwnProperty.call(user, "is_active") ? (user.is_active ? "Si" : "No") : "No disponible")],
      ]}
      fields={[
        { name: "email", label: "Email", type: "email" },
        { name: "username", label: "Nombre de usuario" },
        { name: "name", label: "Nombre" },
        { name: "role", label: "Rol", type: "select", options: ["user", "admin"] },
        { name: "is_active", label: "Activo", type: "checkbox" },
      ]}
    />
  );
}

function AdminCropsPage() {
  return (
    <AdminManagePage
      title="Cultivos"
      description="Cultivos globales del sistema."
      loader={getAdminCrops}
      detailLoader={getAdminCrop}
      updater={updateAdminCrop}
      deleter={deleteAdminCrop}
      entityName="cultivo"
      columns={[
        ["ID", (crop) => crop.id],
        ["Nombre", (crop) => crop.name],
        ["Tipo", (crop) => crop.crop_type],
        ["Publico", (crop) => (Object.prototype.hasOwnProperty.call(crop, "is_public") ? (crop.is_public ? "Si" : "No") : "No disponible")],
        ["Propietario", (crop) => crop.owner_id || "Global"],
      ]}
      fields={[
        { name: "name", label: "Nombre" },
        { name: "description", label: "Descripcion", type: "textarea" },
        { name: "crop_type", label: "Tipo" },
        { name: "is_public", label: "Publico", type: "checkbox" },
      ]}
    />
  );
}

function AdminTasksPage() {
  return (
    <AdminManagePage
      title="Tareas"
      description="Tareas globales creadas por los usuarios."
      loader={getAdminTasks}
      detailLoader={getAdminTask}
      updater={updateAdminTask}
      deleter={deleteAdminTask}
      entityName="tarea"
      columns={[
        ["ID", (task) => task.id],
        ["Titulo", (task) => task.title || task.name],
        ["Estado", (task) => task.status],
        ["Usuario", (task) => task.user_id],
        ["Vencimiento", (task) => task.due_date || "No disponible"],
      ]}
      fields={[
        { name: "title", label: "Titulo" },
        { name: "name", label: "Nombre" },
        { name: "description", label: "Descripcion", type: "textarea" },
        { name: "status", label: "Estado", type: "select", options: ["pending", "completed"] },
        { name: "due_date", label: "Fecha limite", type: "date" },
      ]}
    />
  );
}

function AdminManagePage({ title, description, loader, detailLoader, updater, deleter, entityName, columns, fields }) {
  const [refresh, setRefresh] = useState(0);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({});
  const [message, setMessage] = useState("");
  const [saving, setSaving] = useState(false);
  const { data, loading, error, setError } = useApiData(loader, [refresh]);
  const items = normalizeList(data);

  function availableFields(item) {
    if (!item) return [];
    return fields.filter((field) => field.name in item || alwaysEditableField(field.name, item));
  }

  async function editItem(item) {
    setMessage("");
    setError("");
    try {
      const detail = await detailLoader(item.id);
      const next = detail || item;
      setEditing(next);
      setForm(buildAdminForm(next, fields));
    } catch (err) {
      setError(err.message || `No se pudo cargar el ${entityName}`);
    }
  }

  async function saveItem(event) {
    event.preventDefault();
    if (!editing) return;
    setSaving(true);
    setMessage("");
    setError("");
    try {
      const payload = buildAdminPayload(form, availableFields(editing));
      await updater(editing.id, payload);
      setEditing(null);
      setForm({});
      setMessage(`${capitalize(entityName)} actualizado correctamente.`);
      setRefresh((value) => value + 1);
    } catch (err) {
      setError(err.message || `No se pudo actualizar el ${entityName}`);
    } finally {
      setSaving(false);
    }
  }

  async function removeItem(item) {
    if (!window.confirm(`¿Eliminar ${entityName} #${item.id}?`)) return;
    setMessage("");
    setError("");
    try {
      await deleter(item.id);
      setMessage(`${capitalize(entityName)} eliminado correctamente.`);
      if (editing?.id === item.id) setEditing(null);
      setRefresh((value) => value + 1);
    } catch (err) {
      setError(err.message || `No se pudo eliminar el ${entityName}`);
    }
  }

  return (
    <>
      <PageHeader title={title} description={description} />
      <AdminTabs />
      {message && <p className="state">{message}</p>}
      <StateBlock loading={loading} error={error} empty={items.length === 0}>
        <div className="admin-table-wrap">
          <table className="admin-table">
            <thead>
              <tr>
                {columns.map(([label]) => (
                  <th key={label}>{label}</th>
                ))}
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.id}>
                  {columns.map(([label, render]) => (
                    <td key={label}>{formatAdminValue(render(item))}</td>
                  ))}
                  <td>
                    <div className="button-row compact">
                      <button type="button" onClick={() => editItem(item)}>
                        Editar
                      </button>
                      <button type="button" className="danger" onClick={() => removeItem(item)}>
                        Eliminar
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </StateBlock>
      {editing && (
        <section className="section admin-editor">
          <h2>Editar {entityName} #{editing.id}</h2>
          <form className="form admin-form" onSubmit={saveItem}>
            {availableFields(editing).map((field) => (
              <AdminField
                key={field.name}
                field={field}
                value={form[field.name]}
                onChange={(value) => setForm((current) => ({ ...current, [field.name]: value }))}
              />
            ))}
            <div className="button-row">
              <button className="primary-button" type="submit" disabled={saving}>
                {saving ? "Guardando..." : "Guardar cambios"}
              </button>
              <button type="button" onClick={() => setEditing(null)}>
                Cancelar
              </button>
            </div>
          </form>
        </section>
      )}
    </>
  );
}

function AdminField({ field, value, onChange }) {
  if (field.type === "checkbox") {
    return (
      <label className="check-row">
        <input type="checkbox" checked={Boolean(value)} onChange={(event) => onChange(event.target.checked)} />
        {field.label}
      </label>
    );
  }

  if (field.type === "select") {
    return (
      <label>
        {field.label}
        <select value={value ?? ""} onChange={(event) => onChange(event.target.value)}>
          {field.options.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      </label>
    );
  }

  if (field.type === "textarea") {
    return (
      <label>
        {field.label}
        <textarea value={value ?? ""} onChange={(event) => onChange(event.target.value)} rows="4" />
      </label>
    );
  }

  return (
    <label>
      {field.label}
      <input type={field.type || "text"} value={value ?? ""} onChange={(event) => onChange(event.target.value)} />
    </label>
  );
}

function alwaysEditableField(fieldName, item) {
  if (fieldName === "name" && "title" in item) return true;
  if (fieldName === "title" && "name" in item) return false;
  return false;
}

function buildAdminForm(item, fields) {
  return fields.reduce((current, field) => {
    if (field.name in item || alwaysEditableField(field.name, item)) {
      current[field.name] = field.type === "checkbox" ? Boolean(item[field.name]) : item[field.name] ?? "";
    }
    return current;
  }, {});
}

function buildAdminPayload(form, fields) {
  return fields.reduce((payload, field) => {
    if (!(field.name in form)) return payload;
    payload[field.name] = field.type === "checkbox" ? Boolean(form[field.name]) : form[field.name];
    return payload;
  }, {});
}

function formatAdminValue(value) {
  if (value === null || value === undefined || value === "") return "No disponible";
  return String(value);
}

function capitalize(value) {
  return value ? value.charAt(0).toUpperCase() + value.slice(1) : "";
}

function ProfilePage() {
  const auth = useAuth();
  return (
    <>
      <PageHeader title="Sesion" description="Datos basicos de la cuenta activa." />
      <section className="detail-grid">
        <InfoBox title="Usuario" rows={[["Email", auth.user?.email], ["Nombre", auth.user?.username], ["Rol", auth.user?.role || "user"]]} />
      </section>
      <button className="primary-button narrow" type="button" onClick={auth.logout}>
        Cerrar sesion
      </button>
    </>
  );
}

function NotFoundPage() {
  return <PageHeader title="Pagina no encontrada" description="La ruta solicitada no existe en esta aplicacion." />;
}

createRoot(document.getElementById("root")).render(<App />);
