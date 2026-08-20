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

test("a row offers a way to delete when the rail is given one", () => {
  // A file born by accident mid-chat had to be chased to the project screen to be got rid of.
  const remove = vi.fn();
  render(<FileRail files={FILES} deleting={{ remove }} />);
  fireEvent.click(screen.getByRole("button", { name: "Delete outline.md" }));
  expect(remove).toHaveBeenCalledWith("outline.md");
});

test("without a way to delete the rail rows carry no ×", () => {
  render(<FileRail files={FILES} />);
  expect(screen.queryByRole("button", { name: /^Delete / })).toBeNull();
});

test("the row of the file being read carries no ×", () => {
  // Deleting what is open under the reader leaves the user staring at nothing. The project screen
  // is spared this by its layout; here the rule has to be said.
  const remove = vi.fn();
  render(
    <FileRail
      files={FILES}
      deleting={{ remove }}
      reading={{ name: "outline.md", file: { text: "body" } }}
    />,
  );
  expect(screen.queryByRole("button", { name: "Delete outline.md" })).toBeNull();
  expect(screen.getByRole("button", { name: "Delete sources.txt" })).toBeTruthy();
});

// Madde 50: the rail is dragged by its left edge, and it stays on the right at every width. What it
// reports is the width that was asked for -- whether that is a width at all, or is narrow enough to
// mean closing, is App's answer (railWidth.js), because closing is App's state.

test("the rail is drawn at the width it is handed", () => {
  render(<FileRail files={FILES} width={420} />);
  expect(screen.getByTestId("file-rail").style.width).toBe("420px");
});

test("a rail given no width leaves the stylesheet's own", () => {
  // Before the first drag there is nothing to say, and saying 320 here would copy a number that
  // already lives in the stylesheet.
  render(<FileRail files={FILES} />);
  expect(screen.getByTestId("file-rail").style.width).toBe("");
});

test("the rail carries a grip to pull its edge with", () => {
  render(<FileRail files={FILES} width={320} onResize={vi.fn()} />);
  expect(screen.getByRole("separator")).toBeTruthy();
});

test("pulling the grip leftwards asks for a wider rail", () => {
  const onResize = vi.fn();
  render(<FileRail files={FILES} width={320} onResize={onResize} />);
  fireEvent.mouseDown(screen.getByRole("separator"), { clientX: 500 });
  fireEvent.mouseMove(window, { clientX: 420 });
  expect(onResize).toHaveBeenCalledWith(400);
});

test("pulling it rightwards asks for a narrower one, and letting go ends the drag", () => {
  const onResize = vi.fn();
  render(<FileRail files={FILES} width={320} onResize={onResize} />);
  fireEvent.mouseDown(screen.getByRole("separator"), { clientX: 500 });
  fireEvent.mouseMove(window, { clientX: 560 });
  expect(onResize).toHaveBeenCalledWith(260);
  fireEvent.mouseUp(window);
  onResize.mockClear();
  // The mouse moving across the window afterwards is not a drag: the pointer was let go.
  fireEvent.mouseMove(window, { clientX: 200 });
  expect(onResize).not.toHaveBeenCalled();
});

test("while its edge is being pulled the rail says so", () => {
  // The width follows the pointer frame by frame, and the rail's eased transition -- written for
  // folding -- would run 220ms behind it. The stylesheet turns the easing off on this class.
  render(<FileRail files={FILES} width={320} onResize={vi.fn()} />);
  const rail = screen.getByTestId("file-rail");
  expect(rail.className).not.toContain("rail--dragging");
  fireEvent.mouseDown(screen.getByRole("separator"), { clientX: 500 });
  expect(rail.className).toContain("rail--dragging");
  fireEvent.mouseUp(window);
  expect(rail.className).not.toContain("rail--dragging");
});

test("a folded rail has no grip", () => {
  // 46px of strip is there to be pressed, not pulled.
  render(<FileRail files={FILES} collapsed width={320} onResize={vi.fn()} />);
  expect(screen.queryByRole("separator")).toBeNull();
});

test("a rail showing a document has no grip", () => {
  // While a file is open the width belongs to the document. The dragged width comes back when the
  // reader closes.
  render(
    <FileRail
      files={FILES}
      width={320}
      onResize={vi.fn()}
      reading={{ name: "outline.md", file: { text: "body" } }}
    />,
  );
  expect(screen.queryByRole("separator")).toBeNull();
});

test("a rail folded because the window is narrow has a label, not a control", () => {
  // There is nowhere to open into, so a button that opens would be a lie. The same sentence the rail
  // already says while it is showing a document.
  render(<FileRail files={FILES} collapsed foldedByWidth />);
  expect(screen.getByText("Project files")).toBeTruthy();
  expect(screen.queryByRole("button", { name: /Project files/ })).toBeNull();
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

test("a rail row deletes while a file is open beside it", () => {
  // The list stays standing next to the reader, so the rows keep working -- all but the one being
  // read, which has its own test above.
  const remove = vi.fn();
  render(
    <FileRail
      files={FILES}
      reading={{ name: "outline.md", file: { text: "body" }, open: vi.fn() }}
      deleting={{ remove }}
    />,
  );
  fireEvent.click(screen.getByRole("button", { name: "Delete sources.txt" }));
  expect(remove).toHaveBeenCalledWith("sources.txt");
});

test("a file row offers no rename either", () => {
  render(<FileRail files={FILES} reading={{ open: vi.fn() }} />);
  expect(screen.queryByRole("button", { name: "Rename outline.md" })).toBeNull();
});

test("a delete that goes wrong is said in the rail, not swallowed", () => {
  // It could not report one while it could not delete. Now that it can, a failure with nowhere to
  // be said would be a file the user believes is gone.
  render(<FileRail files={FILES} deleting={{ remove: vi.fn(), error: "HTTP 409" }} />);
  expect(screen.getByText("HTTP 409")).toBeTruthy();
});

test("a rail that could not read the list says so instead of teaching", () => {
  render(<FileRail files={[]} error="the store is unreachable" />);
  // Answering "there are none" to a question that got no answer would be the screen inventing one.
  expect(screen.getByText("the store is unreachable")).toBeTruthy();
  expect(screen.queryByText(/No files yet/)).toBeNull();
});

test("a rail still loading says neither", () => {
  render(<FileRail files={[]} loading />);
  expect(screen.queryByText(/No files yet/)).toBeNull();
  expect(screen.getByTestId("skeleton")).toBeTruthy();
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

test("the rail's reader is come back from rather than closed", () => {
  // The panel here is the rail widened, so it keeps the arrow. The project screen's panel is a
  // surface of its own and closes with an ×.
  render(<FileRail files={FILES} reading={{ name: "outline.md", file: OPEN_FILE }} />);
  expect(screen.getByRole("button", { name: "←" })).toBeTruthy();
  expect(screen.queryByRole("button", { name: "×" })).toBeNull();
});

test("the row of the file being read is the marked one", () => {
  // Madde 21 wrote this rule with nowhere to show it. Here is where it shows.
  // Asked for inside the list: the reader's header carries the same name.
  const { container } = render(
    <FileRail files={FILES} reading={{ name: "outline.md", file: OPEN_FILE }} />,
  );
  const rows = [...container.querySelectorAll(".file-row")];
  expect(rows[0].className).toContain("file-row--selected");
  expect(rows[1].className).not.toContain("selected");
});

test("another file can be reached without closing the one open", () => {
  const open = vi.fn();
  render(<FileRail files={FILES} reading={{ name: "outline.md", file: OPEN_FILE, open }} />);
  fireEvent.click(screen.getByText("sources.txt"));
  expect(open).toHaveBeenCalledWith("sources.txt");
});

// Madde 63: what is being read gets the whole rail. The list is one press of ← away, and 200 of the
// rail's 560 pixels were going to something already reachable.

test("an open file takes the rail over", () => {
  render(<FileRail files={FILES} reading={{ name: "outline.md", file: OPEN_FILE }} />);
  // The reader is asked for first: a rail that drew nothing at all would pass the absences below
  // while being far more broken than the thing they are guarding against.
  expect(screen.getByText("read me")).toBeTruthy();
  expect(screen.queryByText("sources.txt")).toBeNull();
});

test("while reading, the rail says nothing about a list", () => {
  render(<FileRail files={FILES} reading={{ name: "outline.md", file: OPEN_FILE }} />);
  expect(screen.getByText("read me")).toBeTruthy();
  // Neither as a heading nor as a label. There is no list for the words to be about.
  expect(screen.queryByText("Project files")).toBeNull();
});

test("while reading, there is nothing to delete", () => {
  // Not a rule of its own -- a consequence. Deleting happened from rows, and there are no rows.
  render(
    <FileRail
      files={FILES}
      reading={{ name: "outline.md", file: OPEN_FILE }}
      deleting={{ remove: vi.fn() }}
    />,
  );
  expect(screen.getByText("read me")).toBeTruthy();
  expect(screen.queryByRole("button", { name: /^Delete / })).toBeNull();
});

test("while reading, the list keeps its label and loses its control", () => {
  // Madde 20's rule stands: a rail showing a document has nothing to fold away.
  render(<FileRail files={FILES} reading={{ name: "outline.md", file: OPEN_FILE }} />);
  expect(screen.getByText("Project files")).toBeTruthy();
  expect(screen.queryByRole("button", { name: /Project files/ })).toBeNull();
});
