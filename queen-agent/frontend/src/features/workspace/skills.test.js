import { expect, test } from "vitest";

import { SKILLS, skillName } from "./skills.js";

// Madde 94 deleted five of the six and said more rows would come. Madde 101 is the first of them.
test("the menu offers the flow and the editor, in that order", () => {
  // The flow comes first: it is the road for somebody with nothing yet, and since Madde 186 it
  // runs the whole way to the prompts. The second row is for somebody who has them already.
  expect(SKILLS.map((skill) => skill.id)).toEqual(["start-a-scenario", "edit-prompts"]);
});

test("the two rows tell each other apart", () => {
  // A picker whose rows describe the same job is a picker that says nothing. The editor's line is
  // the one that has to name its condition: prompts that already exist.
  const editor = SKILLS.find((skill) => skill.id === "edit-prompts");
  expect(editor.detail).toMatch(/already/i);
});

test("the flow's row says it goes all the way to the prompts", () => {
  // Madde 186 removed the handoff. A row promising only a scene list would send somebody back to
  // the menu for a second skill that no longer exists.
  const flow = SKILLS.find((skill) => skill.id === "start-a-scenario");
  expect(flow.detail).toMatch(/prompt/i);
});

test("the editor's row says it changes what is there", () => {
  // A row that only says "build" sends somebody looking for an editor; a row that only says
  // "prompts" reads exactly like the first one.
  const editor = SKILLS.find((skill) => skill.id === "edit-prompts");
  expect(editor.detail).toMatch(/fix|change/i);
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
  expect(skillName("edit-prompts")).toBe("Edit prompts");
});

test("the name that was renamed away keeps its id on the screen", () => {
  // Madde 186. A chat sent under the old name still opens, and the button says something rather
  // than going blank -- the same road every deleted skill takes.
  expect(skillName("generate-prompts-plus")).toBe("generate-prompts-plus");
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
