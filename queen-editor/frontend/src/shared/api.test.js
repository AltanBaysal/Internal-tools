import { describe, expect, it, vi } from "vitest";

import { getSettings, getStatus, listPhotos, listProjects, saveOrder } from "./api.js";

function okResponse(body) {
  return { ok: true, status: 200, statusText: "OK", json: async () => body };
}

describe("api.request", () => {
  it("percent-encodes the project name in the URL", async () => {
    const fetchMock = vi.fn().mockResolvedValue(okResponse({ photos: [] }));
    vi.stubGlobal("fetch", fetchMock);

    await listPhotos("düğün fotoğrafları");

    const url = fetchMock.mock.calls[0][0];
    expect(url).toBe(`/api/projects/${encodeURIComponent("düğün fotoğrafları")}/photos`);
    expect(url).not.toContain("düğün");
  });

  it("throws the server's own text when the server rejects a request", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: false,
      status: 404,
      statusText: "NOT FOUND",
      json: async () => ({ error: "Proje bulunamadı: düğün" }),
    }));

    await expect(getSettings("düğün")).rejects.toThrow("Proje bulunamadı: düğün");
  });

  it("shows the status and its text when the error body is not JSON", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: false,
      status: 502,
      statusText: "Bad Gateway",
      json: async () => { throw new SyntaxError("Unexpected token < in JSON"); },
    }));

    await expect(getSettings("düğün")).rejects.toThrow("502 Bad Gateway");
  });

  it("wraps a network refusal in a Turkish prefix and keeps the raw text under it", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("Failed to fetch")));

    await expect(listProjects()).rejects.toThrow(
      "Sunucuya ulaşılamadı — bağlantıyı kontrol et.\nFailed to fetch",
    );
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

    const pending = getStatus();
    const assertion = expect(pending).rejects.toThrow(
      "Sunucuya ulaşılamadı — bağlantıyı kontrol et.\nZaman aşımı (10 sn)",
    );
    await vi.advanceTimersByTimeAsync(10_000);
    await assertion;
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
});
