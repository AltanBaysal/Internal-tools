import { fireEvent, render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import DeletedStrip from "./DeletedStrip.jsx";

test("nothing is drawn when nothing was deleted", () => {
  const { container } = render(<DeletedStrip />);
  expect(container.textContent).toBe("");
});

test("a deleted file offers to come back", () => {
  render(<DeletedStrip deleted={{ name: "plan.md", trashed: "plan.md" }} />);
  expect(screen.getByText("File deleted.")).toBeTruthy();
  expect(screen.getByRole("button", { name: "Undo" })).toBeTruthy();
});

test("Undo asks for it back", () => {
  const onUndo = vi.fn();
  render(<DeletedStrip deleted={{ name: "plan.md", trashed: "plan.md" }} onUndo={onUndo} />);
  fireEvent.click(screen.getByRole("button", { name: "Undo" }));
  expect(onUndo).toHaveBeenCalled();
});

test("an undo that failed repeats the server's words and keeps the offer", () => {
  render(
    <DeletedStrip deleted={{ name: "plan.md", trashed: "plan.md" }} error="failed with 409" />,
  );
  // The file is still in the trash, so the offer still stands.
  expect(screen.getByText("failed with 409")).toBeTruthy();
  expect(screen.getByRole("button", { name: "Undo" })).toBeTruthy();
});
