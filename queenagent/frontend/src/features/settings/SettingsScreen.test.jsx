import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import SettingsScreen from "./SettingsScreen.jsx";

test("it names itself and the one thing it holds", () => {
  render(<SettingsScreen apiKey="" onSave={vi.fn()} />);
  expect(screen.getByRole("heading", { level: 1 }).textContent).toBe("Settings");
  expect(screen.getByText("XAI API KEY")).toBeTruthy();
});

test("the key is shown as it was typed", () => {
  // The user's own machine and their own key: a masked one they cannot read back would answer less.
  render(<SettingsScreen apiKey="xai-abc123" onSave={vi.fn()} />);
  expect(screen.getByLabelText("XAI API KEY").value).toBe("xai-abc123");
});

test("Save sends what is in the box", () => {
  const onSave = vi.fn().mockResolvedValue();
  render(<SettingsScreen apiKey="" onSave={onSave} />);
  fireEvent.change(screen.getByLabelText("XAI API KEY"), { target: { value: "xai-new" } });
  fireEvent.click(screen.getByRole("button", { name: "Save" }));
  expect(onSave).toHaveBeenCalledWith("xai-new");
});

test("saving says so, and typing again takes the word back", async () => {
  const onSave = vi.fn().mockResolvedValue();
  render(<SettingsScreen apiKey="" onSave={onSave} />);
  fireEvent.click(screen.getByRole("button", { name: "Save" }));
  await waitFor(() => expect(screen.getByText("Saved.")).toBeTruthy());

  // "Saved" is a moment rather than a state: the box no longer holds what was saved.
  fireEvent.change(screen.getByLabelText("XAI API KEY"), { target: { value: "xai-other" } });
  expect(screen.queryByText("Saved.")).toBeNull();
});

test("an empty key can be saved, because that is how one is taken out", () => {
  const onSave = vi.fn().mockResolvedValue();
  render(<SettingsScreen apiKey="xai-abc123" onSave={onSave} />);
  fireEvent.change(screen.getByLabelText("XAI API KEY"), { target: { value: "" } });
  fireEvent.click(screen.getByRole("button", { name: "Save" }));
  expect(onSave).toHaveBeenCalledWith("");
});

test("a refused save repeats the server's words", async () => {
  const onSave = vi.fn().mockRejectedValue(new Error("PATCH failed with 500"));
  render(<SettingsScreen apiKey="" onSave={onSave} />);
  fireEvent.click(screen.getByRole("button", { name: "Save" }));
  await waitFor(() => expect(screen.getByText("PATCH failed with 500")).toBeTruthy());
  expect(screen.queryByText("Saved.")).toBeNull();
});

test("a key arriving after the screen does fills the box", async () => {
  // The screen is drawn before the request comes back, so the box has to follow it.
  const { rerender } = render(<SettingsScreen apiKey="" onSave={vi.fn()} />);
  rerender(<SettingsScreen apiKey="xai-abc123" onSave={vi.fn()} />);
  await waitFor(() => expect(screen.getByLabelText("XAI API KEY").value).toBe("xai-abc123"));
});
