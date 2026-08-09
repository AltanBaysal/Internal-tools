import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";

import App from "./App.jsx";

test("renders the shell", () => {
  render(<App />);
  expect(screen.getByTestId("app-shell")).toBeTruthy();
});
