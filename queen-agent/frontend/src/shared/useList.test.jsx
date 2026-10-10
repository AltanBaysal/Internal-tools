import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";

import { useList } from "./useList.js";

afterEach(() => {
  vi.unstubAllGlobals();
});

function Host({ path = "/api/things", enabled = true }) {
  const { items, reload, loading, error } = useList(path, enabled);
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

// Madde 457: a server that answers when the test says so. Each path keeps its waiting reads in the
// order they were asked, and `nth` picks one of them -- so a later read can land before an earlier.
function heldServer() {
  const held = {};
  vi.stubGlobal(
    "fetch",
    vi.fn().mockImplementation(
      (path) => new Promise((resolve) => (held[path] ??= []).push(resolve)),
    ),
  );
  const settle = (path, response, nth = 0) =>
    act(async () => held[path].splice(nth, 1)[0](response));
  return {
    answer: (path, body, nth) =>
      settle(path, { ok: true, status: 200, json: async () => body }, nth),
    refuse: (path, message) =>
      settle(path, {
        ok: false,
        status: 500,
        text: async () => JSON.stringify({ error: message }),
      }),
  };
}

test("an answer about a path that is no longer the list's is not drawn", async () => {
  // Project A's chats land after B's were asked for: B's sidebar must not list A's chats.
  const server = heldServer();
  const { rerender } = render(<Host path="/api/a" />);
  rerender(<Host path="/api/b" />);

  await server.answer("/api/b", [1]);
  await server.answer("/api/a", [1, 2, 3]);
  expect(screen.getByTestId("count").textContent).toBe("1");
});

test("a failure about a path that is no longer the list's does not stand over it", async () => {
  // Otherwise a read of the project just left would blank the open one's list with its error.
  const server = heldServer();
  const { rerender } = render(<Host path="/api/a" />);
  rerender(<Host path="/api/b" />);

  await server.answer("/api/b", [1]);
  await server.refuse("/api/a", "the store is unreachable");
  expect(screen.getByTestId("error").textContent).toBe("");
  expect(screen.getByTestId("count").textContent).toBe("1");
});

test("a late answer about another path does not end the wait for the list's own", async () => {
  const server = heldServer();
  const { rerender } = render(<Host path="/api/a" />);
  rerender(<Host path="/api/b" />);

  await server.answer("/api/a", [1, 2, 3]);
  expect(screen.getByTestId("state").textContent).toBe("loading");
  expect(screen.getByTestId("count").textContent).toBe("0");

  await server.answer("/api/b", [1]);
  expect(screen.getByTestId("state").textContent).toBe("settled");
  expect(screen.getByTestId("count").textContent).toBe("1");
});

test("a list moved to another path is loading again, with none of the old path's rows", async () => {
  // The rows of the project just left are not the open one's: clicking one would say chat missing.
  const server = heldServer();
  const { rerender } = render(<Host path="/api/a" />);
  await server.answer("/api/a", [1, 2, 3]);
  expect(screen.getByTestId("count").textContent).toBe("3");

  rerender(<Host path="/api/b" />);
  expect(screen.getByTestId("state").textContent).toBe("loading");
  expect(screen.getByTestId("count").textContent).toBe("0");

  await server.answer("/api/b", [1]);
  expect(screen.getByTestId("state").textContent).toBe("settled");
  expect(screen.getByTestId("count").textContent).toBe("1");
});

test("a path opened again keeps its own last answer while it is read again", async () => {
  // Left for All projects and reopened: the rows on hand are this project's own, as they are while
  // a turn's end reads it again -- so they stay, and nothing waits. Only another path's never show.
  const server = heldServer();
  const { rerender } = render(<Host path="/api/a" />);
  await server.answer("/api/a", [1, 2, 3]);
  rerender(<Host path="/api/a" enabled={false} />);
  rerender(<Host path="/api/a" />);

  expect(screen.getByTestId("state").textContent).toBe("settled");
  expect(screen.getByTestId("count").textContent).toBe("3");
  await server.answer("/api/a", [1]);
  expect(screen.getByTestId("count").textContent).toBe("1");
});

test("a path whose first read fails shows the failure and none of the old path's rows", async () => {
  const server = heldServer();
  const { rerender } = render(<Host path="/api/a" />);
  await server.answer("/api/a", [1, 2, 3]);
  rerender(<Host path="/api/b" />);

  await server.refuse("/api/b", "the store is unreachable");
  expect(screen.getByTestId("error").textContent).toBe("the store is unreachable");
  expect(screen.getByTestId("state").textContent).toBe("settled");
  expect(screen.getByTestId("count").textContent).toBe("0");
});

test("asked again after a failed first read, the list is waiting rather than empty", async () => {
  // Settled with no rows, the screen would say there are none while the answer is on its way.
  const server = heldServer();
  render(<Host />);
  await server.refuse("/api/things", "the store is unreachable");

  fireEvent.click(screen.getByText("again"));
  expect(screen.getByTestId("error").textContent).toBe("");
  expect(screen.getByTestId("state").textContent).toBe("loading");
});

test("an older read of the same list landing last does not put its order back", async () => {
  // A newborn chat's sidebar is read at its first frame and again at the turn's end (Madde 452).
  const server = heldServer();
  render(<Host />);
  fireEvent.click(screen.getByText("again"));

  // The newer read lands first, then the one asked before it.
  await server.answer("/api/things", [1], 1);
  await server.answer("/api/things", [1, 2]);
  expect(screen.getByTestId("count").textContent).toBe("1");
});
