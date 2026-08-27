import { fireEvent, render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import PermissionCard from "./PermissionCard.jsx";

// Madde 99 asked the question; this is where it is seen. The card stands in the transcript while
// the turn is paused, and the two buttons are the only way past it apart from Stop.

const ARGS = '{"name": "plan.md", "content": "# Plan"}';

test("it names the tool that wants to run", () => {
  render(<PermissionCard tool="create_file" args={ARGS} />);
  expect(screen.getByText("QueenAgent wants to run create_file")).toBeTruthy();
});

test("it shows the arguments as they came", () => {
  // Raw, unparsed. Approving a write without seeing what is being written is approving nothing,
  // and a second parser beside run_tool's would drift from it on the first change to either.
  render(<PermissionCard tool="create_file" args={ARGS} />);
  expect(screen.getByText(ARGS)).toBeTruthy();
});

test("allowing hands nothing up but the yes", () => {
  const onAllow = vi.fn();
  render(<PermissionCard tool="create_file" args={ARGS} onAllow={onAllow} />);
  fireEvent.click(screen.getByText("Allow"));
  expect(onAllow).toHaveBeenCalledWith();
});

test("denying carries what is in the box", () => {
  // A refusal with nothing written on it is a wall the model walks into again, so the box is next
  // to the button that needs it.
  const onDeny = vi.fn();
  render(<PermissionCard tool="create_file" args={ARGS} onDeny={onDeny} />);
  fireEvent.change(screen.getByPlaceholderText("Why not? (optional)"), {
    target: { value: "that file is mine" },
  });
  fireEvent.click(screen.getByText("Deny"));
  expect(onDeny).toHaveBeenCalledWith("that file is mine");
});

test("an empty box still denies", () => {
  // Optional means optional: a button that did nothing until a sentence was typed would be a
  // second question nobody asked.
  const onDeny = vi.fn();
  render(<PermissionCard tool="create_file" args={ARGS} onDeny={onDeny} />);
  fireEvent.click(screen.getByText("Deny"));
  expect(onDeny).toHaveBeenCalledWith("");
});
