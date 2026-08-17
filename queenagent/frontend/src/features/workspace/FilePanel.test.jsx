import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import FilePanel from "./FilePanel.jsx";

const FILE = {
  name: "plan.md",
  ext: "md",
  size: 1434,
  text: "the body",
  modifiedAt: new Date(Date.now() - 2 * 3600_000).toISOString(),
};

test("the panel names the file and shows its text", () => {
  render(<FilePanel name="plan.md" file={FILE} />);
  expect(screen.getByText("plan.md")).toBeTruthy();
  expect(screen.getByText("the body")).toBeTruthy();
});

test("the header carries the name before the text has arrived", () => {
  // Nothing is drawn while it loads, but the panel already knows which file was clicked.
  render(<FilePanel name="plan.md" file={null} />);
  expect(screen.getByText("plan.md")).toBeTruthy();
});

test("the meta line carries the chip, the size and the time", () => {
  render(<FilePanel name="plan.md" file={FILE} />);
  expect(screen.getByTestId("file-meta").textContent).toBe("md · 1.4 KB · 2h ago");
});

test("a small file is measured in bytes", () => {
  render(<FilePanel name="a.md" file={{ ...FILE, size: 412 }} />);
  expect(screen.getByTestId("file-meta").textContent).toContain("412 B");
});

test("← closes the panel", () => {
  const onClose = vi.fn();
  render(<FilePanel name="plan.md" file={FILE} onClose={onClose} />);
  fireEvent.click(screen.getByRole("button", { name: "←" }));
  expect(onClose).toHaveBeenCalled();
});

// Escape is not this component's key: one listener owns the keyboard, so the order stays in one
// place. The behaviour is tested in App.test.jsx.

test("a file that is gone says so instead of showing an empty page", () => {
  render(<FilePanel name="plan.md" file={null} missing />);
  expect(screen.getByText("That file is gone.")).toBeTruthy();
});

test("Download asks for the file", () => {
  const onDownload = vi.fn().mockResolvedValue();
  render(<FilePanel name="plan.md" file={FILE} onDownload={onDownload} />);
  fireEvent.click(screen.getByRole("button", { name: "Download" }));
  expect(onDownload).toHaveBeenCalled();
});

test("while it downloads the button says preparing and comes back after", async () => {
  let finish;
  const onDownload = vi.fn().mockReturnValue(
    new Promise((resolve) => {
      finish = resolve;
    }),
  );
  render(<FilePanel name="plan.md" file={FILE} onDownload={onDownload} />);
  fireEvent.click(screen.getByRole("button", { name: "Download" }));

  await waitFor(() => expect(screen.getByRole("button", { name: /preparing/ })).toBeTruthy());
  finish();
  await waitFor(() => expect(screen.getByRole("button", { name: "Download" })).toBeTruthy());
});

test("a download that fails repeats the server's words", async () => {
  const onDownload = vi.fn().mockRejectedValue(new Error("GET failed with 500"));
  render(<FilePanel name="plan.md" file={FILE} onDownload={onDownload} />);
  fireEvent.click(screen.getByRole("button", { name: "Download" }));
  // No guessed cause, and the button goes back to being a button.
  await waitFor(() => expect(screen.getByText("GET failed with 500")).toBeTruthy());
  expect(screen.getByRole("button", { name: "Download" })).toBeTruthy();
});
