import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";

import { clockTime } from "../../shared/time.js";
import Stamp, { LiveStrip } from "./Stamp.jsx";

// Madde 344: the stamp and the strip that stands in its place while a turn runs share one file,
// because they share one place, one class and one way of shortening a count.

const AT = new Date(2026, 7, 9, 11, 5).toISOString();

test("without a time there is no stamp", () => {
  const { container } = render(<Stamp at={null} />);
  expect(container.firstChild).toBeNull();
});

test("an answer's stamp says when and what it spent", () => {
  render(<Stamp at={AT} usage={{ sent: 1000, answered: 200 }} />);
  expect(screen.getByText(`${clockTime(AT)} · 1.2k tokens`)).toBeTruthy();
});

test("nothing spent leaves the time alone", () => {
  const { container } = render(<Stamp at={AT} usage={{ sent: 0, answered: 0 }} />);
  expect(container.querySelector(".msg__stamp").textContent).toBe(clockTime(AT));
});

test("the live strip says the round and the tokens", () => {
  render(<LiveStrip round={2} of={16} tokens={1234} />);
  expect(screen.getByText("round 2/16 · 1.2k tokens", { exact: false })).toBeTruthy();
});

// Madde 348: every note under a message on the stamp's one row, the time first (design item 139).

test("what is handed to the stamp stands after its words, on its row", () => {
  // A question's arrows and pencil ride on the row its time is on.
  const { container } = render(
    <Stamp at={AT}>
      <button type="button">✎</button>
    </Stamp>,
  );
  const row = container.querySelector(".msg__stamp");
  expect([...row.children].map((part) => part.tagName)).toEqual(["SPAN", "BUTTON"]);
  expect(row.firstElementChild.textContent).toBe(clockTime(AT));
});

test("the live strip starts with the time the wait began", () => {
  render(<LiveStrip at={AT} round={2} of={16} tokens={1234} />);
  expect(screen.getByTestId("live-strip").firstElementChild.textContent).toBe(
    `${clockTime(AT)} · round 2/16 · 1.2k tokens · `,
  );
});

test("before the wait is stamped the strip starts with the round", () => {
  render(<LiveStrip round={2} of={16} tokens={1234} />);
  expect(screen.getByTestId("live-strip").firstElementChild.textContent).toBe(
    "round 2/16 · 1.2k tokens · ",
  );
});
