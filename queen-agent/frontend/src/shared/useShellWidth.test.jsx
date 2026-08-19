import { act, render, screen } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";

import { shellSteps, useShellWidth } from "./useShellWidth.js";

afterEach(() => {
  vi.unstubAllGlobals();
});

test("a wide shell is in no step at all", () => {
  expect(shellSteps(1200)).toBe("");
  expect(shellSteps(1001)).toBe("");
});

test("the steps stack rather than replacing each other", () => {
  // At 600 all three hold, so every rule states its own threshold once and nothing is repeated.
  expect(shellSteps(1000)).toBe("app-shell--narrow");
  expect(shellSteps(780)).toBe("app-shell--narrow app-shell--tight");
  expect(shellSteps(640)).toBe("app-shell--narrow app-shell--tight app-shell--compact");
});

test("no measurement is not the smallest step", () => {
  // Zero is the absence of a measurement. Treating it as the narrowest screen would draw the wrong
  // layout for the first frame of every load.
  expect(shellSteps(0)).toBe("");
});

function fakeObserver() {
  const observers = [];
  vi.stubGlobal(
    "ResizeObserver",
    class {
      constructor(callback) {
        observers.push(callback);
      }
      observe() {}
      disconnect() {}
    },
  );
  return (width) =>
    act(() => {
      observers.forEach((callback) => callback([{ contentRect: { width } }]));
    });
}

function Host() {
  const { shell, steps } = useShellWidth();
  return (
    <div ref={shell} className={`app-shell ${steps}`.trim()} data-testid="shell">
      shell
    </div>
  );
}

test("the shell wears the step of the width it was measured at", () => {
  const measure = fakeObserver();
  render(<Host />);
  expect(screen.getByTestId("shell").className).toBe("app-shell");

  measure(700);
  expect(screen.getByTestId("shell").className).toBe(
    "app-shell app-shell--narrow app-shell--tight",
  );

  // The point of measuring rather than asking the window: the same screen embedded in a frame gets
  // the same answer.
  measure(1400);
  expect(screen.getByTestId("shell").className).toBe("app-shell");
});
