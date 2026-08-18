import { fireEvent, render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import ModelPicker from "./ModelPicker.jsx";
import { MODELS } from "./models.js";

test("closed, it says which model this chat answers with", () => {
  render(<ModelPicker model="grok-4.3" />);
  expect(screen.getByRole("button", { name: /Grok 4.3/ })).toBeTruthy();
});

test("a model the list does not know still gets a button", () => {
  // XAI_MODEL can be set to anything at all, and the button has to say something true.
  render(<ModelPicker model="grok-9000" />);
  expect(screen.getByRole("button", { name: /grok-9000/ })).toBeTruthy();
});

test("pressing it opens the labelled menu with every model in it", () => {
  render(<ModelPicker model="grok-4.5" />);
  fireEvent.click(screen.getByRole("button", { name: /Grok 4.5/ }));
  expect(screen.getByText("MODEL")).toBeTruthy();
  for (const model of MODELS) expect(screen.getAllByText(model.name).length).toBeGreaterThan(0);
});

test("the menu says what each model costs", () => {
  render(<ModelPicker model="grok-4.5" />);
  fireEvent.click(screen.getByRole("button", { name: /Grok 4.5/ }));
  expect(screen.getByText(MODELS[0].detail)).toBeTruthy();
});

test("choosing another one hands the id over and closes", () => {
  const onChange = vi.fn();
  render(<ModelPicker model="grok-4.5" onChange={onChange} />);
  fireEvent.click(screen.getByRole("button", { name: /Grok 4.5/ }));
  fireEvent.click(screen.getByText("Grok Build"));
  expect(onChange).toHaveBeenCalledWith("grok-build-0.1");
  expect(screen.queryByText("MODEL")).toBeNull();
});

test("choosing the one already in use asks the server for nothing", () => {
  // A model is never cleared -- that is the Skills button's rule, not this one's -- so pressing the
  // current row is not a change and must not be sent as one.
  const onChange = vi.fn();
  render(<ModelPicker model="grok-4.5" onChange={onChange} />);
  fireEvent.click(screen.getByRole("button", { name: /Grok 4.5/ }));
  fireEvent.click(screen.getByText("Grok 4.5", { selector: ".menu__item-name" }));
  expect(onChange).not.toHaveBeenCalled();
  expect(screen.queryByText("MODEL")).toBeNull();
});

test("the row in use is the marked one", () => {
  const { container } = render(<ModelPicker model="grok-4.5" />);
  fireEvent.click(screen.getByRole("button", { name: /Grok 4.5/ }));
  const checked = [...container.querySelectorAll(".menu__item--checked")];
  expect(checked.length).toBe(1);
  expect(checked[0].textContent).toContain("Grok 4.5");
});

test("it takes no keyboard of its own", () => {
  // Escape belongs to App's one listener; the menu inside follows the same rule.
  const onWindow = vi.spyOn(window, "addEventListener");
  render(<ModelPicker model="grok-4.5" />);
  expect(onWindow.mock.calls.filter(([name]) => name === "keydown")).toEqual([]);
  onWindow.mockRestore();
});
