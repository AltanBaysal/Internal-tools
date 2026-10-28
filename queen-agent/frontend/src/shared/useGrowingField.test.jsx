import { act, render, screen } from "@testing-library/react";
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

// The field's width as the browser reports it, a frame at a time: the observer's notice, and the
// frame the measuring waits for.
function observedWidth() {
  const notices = [];
  const frames = [];
  vi.stubGlobal(
    "ResizeObserver",
    class {
      constructor(callback) {
        notices.push(callback);
      }
      observe() {}
      disconnect() {}
    },
  );
  vi.stubGlobal("requestAnimationFrame", (callback) => frames.push(callback));
  vi.stubGlobal("cancelAnimationFrame", () => {});
  return (width, height = 50) =>
    act(() => {
      notices.forEach((notice) => notice([{ contentRect: { width, height } }]));
      frames.splice(0).forEach((callback) => callback());
    });
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

test("a field whose width changes is measured again, its text unchanged", () => {
  // Madde 505, found by QA: on a narrow window's first load the composer is drawn a few pixels wide
  // before the shell is measured, its empty box measured 202px tall with the placeholder wrapped,
  // and nothing measured it again. A field shown after being hidden is the same case: no width, then
  // its own.
  const resize = observedWidth();
  try {
    content = 200;
    render(<Field value="" />);
    resize(4);
    expect(screen.getByRole("textbox").style.height).toBe("202px");
    content = 52;
    resize(560);
    expect(screen.getByRole("textbox").style.height).toBe("54px");
  } finally {
    vi.unstubAllGlobals();
  }
});

test("a field hidden to no width keeps the height it had", () => {
  // The composer behind the full chat's notice: measured at no width it would fall to its rows, and
  // on Continue paint at two rows for a frame before jumping back (54 then 153 px, the reviewer).
  const resize = observedWidth();
  try {
    content = 300;
    render(<Field value={"a reply\nover\nsix\nlines\nof\ntext"} />);
    resize(560);
    expect(screen.getByRole("textbox").style.height).toBe("302px");
    content = 0;
    resize(0);
    expect(screen.getByRole("textbox").style.height).toBe("302px");
  } finally {
    vi.unstubAllGlobals();
  }
});

test("a field whose height alone changes is not measured again", () => {
  // Its height is what the measuring writes: answering that would measure every measurement.
  const resize = observedWidth();
  try {
    render(<Field value="Write the intro" />);
    resize(560);
    let measured = 0;
    onMeasure = () => {
      measured += 1;
    };
    resize(560, 300);
    expect(measured).toBe(0);
  } finally {
    vi.unstubAllGlobals();
  }
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
