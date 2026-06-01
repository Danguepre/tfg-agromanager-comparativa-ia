import { useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";

export default function OAuthCallback({ onLogin }) {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const token = params.get("token");
    const oauthError = params.get("error");
    console.info("[OAuthCallback] Route reached", {
      path: location.pathname,
      hasToken: Boolean(token),
      hasError: Boolean(oauthError),
      searchLength: location.search.length,
    });

    if (token) {
      localStorage.setItem("token", token);
      console.info("[OAuthCallback] Token saved in localStorage. Redirecting to /");
      if (onLogin) {
        onLogin(token);
      }
      navigate("/", { replace: true });
    } else {
      console.warn("[OAuthCallback] Missing token. Redirecting to /login", { oauthError });
      navigate("/login", { replace: true, state: { oauthError } });
    }
  }, [location.pathname, location.search, onLogin, navigate]);

  return (
    <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100vh" }}>
      <p>Procesando inicio de sesión...</p>
    </div>
  );
}
