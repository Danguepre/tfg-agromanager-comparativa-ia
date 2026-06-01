import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { apiPost, apiGet, getToken, clearSession } from '../api/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Cargar usuario del localStorage al montar
  useEffect(() => {
    const token = getToken();
    if (token) {
      try {
        const stored = localStorage.getItem('user');
        if (stored) {
          setUser(JSON.parse(stored));
        }
      } catch (e) {
        // ignora
      }
    }
    setLoading(false);
  }, []);

  const login = useCallback(async (username, password) => {
    const data = await apiPost('/auth/login', { username, password }, false);
    if (data.access_token) {
      localStorage.setItem('access_token', data.access_token);
      // Intentar obtener datos del usuario desde /users/
      try {
        const users = await apiGet('/users/', true);
        if (Array.isArray(users) && users.length > 0) {
          // Si es admin, devuelve todos los usuarios; tomamos el primero que coincide
          // Lo correcto es tomar el primer elemento que corresponda al usuario logueado
          const tokenData = parseJwt(data.access_token);
          let userData = users[0];
          if (tokenData && tokenData.user_id) {
            const found = users.find(u => u.id === tokenData.user_id);
            if (found) userData = found;
          }
          setUser(userData);
          localStorage.setItem('user', JSON.stringify(userData));
        }
      } catch (e) {
        // Si falla, al menos tenemos token
      }
    }
    return data;
  }, []);

  const register = useCallback(async (userData) => {
    const data = await apiPost('/users/', userData, false);
    return data;
  }, []);

  const logout = useCallback(() => {
    setUser(null);
    clearSession();
  }, []);

  const isAuthenticated = !!getToken();
  const isAdmin = user?.role === 'admin';

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    isAuthenticated,
    isAdmin,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

function parseJwt(token) {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch (e) {
    return null;
  }
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe usarse dentro de AuthProvider');
  }
  return context;
}

export default AuthContext;