import { fireEvent, render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import EditMessage from "./EditMessage.jsx";

// Madde 344: the field a question is corrected in, drawn from its own file.

test("Enter confirms the sentence without its edges", () => {
  const onConfirm = vi.fn();
  render(<EditMessage text="Write the intro" onConfirm={onConfirm} onCancel={vi.fn()} />);
  const field = screen.getByRole("textbox");
  fireEvent.change(field, { target: { value: "  Write the outro  " } });
  fireEvent.keyDown(field, { key: "Enter" });
  expect(onConfirm).toHaveBeenCalledWith("Write the outro");
});

test("Escape gives up", () => {
  const onCancel = vi.fn();
  render(<EditMessage text="Write the intro" onConfirm={vi.fn()} onCancel={onCancel} />);
  fireEvent.keyDown(screen.getByRole("textbox"), { key: "Escape" });
  expect(onCancel).toHaveBeenCalled();
});

test("the field opens as tall as the sentence it corrects", () => {
  // Madde 504: it used to open at two lines whatever it held. jsdom lays nothing out, so the
  // sentence's height is declared; the measuring itself is useGrowingField's own test.
  vi.spyOn(Element.prototype, "scrollHeight", "get").mockReturnValue(400);
  try {
    render(<EditMessage text="Write the intro" onConfirm={vi.fn()} onCancel={vi.fn()} />);
    expect(screen.getByRole("textbox").style.height).toBe("400px");
  } finally {
    vi.restoreAllMocks();
  }
});

test("an empty draft cannot be confirmed", () => {
  render(<EditMessage text="Write the intro" onConfirm={vi.fn()} onCancel={vi.fn()} />);
  fireEvent.change(screen.getByRole("textbox"), { target: { value: "   " } });
  expect(screen.getByRole("button", { name: "Confirm edit" }).disabled).toBe(true);
});
