import axios from "axios";

export const API_URL = import.meta.env.VITE_APP_API_URL || "http://localhost:8000/api/v1";

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