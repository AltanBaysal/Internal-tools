import { fireEvent, render, screen, within } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import { VERSION } from "../../shared/version.js";
import Sidebar from "./Sidebar.jsx";

const CHATS = [
  { id: "c1", title: "Write the intro" },
  { id: "c2", title: "Missing values" },
];

// Madde 362 (design 151, 152, 168): inside a project the sidebar is the project's own -- a filled
// + New chat first, then every chat it holds. Projects are reached from All projects, and the name
// of the open one is in the bar, so the sidebar lists none of them.

test("the sidebar leads with a filled + New chat", () => {
  const { container } = render(<Sidebar chats={CHATS} />);
  const first = container.querySelector(".sidebar").firstElementChild;
  expect(first.className).toBe("sidebar__new-chat");
  expect(first.textContent).toBe("+New chat");
});

test("under New chat stand the search, the chats and the fold, and nothing else", () => {
  // Madde 365 (design 151, 168): Search chats between New chat and the chats it searches.
  const { container } = render(<Sidebar chats={CHATS} onToggle={vi.fn()} />);
  const rows = [...container.querySelector(".sidebar").children].map((child) => child.className);
  expect(rows).toEqual(["sidebar__new-chat", "sidebar__search", "sidebar__chats", "sidebar__foot"]);
});

test("there is no list of projects, no Recent chats and no + for a new project", () => {
  // A new project is made from All projects (Madde 361), the one place projects are listed.
  const { container } = render(<Sidebar chats={CHATS} />);
  expect(screen.queryByText("Projects")).toBeNull();
  expect(screen.queryByText("Recent chats")).toBeNull();
  expect(screen.queryByRole("button", { name: "New project" })).toBeNull();
  expect(container.querySelector(".sidebar__row-open")).toBeNull();
  expect(container.querySelector(".dot")).toBeNull();
});

test("the project's chats are listed with no label above them, the open one marked", () => {
  const { container } = render(<Sidebar chats={CHATS} activeChatId="c2" />);
  expect(container.querySelectorAll(".sidebar__chat").length).toBe(2);
  expect(screen.getByText("Write the intro")).toBeTruthy();
  expect(screen.getByText("Missing values").className).toContain("sidebar__chat--active");
  expect(container.querySelector(".sidebar__chats").firstElementChild.className).toContain(
    "sidebar__chat",
  );
});

test("every chat of the project is listed", () => {
  // The eight-row cap was room shared with a projects list; the list scrolls inside itself now.
  const many = Array.from({ length: 12 }, (_, i) => ({ id: `c${i}`, title: `Chat ${i}` }));
  const { container } = render(<Sidebar chats={many} />);
  expect(container.querySelectorAll(".sidebar__chat").length).toBe(12);
  expect(screen.getByText("Chat 11")).toBeTruthy();
});

test("a project with no chats says so", () => {
  render(<Sidebar chats={[]} />);
  const empty = screen.getByText("No chats yet.");
  expect(empty.className).toBe("sidebar__empty");
  expect(empty.closest(".sidebar__chats")).toBeTruthy();
});

test("loading draws neither rows nor No chats yet.", () => {
  // Madde 457: before the project's own answer there is no list -- not the last project's, and not
  // none. The design draws no wait in the sidebar, so its place stays empty; the search stays.
  const { container } = render(<Sidebar chats={CHATS} loading />);
  expect(container.querySelector(".sidebar__chats").children.length).toBe(0);
  expect(screen.queryByText("No chats yet.")).toBeNull();
  expect(screen.getByRole("textbox", { name: "Search chats" })).toBeTruthy();
});

test("with chats, nothing says there are none", () => {
  render(<Sidebar chats={CHATS} />);
  expect(screen.queryByText("No chats yet.")).toBeNull();
});

test("clicking a chat asks to open it", () => {
  // They all live in the project on screen, so the row does not have to carry one. And only the
  // id: the reply box is handed the focus by Search chats' Enter alone (Madde 365).
  const onOpenChat = vi.fn();
  render(<Sidebar chats={CHATS} onOpenChat={onOpenChat} />);
  fireEvent.click(screen.getByText("Write the intro"));
  expect(onOpenChat).toHaveBeenCalledWith("c1");
});

test("New chat asks rather than creating anything itself", () => {
  const onNewChat = vi.fn();
  render(<Sidebar chats={CHATS} onNewChat={onNewChat} />);
  fireEvent.click(screen.getByRole("button", { name: /New chat/ }));
  expect(onNewChat).toHaveBeenCalled();
});

// Madde 62: the key comes from the environment now. There is no settings screen, so there is
// nothing for a row at the foot of the sidebar to open.
test("there is no Settings row", () => {
  render(<Sidebar chats={CHATS} />);
  expect(screen.queryByRole("button", { name: "Settings" })).toBeNull();
});

// Madde 338: the brand moved into the bar above the sidebar.
test("the sidebar carries no brand", () => {
  const { container } = render(<Sidebar chats={CHATS} />);
  expect(screen.queryByText("QueenAgent")).toBeNull();
  expect(screen.queryByText(VERSION)).toBeNull();
  expect(container.querySelector(".sidebar__brand")).toBeNull();
});

// Madde 51: one button, never a drag -- claude.ai's behaviour rather than the rail's. Madde 351
// (design 174, 187): the button is a panel icon in the sidebar's own last row, and folded the
// sidebar is an icon column -- + for New chat, and the same icon at its foot.

test("the sidebar carries one button that puts it away", () => {
  render(<Sidebar chats={CHATS} onToggle={vi.fn()} />);
  expect(screen.getByRole("button", { name: "Hide the sidebar" })).toBeTruthy();
});

test("the button asks to fold rather than folding by itself", () => {
  // The state lasts the session and crosses addresses, so it lives in App.
  const onToggle = vi.fn();
  render(<Sidebar chats={CHATS} onToggle={onToggle} />);
  fireEvent.click(screen.getByRole("button", { name: "Hide the sidebar" }));
  expect(onToggle).toHaveBeenCalled();
});

test("folded, the chats are gone and the column holds +, the search and the fold", () => {
  // Madde 365 (design 174): the search icon stands under the +.
  const { container } = render(<Sidebar chats={CHATS} collapsed onToggle={vi.fn()} />);
  expect(screen.queryByText("Write the intro")).toBeNull();
  const buttons = [...container.querySelectorAll(".sidebar button")];
  expect(buttons.map((button) => button.getAttribute("aria-label"))).toEqual([
    "New chat",
    "Search chats",
    "Show the sidebar",
  ]);
});

test("folded, the same button is what brings it back", () => {
  const onToggle = vi.fn();
  render(<Sidebar chats={CHATS} collapsed onToggle={onToggle} />);
  fireEvent.click(screen.getByRole("button", { name: "Show the sidebar" }));
  expect(onToggle).toHaveBeenCalled();
});

test("folded, it says so where the stylesheet can hear it", () => {
  const { container } = render(<Sidebar chats={CHATS} collapsed onToggle={vi.fn()} />);
  expect(container.querySelector(".sidebar").className).toContain("sidebar--collapsed");
});

// Madde 351: Claude Code's place for it -- the sidebar's bottom right, and there in both states, so
// a press never moves out from under the pointer.
test("the fold is the sidebar's last row", () => {
  const { container } = render(<Sidebar chats={CHATS} onToggle={vi.fn()} />);
  const foot = container.querySelector(".sidebar").lastElementChild;
  expect(foot.className).toBe("sidebar__foot");
  expect(within(foot).getByRole("button", { name: "Hide the sidebar" })).toBeTruthy();
});

test("folded, the fold is still the last row", () => {
  const { container } = render(<Sidebar chats={CHATS} collapsed onToggle={vi.fn()} />);
  const foot = container.querySelector(".sidebar").lastElementChild;
  expect(foot.className).toBe("sidebar__foot");
  expect(within(foot).getByRole("button", { name: "Show the sidebar" })).toBeTruthy();
});

test("the fold is a panel icon rather than an arrow, open or folded", () => {
  const { rerender } = render(<Sidebar chats={CHATS} onToggle={vi.fn()} />);
  const open = screen.getByRole("button", { name: "Hide the sidebar" });
  expect(open.querySelector(".sidebar__panel-icon")).toBeTruthy();
  expect(open.textContent).toBe("");
  rerender(<Sidebar chats={CHATS} collapsed onToggle={vi.fn()} />);
  const folded = screen.getByRole("button", { name: "Show the sidebar" });
  expect(folded.querySelector(".sidebar__panel-icon")).toBeTruthy();
  expect(folded.textContent).toBe("");
});

test("folded, New chat stays as a + of its own", () => {
  const onNewChat = vi.fn();
  render(<Sidebar chats={CHATS} collapsed onToggle={vi.fn()} onNewChat={onNewChat} />);
  const plus = screen.getByRole("button", { name: "New chat" });
  expect(plus.className).toContain("sidebar__new-chat--icon");
  expect(plus.textContent).toBe("+");
  fireEvent.click(plus);
  expect(onNewChat).toHaveBeenCalled();
});

// --- Search chats (Madde 365; design 151, 168, 174) ------------------------------------------------

const search = () => screen.getByRole("textbox", { name: "Search chats" });
const type = (value) => fireEvent.change(search(), { target: { value } });
const press = (key) => fireEvent.keyDown(search(), { key });
const rows = (container) =>
  [...container.querySelectorAll(".sidebar__chat")].map((row) => row.textContent);

test("the search is a box named Search chats, and the project does not open onto it", () => {
  // The design gives it no focus on arrival; the browser's own suggestions would cover the list.
  render(<Sidebar chats={CHATS} />);
  expect(search().getAttribute("placeholder")).toBe("Search chats");
  expect(search().getAttribute("autocomplete")).toBe("off");
  expect(document.activeElement).not.toBe(search());
});

test("typing narrows the chats by title, whatever the case and the accents", () => {
  const { container } = render(
    <Sidebar chats={[...CHATS, { id: "c3", title: "Café notes" }]} />,
  );
  type("missing");
  expect(rows(container)).toEqual(["Missing values"]);
  type("CAFE");
  expect(rows(container)).toEqual(["Café notes"]);
});

test("with no match the list says so, with what was typed", () => {
  const { container } = render(<Sidebar chats={CHATS} />);
  type("  zebra ");
  const none = screen.getByText('No chats match "zebra".');
  expect(none.className).toBe("sidebar__empty");
  expect(none.closest(".sidebar__chats")).toBeTruthy();
  expect(rows(container)).toEqual([]);
  expect(screen.queryByText("No chats yet.")).toBeNull();
});

test("a project with no chats says no match once something is typed", () => {
  // The design's sidebar asks about the query first.
  render(<Sidebar chats={[]} />);
  type("x");
  expect(screen.getByText('No chats match "x".')).toBeTruthy();
});

test("Enter asks to open the first match and to hand it the reply box", () => {
  const onOpenChat = vi.fn();
  render(<Sidebar chats={CHATS} onOpenChat={onOpenChat} />);
  type("missing");
  press("Enter");
  expect(onOpenChat).toHaveBeenCalledWith("c2", { focusReply: true });
});

test("Enter in an empty box opens the first chat", () => {
  // An empty query is every chat, and the server lists the most recent first.
  const onOpenChat = vi.fn();
  render(<Sidebar chats={CHATS} onOpenChat={onOpenChat} />);
  press("Enter");
  expect(onOpenChat).toHaveBeenCalledWith("c1", { focusReply: true });
});

test("Enter with no match asks for nothing", () => {
  const onOpenChat = vi.fn();
  render(<Sidebar chats={CHATS} onOpenChat={onOpenChat} />);
  type("zebra");
  press("Enter");
  expect(onOpenChat).not.toHaveBeenCalled();
});

test("Escape empties the box and brings every chat back", () => {
  const { container } = render(<Sidebar chats={CHATS} />);
  type("missing");
  press("Escape");
  expect(search().value).toBe("");
  expect(rows(container)).toEqual(["Write the intro", "Missing values"]);
});

test("folded, the search is a drawn magnifier with no text", () => {
  render(<Sidebar chats={CHATS} collapsed onToggle={vi.fn()} />);
  const toggle = screen.getByRole("button", { name: "Search chats" });
  expect(toggle.className).toBe("sidebar__search-toggle");
  expect(toggle.querySelector(".sidebar__search-icon")).toBeTruthy();
  expect(toggle.textContent).toBe("");
});

test("folded, the search asks to unfold and then holds the focus", () => {
  // Whether the sidebar is folded is App's; where the focus lands once it opens is the sidebar's.
  const onToggle = vi.fn();
  const { rerender } = render(<Sidebar chats={CHATS} collapsed onToggle={onToggle} />);
  fireEvent.click(screen.getByRole("button", { name: "Search chats" }));
  expect(onToggle).toHaveBeenCalled();
  rerender(<Sidebar chats={CHATS} onToggle={onToggle} />);
  expect(document.activeElement).toBe(search());
});

test("unfolded by the fold, the search does not take the focus", () => {
  const onToggle = vi.fn();
  const { rerender } = render(<Sidebar chats={CHATS} collapsed onToggle={onToggle} />);
  fireEvent.click(screen.getByRole("button", { name: "Show the sidebar" }));
  rerender(<Sidebar chats={CHATS} onToggle={onToggle} />);
  expect(document.activeElement).not.toBe(search());
});

test("folding and unfolding keeps what was typed", () => {
  const { container, rerender } = render(<Sidebar chats={CHATS} onToggle={vi.fn()} />);
  type("missing");
  rerender(<Sidebar chats={CHATS} collapsed onToggle={vi.fn()} />);
  rerender(<Sidebar chats={CHATS} onToggle={vi.fn()} />);
  expect(search().value).toBe("missing");
  expect(rows(container)).toEqual(["Missing values"]);
});

// --- A chat list that could not be read (Madde 386; 364's pattern, the design has none) ---------

// What failure.js makes of a Flask 500 page: the code and the body, as they came.
const RAW = "HTTP 500: <!doctype html>\n<title>500 Internal Server Error</title>";

function stubClipboard(answer) {
  const writeText = vi.fn(() => answer);
  Object.defineProperty(navigator, "clipboard", { value: { writeText }, configurable: true });
  return writeText;
}

test("a chat list that could not be read says so, not that there are none", () => {
  // The chats are on disk; only the read failed. The raw words are Copy's, not the sidebar's.
  render(<Sidebar chats={[]} error={RAW} />);
  const said = screen.getByText("Couldn't load chats.");
  expect(said.className).toBe("sidebar__error");
  expect(said.closest(".sidebar__chats")).toBeTruthy();
  expect(screen.queryByText("No chats yet.")).toBeNull();
  expect(screen.queryByText(/HTTP 500/)).toBeNull();
});

test("under the sentence stand Try again and Copy, and Try again asks for the list again", () => {
  const onRetry = vi.fn();
  const { container } = render(<Sidebar chats={[]} error={RAW} onRetry={onRetry} />);
  const buttons = [...container.querySelectorAll(".sidebar__chats button")];
  expect(buttons.map((one) => one.textContent)).toEqual(["Try again", "Copy"]);
  expect(buttons[0].className).toBe("failure__retry");
  expect(buttons[1].className).toBe("ghost sidebar__copy");
  fireEvent.click(buttons[0]);
  expect(onRetry).toHaveBeenCalled();
});

test("its Copy puts the error on the clipboard exactly as it came", async () => {
  const writeText = stubClipboard(Promise.resolve());
  render(<Sidebar chats={[]} error={RAW} />);
  fireEvent.click(screen.getByRole("button", { name: "Copy" }));
  expect(writeText).toHaveBeenCalledWith(RAW);
  expect(await screen.findByRole("button", { name: "Copied" })).toBeTruthy();
});

test("the failure stands in the rows' place, whatever was listed and whatever is typed", () => {
  // A failed read leaves the project's last list standing, maybe no longer what it holds -- so it is
  // not shown.
  const { container } = render(<Sidebar chats={CHATS} error={RAW} />);
  expect(rows(container)).toEqual([]);
  type("zebra");
  expect(screen.queryByText('No chats match "zebra".')).toBeNull();
  expect(screen.getByText("Couldn't load chats.")).toBeTruthy();
});

test("with the list unread, Enter opens nothing", () => {
  const onOpenChat = vi.fn();
  render(<Sidebar chats={CHATS} error={RAW} onOpenChat={onOpenChat} />);
  press("Enter");
  expect(onOpenChat).not.toHaveBeenCalled();
});

test("the failure leaves the sidebar's rows where they were", () => {
  const { container } = render(<Sidebar chats={[]} error={RAW} onToggle={vi.fn()} />);
  const shape = [...container.querySelector(".sidebar").children].map((child) => child.className);
  expect(shape).toEqual(["sidebar__new-chat", "sidebar__search", "sidebar__chats", "sidebar__foot"]);
});
