import { fireEvent, render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import ModelPicker from "./ModelPicker.jsx";
import { MODELS } from "./models.js";

test("closed, it says which model this chat answers with", () => {
  render(<ModelPicker model="grok-build-0.1" />);
  expect(screen.getByRole("button", { name: /Grok Build/ })).toBeTruthy();
});

test("a model the list does not know still gets a button", () => {
  // XAI_MODEL can be set to anything at all, and the button has to say something true.
  render(<ModelPicker model="grok-9000" />);
  expect(screen.getByRole("button", { name: /grok-9000/ })).toBeTruthy();
});

test("open, it lists every model under a label", () => {
  render(<ModelPicker model="grok-build-0.1" open />);
  expect(screen.getByText("MODEL")).toBeTruthy();
  for (const model of MODELS) expect(screen.getAllByText(model.name).length).toBeGreaterThan(0);
});

test("the menu says what each model costs", () => {
  render(<ModelPicker model="grok-build-0.1" open />);
  expect(screen.getAllByText(MODELS[0].detail).length).toBeGreaterThan(0);
});

test("choosing another one hands the id over", () => {
  // Since Madde 72 the move that exists is from a model we no longer offer to the one we do.
  const onChange = vi.fn();
  render(<ModelPicker model="grok-4.3" open onChange={onChange} />);
  fireEvent.click(screen.getByText("Grok Build"));
  expect(onChange).toHaveBeenCalledWith("grok-build-0.1");
});

test("choosing the one already in use asks the server for nothing", () => {
  // A model is never cleared -- that is the Skills button's rule, not this one's -- so pressing the
  // current row is not a change and must not be sent as one.
  const onChange = vi.fn();
  render(<ModelPicker model="grok-build-0.1" open onChange={onChange} />);
  fireEvent.click(screen.getByText("Grok Build", { selector: ".menu__item-name" }));
  expect(onChange).not.toHaveBeenCalled();
});

test("the row in use is the marked one", () => {
  const { container } = render(<ModelPicker model="grok-build-0.1" open />);
  const checked = [...container.querySelectorAll(".menu__item--checked")];
  expect(checked.length).toBe(1);
  expect(checked[0].textContent).toContain("Grok Build");
});

test("a chat on a model we no longer offer marks no row", () => {
  // Marking Grok Build would say this chat answers with it, and it does not: the record keeps
  // grok-4.3 and the server sends that. No row is the honest drawing.
  const { container } = render(<ModelPicker model="grok-4.3" open />);
  expect(container.querySelectorAll(".menu__item--checked").length).toBe(0);
});

// Whether it is open is App's business now: Escape closes the two pickers in a fixed order and one
// closes the other, and neither is knowable from inside a single picker.
test("open and shut is asked for from outside", () => {
  const onToggle = vi.fn();
  render(<ModelPicker model="grok-build-0.1" onToggle={onToggle} />);
  expect(screen.queryByText("MODEL")).toBeNull();
  fireEvent.click(screen.getByRole("button", { name: /Grok Build/ }));
  expect(onToggle).toHaveBeenCalled();
});

test("it takes no keyboard of its own", () => {
  // Escape belongs to App's one listener; the menu inside follows the same rule.
  const onWindow = vi.spyOn(window, "addEventListener");
  render(<ModelPicker model="grok-build-0.1" />);
  expect(onWindow.mock.calls.filter(([name]) => name === "keydown")).toEqual([]);
  onWindow.mockRestore();
});
