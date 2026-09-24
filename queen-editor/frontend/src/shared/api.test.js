import { describe, expect, it, vi } from "vitest";

import * as api from "./api.js";
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

  it("sends reference files as a form the browser describes itself", async () => {
    const fetchMock = vi.fn().mockResolvedValue(okResponse({ references: [] }));
    vi.stubGlobal("fetch", fetchMock);
    const file = new File([new Uint8Array([1, 2])], "kedi.png", { type: "image/png" });

    await api.uploadReferences("düğün", [file]);

    const [url, options] = fetchMock.mock.calls[0];
    expect(url).toBe(`/api/projects/${encodeURIComponent("düğün")}/references`);
    expect(options.body).toBeInstanceOf(FormData);
    expect(options.body.getAll("files").map((one) => one.name)).toEqual(["kedi.png"]);
    // No Content-Type of ours: multipart carries a boundary, and only the browser knows it.
    expect(options.headers).toBeUndefined();
  });

  it("gives an upload longer than the ten seconds every other request gets", async () => {
    // A fifteen second video onto Drive is not a ten second request, and a cut upload would come
    // back as "sunucuya ulaşılamadı" -- a sentence about the wrong thing.
    vi.useFakeTimers();
    const signals = [];
    vi.stubGlobal("fetch", vi.fn((path, options) => {
      signals.push(options.signal);
      return new Promise(() => {});
    }));

    api.uploadReferences("düğün", []).catch(() => {});
    await vi.advanceTimersByTimeAsync(10_000);

    expect(signals[0].aborted).toBe(false);
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

  it("renames a project at the address it has now", async () => {
    const fetchMock = vi.fn().mockResolvedValue(okResponse({ name: "nikah" }));
    vi.stubGlobal("fetch", fetchMock);

    // Reached through the module rather than by name, so a missing export shows up as one failing
    // test instead of a file that will not load at all.
    await api.renameProject("düğün", "nikah");

    const [url, options] = fetchMock.mock.calls[0];
    // The address is the name the project has today and the body is the one it is getting: a
    // project IS its folder, so the folder it is in now is where the request has to go.
    expect(url).toBe(`/api/projects/${encodeURIComponent("düğün")}/rename`);
    expect(options.method).toBe("POST");
    expect(JSON.parse(options.body)).toEqual({ name: "nikah" });
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

  it("reads and writes Referanstan's record at the project's own address", async () => {
    const fetchMock = vi.fn().mockResolvedValue(okResponse({ prompts: "", variants: null }));
    vi.stubGlobal("fetch", fetchMock);

    // Through the module, so a missing export fails this test rather than the file.
    await api.getReferenceSettings("düğün");
    await api.saveReferenceSettings("düğün", { prompts: '["a"]', variants: 2 });

    const url = `/api/projects/${encodeURIComponent("düğün")}/reference-settings`;
    expect(fetchMock.mock.calls[0][0]).toBe(url);
    expect(fetchMock.mock.calls[0][1].method).toBeUndefined();
    const [putUrl, put] = fetchMock.mock.calls[1];
    expect(putUrl).toBe(url);
    expect(put.method).toBe("PUT");
    expect(JSON.parse(put.body)).toEqual({ prompts: '["a"]', variants: 2 });
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
