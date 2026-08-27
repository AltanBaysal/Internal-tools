import { expect, test } from "vitest";

import { SKILLS, skillName } from "./skills.js";

// Madde 94: five of the six were deleted. What is left is the one that builds a prompt from parts,
// and the menu is one row -- not none, because having no skill selected is an ordinary state and
// more rows will come.
test("the one skill left is the one that builds", () => {
  expect(SKILLS.map((skill) => skill.id)).toEqual(["generate-prompts-plus"]);
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

test("a deleted skill keeps its id on the screen rather than vanishing", () => {
  // An old record can still name one. The button says something rather than going blank.
  expect(skillName("verify-prompts")).toBe("verify-prompts");
});

test("nothing selected is the button's own word", () => {
  expect(skillName("")).toBe("Skills");
});
