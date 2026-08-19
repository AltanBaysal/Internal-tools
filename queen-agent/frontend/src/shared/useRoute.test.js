import { renderHook } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";

import { parsePath, useRoute } from "./useRoute.js";

afterEach(() => {
  vi.restoreAllMocks();
  window.history.pushState(null, "", "/");
});

test("the root carries no ids of its own", () => {
  expect(parsePath("/")).toEqual({ view: "root", projectId: null, chatId: null });
});

test("a replacing navigation changes the address without adding to the history", () => {
  // "/" is a fork rather than a place: left in the history, the back button lands on it and the
  // fork pushes the user straight forward again.
  const push = vi.spyOn(window.history, "pushState");
  const replace = vi.spyOn(window.history, "replaceState");
  const { result } = renderHook(() => useRoute());

  result.current.navigate("/p/p1", { replace: true });

  expect(replace).toHaveBeenCalled();
  expect(push).not.toHaveBeenCalled();
  expect(window.location.pathname).toBe("/p/p1");
});

test("an ordinary navigation is still pushed", () => {
  const push = vi.spyOn(window.history, "pushState");
  const { result } = renderHook(() => useRoute());

  result.current.navigate("/p/p1/c/c1");

  expect(push).toHaveBeenCalled();
  expect(window.location.pathname).toBe("/p/p1/c/c1");
});

test("a project path carries its id", () => {
  expect(parsePath("/p/pabc")).toEqual({ view: "project", projectId: "pabc", chatId: null });
});

test("a chat path carries both ids", () => {
  expect(parsePath("/p/pabc/c/c1")).toEqual({ view: "chat", projectId: "pabc", chatId: "c1" });
});

test("a draft chat has an address of its own", () => {
  // A chat is born with its first message, so the draft has no id yet -- but it still has a place,
  // or a reload would throw the user out of what they were typing.
  expect(parsePath("/p/p1/c/new")).toEqual({ view: "chat", projectId: "p1", chatId: "new" });
});

test("/settings is a place of its own", () => {
  // Its own address, so a reload lands back on it like every other screen.
  expect(parsePath("/settings")).toEqual({ view: "settings", projectId: null, chatId: null });
});

test("anything unrecognised falls back to the root", () => {
  expect(parsePath("/nonsense/deep").view).toBe("root");
});
