// Single fetch wrapper -- same-origin "/api", so no base URL and no CORS.
// On failure it throws the server's own message: the rules (and their Turkish wording) live in the
// backend, and the UI prints whatever comes back.

// fetch has no timeout of its own; when the Colab runtime dies, the Cloudflare edge can hold a
// request open for minutes, so the poll's catch never fires and the screen freezes on stale state.
const TIMEOUT_MS = 10_000;

async function request(path, options) {
  let resp;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
  try {
    resp = await fetch(path, { ...options, signal: controller.signal });
  } catch (err) {
    // fetch rejects with a browser-English TypeError (or AbortError on timeout) when the tunnel is
    // unreachable; say it in Turkish and keep the raw text underneath (we never guess the cause).
    const detail = err.name === "AbortError" ? `Zaman aşımı (${TIMEOUT_MS / 1000} sn)` : err.message;
    throw new Error(`Sunucuya ulaşılamadı — bağlantıyı kontrol et.\n${detail}`);
  } finally {
    clearTimeout(timer);
  }
  let body = null;
  try {
    body = await resp.json();
  } catch {
    body = null; // empty or non-JSON body (e.g. a tunnel error page)
  }
  if (!resp.ok) {
    const err = new Error(body?.error || `${resp.status} ${resp.statusText}`);
    // Which input the server blamed, when it says so -- the panel marks that box (spec §4).
    if (body?.field) err.field = body.field;
    throw err;
  }
  return body;
}

export async function listProjects() {
  const body = await request("/api/projects");
  return body.projects;
}

export async function createProject(name) {
  return request("/api/projects", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
}

// Would this name be accepted? Asked while it is being typed, so the box can warn without keeping
// a copy of the rules -- the answer is the server's own sentence, or null.
export async function checkProjectName(name) {
  return request(`/api/projects/name-check?name=${encodeURIComponent(name)}`);
}

export async function getSettings(project) {
  return request(`/api/projects/${encodeURIComponent(project)}/settings`);
}

export async function saveSettings(project, { prompts, negative, variants, model }) {
  return request(`/api/projects/${encodeURIComponent(project)}/settings`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompts, negative, variants, model }),
  });
}

export async function generateBatch(project, { prompts, negative, variants, model }) {
  return request(`/api/projects/${encodeURIComponent(project)}/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompts, negative, variants, model }),
  });
}

// Which models can render right now. Not a project's question: the renderer answers it, and the
// app keeps no list of its own (the notebook decides what is installed).
export async function listModels() {
  const body = await request("/api/models");
  return body.models;
}

export async function stopGeneration() {
  return request("/api/stop", { method: "POST" });
}

export async function resumeBatch(project) {
  return request(`/api/projects/${encodeURIComponent(project)}/resume`, { method: "POST" });
}


export async function retryFrame(project, file) {
  return request(`/api/projects/${encodeURIComponent(project)}/retry`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ file }),
  });
}

export async function cancelGeneration(project) {
  return request(`/api/projects/${encodeURIComponent(project)}/cancel`, { method: "POST" });
}

export async function saveOrder(project, order) {
  return request(`/api/projects/${encodeURIComponent(project)}/order`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ order }),
  });
}

// The whole gallery in one answer: produced photos, pending frames and failed ones alike, in the
// order they are shown. This is what survives a dead session -- it is read from Drive, not memory.
export async function listFrames(project) {
  const body = await request(`/api/projects/${encodeURIComponent(project)}/frames`);
  return body.frames;
}

// One call for one frame and for many, and for photos and pending frames alike -- the confirm box
// is a single window over a mixed selection. The answer splits what really happened:
// {deleted: [...], removed: [...]}.
export async function removeFrames(project, files) {
  return request(`/api/projects/${encodeURIComponent(project)}/frames/delete`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ files }),
  });
}

// 204 with no body: request() reads nothing back and answers null, which is the whole result.
export async function deleteProject(project) {
  return request(`/api/projects/${encodeURIComponent(project)}`, { method: "DELETE" });
}

export async function getStatus() {
  return request("/api/status");
}

// Plain URL, not a fetch: the browser loads it into an <img>.
export function photoUrl(project, file) {
  return `/photos/${encodeURIComponent(project)}/${encodeURIComponent(file)}`;
}

// Also a plain URL: the browser downloads it straight from the link (see ProjectScreen).
export function exportUrl(project) {
  return `/api/projects/${encodeURIComponent(project)}/export`;
}
