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

// The heading stops being a heading: it is the control that folds the rail away, and it says how
// much is in there so the count is readable folded as well as open.
test("the heading is the control, and it counts", () => {
  render(<FileRail files={FILES} />);
  const head = screen.getByRole("button", { name: /Project files/ });
  expect(head.textContent).toContain("2");
  expect(head.getAttribute("aria-expanded")).toBe("true");
});

test("pressing it asks to fold rather than folding by itself", () => {
  // The state lives in App: it has to survive moving between chats, and the rail does not.
  const onToggle = vi.fn();
  render(<FileRail files={FILES} onToggle={onToggle} />);
  fireEvent.click(screen.getByRole("button", { name: /Project files/ }));
  expect(onToggle).toHaveBeenCalled();
});

test("folded, the list goes and the label and the count stay", () => {
  render(<FileRail files={FILES} collapsed />);
  expect(screen.queryByText("outline.md")).toBeNull();
  const head = screen.getByRole("button", { name: /Project files/ });
  expect(head.textContent).toContain("2");
  expect(head.getAttribute("aria-expanded")).toBe("false");
});

test("folded, one click on the strip is what opens it", () => {
  const onToggle = vi.fn();
  render(<FileRail files={FILES} collapsed onToggle={onToggle} />);
  fireEvent.click(screen.getByRole("button", { name: /Project files/ }));
  expect(onToggle).toHaveBeenCalled();
});

test("with a file open there is nothing to fold", () => {
  // The rail is drawing a document, not a list, so the control has no subject.
  const file = { name: "outline.md", ext: "md", size: 12, text: "read me", modifiedAt: NOW_ISO };
  render(<FileRail files={FILES} reading={{ name: "outline.md", file }} />);
  expect(screen.queryByRole("button", { name: /Project files/ })).toBeNull();
});

test("every file gets a row, chip and all", () => {
  render(<FileRail files={FILES} />);
  expect(screen.getByText("outline.md")).toBeTruthy();
  expect(screen.getByText("sources.txt")).toBeTruthy();
  expect(screen.getByText("txt")).toBeTruthy();
});

test("a row says whose file it is and how long ago it was written", () => {
  // One line under the name, in the row itself: the design took the advice line away and put what
  // it said here instead.
  render(<FileRail files={FILES} />);
  expect(screen.getByText("project file · 2h ago")).toBeTruthy();
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

test("a file row offers no rename", () => {
  // Renaming lives on the project alone; the row opens and deletes, nothing else.
  render(<FileRail files={FILES} reading={{ open: vi.fn() }} />);
  expect(screen.queryByRole("button", { name: "Rename outline.md" })).toBeNull();
});

test("a refused delete says so above the list, and offers nothing back", () => {
  // The strip is gone with the undo it existed for; its other job is one line.
  render(<FileRail files={FILES} deleting={{ error: "HTTP 409", remove: vi.fn() }} />);
  expect(screen.getByText("HTTP 409")).toBeTruthy();
  expect(screen.queryByText("Undo")).toBeNull();
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
