import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { expect, test } from "vitest";

// A lock, not a behaviour test. jsdom neither loads this stylesheet nor evaluates media queries, so
// nothing here proves the sidebar narrows -- that is Madde 35's manual pass. What it does prove is
// that the four widths the design specifies are still the four widths the stylesheet carries.
//
// Read off disk rather than imported: vitest serves modules over its own protocol, so neither
// import.meta.url nor `?raw` hands back the file. The working directory is the frontend root.
const CSS = readFileSync(resolve(process.cwd(), "src/features/workspace/workspace.css"), "utf8");

// The `.sidebar { ... }` rule inside a given media block, or at the top level when none is named.
function sidebarRule(maxWidth) {
  const scope = maxWidth
    ? CSS.slice(CSS.indexOf(`@media (max-width: ${maxWidth}px)`))
    : CSS;
  const start = scope.indexOf(".sidebar {");
  expect(start).toBeGreaterThan(-1);
  return scope.slice(start, scope.indexOf("}", start));
}

test("the sidebar starts at its full width", () => {
  expect(sidebarRule()).toContain("width: 280px");
});

test("it narrows in three steps rather than one", () => {
  expect(sidebarRule(1000)).toContain("width: 226px");
  expect(sidebarRule(780)).toContain("width: 198px");
  expect(sidebarRule(640)).toContain("width: 172px");
});

test("only the narrowest step tightens the padding", () => {
  // Giving up width is not the same as giving up room to breathe: the padding holds until there is
  // no width left to hold it.
  expect(sidebarRule()).toContain("padding: 18px 14px");
  expect(sidebarRule(1000)).not.toContain("padding");
  expect(sidebarRule(780)).not.toContain("padding");
  expect(sidebarRule(640)).toContain("padding: 16px 10px");
});

// The radius set is three values -- control 8px, card 12-14px, pill 20px -- and a surface that
// writes its own number drifts out of it. These lock the two that had drifted.
// Anchored to the start of a line: ".composer {" also appears inside ".chat__composer .composer {",
// and reading the wrong block would prove the wrong thing.
function rule(selector) {
  const start = CSS.indexOf(`\n${selector} {`);
  expect(start).toBeGreaterThan(-1);
  return CSS.slice(start, CSS.indexOf("}", start));
}

test("every control rounds by the same variable", () => {
  expect(rule(".sidebar__new-chat")).toContain("border-radius: var(--radius-control)");
  expect(rule(".sidebar__row")).toContain("border-radius: var(--radius-control)");
  expect(rule(".composer__send")).toContain("border-radius: var(--radius-control)");
  expect(CSS).not.toContain("border-radius: 9px");
});

test("the composer sits inside the card band", () => {
  expect(rule(".composer")).toContain("border-radius: 14px");
  expect(rule(".composer")).toContain("padding: 14px 16px 10px");
  expect(CSS).not.toContain("border-radius: 16px");
});

test("the extension chip is a fixed square", () => {
  // However long the extension, the row's alignment does not move.
  const chip = rule(".file-chip");
  expect(chip).toContain("width: 30px");
  expect(chip).toContain("height: 30px");
  expect(chip).toContain("border-radius: 7px");
  expect(chip).toContain("background: #f0e7de");
  expect(chip).toContain("font-size: 9.5px");
});

// Every column in the chain zeroes its own overflow, so the scrolling happens inside rather than
// carrying the whole layout with it.
test("the message list can scroll inside its column", () => {
  expect(rule(".chat__scroll")).toContain("min-height: 0");
});

test("the composer never scrolls away", () => {
  expect(rule(".chat__composer")).toContain("flex: none");
});

test("narrow windows scroll their regions, not the layout", () => {
  const narrow = CSS.slice(CSS.indexOf("@media (max-width: 1100px)"));
  const layouts = narrow.slice(0, narrow.indexOf("}", narrow.indexOf(".chat-layout")));
  expect(layouts).toContain("flex-direction: column");
  expect(layouts).not.toContain("overflow-y: auto");
  // The rail drops under the chat, so it needs a ceiling or it eats the conversation's room.
  const rails = narrow.slice(narrow.indexOf(".rail,"), narrow.indexOf("}", narrow.indexOf(".rail,")));
  expect(rails).toContain("max-height: 44%");
  expect(rails).toContain("overflow-y: auto");
});

// One parser, two scales. The bubble's is the design's own three numbers, and a page-level heading
// size must never reach inside a message.
test("the bubble scale is written where the answer is drawn", () => {
  expect(rule(".msg__text .md h1")).toContain("font-size: 19.5px");
  expect(rule(".msg__text .md h2")).toContain("font-size: 17px");
  expect(rule(".msg__text .md h3")).toContain("font-size: 14.5px");
});

test("the two serif levels are the two the design names", () => {
  expect(rule(".msg__text .md h1")).toContain("var(--font-heading)");
  expect(rule(".msg__text .md h2")).toContain("var(--font-heading)");
});

test("only code keeps its whitespace once the answer is parsed", () => {
  // The parser owns the line breaks now; left in place the rule would double every gap.
  expect(rule(".msg__text")).not.toContain("white-space");
  expect(rule(".md pre")).toContain("white-space: pre");
  // What the user typed is not parsed at all, so its bubble still keeps every newline.
  expect(rule(".msg__bubble")).toContain("white-space: pre-wrap");
});

test("a wide table or a long code line scrolls inside itself", () => {
  expect(rule(".md pre")).toContain("overflow-x: auto");
  expect(rule(".md__table-scroll")).toContain("overflow-x: auto");
});

test("the caret is the design's block and borrows the dots' blink", () => {
  const caret = rule(".caret");
  expect(caret).toContain("width: 7px");
  expect(caret).toContain("height: 15px");
  expect(caret).toContain("animation: blink");
  // The accent marks the primary action and nothing else; a text cursor is ink.
  expect(caret).not.toContain("var(--accent)");
});

test("the layout breakpoint no longer sets the sidebar width", () => {
  // Madde 33 brings the layout onto the same measurements; until then it keeps its own, and the
  // sidebar's four steps are the only thing that decides its width.
  const layout = CSS.slice(CSS.indexOf("@media (max-width: 1100px)"));
  expect(layout.slice(0, layout.indexOf("}", layout.indexOf(".chat-layout")))).not.toContain(
    ".sidebar",
  );
});
