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

// The `.sidebar { ... }` rule at a given step, or the one that holds at every width when no step is
// named. The step is a class on the shell, because what is measured is the shell rather than the
// window -- the same screen inside a frame has to answer the same way.
function sidebarRule(step) {
  const selector = step ? `\n.app-shell--${step} .sidebar {` : "\n.sidebar {";
  const start = CSS.indexOf(selector);
  expect(start).toBeGreaterThan(-1);
  return CSS.slice(start, CSS.indexOf("}", start));
}

test("nothing asks the window how wide it is", () => {
  // A media query can only ask about the window. Leaving one in would make the sidebar follow the
  // window while the rail follows the shell.
  expect(CSS).not.toContain("@media");
});

test("the sidebar starts at its full width", () => {
  expect(sidebarRule()).toContain("width: 280px");
});

test("it narrows in three steps rather than one", () => {
  expect(sidebarRule("narrow")).toContain("width: 226px");
  expect(sidebarRule("tight")).toContain("width: 198px");
  expect(sidebarRule("compact")).toContain("width: 172px");
});

test("only the narrowest step tightens the padding", () => {
  // Giving up width is not the same as giving up room to breathe: the padding holds until there is
  // no width left to hold it.
  expect(sidebarRule()).toContain("padding: 18px 14px");
  expect(sidebarRule("narrow")).not.toContain("padding");
  expect(sidebarRule("tight")).not.toContain("padding");
  expect(sidebarRule("compact")).toContain("padding: 16px 10px");
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

// A grouped rule, so it is read by hand: rule() anchors on a single selector.
function grouped(first) {
  const start = CSS.indexOf(`\n${first}`);
  expect(start).toBeGreaterThan(-1);
  return CSS.slice(start, CSS.indexOf("}", start));
}

test("a narrow shell scrolls its regions, not the layout", () => {
  const layouts = grouped(".app-shell--narrow .chat-layout,");
  expect(layouts).toContain("flex-direction: column");
  expect(layouts).not.toContain("overflow-y: auto");
  // The rail drops under the chat, so it needs a ceiling or it eats the conversation's room.
  const rails = grouped(".app-shell--narrow .rail,");
  // 44% of the area, never more than 250px and never less than 150px -- the design's three numbers.
  expect(rails).toContain("max-height: min(250px, 44%)");
  expect(rails).toContain("min-height: 150px");
  expect(rails).toContain("overflow-y: auto");
});

test("a narrow shell puts the project's two columns one above the other", () => {
  // Reading or not: at this width there is only ever one column to give.
  expect(grouped(".app-shell--narrow .project-grid,")).toContain(
    "grid-template-columns: minmax(0, 1fr)",
  );
});

test("reading in a narrow shell takes the whole area rather than lengthening the page", () => {
  // The column stays in place today and the panel is added underneath it, which is the one thing
  // the contract forbids: the page itself scrolls.
  expect(rule(".app-shell--narrow .chat-layout--reading .chat")).toContain("display: none");
  expect(rule(".app-shell--narrow .screen-layout--reading .screen")).toContain("display: none");
  const readers = grouped(".app-shell--narrow .chat-layout--reading .rail--open,");
  expect(readers).toContain("max-height: none");
  expect(readers).toContain("flex: 1");
});

test("a tight shell gives up its side room in one move", () => {
  // Six surfaces share the same 32px of breathing room; loosening one and not the others would
  // stagger the left edge.
  const sides = grouped(".app-shell--tight .screen,");
  expect(sides).toContain("padding-left: 20px");
  expect(sides).toContain("padding-right: 20px");
  ["chat__header", "chat__scroll", "chat__composer", "offline", "empty"].forEach((surface) => {
    expect(sides).toContain(`.${surface}`);
  });
});

test("a tight shell shrinks the project title and drops the time from a chat row", () => {
  expect(rule(".app-shell--tight .screen__title")).toContain("font-size: 27px");
  // The title is what a narrow row is for; the time is what it can afford to lose.
  expect(rule(".app-shell--tight .chat-row__when")).toContain("display: none");
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

test("the menu escapes the sidebar's scroll and scrolls inside itself", () => {
  const menu = rule(".menu");
  // Fixed rather than absolute: inside the sidebar's scrolling area an absolute menu gets clipped,
  // and the placement it is given is measured against the window.
  expect(menu).toContain("position: fixed");
  // Its height is capped by the placement, so what is left is letting the overflow scroll.
  expect(menu).toContain("overflow-y: auto");
  // One box, three callers: the width belongs to each of them, not to the box.
  expect(menu).not.toContain("width");
});

test("the sidebar's menu is the design's own width", () => {
  expect(rule(".sidebar__row .menu")).toContain("width: 176px");
});

test("the catcher covers the screen and shows nothing", () => {
  const catcher = rule(".menu__catcher");
  expect(catcher).toContain("position: fixed");
  expect(catcher).toContain("inset: 0");
  expect(catcher).not.toContain("background");
});

test("the destructive choice is the only red one in the menu", () => {
  expect(rule(".menu__item--danger")).toContain("color: var(--destructive)");
});

test("the menu that was a row's alone is gone by that name", () => {
  expect(CSS).not.toContain(".row-menu");
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
  const folded = rule(".app-shell--narrow .rail--collapsed");
  expect(folded).toContain("width: auto");
  expect(folded).not.toContain("46px");
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

// The second scale, written against the reader's own container for the same reason the bubble's is
// written against the message's: neither may reach into the other.
test("the reader draws its document at the doc scale", () => {
  expect(rule(".reader__body .md h1")).toContain("font-size: 25px");
  expect(rule(".reader__body .md h2")).toContain("font-size: 20px");
  expect(rule(".reader__body .md h3")).toContain("font-size: 15.5px");
  // The bubble keeps its own three; a page-level size arriving here must not follow the parser back.
  expect(rule(".msg__text .md h1")).toContain("font-size: 19.5px");
});

test("the document reads at the design's size and leading", () => {
  const body = rule(".reader__body");
  expect(body).toContain("font-size: 14.5px");
  expect(body).toContain("line-height: 1.8");
  expect(body).toContain("padding: 26px 28px");
  // The parser owns the line breaks here too -- kept, the rule would double every gap.
  expect(body).not.toContain("white-space");
});

test("the first load has a shape, and it is the design's three", () => {
  const screenSkeleton = rule(".skeleton--screen .skeleton__block:nth-child(1)");
  expect(screenSkeleton).toContain("width: 280px");
  expect(screenSkeleton).toContain("height: 38px");
  expect(rule(".skeleton--screen .skeleton__block:nth-child(2)")).toContain("height: 104px");
  const third = rule(".skeleton--screen .skeleton__block:nth-child(3)");
  expect(third).toContain("width: 180px");
  expect(third).toContain("height: 16px");
});

test("the blocks blink at the design's speed, one after another", () => {
  // One blink in the app, and the number is the design's rather than the one that was here.
  expect(rule(".skeleton__block")).toContain("animation: blink 1.4s infinite");
  expect(CSS).not.toContain("blink 1.6s");
  // Staged only on this screen: the design says it here, and generalising it would be inventing.
  expect(rule(".skeleton--screen .skeleton__block:nth-child(2)")).toContain("animation-delay");
  expect(rule(".skeleton--screen .skeleton__block:nth-child(3)")).toContain("animation-delay");
});

test("the offline strip turns reddish and carries a dot", () => {
  const strip = rule(".offline");
  expect(strip).toContain("background: #f5e9e3");
  expect(strip).toContain("border-bottom: 1px solid #e7d3c8");
  expect(strip).toContain("color: #8a5237");

  const dot = rule(".offline__dot");
  expect(dot).toContain("width: 7px");
  expect(dot).toContain("height: 7px");
  // Being offline is a state, and the accent marks the primary action and nothing else.
  expect(dot).not.toContain("var(--accent)");
});

test("a row is a box holding buttons, and the lit surface is the box", () => {
  // The × cannot sit inside a button, so it became a sibling -- and the hover has to survive that.
  expect(rule(".file-row:hover")).toContain("background: #f0ece5");
  expect(rule(".chat-row:hover")).toContain("background: #f0ece5");
  // The room the row used to hold moves to the opener, so the clickable area does not shrink.
  expect(rule(".file-row")).not.toContain("padding");
  expect(rule(".file-row__open")).toContain("padding: 10px 8px");
  expect(rule(".chat-row")).not.toContain("padding");
  expect(rule(".chat-row__open")).toContain("padding: 13px 8px");
});

test("a list says what went wrong in one voice", () => {
  // One class for all four places: a line saying something failed in this list is the same thing in
  // the rail, in either column, and after a refused delete.
  const line = rule(".list-error");
  expect(line).toContain("font-family: var(--font-mono)");
  expect(line).toContain("font-size: 11px");
  // The look does not change with the name: this madde widens where the line is used, nothing else.
  expect(line).toContain("color: #a4735a");
  // The old name was the file list's alone and read wrong in a column of chats.
  expect(CSS).not.toContain(".file-list__error");
});

test("a file that is not a document is read in mono, exactly as written", () => {
  const code = rule(".reader__code");
  expect(code).toContain("font-family: var(--font-mono)");
  expect(code).toContain("white-space: pre");
  // A long prompt line scrolls inside its own block rather than widening the reader.
  expect(code).toContain("overflow-x: auto");
  // The code block's own measures, not a new pair invented for this.
  expect(code).toContain("font-size: 12.5px");
  expect(code).toContain("line-height: 1.6");
  // No box: the reader's body is already a surface, and a block inside it is paper on paper.
  expect(code).not.toContain("background");
  expect(code).not.toContain("border");
});

test("the header and the footer stay while the document scrolls", () => {
  expect(rule(".reader__head")).toContain("flex: none");
  expect(rule(".reader__body")).toContain("overflow-y: auto");
  expect(rule(".reader__meta")).toContain("flex: none");
  expect(rule(".reader__meta")).toContain("border-top: 1px solid var(--line)");
  // The reader as a whole no longer scrolls: that is what used to carry the head away.
  expect(rule(".rail--open .reader")).not.toContain("overflow-y");
});

test("the room around the document belongs to the document", () => {
  // Once the body carries the design's 26/28 the container's own padding would sit under it, so it
  // moves to the list -- the only thing left in the rail that still needs it.
  expect(rule(".panel")).toContain("padding: 0");
  expect(rule(".rail--open")).toContain("padding: 0");
  expect(rule(".rail__list")).toContain("padding: 20px 18px");
});

test("a selected skill warms its button without borrowing the accent", () => {
  // One accent only: it marks the primary action, and a selection is a state rather than an action.
  const on = rule(".picker--on");
  expect(on).toContain("background: #f0e7de");
  expect(on).not.toContain("var(--accent)");
});

test("the layout and the sidebar now step at the same widths", () => {
  // They used to disagree: the sidebar stepped at 1000/780/640 and the layout stacked at 1100.
  // Madde 33 put both on the shell's measured width, so the stacking step is the sidebar's first.
  expect(grouped(".app-shell--narrow .chat-layout,")).not.toContain(".sidebar");
  expect(CSS).not.toContain("1100px");
});
