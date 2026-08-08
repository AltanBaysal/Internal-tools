import { describe, it, expect } from "vitest";
import { skills, errors } from "./skillSource.js";

// This is the one test that reads the real files in the repo rather than a fixture: it is the only
// way to catch a glob pattern that silently matches nothing, or a shipped skill that stopped being
// valid.
describe("the skills shipped with the app", () => {
  it("loads every folder under skills/ with no errors", () => {
    expect(errors).toEqual([]);
    expect(skills.length).toBeGreaterThanOrEqual(2);
  });

  it("ships netlestirme and plan-yazma", () => {
    expect(skills.map((s) => s.name)).toEqual(
      expect.arrayContaining(["netlestirme", "plan-yazma"])
    );
  });

  it("gives every shipped skill a body worth sending", () => {
    for (const skill of skills) {
      expect(skill.body.length).toBeGreaterThan(80);
    }
  });
});
