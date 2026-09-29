import { fireEvent, render, screen, within } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import { VERSION } from "../../shared/version.js";
import Sidebar from "./Sidebar.jsx";

const PROJECTS = [
  { id: "p1", name: "Thesis research", chats: 3, files: 3 },
  { id: "p2", name: "Product notes", chats: 2, files: 2 },
];

test("with no project selected only the projects remain", () => {
  // Chats belong to a project, so with none selected neither control has anywhere to point.
  render(<Sidebar projects={PROJECTS} activeProjectId={null} />);
  expect(screen.getByText("Projects")).toBeTruthy();
  expect(screen.queryByText("Recent chats")).toBeNull();
  expect(screen.queryByRole("button", { name: /New chat/ })).toBeNull();
});

// Madde 62: the key comes from the environment now. There is no settings screen, so there is
// nothing for a row at the foot of the sidebar to open.
test("there is no Settings row", () => {
  render(<Sidebar projects={PROJECTS} activeProjectId="p1" />);
  expect(screen.queryByRole("button", { name: "Settings" })).toBeNull();
});

// Madde 51: one button, never a drag -- claude.ai's behaviour rather than the rail's. Madde 351
// (design 174, 187): the button is a panel icon in the sidebar's own last row, and folded the
// sidebar is an icon column -- + for New chat, and the same icon at its foot.

test("the sidebar carries one button that puts it away", () => {
  render(<Sidebar projects={PROJECTS} activeProjectId="p1" onToggle={vi.fn()} />);
  expect(screen.getByRole("button", { name: "Hide the sidebar" })).toBeTruthy();
});

test("the button asks to fold rather than folding by itself", () => {
  // The state lasts the session and crosses addresses, so it lives in App.
  const onToggle = vi.fn();
  render(<Sidebar projects={PROJECTS} activeProjectId="p1" onToggle={onToggle} />);
  fireEvent.click(screen.getByRole("button", { name: "Hide the sidebar" }));
  expect(onToggle).toHaveBeenCalled();
});

test("folded, the projects and chats are gone", () => {
  render(<Sidebar projects={PROJECTS} activeProjectId="p1" collapsed onToggle={vi.fn()} />);
  expect(screen.queryByText("Projects")).toBeNull();
  expect(screen.queryByText("Thesis research")).toBeNull();
  expect(screen.queryByText("Recent chats")).toBeNull();
});

test("folded, the same button is what brings it back", () => {
  const onToggle = vi.fn();
  render(<Sidebar projects={PROJECTS} activeProjectId="p1" collapsed onToggle={onToggle} />);
  fireEvent.click(screen.getByRole("button", { name: "Show the sidebar" }));
  expect(onToggle).toHaveBeenCalled();
});

test("folded, it says so where the stylesheet can hear it", () => {
  const { container } = render(<Sidebar projects={PROJECTS} collapsed onToggle={vi.fn()} />);
  expect(container.querySelector(".sidebar").className).toContain("sidebar--collapsed");
});

// Madde 338: the brand moved into the bar above the sidebar.
test("the sidebar carries no brand", () => {
  const { container } = render(<Sidebar projects={PROJECTS} activeProjectId="p1" />);
  expect(screen.queryByText("QueenAgent")).toBeNull();
  expect(screen.queryByText(VERSION)).toBeNull();
  expect(container.querySelector(".sidebar__brand")).toBeNull();
});

// Madde 351: Claude Code's place for it -- the sidebar's bottom right, and there in both states, so
// a press never moves out from under the pointer.
test("the fold is the sidebar's last row", () => {
  const { container } = render(
    <Sidebar projects={PROJECTS} activeProjectId="p1" onToggle={vi.fn()} />,
  );
  const foot = container.querySelector(".sidebar").lastElementChild;
  expect(foot.className).toBe("sidebar__foot");
  expect(within(foot).getByRole("button", { name: "Hide the sidebar" })).toBeTruthy();
});

test("folded, the fold is still the last row", () => {
  const { container } = render(
    <Sidebar projects={PROJECTS} activeProjectId="p1" collapsed onToggle={vi.fn()} />,
  );
  const foot = container.querySelector(".sidebar").lastElementChild;
  expect(foot.className).toBe("sidebar__foot");
  expect(within(foot).getByRole("button", { name: "Show the sidebar" })).toBeTruthy();
});

test("the fold is a panel icon rather than an arrow, open or folded", () => {
  const { rerender } = render(
    <Sidebar projects={PROJECTS} activeProjectId="p1" onToggle={vi.fn()} />,
  );
  const open = screen.getByRole("button", { name: "Hide the sidebar" });
  expect(open.querySelector(".sidebar__panel-icon")).toBeTruthy();
  expect(open.textContent).toBe("");
  rerender(<Sidebar projects={PROJECTS} activeProjectId="p1" collapsed onToggle={vi.fn()} />);
  const folded = screen.getByRole("button", { name: "Show the sidebar" });
  expect(folded.querySelector(".sidebar__panel-icon")).toBeTruthy();
  expect(folded.textContent).toBe("");
});

test("folded, New chat stays as a + of its own", () => {
  const onNewChat = vi.fn();
  render(
    <Sidebar
      projects={PROJECTS}
      activeProjectId="p1"
      collapsed
      onToggle={vi.fn()}
      onNewChat={onNewChat}
    />,
  );
  const plus = screen.getByRole("button", { name: "New chat" });
  expect(plus.className).toContain("sidebar__new-chat--icon");
  expect(plus.textContent).toBe("+");
  fireEvent.click(plus);
  expect(onNewChat).toHaveBeenCalled();
});

test("folded with no project open, the fold stands alone", () => {
  // Open, New chat is there only with a project; folded, its + follows the same rule.
  const { container } = render(
    <Sidebar projects={PROJECTS} activeProjectId={null} collapsed onToggle={vi.fn()} />,
  );
  expect(screen.queryByRole("button", { name: "New chat" })).toBeNull();
  expect(container.querySelectorAll(".sidebar button").length).toBe(1);
});

test("every project dot is the same tone", () => {
  // One accent marks the primary action and nothing else, so a project has no colour of its own --
  // two projects are told apart by name.
  const { container } = render(<Sidebar projects={PROJECTS} activeProjectId="p1" />);
  const dots = [...container.querySelectorAll(".dot")];
  expect(dots.length).toBe(2);
  expect(dots.every((dot) => dot.getAttribute("style") === null)).toBe(true);
});

test("a project with no files still holds the badge's place", () => {
  // Nothing shifts sideways when the first file lands: the badge was already standing there.
  const { container } = render(
    <Sidebar projects={[{ id: "p1", name: "Empty", chats: 0, files: 0 }]} activeProjectId="p1" />,
  );
  const badge = container.querySelector(".sidebar__row-badge");
  expect(badge.textContent).toBe("0");
  expect(badge.className).toContain("sidebar__row-badge--none");
});

test("a project with files shows the count plainly", () => {
  const { container } = render(<Sidebar projects={PROJECTS} activeProjectId="p1" />);
  const badge = container.querySelector(".sidebar__row-badge");
  expect(badge.textContent).toBe("3");
  expect(badge.className).not.toContain("--none");
});

test("projects are listed by name", () => {
  render(<Sidebar projects={PROJECTS} activeProjectId={null} />);
  expect(screen.getByText("Thesis research")).toBeTruthy();
  expect(screen.getByText("Product notes")).toBeTruthy();
});

test("clicking a project asks to open it", () => {
  const onOpenProject = vi.fn();
  render(<Sidebar projects={PROJECTS} activeProjectId={null} onOpenProject={onOpenProject} />);
  fireEvent.click(screen.getByText("Thesis research"));
  expect(onOpenProject).toHaveBeenCalledWith("p1");
});

test("the open project is the marked row", () => {
  render(<Sidebar projects={PROJECTS} activeProjectId="p2" />);
  const marked = screen.getByText("Product notes").closest("button");
  expect(marked.className).toContain("sidebar__row--active");
});

const CHATS = [
  { id: "c1", title: "Write the intro" },
  { id: "c2", title: "Missing values" },
];

test("the project's chats are listed and the open one is marked", () => {
  render(<Sidebar projects={PROJECTS} chats={CHATS} activeProjectId="p1" activeChatId="c2" />);
  expect(screen.getByText("Recent chats")).toBeTruthy();
  expect(screen.getByText("Write the intro")).toBeTruthy();
  expect(screen.getByText("Missing values").className).toContain("sidebar__chat--active");
});

test("clicking a chat asks to open it", () => {
  // They all live in the project on screen, so the row does not have to carry one.
  const onOpenChat = vi.fn();
  render(<Sidebar projects={PROJECTS} chats={CHATS} activeProjectId="p1" onOpenChat={onOpenChat} />);
  fireEvent.click(screen.getByText("Write the intro"));
  expect(onOpenChat).toHaveBeenCalledWith("c1");
});

test("at most eight chats are listed", () => {
  const many = Array.from({ length: 12 }, (_, i) => ({ id: `c${i}`, title: `Chat ${i}` }));
  render(<Sidebar projects={PROJECTS} chats={many} activeProjectId="p1" />);
  expect(screen.queryByText("Chat 7")).toBeTruthy();
  expect(screen.queryByText("Chat 8")).toBeNull();
});

test("the sidebar carries no search control", () => {
  // The design drops search on purpose: the project structure is the navigation.
  render(<Sidebar projects={PROJECTS} activeProjectId={null} />);
  expect(screen.queryByText("Search")).toBeNull();
  expect(screen.queryByText("⌘K")).toBeNull();
});

test("New chat asks rather than creating anything itself", () => {
  const onNewChat = vi.fn();
  render(<Sidebar projects={PROJECTS} activeProjectId="p1" onNewChat={onNewChat} />);
  fireEvent.click(screen.getByRole("button", { name: /New chat/ }));
  expect(onNewChat).toHaveBeenCalled();
});

// The row stops being a single button here: a ⋯ button cannot live inside another button. What the
// row looks like does not change; what it is made of does.
test("every project row carries a way into its menu", () => {
  render(<Sidebar projects={PROJECTS} activeProjectId="p1" />);
  expect(screen.getByRole("button", { name: "More for Thesis research" })).toBeTruthy();
  expect(screen.getByRole("button", { name: "More for Product notes" })).toBeTruthy();
});

test("opening the menu does not open the project", () => {
  const onOpenProject = vi.fn();
  const onOpenMenu = vi.fn();
  render(
    <Sidebar
      projects={PROJECTS}
      activeProjectId="p1"
      onOpenProject={onOpenProject}
      onOpenMenu={onOpenMenu}
    />,
  );
  fireEvent.click(screen.getByRole("button", { name: "More for Thesis research" }));
  expect(onOpenMenu).toHaveBeenCalledWith("p1");
  expect(onOpenProject).not.toHaveBeenCalled();
});

test("the menu offers the two things a project row can do", () => {
  render(<Sidebar projects={PROJECTS} activeProjectId="p1" menuFor="p1" />);
  expect(screen.getByRole("button", { name: "Rename" })).toBeTruthy();
  expect(screen.getByRole("button", { name: "Delete project" })).toBeTruthy();
});

test("only the row whose menu is open has one", () => {
  const { container } = render(<Sidebar projects={PROJECTS} activeProjectId="p1" menuFor="p2" />);
  const menus = container.querySelectorAll(".menu");
  expect(menus.length).toBe(1);
  expect(menus[0].closest(".sidebar__row").textContent).toContain("Product notes");
});

test("each choice names the project it belongs to", () => {
  const onRenameProject = vi.fn();
  const onDeleteProject = vi.fn();
  render(
    <Sidebar
      projects={PROJECTS}
      activeProjectId="p1"
      menuFor="p2"
      onRenameProject={onRenameProject}
      onDeleteProject={onDeleteProject}
    />,
  );
  fireEvent.click(screen.getByRole("button", { name: "Rename" }));
  expect(onRenameProject).toHaveBeenCalledWith("p2");
  fireEvent.click(screen.getByRole("button", { name: "Delete project" }));
  expect(onDeleteProject).toHaveBeenCalledWith("p2");
});

test("New chat is hidden rather than disabled when nothing is selected", () => {
  // A chat lives inside a project, so with none selected there is nothing for the control to do --
  // and a disabled button is a dead control the design refuses to draw.
  render(<Sidebar projects={[]} activeProjectId={null} />);
  expect(screen.queryByRole("button", { name: /New chat/ })).toBeNull();
});
