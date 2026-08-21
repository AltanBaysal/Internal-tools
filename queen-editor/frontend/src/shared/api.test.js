import { describe, expect, it, vi } from "vitest";

import {
  createProject,
  getSettings,
  getStatus,
  listFrames,
  listProjects,
  queueLayer,
  saveOrder,
} from "./api.js";

function okResponse(body) {
  const text = JSON.stringify(body);
  return { ok: true, status: 200, statusText: "OK", text: async () => text, json: async () => body };
}

// A failed response the way a tunnel really answers: a body of bytes, which may or may not be
// JSON. json() throwing on a page of HTML is exactly what the real one does.
function errorResponse(status, statusText, text) {
  return { ok: false, status, statusText,
           text: async () => text, json: async () => JSON.parse(text) };
}

describe("api.request", () => {
  it("percent-encodes the project name in the URL", async () => {
    const fetchMock = vi.fn().mockResolvedValue(okResponse({ frames: [] }));
    vi.stubGlobal("fetch", fetchMock);

    await listFrames("düğün fotoğrafları");

    const url = fetchMock.mock.calls[0][0];
    expect(url).toBe(`/api/projects/${encodeURIComponent("düğün fotoğrafları")}/frames`);
    expect(url).not.toContain("düğün");
  });

  it("throws the server's own text when the server rejects a request", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(
      errorResponse(404, "NOT FOUND", JSON.stringify({ error: "Proje bulunamadı: düğün" }))));

    await expect(getSettings("düğün")).rejects.toThrow("Proje bulunamadı: düğün");
  });

  it("shows the status and its text when the error body is not JSON", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(
      errorResponse(502, "Bad Gateway", "<html><body>error code: 1033</body></html>")));

    await expect(getSettings("düğün")).rejects.toThrow("502 Bad Gateway");
  });

  it("names the request that never answered", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("Failed to fetch")));

    const failure = await listProjects().catch((err) => err);

    // The sentence is what is read, the proof is what is copied. The browser's own text living in
    // both would be one fact kept in two places.
    expect(failure.message).toBe("Sunucuya ulaşılamadı — bağlantıyı kontrol et.");
    expect(failure.evidence).toBe("GET /api/projects\nFailed to fetch");
  });

  it("aborts a request that goes 10 seconds without an answer", async () => {
    vi.useFakeTimers();
    // A dead tunnel answers nothing at all: this fetch settles only if the abort signal fires.
    vi.stubGlobal("fetch", vi.fn((path, options) => new Promise((_, reject) => {
      options.signal.addEventListener("abort", () => {
        const err = new Error("The operation was aborted.");
        err.name = "AbortError";
        reject(err);
      });
    })));

    const pending = getStatus().catch((err) => err);
    await vi.advanceTimersByTimeAsync(10_000);
    const failure = await pending;

    expect(failure.message).toBe("Sunucuya ulaşılamadı — bağlantıyı kontrol et.");
    // AbortError's own text names our abort, not the server: it would be evidence of nothing.
    // What we can honestly say is which request we cut, and after how long.
    expect(failure.evidence).toBe("GET /api/status\nZaman aşımı (10 sn)");
  });

  it("sends the ordering with PUT", async () => {
    const fetchMock = vi.fn().mockResolvedValue(okResponse({ order: ["1_a.png"] }));
    vi.stubGlobal("fetch", fetchMock);

    await saveOrder("düğün", ["1_a.png"]);

    const [url, options] = fetchMock.mock.calls[0];
    expect(url).toBe(`/api/projects/${encodeURIComponent("düğün")}/order`);
    expect(options.method).toBe("PUT");
    expect(JSON.parse(options.body)).toEqual({ order: ["1_a.png"] });
  });

  it("carries the production mode into the queue request", async () => {
    // The panel is where the mode is chosen and the plan is where it lands; this line is the only
    // thing between them, and a body that quietly drops the key would leave every video standard
    // with nothing on screen to say so.
    const fetchMock = vi.fn().mockResolvedValue(okResponse({ added: 1 }));
    vi.stubGlobal("fetch", fetchMock);

    await queueLayer("düğün", "video", ["0_a.png"], 2, "loop");

    const [url, options] = fetchMock.mock.calls[0];
    expect(url).toBe(`/api/projects/${encodeURIComponent("düğün")}/layers/video`);
    expect(JSON.parse(options.body)).toEqual({ files: ["0_a.png"], variants: 2, mode: "loop" });
  });

  it("does not abort a request after its answer has arrived", async () => {
    vi.useFakeTimers();
    let signal;
    vi.stubGlobal("fetch", vi.fn((path, options) => {
      signal = options.signal;
      return Promise.resolve(okResponse({ status: "idle" }));
    }));

    await getStatus();
    await vi.advanceTimersByTimeAsync(30_000);

    expect(signal.aborted).toBe(false);
  });

  it("names the request that failed", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(
      errorResponse(400, "BAD REQUEST", JSON.stringify({ error: "Bu ad zaten var." }))));

    const failure = await createProject("düğün").catch((err) => err);

    // Read from the request, never assumed: a hardcoded GET would name the wrong call for every
    // POST in this file, and naming the wrong request is worse than naming none.
    expect(failure.evidence.split("\n")[0]).toBe("POST /api/projects");
  });

  it("keeps the body a tunnel sent instead of JSON", async () => {
    const page = "<html><body>error code: 1033</body></html>";
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(errorResponse(502, "Bad Gateway", page)));

    const failure = await listProjects().catch((err) => err);

    // What used to disappear: the body was dropped the moment it would not parse, taking the one
    // line that says which tunnel refused and why.
    expect(failure.evidence).toContain(page);
  });

  it("keeps the status even when the body carried a sentence", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(
      errorResponse(400, "BAD REQUEST", JSON.stringify({ error: "Bu ad zaten var." }))));

    const failure = await createProject("düğün").catch((err) => err);

    // A server sentence is an answer, not a diagnosis: the same words come back with a 400 and
    // with a 500, and only the code tells them apart.
    expect(failure.message).toBe("Bu ad zaten var.");
    expect(failure.evidence).toContain("400 BAD REQUEST");
  });
});
