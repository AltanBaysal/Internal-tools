import { act, fireEvent, render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import CopyButton from "./CopyButton.jsx";

// The three Copy buttons are this one component, so what a press leaves is tested once, here. The
// words and the 2.5 seconds are FilePanel.test.jsx's; this is the mark the stylesheet colours by --
// data-said, green for yes and red words for no (item 444, the design's 219).
function stubClipboard(answer) {
  const writeText = vi.fn(() => answer);
  Object.defineProperty(navigator, "clipboard", { value: { writeText }, configurable: true });
  return writeText;
}

test("a copy that worked marks the button yes", async () => {
  stubClipboard(Promise.resolve());
  render(<CopyButton text="the body" className="reader__copy" />);
  fireEvent.click(screen.getByRole("button", { name: "Copy" }));
  const said = await screen.findByRole("button", { name: "Copied" });
  expect(said.dataset.said).toBe("yes");
});

test("a copy that failed marks it no", async () => {
  stubClipboard(Promise.reject(new Error("denied")));
  render(<CopyButton text="the body" className="reader__copy" />);
  fireEvent.click(screen.getByRole("button", { name: "Copy" }));
  const said = await screen.findByRole("button", { name: "Could not copy" });
  expect(said.dataset.said).toBe("no");
});

test("once the answer fades the mark goes with it", async () => {
  vi.useFakeTimers();
  try {
    stubClipboard(Promise.resolve());
    render(<CopyButton text="the body" className="reader__copy" />);
    fireEvent.click(screen.getByRole("button", { name: "Copy" }));
    await act(() => vi.advanceTimersByTimeAsync(2500));
    expect(screen.getByRole("button", { name: "Copy" }).dataset.said).toBeUndefined();
  } finally {
    vi.useRealTimers();
  }
});

test("a dimmed Copy never turns green, even with a copy still being answered", async () => {
  // The open file's header: Copy pressed on one file, then another opened while Copied still
  // shows. The new file is still being read, so there is nothing to copy -- and a dimmed button
  // saying Copied, in green, would claim a copy of a file that is not there yet.
  stubClipboard(Promise.resolve());
  const { rerender } = render(<CopyButton text="the body" className="reader__copy" />);
  fireEvent.click(screen.getByRole("button", { name: "Copy" }));
  await screen.findByRole("button", { name: "Copied" });
  rerender(<CopyButton text="" className="reader__copy" />);
  const button = screen.getByRole("button", { name: "Copy" });
  expect(button.disabled).toBe(true);
  expect(button.dataset.said).toBeUndefined();
});

test("a Copy with nothing to copy is dimmed and unmarked", () => {
  render(<CopyButton text="" className="reader__copy" />);
  const button = screen.getByRole("button", { name: "Copy" });
  expect(button.disabled).toBe(true);
  expect(button.dataset.said).toBeUndefined();
});

test("the answer belongs to the text that was copied, not to the next one", async () => {
  // The header keeps one button while files come and go: copy one file, open another that arrives
  // inside the 2.5 seconds, and Copied in green would claim a copy of a file never copied.
  stubClipboard(Promise.resolve());
  const { rerender } = render(<CopyButton text="file A" className="reader__copy" />);
  fireEvent.click(screen.getByRole("button", { name: "Copy" }));
  await screen.findByRole("button", { name: "Copied" });
  rerender(<CopyButton text="file B" className="reader__copy" />);
  const button = screen.getByRole("button", { name: "Copy" });
  expect(button.disabled).toBe(false);
  expect(button.dataset.said).toBeUndefined();
});
