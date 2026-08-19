import { fireEvent, render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import FileRow from "./FileRow.jsx";

const FILE = {
  name: "outline.md",
  ext: "md",
  modifiedAt: new Date(Date.now() - 2 * 3600_000).toISOString(),
};

// One row serves both screens. What it can do is decided by what it is given, so the two lists
// cannot drift into two different-looking rows.
test("the row says the name, the chip and whose file it is", () => {
  render(<FileRow file={FILE} />);
  expect(screen.getByText("outline.md")).toBeTruthy();
  expect(screen.getByText("md")).toBeTruthy();
  expect(screen.getByText("project file · 2h ago")).toBeTruthy();
});

test("clicking it opens the file", () => {
  const onOpen = vi.fn();
  render(<FileRow file={FILE} onOpen={onOpen} />);
  fireEvent.click(screen.getByText("outline.md"));
  expect(onOpen).toHaveBeenCalledWith("outline.md");
});

test("without a way to delete there is no × to press", () => {
  render(<FileRow file={FILE} onOpen={vi.fn()} />);
  expect(screen.queryByRole("button", { name: "Delete outline.md" })).toBeNull();
});

test("with one, the × deletes without opening", () => {
  const onOpen = vi.fn();
  const onDelete = vi.fn();
  render(<FileRow file={FILE} onOpen={onOpen} onDelete={onDelete} />);
  fireEvent.click(screen.getByRole("button", { name: "Delete outline.md" }));
  expect(onDelete).toHaveBeenCalledWith("outline.md");
  expect(onOpen).not.toHaveBeenCalled();
});

// A row that only listens for a click cannot be reached from the keyboard at all: no tab stop, no
// Enter, no focus ring. Opening a file was impossible without a mouse.
test("the row is a real button", () => {
  render(<FileRow file={FILE} onOpen={vi.fn()} />);
  const opener = screen.getByRole("button", { name: /outline\.md/ });
  expect(opener.tagName).toBe("BUTTON");
});

test("Enter on the row opens the file", () => {
  const onOpen = vi.fn();
  render(<FileRow file={FILE} onOpen={onOpen} />);
  const opener = screen.getByRole("button", { name: /outline\.md/ });
  opener.focus();
  expect(document.activeElement).toBe(opener);
  // A button answers Enter itself; the browser turns it into a click.
  fireEvent.click(opener);
  expect(onOpen).toHaveBeenCalledWith("outline.md");
});

test("the × is a sibling of the opener rather than sitting inside it", () => {
  // A button inside a button is not valid HTML, and the row had to become a button.
  const { container } = render(<FileRow file={FILE} onOpen={vi.fn()} onDelete={vi.fn()} />);
  const remove = screen.getByRole("button", { name: "Delete outline.md" });
  expect(remove.closest("button")).toBe(remove);
  expect(container.querySelector(".file-row__open").contains(remove)).toBe(false);
});

test("the × says what it does to a pointer as well as to a screen reader", () => {
  render(<FileRow file={FILE} onOpen={vi.fn()} onDelete={vi.fn()} />);
  expect(screen.getByRole("button", { name: "Delete outline.md" }).title).toBe("Delete outline.md");
});

// Which row is open is the caller's answer, not the row's: the row is drawn in two lists and
// neither of them owns the reader.
test("a row can be marked as the one being read", () => {
  const { container } = render(<FileRow file={FILE} selected />);
  expect(container.querySelector(".file-row").className).toContain("file-row--selected");
});

test("and is not marked when it is not", () => {
  const { container } = render(<FileRow file={FILE} />);
  expect(container.querySelector(".file-row").className).not.toContain("selected");
});
