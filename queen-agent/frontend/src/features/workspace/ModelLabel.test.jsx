import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";

import ModelLabel from "./ModelLabel.jsx";

test("it says which model answers", () => {
  render(<ModelLabel />);
  expect(screen.getByText("Grok Build")).toBeTruthy();
});

test("it is not something to press", () => {
  // Madde 82: one model, so there is nothing to choose. A control that opens nothing would be a
  // promise the app cannot keep.
  render(<ModelLabel />);
  expect(screen.queryByRole("button")).toBeNull();
});
