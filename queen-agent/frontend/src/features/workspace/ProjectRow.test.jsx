import { fireEvent, render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import ProjectRow from "./ProjectRow.jsx";

// Madde 360: an All projects row and its ⋯ (the design's items 135, 161, 167). Rename, Pin and
// Delete live here and nowhere inside a project; Archive is Madde 363's.

const PROJECT = {
  id: "p2",
  name: "Night market",
  chats: 1,
  files: 1,
  pinned: false,
  lastActivity: new Date().toISOString(),
};
const PINNED = { ...PROJECT, pinned: true };

const itemNames = (container) =>
  [...container.querySelectorAll(".menu__item")].map((item) => item.textContent);

// The menu is App's to close, so here it stays drawn after a choice; what matters is the field.
function renaming(props = {}) {
  render(<ProjectRow project={PROJECT} menuOpen onCloseMenu={() => {}} {...props} />);
  fireEvent.click(screen.getByRole("button", { name: "Rename" }));
  return screen.getByRole("textbox", { name: "Project name" });
}

test("the row carries a ⋯ that asks for its menu and opens nothing", () => {
  const onOpen = vi.fn();
  const onOpenMenu = vi.fn();
  render(<ProjectRow project={PROJECT} onOpen={onOpen} onOpenMenu={onOpenMenu} />);
  const more = screen.getByRole("button", { name: "Actions for Night market" });
  expect(more.className).toBe("all-projects__row-more");
  expect(more.textContent).toBe("⋯");
  fireEvent.click(more);
  expect(onOpenMenu).toHaveBeenCalledWith("p2");
  expect(onOpen).not.toHaveBeenCalled();
});

test("the menu holds Rename, Pin and, under a line, a red Delete", () => {
  const { container } = render(<ProjectRow project={PROJECT} menuOpen />);
  expect(itemNames(container)).toEqual(["Rename", "Pin", "Delete"]);
  const items = container.querySelectorAll(".menu__item");
  expect(items[2].className).toContain("menu__item--danger");
  // The design's own line: what cannot be undone stands apart from what can.
  expect(items[2].previousElementSibling.className).toBe("menu__divider");
  expect(container.querySelectorAll(".menu__divider").length).toBe(1);
  expect(screen.queryByRole("button", { name: "Archive" })).toBeNull();
});

test("a pinned project offers Unpin instead", () => {
  const { container } = render(<ProjectRow project={PINNED} menuOpen />);
  expect(itemNames(container)).toEqual(["Rename", "Unpin", "Delete"]);
});

test("Pin asks for the mark", () => {
  const onPin = vi.fn();
  render(<ProjectRow project={PROJECT} menuOpen onPin={onPin} />);
  fireEvent.click(screen.getByRole("button", { name: "Pin" }));
  expect(onPin).toHaveBeenCalledWith("p2", true);
});

test("Unpin asks for the mark to go", () => {
  const onPin = vi.fn();
  render(<ProjectRow project={PINNED} menuOpen onPin={onPin} />);
  fireEvent.click(screen.getByRole("button", { name: "Unpin" }));
  expect(onPin).toHaveBeenCalledWith("p2", false);
});

test("Delete asks for the project's deletion", () => {
  const onDelete = vi.fn();
  render(<ProjectRow project={PROJECT} menuOpen onDelete={onDelete} />);
  fireEvent.click(screen.getByRole("button", { name: "Delete" }));
  expect(onDelete).toHaveBeenCalledWith("p2");
});

test("Rename turns the name into a field, in the row's own place", () => {
  const field = renaming();
  expect(field.className).toBe("all-projects__rename");
  expect(field.value).toBe("Night market");
  expect(document.activeElement).toBe(field);
  expect(document.querySelector(".all-projects__row-open")).toBeNull();
  expect(screen.getByRole("button", { name: "Actions for Night market" })).toBeTruthy();
});

test("Enter saves what was typed, once, and closes the field", () => {
  const onRename = vi.fn();
  const field = renaming({ onRename });
  fireEvent.change(field, { target: { value: "  Harbour  " } });
  fireEvent.keyDown(field, { key: "Enter" });
  expect(onRename).toHaveBeenCalledTimes(1);
  expect(onRename).toHaveBeenCalledWith("p2", "Harbour");
  expect(screen.queryByRole("textbox", { name: "Project name" })).toBeNull();
  expect(document.querySelector(".all-projects__row-open")).toBeTruthy();
});

test("Escape gives up: nothing is saved", () => {
  const onRename = vi.fn();
  const field = renaming({ onRename });
  fireEvent.change(field, { target: { value: "Harbour" } });
  fireEvent.keyDown(field, { key: "Escape" });
  expect(onRename).not.toHaveBeenCalled();
  expect(screen.queryByRole("textbox", { name: "Project name" })).toBeNull();
  expect(screen.getByText("Night market")).toBeTruthy();
});

test("pressing anywhere else saves, as the design's settleRename does", () => {
  // A rename the user walked away from is kept, never silently dropped.
  const onRename = vi.fn();
  const field = renaming({ onRename });
  fireEvent.change(field, { target: { value: "Harbour" } });
  fireEvent.blur(field);
  expect(onRename).toHaveBeenCalledWith("p2", "Harbour");
  expect(screen.queryByRole("textbox", { name: "Project name" })).toBeNull();
});

test("an empty name saves nothing", () => {
  const onRename = vi.fn();
  const field = renaming({ onRename });
  fireEvent.change(field, { target: { value: "   " } });
  fireEvent.keyDown(field, { key: "Enter" });
  expect(onRename).not.toHaveBeenCalled();
  expect(screen.queryByRole("textbox", { name: "Project name" })).toBeNull();
  expect(screen.getByText("Night market")).toBeTruthy();
});
