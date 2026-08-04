import { describe, expect, it, vi } from "vitest";

import { getSettings, getStatus, listPhotos, listProjects, saveOrder } from "./api.js";

function okResponse(body) {
  return { ok: true, status: 200, statusText: "OK", json: async () => body };
}

describe("api.request", () => {
  it("proje adını URL'de kodlar", async () => {
    const fetchMock = vi.fn().mockResolvedValue(okResponse({ photos: [] }));
    vi.stubGlobal("fetch", fetchMock);

    await listPhotos("düğün fotoğrafları");

    const url = fetchMock.mock.calls[0][0];
    expect(url).toBe(`/api/projects/${encodeURIComponent("düğün fotoğrafları")}/photos`);
    expect(url).not.toContain("düğün");
  });

  it("sunucunun reddettiği istekte sunucunun kendi metnini fırlatır", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: false,
      status: 404,
      statusText: "NOT FOUND",
      json: async () => ({ error: "Proje bulunamadı: düğün" }),
    }));

    await expect(getSettings("düğün")).rejects.toThrow("Proje bulunamadı: düğün");
  });

  it("JSON olmayan hata gövdesinde kodu ve durum metnini gösterir", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: false,
      status: 502,
      statusText: "Bad Gateway",
      json: async () => { throw new SyntaxError("Unexpected token < in JSON"); },
    }));

    await expect(getSettings("düğün")).rejects.toThrow("502 Bad Gateway");
  });

  it("ağ reddini Türkçe önekle sarar ve ham metni altında tutar", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("Failed to fetch")));

    await expect(listProjects()).rejects.toThrow(
      "Sunucuya ulaşılamadı — bağlantıyı kontrol et.\nFailed to fetch",
    );
  });

  it("10 saniye cevapsız kalan isteği iptal eder", async () => {
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

  it("sırayı PUT ile gönderir", async () => {
    const fetchMock = vi.fn().mockResolvedValue(okResponse({ order: ["1_a.png"] }));
    vi.stubGlobal("fetch", fetchMock);

    await saveOrder("düğün", ["1_a.png"]);

    const [url, options] = fetchMock.mock.calls[0];
    expect(url).toBe(`/api/projects/${encodeURIComponent("düğün")}/order`);
    expect(options.method).toBe("PUT");
    expect(JSON.parse(options.body)).toEqual({ order: ["1_a.png"] });
  });

  it("cevap gelen isteği sonradan iptal etmez", async () => {
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
