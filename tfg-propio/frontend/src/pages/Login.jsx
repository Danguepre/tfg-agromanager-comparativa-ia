import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { loginRequest } from "../api/auth";
import { API_URL } from "../api/api";

const GOOGLE_AUTH_URL = `${API_URL}/auth/google`;

const oauthErrorMessages = {
  access_denied: "No se autorizo el acceso con Google.",
  google_token_exchange_failed: "Google no acepto el codigo de acceso. Revisa el redirect URI autorizado.",
  google_token_request_failed: "No se pudo conectar con Google para completar el login.",
  google_userinfo_failed: "No se pudo obtener tu perfil de Google.",
  google_userinfo_request_failed: "No se pudo conectar con Google para leer tu perfil.",
  missing_google_access_token: "Google no devolvio un token valido.",
  missing_google_code: "Google no devolvio el codigo de acceso.",
  missing_google_email: "Google no devolvio un email valido.",
};

export default function Login({ onSwitch, onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const oauthError = location.state?.oauthError;
  const visibleError = error || (oauthError ? oauthErrorMessages[oauthError] || `Error de Google: ${oauthError}` : null);

  const handleLogin = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const data = await loginRequest(email, password);
      localStorage.setItem("token", data.access_token);
      onLogin(data.access_token);
      navigate("/dashboard", { replace: true });
    } catch {
      setError("❌ Email o contraseña incorrectos");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={page}>
      <div style={card}>
        <div style={hero}>
          <div>
            <span style={badge}>Inicio de sesión</span>
            <h2>Bienvenido a AgroManager</h2>
            <p style={subtitle}>
              Accede rápidamente a tu panel de cultivos, calendario y tareas.
            </p>
          </div>
          <div style={heroAccent}>🌿</div>
        </div>

        <form onSubmit={handleLogin} style={form}>
          <label style={label}>Correo electrónico</label>
          <input
            type="email"
            placeholder="tucorreo@ejemplo.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            style={input}
            required
          />

          <label style={label}>Contraseña</label>
          <input
            type="password"
            placeholder="********"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={input}
            required
          />

          <button type="submit" style={button} disabled={loading}>
            {loading ? "Entrando..." : "Entrar"}
          </button>
        </form>

        <a href={GOOGLE_AUTH_URL} target="_top" style={googleButton}>
          <span style={googleIcon}>G</span>
          Iniciar sesión con Google
        </a>

        <p style={switchText}>
          ¿No tienes cuenta? <span onClick={onSwitch} style={link}>Crear cuenta</span>
        </p>

        {visibleError && <p style={errorText}>{visibleError}</p>}
      </div>
    </div>
  );
}

const page = {
  minHeight: "100vh",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  background: "radial-gradient(circle at top, #d7f7f0, #fffefb 40%)",
  padding: "20px",
};

const card = {
  width: "100%",
  maxWidth: "420px",
  background: "#ffffff",
  borderRadius: "24px",
  boxShadow: "0 28px 80px rgba(27, 63, 80, 0.12)",
  padding: "36px",
  border: "1px solid rgba(145, 158, 171, 0.16)",
};

const hero = {
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  gap: "16px",
  marginBottom: "28px",
};

const heroAccent = {
  fontSize: "2.6rem",
};

const badge = {
  display: "inline-block",
  marginBottom: "10px",
  padding: "6px 14px",
  borderRadius: "999px",
  background: "#e6f7ef",
  color: "#1f8b63",
  fontSize: "0.85rem",
  fontWeight: 700,
};

const subtitle = {
  color: "#617d8a",
  lineHeight: 1.65,
  marginTop: "6px",
};

const form = {
  display: "grid",
  gap: "16px",
};

const label = {
  fontSize: "0.95rem",
  color: "#344054",
  fontWeight: 600,
  textAlign: "left",
};

const input = {
  width: "100%",
  padding: "14px 16px",
  borderRadius: "14px",
  border: "1px solid #d7dde5",
  outline: "none",
  fontSize: "1rem",
  transition: "border-color 0.2s ease",
};

const button = {
  width: "100%",
  padding: "14px 16px",
  borderRadius: "14px",
  border: "none",
  background: "linear-gradient(135deg, #2e7d32, #4caf50)",
  color: "#fff",
  fontSize: "1rem",
  fontWeight: 700,
  cursor: "pointer",
  transition: "transform 0.2s ease, box-shadow 0.2s ease",
};

const googleButton = {
  width: "100%",
  boxSizing: "border-box",
  marginTop: "16px",
  padding: "14px 16px",
  borderRadius: "14px",
  border: "1px solid #d1d5db",
  background: "#ffffff",
  color: "#202124",
  textDecoration: "none",
  fontSize: "0.96rem",
  fontWeight: 700,
  cursor: "pointer",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  gap: "10px",
  boxShadow: "0 10px 30px rgba(15, 23, 42, 0.04)",
};

const googleIcon = {
  width: "30px",
  height: "30px",
  borderRadius: "8px",
  background: "#f8f9fa",
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
  color: "#3c4043",
  fontWeight: 700,
};

const switchText = {
  marginTop: "20px",
  color: "#5f6d7a",
  fontSize: "0.95rem",
};

const link = {
  color: "#157bfb",
  cursor: "pointer",
  fontWeight: 700,
};

const errorText = {
  marginTop: "14px",
  color: "#b71c1c",
  fontWeight: 600,
};
