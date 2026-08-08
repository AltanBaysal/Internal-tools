import { cleanup } from "@testing-library/react";
import { afterEach, vi } from "vitest";

// One test's leftovers must never decide another test's outcome: unmount what was rendered, drop
// the fake fetch, hand the clock back, and forget the stored key. Without globals enabled,
// Testing Library's own auto cleanup does not run, so it is done here explicitly.
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  vi.useRealTimers();
  localStorage.clear();
});
