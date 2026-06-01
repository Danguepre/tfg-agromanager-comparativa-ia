import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { getDashboardSummary } from "../api/api";
import { parseJwt } from "../utils/auth";

const monthNames = [
  "enero",
  "febrero",
  "marzo",
  "abril",
  "mayo",
  "junio",
  "julio",
  "agosto",
  "septiembre",
  "octubre",
  "noviembre",
  "diciembre",
];

const formatHalf = (month, half) => {
  const halfText = half === 1 ? "primera quincena" : "segunda quincena";
  const monthText = monthNames[month - 1] || `mes ${month}`;
  return `${halfText} de ${monthText}`;
};

export default function Dashboard({ token }) {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const currentUser = useMemo(() => parseJwt(token || ""), [token]);

  useEffect(() => {
    const loadSummary = async () => {
      setLoading(true);
      setError(null);

      try {
        setSummary(await getDashboardSummary(token));
      } catch (err) {
        setError(err.message || "No se pudo cargar tu resumen");
      } finally {
        setLoading(false);
      }
    };

    if (token) {
      loadSummary();
    }
  }, [token]);

  const stats = [
    { label: "Mis cultivos", value: summary?.crops_count ?? 0 },
    { label: "Activos en calendario", value: summary?.active_calendar_count ?? 0 },
    { label: "Tareas pendientes", value: summary?.pending_tasks_count ?? 0 },
    { label: "Fases incompletas", value: summary?.incomplete_phase_crops_count ?? 0 },
  ];

  return (
    <main style={page}>
      <header style={hero}>
        <div>
          <p style={eyebrow}>Resumen personal</p>
          <h1 style={title}>Inicio</h1>
          <p style={subtitle}>
            Tu actividad reciente de cultivos, tareas y calendario en un solo sitio.
          </p>
        </div>
        {currentUser?.role === "admin" && (
          <Link to="/admin" style={adminButton}>
            Panel admin
          </Link>
        )}
      </header>

      {loading ? (
        <p style={emptyText}>Cargando tu resumen...</p>
      ) : error ? (
        <p style={errorText}>{error}</p>
      ) : (
        <>
          <section style={statsGrid}>
            {stats.map((stat) => (
              <article key={stat.label} style={statCard}>
                <span style={statLabel}>{stat.label}</span>
                <strong style={statValue}>{stat.value}</strong>
              </article>
            ))}
          </section>

          <section style={quickGrid}>
            <QuickLink to="/crops" title="Mis cultivos" text="Revisa y edita tus plantaciones." />
            <QuickLink to="/published-crops" title="Catalogo" text="Anade nuevos cultivos a tu lista." />
            <QuickLink to="/calendar" title="Calendario" text="Consulta fases por mes y quincena." />
            <QuickLink to="/tasks" title="Tareas" text="Gestiona trabajo pendiente." />
          </section>

          <section style={contentGrid}>
            <article style={panel}>
              <div style={panelHeader}>
                <h2 style={panelTitle}>Tareas pendientes</h2>
                <Link to="/tasks" style={panelLink}>Ver tareas</Link>
              </div>
              {summary.pending_tasks.length === 0 ? (
                <p style={emptyText}>No tienes tareas pendientes.</p>
              ) : (
                <div style={list}>
                  {summary.pending_tasks.map((task) => (
                    <div key={task.id} style={listItem}>
                      <strong style={itemTitle}>{task.name}</strong>
                      <span style={muted}>{task.status}</span>
                      {task.description && <p style={itemText}>{task.description}</p>}
                    </div>
                  ))}
                </div>
              )}
            </article>

            <article style={panel}>
              <div style={panelHeader}>
                <h2 style={panelTitle}>Cultivos activos</h2>
                <Link to="/calendar" style={panelLink}>Ver calendario</Link>
              </div>
              {summary.active_calendars.length === 0 ? (
                <p style={emptyText}>No hay cultivos activos en el calendario.</p>
              ) : (
                <div style={list}>
                  {summary.active_calendars.map((event) => (
                    <div key={`${event.crop_id}-${event.phase}`} style={listItem}>
                      <strong style={itemTitle}>{event.crop_name}</strong>
                      <span style={phaseBadge}>{event.phase}</span>
                      <p style={itemText}>{formatHalf(event.month, event.half)}</p>
                    </div>
                  ))}
                </div>
              )}
            </article>
          </section>

          <section style={panel}>
            <div style={panelHeader}>
              <h2 style={panelTitle}>Avisos</h2>
              <Link to="/crops" style={panelLink}>Revisar cultivos</Link>
            </div>
            {summary.warnings.length === 0 ? (
              <p style={emptyText}>Todo listo: no hay avisos importantes ahora mismo.</p>
            ) : (
              <div style={warningGrid}>
                {summary.warnings.map((warning) => (
                  <div key={`${warning.crop_id}-${warning.reason}`} style={warningCard}>
                    <strong style={itemTitle}>{warning.crop_name}</strong>
                    <p style={itemText}>{warning.reason}</p>
                  </div>
                ))}
              </div>
            )}
          </section>

          {summary.crops_count === 0 && (
            <section style={startPanel}>
              <h2 style={panelTitle}>Aun no tienes cultivos</h2>
              <p style={subtitle}>Puedes empezar desde el catalogo o crear uno propio en Mis cultivos.</p>
              <div style={actions}>
                <Link to="/published-crops" style={primaryButton}>Ir al catalogo</Link>
                <Link to="/crops" style={secondaryButton}>Mis cultivos</Link>
              </div>
            </section>
          )}
        </>
      )}
    </main>
  );
}

function QuickLink({ to, title, text }) {
  return (
    <Link to={to} style={quickCard}>
      <strong style={quickTitle}>{title}</strong>
      <span style={quickText}>{text}</span>
    </Link>
  );
}

const page = {
  minHeight: "100vh",
  padding: "32px",
  background: "#F4FBF6",
  fontFamily: "Inter, Arial, sans-serif",
};

const hero = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  gap: "18px",
  marginBottom: "24px",
  flexWrap: "wrap",
};

const eyebrow = {
  margin: "0 0 8px",
  color: "#2E7D32",
  fontWeight: 800,
  textTransform: "uppercase",
  fontSize: "0.82rem",
};

const title = {
  margin: 0,
  fontSize: "2.4rem",
  color: "#1E4E2E",
};

const subtitle = {
  margin: "8px 0 0",
  color: "#4D6A5E",
  lineHeight: 1.6,
};

const statsGrid = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(190px, 1fr))",
  gap: "16px",
  marginBottom: "20px",
};

const statCard = {
  padding: "20px",
  borderRadius: "18px",
  background: "white",
  boxShadow: "0 14px 34px rgba(15, 23, 42, 0.08)",
  border: "1px solid rgba(126, 186, 137, 0.16)",
};

const statLabel = {
  display: "block",
  color: "#4D6A5E",
  fontWeight: 700,
  marginBottom: "10px",
};

const statValue = {
  color: "#15452A",
  fontSize: "2rem",
};

const quickGrid = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(210px, 1fr))",
  gap: "14px",
  marginBottom: "22px",
};

const quickCard = {
  padding: "18px",
  borderRadius: "16px",
  background: "#FFFFFF",
  color: "#1F3D2E",
  textDecoration: "none",
  border: "1px solid #D7E7D8",
  boxShadow: "0 10px 24px rgba(15, 23, 42, 0.06)",
};

const quickTitle = {
  display: "block",
  color: "#2E7D32",
  marginBottom: "6px",
};

const quickText = {
  color: "#5A6E60",
  lineHeight: 1.5,
};

const contentGrid = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
  gap: "18px",
  marginBottom: "18px",
};

const panel = {
  padding: "22px",
  borderRadius: "18px",
  background: "white",
  boxShadow: "0 14px 34px rgba(15, 23, 42, 0.08)",
  border: "1px solid rgba(126, 186, 137, 0.16)",
};

const panelHeader = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  gap: "12px",
  marginBottom: "16px",
};

const panelTitle = {
  margin: 0,
  color: "#264F37",
  fontSize: "1.2rem",
};

const panelLink = {
  color: "#2E7D32",
  fontWeight: 800,
  textDecoration: "none",
};

const list = {
  display: "grid",
  gap: "12px",
};

const listItem = {
  padding: "14px",
  borderRadius: "14px",
  background: "#F8FBF8",
  border: "1px solid #D7E7D8",
};

const itemTitle = {
  display: "block",
  color: "#15452A",
  marginBottom: "6px",
};

const itemText = {
  margin: "6px 0 0",
  color: "#4D6A5E",
  lineHeight: 1.5,
};

const muted = {
  color: "#6B7F72",
  fontSize: "0.9rem",
};

const phaseBadge = {
  display: "inline-flex",
  padding: "6px 10px",
  borderRadius: "999px",
  background: "#E8F6EA",
  color: "#2E7D32",
  fontWeight: 800,
  fontSize: "0.86rem",
};

const warningGrid = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
  gap: "12px",
};

const warningCard = {
  padding: "14px",
  borderRadius: "14px",
  background: "#FFF8E6",
  border: "1px solid #F6D98B",
};

const startPanel = {
  ...panel,
  marginTop: "18px",
};

const actions = {
  display: "flex",
  gap: "12px",
  flexWrap: "wrap",
  marginTop: "16px",
};

const primaryButton = {
  padding: "12px 18px",
  borderRadius: "14px",
  background: "#2F8F4C",
  color: "white",
  textDecoration: "none",
  fontWeight: 800,
};

const secondaryButton = {
  padding: "12px 18px",
  borderRadius: "14px",
  background: "white",
  border: "1px solid #C8D8CB",
  color: "#2E7D32",
  textDecoration: "none",
  fontWeight: 800,
};

const adminButton = {
  ...secondaryButton,
  background: "#0F172A",
  color: "white",
  border: "1px solid #0F172A",
};

const emptyText = {
  margin: 0,
  color: "#6B7F72",
  lineHeight: 1.6,
};

const errorText = {
  padding: "16px",
  borderRadius: "14px",
  color: "#9B2C2C",
  background: "#FEE2E2",
  fontWeight: 700,
};
