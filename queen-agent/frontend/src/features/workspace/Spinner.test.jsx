import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";

import Spinner from "./Spinner.jsx";

// Madde 340, the design's items 173 and 181: one small turning ring. Every place that waits puts the
// same ring in a box of its own, so the ring is all this draws.
test("it is the design's ring", () => {
  render(<Spinner />);
  expect(screen.getByTestId("spinner").className).toBe("spinner");
});

test("the ring says nothing", () => {
  // The heading and the buttons standing around it already say what is loading.
  render(<Spinner />);
  const ring = screen.getByTestId("spinner");
  expect(ring.getAttribute("aria-hidden")).toBe("true");
  expect(ring.textContent).toBe("");
});
