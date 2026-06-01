import { useNavigate } from "react-router-dom";

export default function Home() {
  const navigate = useNavigate();

  return (
    <main style={page}>
      <section style={heroSection}>
        <div style={heroContent}>
          <span style={badge}>AgroManager</span>
          <h1 style={heroTitle}>Gestiona tu granja con claridad y control.</h1>
          <p style={heroText}>
            AgroManager es la plataforma SaaS para agricultores que buscan organización, seguimiento de cultivos y planificación inteligente.
          </p>

          <div style={heroButtons}>
            <button className="home-button home-button-primary" style={primaryButton} onClick={() => navigate("/login")}>Iniciar sesión</button>
            <button className="home-button home-button-secondary" style={secondaryButton} onClick={() => navigate("/signup")}>Crear cuenta</button>
          </div>

          <div style={heroStats}>
            <div className="home-stat-card" style={statCard}>
              <strong>+30%</strong>
              <span>Mejora en la planificación</span>
            </div>
            <div className="home-stat-card" style={statCard}>
              <strong>10k+</strong>
              <span>Datos agrícolas almacenados</span>
            </div>
            <div className="home-stat-card" style={statCard}>
              <strong>Disponible</strong>
              <span>En cualquier dispositivo</span>
            </div>
          </div>
        </div>
      </section>

      <section style={featuresSection}>
        <h2 style={sectionTitle}>Todo lo que necesitas para gestionar tu producción</h2>
        <div style={featureGrid}>
          <article className="home-feature-card" style={featureCard}>
            <div className="home-icon-circle" style={iconCircle}>🌿</div>
            <h3 style={featureTitle}>Control de cultivos</h3>
            <p style={featureDescription}>Monitorea cada cultivo, ciclo y actividad con alertas claras.</p>
          </article>
          <article className="home-feature-card" style={featureCard}>
            <div className="home-icon-circle" style={iconCircle}>📅</div>
            <h3 style={featureTitle}>Calendario inteligente</h3>
            <p style={featureDescription}>Planifica tareas, siembras y riegos desde un espacio centralizado.</p>
          </article>
          <article className="home-feature-card" style={featureCard}>
            <div className="home-icon-circle" style={iconCircle}>💧</div>
            <h3 style={featureTitle}>Riego eficiente</h3>
            <p style={featureDescription}>Gestiona el agua de forma óptima para mejorar rendimiento y ahorro.</p>
          </article>
          <article className="home-feature-card" style={featureCard}>
            <div className="home-icon-circle" style={iconCircle}>📈</div>
            <h3 style={featureTitle}>Informe rápido</h3>
            <p style={featureDescription}>Obtén datos clave de rendimiento en un diseño sencillo y moderno.</p>
          </article>
        </div>
      </section>

      <section style={benefitsSection}>
        <h2 style={sectionTitle}>Beneficios para tu proyecto agrícola</h2>
        <div style={benefitsGrid}>
          <div className="home-benefit-card" style={benefitCard}>
            <h3 style={benefitTitle}>Ahorro de tiempo</h3>
            <p style={benefitText}>Automatiza el seguimiento de cultivos y reduce las tareas manuales para que tu equipo pueda centrarse en lo importante.</p>
          </div>
          <div className="home-benefit-card" style={benefitCard}>
            <h3 style={benefitTitle}>Organización completa</h3>
            <p style={benefitText}>Centraliza tus tareas, calendarios y recursos en una sola plataforma intuitiva.</p>
          </div>
          <div className="home-benefit-card" style={benefitCard}>
            <h3 style={benefitTitle}>Control de cultivos</h3>
            <p style={benefitText}>Visualiza toda la información relevante de cada cultivo y toma decisiones basadas en datos.</p>
          </div>
        </div>
      </section>

      <footer style={footer}>
        <span>AgroManager</span>
        <span>2026</span>
        <span>Proyecto TFG</span>
      </footer>

      <style>{`
        .home-button {
          transition: transform 220ms ease, box-shadow 220ms ease, background-color 220ms ease, color 220ms ease;
        }

        .home-button:hover {
          transform: translateY(-2px);
          box-shadow: 0 18px 40px rgba(76, 175, 80, 0.25);
        }

        .home-button-primary:hover {
          background-color: #3f8c3f;
        }

        .home-button-secondary:hover {
          background-color: #f4fbf4;
        }

        .home-feature-card,
        .home-benefit-card,
        .home-stat-card {
          transition: transform 220ms ease, box-shadow 220ms ease;
        }

        .home-feature-card:hover,
        .home-benefit-card:hover,
        .home-stat-card:hover {
          transform: translateY(-5px);
          box-shadow: 0 28px 60px rgba(15, 23, 42, 0.14);
        }

        .home-icon-circle {
          transition: transform 220ms ease, box-shadow 220ms ease;
        }

        .home-feature-card:hover .home-icon-circle {
          transform: translateY(-3px);
          box-shadow: 0 18px 28px rgba(46, 125, 50, 0.16);
        }

        .home-feature-card,
        .home-benefit-card,
        .home-stat-card {
          cursor: default;
        }

        @media (max-width: 720px) {
          .home-button {
            width: 100%;
          }
        }
      `}</style>
    </main>
  );
}

const page = {
  fontFamily: "Inter, Arial, sans-serif",
  color: "#1F3D2E",
  background: "linear-gradient(180deg, #F5FBF5 0%, #FFFFFF 100%)",
  minHeight: "100vh",
};

const heroSection = {
  padding: "80px 24px 40px",
  background: "linear-gradient(135deg, #E8F6EA 0%, #F7FAFB 100%)",
};

const heroContent = {
  maxWidth: "1080px",
  margin: "0 auto",
  display: "flex",
  flexDirection: "column",
  gap: "32px",
};

const badge = {
  display: "inline-flex",
  alignItems: "center",
  padding: "10px 16px",
  borderRadius: "999px",
  background: "#E6F4EA",
  color: "#2E7D32",
  fontWeight: 700,
  letterSpacing: "0.02em",
  fontSize: "0.95rem",
  width: "fit-content",
};

const heroTitle = {
  margin: 0,
  fontSize: "clamp(2.6rem, 5vw, 4.2rem)",
  lineHeight: 1.03,
  maxWidth: "760px",
  color: "#15452A",
};

const heroText = {
  fontSize: "1.05rem",
  lineHeight: 1.8,
  maxWidth: "680px",
  color: "#40504F",
};

const heroButtons = {
  display: "flex",
  gap: "16px",
  flexWrap: "wrap",
};

const primaryButton = {
  padding: "16px 28px",
  borderRadius: "14px",
  border: "none",
  background: "#4CAF50",
  color: "white",
  fontSize: "1rem",
  fontWeight: 700,
  cursor: "pointer",
  boxShadow: "0 18px 40px rgba(76, 175, 80, 0.18)",
};

const secondaryButton = {
  padding: "16px 28px",
  borderRadius: "14px",
  border: "1px solid rgba(76, 175, 80, 0.18)",
  background: "white",
  color: "#2E7D32",
  fontSize: "1rem",
  fontWeight: 700,
  cursor: "pointer",
};

const heroStats = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
  gap: "14px",
};

const statCard = {
  background: "rgba(76, 175, 80, 0.08)",
  borderRadius: "16px",
  padding: "20px",
  display: "flex",
  flexDirection: "column",
  gap: "8px",
  color: "#1F3D2E",
  boxShadow: "0 14px 30px rgba(46, 125, 50, 0.08)",
};

const featuresSection = {
  padding: "64px 24px 24px",
  maxWidth: "1080px",
  margin: "0 auto",
};

const sectionTitle = {
  fontSize: "2rem",
  margin: 0,
  marginBottom: "28px",
  color: "#163B29",
};

const featureGrid = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
  gap: "20px",
};

const featureCard = {
  background: "white",
  borderRadius: "24px",
  padding: "28px",
  boxShadow: "0 24px 50px rgba(15, 23, 42, 0.08)",
  minHeight: "220px",
  display: "flex",
  flexDirection: "column",
  gap: "16px",
};

const iconCircle = {
  width: "52px",
  height: "52px",
  borderRadius: "16px",
  display: "grid",
  placeItems: "center",
  background: "#EAF6F0",
  fontSize: "1.4rem",
};

const featureTitle = {
  margin: 0,
  fontSize: "1.2rem",
  color: "#18422D",
};

const featureDescription = {
  margin: 0,
  fontSize: "1rem",
  lineHeight: 1.7,
  color: "#52635D",
};

const benefitsSection = {
  padding: "48px 24px 36px",
  background: "#F8FCF8",
};

const benefitsGrid = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
  gap: "20px",
  maxWidth: "1080px",
  margin: "0 auto",
};

const benefitCard = {
  background: "white",
  borderRadius: "22px",
  padding: "28px",
  boxShadow: "0 20px 40px rgba(15, 23, 42, 0.06)",
};

const benefitTitle = {
  fontSize: "1.15rem",
  margin: 0,
  marginBottom: "14px",
  color: "#1F3D2E",
};

const benefitText = {
  margin: 0,
  fontSize: "1rem",
  lineHeight: 1.8,
  color: "#57645C",
};

const footer = {
  padding: "24px",
  marginTop: "12px",
  borderTop: "1px solid #E6F1EA",
  display: "flex",
  justifyContent: "center",
  gap: "20px",
  flexWrap: "wrap",
  color: "#67786D",
  fontSize: "0.95rem",
  textAlign: "center",
};
