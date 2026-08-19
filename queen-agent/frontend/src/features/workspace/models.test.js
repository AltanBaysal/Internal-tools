import { expect, test } from "vitest";

import { MODELS, modelName } from "./models.js";

// The list is text, and text belongs here rather than on the server. What the server owns is which
// of these a chat that picked nothing answers with.
test("every text model xAI documents is offered", () => {
  expect(MODELS.map((model) => model.id)).toEqual([
    "grok-4.6",
    "grok-4.5",
    "grok-4.3",
    "grok-4.20-0309-reasoning",
    "grok-4.20-0309-non-reasoning",
    "grok-4.20-multi-agent-0309",
    "grok-build-0.1",
  ]);
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

test("nothing chosen yet says so rather than lying about a model", () => {
  expect(modelName("")).toBe("Model");
});
