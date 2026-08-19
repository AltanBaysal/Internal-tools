import { fireEvent, render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import SkillPicker from "./SkillPicker.jsx";
import { SKILLS } from "./skills.js";

test("with nothing selected the button says Skills and stays quiet", () => {
  const { container } = render(<SkillPicker skill="" />);
  expect(screen.getByRole("button", { name: /Skills/ })).toBeTruthy();
  expect(container.querySelector(".picker--on")).toBeNull();
});

test("a selected skill gives the button its name and its warm tone", () => {
  const { container } = render(<SkillPicker skill="verify-prompts" />);
  expect(screen.getByRole("button", { name: /Verify prompts/ })).toBeTruthy();
  expect(container.querySelector(".picker--on")).toBeTruthy();
});

test("open, it lists every skill under a label", () => {
  render(<SkillPicker skill="" open />);
  expect(screen.getByText("SKILLS")).toBeTruthy();
  for (const skill of SKILLS) expect(screen.getAllByText(skill.name).length).toBeGreaterThan(0);
  expect(screen.getByText(SKILLS[0].detail)).toBeTruthy();
});

test("choosing one hands the id over", () => {
  const onChange = vi.fn();
  render(<SkillPicker skill="" open onChange={onChange} />);
  fireEvent.click(screen.getByText("Split into frames"));
  expect(onChange).toHaveBeenCalledWith("split-into-frames");
});

test("pressing the selected one clears it", () => {
  // The difference from the model picker: a chat may have no skill at all, and this is how it gets
  // back there.
  const onChange = vi.fn();
  render(<SkillPicker skill="verify-prompts" open onChange={onChange} />);
  fireEvent.click(screen.getByText("Verify prompts", { selector: ".menu__item-name" }));
  expect(onChange).toHaveBeenCalledWith("");
});

test("the selected row is the marked one", () => {
  const { container } = render(<SkillPicker skill="verify-prompts" open />);
  const checked = [...container.querySelectorAll(".menu__item--checked")];
  expect(checked.length).toBe(1);
  expect(checked[0].textContent).toContain("Verify prompts");
});

// Whether a picker is open is App's business now: Escape closes them in a fixed order and one menu
// closes the other, and neither is knowable from inside a single picker.
test("open and shut is asked for from outside", () => {
  const onToggle = vi.fn();
  render(<SkillPicker skill="" onToggle={onToggle} />);
  expect(screen.queryByText("SKILLS")).toBeNull();
  fireEvent.click(screen.getByRole("button", { name: /Skills/ }));
  expect(onToggle).toHaveBeenCalled();
});
