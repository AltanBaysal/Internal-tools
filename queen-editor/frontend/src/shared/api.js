// Single fetch wrapper -- same-origin "/api", so no base URL and no CORS.
// On failure it throws the server's own message: the rules (and their Turkish wording) live in the
// backend, and the UI prints whatever comes back. The proof of what happened rides beside it on
// the error's `evidence`, for the panels that offer it to be copied.

// fetch has no timeout of its own; when the Colab runtime dies, the Cloudflare edge can hold a
// request open for minutes, so the poll's catch never fires and the screen freezes on stale state.
const TIMEOUT_MS = 10_000;
// An upload is not one of those: a fifteen second video onto Drive can take minutes, and cutting it
// at ten seconds tells the user the server is unreachable -- about the wrong thing entirely.
const UPLOAD_TIMEOUT_MS = 120_000;

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
  // Ours, not fetch's: it is taken out of the options so nothing hands the browser a key it has no
  // use for.
  const { timeout = TIMEOUT_MS, ...sent } = options || {};
  let resp;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeout);
  try {
    resp = await fetch(path, { ...sent, signal: controller.signal });
  } catch (err) {
    // fetch rejects with a browser-English TypeError (or AbortError on timeout) when the tunnel is
    // unreachable. AbortError's own text names our own abort rather than the server, so what goes
    // down is what we can honestly say: which request, and that we cut it after ten seconds.
    const detail = err.name === "AbortError" ? `Zaman aşımı (${timeout / 1000} sn)` : err.message;
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
// The address is the name the project has today and the body is the one it is getting: a project IS
// its folder, so the folder it is in now is where the request has to go.
export async function renameProject(project, name) {
  return request(`/api/projects/${encodeURIComponent(project)}/rename`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
}

export async function checkProjectName(name) {
  return request(`/api/projects/name-check?name=${encodeURIComponent(name)}`);
}

export async function getSettings(project) {
  return request(`/api/projects/${encodeURIComponent(project)}/settings`);
}

export async function saveSettings(project, { prompts, negative, variants, model, lora,
                                               orientation }) {
  return request(`/api/projects/${encodeURIComponent(project)}/settings`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompts, negative, variants, model, lora, orientation }),
  });
}

// Referanstan's own record (madde 317): what its boxes open with once a visit's draft is gone. An
// address of its own because it is written at a moment of its own -- a reference production, not a
// photo batch.
export async function getReferenceSettings(project) {
  return request(`/api/projects/${encodeURIComponent(project)}/reference-settings`);
}

export async function saveReferenceSettings(project, { prompts, variants, orientation }) {
  return request(`/api/projects/${encodeURIComponent(project)}/reference-settings`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompts, variants, orientation }),
  });
}

// How long the project's H3 videos run (madde 422, 424): 4, 8 or 12 seconds. With nothing saved the
// server answers 8 -- the default is its to say, not the screen's.
export async function getVideoLength(project) {
  const body = await request(`/api/projects/${encodeURIComponent(project)}/video-length`);
  return body.seconds;
}

// 204 with no body: the screen already shows what it sent.
export async function saveVideoLength(project, seconds) {
  return request(`/api/projects/${encodeURIComponent(project)}/video-length`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ seconds }),
  });
}

// The project's Mutlu son switch (madde 426): on or off. With nothing saved the server answers off.
export async function getHappyEnding(project) {
  const body = await request(`/api/projects/${encodeURIComponent(project)}/happy-ending`);
  return body.on;
}

// 204 with no body, like the length's.
export async function saveHappyEnding(project, on) {
  return request(`/api/projects/${encodeURIComponent(project)}/happy-ending`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ on }),
  });
}

// The frames whose sound is turned off (madde 510), by identity.
export async function getMuted(project) {
  const body = await request(`/api/projects/${encodeURIComponent(project)}/muted`);
  return body.frames;
}

// A state, not a toggle: true turns the frame's sound off, false on. Answers with the new list.
export async function saveMuted(project, frame, muted) {
  const body = await request(
    `/api/projects/${encodeURIComponent(project)}/frames/${encodeURIComponent(frame)}/muted`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ muted }),
    });
  return body.frames;
}

// `orientation` is yatay or dikey (madde 477): the size the batch's photos are made at.
export async function generateBatch(project, { prompts, negative, variants, model, lora,
                                               orientation }) {
  return request(`/api/projects/${encodeURIComponent(project)}/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompts, negative, variants, model, lora, orientation }),
  });
}

// What can render right now: `{models, loras}`, the two boxes of the photo panel. Not a project's
// question: the notebook decides which models are installed and the server reports them.
export async function listModels() {
  return request("/api/models");
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
// `orientation`, like `negative`, is a photo's alone (madde 477): undefined leaves it out of the body.
export async function regenerateFrame(project, frame, layer, prompt, mode, negative, orientation) {
  return request(`/api/projects/${encodeURIComponent(project)}/regenerate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ frame, layer, prompt, mode, negative, orientation }),
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

// Take a layer's waiting job out of the queue (madde 516). The frame stays with everything it holds,
// and a layer that has landed meanwhile stays too. A door of its own, never a mode of removeLayer:
// that one deletes. The answer names the jobs really taken out.
export async function dequeueLayer(project, frames, kind) {
  return request(`/api/projects/${encodeURIComponent(project)}/layers/${kind}/dequeue`, {
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

// The archive is a folder beside the projects, so these read and write the same way the projects
// do; nothing is deleted by either.
export async function listArchivedProjects() {
  const body = await request("/api/projects/archived");
  return body.projects;
}

export async function archiveProject(project) {
  return request(`/api/projects/${encodeURIComponent(project)}/archive`, { method: "POST" });
}

export async function restoreProject(project) {
  return request(`/api/projects/${encodeURIComponent(project)}/restore`, { method: "POST" });
}

export async function getStatus() {
  return request("/api/status");
}

// How many times the queue has ended and how it last did, as the server keeps them (madde 509):
// { ended, last }.
// Asked from a count, the server holds the answer until the count moves or 50 seconds pass -- long
// polling, since the Quick Tunnel holds a streaming body until it ends -- so the wait outlasts the
// server's hold and stays under the tunnel's cut of about 100 quiet seconds. With no count, at once.
const ENDED_ASK_TIMEOUT_MS = 80_000;

export async function waitForEnded(after) {
  const since = after === null ? "" : `?after=${after}`;
  return request(`/api/queue/ended${since}`, { timeout: ENDED_ASK_TIMEOUT_MS });
}

// Plain URL, not a fetch: the browser loads it into an <img>, a <video> or an <audio>. Any file
// the project folder holds is reachable this way; the route is still called /photos because that is
// the server's own name for the project's file area.
export function fileUrl(project, file) {
  return `/photos/${encodeURIComponent(project)}/${encodeURIComponent(file)}`;
}

// The project's reference pool (madde 297). The answer carries the limits beside the files, so the
// panel can head a row with 4/9 without keeping its own copy of the numbers.
export async function listReferences(project) {
  return request(`/api/projects/${encodeURIComponent(project)}/references`);
}

// A form rather than JSON, and no Content-Type of ours: multipart carries a boundary, and only the
// browser knows what it wrote. The kind is the row whose Ekle card picked the files: the server
// holds them to it (madde 320).
export async function uploadReferences(project, files, kind) {
  const form = new FormData();
  for (const file of files) form.append("files", file);
  form.append("kind", kind);
  return request(`/api/projects/${encodeURIComponent(project)}/references`,
                 { method: "POST", body: form, timeout: UPLOAD_TIMEOUT_MS });
}

// The order a drag made, per kind. The whole row goes down because a slot is a place in a sequence
// (madde 300).
export async function saveReferenceOrder(project, order) {
  return request(`/api/projects/${encodeURIComponent(project)}/references/order`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ order }),
  });
}

export async function removeReference(project, name) {
  return request(`/api/projects/${encodeURIComponent(project)}/references/`
                 + `${encodeURIComponent(name)}/delete`, { method: "POST" });
}

// A production made of the pool rather than of a frame: no frames go up, and what comes back are
// cards (madde 302, 303). Its own door for that reason -- the layer one is about frames that exist.
// A card has no photo whose shape its video could follow, so it carries an orientation (madde 477).
export async function produceFromReferences(project, prompts, variants, orientation) {
  return request(`/api/projects/${encodeURIComponent(project)}/references/produce`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompts, variants, orientation }),
  });
}

// Plain URL, like fileUrl: the pool's own file area, which the browser loads into a tag.
export function referenceUrl(project, name) {
  return `/references/${encodeURIComponent(project)}/${encodeURIComponent(name)}`;
}

// The agent's chats (madde 417, 420): a chat is named by its number inside the project. The empty
// chat waiting comes back rather than a new one -- the server never makes a second.
export async function newChat(project) {
  return request(`/api/projects/${encodeURIComponent(project)}/chats`, { method: "POST" });
}

// Only the chats with a question, the newest last question first, each first question whole.
export async function listChats(project) {
  const body = await request(`/api/projects/${encodeURIComponent(project)}/chats`);
  return body.chats;
}

export async function openChat(project, chat) {
  return request(`/api/projects/${encodeURIComponent(project)}/chats/${chat}`);
}

// Answers at once with the chat, the question last and no outcome yet: the agent goes on on the
// server.
export async function askQuestion(project, chat, text) {
  return request(`/api/projects/${encodeURIComponent(project)}/chats/${chat}/questions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
}

export async function stopAgent(project, chat) {
  return request(`/api/projects/${encodeURIComponent(project)}/chats/${chat}/stop`,
                 { method: "POST" });
}

// { working, asking }: which chats' agents work now, and the changes they wait on the user for
// (madde 480), each { chat, id, change }. It lives in the server's memory, not in the chats' record,
// so it is a door of its own.
export async function workingChats(project) {
  return request(`/api/projects/${encodeURIComponent(project)}/chats/working`);
}

// İzin ver (`allow` true) or Reddet to change `id`; answers with { working, asking } as they stand
// after it. A change no longer waiting is refused in the server's words.
export async function answerPermission(project, chat, id, allow) {
  return request(`/api/projects/${encodeURIComponent(project)}/chats/${chat}/permission`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id, allow }),
  });
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
