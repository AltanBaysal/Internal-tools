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
  // The × sits inside the row, so it has to stop the click from reaching it.
  expect(onOpen).not.toHaveBeenCalled();
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
