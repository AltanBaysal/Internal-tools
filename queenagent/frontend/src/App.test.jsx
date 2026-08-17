import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";

import App from "./App.jsx";

afterEach(() => {
  vi.unstubAllGlobals();
  // jsdom shares one document across tests, so a pushed address has to be put back.
  window.history.pushState(null, "", "/");
  Object.defineProperty(window.navigator, "onLine", { value: true, configurable: true });
});

const PROJECT = { id: "p1", name: "Old", desc: "Notes.", hue: 45, chats: 0, files: 0 };

function stubProjects(projects) {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({ ok: true, status: 200, json: async () => projects }),
  );
}

test("the shell renders", () => {
  stubProjects([]);
  render(<App />);
  expect(screen.getByTestId("app-shell")).toBeTruthy();
});

test("loaded projects reach both the sidebar and the cards", async () => {
  stubProjects([{ id: "p1", name: "Thesis", desc: "Summaries.", hue: 45, chats: 0, files: 0 }]);
  render(<App />);
  await waitFor(() => expect(screen.getAllByText("Thesis").length).toBe(2));
});

test("a project address does not draw home", async () => {
  stubProjects([]);
  window.history.pushState(null, "", "/p/pabc");
  render(<App />);
  await waitFor(() => expect(screen.getByText("That project does not exist.")).toBeTruthy());
});

test("a renamed project shows the new name in both places at once", async () => {
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (options?.method === "PATCH") {
      return Promise.resolve({
        ok: true,
        status: 200,
        json: async () => ({ ...PROJECT, name: "New" }),
      });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [PROJECT] });
  });
  vi.stubGlobal("fetch", fetch);
  vi.stubGlobal("prompt", vi.fn().mockReturnValue("New"));
  window.history.pushState(null, "", "/p/p1");

  render(<App />);
  await waitFor(() => expect(screen.getByRole("button", { name: "Rename" })).toBeTruthy());
  fireEvent.click(screen.getByRole("button", { name: "Rename" }));
  // The title and the sidebar row read the same array, so they cannot disagree.
  await waitFor(() => expect(screen.getAllByText("New").length).toBe(2));
});

test("a message from home opens a project and a chat and goes there", async () => {
  const chat = { id: "c1", title: "Write the intro", messages: [], lastActivity: "x" };
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (path === "/api/chats" && options?.method === "POST") {
      return Promise.resolve({
        ok: true,
        status: 201,
        json: async () => ({ project: { ...PROJECT, name: "Write the intro" }, chat }),
      });
    }
    if (path.endsWith("/chats/c1")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => chat });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [] });
  });
  vi.stubGlobal("fetch", fetch);

  render(<App />);
  fireEvent.change(screen.getByPlaceholderText(/Ask anything/), {
    target: { value: "Write the intro" },
  });
  fireEvent.keyDown(screen.getByPlaceholderText(/Ask anything/), { key: "Enter" });

  await waitFor(() => expect(window.location.pathname).toBe("/p/p1/c/c1"));
});

test("the user bubble shows before the server answers, and leaves if it refuses", async () => {
  const chat = { id: "c1", title: "Hi", messages: [], lastActivity: "x" };
  let refuse;
  const pending = new Promise((resolve) => {
    refuse = () => resolve({ ok: false, status: 500, json: async () => ({}) });
  });
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (path.endsWith("/messages") && options?.method === "POST") return pending;
    if (path.endsWith("/chats/c1")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => chat });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/c1");

  render(<App />);
  await waitFor(() => expect(screen.getByPlaceholderText("Reply...")).toBeTruthy());
  fireEvent.change(screen.getByPlaceholderText("Reply..."), { target: { value: "hello" } });
  fireEvent.keyDown(screen.getByPlaceholderText("Reply..."), { key: "Enter" });

  // The design says the bubble appears immediately -- before the request has come back.
  await waitFor(() => expect(screen.getByText("hello")).toBeTruthy());

  refuse();
  await waitFor(() => expect(screen.queryByText("hello")).toBeNull());
  expect(screen.getByText(/failed with 500/)).toBeTruthy();
});

function sseResponse(text) {
  const encoded = new TextEncoder().encode(text);
  let sent = false;
  return {
    ok: true,
    status: 200,
    body: {
      getReader: () => ({
        read: async () => {
          if (sent) return { done: true };
          sent = true;
          return { done: false, value: encoded };
        },
      }),
    },
  };
}

test("a chat that is owed an answer streams one and keeps the server's record", async () => {
  const owed = {
    id: "c1",
    title: "hello",
    messages: [{ role: "user", at: new Date().toISOString(), text: "hello" }],
  };
  const answered = {
    ...owed,
    messages: [...owed.messages, { role: "ai", at: new Date().toISOString(), text: "Done." }],
  };
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (path.endsWith("/answer") && options?.method === "POST") {
      return Promise.resolve(
        sseResponse(
          `event: chunk\ndata: {"text":"Do"}\n\nevent: done\ndata: ${JSON.stringify(answered)}\n\n`,
        ),
      );
    }
    if (path.endsWith("/chats/c1")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => owed });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/c1");

  render(<App />);
  await waitFor(() => expect(screen.getByText("Done.")).toBeTruthy());
});

test("a file born mid-answer reaches the rail without a reload", async () => {
  const owed = {
    id: "c1",
    title: "hello",
    messages: [{ role: "user", at: new Date().toISOString(), text: "write the outline" }],
  };
  const answered = {
    ...owed,
    messages: [
      ...owed.messages,
      { role: "ai", at: new Date().toISOString(), text: "Saved.", files: ["outline.md"] },
    ],
  };
  // The directory is the list, so the stub answers differently once the file has been written.
  let onDisk = [];
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (path.endsWith("/answer") && options?.method === "POST") {
      onDisk = [{ name: "outline.md", ext: "md", modifiedAt: new Date().toISOString() }];
      return Promise.resolve(
        sseResponse(
          'event: file-start\ndata: {}\n\n' +
            'event: file\ndata: {"name":"outline.md"}\n\n' +
            `event: done\ndata: ${JSON.stringify(answered)}\n\n`,
        ),
      );
    }
    if (path.endsWith("/files")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => onDisk });
    }
    if (path.endsWith("/chats/c1")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => owed });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/c1");

  render(<App />);
  await waitFor(() => expect(screen.getByTestId("file-rail").textContent).toContain("outline.md"));
});

test("a fault inside the stream shows the card and Try again asks again", async () => {
  const owed = {
    id: "c1",
    title: "hello",
    messages: [{ role: "user", at: new Date().toISOString(), text: "hello" }],
  };
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (path.endsWith("/answer") && options?.method === "POST") {
      return Promise.resolve(
        sseResponse('event: error\ndata: {"error":"401 bad key"}\n\n'),
      );
    }
    if (path.endsWith("/chats/c1")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => owed });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/c1");

  render(<App />);
  await waitFor(() => expect(screen.getByText("401 bad key")).toBeTruthy());
  const before = fetch.mock.calls.filter(([path]) => path.endsWith("/answer")).length;

  fireEvent.click(screen.getByRole("button", { name: "Try again" }));
  await waitFor(() =>
    expect(fetch.mock.calls.filter(([path]) => path.endsWith("/answer")).length).toBe(before + 1),
  );
  // Try again never re-sends the message: the chat is still owed an answer.
  expect(fetch.mock.calls.some(([path]) => path.endsWith("/messages"))).toBe(false);
});

test("a broken engine is reported once and not asked again", async () => {
  const owed = {
    id: "c1",
    title: "hello",
    messages: [{ role: "user", at: new Date().toISOString(), text: "hello" }],
  };
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (path.endsWith("/answer") && options?.method === "POST") {
      return Promise.resolve({ ok: false, status: 502, json: async () => ({}) });
    }
    if (path.endsWith("/chats/c1")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => owed });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/c1");

  render(<App />);
  await waitFor(() => expect(screen.getByText(/failed with 502/)).toBeTruthy());
  const asked = fetch.mock.calls.filter(([path]) => path.endsWith("/answer")).length;
  // A chat that is owed an answer must not turn a broken engine into an endless retry.
  expect(asked).toBe(1);
});

test("deleting a chat asks first, and a no sends nothing", async () => {
  const chats = [{ id: "c1", title: "Write the intro", lastActivity: new Date().toISOString() }];
  const fetch = vi.fn().mockImplementation((path) => {
    if (path === `/api/projects/p1/chats`) {
      return Promise.resolve({ ok: true, status: 200, json: async () => chats });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [PROJECT] });
  });
  vi.stubGlobal("fetch", fetch);
  vi.stubGlobal("confirm", vi.fn().mockReturnValue(false));
  window.history.pushState(null, "", "/p/p1");

  render(<App />);
  await waitFor(() => expect(screen.getByText("Write the intro")).toBeTruthy());
  fireEvent.click(screen.getByRole("button", { name: "Delete Write the intro" }));

  expect(window.confirm).toHaveBeenCalled();
  expect(fetch.mock.calls.every(([, options]) => options?.method !== "DELETE")).toBe(true);
});

test("a chat the user confirms is deleted and leaves both lists", async () => {
  let chats = [{ id: "c1", title: "Write the intro", lastActivity: new Date().toISOString() }];
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (options?.method === "DELETE") {
      chats = [];
      return Promise.resolve({ ok: true, status: 200, json: async () => ({}) });
    }
    if (path === "/api/projects/p1/chats" || path === "/api/chats") {
      return Promise.resolve({ ok: true, status: 200, json: async () => chats });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [PROJECT] });
  });
  vi.stubGlobal("fetch", fetch);
  vi.stubGlobal("confirm", vi.fn().mockReturnValue(true));
  window.history.pushState(null, "", "/p/p1");

  render(<App />);
  await waitFor(() => expect(screen.getAllByText("Write the intro").length).toBeGreaterThan(0));
  fireEvent.click(screen.getByRole("button", { name: "Delete Write the intro" }));
  await waitFor(() => expect(screen.queryByText("Write the intro")).toBeNull());
});

test("deleting the file that is open closes the panel", async () => {
  const file = { name: "plan.md", ext: "md", modifiedAt: new Date().toISOString() };
  let onDisk = [file];
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (options?.method === "DELETE") {
      onDisk = [];
      return Promise.resolve({ ok: true, status: 200, json: async () => ({ trashed: "plan.md" }) });
    }
    if (path.endsWith("/files/plan.md")) {
      return Promise.resolve({
        ok: true,
        status: 200,
        json: async () => ({ ...file, size: 4, text: "body" }),
      });
    }
    if (path.endsWith("/files")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => onDisk });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [PROJECT] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1");

  render(<App />);
  await waitFor(() => expect(screen.getByText("plan.md")).toBeTruthy());
  fireEvent.click(screen.getByText("plan.md"));
  await waitFor(() => expect(screen.getByText("body")).toBeTruthy());

  fireEvent.click(screen.getByRole("button", { name: "Delete plan.md" }));
  // Reading something that is no longer there is not reading.
  await waitFor(() => expect(screen.queryByText("body")).toBeNull());
  expect(screen.getByText("File deleted.")).toBeTruthy();
});

test("renaming the open file keeps the panel on it", async () => {
  const file = { name: "plan.md", ext: "md", modifiedAt: new Date().toISOString() };
  let onDisk = [file];
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (options?.method === "PATCH") {
      onDisk = [{ ...file, name: "outline.md" }];
      return Promise.resolve({ ok: true, status: 200, json: async () => onDisk[0] });
    }
    if (path.endsWith("/files/plan.md")) {
      return Promise.resolve({
        ok: true,
        status: 200,
        json: async () => ({ ...file, size: 4, text: "body" }),
      });
    }
    if (path.endsWith("/files/outline.md")) {
      return Promise.resolve({
        ok: true,
        status: 200,
        json: async () => ({ ...onDisk[0], size: 4, text: "body" }),
      });
    }
    if (path.endsWith("/files")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => onDisk });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [PROJECT] });
  });
  vi.stubGlobal("fetch", fetch);
  vi.stubGlobal("prompt", vi.fn().mockReturnValue("outline.md"));
  window.history.pushState(null, "", "/p/p1");

  render(<App />);
  await waitFor(() => expect(screen.getByText("plan.md")).toBeTruthy());
  fireEvent.click(screen.getByText("plan.md"));
  await waitFor(() => expect(screen.getByText("body")).toBeTruthy());

  fireEvent.click(screen.getByRole("button", { name: "Rename plan.md" }));
  // The file is still there under another name, so the panel follows it rather than closing.
  await waitFor(() => expect(screen.getAllByText("outline.md").length).toBe(2));
});

test("an empty answer to the rename prompt sends nothing", async () => {
  const file = { name: "plan.md", ext: "md", modifiedAt: new Date().toISOString() };
  const fetch = vi.fn().mockImplementation((path) => {
    if (path.endsWith("/files")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => [file] });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [PROJECT] });
  });
  vi.stubGlobal("fetch", fetch);
  vi.stubGlobal("prompt", vi.fn().mockReturnValue(""));
  window.history.pushState(null, "", "/p/p1");

  render(<App />);
  await waitFor(() => expect(screen.getByText("plan.md")).toBeTruthy());
  fireEvent.click(screen.getByRole("button", { name: "Rename plan.md" }));
  expect(fetch.mock.calls.every(([, options]) => options?.method !== "PATCH")).toBe(true);
});

test("⌘K is bound to nothing", async () => {
  // Search is gone with its three parts: the sidebar button, ⌘K and the layer.
  stubProjects([]);
  render(<App />);
  fireEvent.keyDown(window, { key: "k", metaKey: true });
  fireEvent.keyDown(window, { key: "k", ctrlKey: true });
  await waitFor(() => expect(screen.getByText("QueenAgent")).toBeTruthy());
  expect(screen.queryByTestId("search")).toBeNull();
});

test("Escape closes the reading panel", async () => {
  const file = { name: "plan.md", ext: "md", modifiedAt: new Date().toISOString() };
  const fetch = vi.fn().mockImplementation((path) => {
    if (path.endsWith("/files/plan.md")) {
      return Promise.resolve({
        ok: true,
        status: 200,
        json: async () => ({ ...file, size: 4, text: "body" }),
      });
    }
    if (path.endsWith("/files")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => [file] });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [PROJECT] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1");

  render(<App />);
  await waitFor(() => expect(screen.getByText("plan.md")).toBeTruthy());
  fireEvent.click(screen.getByText("plan.md"));
  await waitFor(() => expect(screen.getByText("body")).toBeTruthy());

  fireEvent.keyDown(window, { key: "Escape" });
  await waitFor(() => expect(screen.queryByText("body")).toBeNull());
  // Escape closes; it never steps backwards.
  expect(window.location.pathname).toBe("/p/p1");
});

test("nothing asks the server to search", async () => {
  const fetch = vi.fn().mockImplementation(() =>
    Promise.resolve({ ok: true, status: 200, json: async () => [PROJECT] }),
  );
  vi.stubGlobal("fetch", fetch);

  render(<App />);
  await waitFor(() => expect(screen.getByText("QueenAgent")).toBeTruthy());
  fireEvent.keyDown(window, { key: "k", metaKey: true });

  expect(fetch.mock.calls.every(([path]) => !String(path).startsWith("/api/search"))).toBe(true);
});

function goOffline(offline) {
  Object.defineProperty(window.navigator, "onLine", { value: !offline, configurable: true });
  window.dispatchEvent(new Event(offline ? "offline" : "online"));
}

test("offline, the strip shows and the composer stays open", async () => {
  goOffline(true);
  stubProjects([]);
  render(<App />);
  await waitFor(() => expect(screen.getByTestId("offline")).toBeTruthy());
  // The composer is not taken away: what is offline is the engine, not the machine.
  expect(screen.getByPlaceholderText(/Ask anything/)).toBeTruthy();
  goOffline(false);
  await waitFor(() => expect(screen.queryByTestId("offline")).toBeNull());
});

test("offline, no answer is asked for; back online, one is", async () => {
  const owed = {
    id: "c1",
    title: "hello",
    messages: [{ role: "user", at: new Date().toISOString(), text: "hello" }],
  };
  const answered = {
    ...owed,
    messages: [...owed.messages, { role: "ai", at: new Date().toISOString(), text: "Done." }],
  };
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (path.endsWith("/answer") && options?.method === "POST") {
      return Promise.resolve(
        sseResponse(`event: done\ndata: ${JSON.stringify(answered)}\n\n`),
      );
    }
    if (path.endsWith("/chats/c1")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => owed });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [] });
  });
  vi.stubGlobal("fetch", fetch);
  goOffline(true);
  window.history.pushState(null, "", "/p/p1/c/c1");

  render(<App />);
  // The title says "hello" too, so the bubble is asked for by name.
  await waitFor(() => expect(screen.getByText("hello", { selector: ".msg__bubble" })).toBeTruthy());
  expect(fetch.mock.calls.some(([path]) => path.endsWith("/answer"))).toBe(false);

  // The chat is still owed an answer, so the connection coming back is the whole mechanism.
  goOffline(false);
  await waitFor(() => expect(screen.getByText("Done.")).toBeTruthy());
});

test("an empty prompt sends nothing", async () => {
  const fetch = vi.fn().mockResolvedValue({ ok: true, status: 200, json: async () => [PROJECT] });
  vi.stubGlobal("fetch", fetch);
  vi.stubGlobal("prompt", vi.fn().mockReturnValue(""));
  window.history.pushState(null, "", "/p/p1");

  render(<App />);
  await waitFor(() => expect(screen.getByRole("button", { name: "Rename" })).toBeTruthy());
  fireEvent.click(screen.getByRole("button", { name: "Rename" }));
  expect(fetch.mock.calls.every(([, options]) => options?.method !== "PATCH")).toBe(true);
});
