import { useCallback, useContext, useEffect, useMemo, useState } from "react";
import { AuthContext } from "../context/auth-context";
import { advanceCalendarCropPhase, getMyCalendarEvents } from "../api/api";

const months = [
  "Enero",
  "Febrero",
  "Marzo",
  "Abril",
  "Mayo",
  "Junio",
  "Julio",
  "Agosto",
  "Septiembre",
  "Octubre",
  "Noviembre",
  "Diciembre",
];

export default function Calendar() {
  const { token } = useContext(AuthContext);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [advancingCropId, setAdvancingCropId] = useState(null);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState(null);

  const loadEvents = useCallback(async () => {
    setLoading(true);
    setError(null);
    setMessage(null);

    try {
      const data = await getMyCalendarEvents(token);
      setEvents(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err.message || "Error al cargar eventos");
      setEvents([]);
    } finally {
      setLoading(false);
    }
  }, [token]);

  const handleAdvancePhase = async (cropId, isLastPhase) => {
    setAdvancingCropId(cropId);
    setError(null);
    setMessage(null);

    try {
      await advanceCalendarCropPhase(token, cropId);
      setMessage(isLastPhase ? "Cultivo finalizado correctamente" : "Cultivo avanzado a la siguiente fase");
      await loadEvents();
    } catch (err) {
      setError(err.message || "No se pudo avanzar la fase del cultivo");
    } finally {
      setAdvancingCropId(null);
    }
  };

  useEffect(() => {
    if (token) {
      loadEvents();
    }
  }, [loadEvents, token]);

  const groupedEvents = useMemo(() => {
    const grouped = {};
    months.forEach((_, index) => {
      grouped[index + 1] = { 1: [], 2: [] };
    });

    events.forEach((event) => {
      const month = Number(event.month);
      const half = Number(event.half);
      if (grouped[month]?.[half]) {
        grouped[month][half].push(event);
      }
    });

    return grouped;
  }, [events]);

  return (
    <main style={page}>
      <section style={headerSection}>
        <div style={headerContent}>
          <span style={label}>Calendario agrícola</span>
          <h1 style={title}>Calendario por quincenas</h1>
          <p style={description}>
            Visualiza cada mes con su primera y segunda quincena, mostrando los eventos de siembra, trasplante y cosecha.
          </p>

          <div style={form}>
            <button type="button" style={loadButton} disabled={loading} onClick={loadEvents}>
              {loading ? "Cargando..." : "Cargar eventos"}
            </button>
          </div>

          {error && <p style={errorText}>{error}</p>}
          {message && <p style={successText}>{message}</p>}
        </div>
      </section>

      <section style={gridSection}>
        <div style={calendarGrid}>
          {months.map((monthName, index) => {
            const monthNumber = index + 1;
            const firstHalf = groupedEvents[monthNumber]?.[1] ?? [];
            const secondHalf = groupedEvents[monthNumber]?.[2] ?? [];

            return (
              <article key={monthName} style={monthCard} className="calendar-month-card">
                <h2 style={monthTitle}>{monthName}</h2>
                <div style={halfGrid}>
                  <div style={halfCard} className="calendar-half-card">
                    <div style={halfHeader}>Primera mitad</div>
                    {firstHalf.length > 0 ? (
                      firstHalf.map((event, key) => (
                        <div key={`first-${key}`} style={eventBlock} className="event-block">
                          <span style={phaseBadge(event.phase)}>{event.phase}</span>
                          <span style={eventTitle}>{event.crop_name || event.title}</span>
                          <button
                            type="button"
                            style={advanceButton}
                            onClick={() => handleAdvancePhase(event.crop_id, event.is_last_phase)}
                            disabled={advancingCropId === event.crop_id}
                          >
                            {advancingCropId === event.crop_id
                              ? "Guardando..."
                              : event.is_last_phase
                                ? "Finalizar cultivo"
                                : "Pasar a siguiente fase"}
                          </button>
                        </div>
                      ))
                    ) : (
                      <p style={emptyText}>Sin actividad</p>
                    )}
                  </div>

                  <div style={halfCard} className="calendar-half-card">
                    <div style={halfHeader}>Segunda mitad</div>
                    {secondHalf.length > 0 ? (
                      secondHalf.map((event, key) => (
                        <div key={`second-${key}`} style={eventBlock} className="event-block">
                          <span style={phaseBadge(event.phase)}>{event.phase}</span>
                          <span style={eventTitle}>{event.crop_name || event.title}</span>
                          <span style={eventMeta}>Mes {event.month}</span>
                          <button
                            type="button"
                            style={advanceButton}
                            onClick={() => handleAdvancePhase(event.crop_id, event.is_last_phase)}
                            disabled={advancingCropId === event.crop_id}
                          >
                            {advancingCropId === event.crop_id
                              ? "Guardando..."
                              : event.is_last_phase
                                ? "Finalizar cultivo"
                                : "Pasar a siguiente fase"}
                          </button>
                        </div>
                      ))
                    ) : (
                      <p style={emptyText}>Sin actividad</p>
                    )}
                  </div>
                </div>
              </article>
            );
          })}
        </div>
      </section>

      <style>{`
        .calendar-month-card:hover {
          transform: translateY(-4px);
          box-shadow: 0 28px 50px rgba(15, 23, 42, 0.14);
        }

        .calendar-half-card:hover {
          transform: translateY(-2px);
        }

        .event-block:hover {
          transform: translateX(2px);
        }
      `}</style>
    </main>
  );
}

const page = {
  minHeight: "100vh",
  padding: "24px",
  background: "#F6FBF5",
  fontFamily: "Inter, Arial, sans-serif",
  color: "#1F3D2E",
};

const headerSection = {
  background: "linear-gradient(135deg, #E8F6EA 0%, #F4FAF6 100%)",
  borderRadius: "28px",
  padding: "36px 28px",
  boxShadow: "0 24px 50px rgba(15, 23, 42, 0.08)",
  marginBottom: "32px",
};

const headerContent = {
  maxWidth: "900px",
};

const label = {
  display: "inline-flex",
  marginBottom: "18px",
  padding: "10px 16px",
  borderRadius: "999px",
  background: "#E6F4EA",
  color: "#2E7D32",
  fontWeight: 700,
  fontSize: "0.95rem",
};

const title = {
  fontSize: "clamp(2rem, 4vw, 3.4rem)",
  lineHeight: 1.03,
  margin: 0,
  color: "#15452A",
};

const description = {
  maxWidth: "720px",
  marginTop: "18px",
  fontSize: "1.02rem",
  lineHeight: 1.8,
  color: "#4F645C",
};

const form = {
  marginTop: "28px",
  display: "flex",
  flexWrap: "wrap",
  alignItems: "flex-end",
  gap: "16px",
};

const phaseBadge = (phase) => {
  const colors = {
    Siembra: { background: "#E8F6EA", color: "#2E7D32" },
    Trasplante: { background: "#E0F2FE", color: "#0369A1" },
    Cosecha: { background: "#FEF3C7", color: "#92400E" },
  };

  return {
    alignSelf: "flex-start",
    padding: "5px 9px",
    borderRadius: "999px",
    fontSize: "0.78rem",
    fontWeight: 800,
    ...(colors[phase] || colors.Siembra),
  };
};

const loadButton = {
  padding: "14px 24px",
  borderRadius: "14px",
  border: "none",
  background: "#4CAF50",
  color: "white",
  fontSize: "1rem",
  fontWeight: 700,
  cursor: "pointer",
  transition: "transform 180ms ease, box-shadow 180ms ease",
  boxShadow: "0 14px 24px rgba(76, 175, 80, 0.18)",
};

const errorText = {
  marginTop: "18px",
  color: "#9B2C2C",
  fontWeight: 600,
};

const successText = {
  marginTop: "18px",
  color: "#2E7D32",
  fontWeight: 700,
};

const gridSection = {
  maxWidth: "1180px",
  margin: "0 auto",
};

const calendarGrid = {
  display: "grid",
  gap: "20px",
  gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
};

const monthCard = {
  borderRadius: "24px",
  background: "white",
  padding: "22px",
  boxShadow: "0 18px 38px rgba(15, 23, 42, 0.08)",
  transition: "transform 180ms ease, box-shadow 180ms ease",
};

const monthTitle = {
  margin: 0,
  marginBottom: "18px",
  fontSize: "1.25rem",
  color: "#1F3D2E",
};

const halfGrid = {
  display: "grid",
  gap: "16px",
};

const halfCard = {
  borderRadius: "20px",
  padding: "18px",
  background: "#F8FBF8",
  transition: "transform 180ms ease, box-shadow 180ms ease",
  boxShadow: "inset 0 0 0 1px rgba(76, 175, 80, 0.08)",
};

const halfHeader = {
  margin: 0,
  marginBottom: "14px",
  fontWeight: 700,
  color: "#2E7D32",
};

const eventBlock = {
  borderRadius: "16px",
  padding: "14px 16px",
  background: "white",
  border: "1px solid #E5EFE4",
  display: "flex",
  flexDirection: "column",
  gap: "8px",
  marginBottom: "12px",
  transition: "transform 180ms ease, box-shadow 180ms ease",
  boxShadow: "0 10px 20px rgba(15, 23, 42, 0.06)",
};

const eventTitle = {
  fontWeight: 700,
  color: "#15452A",
};

const eventMeta = {
  fontSize: "0.95rem",
  color: "#5B705F",
};

const advanceButton = {
  marginTop: "4px",
  padding: "10px 12px",
  borderRadius: "12px",
  border: "1px solid #C8D8CB",
  background: "#F8FBF8",
  color: "#2E7D32",
  fontWeight: 800,
  cursor: "pointer",
};

const emptyText = {
  margin: 0,
  color: "#6B7D6D",
  fontStyle: "italic",
};
