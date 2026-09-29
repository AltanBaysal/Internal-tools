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

test("while the list loads, nothing is asked yet", () => {
  // Whether this is the first project is not known until the list comes; the spinner is Madde 364's.
  render(<NameProjectScreen loading onCreate={vi.fn()} />);
  expect(screen.queryByPlaceholderText("Project name")).toBeNull();
  expect(screen.queryByText(/Name your/)).toBeNull();
});

test("a failure says what the server said, and nothing else", () => {
  const { container } = render(
    <NameProjectScreen error="a project needs a name" onCreate={vi.fn()} />,
  );
  expect(screen.getByText("a project needs a name").className).toBe("empty__error");
  expect(container.querySelector(".empty")).toBeTruthy();
  expect(screen.queryByPlaceholderText("Project name")).toBeNull();
});
