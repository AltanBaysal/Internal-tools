import { afterEach, expect, test, vi } from "vitest";

import { getJson, postJson, reach } from "./api.js";

afterEach(() => vi.unstubAllGlobals());

function stubFetch(response) {
  const fetch = vi.fn().mockResolvedValue(response);
  vi.stubGlobal("fetch", fetch);
  return fetch;
}

test("getJson returns the parsed body", async () => {
  stubFetch({ ok: true, status: 200, json: async () => [{ id: "p1" }] });
  await expect(getJson("/api/projects")).resolves.toEqual([{ id: "p1" }]);
});

test("a failing response throws instead of returning it", async () => {
  stubFetch({ ok: false, status: 500, text: async () => "" });
  await expect(getJson("/api/projects")).rejects.toThrow("500");
});

test("the server's own sentence is what reaches the screen", async () => {
  // It was being thrown away and replaced with the method, the address and the code, so the one
  // thing that said what actually happened never got out of here.
  stubFetch({
    ok: false,
    status: 409,
    text: async () => JSON.stringify({ error: "a file by that name is back in the project" }),
  });
  await expect(getJson("/api/x")).rejects.toThrow("a file by that name is back in the project");
});

test("a body that is not JSON is still what the server said", async () => {
  stubFetch({ ok: false, status: 500, text: async () => "<html>Internal Server Error</html>" });
  // No cause invented on the way: the code and the body, as they arrived.
  await expect(getJson("/api/x")).rejects.toThrow("HTTP 500: <html>Internal Server Error</html>");
});

test("an empty body leaves only the code to report", async () => {
  stubFetch({ ok: false, status: 502, text: async () => "  " });
  await expect(getJson("/api/x")).rejects.toThrow("HTTP 502");
});

test("the code is still carried apart from the sentence", async () => {
  // "This does not exist" is a screen, not an error line, and that decision reads the number.
  stubFetch({ ok: false, status: 404, text: async () => JSON.stringify({ error: "gone" }) });
  await expect(getJson("/api/x")).rejects.toMatchObject({ status: 404, message: "gone" });
});

test("what else a refusal said is carried with it", async () => {
  // Madde 462: a message refused while a turn runs names that turn, so the screen can follow it.
  stubFetch({
    ok: false,
    status: 409,
    text: async () => JSON.stringify({ error: "busy", turn: { id: "t1" } }),
  });
  await expect(postJson("/api/x", {})).rejects.toMatchObject({
    message: "busy",
    body: { error: "busy", turn: { id: "t1" } },
  });
});

test("reach leaves a body it was not asked for unread, and a refusal says what it said", async () => {
  const cancel = vi.fn();
  stubFetch({ ok: true, status: 200, body: { cancel } });
  await reach("/api/x/events");
  expect(cancel).toHaveBeenCalled();
  stubFetch({ ok: false, status: 524, text: async () => "A timeout occurred" });
  await expect(reach("/api/x/events")).rejects.toThrow("HTTP 524: A timeout occurred");
});

test("postJson sends POST and needs no body", async () => {
  const fetch = stubFetch({ ok: true, status: 201, json: async () => ({ id: "p1" }) });
  await postJson("/api/projects");
  expect(fetch.mock.calls[0][1].method).toBe("POST");
  expect(fetch.mock.calls[0][1].body).toBeUndefined();
});
