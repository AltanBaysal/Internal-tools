import { act, fireEvent, render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import ProjectRow from "./ProjectRow.jsx";

// Madde 360: an All projects row and its ⋯ (the design's items 135, 161, 167). Rename, Pin, Archive
// and Delete live here and nowhere inside a project. Madde 363 (the design's 190, 191): an archived
// row's ⋯ brings the project back; Madde 443 (the design's 218): the row opens it, as any row does.

const PROJECT = {
  id: "p2",
  name: "Night market",
  chats: 1,
  files: 1,
  pinned: false,
  lastActivity: new Date().toISOString(),
};
const PINNED = { ...PROJECT, pinned: true };
const SHELVED = { ...PROJECT, archived: true };

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
  // Whose ⋯ it is, so the screen can find the one that comes next once a row leaves (Madde 441).
  expect(more.dataset.project).toBe("p2");
  fireEvent.click(more);
  expect(onOpenMenu).toHaveBeenCalledWith("p2");
  expect(onOpen).not.toHaveBeenCalled();
});

test("the menu holds Rename, Pin, Archive and, under a line, a red Delete", () => {
  const { container } = render(<ProjectRow project={PROJECT} menuOpen />);
  expect(itemNames(container)).toEqual(["Rename", "Pin", "Archive", "Delete"]);
  const items = container.querySelectorAll(".menu__item");
  expect(items[3].className).toContain("menu__item--danger");
  // The design's own line: what cannot be undone stands apart from what can -- and Archive can.
  expect(items[3].previousElementSibling.className).toBe("menu__divider");
  expect(container.querySelectorAll(".menu__divider").length).toBe(1);
});

test("a pinned project offers Unpin instead", () => {
  const { container } = render(<ProjectRow project={PINNED} menuOpen />);
  expect(itemNames(container)).toEqual(["Rename", "Unpin", "Archive", "Delete"]);
});

test("Archive asks for the project to be archived", () => {
  const onArchive = vi.fn();
  render(<ProjectRow project={PROJECT} menuOpen onArchive={onArchive} />);
  fireEvent.click(screen.getByRole("button", { name: "Archive" }));
  expect(onArchive).toHaveBeenCalledWith("p2", true);
});

test("an archived row opens its project, as any row does", () => {
  // Madde 443 (the design's 218): the only difference is the list it stands in -- and its ⋯.
  const onOpen = vi.fn();
  const { container } = render(<ProjectRow project={SHELVED} onOpen={onOpen} />);
  const open = container.querySelector(".all-projects__row-open");
  expect(open.tagName).toBe("BUTTON");
  expect(open.title).toBe("Night market");
  expect(open.querySelector(".all-projects__row-name").textContent).toBe("Night market");
  expect(open.querySelector(".all-projects__row-meta").textContent).toBe("1 chat · 1 file");
  expect(open.querySelector(".all-projects__row-when")).toBeTruthy();
  fireEvent.click(open);
  expect(onOpen).toHaveBeenCalledWith("p2");
  expect(screen.getByRole("button", { name: "Actions for Night market" })).toBeTruthy();
});

test("an archived row's menu holds Rename, Unarchive and, under a line, a red Delete", () => {
  const { container } = render(<ProjectRow project={SHELVED} menuOpen />);
  expect(itemNames(container)).toEqual(["Rename", "Unarchive", "Delete"]);
  const items = container.querySelectorAll(".menu__item");
  expect(items[2].className).toContain("menu__item--danger");
  expect(items[2].previousElementSibling.className).toBe("menu__divider");
  expect(container.querySelectorAll(".menu__divider").length).toBe(1);
});

test("Unarchive asks for the project to come back", () => {
  const onArchive = vi.fn();
  render(<ProjectRow project={SHELVED} menuOpen onArchive={onArchive} />);
  fireEvent.click(screen.getByRole("button", { name: "Unarchive" }));
  expect(onArchive).toHaveBeenCalledWith("p2", false);
});

test("an archived row is renamed in its own place too", () => {
  const onRename = vi.fn();
  render(<ProjectRow project={SHELVED} menuOpen onCloseMenu={() => {}} onRename={onRename} />);
  fireEvent.click(screen.getByRole("button", { name: "Rename" }));
  const field = screen.getByRole("textbox", { name: "Project name" });
  fireEvent.change(field, { target: { value: "Harbour" } });
  fireEvent.keyDown(field, { key: "Enter" });
  expect(onRename).toHaveBeenCalledWith("p2", "Harbour");
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

test("Enter saves what was typed, once, and closes the field once it has landed", async () => {
  const onRename = vi.fn().mockResolvedValue(PROJECT);
  const field = renaming({ onRename });
  fireEvent.change(field, { target: { value: "  Harbour  " } });
  await act(async () => {
    fireEvent.keyDown(field, { key: "Enter" });
    // A second press while the first is on its way is not a second rename.
    fireEvent.keyDown(field, { key: "Enter" });
  });
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

test("pressing anywhere else saves, as the design's settleRename does", async () => {
  // A rename the user walked away from is kept, never silently dropped.
  const onRename = vi.fn().mockResolvedValue(PROJECT);
  const field = renaming({ onRename });
  fireEvent.change(field, { target: { value: "Harbour" } });
  await act(async () => {
    fireEvent.blur(field);
  });
  expect(onRename).toHaveBeenCalledWith("p2", "Harbour");
  expect(screen.queryByRole("textbox", { name: "Project name" })).toBeNull();
});

// Madde 387: the name is the user's work, so the field waits for the server's answer and a refusal
// leaves it where it was typed -- as the naming screen keeps the name it could not create.

test("the field holds the name while it is on its way", () => {
  const field = renaming({ onRename: vi.fn(() => new Promise(() => {})) });
  fireEvent.change(field, { target: { value: "Harbour" } });
  fireEvent.keyDown(field, { key: "Enter" });
  expect(screen.getByRole("textbox", { name: "Project name" }).value).toBe("Harbour");
});

test("a refused name stays in the field, ready to send again", async () => {
  const onRename = vi.fn().mockResolvedValueOnce(null).mockResolvedValueOnce(PROJECT);
  const field = renaming({ onRename });
  fireEvent.change(field, { target: { value: "Harbour" } });
  await act(async () => {
    fireEvent.keyDown(field, { key: "Enter" });
  });
  const kept = screen.getByRole("textbox", { name: "Project name" });
  expect(kept.value).toBe("Harbour");
  expect(document.activeElement).toBe(kept);
  await act(async () => {
    fireEvent.keyDown(kept, { key: "Enter" });
  });
  expect(onRename).toHaveBeenCalledTimes(2);
  expect(onRename).toHaveBeenLastCalledWith("p2", "Harbour");
  expect(screen.queryByRole("textbox", { name: "Project name" })).toBeNull();
});

test("Escape after a refusal gives the name up", async () => {
  const onRename = vi.fn().mockResolvedValue(null);
  const field = renaming({ onRename });
  fireEvent.change(field, { target: { value: "Harbour" } });
  await act(async () => {
    fireEvent.keyDown(field, { key: "Enter" });
  });
  fireEvent.keyDown(screen.getByRole("textbox", { name: "Project name" }), { key: "Escape" });
  expect(onRename).toHaveBeenCalledTimes(1);
  expect(screen.queryByRole("textbox", { name: "Project name" })).toBeNull();
  expect(screen.getByText("Night market")).toBeTruthy();
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
