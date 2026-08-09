import { fireEvent, render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import FileStrip from "./FileStrip.jsx";

const DELETED = { name: "plan.md", trashed: "plan.md" };

test("nothing is drawn when there is nothing to say", () => {
  const { container } = render(<FileStrip />);
  expect(container.textContent).toBe("");
});

test("a deleted file offers to come back", () => {
  render(<FileStrip deleted={DELETED} />);
  expect(screen.getByText("File deleted.")).toBeTruthy();
  expect(screen.getByRole("button", { name: "Undo" })).toBeTruthy();
});

test("Undo asks for it back", () => {
  const onUndo = vi.fn();
  render(<FileStrip deleted={DELETED} onUndo={onUndo} />);
  fireEvent.click(screen.getByRole("button", { name: "Undo" }));
  expect(onUndo).toHaveBeenCalled();
});

test("an undo that failed repeats the server's words and keeps the offer", () => {
  render(<FileStrip deleted={DELETED} error="failed with 409" />);
  // The file is still in the trash, so the offer still stands.
  expect(screen.getByText("failed with 409")).toBeTruthy();
  expect(screen.getByRole("button", { name: "Undo" })).toBeTruthy();
});

test("a failure with nothing deleted is still said out loud", () => {
  render(<FileStrip error="PATCH failed with 500" />);
  expect(screen.getByText("PATCH failed with 500")).toBeTruthy();
  // Nothing was deleted, so there is nothing to undo.
  expect(screen.queryByRole("button", { name: "Undo" })).toBeNull();
});
