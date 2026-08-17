import { render, screen, waitFor } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";

import { useList } from "./useList.js";

afterEach(() => {
  vi.unstubAllGlobals();
});

function Host({ enabled = true }) {
  const { items, loading } = useList("/api/things", enabled);
  return (
    <div>
      <span data-testid="state">{loading ? "loading" : "settled"}</span>
      <span data-testid="count">{items.length}</span>
    </div>
  );
}

test("a list is loading until its first answer arrives", async () => {
  let answer;
  vi.stubGlobal(
    "fetch",
    vi.fn().mockReturnValue(
      new Promise((resolve) => {
        answer = () => resolve({ ok: true, status: 200, json: async () => [1, 2] });
      }),
    ),
  );
  render(<Host />);
  expect(screen.getByTestId("state").textContent).toBe("loading");

  answer();
  await waitFor(() => expect(screen.getByTestId("state").textContent).toBe("settled"));
  expect(screen.getByTestId("count").textContent).toBe("2");
});

test("a refused list stops loading too", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 500, text: async () => "" }));
  render(<Host />);
  // Otherwise the blocks would stand there for ever, which is a lie about what is coming.
  await waitFor(() => expect(screen.getByTestId("state").textContent).toBe("settled"));
});

test("a list that was never asked for is not loading", () => {
  vi.stubGlobal("fetch", vi.fn());
  render(<Host enabled={false} />);
  expect(screen.getByTestId("state").textContent).toBe("settled");
});
