import { describe, it, expect } from "vitest";
import { findSkill, loadSkills, matchSkills, parseSkill, splitSkillPrefix } from "./skills.js";

const gecerli = `---
name: plan-yazma
description: Hedefi adımlara böler.
---

Hedefi uygulanabilir adımlara böl.
`;

describe("parseSkill", () => {
  it("reads the two required fields and the body", () => {
    expect(parseSkill(gecerli)).toEqual({
      name: "plan-yazma",
      description: "Hedefi adımlara böler.",
      body: "Hedefi uygulanabilir adımlara böl.",
    });
  });

  it("joins a description wrapped over several lines", () => {
    const raw = `---
name: netlestirme
description: Belirsiz bir isteği alır
             ve soruları çıkarır.
---
gövde`;
    expect(parseSkill(raw).description).toBe("Belirsiz bir isteği alır ve soruları çıkarır.");
  });

  it("ignores fields the app does not use", () => {
    const raw = `---
name: ornek
description: Bir şey yapar.
license: Apache-2.0
---
gövde`;
    expect(parseSkill(raw)).toEqual({ name: "ornek", description: "Bir şey yapar.", body: "gövde" });
  });

  it("keeps blank lines and markdown inside the body", () => {
    const raw = `---
name: ornek
description: Bir şey yapar.
---
## Başlık

- madde`;
    expect(parseSkill(raw).body).toBe("## Başlık\n\n- madde");
  });

  it("refuses a file that does not open with a frontmatter fence", () => {
    expect(() => parseSkill("name: ornek\n")).toThrow(/frontmatter yok/);
  });

  it("refuses a frontmatter that is never closed", () => {
    expect(() => parseSkill("---\nname: ornek\n")).toThrow(/kapanmamış/);
  });

  it("refuses a name with characters the standard forbids", () => {
    for (const kotu of ["Plan-Yazma", "-plan", "plan-", "plan--yazma", "plan yazma", ""]) {
      const raw = `---\nname: ${kotu}\ndescription: Bir şey.\n---\ngövde`;
      expect(() => parseSkill(raw)).toThrow(/geçersiz name/);
    }
  });

  it("refuses a name longer than 64 characters", () => {
    const raw = `---\nname: ${"a".repeat(65)}\ndescription: Bir şey.\n---\ngövde`;
    expect(() => parseSkill(raw)).toThrow(/geçersiz name/);
  });

  it("refuses a missing or oversized description", () => {
    expect(() => parseSkill("---\nname: ornek\n---\ngövde")).toThrow(/geçersiz description/);
    const uzun = `---\nname: ornek\ndescription: ${"a".repeat(1025)}\n---\ngövde`;
    expect(() => parseSkill(uzun)).toThrow(/geçersiz description/);
  });

  it("names the offending value in the error, so the settings panel can show it", () => {
    const raw = `---\nname: Plan\ndescription: Bir şey.\n---\ngövde`;
    expect(() => parseSkill(raw)).toThrow(/"Plan"/);
  });
});

const dosya = (name) => `---\nname: ${name}\ndescription: ${name} yapar.\n---\n${name} gövdesi`;

describe("loadSkills", () => {
  it("returns one skill per folder, sorted by name", () => {
    const { skills } = loadSkills({
      "../skills/plan-yazma/SKILL.md": dosya("plan-yazma"),
      "../skills/netlestirme/SKILL.md": dosya("netlestirme"),
    });
    expect(skills.map((s) => s.name)).toEqual(["netlestirme", "plan-yazma"]);
    expect(skills[0].body).toBe("netlestirme gövdesi");
  });

  it("rejects a skill whose name disagrees with its folder", () => {
    const { skills, errors } = loadSkills({
      "../skills/plan-yazma/SKILL.md": dosya("baska-ad"),
    });
    expect(skills).toEqual([]);
    expect(errors[0].path).toBe("../skills/plan-yazma/SKILL.md");
    expect(errors[0].reason).toMatch(/klasör adı/);
  });

  it("drops only the broken file and keeps the rest working", () => {
    const { skills, errors } = loadSkills({
      "../skills/bozuk/SKILL.md": "frontmatter'sız metin",
      "../skills/plan-yazma/SKILL.md": dosya("plan-yazma"),
    });
    expect(skills.map((s) => s.name)).toEqual(["plan-yazma"]);
    expect(errors).toHaveLength(1);
    expect(errors[0].reason).toMatch(/frontmatter yok/);
  });

  it("gives two empty lists when there are no files at all", () => {
    expect(loadSkills({})).toEqual({ skills: [], errors: [] });
  });
});

const LISTE = [
  { name: "netlestirme", description: "Soruları çıkarır.", body: "A" },
  { name: "plan-yazma", description: "Adımlara böler.", body: "B" },
];

describe("findSkill", () => {
  it("finds an exact name", () => {
    expect(findSkill(LISTE, "plan-yazma").body).toBe("B");
  });

  it("returns null rather than undefined for an unknown name", () => {
    expect(findSkill(LISTE, "yok")).toBeNull();
  });
});

describe("matchSkills", () => {
  it("lists everything for an empty query", () => {
    expect(matchSkills(LISTE, "")).toHaveLength(2);
  });

  it("matches anywhere in the name, not only at the start", () => {
    expect(matchSkills(LISTE, "yazma").map((s) => s.name)).toEqual(["plan-yazma"]);
  });

  it("ignores case", () => {
    expect(matchSkills(LISTE, "PLAN").map((s) => s.name)).toEqual(["plan-yazma"]);
  });

  it("returns an empty list when nothing matches", () => {
    expect(matchSkills(LISTE, "zzz")).toEqual([]);
  });
});

describe("splitSkillPrefix", () => {
  it("splits a leading slash name from the rest", () => {
    expect(splitSkillPrefix("/plan-yazma hafta sonu taşınacağım")).toEqual({
      name: "plan-yazma",
      content: "hafta sonu taşınacağım",
    });
  });

  it("accepts a newline between the name and the text", () => {
    expect(splitSkillPrefix("/plan-yazma\nilk satır\nikinci")).toEqual({
      name: "plan-yazma",
      content: "ilk satır\nikinci",
    });
  });

  it("reports an empty body when only the name was typed", () => {
    expect(splitSkillPrefix("/plan-yazma")).toEqual({ name: "plan-yazma", content: "" });
  });

  it("leaves a slash in the middle of the text alone", () => {
    const cumle = "src/App.jsx dosyasına bak";
    expect(splitSkillPrefix(cumle)).toEqual({ name: null, content: cumle });
  });

  it("leaves a date written with slashes alone", () => {
    expect(splitSkillPrefix("8/8/2026 tarihinde")).toEqual({
      name: null,
      content: "8/8/2026 tarihinde",
    });
  });

  it("still recognises a wrongly-cased name, so the caller can say it does not exist", () => {
    expect(splitSkillPrefix("/Plan-Yazma bir şey")).toEqual({
      name: "Plan-Yazma",
      content: "bir şey",
    });
  });
});
