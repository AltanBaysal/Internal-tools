// Where a menu hangs off the button that opened it. Pure on purpose: it takes rectangles and gives
// back numbers, so the arithmetic can be proved without a layout engine -- jsdom has none.

// Between the trigger and the menu.
const GAP = 6;
// The closest a menu comes to the edge of the window.
const EDGE = 8;
// Ours, not the design's: karar 11 asks for a ceiling without naming one. 320 holds the model
// menu's four described rows and puts a taller menu into its own scroll.
const TALLEST = 320;

function clamp(value, low, high) {
  return Math.min(Math.max(value, low), Math.max(low, high));
}

export function placeMenu(anchor, menu, viewport) {
  const maxHeight = Math.min(TALLEST, viewport.height - 2 * EDGE);
  const height = Math.min(menu.height, maxHeight);

  // Right-aligned to its trigger, then pulled back inside the window if that put it outside.
  const left = clamp(anchor.right - menu.width, EDGE, viewport.width - menu.width - EDGE);

  // Never flipped over: karar 11 says the case the flip was for never arises, and a flip moves a
  // laid-out element sideways in a design that allows no such motion. What is left is sliding it up
  // until it fits.
  const below = anchor.bottom + GAP;
  const fits = below + height <= viewport.height - EDGE;
  const top = fits ? below : Math.max(EDGE, viewport.height - EDGE - height);

  return { left, top, maxHeight };
}
