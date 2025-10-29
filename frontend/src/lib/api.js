import axios from "axios";

// Aceptar VITE_API_URL (preferido) y VITE_APP_API_URL (si lo configuraste por error)
export const API_ROOT = (
  import.meta.env.VITE_API_URL ||
  import.meta.env.VITE_APP_API_URL || // fallback para la variable que aparece en tu panel
  ""
).replace(/\/$/, '') || window.__API_ROOT__ || "";

export const API_URL = (API_ROOT ? API_ROOT.replace(/\/$/, '') : window.location.origin.replace(/\/$/, '')) + "/api/v1";

function joinPath(path) {
  return API_URL.replace(/\/+$/,"") + "/" + path.replace(/^\/+/,"");
}

export const api = axios.create({
  baseURL: API_URL,
  headers: { "Content-Type": "application/json" },
});

export async function apiFetch(path, options = {}) {
  const url = joinPath(path);
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  const resp = await fetch(url, { ...options, headers });
  if (!resp.ok) {
    const body = await resp.json().catch(()=>({}));
    const err = new Error(body.detail || resp.statusText || "Error");
    err.response = body;
    throw err;
  }
  return resp.json().catch(()=>({}));
}