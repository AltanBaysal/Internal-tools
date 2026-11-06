import { render, screen } from "@testing-library/react";
import { expect, it } from "vitest";
import { Placeholder } from "./Placeholder";
import { appTitle } from "./about";
import { info } from "./api/openapi.json";

it("shows the app and its version as the core's OpenAPI document names them", () => {
  render(<Placeholder />);

  expect(screen.getByRole("heading").textContent).toBe(
    appTitle({ app: info.title, version: info.version }),
  );
});
