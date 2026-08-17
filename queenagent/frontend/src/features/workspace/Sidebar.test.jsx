import { fireEvent, render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import Sidebar from "./Sidebar.jsx";

const PROJECTS = [
  { id: "p1", name: "Thesis research", desc: "", hue: 45, chats: 3, files: 3 },
  { id: "p2", name: "Product notes", desc: "", hue: 150, chats: 2, files: 2 },
];

test("both section headings are there with no projects at all", () => {
  render(<Sidebar projects={[]} activeProjectId={null} />);
  // A hidden section would hide the fact that projects can be made at all.
  expect(screen.getByText("Projects")).toBeTruthy();
  expect(screen.getByText("Recent chats")).toBeTruthy();
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

test("recent chats are listed and the open one is marked", () => {
  const recentChats = [
    { id: "c1", title: "Write the intro", projectId: "p1" },
    { id: "c2", title: "Missing values", projectId: "p2" },
  ];
  render(<Sidebar projects={[]} recentChats={recentChats} activeChatId="c2" />);
  expect(screen.getByText("Write the intro")).toBeTruthy();
  expect(screen.getByText("Missing values").className).toContain("sidebar__chat--active");
});

test("clicking a recent chat carries its project along", () => {
  const onOpenChat = vi.fn();
  const recentChats = [{ id: "c1", title: "Write the intro", projectId: "p1" }];
  render(<Sidebar projects={[]} recentChats={recentChats} onOpenChat={onOpenChat} />);
  fireEvent.click(screen.getByText("Write the intro"));
  expect(onOpenChat).toHaveBeenCalledWith("p1", "c1");
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

test("with no projects New chat is hidden rather than disabled", () => {
  // A chat lives inside a project, so with none there is nothing for the control to do -- and a
  // disabled button is a dead control the design refuses to draw.
  render(<Sidebar projects={[]} activeProjectId={null} />);
  expect(screen.queryByRole("button", { name: /New chat/ })).toBeNull();
});
