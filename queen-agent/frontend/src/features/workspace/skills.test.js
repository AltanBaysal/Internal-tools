import { expect, test } from "vitest";

import { SKILLS, skillName } from "./skills.js";

// The design drew four placeholders -- Web search, Deep research, Data & tables, Code -- for a
// product that does something else. These six are the real set, settled with the user.
test("the six skills are the ones that were agreed", () => {
  expect(SKILLS.map((skill) => skill.id)).toEqual([
    "create-scenario",
    "create-character-prompt",
    "split-into-frames",
    "generate-prompts",
    "generate-prompts-plus",
    "verify-prompts",
  ]);
});

test("the skill that checks carries no frame in its name", () => {
  // It reads the material the prompts are made of, not the frames themselves.
  const verify = SKILLS.find((skill) => skill.id === "verify-prompts");
  expect(verify.name).toBe("Verify prompts");
  expect(verify.detail).toBe("Check the structure files against the rules.");
});

test("the skill that splits says frames", () => {
  const split = SKILLS.find((skill) => skill.id === "split-into-frames");
  expect(split.name).toBe("Split into frames");
});

test("each row says what it does", () => {
  for (const skill of SKILLS) {
    expect(skill.name.length).toBeGreaterThan(0);
    expect(skill.detail.length).toBeGreaterThan(0);
  }
});

test("no row promises to stay in the chat any more", () => {
  // Both of them write a file now, and a menu that says otherwise is the app telling a lie.
  expect(SKILLS.filter((skill) => /stays in the chat/i.test(skill.detail))).toEqual([]);
});

test("the rows that write a file say so", () => {
  const writing = SKILLS.filter((skill) => /file/i.test(skill.detail)).map((skill) => skill.id);
  expect(writing).toContain("create-character-prompt");
  expect(writing).toContain("split-into-frames");
});

test("a name is the label, not the id", () => {
  expect(skillName("generate-prompts-plus")).toBe("Generate prompts+");
});

test("nothing selected is the button's own word", () => {
  expect(skillName("")).toBe("Skills");
});
