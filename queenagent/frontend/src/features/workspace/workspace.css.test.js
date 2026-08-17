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
  // The row became a box holding two buttons, so the rounding belongs to the one that is a control.
  expect(rule(".sidebar__row-open")).toContain("border-radius: var(--radius-control)");
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

test("the waiting block breathes wider than an ordinary message", () => {
  // The design measures this one: 10px between the label and the dots, where a message uses 6.
  expect(rule(".msg--waiting")).toContain("gap: 10px");
  expect(rule(".msg")).toContain("gap: 6px");
});

test("the box carries the skeleton of the card about to be born", () => {
  const creating = rule(".creating");
  expect(creating).toContain("max-width: 340px");
  const chip = rule(".creating__chip");
  expect(chip).toContain("width: 30px");
  expect(chip).toContain("height: 30px");
  expect(chip).toContain("border-radius: 7px");
});

// The one confirmation pattern in the app, and the first filled red button it has ever had.
test("the confirm button is filled with the destructive red", () => {
  expect(rule(".dialog__confirm")).toContain("background: var(--destructive)");
  expect(rule(".dialog__confirm:hover")).toContain("background: var(--destructive-hover)");
});

test("the darkened screen covers the screen", () => {
  const dialog = rule(".dialog");
  expect(dialog).toContain("position: fixed");
  expect(dialog).toContain("inset: 0");
});

test("the row menu is the design's width and escapes the sidebar's scroll", () => {
  const menu = rule(".row-menu");
  expect(menu).toContain("width: 176px");
  // Fixed rather than absolute: inside the sidebar's scrolling area an absolute menu gets clipped.
  expect(menu).toContain("position: fixed");
});

test("the destructive choice is the only red one in the menu", () => {
  expect(rule(".row-menu__item--danger")).toContain("color: var(--destructive)");
});

test("the header wraps rather than squeezing its buttons", () => {
  // A second button joined Rename, and a title has no business being cut for it.
  expect(rule(".screen__title-row")).toContain("flex-wrap: wrap");
});

test("the header's Delete is outlined until it is hovered", () => {
  expect(rule(".screen__delete")).toContain("border: 1px solid var(--destructive-line)");
  expect(rule(".screen__delete")).toContain("color: var(--destructive)");
  expect(rule(".screen__delete:hover")).toContain("background: var(--destructive)");
});

test("a chat row's delete is there before it is reached for", () => {
  // The design separates the two deliberately: the sidebar's menu button waits for the row, this
  // one stands in it.
  expect(rule(".row-x")).not.toContain("opacity: 0");
  expect(rule(".row-x")).toContain("color: #b5ada2");
});

test("the undo strip is gone rather than restyled", () => {
  // fark 31 was about its colour and its radius; karar 16 took the strip itself.
  expect(CSS).not.toContain(".strip");
});

test("a folded rail is the design's strip, and it gets there by the one transition", () => {
  expect(rule(".rail--collapsed")).toContain("width: 46px");
  expect(rule(".rail")).toContain("transition: width 220ms");
});

test("the label turns rather than being cut", () => {
  expect(rule(".rail--collapsed .rail__label")).toContain("writing-mode: vertical-rl");
});

test("under the chat a folded rail is a row, not a column", () => {
  // A vertical strip means nothing in a layout that is already stacked.
  const narrow = CSS.slice(CSS.indexOf("@media (max-width: 1100px)"));
  const folded = narrow.slice(narrow.indexOf(".rail--collapsed"));
  expect(folded.slice(0, folded.indexOf("}"))).toContain("width: auto");
  expect(folded.slice(0, folded.indexOf("}"))).not.toContain("46px");
});

test("the rail is a surface of its own rather than the canvas with a line on it", () => {
  expect(rule(".rail")).toContain("background: #fbf9f5");
});

test("the row being read is marked, and hovering is not the same as being open", () => {
  // Written as one grouped rule on purpose: being read outranks being pointed at, so the selected
  // tone has to survive the hover.
  const selected = CSS.slice(CSS.indexOf("\n.file-row--selected,"));
  expect(selected.slice(0, selected.indexOf("}"))).toContain("background: #efebe4");
  expect(rule(".file-row:hover")).toContain("background: #f0ece5");
});

test("the card in the transcript is the size of the box that preceded it", () => {
  // The dashed creating box is this card before it was born, so they share a skeleton.
  expect(rule(".file-card")).toContain("max-width: 340px");
  expect(rule(".file-card")).toContain("border-radius: 12px");
});

test("the card of the file being read is marked", () => {
  // Grouped with its hover for the same reason the row is: being read outranks being pointed at.
  const selected = CSS.slice(CSS.indexOf("\n.file-card--selected,"));
  const block = selected.slice(0, selected.indexOf("}"));
  expect(block).toContain("background: #f4efe7");
  expect(block).toContain("border-color: #cfc3b2");
});

test("while reading, the rail is two columns and the list keeps one", () => {
  // The design gives 320 to 560 and no split; the list takes the narrower half so the document gets
  // the room it is there for.
  expect(rule(".rail--open")).toContain("display: flex");
  expect(rule(".rail__list")).toContain("width: 200px");
});

test("the layout breakpoint no longer sets the sidebar width", () => {
  // Madde 33 brings the layout onto the same measurements; until then it keeps its own, and the
  // sidebar's four steps are the only thing that decides its width.
  const layout = CSS.slice(CSS.indexOf("@media (max-width: 1100px)"));
  expect(layout.slice(0, layout.indexOf("}", layout.indexOf(".chat-layout")))).not.toContain(
    ".sidebar",
  );
});
