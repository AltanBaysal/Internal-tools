import { expect, test } from "vitest";

import { MODELS, modelName } from "./models.js";

// The list is text, and text belongs here rather than on the server. What the server owns is which
// of these a chat that picked nothing answers with.
test("Grok Build is the only model we offer", () => {
  // Madde 72. The others were removed knowingly: Grok Build costs less, and the run is meant to
  // stand on one model rather than on a choice nobody was making.
  expect(MODELS.map((model) => model.id)).toEqual(["grok-build-0.1"]);
});

test("the default the server starts from is a row in this menu", () => {
  // Python cannot read this file, so the match between config.XAI_MODEL and the list is pinned
  // here in words. A default the menu does not know leaves every new chat showing a raw id.
  expect(MODELS.map((model) => model.id)).toContain("grok-build-0.1");
});

test("each row carries a name and what it costs", () => {
  // The design wrote a sentence under each name, but those sentences belonged to models that do not
  // exist and the documentation describes only one of the real ones. The price is true for all of
  // them, and it is what the choice is actually about.
  for (const model of MODELS) {
    expect(model.name.length).toBeGreaterThan(0);
    expect(model.detail).toMatch(/\$/);
  }
});

test("a name is the display name, not the id", () => {
  expect(modelName("grok-build-0.1")).toBe("Grok Build");
});

test("a model the list does not know is shown as it is", () => {
  // XAI_MODEL can be set to anything, and a button that said nothing would be worse than one that
  // says a raw id.
  expect(modelName("grok-9000")).toBe("grok-9000");
});

test("a chat that picked a model we stopped offering still says what it is", () => {
  // Not hypothetical since Madde 72: grok-4.3 was the default until today, so chats on disk carry
  // it. Removing its row must not make them unreadable -- and a display name for a model the menu
  // no longer has would imply it can still be picked.
  expect(modelName("grok-4.3")).toBe("grok-4.3");
});

test("nothing chosen yet says so rather than lying about a model", () => {
  expect(modelName("")).toBe("Model");
});
