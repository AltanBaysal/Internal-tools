import { expect, test } from "vitest";

import { SKILLS, skillName } from "./skills.js";

// The design drew four placeholders -- Web search, Deep research, Data & tables, Code -- for a
// product that does something else. These six are the real set, settled with the user.
test("the six skills are the ones that were agreed", () => {
  expect(SKILLS.map((skill) => skill.id)).toEqual([
    "create-scenario",
    "create-character-prompt",
    "split-into-shots",
    "generate-prompts",
    "generate-prompts-plus",
    "verify-shots",
  ]);
});

test("each row says what it does", () => {
  for (const skill of SKILLS) {
    expect(skill.name.length).toBeGreaterThan(0);
    expect(skill.detail.length).toBeGreaterThan(0);
  }
});

test("the two that produce nothing on disk say so in the menu", () => {
  // The most surprising thing about them, so the line has to carry it.
  const staying = SKILLS.filter((skill) => /stays in the chat/i.test(skill.detail));
  expect(staying.map((skill) => skill.id)).toEqual([
    "create-character-prompt",
    "split-into-shots",
  ]);
});

test("a name is the label, not the id", () => {
  expect(skillName("generate-prompts-plus")).toBe("Generate prompts+");
});

test("nothing selected is the button's own word", () => {
  expect(skillName("")).toBe("Skills");
});
