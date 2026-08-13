import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { RawOutput } from "./RawOutput.jsx";

// What a real failure looks like: one useful line, then sixty nobody reads on screen.
const LONG = ["POST /prompt -> node_errors", "{"]
  .concat(Array.from({ length: 60 }, (_, i) => `  "line ${i}": "value",`))
  .concat(["}"])
  .join("\n");

// jsdom ships no clipboard, so the test supplies one and watches what it is handed.
function stubClipboard(answer) {
  const writeText = vi.fn(() => answer);
  Object.defineProperty(navigator, "clipboard", { value: { writeText }, configurable: true });
  return writeText;
}

const box = () => document.querySelector("[data-raw]");
const copy = () => screen.getByRole("button", { name: /Kopyala/ });

describe("RawOutput", () => {
  it("keeps a long output inside its own box", () => {
    // jsdom does not scroll, so what can be tested is that the rule to scroll is there. Whether it
    // really scrolls is the Colab round's answer -- and the rule is what kept disappearing.
    render(<RawOutput text={LONG} />);

    expect(box().style.overflowY).toBe("auto");
    expect(box().style.maxHeight).not.toBe("");
  });

  it("shows the whole output rather than a cut of it", () => {
    // The repo rule: print what the service actually said. Folding is allowed, losing is not.
    render(<RawOutput text={LONG} />);

    expect(box().textContent).toBe(LONG);
  });

  it("copies exactly what it shows", async () => {
    const writeText = stubClipboard(Promise.resolve());
    render(<RawOutput text={LONG} />);

    fireEvent.click(copy());

    expect(writeText).toHaveBeenCalledWith(LONG);
    expect(await screen.findByText("Kopyalandı")).toBeTruthy();
  });

  it("says so when the clipboard refuses", async () => {
    // Silence would leave the user believing they had the text. The box is still selectable, so
    // saying it failed is also saying take it by hand.
    stubClipboard(Promise.reject(new Error("denied")));
    render(<RawOutput text={LONG} />);

    fireEvent.click(copy());

    expect(await screen.findByText("Kopyalanamadı")).toBeTruthy();
  });
});
