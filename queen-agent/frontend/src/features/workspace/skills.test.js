import { expect, test } from "vitest";

import { SKILLS, skillName } from "./skills.js";

// Madde 94 deleted five of the six and said more rows would come. Madde 101 is the first of them.
test("the menu offers the flow and the builder, in that order", () => {
  // The flow comes first: it is the road for somebody with nothing yet, and the builder is for
  // somebody who already has a file.
  expect(SKILLS.map((skill) => skill.id)).toEqual(["start-a-scenario", "generate-prompts-plus"]);
});

test("the two rows tell each other apart", () => {
  // A picker whose rows describe the same job is a picker that says nothing. The builder's line is
  // the one that has to name its condition: a structure file that already exists.
  const builder = SKILLS.find((skill) => skill.id === "generate-prompts-plus");
  expect(builder.detail).toMatch(/already have/i);
});

test("each row says what it does", () => {
  for (const skill of SKILLS) {
    expect(skill.name.length).toBeGreaterThan(0);
    expect(skill.detail.length).toBeGreaterThan(0);
  }
});

test("no row promises to stay in the chat any more", () => {
  // It writes a file, and a menu that says otherwise is the app telling a lie.
  expect(SKILLS.filter((skill) => /stays in the chat/i.test(skill.detail))).toEqual([]);
});

test("a name is the label, not the id", () => {
  expect(skillName("generate-prompts-plus")).toBe("Generate prompts+");
});

test("the flow's name is the label, not the id", () => {
  expect(skillName("start-a-scenario")).toBe("Start a scenario");
});

test("a deleted skill keeps its id on the screen rather than vanishing", () => {
  // An old record can still name one. The button says something rather than going blank.
  expect(skillName("verify-prompts")).toBe("verify-prompts");
});

test("nothing selected is the button's own word", () => {
  expect(skillName("")).toBe("Skills");
});
