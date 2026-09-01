import { expect, test } from "vitest";

import config from "../vite.config.js";

// A lock, not a behaviour test -- the same kind as app.css.test.js. What it holds is the setting
// that decides how much of the machine one test run is allowed to take.
//
// The config is imported rather than read as text. The css locks read text because jsdom loads no
// stylesheet and there is nothing to import; a JS config has no such excuse, and importing it
// reads the value actually in force rather than the one that happens to be written down.
//
// Why the setting exists at all: with a worker per core, thirty-five files each stand up their own
// jsdom and then queue for the same memory. A test measured at 99ms alone read 5107ms in that
// crowd, and the timeout -- which measures the wall clock -- called it stuck. Halving the workers
// made the suite green and twice as fast.

test("one run does not ask the machine for every core it has", () => {
  expect(config.test.maxWorkers).toBeDefined();
});

test("the share is written as a proportion, so it travels between machines", () => {
  // A fixed count would fix this machine and bind every other: ten workers is still too many on a
  // four-core runner and leaves a sixty-four-core one idle. The rule is half the cores, so that is
  // what the file says.
  expect(config.test.maxWorkers).toMatch(/^\d+%$/);
  expect(Number.parseInt(config.test.maxWorkers, 10)).toBeLessThanOrEqual(50);
});
