import { describe, it, expect, vi } from "vitest";
import { sendChat } from "./api.js";

// Hand-built stubs rather than a real Response: jsdom does not provide one, and these say exactly
// what sendChat reads.
const ok = (content) => ({
  ok: true,
  status: 200,
  text: async () => JSON.stringify({ choices: [{ message: { content } }] }),
});
const fail = (status, body) => ({ ok: false, status, text: async () => body });

describe("sendChat", () => {
  it("returns the reply text", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(ok("merhaba")));
    const text = await sendChat({ key: "k", model: "grok-4.3", messages: [] });
    expect(text).toBe("merhaba");
  });

  it("puts the trimmed key in the Authorization header", async () => {
    const fetchMock = vi.fn().mockResolvedValue(ok("ok"));
    vi.stubGlobal("fetch", fetchMock);
    await sendChat({ key: "  xai-123  ", model: "grok-4.3", messages: [] });
    const [, init] = fetchMock.mock.calls[0];
    expect(init.headers.Authorization).toBe("Bearer xai-123");
  });

  it("puts the model and the messages in the body", async () => {
    const fetchMock = vi.fn().mockResolvedValue(ok("ok"));
    vi.stubGlobal("fetch", fetchMock);
    await sendChat({
      key: "k",
      model: " grok-4.3 ",
      messages: [{ role: "user", content: "selam" }],
    });
    const [, init] = fetchMock.mock.calls[0];
    const body = JSON.parse(init.body);
    expect(body.model).toBe("grok-4.3");
    expect(body.messages[0].role).toBe("system");
    expect(body.messages[1]).toEqual({ role: "user", content: "selam" });
  });

  it("expands a skill call before the request leaves", async () => {
    const fetchMock = vi.fn().mockResolvedValue(ok("ok"));
    vi.stubGlobal("fetch", fetchMock);
    await sendChat({
      key: "k",
      model: "grok-4.3",
      messages: [{ role: "user", content: "taşınacağım", skill: "plan-yazma" }],
      skills: [{ name: "plan-yazma", description: "Adımlara böler.", body: "PLAN TALİMATI" }],
    });
    const [, init] = fetchMock.mock.calls[0];
    expect(JSON.parse(init.body).messages[1].content).toBe("PLAN TALİMATI\n\ntaşınacağım");
  });

  it("carries a non-200 body into the error verbatim", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(fail(404, '{"error":"model yok"}')));
    await expect(sendChat({ key: "k", model: "yok", messages: [] })).rejects.toThrow(
      'HTTP 404 — {"error":"model yok"}'
    );
  });

  it("expands a file mention before the request leaves", async () => {
    const fetchMock = vi.fn().mockResolvedValue(ok("ok"));
    vi.stubGlobal("fetch", fetchMock);
    await sendChat({
      key: "k",
      model: "grok-4.3",
      messages: [{ role: "user", content: "@plan.md ne", files: ["plan.md"] }],
      files: [{ id: 1, projectId: 1, name: "plan.md", content: "PLAN İÇERİĞİ" }],
    });
    const [, init] = fetchMock.mock.calls[0];
    expect(JSON.parse(init.body).messages[1].content).toContain("PLAN İÇERİĞİ");
  });

  it("does not swallow a network failure", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("Failed to fetch")));
    await expect(sendChat({ key: "k", model: "m", messages: [] })).rejects.toThrow(
      "Failed to fetch"
    );
  });
});
