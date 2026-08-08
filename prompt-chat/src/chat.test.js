import { describe, it, expect } from "vitest";
import { toRequestBody, formatHttpError } from "./chat.js";

describe("toRequestBody", () => {
  it("carries the model and the messages", () => {
    const body = toRequestBody([{ role: "user", content: "selam" }], "grok-4.3");
    expect(body).toEqual({
      model: "grok-4.3",
      messages: [{ role: "user", content: "selam" }],
    });
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
    expect(body.messages).toEqual([
      { role: "user", content: "selam" },
      { role: "assistant", content: "merhaba" },
    ]);
  });

  it("does not send fields the screen added", () => {
    const body = toRequestBody([{ role: "user", content: "selam", copied: true }], "grok-4.3");
    expect(body.messages[0]).toEqual({ role: "user", content: "selam" });
  });

  it("gives an empty list for an empty chat", () => {
    expect(toRequestBody([], "grok-4.3").messages).toEqual([]);
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
