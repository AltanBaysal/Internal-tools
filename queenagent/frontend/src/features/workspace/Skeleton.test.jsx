import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";

import Skeleton from "./Skeleton.jsx";

test("it draws the number of blocks it was asked for", () => {
  render(<Skeleton rows={4} />);
  expect(screen.getByTestId("skeleton").children.length).toBe(4);
});

test("one block is the default", () => {
  render(<Skeleton />);
  expect(screen.getByTestId("skeleton").children.length).toBe(1);
});

test("the whole content area has a shape of its own", () => {
  // Three blocks: a bar, a block, a shorter bar. The design's fourth part was a card grid, and the
  // grid went in Madde 3.
  const { container } = render(<Skeleton variant="screen" rows={3} />);
  expect(container.querySelector(".skeleton--screen")).toBeTruthy();
  expect(screen.getByTestId("skeleton").children.length).toBe(3);
});

test("the blocks say nothing", () => {
  // A skeleton stands in for content that has not arrived; inventing words for it would be a lie.
  render(<Skeleton rows={2} />);
  expect(screen.getByTestId("skeleton").textContent).toBe("");
});
