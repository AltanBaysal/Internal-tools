import { fireEvent, render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import MessageFoot from "./MessageFoot.jsx";

// Madde 344: the line under a bubble, and the version arrows that only it draws, in one file.

const BESIDE = { index: 0, of: 2, versions: ["", "l2"] };

test("a lone message with no pencil draws no line", () => {
  const { container } = render(<MessageFoot standing={{ index: 0, of: 1, versions: [""] }} />);
  expect(container.firstChild).toBeNull();
});

test("the pencil asks for the edit", () => {
  const onEdit = vi.fn();
  render(<MessageFoot onEdit={onEdit} />);
  fireEvent.click(screen.getByRole("button", { name: "Edit message" }));
  expect(onEdit).toHaveBeenCalled();
});

test("the arrows hand over the version beside this one", () => {
  const onVersion = vi.fn();
  render(<MessageFoot standing={BESIDE} onVersion={onVersion} />);
  expect(screen.getByText("1/2")).toBeTruthy();
  expect(screen.getByRole("button", { name: "Previous version" }).disabled).toBe(true);
  fireEvent.click(screen.getByRole("button", { name: "Next version" }));
  expect(onVersion).toHaveBeenCalledWith("l2");
});

test("it draws no row of its own: its parts stand in the stamp's", () => {
  // Madde 348: the time, the arrows and the pencil share one row, and the row is the stamp's.
  const { container } = render(<MessageFoot standing={BESIDE} onEdit={vi.fn()} />);
  expect([...container.children].map((part) => part.className)).toEqual(["versions", "msg__edit"]);
});
