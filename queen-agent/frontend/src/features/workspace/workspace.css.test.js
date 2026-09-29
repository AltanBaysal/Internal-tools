import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { expect, test } from "vitest";

import { DEFAULT_RAIL_WIDTH } from "./railWidth.js";

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

test("the stopped line reads as a note, not as the answer", () => {
  // Same register as the steps above the answer and the count below it: all three are notes about
  // the text rather than the text itself.
  const line = rule(".msg__stopped");
  expect(line).toContain("var(--font-mono)");
  expect(line).toContain("color: var(--muted)");
});

test("the stamp reads as a note in the same voice as the line above it", () => {
  // What it says is a clock and maybe a count. Neither has a case, so the uppercase the label above
  // the message used to carry goes with the label.
  const stamp = rule(".msg__stamp");
  expect(stamp).toContain("var(--font-mono)");
  expect(stamp).toContain("color: var(--muted)");
  expect(stamp).not.toContain("text-transform");
});

test("a call is drawn on the card the repo already has", () => {
  // Not a second card language: the file card settled what a card looks like here, and a call
  // borrows its skeleton rather than inventing one beside it.
  const card = rule(".tool-call");
  expect(card).toContain("border-radius: 12px");
  expect(card).toContain("border: 1px solid var(--line)");
  expect(card).toContain("max-width: 340px");
});

test("only the handle offers to be pressed", () => {
  // A card you can press does something; a card you cannot is a record. Madde 78's rule, kept.
  expect(rule(".tool-call")).not.toContain("cursor");
  expect(rule(".tool-calls__handle")).toContain("cursor: pointer");
});

test("a call card sits back rather than forward", () => {
  // The file card is lit brighter than the page because it is a door and has to come forward. A
  // call opens nothing, so its fill goes under the page's own tone instead of above it -- and the
  // tone is the softest one the palette already holds rather than a new one.
  expect(rule(".tool-call")).toContain("background: #f4efe7");
  expect(rule(".tool-call")).not.toContain("var(--surface)");
  expect(rule(".tool-calls__handle")).toContain("background: #f4efe7");
  expect(rule(".tool-calls__handle")).not.toContain("var(--surface)");
});

test("a call reads in the stopped line's voice", () => {
  // The measure the owner named: the same grey as the word under an answer that was cut short.
  expect(rule(".tool-call__head")).toContain("color: var(--muted)");
  expect(rule(".tool-call__head")).not.toContain("var(--ink)");
  expect(rule(".tool-calls__summary")).toContain("color: var(--muted)");
  expect(rule(".tool-calls__summary")).not.toContain("var(--ink)");
});

test("the two lines the stamp replaces are gone", () => {
  // Madde 83 folded a label above the message and a count below it into one line under it. Either
  // name left behind would style something nothing draws any more.
  expect(CSS).not.toContain(".msg__label");
  expect(CSS).not.toContain(".token-count");
});

test("the send button is a fixed square", () => {
  // Madde 80 put a mark on it instead of a word, so it stops being as wide as its label. The two
  // marks must take the same room, or the button would widen and narrow as an answer runs.
  const send = rule(".composer__send");
  expect(send).toContain("width: 32px");
  expect(send).toContain("height: 32px");
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

test("reading in a narrow shell takes the whole area rather than lengthening the page", () => {
  // The column stays in place today and the reader is added beside it, which is the one thing the
  // contract forbids: the page itself scrolls.
  expect(rule(".app-shell--narrow .chat-layout--reading .chat")).toContain("display: none");
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

test("a tight shell shrinks the screen's title", () => {
  expect(rule(".app-shell--tight .screen__title")).toContain("font-size: 27px");
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

// Madde 338: the design's bar (queen-design v3, items 150, 159, 161, 166).
test("the bar is one height on every screen, its middle at the window's centre", () => {
  const bar = rule(".bar");
  expect(bar).toContain("height: 56px");
  expect(bar).toContain("flex: none");
  expect(bar).toContain("grid-template-columns: minmax(0, 1fr) minmax(0, auto) minmax(0, 1fr)");
});

test("the version is the name's own size and weight, never bold", () => {
  const name = rule(".bar__name");
  expect(name).toContain("font-family: var(--font-heading)");
  expect(name).toContain("font-size: 21px");
  expect(name).toContain("white-space: nowrap");
  // Nothing of its own but the weight, written out: the size and the ink are the name's.
  const version = rule(".bar__version");
  expect(version).toContain("font-weight: 400");
  expect(version).not.toContain("font-size");
  expect(version).not.toContain("color");
});

test("the project's name is cut on one line, and the way out keeps the right", () => {
  const project = rule(".bar__project");
  expect(project).toContain("max-width: 640px");
  expect(project).toContain("white-space: nowrap");
  expect(project).toContain("text-overflow: ellipsis");
  // With no project the middle draws nothing, and the button would slide into its column.
  const exit = rule(".bar__exit");
  expect(exit).toContain("grid-column: 3");
  expect(exit).toContain("justify-self: end");
});

test("the sidebar's brand is gone by every name", () => {
  for (const name of ["sidebar__brand", "sidebar__name", "sidebar__wordmark", "sidebar__version"]) {
    expect(CSS).not.toContain(`.${name}`);
  }
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

test("a file row's delete is there before it is reached for", () => {
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

test("the rail is a surface of its own rather than the canvas with a line on it", () => {
  expect(rule(".rail")).toContain("background: #fbf9f5");
});

test("the row being read is marked, and hovering is not the same as being open", () => {
  // Written as one grouped rule on purpose: being read outranks being pointed at, so the selected
  // tone has to survive the hover.
  //
  // Nothing in the app reaches this state since Madde 63 -- the rail's list is not drawn while a
  // file is open, and the project screen never marked its rows. FileRow keeps the capability and
  // its own test; narrowing that is a separate decision, and this note is here so the next reader
  // does not go looking for the caller.
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

// Madde 63: reading empties the rail rather than splitting it.

test("the rail has no list column while it is reading", () => {
  // Asked of the file rather than through rule(): that helper asserts the selector exists, so a
  // deleted rule would fail its assert instead of this one, and the test would go red saying the
  // wrong thing.
  //
  // Collected into a list rather than asked as `not.toContain`: a failing toContain on a file this
  // size prints the whole stylesheet, and whoever re-adds the rule one day deserves to be shown the
  // line they added instead of twenty thousand they did not.
  const found = CSS.split("\n").filter((line) => line.startsWith(".rail__list"));
  expect(found).toEqual([]);
});

test("nothing in the reading rail is spaced apart from anything", () => {
  // gap separates two children. There is one.
  expect(rule(".rail--open")).not.toContain("gap");
});

test("while reading, the rail has no width of its own", () => {
  // Madde 356 (the design's item 158): the list and the open file are one width. The app writes it
  // inline, and until anything is dragged .rail's 320 holds for both.
  expect(rule(".rail--open")).not.toMatch(/[\s;{]width:/);
  // Still flex with one child: the reader claims the space with flex: 1 rather than a width.
  expect(rule(".rail--open")).toContain("display: flex");
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

// Madde 340: the design's spinner (items 173, 181) is the live stamp's ring at twice the size, on
// the turn that ring already has, so no animation is invented for it.
test("the spinner is the live stamp's ring at 20px", () => {
  const ring = rule(".spinner");
  expect(ring).toContain("width: 20px");
  expect(ring).toContain("height: 20px");
  expect(ring).toContain("border: 1.5px solid var(--line)");
  expect(ring).toContain("border-top-color: var(--accent)");
  expect(ring).toContain("border-radius: 50%");
  expect(ring).toContain("animation: msg-spin 0.8s linear infinite");
});

test("in the file list the spinner stands centred where the rows will be", () => {
  const spot = rule(".file-list__spinner");
  expect(spot).toContain("display: flex");
  expect(spot).toContain("justify-content: center");
  expect(spot).toContain("padding: 24px 12px");
});

// Madde 355, design item 194: a chat opening turns the same ring where its messages will be.
test("in a chat that is opening the spinner stands centred where the messages will be", () => {
  const spot = rule(".chat__spinner");
  expect(spot).toContain("display: flex");
  expect(spot).toContain("justify-content: center");
  expect(spot).toContain("padding: 40px 12px");
});

test("the box and its pickers, shut while the chat opens, fade like every shut control", () => {
  expect(CSS).toMatch(/\n\.composer__input:disabled,\r?\n\.picker:disabled \{/);
  const shut = rule(".picker:disabled");
  expect(shut).toContain("cursor: default");
  expect(shut).toContain("opacity: 0.4");
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
  // The room the row used to hold moves to the opener, so the clickable area does not shrink.
  expect(rule(".file-row")).not.toContain("padding");
  expect(rule(".file-row__open")).toContain("padding: 10px 8px");
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
  // Once the body carries the design's 26/28, a container adding its own padding would sit under it.
  // The rail holding the reader adds none.
  expect(rule(".rail--open")).toContain("padding: 0");
});

// Madde 342 (tasarım 176, 186; APP-BUGS 48). Every rule that selects one of the names, comments taken
// out first so that a sentence about a class is not read as a selector.
function rulesSelecting(names) {
  const bare = CSS.replace(/\/\*[\s\S]*?\*\//g, "");
  return [...bare.matchAll(/([^{}]+)\{([^}]*)\}/g)]
    .map(([, selectors, body]) => ({ selectors: selectors.split(",").map((one) => one.trim()), body }))
    .filter(({ selectors }) => selectors.some((one) => names.some((name) => one.includes(name))));
}

test("the reader's head is the bar above the name, closed by a line", () => {
  const head = rule(".reader__head");
  expect(head).toContain("flex-direction: column");
  expect(head).toContain("border-bottom: 1px solid var(--line)");
});

test("the way back and the two tools stand at the bar's two edges", () => {
  const bar = rule(".reader__bar");
  expect(bar).toContain("justify-content: space-between");
  expect(bar).toContain("align-items: center");
});

test("a way back inside a row outweighs the way back's own margin", () => {
  // APP-BUGS 48: one class lost to .back's 18 by source order, and the arrow stood 9 above the
  // middle of its row. Two classes win wherever the rule is written.
  expect(rule(".back.back--inline")).toContain("margin-bottom: 0");
  expect(CSS).not.toContain("\n.back--inline {");
});

test("the reader's way back is framed like Refresh and Copy", () => {
  const back = rule(".reader__bar > .back");
  expect(back).toContain("border: 1px solid var(--line)");
  expect(back).toContain("background: var(--surface)");
  expect(back).toContain("border-radius: var(--radius-control)");
  expect(back).toContain("padding: 5px 11px");
});

test("the three buttons in the bar are one height", () => {
  expect(grouped(".reader__bar > button,")).toContain("line-height: 20px");
});

test("Copy is wide enough for Could not copy, and Download is gone", () => {
  expect(rule(".reader__copy")).toContain("min-width: 116px");
  expect(CSS).not.toContain(".reader__download");
});

test("no rule takes the ghost's frame off Refresh or Copy", () => {
  const theirs = rulesSelecting([".reader__refresh", ".reader__copy"]);
  expect(theirs.length).toBeGreaterThan(0);
  for (const { selectors, body } of theirs) {
    expect(body).not.toContain("border: none");
    expect(body).not.toContain("background: transparent");
    expect(selectors).not.toContain(".reader__refresh:hover");
    expect(selectors).not.toContain(".reader__copy:hover");
  }
});

// Madde 350 (the design's item 175): the heading and Refresh share one row, and the 12 under the
// heading is the row's now.
test("the heading's row lays the heading and Refresh side by side", () => {
  const row = rule(".rail__bar");
  expect(row).toContain("display: flex");
  expect(row).toContain("align-items: center");
  expect(row).toContain("margin-bottom: 12px");
});

test("the heading takes what Refresh leaves of the row", () => {
  const head = rule(".rail__head");
  expect(head).toContain("flex: 1");
  expect(head).not.toContain("width: 100%");
  expect(head).not.toContain("margin-bottom");
  expect(rule(".rail__head--still")).not.toContain("margin-bottom");
});

test("no rule takes the ghost's frame off the list's Refresh", () => {
  for (const { selectors, body } of rulesSelecting([".file-list__refresh"])) {
    expect(body).not.toContain("border: none");
    expect(body).not.toContain("background: transparent");
    expect(selectors).not.toContain(".file-list__refresh:hover");
  }
});

test("a selected skill warms its button without borrowing the accent", () => {
  // One accent only: it marks the primary action, and a selection is a state rather than an action.
  const on = rule(".picker--on");
  expect(on).toContain("background: #f0e7de");
  expect(on).not.toContain("var(--accent)");
});

test("the layout and the sidebar step at the same widths", () => {
  // They used to disagree: the sidebar stepped at 1000/780/640 and the layout stacked at 1100.
  // Madde 33 put both on the shell's measured width; Madde 50 took the chat's rail out of the
  // stacking, and Madde 353 took the project screen that was left stacking.
  expect(CSS).not.toContain("1100px");
});

test("the chat's rail stays beside the conversation at every width", () => {
  // v2 Madde 33 dropped it under the chat below 1000px. The user asked for VS Code: it stays on the
  // right and closes instead. No step may name the chat's layout or its rail again.
  for (const step of ["narrow", "tight", "compact"]) {
    expect(CSS).not.toContain(`.app-shell--${step} .chat-layout {`);
    expect(CSS).not.toContain(`.app-shell--${step} .chat-layout,`);
    expect(CSS).not.toContain(`.app-shell--${step} .rail`);
  }
});

test("the width the rail starts at is one number said twice, and the two agree", () => {
  // The app writes it inline from the first frame; the stylesheet's is what holds where nothing is
  // said. Two copies of a number are a lie waiting to happen, so they are pinned to each other.
  expect(rule(".rail")).toContain(`width: ${DEFAULT_RAIL_WIDTH}px`);
});

test("a folded sidebar is a strip, and it gets there by its own transition", () => {
  // Not hidden: a strip stands where it was, carrying the button that brings it back. The rail's
  // rule, on the other side of the screen.
  expect(rule(".sidebar")).toContain("transition: width 220ms");
  const folded = rule(".sidebar--collapsed");
  expect(folded).toContain("width: 52px");
  expect(folded).toContain("overflow: hidden");
});

// Madde 351 (design 174, 187): the fold is a panel icon in the sidebar's own last row.
test("the fold's row keeps to the sidebar's bottom right", () => {
  const foot = rule(".sidebar__foot");
  expect(foot).toContain("display: flex");
  expect(foot).toContain("justify-content: flex-end");
  expect(foot).toContain("margin-top: auto");
});

test("the fold is a square button with no glyph of its own", () => {
  const fold = rule(".sidebar__fold");
  expect(fold).toContain("width: 30px");
  expect(fold).toContain("height: 30px");
  expect(fold).toContain("background: transparent");
  expect(fold).not.toContain("font-size");
});

test("the panel icon is a square with a line near its left edge", () => {
  const icon = rule(".sidebar__panel-icon");
  expect(icon).toContain("width: 16px");
  expect(icon).toContain("height: 16px");
  expect(icon).toContain("border: 1.5px solid var(--ink)");
  expect(icon).toContain("border-radius: 3px");
  const line = rule(".sidebar__panel-icon::after");
  expect(line).toContain("left: 6px");
  expect(line).toContain("border-left: 1.5px solid var(--ink)");
});

test("folded, New chat is a square holding only its plus", () => {
  const plus = rule(".sidebar__new-chat--icon");
  expect(plus).toContain("width: 30px");
  expect(plus).toContain("height: 30px");
  expect(plus).toContain("padding: 0");
  expect(plus).toContain("justify-content: center");
});

test("the easing is for folding, and a drag turns it off", () => {
  // 220ms is right for a rail folding itself away and wrong for one following the pointer.
  expect(rule(".rail")).toContain("transition: width 220ms");
  expect(rule(".rail--dragging")).toContain("transition: none");
});

test("the rail's folding control is big enough and dark enough to find", () => {
  // It was too faint to see -- 15px of muted grey on a surface nearly the same colour. The
  // sidebar's fold was the other half of this rule until Madde 351 made it an icon.
  expect(rule(".rail__chevron")).toContain("font-size: 20px");
  expect(rule(".rail__chevron")).toContain("color: var(--ink)");
});

test("the grip is on the rail's left edge and says it can be pulled", () => {
  const grip = rule(".rail__grip");
  expect(grip).toContain("cursor: col-resize");
  expect(grip).toContain("left: 0");
});

test("the grip stands above the reader", () => {
  // Madde 356 (the design's item 177): the reader's fadeIn lifts it into the grip's paint layer, and
  // as the later sibling it would cover the grip, so the pointer never reached the edge.
  expect(rule(".rail__grip")).toContain("z-index: 1");
});

test("nothing in the stylesheet draws a model's name", () => {
  // Madde 358: no model is shown anywhere, and this rule has drawn nothing since Madde 82.
  expect(CSS).not.toContain(".model-label");
});

test("the gauge pushes the rest of the foot to the far end", () => {
  // Madde 92. Not `space-between` on the foot: the pickers and Send are separate items in that
  // row, and spreading the row would put its whole width between them.
  expect(rule(".composer__gauge")).toContain("margin-right: auto");
});

test("the gauge's words are the notes' mono in the pickers' ink", () => {
  // Madde 343, design items 146 and 182. Not --muted: that is 3.7:1 on the composer's box.
  const words = rule(".context-gauge__words");
  expect(words).toContain("font-family: var(--font-mono)");
  expect(words).toContain("font-size: 11.5px");
  expect(words).toContain("color: #6b6259");
});

test("the words stand 6 from the circle, the stamp's gap", () => {
  expect(rule(".composer__gauge")).toContain("gap: 6px");
});

// --- editing a message, and the versions it leaves behind (Madde 195) ----------------------------

test("nothing wraps the bubble in a row of its own", () => {
  // Madde 197, and Madde 195's own defect. .msg is a column with align-items: flex-end for the
  // user, so a row wrapper became the thing being aligned -- and the bubble's max-width then
  // measured against the wrapper instead of the column. Every message's right edge landed
  // somewhere else. The fix is the wrapper being gone, not a rule correcting it.
  expect(CSS).not.toContain(".msg__said");
});

test("the field that corrects a message is the width the message was", () => {
  // Opening the edit must not make the message grow or shrink: what is being corrected is that
  // sentence, in its place, at its size.
  expect(rule(".msg__editing")).toContain("max-width: 78%");
});

test("the tick and the cross sit under the field, in the message's own direction", () => {
  const actions = rule(".msg__editing-actions");
  expect(actions).toContain("display: flex");
  expect(actions).toContain("justify-content: flex-end");
});

test("the edit is quiet until it is wanted", () => {
  // Present at every width and on a touch screen -- hidden until hover is a control that does not
  // exist on half the devices the app runs on. Quiet instead, and full strength when reached for.
  expect(rule(".msg__edit")).toContain("opacity: 0.35");
  expect(rule(".msg--user:hover .msg__edit")).toContain("opacity: 1");
  expect(rule(".msg__edit:focus-visible")).toContain("opacity: 1");
});

test("the version strip reads in the stamp's voice", () => {
  // It is a note about the message, exactly as the time under it is, and two notes under one
  // sentence in two different voices read as two different kinds of thing.
  const strip = rule(".versions");
  expect(strip).toContain("font-family: var(--font-mono)");
  expect(strip).toContain("font-size: 11.5px");
  expect(strip).toContain("color: var(--muted)");
});

test("an arrow with nothing to step to does not offer to be pressed", () => {
  expect(rule(".versions__step:disabled")).toContain("cursor: default");
  expect(rule(".versions__step:disabled")).toContain("opacity: 0.3");
});

// --- the notes under a message on one row (Madde 199, Madde 348) --------------------------------

test("the notes under a message share the stamp's one row", () => {
  // .msg is a column, so two children of it are two lines. Madde 199's row put the arrows and the
  // pencil beside each other and left the time a line below them; design item 139 puts all three
  // on the stamp's row, 6 apart. The bubble stays a child of the column, which is what Madde 197
  // fixed.
  const stamp = rule(".msg__stamp");
  expect(stamp).toContain("display: flex");
  expect(stamp).toContain("align-items: center");
  expect(stamp).toContain("gap: 6px");
  expect(CSS).not.toContain(".msg__foot");
});

test("the strip carries no gap of its own", () => {
  // Inside the row now, so a margin of its own would sit on top of the column's gap and push the
  // line down away from the message it belongs to.
  expect(rule(".versions")).not.toContain("margin-top");
});

test("cached is the design's darker green and missed the destructive red", () => {
  // Madde 354, design items 189 and 192: the app's only green, darkened to read on the canvas, and
  // the red that marks a cost here rather than a destruction.
  expect(rule(".msg__stamp-cached")).toContain("color: #536747");
  expect(rule(".msg__stamp-missed")).toContain("color: var(--destructive)");
});

// Madde 352: the full chat's notice stands in the box's place in the box's own shape (design item
// 140, kit.css's .full).
test("the full chat's notice is shaped like the box it stands in for", () => {
  const notice = rule(".full");
  expect(notice).toContain("max-width: 720px");
  expect(notice).toContain("border-radius: 14px");
  expect(notice).toContain("padding: 14px 16px 10px");
  expect(rule(".full__line")).toContain("font-size: 14px");
  expect(rule(".full__detail")).toContain("font-size: 13px");
  expect(rule(".full__detail")).toContain("color: #6b6259");
  expect(rule(".full__actions")).toContain("justify-content: flex-end");
});

// --- All projects (Madde 353; the design's items 142, 167, kit.css's .all-projects__*) ------------

test("the project screen, the empty screen and the skeleton left no rule behind", () => {
  // They went with the screens that drew them, and so did the reader's ×; the skeleton's last place
  // went with Madde 355. Comments are taken out first, so a sentence about a class is not read as a
  // rule; collected rather than asked with not.toContain, so a failure prints the lines at fault and
  // not the whole stylesheet.
  const gone = [
    ".screen-layout",
    ".project-grid",
    ".chat-list",
    ".chat-row",
    ".column__title",
    ".screen__title-row",
    ".screen__delete",
    ".file-list__bar",
    ".panel",
    ".skeleton",
    ".reader__close",
    ".empty__title",
    ".empty__line",
  ];
  const selectors = CSS.replace(/\/\*[\s\S]*?\*\//g, "")
    .split("\n")
    .filter((line) => line && !/^\s/.test(line));
  expect(selectors.filter((line) => gone.some((name) => line.includes(name)))).toEqual([]);
});

test("PINNED and RECENT are the design's label", () => {
  // Not --muted, which falls under the 4.5:1 text needs (the design's DESIGN-STANDARD, Colour).
  const label = rule(".all-projects__label");
  expect(label).toContain("font-size: 11px");
  expect(label).toContain("letter-spacing: 0.09em");
  expect(label).toContain("text-transform: uppercase");
  expect(label).toContain("color: #6b6259");
});

test("a project row is 48 tall between two hairlines", () => {
  expect(rule(".all-projects__row")).toContain("min-height: 48px");
  expect(rule(".all-projects__row")).toContain("border-bottom: 1px solid #e9e3da");
  expect(rule(".all-projects__list")).toContain("border-top: 1px solid #e9e3da");
});

test("the time is the row's one fixed column", () => {
  const when = rule(".all-projects__row-when");
  expect(when).toContain("width: 96px");
  expect(when).toContain("text-align: right");
  expect(when).toContain("font-family: var(--font-mono)");
});

test("the head puts the title and + New project at its two ends", () => {
  const head = rule(".all-projects__head");
  expect(head).toContain("display: flex");
  expect(head).toContain("justify-content: space-between");
  expect(head).toContain("margin: 0 0 24px");
});

test("No projects yet. is the design's quiet line", () => {
  const empty = rule(".all-projects__empty");
  expect(empty).toContain("padding: 18px 12px");
  expect(empty).toContain("color: #a79e93");
});
