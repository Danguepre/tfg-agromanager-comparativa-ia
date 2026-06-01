import { useState } from "react";
import { registerRequest, loginRequest } from "../api/auth";

export default function SignUp({ onSwitch, onLogin }) {
  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    location: ""
  });

  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value
    });
  };

  const handleRegister = async () => {
    setLoading(true);
    setError(null);

    try {
      await registerRequest(form);

      const data = await loginRequest(form.email, form.password);

      localStorage.setItem("token", data.access_token);

      onLogin(data.access_token);

    } catch {
      setError("❌ Error al registrar o login automático");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={container}>
      <h2>🌿 Crear cuenta</h2>

      <input name="name" placeholder="Nombre" onChange={handleChange} style={input}/>
      <input name="email" placeholder="Email" onChange={handleChange} style={input}/>
      <input name="password" type="password" placeholder="Contraseña" onChange={handleChange} style={input}/>
      <input name="location" placeholder="Ubicación" onChange={handleChange} style={input}/>

      <button onClick={handleRegister} style={button} disabled={loading}>
        {loading ? "Creando..." : "Registrarse"}
      </button>

      <p onClick={onSwitch} style={switchText}>
        ¿Ya tienes cuenta? Inicia sesión
      </p>

      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}


const container = {
  padding: "40px",
  maxWidth: "320px",
  margin: "100px auto",
  textAlign: "center",
  background: "#f4f9f4",
  borderRadius: "12px",
  boxShadow: "0 4px 12px rgba(0,0,0,0.1)"
};

const input = {
  display: "block",
  marginBottom: "12px",
  padding: "10px",
  width: "100%",
  borderRadius: "6px",
  border: "1px solid #ccc"
};

const button = {
  background: "#4CAF50",
  color: "white",
  border: "none",
  padding: "10px",
  width: "100%",
  borderRadius: "8px",
  cursor: "pointer",
  fontWeight: "bold"
};

const switchText = {
  marginTop: "12px",
  cursor: "pointer",
  color: "#2e7d32"
};
