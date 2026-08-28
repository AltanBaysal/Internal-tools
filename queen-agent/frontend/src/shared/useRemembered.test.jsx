import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";

import { useRemembered, useRememberedMap } from "./remembered.js";

// What the browser keeps for itself. Not the server: since Madde 86 nothing there reads a selection
// back, and what is kept here is this browser's preference rather than the chat's record.

afterEach(() => {
  vi.unstubAllGlobals();
});

function Host({ fallback = "none" }) {
  const [value, setValue] = useRemembered("skill", fallback);
  return (
    <div>
      <span data-testid="value">{value}</span>
      <button type="button" onClick={() => setValue("picked")}>
        pick
      </button>
      <button type="button" onClick={() => setValue("")}>
        let go
      </button>
    </div>
  );
}

test("with nothing kept the answer is the fallback", () => {
  render(<Host />);
  expect(screen.getByTestId("value").textContent).toBe("none");
});

test("what was kept comes back on the next mount", () => {
  const first = render(<Host />);
  fireEvent.click(screen.getByText("pick"));
  first.unmount();

  render(<Host />);
  expect(screen.getByTestId("value").textContent).toBe("picked");
});

test("letting a value go is kept as itself, not as nothing", () => {
  // The trap this exists for: an empty selection and no selection are different things, and a read
  // that folds them together undoes the user's "drop this" on every reload.
  const first = render(<Host />);
  fireEvent.click(screen.getByText("pick"));
  fireEvent.click(screen.getByText("let go"));
  first.unmount();

  render(<Host />);
  expect(screen.getByTestId("value").textContent).toBe("");
});

test("a browser that refuses to be read hands back the fallback", () => {
  // A private window, or storage switched off. Both throw on the read rather than answering null.
  vi.stubGlobal("localStorage", {
    getItem: () => {
      throw new Error("denied");
    },
    setItem: () => {},
  });
  render(<Host />);
  expect(screen.getByTestId("value").textContent).toBe("none");
});

test("a browser that refuses to be written to still works", () => {
  // The memory is lost and nothing else is: the selection still holds for this session.
  vi.stubGlobal("localStorage", {
    getItem: () => null,
    setItem: () => {
      throw new Error("full");
    },
  });
  render(<Host />);
  fireEvent.click(screen.getByText("pick"));
  expect(screen.getByTestId("value").textContent).toBe("picked");
});

// The map: one browser key, one entry per chat -- Madde 105's shape for the skill selection.
function MapHost({ chat }) {
  const [skills, remember] = useRememberedMap("chat-skills");
  return (
    <div>
      <span data-testid="value">{skills[chat] ?? "none"}</span>
      <button type="button" onClick={() => remember(chat, "picked")}>
        pick
      </button>
    </div>
  );
}

test("a map keeps each key to itself", () => {
  const first = render(<MapHost chat="c1" />);
  fireEvent.click(screen.getByText("pick"));
  first.unmount();

  render(<MapHost chat="c2" />);
  expect(screen.getByTestId("value").textContent).toBe("none");
});

test("what a key kept comes back on the next mount", () => {
  const first = render(<MapHost chat="c1" />);
  fireEvent.click(screen.getByText("pick"));
  first.unmount();

  render(<MapHost chat="c1" />);
  expect(screen.getByTestId("value").textContent).toBe("picked");
});

test("a memory that is not even JSON is an empty map, not a crash", () => {
  // Storage is shared with every past version of the app: what is read must never be trusted to
  // parse.
  window.localStorage.setItem("queenagent.chat-skills", "{broken");
  render(<MapHost chat="c1" />);
  expect(screen.getByTestId("value").textContent).toBe("none");
});
