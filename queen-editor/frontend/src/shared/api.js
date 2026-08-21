// Single fetch wrapper -- same-origin "/api", so no base URL and no CORS.
// On failure it throws the server's own message: the rules (and their Turkish wording) live in the
// backend, and the UI prints whatever comes back. The proof of what happened rides beside it on
// the error's `evidence`, for the panels that offer it to be copied.

// fetch has no timeout of its own; when the Colab runtime dies, the Cloudflare edge can hold a
// request open for minutes, so the poll's catch never fires and the screen freezes on stale state.
const TIMEOUT_MS = 10_000;

// The sentence a panel shows, and beside it what a developer needs to act: which request, what came
// back, and the body verbatim. Never a guessed cause -- every line is either what we did or what
// the service said.
function failure(said, evidence) {
  const err = new Error(said);
  err.evidence = evidence;
  return err;
}

async function request(path, options) {
  const method = options?.method || "GET";
  let resp;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
  try {
    resp = await fetch(path, { ...options, signal: controller.signal });
  } catch (err) {
    // fetch rejects with a browser-English TypeError (or AbortError on timeout) when the tunnel is
    // unreachable. AbortError's own text names our own abort rather than the server, so what goes
    // down is what we can honestly say: which request, and that we cut it after ten seconds.
    const detail = err.name === "AbortError" ? `Zaman aşımı (${TIMEOUT_MS / 1000} sn)` : err.message;
    throw failure("Sunucuya ulaşılamadı — bağlantıyı kontrol et.", `${method} ${path}\n${detail}`);
  } finally {
    clearTimeout(timer);
  }
  // Bytes first, parsing after. A body is read once and only once, so parsing straight into JSON
  // threw away every answer that was not JSON -- which is exactly what a tunnel's error page is.
  const raw = await resp.text();
  let body = null;
  try {
    body = JSON.parse(raw);
  } catch {
    body = null; // empty or non-JSON body (e.g. a tunnel error page)
  }
  if (!resp.ok) {
    // The server's sentence is an answer, not a diagnosis: the same words come back with a 400 and
    // with a 500, so the code goes into the evidence even when there is a sentence to show.
    const err = failure(body?.error || `${resp.status} ${resp.statusText}`,
                        `${method} ${path}\n${resp.status} ${resp.statusText}\n${raw}`);
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

// Hang a layer on every frame in scope. No "files" key means every frame that does not hold it; a
// list means that selection. `variants` is how many each of them gets: the ones past the first are
// born as copy frames. `mode` is how a video ends -- plain, looping, or on the next frame's picture.
export async function queueLayer(project, kind, files, variants, mode) {
  return request(`/api/projects/${encodeURIComponent(project)}/layers/${kind}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...(files === null ? {} : { files }), variants, mode }),
  });
}

// Make one frame's layer again, with the words the user has in front of them. The answer names the
// frame it will be made on -- a new one, never the frame it was asked from.
//
// The frame is named by its identity rather than by a file, here and in removeLayer: a copy frame
// shares its source's picture, so one file name can belong to two frames.
export async function regenerateFrame(project, frame, layer, prompt, mode, negative) {
  return request(`/api/projects/${encodeURIComponent(project)}/regenerate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ frame, layer, prompt, mode, negative }),
  });
}

// Take one layer off a frame. The frame stays in the gallery: what goes is this layer and whatever
// lies over it. The answer says which files really left the disk.
// One call for one frame and for many, the same as deleting frames: the bar takes a layer off a
// whole selection and the detail page takes it off one.
export async function removeLayer(project, frames, kind) {
  return request(`/api/projects/${encodeURIComponent(project)}/layers/${kind}/delete`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ frames }),
  });
}

// Which producers this machine has, and which of them are installed. Not a project's question --
// the models live next to the renderer, not in a project folder.
export async function listProducers() {
  const body = await request("/api/producers");
  return body.producers;
}

export async function stopGeneration() {
  return request("/api/stop", { method: "POST" });
}

export async function resumeBatch(project) {
  return request(`/api/projects/${encodeURIComponent(project)}/resume`, { method: "POST" });
}


export async function retryFrame(project, frame) {
  return request(`/api/projects/${encodeURIComponent(project)}/retry`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ frame }),
  });
}

// No frame named: the server reads that as "all of them" (see the retry endpoint).
export async function retryFailed(project) {
  return request(`/api/projects/${encodeURIComponent(project)}/retry`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({}),
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
// is a single window over a mixed selection. Frames are named by their identities, and the answer
// splits what really happened in the same words: {deleted: [...], removed: [...]}.
export async function removeFrames(project, frames) {
  return request(`/api/projects/${encodeURIComponent(project)}/frames/delete`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ frames }),
  });
}

// The twins of the frames named, born beside them. Identities again, the same as the delete call,
// and the answer carries both their names and the gallery they landed in.
export async function copyFrames(project, frames) {
  return request(`/api/projects/${encodeURIComponent(project)}/frames/copy`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ frames }),
  });
}

// 204 with no body: request() reads nothing back and answers null, which is the whole result.
export async function deleteProject(project) {
  return request(`/api/projects/${encodeURIComponent(project)}`, { method: "DELETE" });
}

export async function getStatus() {
  return request("/api/status");
}

// Plain URL, not a fetch: the browser loads it into an <img>, a <video> or an <audio>. Any file
// the project folder holds is reachable this way; the route is still called /photos because that is
// the server's own name for the project's file area.
export function fileUrl(project, file) {
  return `/photos/${encodeURIComponent(project)}/${encodeURIComponent(file)}`;
}

// What an export would write: how many videos, how long they run, and the folder they would land
// in. Nothing is created by asking -- the export screen is the step that asks before it runs.
export async function getExportSummary(project) {
  return request(`/api/projects/${encodeURIComponent(project)}/export/summary`);
}

// Start writing. 202: the files take minutes, and how far it has got is read from the state.
export async function startExport(project, mode) {
  return request(`/api/projects/${encodeURIComponent(project)}/export/${mode}`, { method: "POST" });
}

// Both modes in one answer: one can be running while the other is finished.
export async function getExportState(project) {
  return request(`/api/projects/${encodeURIComponent(project)}/export/status`);
}

// Leaving the screen cancels whatever it started -- an export is session-bound (madde 96).
export async function cancelExport(project) {
  return request(`/api/projects/${encodeURIComponent(project)}/export/cancel`, { method: "POST" });
}
