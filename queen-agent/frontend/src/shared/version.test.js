import { expect, test } from "vitest";

import { VERSION } from "./version.js";

test("the version reads as a run number", () => {
  // The value itself is a decision, not a behaviour: it is written by hand when a run opens and by
  // nothing else, so pinning the value here would put one decision in two places and let the suite
  // pass on the day only one of them moved. What is held is the shape the madde asked for -- the run
  // number after a capital V -- so a lowercase v, a bare number, a point release or a suffix are all
  // caught.
  expect(VERSION).toMatch(/^V\d+$/);
});
