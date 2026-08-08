import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import Message from "./Message.jsx";

const copyButton = () => screen.getByRole("button", { name: /Kopyala/ });

// Replacing the whole navigator object would drop userAgent and friends that React and Testing
// Library read; defining just the one property keeps the rest intact.
function stubClipboard(writeText) {
  Object.defineProperty(navigator, "clipboard", { value: { writeText }, configurable: true });
}

describe("the copy button", () => {
  it("appears only on replies", () => {
    const { rerender } = render(<Message role="user" content="selam" />);
    expect(screen.queryByRole("button")).toBeNull();

    rerender(<Message role="error" content="HTTP 500 — patladı" />);
    expect(screen.queryByRole("button")).toBeNull();

    rerender(<Message role="assistant" content="merhaba" />);
    expect(copyButton()).toBeTruthy();
  });

  it("writes the whole text to the clipboard, line breaks included", async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    stubClipboard(writeText);

    // A JSX expression, not an attribute string: content="a\nb" would pass a literal backslash-n.
    const iki = "birinci satır\nikinci satır";
    render(<Message role="assistant" content={iki} />);
    fireEvent.click(copyButton());

    await waitFor(() => expect(writeText).toHaveBeenCalledWith(iki));
  });

  it("acknowledges a successful copy", async () => {
    stubClipboard(vi.fn().mockResolvedValue(undefined));

    render(<Message role="assistant" content="merhaba" />);
    fireEvent.click(copyButton());

    expect(await screen.findByRole("button", { name: "Kopyalandı" })).toBeTruthy();
  });

  it("shows the browser's own reason when the clipboard refuses", async () => {
    stubClipboard(vi.fn().mockRejectedValue(new Error("izin yok")));

    render(<Message role="assistant" content="merhaba" />);
    fireEvent.click(copyButton());

    expect(await screen.findByRole("button", { name: /izin yok/ })).toBeTruthy();
  });
});
