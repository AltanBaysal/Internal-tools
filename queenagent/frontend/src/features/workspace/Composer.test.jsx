import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import Composer from "./Composer.jsx";

function draw(props = {}) {
  render(<Composer rows={3} placeholder="Ask anything" action="Send" {...props} />);
  return {
    box: screen.getByPlaceholderText("Ask anything"),
    button: screen.getByRole("button", { name: "Send" }),
  };
}

test("an empty draft disables the button", () => {
  expect(draw().button.disabled).toBe(true);
});

test("whitespace alone still counts as empty", () => {
  const { box, button } = draw();
  fireEvent.change(box, { target: { value: "   " } });
  expect(button.disabled).toBe(true);
});

test("typing wakes the button up", () => {
  const { box, button } = draw();
  fireEvent.change(box, { target: { value: "hello" } });
  expect(button.disabled).toBe(false);
});

test("Enter sends the trimmed draft", () => {
  const onSubmit = vi.fn();
  const { box } = draw({ onSubmit });
  fireEvent.change(box, { target: { value: "  hello  " } });
  fireEvent.keyDown(box, { key: "Enter" });
  expect(onSubmit).toHaveBeenCalledWith("hello");
});

test("Shift+Enter is a newline, not a send", () => {
  const onSubmit = vi.fn();
  const { box } = draw({ onSubmit });
  fireEvent.change(box, { target: { value: "hello" } });
  fireEvent.keyDown(box, { key: "Enter", shiftKey: true });
  expect(onSubmit).not.toHaveBeenCalled();
});

test("the draft is cleared once it has been sent", () => {
  const { box } = draw({ onSubmit: vi.fn() });
  fireEvent.change(box, { target: { value: "hello" } });
  fireEvent.keyDown(box, { key: "Enter" });
  expect(box.value).toBe("");
});

test("nothing fills the draft for the user", () => {
  // The three prompt pills go with the screen that held them; the composer offers no wording.
  const { box } = draw({ suggestions: ["Draft a meeting agenda"] });
  expect(screen.queryByRole("button", { name: "Draft a meeting agenda" })).toBeNull();
  expect(box.value).toBe("");
});

// FOUNDATION's first principle: no scenario may lose work the user already did. A refused message
// used to take the sentence with it -- the box had cleared and the optimistic bubble was withdrawn.
test("a refused message comes back to the box", async () => {
  const onSubmit = vi.fn().mockRejectedValue(new Error("a chat needs text"));
  const { box } = draw({ onSubmit });
  fireEvent.change(box, { target: { value: "hello" } });
  fireEvent.keyDown(box, { key: "Enter" });
  await waitFor(() => expect(box.value).toBe("hello"));
});

test("what the user has started writing since is not overwritten", async () => {
  let refuse;
  const onSubmit = vi.fn().mockReturnValue(new Promise((_, reject) => (refuse = reject)));
  const { box } = draw({ onSubmit });
  fireEvent.change(box, { target: { value: "hello" } });
  fireEvent.keyDown(box, { key: "Enter" });
  fireEvent.change(box, { target: { value: "second thought" } });
  refuse(new Error("no"));
  await waitFor(() => expect(box.value).toBe("second thought"));
});

test("an accepted message does not come back", async () => {
  const onSubmit = vi.fn().mockResolvedValue(undefined);
  const { box } = draw({ onSubmit });
  fireEvent.change(box, { target: { value: "hello" } });
  fireEvent.keyDown(box, { key: "Enter" });
  await waitFor(() => expect(box.value).toBe(""));
});

test("with no handler attached Enter does nothing and nothing breaks", () => {
  // Wiring onSubmit is Madde 10's job: this phase owns the rules, not the destination.
  const { box } = draw();
  fireEvent.change(box, { target: { value: "hello" } });
  fireEvent.keyDown(box, { key: "Enter" });
  expect(box.value).toBe("hello");
});
