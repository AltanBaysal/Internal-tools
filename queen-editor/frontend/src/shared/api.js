// Single fetch wrapper -- same-origin "/api", so no base URL and no CORS.
export async function getHealth() {
  const resp = await fetch("/api/health");
  if (!resp.ok) throw new Error(`health ${resp.status}`);
  return resp.json();
}
