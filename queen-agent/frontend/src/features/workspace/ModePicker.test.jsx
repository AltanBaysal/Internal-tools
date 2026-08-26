import { fireEvent, render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import ModePicker from "./ModePicker.jsx";

// Madde 91. The skill picker's twin, with one difference that comes from what the two things are:
// a chat may have no skill and usually does not, but there is no such thing as no mode.

test("the button names the mode in force", () => {
  render(<ModePicker mode="plan" />);
  expect(screen.getByText("Plan", { selector: ".picker__name" })).toBeTruthy();
});

test("choosing a mode hands it up", () => {
  const onChange = vi.fn();
  render(<ModePicker mode="edit" open onChange={onChange} />);
  fireEvent.click(screen.getByText("Ask", { selector: ".menu__item-name" }));
  expect(onChange).toHaveBeenCalledWith("ask");
});

test("pressing the mode already in force does not clear it", () => {
  // Where the skill picker clears, this one holds: there is no way back to no mode, so a press
  // that emptied the button would leave the row saying something that cannot be true.
  const onChange = vi.fn();
  render(<ModePicker mode="ask" open onChange={onChange} />);
  fireEvent.click(screen.getByText("Ask", { selector: ".menu__item-name" }));
  expect(onChange).toHaveBeenCalledWith("ask");
});
