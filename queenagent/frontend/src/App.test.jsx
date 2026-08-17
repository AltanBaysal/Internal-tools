import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";

import App from "./App.jsx";

afterEach(() => {
  vi.unstubAllGlobals();
  // jsdom shares one document across tests, so a pushed address has to be put back.
  window.history.pushState(null, "", "/");
  Object.defineProperty(window.navigator, "onLine", { value: true, configurable: true });
});

const PROJECT = { id: "p1", name: "Old", chats: 0, files: 0 };

function stubProjects(projects) {
  const fetch = vi.fn().mockResolvedValue({ ok: true, status: 200, json: async () => projects });
  vi.stubGlobal("fetch", fetch);
  return fetch;
}

test("the shell renders", () => {
  stubProjects([]);
  render(<App />);
  expect(screen.getByTestId("app-shell")).toBeTruthy();
});

test("the app opens on the first project", async () => {
  // "/" is a fork, not a screen: with a project to show, the app lands inside it.
  stubProjects([{ id: "p1", name: "Thesis", chats: 0, files: 0 }]);
  render(<App />);
  await waitFor(() => expect(window.location.pathname).toBe("/p/p1"));
  // The sidebar row and the project title read the same array, so the name stands twice.
  expect(screen.getAllByText("Thesis").length).toBe(2);
});

test("with no projects the fork draws the empty screen and stays at /", async () => {
  stubProjects([]);
  render(<App />);
  await waitFor(() => expect(screen.getByText("No projects yet")).toBeTruthy());
  expect(window.location.pathname).toBe("/");
  // No dead control beside an empty screen.
  expect(screen.queryByRole("button", { name: /New chat/ })).toBeNull();
});

test("the fork is not written into the history", async () => {
  const push = vi.spyOn(window.history, "pushState");
  const replace = vi.spyOn(window.history, "replaceState");
  stubProjects([{ id: "p1", name: "Thesis", chats: 0, files: 0 }]);

  render(<App />);
  await waitFor(() => expect(window.location.pathname).toBe("/p/p1"));
  // Pushed, the back button would land on the fork and be thrown forward again.
  expect(replace).toHaveBeenCalled();
  expect(push).not.toHaveBeenCalled();
});

// --- deleting a project ------------------------------------------------------------------------

const TWO = [
  { id: "p1", name: "Thesis", chats: 3, files: 2 },
  { id: "p2", name: "Notes", chats: 1, files: 0 },
];

// The list answers the GET, and the DELETE takes a project out of it, so what the screen shows after
// a delete is the server's answer rather than a guess made here.
function serverWith(projects) {
  const live = [...projects];
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (path.startsWith("/api/projects/") && options?.method === "DELETE") {
      const id = path.slice("/api/projects/".length);
      const at = live.findIndex((project) => project.id === id);
      live.splice(at, 1);
      return Promise.resolve({ ok: true, status: 200, json: async () => ({ trashed: id }) });
    }
    if (path === "/api/projects") {
      return Promise.resolve({ ok: true, status: 200, json: async () => [...live] });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [] });
  });
  vi.stubGlobal("fetch", fetch);
  return fetch;
}

const openMenuFor = (name) =>
  fireEvent.click(screen.getByRole("button", { name: `More for ${name}` }));

test("the sidebar menu and the header open the same question", async () => {
  serverWith(TWO);
  render(<App />);
  await waitFor(() => expect(window.location.pathname).toBe("/p/p1"));

  openMenuFor("Thesis");
  fireEvent.click(screen.getByRole("button", { name: "Delete project" }));
  expect(screen.getByText('Delete "Thesis"?')).toBeTruthy();
  fireEvent.click(screen.getByRole("button", { name: "Cancel" }));

  fireEvent.click(screen.getByRole("button", { name: "Delete" }));
  expect(screen.getByText('Delete "Thesis"?')).toBeTruthy();
});

test("the box counts what goes with the project", async () => {
  serverWith(TWO);
  render(<App />);
  await waitFor(() => expect(window.location.pathname).toBe("/p/p1"));
  openMenuFor("Thesis");
  fireEvent.click(screen.getByRole("button", { name: "Delete project" }));
  expect(
    screen.getByText("The 3 chats and 2 files in this project are deleted with it. This can't be undone."),
  ).toBeTruthy();
});

test("one of a thing is one, not one of them", async () => {
  serverWith(TWO);
  render(<App />);
  await waitFor(() => expect(window.location.pathname).toBe("/p/p1"));
  openMenuFor("Notes");
  fireEvent.click(screen.getByRole("button", { name: "Delete project" }));
  expect(screen.getByText(/The 1 chat and 0 files/)).toBeTruthy();
});

test("cancelling asks the server nothing", async () => {
  const fetch = serverWith(TWO);
  render(<App />);
  await waitFor(() => expect(window.location.pathname).toBe("/p/p1"));
  openMenuFor("Thesis");
  fireEvent.click(screen.getByRole("button", { name: "Delete project" }));
  fireEvent.click(screen.getByRole("button", { name: "Cancel" }));
  expect(fetch.mock.calls.filter(([, options]) => options?.method === "DELETE")).toEqual([]);
  expect(screen.queryByText('Delete "Thesis"?')).toBeNull();
});

test("deleting the project you are in moves to the first one left", async () => {
  serverWith(TWO);
  render(<App />);
  await waitFor(() => expect(window.location.pathname).toBe("/p/p1"));
  openMenuFor("Thesis");
  fireEvent.click(screen.getByRole("button", { name: "Delete project" }));
  fireEvent.click(screen.getByRole("button", { name: "Delete project" }));
  await waitFor(() => expect(window.location.pathname).toBe("/p/p2"));
  expect(screen.queryByText("Thesis")).toBeNull();
});

test("deleting the last project leaves the empty screen", async () => {
  serverWith([TWO[0]]);
  render(<App />);
  await waitFor(() => expect(window.location.pathname).toBe("/p/p1"));
  openMenuFor("Thesis");
  fireEvent.click(screen.getByRole("button", { name: "Delete project" }));
  fireEvent.click(screen.getByRole("button", { name: "Delete project" }));
  await waitFor(() => expect(screen.getByText("No projects yet")).toBeTruthy());
});

test("deleting another project leaves where you are alone", async () => {
  serverWith(TWO);
  render(<App />);
  await waitFor(() => expect(window.location.pathname).toBe("/p/p1"));
  openMenuFor("Notes");
  fireEvent.click(screen.getByRole("button", { name: "Delete project" }));
  fireEvent.click(screen.getByRole("button", { name: "Delete project" }));
  await waitFor(() => expect(screen.queryByText("Notes")).toBeNull());
  // Nothing about the screen the user was on has any business changing.
  expect(window.location.pathname).toBe("/p/p1");
});

test("a deleted project is not offered back", async () => {
  serverWith(TWO);
  render(<App />);
  await waitFor(() => expect(window.location.pathname).toBe("/p/p1"));
  openMenuFor("Notes");
  fireEvent.click(screen.getByRole("button", { name: "Delete project" }));
  fireEvent.click(screen.getByRole("button", { name: "Delete project" }));
  await waitFor(() => expect(screen.queryByText("Notes")).toBeNull());
  // Undo is gone by karar 16: the question was the protection, and the disk keeps the directory.
  expect(screen.queryByText("Undo")).toBeNull();
});

test("Escape closes the menu first, then the question", async () => {
  serverWith(TWO);
  const { container } = render(<App />);
  await waitFor(() => expect(window.location.pathname).toBe("/p/p1"));

  openMenuFor("Thesis");
  expect(container.querySelector(".row-menu")).toBeTruthy();
  fireEvent.keyDown(window, { key: "Escape" });
  // Asked for by shape rather than by name: the project header carries a Rename of its own.
  expect(container.querySelector(".row-menu")).toBeNull();

  openMenuFor("Thesis");
  fireEvent.click(screen.getByRole("button", { name: "Delete project" }));
  fireEvent.keyDown(window, { key: "Escape" });
  expect(screen.queryByText('Delete "Thesis"?')).toBeNull();
});

test("nothing is drawn while the list is still on its way", () => {
  // An empty array cannot tell "none" from "not here yet", and guessing shows the wrong screen.
  vi.stubGlobal("fetch", vi.fn().mockReturnValue(new Promise(() => {})));
  render(<App />);
  expect(screen.queryByText("No projects yet")).toBeNull();
  expect(screen.queryByRole("button", { name: "Rename" })).toBeNull();
  // Not even blocks standing in for cards: the fork has no screen of its own to fill.
  expect(screen.queryByTestId("skeleton")).toBeNull();
});

test("a list that fails to load says so instead of claiming there are none", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({ ok: false, status: 500, text: async () => "" }),
  );
  render(<App />);
  await waitFor(() => expect(screen.getByText(/HTTP 500/)).toBeTruthy());
  expect(screen.queryByText("No projects yet")).toBeNull();
  // And no way to send a message either -- there is no project for one to land in.
  expect(screen.queryByPlaceholderText(/Ask anything/)).toBeNull();
});

test("a project address that matches nothing says so", async () => {
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

test("nothing is asked of a workspace-wide chat address", async () => {
  // A chat is always started from inside a project, and Recent chats now lists that project's own
  // chats -- so nothing reaches /api/chats at all, by any method.
  const fetch = stubProjects([]);
  render(<App />);
  await waitFor(() => expect(screen.getByText("No projects yet")).toBeTruthy());
  expect(fetch.mock.calls.every(([path]) => path !== "/api/chats")).toBe(true);
});

test("New chat opens an empty chat in the project it was pressed in", async () => {
  const fetch = vi.fn().mockImplementation((path) => {
    if (path === "/api/projects/p1/chats") {
      return Promise.resolve({ ok: true, status: 200, json: async () => [] });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [PROJECT] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1");

  render(<App />);
  await waitFor(() => expect(screen.getByRole("button", { name: /New chat/ })).toBeTruthy());
  fireEvent.click(screen.getByRole("button", { name: /New chat/ }));

  await waitFor(() => expect(window.location.pathname).toBe("/p/p1/c/new"));
  expect(screen.getByText("New chat", { selector: ".chat__title" })).toBeTruthy();
  // There is no chat to read yet, so nothing is asked for one.
  expect(fetch.mock.calls.every(([path]) => !String(path).endsWith("/chats/new"))).toBe(true);
});

test("the first message in a draft creates the chat and takes its address", async () => {
  const chat = { id: "c1", title: "Write the intro", messages: [], lastActivity: "x" };
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (path === "/api/projects/p1/chats" && options?.method === "POST") {
      return Promise.resolve({ ok: true, status: 201, json: async () => chat });
    }
    if (path.endsWith("/chats/c1")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => chat });
    }
    if (path === "/api/projects/p1/chats") {
      return Promise.resolve({ ok: true, status: 200, json: async () => [chat] });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [PROJECT] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/new");
  const push = vi.spyOn(window.history, "pushState");

  render(<App />);
  await waitFor(() => expect(screen.getByPlaceholderText("Reply...")).toBeTruthy());
  fireEvent.change(screen.getByPlaceholderText("Reply..."), {
    target: { value: "Write the intro" },
  });
  fireEvent.keyDown(screen.getByPlaceholderText("Reply..."), { key: "Enter" });

  await waitFor(() => expect(window.location.pathname).toBe("/p/p1/c/c1"));
  // The draft address is not a place to go back to: it no longer exists.
  expect(push).not.toHaveBeenCalled();
});

test("the user bubble shows before the server answers, and a refusal hands the words back", async () => {
  const chat = { id: "c1", title: "Hi", messages: [], lastActivity: "x" };
  let refuse;
  const pending = new Promise((resolve) => {
    refuse = () =>
      resolve({
        ok: false,
        status: 400,
        text: async () => JSON.stringify({ error: "a message needs text" }),
      });
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
  // The server's own sentence, not the method and the code the browser used to write instead.
  expect(screen.getByText("a message needs text")).toBeTruthy();
  // A message that was never sent has no answer to retry.
  expect(screen.queryByText("Couldn't get a response.")).toBeNull();
  // And FOUNDATION's first principle: the sentence the user wrote comes back to them.
  expect(screen.getByPlaceholderText("Reply...").value).toBe("hello");
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
      return Promise.resolve({ ok: false, status: 502, text: async () => "" });
    }
    if (path.endsWith("/chats/c1")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => owed });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/c1");

  render(<App />);
  await waitFor(() => expect(screen.getByText(/HTTP 502/)).toBeTruthy());
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
  // Asked for by its control: the title itself now stands twice, in the row and in the sidebar.
  await waitFor(() =>
    expect(screen.getByRole("button", { name: "Delete Write the intro" })).toBeTruthy(),
  );
  fireEvent.click(screen.getByRole("button", { name: "Delete Write the intro" }));

  expect(window.confirm).toHaveBeenCalled();
  expect(fetch.mock.calls.every(([, options]) => options?.method !== "DELETE")).toBe(true);
});

test("a chat the user confirms is deleted and leaves the list", async () => {
  let chats = [{ id: "c1", title: "Write the intro", lastActivity: new Date().toISOString() }];
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (options?.method === "DELETE") {
      chats = [];
      return Promise.resolve({ ok: true, status: 200, json: async () => ({}) });
    }
    if (path === "/api/projects/p1/chats") {
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

test("no row anywhere offers a rename", async () => {
  // Renaming lives on the project alone, so neither a file row nor a chat row carries one.
  const file = { name: "plan.md", ext: "md", modifiedAt: new Date().toISOString() };
  const chats = [{ id: "c1", title: "Write the intro", lastActivity: new Date().toISOString() }];
  const fetch = vi.fn().mockImplementation((path) => {
    if (path.endsWith("/files")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => [file] });
    }
    if (path === "/api/projects/p1/chats") {
      return Promise.resolve({ ok: true, status: 200, json: async () => chats });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [PROJECT] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1");

  render(<App />);
  await waitFor(() => expect(screen.getByText("plan.md")).toBeTruthy());
  expect(screen.queryByRole("button", { name: "Rename plan.md" })).toBeNull();
  expect(screen.queryByRole("button", { name: "Rename Write the intro" })).toBeNull();
  // The project's own Rename is the one that stays.
  expect(screen.getByRole("button", { name: "Rename" })).toBeTruthy();
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
  const fetch = stubProjects([]);

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
  // Inside a project, because that is now the only place a composer stands.
  stubProjects([PROJECT]);
  window.history.pushState(null, "", "/p/p1");
  render(<App />);
  await waitFor(() => expect(screen.getByTestId("offline")).toBeTruthy());
  // The composer is not taken away: what is offline is the engine, not the machine.
  expect(screen.getByPlaceholderText(/Start a new chat/)).toBeTruthy();
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
