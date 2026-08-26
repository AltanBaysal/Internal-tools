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

// karar 1 settled the foot's order: Skills · model · Send. The box does not know what goes in
// there, only that it comes before Send.
test("the foot has room to the left of Send", () => {
  const { container } = render(<Composer action="Send" foot={<button type="button">Grok 4.5</button>} />);
  const buttons = [...container.querySelectorAll(".composer__foot button")];
  expect(buttons.map((button) => button.textContent)).toEqual(["Grok 4.5", "↑"]);
  // Madde 80 took the word off the button, so the order alone no longer says which one it is.
  expect(buttons[1].getAttribute("aria-label")).toBe("Send");
});

test("with nothing to put there the foot is Send alone", () => {
  const { container } = render(<Composer action="Send" />);
  expect(container.querySelectorAll(".composer__foot button").length).toBe(1);
});

// Madde 92: the foot grows a second end. Skills, the model's name and Send have been on the right
// since karar 1; the gauge goes to the other one, because it is read rather than pressed and
// standing among the three would make it look like a fourth thing to press.
test("the gauge stands at the far end of the foot from Send", () => {
  const { container } = render(
    <Composer
      action="Send"
      gauge={<span data-testid="gauge" />}
      foot={<button type="button">Grok 4.5</button>}
    />,
  );
  const foot = container.querySelector(".composer__foot");
  expect(foot.firstChild.className).toBe("composer__gauge");
  expect(foot.querySelector('[data-testid="gauge"]')).toBeTruthy();
});

// --- one button, two jobs (Madde 79) -------------------------------------------------------------
//
// While an answer is running there is nothing to send, so the button that sends is the one free to
// stop. Madde 67 put a second button beside it; this replaces both with one.

test("while an answer runs the button stops instead of sending", () => {
  render(<Composer action="Send" running onStop={vi.fn()} />);
  expect(screen.getByRole("button", { name: "Stop" })).toBeTruthy();
  expect(screen.queryByRole("button", { name: "Send" })).toBeNull();
});

test("stopping does not wait for a draft", () => {
  // An empty draft is what blocks sending. Blocking a stop with it would make the control useless
  // in the very case it exists for -- nothing has been typed and the answer is running away.
  const onStop = vi.fn();
  render(<Composer action="Send" running onStop={onStop} />);
  const button = screen.getByRole("button", { name: "Stop" });
  expect(button.disabled).toBe(false);
  fireEvent.click(button);
  expect(onStop).toHaveBeenCalled();
});

test("pressing it while an answer runs sends nothing", () => {
  // Two jobs on one button, and the wrong one firing would send a sentence the user was still
  // writing.
  const onSubmit = vi.fn();
  render(
    <Composer
      action="Send"
      placeholder="Ask anything"
      running
      onStop={vi.fn()}
      onSubmit={onSubmit}
    />,
  );
  fireEvent.change(screen.getByPlaceholderText("Ask anything"), { target: { value: "half a th" } });
  fireEvent.click(screen.getByRole("button", { name: "Stop" }));
  expect(onSubmit).not.toHaveBeenCalled();
});

test("with nothing running the button is what it always was", () => {
  const { button } = draw();
  expect(button.disabled).toBe(true);
  expect(screen.queryByRole("button", { name: "Stop" })).toBeNull();
});

// --- a mark instead of a word (Madde 80) ---------------------------------------------------------
//
// What the button does is unchanged; what stands on it is not. The name moves to aria-label, so it
// stops being visible rather than stopping existing. The proof of that is the rest of this file:
// every test above finds the button by { name: "Send" }.

test("the button carries an arrow, not the word", () => {
  const { button } = draw();
  expect(button.textContent).toBe("↑");
});

test("hovering says what the arrow does", () => {
  // A mark has to explain itself, and the mouse is the only place left to ask.
  expect(draw().button.getAttribute("title")).toBe("Send");
});

test("while an answer runs the arrow becomes a stop", () => {
  render(<Composer action="Send" running onStop={vi.fn()} />);
  const button = screen.getByRole("button", { name: "Stop" });
  expect(button.textContent).toBe("⏹");
  expect(button.getAttribute("title")).toBe("Stop");
});

test("the project screen's button is the same arrow under another name", () => {
  // Both mean "send what I wrote", so the mark is the same. What differs is the name.
  render(<Composer action="Start" placeholder="Start a new chat in this project..." />);
  expect(screen.getByRole("button", { name: "Start" }).textContent).toBe("↑");
});
