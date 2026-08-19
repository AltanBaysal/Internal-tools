import { afterEach, expect, test, vi } from "vitest";

import { parseFrame, streamEvents } from "./sse.js";

afterEach(() => vi.unstubAllGlobals());

test("a frame becomes an event and its parsed data", () => {
  expect(parseFrame('event: chunk\ndata: {"text":"hi"}')).toEqual({
    event: "chunk",
    data: { text: "hi" },
  });
});

test("a frame with no event is ignored", () => {
  expect(parseFrame(": keep-alive")).toBeNull();
});

test("a frame with broken data is ignored rather than thrown", () => {
  expect(parseFrame("event: chunk\ndata: {oops")).toBeNull();
});

function stubStream(text) {
  const encoded = new TextEncoder().encode(text);
  let sent = false;
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      body: {
        getReader: () => ({
          read: async () => {
            if (sent) return { done: true };
            sent = true;
            return { done: false, value: encoded };
          },
        }),
      },
    }),
  );
}

test("events arrive in order", async () => {
  stubStream(
    'event: chunk\ndata: {"text":"He"}\n\nevent: chunk\ndata: {"text":"llo"}\n\nevent: done\ndata: {"id":"c1"}\n\n',
  );
  const seen = [];
  await streamEvents("/api/x", (frame) => seen.push(frame));
  expect(seen.map((frame) => frame.event)).toEqual(["chunk", "chunk", "done"]);
  expect(seen[1].data.text).toBe("llo");
});

test("a refused request throws with its status", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 404, text: async () => "" }));
  await expect(streamEvents("/api/x", () => {})).rejects.toThrow("404");
});

test("the stream reports what the server said, like every other request", async () => {
  // This is the second road out of the browser, and it was writing its own sentence over the
  // server's exactly as the first one did.
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok: false,
      status: 502,
      text: async () => JSON.stringify({ error: "xai answered 401: bad key" }),
    }),
  );
  await expect(streamEvents("/api/x", () => {})).rejects.toThrow("xai answered 401: bad key");
});
