import { useContext } from "react";
import { Link } from "react-router-dom";
import { AuthContext } from "../context/auth-context";
import { parseJwt } from "../utils/auth";

export default function Navbar() {
  const { token, logout } = useContext(AuthContext);
  const currentUser = parseJwt(token || "");

  return (
    <header style={navStyle}>
      <div style={brandStyle}>
        <span style={brandIcon}>🌿</span>
        <h1 style={brandTitle}>AgroManager</h1>
      </div>

      <nav style={menuStyle}>
        <Link to="/dashboard" style={linkStyle}>
          Dashboard
        </Link>
        <Link to="/crops" style={linkStyle}>
          Cultivos
        </Link>
        <Link to="/published-crops" style={linkStyle}>
          Catalogo
        </Link>
        <Link to="/tasks" style={linkStyle}>
          Tareas
        </Link>
        <Link to="/calendar" style={linkStyle}>
          Calendario
        </Link>
        {currentUser?.role === "admin" && (
          <Link to="/admin" style={linkStyle}>
            Admin
          </Link>
        )}
      </nav>

      <button style={buttonStyle} onClick={logout}>
        Logout
      </button>
    </header>
  );
}

const navStyle = {
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  gap: "18px",
  padding: "18px 28px",
  background: "#0F172A",
  color: "#ffffff",
  position: "sticky",
  top: 0,
  zIndex: 1000,
  boxShadow: "0 10px 40px rgba(15, 23, 42, 0.18)",
};

const brandStyle = {
  display: "flex",
  alignItems: "center",
  gap: "10px",
};

const brandIcon = {
  fontSize: "1.4rem",
};

const brandTitle = {
  margin: 0,
  fontSize: "1.2rem",
  fontWeight: 700,
};

const menuStyle = {
  display: "flex",
  alignItems: "center",
  gap: "18px",
};

const linkStyle = {
  color: "#CBD5E1",
  textDecoration: "none",
  fontWeight: 600,
};

const buttonStyle = {
  background: "#22C55E",
  border: "none",
  color: "white",
  padding: "10px 18px",
  borderRadius: "999px",
  cursor: "pointer",
  fontWeight: 700,
};
