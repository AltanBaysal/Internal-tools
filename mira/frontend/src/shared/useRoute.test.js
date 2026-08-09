import { expect, test } from "vitest";

import { parsePath } from "./useRoute.js";

test("the root is home", () => {
  expect(parsePath("/")).toEqual({ view: "home", projectId: null, chatId: null });
});

test("a project path carries its id", () => {
  expect(parsePath("/p/pabc")).toEqual({ view: "project", projectId: "pabc", chatId: null });
});

test("a chat path carries both ids", () => {
  expect(parsePath("/p/pabc/c/c1")).toEqual({ view: "chat", projectId: "pabc", chatId: "c1" });
});

test("anything unrecognised falls back to home", () => {
  expect(parsePath("/nonsense/deep").view).toBe("home");
});
