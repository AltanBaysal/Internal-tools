import { expect, test } from "vitest";

import { matches } from "./matches.js";

// Madde 365: All projects (Madde 359) and the sidebar's Search chats search by one rule, so it has
// one home -- a second copy would be the first to drift.

test("an empty query matches every name", () => {
  expect(matches("Anything", "")).toBe(true);
  expect(matches("Anything", "   ")).toBe(true);
});

test("case does not count", () => {
  expect(matches("Harbour at dusk", "HARBOUR")).toBe(true);
});

test("accents do not count, either way round", () => {
  // As the design's data.js and shell.js match: "cafe" finds "Café".
  expect(matches("Café noir", "cafe")).toBe(true);
  expect(matches("Cafe", "café")).toBe(true);
});

test("the spaces around the query do not count, and a name without it does not match", () => {
  expect(matches("Old pier", "  pier  ")).toBe(true);
  expect(matches("Old pier", "harbour")).toBe(false);
});
