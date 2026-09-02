import { expect, test } from "vitest";

import { DEFAULT_MODEL, MODELS, modelName } from "./models.js";

test("three models are offered", () => {
  expect(MODELS.map((model) => model.id)).toEqual([
    "grok-build-0.1",
    "deepseek-v4-flash",
    "deepseek-v4-pro",
  ]);
});

test("every row carries a name and what it costs", () => {
  // The price is the detail because choosing between these is a price question: the roadmap's
  // reason for the madde is the bill, and a menu that hid the number would answer the wrong one.
  expect(MODELS.map((model) => [model.name, model.detail])).toEqual([
    ["Grok Build", "$1 / $2 per 1M"],
    ["DeepSeek Flash", "$0.22 / $0.66 per 1M"],
    ["DeepSeek Pro", "$0.66 / $1.98 per 1M"],
  ]);
});

test("the default is the one the app has always answered with", () => {
  expect(DEFAULT_MODEL).toBe("grok-build-0.1");
});

test("a known id reads as its name", () => {
  expect(modelName("deepseek-v4-flash")).toBe("DeepSeek Flash");
});

test("no id reads as the default's name", () => {
  // Where this parts from skillName: no skill is an ordinary state and reads as "Skills", but
  // every answer is given by some model, so nothing here means the default rather than a gap.
  expect(modelName("")).toBe("Grok Build");
});

test("an unknown id says itself", () => {
  // A record written before Madde 72 can still name one of the five that were dropped, and the
  // button says its id rather than going blank -- skillName's own rule.
  expect(modelName("grok-4.3")).toBe("grok-4.3");
});
