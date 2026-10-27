import { render, screen } from "@testing-library/react";
import { useRef } from "react";
import { afterEach, beforeEach, expect, test, vi } from "vitest";

import { useGrowingField } from "./useGrowingField.js";

// jsdom lays nothing out, so the sizes are declared and what is under test is the decision: how tall
// the field is told to be. Whether the browser then draws it so is QA's look at the screen.
let content;
let onMeasure;

beforeEach(() => {
  content = 120;
  onMeasure = () => {};
  vi.spyOn(Element.prototype, "scrollHeight", "get").mockImplementation(function scrollHeight() {
    if (this.tagName !== "TEXTAREA") return 0;
    onMeasure(this);
    return content;
  });
  // A 1px border above and below: what the box adds to what scrollHeight measures.
  vi.spyOn(HTMLElement.prototype, "offsetHeight", "get").mockReturnValue(50);
  vi.spyOn(Element.prototype, "clientHeight", "get").mockReturnValue(48);
});

afterEach(() => {
  vi.restoreAllMocks();
});

function Field({ value }) {
  const field = useRef(null);
  useGrowingField(field, value);
  return <textarea ref={field} rows={2} value={value} readOnly />;
}

test("the field is as tall as its text, its border included", () => {
  render(<Field value="Write the intro" />);
  expect(screen.getByRole("textbox").style.height).toBe("122px");
});

test("it follows the text as it grows and as it shrinks", () => {
  const { rerender } = render(<Field value="one line" />);
  content = 300;
  rerender(<Field value={"one line\nand many more"} />);
  expect(screen.getByRole("textbox").style.height).toBe("302px");

  content = 60;
  rerender(<Field value="one line" />);
  expect(screen.getByRole("textbox").style.height).toBe("62px");
});

test("a field that is not drawn keeps its rows rather than falling to nothing", () => {
  // A hidden field measures 0. Writing that down would leave it 0px tall once it is shown.
  content = 0;
  render(<Field value="Write the intro" />);
  expect(screen.getByRole("textbox").style.height).toBe("auto");
});

test("it is measured with no scrollbar narrowing its lines, and gets the bar back after", () => {
  // At its rows a long text shows the bar, the lines wrap narrower, and the field came out a line
  // too tall (found by the reviewer in Chrome).
  const overflow = [];
  onMeasure = (field) => overflow.push(field.style.overflowY);
  render(<Field value="Write the intro" />);
  expect(overflow).toEqual(["hidden"]);
  expect(screen.getByRole("textbox").style.overflowY).toBe("");
});
