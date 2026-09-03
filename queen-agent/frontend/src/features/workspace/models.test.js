import { expect, test } from "vitest";

import { DEFAULT_MODEL, MODELS, modelName } from "./models.js";

test("five models are offered, each pair next to its other road", () => {
  // Madde 149 put the same weights behind two providers. They sit next to each other on purpose:
  // the reason both exist is to be run one after the other on the same request, and a menu that
  // scattered them would make the comparison a scroll rather than a click.
  expect(MODELS.map((model) => model.id)).toEqual([
    "grok-build-0.1",
    "deepseek-v4-flash",
    "deepseek/deepseek-v4-flash-0731",
    "deepseek-v4-pro",
    "deepseek/deepseek-v4-pro-0813",
  ]);
});

test("every row carries a name and what it costs", () => {
  // The price is the detail because choosing between these is a price question: the roadmap's
  // reason for the madde is the bill, and a menu that hid the number would answer the wrong one.
  // The name is what tells the two roads apart -- the model is the same on both.
  expect(MODELS.map((model) => [model.name, model.detail])).toEqual([
    ["Grok Build", "$1 / $2 per 1M"],
    ["DeepSeek Flash", "$0.22 / $0.66 per 1M"],
    ["DeepSeek Flash · Infra", "$0.08 / $0.18 per 1M"],
    ["DeepSeek Pro", "$0.66 / $1.98 per 1M"],
    ["DeepSeek Pro · Infra", "$1.30 / $2.60 per 1M"],
  ]);
});

test("the default is the one the app has always answered with", () => {
  expect(DEFAULT_MODEL).toBe("grok-build-0.1");
});

test("a known id reads as its name", () => {
  expect(modelName("deepseek-v4-flash")).toBe("DeepSeek Flash");
});

test("an id with a slash in it reads as its name too", () => {
  // The first ids to carry one. Nothing takes an id apart -- it is carried, compared and looked
  // up -- so the slash is only worth pinning because a later reader may assume it cannot be there.
  expect(modelName("deepseek/deepseek-v4-flash-0731")).toBe("DeepSeek Flash · Infra");
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
