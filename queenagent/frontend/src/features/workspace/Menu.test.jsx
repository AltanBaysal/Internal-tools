import { fireEvent, render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import Menu from "./Menu.jsx";

const ITEMS = [
  { label: "Rename", onChoose: () => {} },
  { label: "Delete project", danger: true, onChoose: () => {} },
];

test("it draws what it was given, in the order it was given", () => {
  render(<Menu items={ITEMS} />);
  const buttons = screen.getAllByRole("button");
  expect(buttons.map((button) => button.textContent)).toEqual(["Rename", "Delete project"]);
});

test("a destructive choice is marked as one", () => {
  const { container } = render(<Menu items={ITEMS} />);
  expect(container.querySelector(".menu__item--danger").textContent).toBe("Delete project");
});

test("choosing runs the choice and closes the menu", () => {
  const onChoose = vi.fn();
  const onClose = vi.fn();
  render(<Menu items={[{ label: "Rename", onChoose }]} onClose={onClose} />);
  fireEvent.click(screen.getByRole("button", { name: "Rename" }));
  expect(onChoose).toHaveBeenCalled();
  expect(onClose).toHaveBeenCalled();
});

// A catcher rather than a listener on the document. The two close the menu alike, but a listener
// lets the same click reach whatever was under it, and the design wants the first click spent on
// closing. That it covers the screen is a CSS lock; that it closes is here.
test("an invisible catcher stands over the screen and closes the menu", () => {
  const onClose = vi.fn();
  render(<Menu items={ITEMS} onClose={onClose} />);
  fireEvent.click(screen.getByTestId("menu-catcher"));
  expect(onClose).toHaveBeenCalled();
});

test("a click inside it does not close it", () => {
  const onClose = vi.fn();
  const { container } = render(<Menu items={ITEMS} onClose={onClose} />);
  fireEvent.click(container.querySelector(".menu"));
  expect(onClose).not.toHaveBeenCalled();
});

test("nothing is listened for on the document", () => {
  // The catcher is the whole of it now: a document-wide mousedown would fire for the catcher's own
  // click as well, and two ways to close one menu is one too many.
  const listen = vi.spyOn(document, "addEventListener");
  render(<Menu items={ITEMS} />);
  expect(listen.mock.calls).toEqual([]);
  listen.mockRestore();
});

test("the menu does not take the keyboard for itself", () => {
  // Escape belongs to App's one listener, exactly as it does for the confirmation box.
  const listen = vi.spyOn(document, "addEventListener");
  const onWindow = vi.spyOn(window, "addEventListener");
  render(<Menu items={ITEMS} />);
  const keys = [...listen.mock.calls, ...onWindow.mock.calls].filter(([name]) => name === "keydown");
  expect(keys).toEqual([]);
  listen.mockRestore();
  onWindow.mockRestore();
});

test("given the button it hangs off, it takes a place on the screen", () => {
  // jsdom measures everything as zero, so what is asserted is that the placement was applied at
  // all; the arithmetic is proved in menuPlacement.test.js.
  const anchor = document.createElement("button");
  document.body.appendChild(anchor);
  const { container } = render(<Menu items={ITEMS} anchor={anchor} />);
  const box = container.querySelector(".menu");
  expect(box.style.top).not.toBe("");
  expect(box.style.left).not.toBe("");
  expect(box.style.maxHeight).not.toBe("");
  anchor.remove();
});
