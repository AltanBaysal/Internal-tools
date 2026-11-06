import { describe, expect, it } from "vitest";
import { appTitle } from "./about";

describe("appTitle", () => {
  it("writes the name in words and the version's first number", () => {
    expect(appTitle({ app: "queen-studio", version: "1.0.0" })).toBe("Queen Studio V1");
  });

  it("follows a rename and a later version", () => {
    expect(appTitle({ app: "queen-editor", version: "12.3.0" })).toBe("Queen Editor V12");
  });
});
