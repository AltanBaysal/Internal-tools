import { fireEvent, render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import { VERSION } from "../../shared/version.js";
import Bar from "./Bar.jsx";

const PROJECT = { id: "p1", name: "Thesis research", chats: 3, files: 3 };

test("the name and the run number read as one line", () => {
  // Madde 209 put the version under the name, where it read as a footnote. The user's call (v9-2,
  // and the design's 159): beside it, as Queen Editor writes "Queen Editor 1.4.2". Asked of the
  // constant rather than of a literal, for the reason version.test.js gives.
  const { container } = render(<Bar project={null} onExit={vi.fn()} />);
  expect(container.querySelector(".bar__name").textContent).toBe(`QueenAgent ${VERSION}`);
});

test("with no project open, the bar holds the brand alone", () => {
  const { container } = render(<Bar project={null} onExit={vi.fn()} />);
  expect(container.querySelector(".bar__project")).toBeNull();
  expect(screen.queryByRole("button", { name: "Exit project" })).toBeNull();
});

test("with a project open, its name stands in the middle and the way out on the right", () => {
  const { container } = render(<Bar project={PROJECT} onExit={vi.fn()} />);
  const name = container.querySelector(".bar__project");
  expect(name.textContent).toBe("Thesis research");
  // Cut on one line when it is long, so the whole of it has to be somewhere.
  expect(name.getAttribute("title")).toBe("Thesis research");
  expect(screen.getByRole("button", { name: "Exit project" }).className).toBe("ghost bar__exit");
});

// Madde 361 (the design's 195): the bar's right is each screen's own way out, and on the naming
// screen that is Cancel, in Exit project's place and look -- with no project open in the middle.
test("on the naming screen the right holds Cancel, in Exit project's place and look", () => {
  const onExit = vi.fn();
  const { container } = render(<Bar project={null} exit="Cancel" onExit={onExit} />);
  expect(container.querySelector(".bar__project")).toBeNull();
  const cancel = screen.getByRole("button", { name: "Cancel" });
  expect(cancel.className).toBe("ghost bar__exit");
  fireEvent.click(cancel);
  expect(onExit).toHaveBeenCalled();
});

test("Exit project asks to leave rather than deciding where to", () => {
  const onExit = vi.fn();
  render(<Bar project={PROJECT} onExit={onExit} />);
  fireEvent.click(screen.getByRole("button", { name: "Exit project" }));
  expect(onExit).toHaveBeenCalled();
});
