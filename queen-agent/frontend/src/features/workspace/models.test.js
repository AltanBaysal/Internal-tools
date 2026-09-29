import { expect, test } from "vitest";

import { DEFAULT_MODEL, MODELS, modelName } from "./models.js";

test("one model is offered", () => {
  // Madde 336. DeepSeek closed deepseek-v4-pro on 14 September and answers it with Flash, so Queen
  // Pro left the menu; Flash stays under the name DeepSeek gives it today.
  expect(MODELS.map((model) => model.id)).toEqual(["deepseek-flash"]);
});

test("the row carries a name and what it costs", () => {
  // The names are this file's own. What config.py holds is what an id means to a provider -- and
  // the id IS the model name on the wire, so it cannot be renamed there without breaking the call.
  expect(MODELS.map((model) => [model.name, model.detail])).toEqual([
    ["Queen Flash", "$0.22 / $0.66 per 1M"],
  ]);
});

test("the default is the one on offer", () => {
  // And it has to be the same id config.py defaults to, or the button would say one thing while
  // the request went somewhere else.
  expect(DEFAULT_MODEL).toBe("deepseek-flash");
});

test("a known id reads as its name", () => {
  expect(modelName("deepseek-flash")).toBe("Queen Flash");
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
