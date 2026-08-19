import { expect, test } from "vitest";

import { MAX_RAIL_WIDTH, MIN_RAIL_WIDTH, railFitsIn, railWidthFor } from "./railWidth.js";

test("a width between the two bounds is the width that was asked for", () => {
  expect(railWidthFor(400)).toBe(400);
  expect(railWidthFor(MIN_RAIL_WIDTH)).toBe(MIN_RAIL_WIDTH);
  expect(railWidthFor(MAX_RAIL_WIDTH)).toBe(MAX_RAIL_WIDTH);
});

test("wider than the widest is held at the widest", () => {
  // 560 is what the rail is drawn at while a document is open. The list may not outgrow the thing
  // the room was made for.
  expect(railWidthFor(900)).toBe(MAX_RAIL_WIDTH);
});

test("narrower than the narrowest is not a width at all", () => {
  // Pulled in past its minimum the rail closes -- it does not become a sliver. null is that answer,
  // and the caller reads it as closing rather than as a number.
  expect(railWidthFor(MIN_RAIL_WIDTH - 1)).toBeNull();
  expect(railWidthFor(0)).toBeNull();
  expect(railWidthFor(-40)).toBeNull();
});

test("a shell with room for both keeps the rail, and one without does not", () => {
  expect(railFitsIn(1200)).toBe(true);
  expect(railFitsIn(860)).toBe(true);
  expect(railFitsIn(859)).toBe(false);
  expect(railFitsIn(500)).toBe(false);
});

test("a shell that has not been measured is not a narrow shell", () => {
  // Zero is the absence of a measurement, the same way useShellWidth reads it. Folding the rail on
  // the first frame of every load would be answering a question nobody has asked yet.
  expect(railFitsIn(0)).toBe(true);
});
