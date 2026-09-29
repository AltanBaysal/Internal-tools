import { act, fireEvent, render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import FilePanel from "./FilePanel.jsx";

// jsdom ships no clipboard, so the test supplies one and watches what it is handed. The same shape
// queen-editor's RawOutput is tested with.
function stubClipboard(answer) {
  const writeText = vi.fn(() => answer);
  Object.defineProperty(navigator, "clipboard", { value: { writeText }, configurable: true });
  return writeText;
}

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

// A structure file and a prompt list are the point of the skills, and Markdown eats both: the
// indentation goes, the lines run together, and a Python comment becomes a heading. The decision is
// read off the name -- the chip's three letters say "jso", which is not an extension.
const STRUCTURE = '{\n  "quality": "score_9_up",\n  "frames": []\n}';

test("a file that is not Markdown is shown exactly as it is written", () => {
  const { container } = render(
    <FilePanel name="frames.json" file={{ ...FILE, name: "frames.json", text: STRUCTURE }} />,
  );
  expect(container.querySelector(".reader__code").textContent).toBe(STRUCTURE);
  expect(container.querySelector(".reader__body .md")).toBeNull();
});

test("Markdown syntax inside a code file stays as syntax", () => {
  const { container } = render(
    <FilePanel
      name="prompts.py"
      file={{ ...FILE, name: "prompts.py", text: "# a comment\nPROMPTS = [**x**]" }}
    />,
  );
  expect(container.querySelector("h1")).toBeNull();
  expect(container.querySelector("strong")).toBeNull();
  expect(container.querySelector(".reader__code").textContent).toContain("**x**");
});

test("a Markdown file is still drawn as a document", () => {
  const { container } = render(
    <FilePanel name="plan.md" file={{ ...FILE, text: "# Title" }} />,
  );
  expect(container.querySelector(".reader__body h1")).toBeTruthy();
  expect(container.querySelector(".reader__code")).toBeNull();
});

test("the footer says only how long ago it was written", () => {
  render(<FilePanel name="plan.md" file={FILE} />);
  expect(screen.getByTestId("file-meta").textContent).toBe("2h ago");
});

test("the footer does not repeat that the file belongs to the project", () => {
  // It was true of every file, so it told the reader nothing about the one in front of them --
  // and the screen is crowded enough with a file open.
  render(<FilePanel name="plan.md" file={FILE} />);
  expect(screen.getByTestId("file-meta").textContent).not.toContain("project file");
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

// Madde 192: the same button the list carries, because it does the same thing -- one action reads
// the list and the open file both, so the user never has to pick which staleness they are fixing.
test("the header carries a Refresh, and it asks for the file again", () => {
  const onRefresh = vi.fn();
  render(<FilePanel name="plan.md" file={FILE} onRefresh={onRefresh} />);
  fireEvent.click(screen.getByRole("button", { name: "Refresh" }));
  expect(onRefresh).toHaveBeenCalled();
});

test("Refresh says nothing while it runs", () => {
  // It changes the page in place, and the changed page is the answer.
  const onRefresh = vi.fn().mockReturnValue(new Promise(() => {}));
  const { container } = render(<FilePanel name="plan.md" file={FILE} onRefresh={onRefresh} />);
  fireEvent.click(screen.getByRole("button", { name: "Refresh" }));
  expect(screen.getByRole("button", { name: "Refresh" }).disabled).toBe(false);
  expect(container.querySelector(".spinner")).toBeNull();
});

// Madde 193. build_prompts writes to a file and does not print into the chat (Madde 130, and that
// rule stays), so the only way to get a prompt out was to select it by hand, line by line, inside a
// scrolling box. What the user does next is paste into ComfyUI.
test("Copy puts the whole file on the clipboard", () => {
  const writeText = stubClipboard(Promise.resolve());
  render(<FilePanel name="plan.md" file={FILE} />);
  fireEvent.click(screen.getByRole("button", { name: "Copy" }));
  expect(writeText).toHaveBeenCalledWith("the body");
});

test("what is copied is the file, not what the panel drew from it", () => {
  // The item's own sentence. A per-prompt button would mean a second reader of the shape
  // render_module writes -- and the day that reader drifts from the writer, the buttons copy the
  // wrong text. There is one reader, and it is the file.
  const writeText = stubClipboard(Promise.resolve());
  const { container } = render(
    <FilePanel name="plan.md" file={{ ...FILE, text: "# Title\n\nsome **bold** text" }} />,
  );
  expect(container.querySelector(".reader__body h1").textContent).toBe("Title");
  fireEvent.click(screen.getByRole("button", { name: "Copy" }));
  expect(writeText).toHaveBeenCalledWith("# Title\n\nsome **bold** text");
});

test("the button says it landed", async () => {
  stubClipboard(Promise.resolve());
  render(<FilePanel name="plan.md" file={FILE} />);
  fireEvent.click(screen.getByRole("button", { name: "Copy" }));
  expect(await screen.findByRole("button", { name: "Copied" })).toBeTruthy();
});

test("and says when it did not", async () => {
  // Silence would leave the user believing they had the text. The body is still selectable, so
  // saying it failed is also saying take it by hand.
  stubClipboard(Promise.reject(new Error("denied")));
  render(<FilePanel name="plan.md" file={FILE} />);
  fireEvent.click(screen.getByRole("button", { name: "Copy" }));
  expect(await screen.findByRole("button", { name: "Could not copy" })).toBeTruthy();
});

// Madde 342 (tasarım 154): the answer is the button's own word, written where Copy was. A word
// appearing beside the heading would push the body under it down, which is a page moving under the
// reader while they are reading it.
test("the answer is the button's own word and adds no line to the panel", async () => {
  stubClipboard(Promise.resolve());
  render(<FilePanel name="plan.md" file={FILE} />);
  fireEvent.click(screen.getByRole("button", { name: "Copy" }));
  const said = await screen.findByRole("button", { name: "Copied" });
  expect(said.textContent).toBe("Copied");
  expect(screen.getAllByText("Copied").length).toBe(1);
});

test("a copy that did not land says so in the same place", async () => {
  stubClipboard(Promise.reject(new Error("denied")));
  render(<FilePanel name="plan.md" file={FILE} />);
  fireEvent.click(screen.getByRole("button", { name: "Copy" }));
  const said = await screen.findByRole("button", { name: "Could not copy" });
  expect(said.textContent).toBe("Could not copy");
});

test("after a moment the button is Copy again", async () => {
  vi.useFakeTimers();
  try {
    stubClipboard(Promise.resolve());
    render(<FilePanel name="plan.md" file={FILE} />);
    fireEvent.click(screen.getByRole("button", { name: "Copy" }));
    await act(() => vi.advanceTimersByTimeAsync(0));
    expect(screen.getByRole("button", { name: "Copied" }).textContent).toBe("Copied");
    await act(() => vi.advanceTimersByTimeAsync(2500));
    expect(screen.getByRole("button", { name: "Copy" }).textContent).toBe("Copy");
  } finally {
    vi.useRealTimers();
  }
});

test("a file that has not arrived has nothing to copy, and the button stays", () => {
  // Dimmed rather than gone: a button that came and went as the file loaded would make the header
  // twitch. A button that copies nothing and says it did is the other half of the same lie.
  render(<FilePanel name="plan.md" file={null} />);
  expect(screen.getByRole("button", { name: "Copy" }).disabled).toBe(true);
});

// Madde 342 (tasarım 154, 176, 186): the head is two rows. The framed buttons stand above, the way
// back at one edge and Refresh and Copy at the other; the name stands under them on a row of its own,
// so it never gives up room to the buttons.

test("the header carries no Download", () => {
  render(<FilePanel name="plan.md" file={FILE} back />);
  expect(screen.queryByRole("button", { name: "Download" })).toBeNull();
});

test("the bar holds the way back at one edge, and Refresh then Copy at the other", () => {
  const { container } = render(<FilePanel name="plan.md" file={FILE} back />);
  const bar = container.querySelector(".reader__head > .reader__bar");
  expect(bar.firstElementChild.textContent).toBe("←");
  const tools = [...bar.querySelectorAll(".reader__tools > button")].map((one) => one.textContent);
  expect(tools).toEqual(["Refresh", "Copy"]);
});

test("Refresh and Copy are framed buttons with words on them", () => {
  render(<FilePanel name="plan.md" file={FILE} back />);
  expect(screen.getByRole("button", { name: "Refresh" }).classList.contains("ghost")).toBe(true);
  expect(screen.getByRole("button", { name: "Copy" }).classList.contains("ghost")).toBe(true);
});

test("the name stands under the bar, on a row of its own", () => {
  const { container } = render(<FilePanel name="plan.md" file={FILE} back />);
  const head = container.querySelector(".reader__head");
  expect(head.firstElementChild.className).toBe("reader__bar");
  expect(head.lastElementChild.className).toBe("reader__name");
  expect(head.lastElementChild.textContent).toBe("plan.md");
});

test("until the project screen goes, its × stands where the rail's ← does", () => {
  const { container } = render(<FilePanel name="plan.md" file={FILE} onClose={vi.fn()} />);
  expect(container.querySelector(".reader__bar").firstElementChild.textContent).toBe("×");
});
