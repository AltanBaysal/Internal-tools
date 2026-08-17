import { afterEach, expect, test, vi } from "vitest";

import { getJson, postJson } from "./api.js";

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
  stubFetch({ ok: false, status: 500, json: async () => ({}) });
  await expect(getJson("/api/projects")).rejects.toThrow("500");
});

test("postJson sends POST and needs no body", async () => {
  const fetch = stubFetch({ ok: true, status: 201, json: async () => ({ id: "p1" }) });
  await postJson("/api/projects");
  expect(fetch.mock.calls[0][1].method).toBe("POST");
  expect(fetch.mock.calls[0][1].body).toBeUndefined();
});
