import { renderHook } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";

import { parsePath, useRoute } from "./useRoute.js";

afterEach(() => {
  vi.restoreAllMocks();
  window.history.pushState(null, "", "/");
});

test("the root is home", () => {
  expect(parsePath("/")).toEqual({ view: "home", projectId: null, chatId: null });
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

test("anything unrecognised falls back to home", () => {
  expect(parsePath("/nonsense/deep").view).toBe("home");
});
