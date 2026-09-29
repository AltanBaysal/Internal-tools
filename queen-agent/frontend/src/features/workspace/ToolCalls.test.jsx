import { fireEvent, render, screen } from "@testing-library/react";
import { expect, test } from "vitest";

import ToolCalls from "./ToolCalls.jsx";

// Madde 344 moved the door out of ChatScreen.jsx. Every branch of it is still held by the screen's
// own tests; these hold that it draws from its own file, alone.

const CALLS = [
  { tool: "list_files", target: "", outcome: "No files" },
  { tool: "read_file", target: "aylin.json", outcome: "45 lines" },
];

test("a turn that called nothing draws no door", () => {
  const { container } = render(<ToolCalls calls={[]} />);
  expect(container.firstChild).toBeNull();
});

test("shut it counts the steps, and open it lists them", () => {
  const { container } = render(<ToolCalls calls={CALLS} />);
  fireEvent.click(screen.getByRole("button", { name: /2 steps/ }));
  const heads = [...container.querySelectorAll(".tool-call__head")].map((head) => head.textContent);
  expect(heads).toEqual(["⏺ list_files", "⏺ read_file(aylin.json)"]);
  expect(screen.getByText("45 lines")).toBeTruthy();
});

test("while the turn runs the shut door names the last call", () => {
  render(<ToolCalls calls={CALLS} running />);
  expect(screen.getByRole("button", { name: /read_file\(aylin\.json\)/ })).toBeTruthy();
});
