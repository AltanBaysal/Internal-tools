import { describe, it, expect } from "vitest";
import { toRequestBody, formatHttpError } from "./chat.js";

describe("toRequestBody", () => {
  it("modeli ve mesajları taşır", () => {
    const body = toRequestBody([{ role: "user", content: "selam" }], "grok-4.3");
    expect(body).toEqual({
      model: "grok-4.3",
      messages: [{ role: "user", content: "selam" }],
    });
  });

  it("hata satırlarını dışarıda bırakır", () => {
    const body = toRequestBody(
      [
        { role: "user", content: "selam" },
        { role: "error", content: "HTTP 401 — nope" },
        { role: "assistant", content: "merhaba" },
      ],
      "grok-4.3"
    );
    expect(body.messages).toEqual([
      { role: "user", content: "selam" },
      { role: "assistant", content: "merhaba" },
    ]);
  });

  it("ekranın kendi alanlarını göndermez", () => {
    const body = toRequestBody([{ role: "user", content: "selam", copied: true }], "grok-4.3");
    expect(body.messages[0]).toEqual({ role: "user", content: "selam" });
  });

  it("boş sohbette boş liste verir", () => {
    expect(toRequestBody([], "grok-4.3").messages).toEqual([]);
  });
});

describe("formatHttpError", () => {
  it("kodu ve gövdeyi olduğu gibi birleştirir", () => {
    expect(formatHttpError(401, '{"error":"bad key"}')).toBe('HTTP 401 — {"error":"bad key"}');
  });

  it("boş gövdeyi de olduğu gibi geçirir", () => {
    expect(formatHttpError(500, "")).toBe("HTTP 500 — ");
  });
});
