import { expect, test } from "vitest";

import { DEFAULT_MODEL, MODELS, modelName } from "./models.js";

test("two models are offered", () => {
  // Three until Madde 177. Grok left the menu rather than the app: it writes the frames' actions
  // now (config.PROMPT_MODEL), which is a role rather than something to pick.
  expect(MODELS.map((model) => model.id)).toEqual(["deepseek-v4-flash", "deepseek-v4-pro"]);
});

test("every row carries a name and what it costs", () => {
  // The price is the detail because choosing between these is a price question: the roadmap's
  // reason for the madde is the bill, and a menu that hid the number would answer the wrong one.
  //
  // The names are this file's own. What config.py holds is what an id means to a provider -- and
  // the id IS the model name on the wire, so it cannot be renamed there without breaking the call.
  expect(MODELS.map((model) => [model.name, model.detail])).toEqual([
    ["Queen Flash", "$0.22 / $0.66 per 1M"],
    ["Queen Pro", "$0.66 / $1.98 per 1M"],
  ]);
});

test("the default is the cheaper of the two", () => {
  // And it has to be the same id config.py defaults to, or the button would say one thing while
  // the request went somewhere else.
  expect(DEFAULT_MODEL).toBe("deepseek-v4-flash");
});

test("a known id reads as its name", () => {
  expect(modelName("deepseek-v4-pro")).toBe("Queen Pro");
});

test("no id reads as the default's name", () => {
  // Where this parts from skillName: no skill is an ordinary state and reads as "Skills", but
  // every answer is given by some model, so nothing here means the default rather than a gap.
  expect(modelName("")).toBe("Queen Flash");
});

test("an unknown id says itself", () => {
  // A record written before Madde 72 can still name one of the five that were dropped, and the
  // button says its id rather than going blank -- skillName's own rule.
  expect(modelName("grok-4.3")).toBe("grok-4.3");
});

test("a model that is only a role says its id", () => {
  // Madde 177 took Grok out of the menu while Madde 175 kept it wired, so a message answered by it
  // before today is the first record this rule ever meets for real. Its id rather than a name we
  // made up: that message really was answered by it, and a friendly label would misread the record.
  expect(modelName("grok-build-0.1")).toBe("grok-build-0.1");
});
