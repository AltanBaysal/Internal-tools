import { expect, test } from "vitest";

import { clockTime, relativeTime } from "./time.js";

const NOW = Date.parse("2026-08-09T12:00:00.000Z");

function ago(milliseconds) {
  return new Date(NOW - milliseconds).toISOString();
}

test("a stamp becomes a wall clock", () => {
  // Built from the same local zone the browser renders in, so the test cannot drift with the CI box.
  const iso = new Date(2026, 7, 9, 11, 4).toISOString();
  expect(clockTime(iso)).toBe("11:04");
});

test("under a minute reads as just now", () => {
  expect(relativeTime(ago(30_000), NOW)).toBe("just now");
});

test("minutes and hours are counted", () => {
  expect(relativeTime(ago(5 * 60_000), NOW)).toBe("5m ago");
  expect(relativeTime(ago(2 * 3_600_000), NOW)).toBe("2h ago");
});

test("one day back is yesterday, not 1 days ago", () => {
  expect(relativeTime(ago(26 * 3_600_000), NOW)).toBe("yesterday");
});

test("a few days are counted, a week becomes a date", () => {
  expect(relativeTime(ago(3 * 86_400_000), NOW)).toBe("3 days ago");
  expect(relativeTime(ago(30 * 86_400_000), NOW)).toMatch(/Jul/);
});
