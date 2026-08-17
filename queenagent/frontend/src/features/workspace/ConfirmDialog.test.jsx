import { fireEvent, render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import ConfirmDialog from "./ConfirmDialog.jsx";

const ASKS = {
  title: 'Delete "Thesis research"?',
  body: "The 3 chats and 2 files in this project are deleted with it. This can't be undone.",
  confirmLabel: "Delete project",
};

function draw(props = {}) {
  return render(<ConfirmDialog {...ASKS} {...props} />).container;
}

test("it asks, says what will happen, and offers both ways out", () => {
  draw();
  expect(screen.getByText('Delete "Thesis research"?')).toBeTruthy();
  expect(screen.getByText(/deleted with it/)).toBeTruthy();
  expect(screen.getByRole("button", { name: "Cancel" })).toBeTruthy();
  expect(screen.getByRole("button", { name: "Delete project" })).toBeTruthy();
});

test("the box does not know what it is deleting", () => {
  // Every sentence comes from the caller, which is what lets one pattern serve every deletion.
  draw({ title: "Delete this chat?", body: "Its files stay in the project.", confirmLabel: "Delete chat" });
  expect(screen.getByRole("button", { name: "Delete chat" })).toBeTruthy();
});

test("Cancel cancels and the confirm button confirms", () => {
  const onCancel = vi.fn();
  const onConfirm = vi.fn();
  draw({ onCancel, onConfirm });
  fireEvent.click(screen.getByRole("button", { name: "Cancel" }));
  expect(onCancel).toHaveBeenCalled();
  fireEvent.click(screen.getByRole("button", { name: "Delete project" }));
  expect(onConfirm).toHaveBeenCalled();
});

test("clicking the darkened screen is a way out", () => {
  const onCancel = vi.fn();
  const container = draw({ onCancel });
  fireEvent.click(container.querySelector(".dialog"));
  expect(onCancel).toHaveBeenCalled();
});

test("clicking inside the box is not", () => {
  // Otherwise reading the sentence would be enough to dismiss the question.
  const onCancel = vi.fn();
  const container = draw({ onCancel });
  fireEvent.click(container.querySelector(".dialog__card"));
  expect(onCancel).not.toHaveBeenCalled();
});

test("the keyboard arrives on the way out, not the way through", () => {
  // A destructive question should not have Enter land on the destructive answer.
  draw();
  expect(document.activeElement).toBe(screen.getByRole("button", { name: "Cancel" }));
});

test("it is announced as a dialog, named by what it asks", () => {
  const dialog = draw().querySelector("[role=dialog]");
  expect(dialog.getAttribute("aria-modal")).toBe("true");
  const named = dialog.getAttribute("aria-labelledby");
  expect(document.getElementById(named).textContent).toBe('Delete "Thesis research"?');
});

test("the box does not take the keyboard for itself", () => {
  // One listener owns Escape so the order lives in one place -- App's. A listener here would split
  // that order in two.
  const listen = vi.spyOn(document, "addEventListener");
  const onWindow = vi.spyOn(window, "addEventListener");
  draw();
  const keys = [...listen.mock.calls, ...onWindow.mock.calls].filter(([name]) => name === "keydown");
  expect(keys).toEqual([]);
  listen.mockRestore();
  onWindow.mockRestore();
});
