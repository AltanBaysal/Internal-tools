import { fireEvent, render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import FileCard, { CreatingFile } from "./FileCard.jsx";

// Madde 344: the card a turn leaves behind, and the skeleton it is drawn as while it is being born,
// in one file.

test("the card is a door into the file", () => {
  const onOpen = vi.fn();
  render(<FileCard name="outline.md" onOpen={onOpen} />);
  expect(screen.getByText("md")).toBeTruthy();
  expect(screen.getByText("✓ saved to project")).toBeTruthy();
  fireEvent.click(screen.getByRole("button", { name: /outline\.md/ }));
  expect(onOpen).toHaveBeenCalledWith("outline.md");
});

test("the open card says so and points nowhere", () => {
  render(<FileCard name="outline.md" selected />);
  expect(screen.getByText("open")).toBeTruthy();
  expect(screen.queryByText("Open ›")).toBeNull();
});

test("a card about to be born says what is happening", () => {
  render(<CreatingFile />);
  expect(screen.getByText("creating file…")).toBeTruthy();
});
