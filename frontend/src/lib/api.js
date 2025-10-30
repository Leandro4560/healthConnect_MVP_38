import axios from "axios";

// Aceptar VITE_API_URL (preferido) y VITE_APP_API_URL (si lo configuraste por error)
// Preferir la configuración runtime `window.__API_ROOT__` (generada por env.js)
// si está definida. Si no, usar variables Vite en build-time.
const RUNTIME_API_ROOT = (typeof window !== 'undefined' && window.__API_ROOT__) ? String(window.__API_ROOT__).replace(/\/$/, '') : "";
const BUILD_API_ROOT = (
  import.meta.env.VITE_API_URL ||
  import.meta.env.VITE_APP_API_URL || // fallback para la variable que aparece en tu panel
  ""
).replace(/\/$/, '');

export const API_ROOT = RUNTIME_API_ROOT || BUILD_API_ROOT || "";

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
  // Debug: si API_URL apunta al mismo origen y window.__API_ROOT__ está vacío,
  // informamos en consola para facilitar debugging de despliegues en Render.
  // Mostrar warning sólo si claramente no hay configuración en runtime ni en build.
  if (!API_ROOT) {
    console.warn("[api] WARNING: BACKEND_URL no configurado. Las peticiones se harán al mismo origen (esto suele producir 404 en despliegues). Configura BACKEND_URL en el servicio frontend.");
  }
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