import { createContext } from "react";
import { useContext } from "react";
import { useState } from "react";
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

const AuthContext = createContext();

import { API_URL, api } from "../lib/api";
// usa `api` o `API_URL` según necesites

export const AuthContextProvider = ({ children }) => {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);

  const saveToken = (token) => {
    if (token) {
      localStorage.setItem("hc_token", token);
    }
  };

  const saveRefresh = (refresh) => {
    if (refresh) localStorage.setItem("hc_refresh", refresh);
  };

  const getToken = () => localStorage.getItem("hc_token");

  const clearToken = () => localStorage.removeItem("hc_token");
  const clearRefresh = () => localStorage.removeItem("hc_refresh");
  const clearAll = () => {
    clearToken();
    clearRefresh();
  };

  let refreshTimer = null;

  const scheduleRefresh = (accessToken) => {
    try {
      if (!accessToken) return;
      // JWT formato: header.payload.signature
      const parts = accessToken.split('.');
      if (parts.length < 2) return;
      const payload = JSON.parse(atob(parts[1].replace(/-/g, '+').replace(/_/g, '/')));
      const exp = payload.exp;
      if (!exp) return;
      const now = Math.floor(Date.now() / 1000);
      // refrescar 60 segundos antes de exp
      const when = (exp - now - 60) * 1000;
      if (when <= 0) {
        // intentar refresh inmediatamente
        refreshAccessToken();
        return;
      }
      if (refreshTimer) clearTimeout(refreshTimer);
      refreshTimer = setTimeout(() => {
        refreshAccessToken();
      }, when);
    } catch (e) {
      console.error("scheduleRefresh error", e);
    }
  };

  const refreshAccessToken = async () => {
    try {
      const refresh = localStorage.getItem("hc_refresh");
      if (!refresh) {
        signOut();
        return null;
      }
      const res = await fetch(`${API_URL}/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refresh }),
      });
      if (!res.ok) {
        // no se pudo refrescar
        clearAll();
        setUser(null);
        return null;
      }
      const data = await res.json();
      const newAccess = data.access_token;
      const newRefresh = data.refresh_token;
      saveToken(newAccess);
      saveRefresh(newRefresh);
      scheduleRefresh(newAccess);
      setUser(data.user || null);
      return data;
    } catch (e) {
      console.error("refreshAccessToken error", e);
      clearAll();
      setUser(null);
      return null;
    }
  };

  async function register(userData) {
    try {
  const res = await fetch(`${API_URL}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(userData),
      });
      if (!res.ok) {
        if (res.status === 429) {
          // Intento de rate limit — devolver mensaje amigable
          const retry = res.headers.get("Retry-After");
          throw new Error(retry ? `Demasiadas solicitudes. Intenta nuevamente en ${retry} segundos.` : "Demasiadas solicitudes. Intenta nuevamente en unos segundos.");
        }
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "Error registrando usuario");
      }
      const data = await res.json();
      return data;
    } catch (error) {
      console.error("register error", error);
      throw error;
    }
  }

  async function login(email, password) {
    try {
      const body = new URLSearchParams();
      body.append("username", email);
      body.append("password", password);

  const res = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: body.toString(),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "Credenciales inválidas");
      }

      const data = await res.json();
      const token = data.access_token;
      const refresh = data.refresh_token;
      saveToken(token);
      saveRefresh(refresh);
      scheduleRefresh(token);
  setUser(data.user || null);
  navigate("/dashboard", { replace: true });
      return data;
    } catch (error) {
      console.error("login error", error);
      throw error;
    }
  }

  async function fetchMe() {
    try {
      const token = getToken();
      if (!token) return null;
      const res = await fetch(`${API_URL}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) {
        clearToken();
        setUser(null);
        return null;
      }
      const data = await res.json();
      setUser(data);
      return data;
    } catch (error) {
      console.error("fetchMe error", error);
      return null;
    }
  }

  const setTokenFromString = async (token) => {
    try {
      // token puede ser string (access) o un objeto {access, refresh}
      if (typeof token === "string") {
        saveToken(token);
        scheduleRefresh(token);
      } else if (token && token.access_token) {
        saveToken(token.access_token);
        saveRefresh(token.refresh_token);
        scheduleRefresh(token.access_token);
      }
  const data = await fetchMe();
  if (data) navigate("/dashboard", { replace: true });
    } catch (e) {
      console.error("setTokenFromString error", e);
    }
  };

  function signInWithGoogle() {
    // Redirige al backend que controla el flujo OAuth (backend -> Google -> backend callback)
    window.location.href = `${API_URL}/auth/google/login`;
  }

  function signOut() {
    clearAll();
    setUser(null);
    navigate("/", { replace: true });
  }

  useEffect(() => {
    // Al montar intentamos cargar el usuario si hay token
    // Si hay token, cargar usuario y programar refresh
    const t = getToken();
    if (t) {
      scheduleRefresh(t);
    }
    fetchMe();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <AuthContext.Provider value={{ user, login, register, signInWithGoogle, signOut, setTokenFromString }}>
      {children}
    </AuthContext.Provider>
  );
};

export const userAuth = () => useContext(AuthContext);
