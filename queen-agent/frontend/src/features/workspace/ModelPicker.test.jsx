import { fireEvent, render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import ModelPicker from "./ModelPicker.jsx";
import { MODELS } from "./models.js";

test("the button says which model answers", () => {
  render(<ModelPicker model="deepseek-v4-flash" />);
  expect(screen.getByRole("button", { name: /DeepSeek Flash/ })).toBeTruthy();
});

test("it is something to press", () => {
  // The reversal of Madde 82's lock. One model made a control a promise the app could not keep;
  // three make a label the lie instead.
  const onToggle = vi.fn();
  render(<ModelPicker model="grok-build-0.1" onToggle={onToggle} />);
  fireEvent.click(screen.getByRole("button", { name: /Grok Build/ }));
  expect(onToggle).toHaveBeenCalled();
});

test("open, it lists every model with what it costs", () => {
  render(<ModelPicker model="grok-build-0.1" open />);
  expect(screen.getByText("MODELS")).toBeTruthy();
  for (const model of MODELS) expect(screen.getAllByText(model.name).length).toBeGreaterThan(0);
  expect(screen.getByText("$0.22 / $0.66 per 1M")).toBeTruthy();
});

test("the selected row is the marked one", () => {
  const { container } = render(<ModelPicker model="deepseek-v4-pro" open />);
  const checked = [...container.querySelectorAll(".menu__item--checked")];
  expect(checked.length).toBe(1);
  expect(checked[0].textContent).toContain("DeepSeek Pro");
});

test("choosing one hands the id over", () => {
  const onChange = vi.fn();
  render(<ModelPicker model="grok-build-0.1" open onChange={onChange} />);
  fireEvent.click(screen.getByText("DeepSeek Flash"));
  expect(onChange).toHaveBeenCalledWith("deepseek-v4-flash");
});

test("pressing the selected one keeps it rather than clearing", () => {
  // The difference from SkillPicker, and it comes from what the two things are: a chat may have no
  // skill and that is ordinary, but there is no way back to no model.
  const onChange = vi.fn();
  render(<ModelPicker model="deepseek-v4-flash" open onChange={onChange} />);
  fireEvent.click(screen.getByText("DeepSeek Flash", { selector: ".menu__item-name" }));
  expect(onChange).toHaveBeenCalledWith("deepseek-v4-flash");
});

// Whether a picker is open is App's business: Escape closes them in a fixed order and one menu
// closes the other, and neither is knowable from inside a single picker.
test("open and shut is asked for from outside", () => {
  const onToggle = vi.fn();
  render(<ModelPicker model="grok-build-0.1" onToggle={onToggle} />);
  expect(screen.queryByText("MODELS")).toBeNull();
  fireEvent.click(screen.getByRole("button", { name: /Grok Build/ }));
  expect(onToggle).toHaveBeenCalled();
});
