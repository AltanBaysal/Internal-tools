import { expect, test } from "vitest";

import { MODELS, modelName } from "./models.js";

// The list is text, and text belongs here rather than on the server. What the server owns is which
// of these a chat that picked nothing answers with.
test("the models we offer are these, and grok-4.5 is not one of them", () => {
  // Same price as grok-4.6 for an older version, so offering it only adds a wrong choice.
  expect(MODELS.map((model) => model.id)).toEqual([
    "grok-4.6",
    "grok-4.3",
    "grok-4.20-0309-reasoning",
    "grok-4.20-0309-non-reasoning",
    "grok-4.20-multi-agent-0309",
    "grok-build-0.1",
  ]);
});

test("the default the server starts from is a row in this menu", () => {
  // Python cannot read this file, so the match between config.XAI_MODEL and the list is pinned
  // here in words. A default the menu does not know leaves every new chat showing a raw id.
  expect(MODELS.map((model) => model.id)).toContain("grok-4.3");
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
  expect(modelName("grok-4.20-0309-reasoning")).toBe("Grok 4.20 (Reasoning)");
});

test("a model the list does not know is shown as it is", () => {
  // XAI_MODEL can be set to anything, and a button that said nothing would be worse than one that
  // says a raw id.
  expect(modelName("grok-9000")).toBe("grok-9000");
});

test("a chat that picked the model we stopped offering still says what it is", () => {
  // Removing a row must not make an older chat unreadable: the id it kept is shown as it is.
  expect(modelName("grok-4.5")).toBe("grok-4.5");
});

test("nothing chosen yet says so rather than lying about a model", () => {
  expect(modelName("")).toBe("Model");
});
