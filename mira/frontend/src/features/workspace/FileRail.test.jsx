import { fireEvent, render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import FileRail from "./FileRail.jsx";

const NOW = Date.now();
const NOW_ISO = new Date(NOW).toISOString();
const FILES = [
  { name: "outline.md", ext: "md", modifiedAt: new Date(NOW - 2 * 3600_000).toISOString() },
  { name: "sources.txt", ext: "txt", modifiedAt: NOW_ISO },
];

test("the rail is headed Project files", () => {
  render(<FileRail files={FILES} />);
  expect(screen.getByText("Project files")).toBeTruthy();
});

test("every file gets a row, chip and all", () => {
  render(<FileRail files={FILES} />);
  expect(screen.getByText("outline.md")).toBeTruthy();
  expect(screen.getByText("sources.txt")).toBeTruthy();
  expect(screen.getByText("txt")).toBeTruthy();
});

test("a row says how long ago the file was written", () => {
  render(<FileRail files={FILES} />);
  expect(screen.getByText("2h ago")).toBeTruthy();
});

test("an empty rail teaches instead of sitting blank", () => {
  render(<FileRail files={[]} />);
  expect(screen.getByText(/No files yet/)).toBeTruthy();
});

test("a rail with nothing to draw yet is still a rail", () => {
  // The list arrives after the screen does, so the first render has no prop at all.
  render(<FileRail />);
  expect(screen.getByTestId("file-rail")).toBeTruthy();
});

test("clicking a row opens that file", () => {
  const open = vi.fn();
  render(<FileRail files={FILES} reading={{ open }} />);
  fireEvent.click(screen.getByText("outline.md"));
  expect(open).toHaveBeenCalledWith("outline.md");
});

test("the × deletes the row without opening it", () => {
  const open = vi.fn();
  const remove = vi.fn();
  render(<FileRail files={FILES} reading={{ open }} deleting={{ remove }} />);
  fireEvent.click(screen.getByRole("button", { name: "Delete outline.md" }));
  expect(remove).toHaveBeenCalledWith("outline.md");
  // The × sits inside the row, so it has to stop the click from reaching it.
  expect(open).not.toHaveBeenCalled();
});

test("the strip sits above the list once something was deleted", () => {
  const deleting = { deleted: { name: "gone.md", trashed: "gone.md" }, remove: vi.fn() };
  render(<FileRail files={FILES} deleting={deleting} />);
  expect(screen.getByText("File deleted.")).toBeTruthy();
  expect(screen.getByText("outline.md")).toBeTruthy();
});

test("an open file takes the rail over and widens it", () => {
  const file = { name: "outline.md", ext: "md", size: 12, text: "read me", modifiedAt: NOW_ISO };
  render(<FileRail files={FILES} reading={{ name: "outline.md", file }} />);
  expect(screen.getByText("read me")).toBeTruthy();
  // The list is behind the panel, not beside it: the rail is 320px wide until it is 560.
  expect(screen.queryByText("sources.txt")).toBeNull();
  expect(screen.getByTestId("file-rail").className).toContain("rail--open");
});
