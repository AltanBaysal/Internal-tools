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

test("New chat goes home rather than creating anything", () => {
  const onNewChat = vi.fn();
  render(<Sidebar projects={[]} activeProjectId={null} onNewChat={onNewChat} />);
  fireEvent.click(screen.getByRole("button", { name: /New chat/ }));
  expect(onNewChat).toHaveBeenCalled();
});
