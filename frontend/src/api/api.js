// const BASE = "https://ranjittommy08-pdfchatbot.hf.space";
// const BASE = "http://127.0.0.1:8000";
const BASE = "";


export const uploadPDF = (file) => {
  const formData = new FormData();
  formData.append("file", file);

  return fetch(`${BASE}/upload`, {
    method: "POST",
    body: formData,
  });
};

export const getFiles = () =>
  fetch(`${BASE}/files`).then((res) => res.json());

export const deleteFile = (name) =>
  fetch(`${BASE}/files/${name}`, { method: "DELETE" });

export const chat = async (question, files) => {
  const token = localStorage.getItem("access_token");
  const headers = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${BASE}/chat`, {
    method: "POST",
    headers,
    body: JSON.stringify({ question, file_names: files }),
  });

  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || "Chat request failed");
  }

  return res; // <-- Return the raw response so we can read its stream body
};

export const signup = (payload) =>
  fetch(`${BASE}/auth/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  }).then((r) => r.json());

export const login = (payload) =>
  fetch(`${BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  }).then((r) => r.json());

export const me = () => {
  const token = localStorage.getItem("access_token");
  return fetch(`${BASE}/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  }).then((r) => r.json());
};