import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";

import { useList } from "./useList.js";

afterEach(() => {
  vi.unstubAllGlobals();
});

function Host({ enabled = true }) {
  const { items, reload, loading, error } = useList("/api/things", enabled);
  return (
    <div>
      <span data-testid="state">{loading ? "loading" : "settled"}</span>
      <span data-testid="count">{items.length}</span>
      <span data-testid="error">{error ?? ""}</span>
      <button type="button" onClick={reload}>
        again
      </button>
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

test("a list that could not be read says what the server said", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
      text: async () => JSON.stringify({ error: "the store is unreachable" }),
    }),
  );
  render(<Host />);
  // Kept rather than swallowed: without it the screen answers a question it never got an answer to.
  await waitFor(() => expect(screen.getByTestId("error").textContent).toBe("the store is unreachable"));
});

test("a reload that fails leaves the list that was already there", async () => {
  const fetch = vi
    .fn()
    .mockResolvedValueOnce({ ok: true, status: 200, json: async () => [1, 2] })
    .mockResolvedValue({ ok: false, status: 500, text: async () => "" });
  vi.stubGlobal("fetch", fetch);
  render(<Host />);
  await waitFor(() => expect(screen.getByTestId("count").textContent).toBe("2"));

  fireEvent.click(screen.getByText("again"));
  // Emptying it would be a second lie: the two files are still in the project.
  await waitFor(() => expect(screen.getByTestId("error").textContent).not.toBe(""));
  expect(screen.getByTestId("count").textContent).toBe("2");
});

test("a fresh attempt clears the failure before it starts", async () => {
  const fetch = vi
    .fn()
    .mockResolvedValueOnce({ ok: false, status: 500, text: async () => "" })
    .mockResolvedValue({ ok: true, status: 200, json: async () => [1] });
  vi.stubGlobal("fetch", fetch);
  render(<Host />);
  await waitFor(() => expect(screen.getByTestId("error").textContent).not.toBe(""));

  fireEvent.click(screen.getByText("again"));
  await waitFor(() => expect(screen.getByTestId("count").textContent).toBe("1"));
  expect(screen.getByTestId("error").textContent).toBe("");
});

test("a list that was never asked for is not loading", () => {
  vi.stubGlobal("fetch", vi.fn());
  render(<Host enabled={false} />);
  expect(screen.getByTestId("state").textContent).toBe("settled");
});
