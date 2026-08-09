import { fireEvent, render, screen } from "@testing-library/react";
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

test("a suggestion fills the draft and sends nothing", () => {
  const onSubmit = vi.fn();
  const { box } = draw({ onSubmit, suggestions: ["Draft a meeting agenda"] });
  fireEvent.click(screen.getByRole("button", { name: "Draft a meeting agenda" }));
  expect(box.value).toBe("Draft a meeting agenda");
  expect(onSubmit).not.toHaveBeenCalled();
});

test("with no handler attached Enter does nothing and nothing breaks", () => {
  // Wiring onSubmit is Madde 10's job: this phase owns the rules, not the destination.
  const { box } = draw();
  fireEvent.change(box, { target: { value: "hello" } });
  fireEvent.keyDown(box, { key: "Enter" });
  expect(box.value).toBe("hello");
});
