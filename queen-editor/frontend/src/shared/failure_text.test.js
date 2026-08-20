import { describe, expect, it } from "vitest";

import { failureText } from "./failure_text.js";

describe("failureText", () => {
  it("puts the evidence under the sentence", () => {
    const err = new Error("Sunucuya ulaşılamadı — bağlantıyı kontrol et.");
    err.evidence = "GET /api/status\nZaman aşımı (10 sn)";

    // One string, two jobs: the first line is read on the panel, the rest is what the copy button
    // hands over. The panel splits them at this newline.
    expect(failureText(err)).toBe(
      "Sunucuya ulaşılamadı — bağlantıyı kontrol et.\nGET /api/status\nZaman aşımı (10 sn)");
  });

  it("says just the sentence when there is no evidence", () => {
    // Not every failure comes through the fetch wrapper. An empty line under one of those would
    // read as proof that went missing.
    expect(failureText(new Error("Sıra kaydedilemedi."))).toBe("Sıra kaydedilemedi.");
  });
});
