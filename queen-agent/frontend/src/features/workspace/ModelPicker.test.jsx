import { fireEvent, render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import ModelPicker from "./ModelPicker.jsx";
import { MODELS } from "./models.js";

test("the button says which model answers", () => {
  render(<ModelPicker model="deepseek-v4-flash" />);
  expect(screen.getByRole("button", { name: /Queen Flash/ })).toBeTruthy();
});

test("it is something to press", () => {
  // The reversal of Madde 82's lock. One model made a control a promise the app could not keep;
  // two make a label the lie instead.
  const onToggle = vi.fn();
  render(<ModelPicker model="deepseek-v4-pro" onToggle={onToggle} />);
  fireEvent.click(screen.getByRole("button", { name: /Queen Pro/ }));
  expect(onToggle).toHaveBeenCalled();
});

test("open, it lists every model with what it costs", () => {
  render(<ModelPicker model="deepseek-v4-pro" open />);
  expect(screen.getByText("MODELS")).toBeTruthy();
  for (const model of MODELS) expect(screen.getAllByText(model.name).length).toBeGreaterThan(0);
  expect(screen.getByText("$0.22 / $0.66 per 1M")).toBeTruthy();
});

test("the menu offers the two and nothing else", () => {
  // Madde 177. Grok is still wired -- it writes the frames' actions -- and it is still what some
  // older messages were answered by, so this asks the menu rather than the module: what must be
  // gone is the row somebody can press.
  const { container } = render(<ModelPicker model="deepseek-v4-flash" open />);
  const rows = [...container.querySelectorAll(".menu__item-name")];
  expect(rows.map((row) => row.textContent)).toEqual(["Queen Flash", "Queen Pro"]);
});

test("the selected row is the marked one", () => {
  const { container } = render(<ModelPicker model="deepseek-v4-pro" open />);
  const checked = [...container.querySelectorAll(".menu__item--checked")];
  expect(checked.length).toBe(1);
  expect(checked[0].textContent).toContain("Queen Pro");
});

test("choosing one hands the id over", () => {
  // The id, never the name: what travels on the message is what config.py resolves to an address,
  // and Queen Flash is a word this file made up for the person reading it.
  const onChange = vi.fn();
  render(<ModelPicker model="deepseek-v4-pro" open onChange={onChange} />);
  fireEvent.click(screen.getByText("Queen Flash"));
  expect(onChange).toHaveBeenCalledWith("deepseek-v4-flash");
});

test("pressing the selected one keeps it rather than clearing", () => {
  // The difference from SkillPicker, and it comes from what the two things are: a chat may have no
  // skill and that is ordinary, but there is no way back to no model.
  const onChange = vi.fn();
  render(<ModelPicker model="deepseek-v4-flash" open onChange={onChange} />);
  fireEvent.click(screen.getByText("Queen Flash", { selector: ".menu__item-name" }));
  expect(onChange).toHaveBeenCalledWith("deepseek-v4-flash");
});

test("a model that was picked before it left the menu still marks nothing", () => {
  // An older message can name Grok, and the picker has no row for it now. The button says its id
  // (models.js) and no row is ticked -- rather than the default quietly wearing the mark, which
  // would tell the user this chat was answered by something it was not.
  const { container } = render(<ModelPicker model="grok-build-0.1" open />);
  expect(screen.getByRole("button", { name: /grok-build-0.1/ })).toBeTruthy();
  expect(container.querySelectorAll(".menu__item--checked").length).toBe(0);
});

// Whether a picker is open is App's business: Escape closes them in a fixed order and one menu
// closes the other, and neither is knowable from inside a single picker.
test("open and shut is asked for from outside", () => {
  const onToggle = vi.fn();
  render(<ModelPicker model="deepseek-v4-pro" onToggle={onToggle} />);
  expect(screen.queryByText("MODELS")).toBeNull();
  fireEvent.click(screen.getByRole("button", { name: /Queen Pro/ }));
  expect(onToggle).toHaveBeenCalled();
});
