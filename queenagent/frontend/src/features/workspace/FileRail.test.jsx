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

// With a file open there is nothing to fold -- the rail is showing a document. That is asserted
// below, where the two-column state is set out.

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

// The rail's row does one thing. Deleting stays on the project screen, where the list is the
// subject of the screen rather than something standing beside a conversation.
test("a rail row carries no way to delete, even when one is handed to it", () => {
  render(<FileRail files={FILES} reading={{ open: vi.fn() }} deleting={{ remove: vi.fn() }} />);
  expect(screen.queryByRole("button", { name: "Delete outline.md" })).toBeNull();
});

test("a file row offers no rename either", () => {
  render(<FileRail files={FILES} reading={{ open: vi.fn() }} />);
  expect(screen.queryByRole("button", { name: "Rename outline.md" })).toBeNull();
});

test("a list that cannot delete cannot report a delete going wrong", () => {
  // The line Madde 19 left in place of the strip belongs to the screen that still deletes.
  const { container } = render(<FileRail files={FILES} deleting={{ error: "HTTP 409" }} />);
  expect(container.querySelector(".file-list__error")).toBeNull();
});

const OPEN_FILE = { name: "outline.md", ext: "md", size: 12, text: "read me", modifiedAt: NOW_ISO };

test("an open file widens the rail rather than taking it over", () => {
  render(<FileRail files={FILES} reading={{ name: "outline.md", file: OPEN_FILE }} />);
  expect(screen.getByText("read me")).toBeTruthy();
  // The list stays beside the reader: closing the panel used to be the only way to reach another
  // file.
  expect(screen.getByText("sources.txt")).toBeTruthy();
  expect(screen.getByTestId("file-rail").className).toContain("rail--open");
});

test("the row of the file being read is the marked one", () => {
  // Madde 21 wrote this rule with nowhere to show it. Here is where it shows.
  render(<FileRail files={FILES} reading={{ name: "outline.md", file: OPEN_FILE }} />);
  expect(screen.getByText("outline.md").closest(".file-row").className).toContain(
    "file-row--selected",
  );
  expect(screen.getByText("sources.txt").closest(".file-row").className).not.toContain("selected");
});

test("another file can be reached without closing the one open", () => {
  const open = vi.fn();
  render(<FileRail files={FILES} reading={{ name: "outline.md", file: OPEN_FILE, open }} />);
  fireEvent.click(screen.getByText("sources.txt"));
  expect(open).toHaveBeenCalledWith("sources.txt");
});

test("while reading, the list keeps its label and loses its control", () => {
  // Madde 20's rule stands: a rail showing a document has nothing to fold away.
  render(<FileRail files={FILES} reading={{ name: "outline.md", file: OPEN_FILE }} />);
  expect(screen.getByText("Project files")).toBeTruthy();
  expect(screen.queryByRole("button", { name: /Project files/ })).toBeNull();
});
