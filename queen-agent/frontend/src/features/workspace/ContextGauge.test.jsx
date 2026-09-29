import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";

import ContextGauge from "./ContextGauge.jsx";

// Madde 92. A gauge rather than a control: it is read and never pressed, which is also why it sits
// at the far end of the foot from the three things that are.
//
// Madde 343 gave it its words: the sentence on the circle, and from four fifths of the ceiling the
// share written beside it (design items 146 and 182).
//
// What the tests read is the share the gauge settled on, not the shape it drew with it. The drawing
// is one CSS rule and jsdom does not run it.

test("it fills by what the last answer sent", () => {
  render(<ContextGauge sent={41000} ceiling={50000} />);
  expect(screen.getByRole("img").style.getPropertyValue("--filled")).toBe("0.82");
});

test("a chat that has sent nothing draws no gauge", () => {
  // Not an empty circle: an empty circle is a mark that is always there and says nothing. The
  // gauge is born when the first answer comes back.
  const { container } = render(<ContextGauge sent={0} ceiling={50000} />);
  expect(container.firstChild).toBeNull();
});

test("past the ceiling it is full rather than overfull", () => {
  // A circle cannot fill past full, and drawing the excess would draw a lie.
  render(<ContextGauge sent={60000} ceiling={50000} />);
  const circle = screen.getByRole("img");
  expect(circle.style.getPropertyValue("--filled")).toBe("1");
  expect(circle.getAttribute("title")).toBe("This chat is full");
});

test("resting on it says how full the chat is", () => {
  // The circle shows the share; this is what makes it readable, and a screen reader hears the same.
  render(<ContextGauge sent={41000} ceiling={50000} />);
  const circle = screen.getByRole("img");
  expect(circle.getAttribute("title")).toBe("This chat is 82% full");
  expect(circle.getAttribute("aria-label")).toBe("This chat is 82% full");
});

test("the share is rounded down, so it never says 100 before the chat is full", () => {
  render(<ContextGauge sent={49990} ceiling={50000} />);
  expect(screen.getByRole("img").getAttribute("title")).toBe("This chat is 99% full");
});

test("a chat with an answer is at least 1% full", () => {
  // Rounded down, a small chat would say 0% beside a circle that is there.
  render(<ContextGauge sent={100} ceiling={50000} />);
  expect(screen.getByRole("img").getAttribute("title")).toBe("This chat is 1% full");
});

test("below four fifths the circle stands alone", () => {
  // 79.98% would round to 80; the words wait for the chat itself to reach four fifths.
  const { container } = render(<ContextGauge sent={39990} ceiling={50000} />);
  expect(container.querySelector(".context-gauge__words")).toBeNull();
});

test("from four fifths the share stands beside the circle", () => {
  // Hidden from a screen reader, which already reads the circle's sentence.
  const { container } = render(<ContextGauge sent={40000} ceiling={50000} />);
  const words = container.querySelector(".context-gauge__words");
  expect(words?.textContent).toBe("80% full");
  expect(words.getAttribute("aria-hidden")).toBe("true");
});

test("a full chat's circle has no words beside it", () => {
  // What a full chat says is its own notice's (Madde 352), not a line beside the circle.
  const { container } = render(<ContextGauge sent={50000} ceiling={50000} />);
  expect(container.querySelector(".context-gauge__words")).toBeNull();
});
