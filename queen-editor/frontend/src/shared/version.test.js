import { expect, test } from "vitest";

import { VERSION } from "./version.js";

test("the version reads as a run number", () => {
  // The value itself is a decision, not a behaviour: it is written by hand when a run opens and by
  // nothing else, so pinning "V5" here would put one decision in two places (madde 248, after
  // QueenAgent's 209). What is held is the shape -- the run number, in capitals.
  expect(VERSION).toMatch(/^V\d+$/);
});
