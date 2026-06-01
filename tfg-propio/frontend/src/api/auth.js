import { API_URL } from "./api";

export async function loginRequest(email, password) {
  const res = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email: email,
      password: password,
    }),
  });

  if (!res.ok) {
    throw new Error("Login incorrecto");
  }

  return res.json();
}

export async function registerRequest(user) {
  const res = await fetch(`${API_URL}/users/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(user),
  });

  if (!res.ok) {
    throw new Error("Error al registrar usuario");
  }

  return res.json();
}
