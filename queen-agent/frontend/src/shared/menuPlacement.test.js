import { expect, test } from "vitest";

import { placeMenu } from "./menuPlacement.js";

// Rectangles in, numbers out. jsdom has no layout engine, so this is the only place the arithmetic
// can be proved; the component's job is just to apply what it says.
const WIDE = { width: 1200, height: 800 };
const MENU = { width: 176, height: 120 };
const BUTTON = { left: 260, right: 300, top: 80, bottom: 100 };

test("a menu hangs from the right edge of the button that opened it", () => {
  expect(placeMenu(BUTTON, MENU, WIDE).left).toBe(300 - 176);
});

test("it opens under the button, a hair below it", () => {
  expect(placeMenu(BUTTON, MENU, WIDE).top).toBe(106);
});

test("a button near the left edge does not push the menu off it", () => {
  const near = { ...BUTTON, left: 60, right: 100 };
  expect(placeMenu(near, MENU, WIDE).left).toBe(8);
});

test("nor does one near the right edge", () => {
  const narrow = { width: 400, height: 800 };
  const near = { ...BUTTON, left: 358, right: 398 };
  expect(placeMenu(near, MENU, narrow).left).toBe(400 - 176 - 8);
});

test("with no room under it the menu slides up rather than flipping over", () => {
  // Flipping is what the design refused: it would move a laid-out element, and karar 11 says the
  // case never arises for the composer's menus anyway. What is left is sliding it into the window.
  const short = { width: 1200, height: 300 };
  const low = { ...BUTTON, top: 260, bottom: 280 };
  const place = placeMenu(low, MENU, short);
  expect(place.top).toBe(300 - 8 - 120);
  // Above the button would have been 154. It is not there.
  expect(place.top).not.toBe(260 - 6 - 120);
});

test("a menu never grows taller than the window can hold", () => {
  const short = { width: 1200, height: 200 };
  expect(placeMenu(BUTTON, MENU, short).maxHeight).toBe(200 - 16);
});

test("and never taller than the cap, however tall the window is", () => {
  expect(placeMenu(BUTTON, { width: 176, height: 900 }, WIDE).maxHeight).toBe(320);
});

test("a menu too tall for the room under it is placed at what it is allowed, not at what it asked", () => {
  // The one that scrolls inside itself: it is 900 tall, gets 320, and sits where 320 fits.
  const short = { width: 1200, height: 400 };
  const place = placeMenu(BUTTON, { width: 176, height: 900 }, short);
  expect(place.maxHeight).toBe(320);
  expect(place.top).toBe(400 - 8 - 320);
});
