// Single fetch wrapper -- same-origin "/api", so no base URL and no CORS.
// On failure it throws the server's own message: the rules (and their Turkish wording) live in the
// backend, and the UI prints whatever comes back.
async function request(path, options) {
  const resp = await fetch(path, options);
  let body = null;
  try {
    body = await resp.json();
  } catch {
    body = null; // empty or non-JSON body (e.g. a tunnel error page)
  }
  if (!resp.ok) throw new Error(body?.error || `${resp.status} ${resp.statusText}`);
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

export async function generatePhoto(project, prompt) {
  return request(`/api/projects/${encodeURIComponent(project)}/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt }),
  });
}

export async function getStatus() {
  return request("/api/status");
}

// Plain URL, not a fetch: the browser loads it into an <img>.
export function photoUrl(project, file) {
  return `/photos/${encodeURIComponent(project)}/${encodeURIComponent(file)}`;
}
