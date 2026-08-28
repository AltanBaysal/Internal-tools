import { expect, test } from "vitest";

import { chatTitle } from "./chatTitle.js";

test("a short first message is the title, stripped", () => {
  expect(chatTitle("  Write the intro  ")).toBe("Write the intro");
});

test("a long first message is cut at the server's own limit", () => {
  // Pinned to chat_title in chat.py: 42, and the mark only on a message that lost something.
  expect(chatTitle("m".repeat(80))).toBe("m".repeat(42) + "…");
  expect(chatTitle("m".repeat(42))).toBe("m".repeat(42));
});
