import { fireEvent, render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import Sidebar from "./Sidebar.jsx";

const PROJECTS = [
  { id: "p1", name: "Thesis research", chats: 3, files: 3 },
  { id: "p2", name: "Product notes", chats: 2, files: 2 },
];

test("with no project selected only the wordmark and the projects remain", () => {
  // Chats belong to a project, so with none selected neither control has anywhere to point.
  render(<Sidebar projects={PROJECTS} activeProjectId={null} />);
  expect(screen.getByText("Projects")).toBeTruthy();
  expect(screen.queryByText("Recent chats")).toBeNull();
  expect(screen.queryByRole("button", { name: /New chat/ })).toBeNull();
});

test("there is no logo mark beside the wordmark", () => {
  const { container } = render(<Sidebar projects={PROJECTS} activeProjectId="p1" />);
  expect(screen.getByText("QueenAgent")).toBeTruthy();
  expect(container.querySelector(".sidebar__mark")).toBeNull();
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

test("New chat is hidden rather than disabled when nothing is selected", () => {
  // A chat lives inside a project, so with none selected there is nothing for the control to do --
  // and a disabled button is a dead control the design refuses to draw.
  render(<Sidebar projects={[]} activeProjectId={null} />);
  expect(screen.queryByRole("button", { name: /New chat/ })).toBeNull();
});
