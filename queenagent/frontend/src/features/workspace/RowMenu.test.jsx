import { fireEvent, render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import RowMenu from "./RowMenu.jsx";

const ITEMS = [
  { label: "Rename", onChoose: () => {} },
  { label: "Delete project", danger: true, onChoose: () => {} },
];

test("it draws what it was given, in the order it was given", () => {
  render(<RowMenu items={ITEMS} />);
  const buttons = screen.getAllByRole("button");
  expect(buttons.map((button) => button.textContent)).toEqual(["Rename", "Delete project"]);
});

test("a destructive choice is marked as one", () => {
  const { container } = render(<RowMenu items={ITEMS} />);
  expect(container.querySelector(".row-menu__item--danger").textContent).toBe("Delete project");
});

test("choosing runs the choice and closes the menu", () => {
  const onChoose = vi.fn();
  const onClose = vi.fn();
  render(<RowMenu items={[{ label: "Rename", onChoose }]} onClose={onClose} />);
  fireEvent.click(screen.getByRole("button", { name: "Rename" }));
  expect(onChoose).toHaveBeenCalled();
  expect(onClose).toHaveBeenCalled();
});

test("a click anywhere else closes it", () => {
  const onClose = vi.fn();
  render(<RowMenu items={ITEMS} onClose={onClose} />);
  fireEvent.mouseDown(document.body);
  expect(onClose).toHaveBeenCalled();
});

test("a click inside it does not", () => {
  const onClose = vi.fn();
  const { container } = render(<RowMenu items={ITEMS} onClose={onClose} />);
  fireEvent.mouseDown(container.querySelector(".row-menu"));
  expect(onClose).not.toHaveBeenCalled();
});

test("the menu does not take the keyboard for itself", () => {
  // Escape belongs to App's one listener, exactly as it does for the confirmation box.
  const listen = vi.spyOn(document, "addEventListener");
  const onWindow = vi.spyOn(window, "addEventListener");
  render(<RowMenu items={ITEMS} />);
  const keys = [...listen.mock.calls, ...onWindow.mock.calls].filter(([name]) => name === "keydown");
  expect(keys).toEqual([]);
  listen.mockRestore();
  onWindow.mockRestore();
});
