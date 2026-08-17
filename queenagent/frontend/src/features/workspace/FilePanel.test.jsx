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

// The same parser the answers use, at the document scale. The scale itself is CSS and is locked in
// workspace.css.test.js; what is asserted here is that the text is parsed at all.
test("the body is drawn as a document rather than as plain text", () => {
  const { container } = render(
    <FilePanel name="plan.md" file={{ ...FILE, text: "# Title\n\nsome **bold** text" }} />,
  );
  expect(container.querySelector(".reader__body h1").textContent).toBe("Title");
  expect(container.querySelector(".reader__body strong").textContent).toBe("bold");
});

test("the footer says how long ago it was written and whose file it is", () => {
  render(<FilePanel name="plan.md" file={FILE} />);
  expect(screen.getByTestId("file-meta").textContent).toBe("2h ago · project file");
});

test("the footer no longer measures the file", () => {
  // The extension is on the chip and in the name already, and a byte count answers a question the
  // reader is not asking.
  render(<FilePanel name="plan.md" file={{ ...FILE, size: 412 }} />);
  expect(screen.getByTestId("file-meta").textContent).not.toContain("412");
  expect(screen.getByTestId("file-meta").textContent).not.toContain("md ·");
});

// Two panels, two ways out, because they are two different things: the rail's is the rail widened,
// so it is come back from; the project screen's is a surface standing beside the grid, so it closes.
test("the rail's panel comes back", () => {
  const onClose = vi.fn();
  render(<FilePanel name="plan.md" file={FILE} back onClose={onClose} />);
  fireEvent.click(screen.getByRole("button", { name: "←" }));
  expect(onClose).toHaveBeenCalled();
  expect(screen.queryByRole("button", { name: "×" })).toBeNull();
});

test("the project screen's panel closes, and carries no back arrow", () => {
  const onClose = vi.fn();
  render(<FilePanel name="plan.md" file={FILE} onClose={onClose} />);
  fireEvent.click(screen.getByRole("button", { name: "×" }));
  expect(onClose).toHaveBeenCalled();
  expect(screen.queryByRole("button", { name: "←" })).toBeNull();
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

test("preparing is said in words, not spun", async () => {
  // Motion is a fade and the rail's width; a spinner is neither. The word and the disabled button
  // already say the same thing.
  const onDownload = vi.fn().mockReturnValue(new Promise(() => {}));
  const { container } = render(<FilePanel name="plan.md" file={FILE} onDownload={onDownload} />);
  fireEvent.click(screen.getByRole("button", { name: "Download" }));
  await waitFor(() => expect(screen.getByRole("button", { name: /preparing/ })).toBeTruthy());
  expect(container.querySelector(".spinner")).toBeNull();
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
