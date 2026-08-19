// The rail's width, as four numbers and one decision. Here rather than in the stylesheet because
// both are answered while the app runs: the user drags, and the shell is measured.

// What the rail is before anything is dragged. workspace.css carries the same number for the frame
// where nothing has been said yet, and a lock test holds the two together.
export const DEFAULT_RAIL_WIDTH = 320;

// Below this a row cannot say what it is: 18px of padding on each side leaves 184, and the file's
// name and its "project file · 2h ago" line still have to fit on that.
export const MIN_RAIL_WIDTH = 220;

// The width the rail is drawn at while a document is open. The list may not outgrow the thing the
// room was made for.
export const MAX_RAIL_WIDTH = 560;

// At this shell width the sidebar is 226 (its narrow step) and the rail's own minimum is 220, which
// leaves the conversation 414. Under that the chat would be narrower than the rail beside it, and
// then the rail is what has to go.
export const RAIL_CLOSES_BELOW = 860;

// A drag asks for a width; this answers what it gets. null is not a narrow rail -- it is a closed
// one, and the caller reads it as closing rather than as a number.
export function railWidthFor(desired) {
  if (desired < MIN_RAIL_WIDTH) return null;
  return Math.min(desired, MAX_RAIL_WIDTH);
}

// Zero is the absence of a measurement rather than the narrowest shell, the same way useShellWidth
// reads it. Folding on the first frame of every load would answer a question nobody has asked.
export function railFitsIn(shellWidth) {
  return !shellWidth || shellWidth >= RAIL_CLOSES_BELOW;
}
