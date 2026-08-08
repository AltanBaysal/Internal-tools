import { describe, it, expect } from "vitest";
import { toRequestBody, systemMessage, formatHttpError } from "./chat.js";

const SKILLS = [
  { name: "plan-yazma", description: "Adımlara böler.", body: "PLAN TALİMATI" },
  { name: "netlestirme", description: "Soruları çıkarır.", body: "SORU TALİMATI" },
];

describe("systemMessage", () => {
  it("asks for Turkish even when there is no skill at all", () => {
    expect(systemMessage([])).toMatch(/Türkçe/);
  });

  it("lists every skill by call name and description", () => {
    const text = systemMessage(SKILLS);
    expect(text).toContain("/plan-yazma: Adımlara böler.");
    expect(text).toContain("/netlestirme: Soruları çıkarır.");
  });

  it("keeps the instruction bodies out, so an unused skill costs nothing", () => {
    expect(systemMessage(SKILLS)).not.toContain("PLAN TALİMATI");
  });
});

describe("toRequestBody", () => {
  it("carries the model and puts the system message first", () => {
    const body = toRequestBody([{ role: "user", content: "selam" }], "grok-4.3");
    expect(body.model).toBe("grok-4.3");
    expect(body.messages[0].role).toBe("system");
    expect(body.messages[1]).toEqual({ role: "user", content: "selam" });
  });

  it("leaves error rows out", () => {
    const body = toRequestBody(
      [
        { role: "user", content: "selam" },
        { role: "error", content: "HTTP 401 — nope" },
        { role: "assistant", content: "merhaba" },
      ],
      "grok-4.3"
    );
    expect(body.messages.slice(1)).toEqual([
      { role: "user", content: "selam" },
      { role: "assistant", content: "merhaba" },
    ]);
  });

  it("does not send fields the screen added", () => {
    const body = toRequestBody([{ role: "user", content: "selam", copied: true }], "grok-4.3");
    expect(body.messages[1]).toEqual({ role: "user", content: "selam" });
  });

  it("sends only the system message for an empty chat", () => {
    const body = toRequestBody([], "grok-4.3");
    expect(body.messages).toHaveLength(1);
    expect(body.messages[0].role).toBe("system");
  });

  it("folds the skill body in front of what the user typed", () => {
    const body = toRequestBody(
      [{ role: "user", content: "taşınacağım", skill: "plan-yazma" }],
      "grok-4.3",
      SKILLS
    );
    expect(body.messages[1]).toEqual({
      role: "user",
      content: "PLAN TALİMATI\n\ntaşınacağım",
    });
  });

  it("keeps an earlier skill call in the transcript, so the instruction accumulates", () => {
    const body = toRequestBody(
      [
        { role: "user", content: "taşınacağım", skill: "plan-yazma" },
        { role: "assistant", content: "1. kutu bul" },
        { role: "user", content: "ikinciyi açıkla" },
      ],
      "grok-4.3",
      SKILLS
    );
    expect(body.messages[1].content).toContain("PLAN TALİMATI");
    expect(body.messages[3]).toEqual({ role: "user", content: "ikinciyi açıkla" });
  });

  it("sends the user's own words alone when the named skill no longer exists", () => {
    const body = toRequestBody(
      [{ role: "user", content: "taşınacağım", skill: "silinmis" }],
      "grok-4.3",
      SKILLS
    );
    expect(body.messages[1]).toEqual({ role: "user", content: "taşınacağım" });
  });
});

const DOSYALAR = [
  { id: 1, projectId: 1, name: "plan.md", content: "PLAN İÇERİĞİ" },
  { id: 2, projectId: 1, name: "sahneler.md", content: "SAHNE İÇERİĞİ" },
];

describe("toRequestBody with files", () => {
  it("puts the file content in front of what the user typed", () => {
    const body = toRequestBody(
      [{ role: "user", content: "@plan.md açıkla", files: ["plan.md"] }],
      "grok-4.3",
      [],
      DOSYALAR
    );
    expect(body.messages[1].content).toBe(
      "`@plan.md` dosyasının içeriği:\n---\nPLAN İÇERİĞİ\n---\n\n@plan.md açıkla"
    );
  });

  it("opens a file once in a conversation, at its first mention", () => {
    const body = toRequestBody(
      [
        { role: "user", content: "@plan.md açıkla", files: ["plan.md"] },
        { role: "assistant", content: "şöyle" },
        { role: "user", content: "@plan.md ikinciyi de", files: ["plan.md"] },
      ],
      "grok-4.3",
      [],
      DOSYALAR
    );
    expect(body.messages[1].content).toContain("PLAN İÇERİĞİ");
    expect(body.messages[3]).toEqual({ role: "user", content: "@plan.md ikinciyi de" });
  });

  it("keeps two different files apart", () => {
    const body = toRequestBody(
      [{ role: "user", content: "iki", files: ["sahneler.md", "plan.md"] }],
      "grok-4.3",
      [],
      DOSYALAR
    );
    const sent = body.messages[1].content;
    expect(sent.indexOf("SAHNE İÇERİĞİ")).toBeLessThan(sent.indexOf("PLAN İÇERİĞİ"));
  });

  it("sends the text alone when the named file was deleted", () => {
    const body = toRequestBody(
      [{ role: "user", content: "@silinmis.md ne", files: ["silinmis.md"] }],
      "grok-4.3",
      [],
      DOSYALAR
    );
    expect(body.messages[1]).toEqual({ role: "user", content: "@silinmis.md ne" });
  });

  it("puts the skill instruction before the file, and both before the request", () => {
    const body = toRequestBody(
      [{ role: "user", content: "yap", skill: "plan-yazma", files: ["plan.md"] }],
      "grok-4.3",
      SKILLS,
      DOSYALAR
    );
    const sent = body.messages[1].content;
    expect(sent.indexOf("PLAN TALİMATI")).toBeLessThan(sent.indexOf("PLAN İÇERİĞİ"));
    expect(sent.indexOf("PLAN İÇERİĞİ")).toBeLessThan(sent.indexOf("yap"));
  });
});

describe("formatHttpError", () => {
  it("joins the status and the body verbatim", () => {
    expect(formatHttpError(401, '{"error":"bad key"}')).toBe('HTTP 401 — {"error":"bad key"}');
  });

  it("passes an empty body through unchanged", () => {
    expect(formatHttpError(500, "")).toBe("HTTP 500 — ");
  });
});
