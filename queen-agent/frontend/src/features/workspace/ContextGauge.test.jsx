import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";

import ContextGauge from "./ContextGauge.jsx";

// Madde 92. A gauge rather than a control: it is read and never pressed, which is also why it sits
// at the far end of the foot from the three things that are.
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
  expect(screen.getByRole("img").style.getPropertyValue("--filled")).toBe("1");
});

test("resting on it reads the share in words", () => {
  // The circle shows the share; this is what makes it readable.
  render(<ContextGauge sent={41000} ceiling={50000} />);
  expect(screen.getByRole("img").getAttribute("title")).toBe("82% of the context ceiling");
});
