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

test("under New chat stand the chats and then the fold, and nothing else", () => {
  const { container } = render(<Sidebar chats={CHATS} onToggle={vi.fn()} />);
  const rows = [...container.querySelector(".sidebar").children].map((child) => child.className);
  expect(rows).toEqual(["sidebar__new-chat", "sidebar__chats", "sidebar__foot"]);
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

test("with chats, nothing says there are none", () => {
  render(<Sidebar chats={CHATS} />);
  expect(screen.queryByText("No chats yet.")).toBeNull();
});

test("clicking a chat asks to open it", () => {
  // They all live in the project on screen, so the row does not have to carry one.
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

test("the sidebar carries no search control", () => {
  // Search chats arrives with Madde 365.
  render(<Sidebar chats={CHATS} />);
  expect(screen.queryByText("Search")).toBeNull();
  expect(screen.queryByText("⌘K")).toBeNull();
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

test("folded, the chats are gone and the column holds + and the fold alone", () => {
  const { container } = render(<Sidebar chats={CHATS} collapsed onToggle={vi.fn()} />);
  expect(screen.queryByText("Write the intro")).toBeNull();
  const buttons = [...container.querySelectorAll(".sidebar button")];
  expect(buttons.map((button) => button.getAttribute("aria-label"))).toEqual([
    "New chat",
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
