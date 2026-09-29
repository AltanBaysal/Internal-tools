import { fireEvent, render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import NameProjectScreen from "./NameProjectScreen.jsx";

// Madde 361: every + New project asks for the name first (the design's items 135, 153, 169, 195,
// new-project/index.html). Where Cancel and Escape go is App's, not this screen's.

const field = () => screen.getByPlaceholderText("Project name");
const type = (text) => fireEvent.change(field(), { target: { value: text } });

test("the title is the field's own label, over one line and the field beside Create project", () => {
  const { container } = render(<NameProjectScreen onCreate={vi.fn()} />);
  // No separate "Project name" text stands beside the field: the title names it.
  const named = screen.getByLabelText("Name your project");
  expect(named).toBe(field());
  const title = screen.getByText("Name your project");
  expect(title.className).toBe("empty__title");
  expect(title.tagName).toBe("LABEL");
  expect(
    screen.getByText("Chats live inside a project, and the files they create stay there.").className,
  ).toBe("empty__line");
  expect(field().className).toBe("empty__field");
  expect(field().getAttribute("autocomplete")).toBe("off");
  const create = screen.getByRole("button", { name: "Create project" });
  expect(create.className).toBe("empty__action");
  // Side by side in their own row, inside the left-aligned box in empty's centred column.
  expect(create.parentElement).toBe(field().parentElement);
  expect(field().parentElement.className).toBe("empty__row");
  expect(container.querySelector(".empty > .empty__box")).toBeTruthy();
});

test("with no project yet the title says it is the first", () => {
  render(<NameProjectScreen first onCreate={vi.fn()} />);
  expect(screen.getByLabelText("Name your first project")).toBe(field());
  expect(screen.queryByText("Name your project")).toBeNull();
});

test("the field takes the focus as the screen opens", () => {
  render(<NameProjectScreen onCreate={vi.fn()} />);
  expect(document.activeElement).toBe(field());
});

test("Enter creates the project under the name typed, trimmed", () => {
  const onCreate = vi.fn();
  render(<NameProjectScreen onCreate={onCreate} />);
  type("  Harbour  ");
  fireEvent.keyDown(field(), { key: "Enter" });
  expect(onCreate).toHaveBeenCalledWith("Harbour");
});

test("Create project does what Enter does", () => {
  const onCreate = vi.fn();
  render(<NameProjectScreen onCreate={onCreate} />);
  type("Harbour");
  fireEvent.click(screen.getByRole("button", { name: "Create project" }));
  expect(onCreate).toHaveBeenCalledWith("Harbour");
});

test("a blank name does nothing, and neither does Shift + Enter", () => {
  const onCreate = vi.fn();
  render(<NameProjectScreen onCreate={onCreate} />);
  fireEvent.keyDown(field(), { key: "Enter" });
  fireEvent.click(screen.getByRole("button", { name: "Create project" }));
  type("   ");
  fireEvent.keyDown(field(), { key: "Enter" });
  fireEvent.click(screen.getByRole("button", { name: "Create project" }));
  type("Harbour");
  fireEvent.keyDown(field(), { key: "Enter", shiftKey: true });
  expect(onCreate).not.toHaveBeenCalled();
});

test("a second press while the first is on its way makes no second project", () => {
  // A double Enter is two presses a moment apart, and each would be a project of its own.
  const onCreate = vi.fn().mockReturnValue(new Promise(() => {}));
  render(<NameProjectScreen onCreate={onCreate} />);
  type("Harbour");
  fireEvent.keyDown(field(), { key: "Enter" });
  fireEvent.keyDown(field(), { key: "Enter" });
  fireEvent.click(screen.getByRole("button", { name: "Create project" }));
  expect(onCreate).toHaveBeenCalledTimes(1);
});

// Madde 364 (the design's 172, 173).
test("while the list loads, the spinner stands alone and nothing is asked yet", () => {
  // Whether this is the first project is not known until the list comes, so there is no frame to
  // keep: only empty's own centring, and the ring in it.
  const { container } = render(<NameProjectScreen loading onCreate={vi.fn()} />);
  const empty = container.querySelector(".empty");
  expect(empty.children.length).toBe(1);
  expect(empty.firstElementChild.dataset.testid).toBe("spinner");
  expect(screen.queryByPlaceholderText("Project name")).toBeNull();
  expect(screen.queryByText(/Name your/)).toBeNull();
});

// What failure.js makes of a Flask 500 page: the code and the body, as they came.
const RAW = "HTTP 500: <!doctype html>\n<title>500 Internal Server Error</title>";

test("a list that could not be read says so, with Try again and Copy, and asks nothing", () => {
  // All projects' own failure: one plain sentence, the raw words left to Copy.
  const onRetry = vi.fn();
  render(<NameProjectScreen error={RAW} onRetry={onRetry} onCreate={vi.fn()} />);
  expect(screen.getByText("Couldn't load projects.").className).toBe("empty__error");
  expect(screen.queryByText(/HTTP 500/)).toBeNull();
  expect(screen.queryByPlaceholderText("Project name")).toBeNull();
  fireEvent.click(screen.getByRole("button", { name: "Try again" }));
  expect(onRetry).toHaveBeenCalled();
});

test("its Copy puts the error on the clipboard exactly as it came", () => {
  // jsdom ships no clipboard, so the test supplies one and watches what it is handed.
  const writeText = vi.fn(() => Promise.resolve());
  Object.defineProperty(navigator, "clipboard", { value: { writeText }, configurable: true });
  render(<NameProjectScreen error={RAW} onCreate={vi.fn()} />);
  fireEvent.click(screen.getByRole("button", { name: "Copy" }));
  expect(writeText).toHaveBeenCalledWith(RAW);
});

test("a project the server will not make keeps the name typed, and says what the server said", async () => {
  // The name is the user's work: a refusal is said under it, never in its place.
  const onCreate = vi.fn().mockRejectedValue(new Error("a project needs a name"));
  render(<NameProjectScreen onCreate={onCreate} />);
  type("Harbour");
  fireEvent.keyDown(field(), { key: "Enter" });
  const said = await screen.findByText("a project needs a name");
  expect(said.className).toBe("empty__refused");
  expect(said.previousElementSibling.className).toBe("empty__row");
  expect(field().value).toBe("Harbour");
});
