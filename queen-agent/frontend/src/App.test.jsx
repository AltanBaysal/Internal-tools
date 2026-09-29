import { act, cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";

import App from "./App.jsx";

afterEach(() => {
  vi.unstubAllGlobals();
  // jsdom shares one document across tests, so a pushed address has to be put back.
  window.history.pushState(null, "", "/");
  Object.defineProperty(window.navigator, "onLine", { value: true, configurable: true });
});

const PROJECT = { id: "p1", name: "Old", chats: 0, files: 0 };
// A second project, so a test can tell the project the user is in from the first one on the list.
const PROJECT_2 = { id: "p2", name: "Newer", chats: 0, files: 0 };

function stubProjects(projects) {
  const fetch = vi.fn().mockResolvedValue({ ok: true, status: 200, json: async () => projects });
  vi.stubGlobal("fetch", fetch);
  return fetch;
}

const NOW = new Date().toISOString();
const THESIS = { id: "p1", name: "Thesis", chats: 2, files: 0, pinned: false, lastActivity: NOW };
const ok = (body, status = 200) => Promise.resolve({ ok: true, status, json: async () => body });

// Madde 353: projects, each project's chats, a chat record for any id, and a POST that makes one
// the server then lists first -- where it puts a project nobody has used since it was born. Madde
// 361: the project is born under the name the POST carries.
function serverWithProjects(projects, chatsOf = {}) {
  const live = [...projects];
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (path === "/api/projects" && options?.method === "POST") {
      const born = {
        id: "p9",
        name: JSON.parse(options.body).name,
        chats: 0,
        files: 0,
        pinned: false,
        lastActivity: NOW,
      };
      live.unshift(born);
      return ok(born, 201);
    }
    if (path === "/api/projects") return ok([...live]);
    const list = path.match(/^\/api\/projects\/(\w+)\/chats$/);
    if (list) return ok(chatsOf[list[1]] ?? []);
    const record = path.match(/\/chats\/(\w+)$/);
    if (record) return ok({ id: record[1], title: record[1], messages: [] });
    return ok([]);
  });
  vi.stubGlobal("fetch", fetch);
  return fetch;
}

// Madde 355: a chat's frame stands from the moment it opens, its box and pickers shut until the
// record is read. What a test types or picks in a chat waits for the box to open.
const chatOpened = () =>
  waitFor(() => {
    const box = screen.getByPlaceholderText("Reply...");
    expect(box.disabled).toBe(false);
    return box;
  });

test("the shell renders", () => {
  stubProjects([]);
  render(<App />);
  expect(screen.getByTestId("app-shell")).toBeTruthy();
});

// Madde 338: one bar across the window's top, on every screen. Madde 353: All projects has no
// sidebar, and while its list is on the way the head stands with nothing where the list will be --
// no sentence claiming there are none.
test("while the first list loads, All projects stands under the bar with nothing where the list will be", async () => {
  let answer;
  vi.stubGlobal(
    "fetch",
    vi.fn().mockReturnValue(
      new Promise((resolve) => {
        answer = () => resolve({ ok: true, status: 200, json: async () => [] });
      }),
    ),
  );
  render(<App />);
  const shell = screen.getByTestId("app-shell");
  expect(shell.children[0].className).toBe("bar");
  const body = shell.children[1];
  expect(body.className).toBe("app-shell__body");
  expect(shell.querySelector(".main").parentElement).toBe(body);
  expect(shell.querySelector(".sidebar")).toBeNull();
  expect(screen.getByText("All projects", { selector: ".screen__title" })).toBeTruthy();
  expect(screen.queryByText("No projects yet.")).toBeNull();

  await act(async () => {
    answer();
  });
  expect(await screen.findByText("No projects yet.")).toBeTruthy();
});

test("with no project at all, the bar holds the brand alone", async () => {
  stubProjects([]);
  render(<App />);
  await screen.findByText(/No projects yet/);
  const bar = screen.getByTestId("app-shell").querySelector(".bar");
  expect(bar.textContent).toContain("QueenAgent");
  expect(bar.querySelector(".bar__project")).toBeNull();
  expect(screen.queryByRole("button", { name: "Exit project" })).toBeNull();
});

// The chat is the second project's, so the bar is seen naming the project the user is in rather
// than the first one on the list.
function stubChatInSecondProject() {
  const chat = { id: "c1", title: "Draft", messages: [] };
  vi.stubGlobal(
    "fetch",
    vi.fn().mockImplementation((path) => {
      if (path.endsWith("/chats/c1")) {
        return Promise.resolve({ ok: true, status: 200, json: async () => chat });
      }
      if (path.endsWith("/chats") || path.endsWith("/files")) {
        return Promise.resolve({ ok: true, status: 200, json: async () => [] });
      }
      return Promise.resolve({ ok: true, status: 200, json: async () => [PROJECT, PROJECT_2] });
    }),
  );
  window.history.pushState(null, "", "/p/p2/c/c1");
}

test("in a chat, the bar carries the project's name and the way out of it", async () => {
  stubChatInSecondProject();
  render(<App />);
  expect(await screen.findByText("Newer", { selector: ".bar__project" })).toBeTruthy();
  expect(screen.getByRole("button", { name: "Exit project" })).toBeTruthy();
});

test("Exit project goes back to All projects", async () => {
  // Madde 353: the opening is All projects now, not a fork that lands in the first project.
  stubChatInSecondProject();
  render(<App />);
  await screen.findByText("Newer", { selector: ".bar__project" });
  fireEvent.click(screen.getByRole("button", { name: "Exit project" }));
  await screen.findByText("All projects", { selector: ".screen__title" });
  expect(window.location.pathname).toBe("/");
});

test("an address is not called wrong before the list has arrived", async () => {
  window.history.pushState(null, "", "/p/p1");
  let answer;
  vi.stubGlobal(
    "fetch",
    vi.fn().mockReturnValue(
      new Promise((resolve) => {
        answer = () => resolve({ ok: true, status: 200, json: async () => [] });
      }),
    ),
  );
  render(<App />);
  // Saying "does not exist" about a list nobody has answered yet is the same untruth Madde 32 took
  // out of the file column, one level up.
  expect(screen.queryByText("That project does not exist.")).toBeNull();

  await act(async () => {
    answer();
  });
  await waitFor(() => expect(screen.getByText("That project does not exist.")).toBeTruthy());
});

test("/settings is an address like any other unknown one: it draws All projects", async () => {
  // Madde 62's trap, one screen later. An unknown address parses to "/", and "/" is a screen now
  // rather than a fork, so what it draws is the opening -- never a blank page.
  stubProjects([PROJECT]);
  window.history.pushState(null, "", "/settings");
  render(<App />);

  await screen.findByText("Old", { selector: ".all-projects__row-name" });
  expect(screen.getByText("All projects", { selector: ".screen__title" })).toBeTruthy();
});

test("the app never asks the server for settings", async () => {
  // There is no endpoint left to ask. Said as a test because the call was made on mount, before any
  // screen was drawn -- so nothing on screen would have shown it was still happening.
  const fetch = stubProjects([PROJECT]);
  render(<App />);

  // Any drawn screen will do -- the claim is about a call made on mount.
  await screen.findByText("Old", { selector: ".all-projects__row-name" });
  const asked = fetch.mock.calls.filter(([path]) => String(path).startsWith("/api/settings"));
  expect(asked).toEqual([]);
});

test("the shell wears the step it was measured at", () => {
  stubProjects([]);
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
  render(<App />);
  // Unmeasured is the wide layout: zero is the absence of an answer, not a narrow screen.
  expect(screen.getByTestId("app-shell").className).toBe("app-shell");

  act(() => observers.forEach((callback) => callback([{ contentRect: { width: 600 } }])));
  expect(screen.getByTestId("app-shell").className).toContain("app-shell--compact");
});

// --- All projects, and the way into a project (Madde 353) ---------------------------------------

test("the app opens on All projects, and stays there", async () => {
  // "/" was a fork that landed in the first project. It is a screen now, and it has no sidebar:
  // no project is open on it (the design's items 135, 167).
  serverWithProjects([THESIS]);
  const { container } = render(<App />);
  await screen.findByText("Thesis", { selector: ".all-projects__row-name" });
  expect(window.location.pathname).toBe("/");
  expect(screen.getByText("All projects", { selector: ".screen__title" })).toBeTruthy();
  expect(container.querySelector(".sidebar")).toBeNull();
});

test("with no projects, All projects says so and stays at /", async () => {
  stubProjects([]);
  render(<App />);
  expect(await screen.findByText("No projects yet.")).toBeTruthy();
  expect(window.location.pathname).toBe("/");
  // No dead control beside an empty list.
  expect(screen.queryByRole("button", { name: /New chat/ })).toBeNull();
});

test("a row opens the project's latest chat", async () => {
  // The server's list comes newest first, so its first row is the one to open (design 170).
  serverWithProjects([THESIS], {
    p1: [
      { id: "c2", title: "Newest", lastActivity: NOW },
      { id: "c1", title: "Older", lastActivity: NOW },
    ],
  });
  render(<App />);
  fireEvent.click(await screen.findByRole("button", { name: /^Thesis/ }));
  await waitFor(() => expect(window.location.pathname).toBe("/p/p1/c/c2"));
});

test("a project with no chats opens on its draft", async () => {
  serverWithProjects([THESIS]);
  render(<App />);
  fireEvent.click(await screen.findByRole("button", { name: /^Thesis/ }));
  await waitFor(() => expect(window.location.pathname).toBe("/p/p1/c/new"));
  expect(screen.getByText("New chat", { selector: ".chat__title" })).toBeTruthy();
});

test("the way into a project is written into the history once", async () => {
  // The press is a step and is pushed; /p/<id> has no screen of its own, so the chat it opens
  // writes over it -- or the back button would land there and be thrown forward again.
  serverWithProjects([THESIS], { p1: [{ id: "c2", title: "Newest", lastActivity: NOW }] });
  const push = vi.spyOn(window.history, "pushState");
  const replace = vi.spyOn(window.history, "replaceState");
  render(<App />);
  fireEvent.click(await screen.findByRole("button", { name: /^Thesis/ }));
  await waitFor(() => expect(window.location.pathname).toBe("/p/p1/c/c2"));
  expect(push.mock.calls.map(([, , to]) => to)).toEqual(["/p/p1"]);
  expect(replace.mock.calls.map(([, , to]) => to)).toEqual(["/p/p1/c/c2"]);
});

test("a project's own address opens its latest chat", async () => {
  serverWithProjects([THESIS], { p1: [{ id: "c1", title: "Only", lastActivity: NOW }] });
  window.history.pushState(null, "", "/p/p1");
  render(<App />);
  await waitFor(() => expect(window.location.pathname).toBe("/p/p1/c/c1"));
});

test("leaving before the project's chats arrive stays where the user went", async () => {
  // The answer is about a place the user has left; it must not pull them back into it.
  const waiting = [];
  vi.stubGlobal(
    "fetch",
    vi.fn().mockImplementation((path) => {
      if (path === "/api/projects/p1/chats") {
        return new Promise((resolve) => waiting.push(resolve));
      }
      if (path === "/api/projects") return ok([THESIS]);
      return ok([]);
    }),
  );
  window.history.pushState(null, "", "/p/p1");
  render(<App />);
  fireEvent.click(await screen.findByRole("button", { name: "Exit project" }));
  await screen.findByText("All projects", { selector: ".screen__title" });

  await act(async () => {
    waiting.forEach((resolve) =>
      resolve({
        ok: true,
        status: 200,
        json: async () => [{ id: "c1", title: "Late", lastActivity: NOW }],
      }),
    );
  });
  expect(window.location.pathname).toBe("/");
});

// --- the naming screen (Madde 361; the design's items 135, 153, 169, 195) ------------------------

const posts = (fetch) =>
  fetch.mock.calls.filter(
    ([path, options]) => path === "/api/projects" && options?.method === "POST",
  );
const nameField = () => screen.findByPlaceholderText("Project name");
const barExit = () => document.querySelector(".bar__exit");

test("+ New project asks for the name first, and nothing is made yet", async () => {
  const fetch = serverWithProjects([THESIS]);
  const { container } = render(<App />);
  fireEvent.click(await screen.findByRole("button", { name: "+ New project" }));
  expect(await screen.findByLabelText("Name your project")).toBe(await nameField());
  expect(window.location.pathname).toBe("/new");
  expect(posts(fetch)).toEqual([]);
  // No project is open here, so no sidebar and nothing in the bar's middle; the right holds the
  // way back.
  expect(container.querySelector(".sidebar")).toBeNull();
  expect(container.querySelector(".bar__project")).toBeNull();
  expect(barExit().textContent).toBe("Cancel");
});

test("the name typed is the project's, and its draft opens in the naming screen's place", async () => {
  const fetch = serverWithProjects([THESIS]);
  const push = vi.spyOn(window.history, "pushState");
  const replace = vi.spyOn(window.history, "replaceState");
  // A method spied on already hands back the same spy, and an earlier test's calls with it.
  push.mockClear();
  replace.mockClear();
  render(<App />);
  fireEvent.click(await screen.findByRole("button", { name: "+ New project" }));
  const field = await nameField();
  fireEvent.change(field, { target: { value: "Harbour" } });
  fireEvent.keyDown(field, { key: "Enter" });

  await waitFor(() => expect(window.location.pathname).toBe("/p/p9/c/new"));
  // One request, carrying the name: no project is ever left under a name nobody chose.
  expect(posts(fetch).map(([, options]) => JSON.parse(options.body))).toEqual([{ name: "Harbour" }]);
  expect(await screen.findByText("Harbour", { selector: ".bar__project" })).toBeTruthy();
  // The naming screen's work is done: the back button does not land on it to make a second one.
  expect(push.mock.calls.map(([, , to]) => to)).toEqual(["/new"]);
  expect(replace.mock.calls.map(([, , to]) => to)).toEqual(["/p/p9/c/new"]);

  // Where it belongs is the server's order, read again.
  fireEvent.click(screen.getByRole("button", { name: "Exit project" }));
  await screen.findByText("All projects", { selector: ".screen__title" });
  const rows = [...document.querySelectorAll(".all-projects__row-name")].map((row) => row.textContent);
  expect(rows).toEqual(["Harbour", "Thesis"]);
});

test("a blank name makes nothing and stays", async () => {
  const fetch = serverWithProjects([THESIS]);
  render(<App />);
  fireEvent.click(await screen.findByRole("button", { name: "+ New project" }));
  const field = await nameField();
  fireEvent.change(field, { target: { value: "   " } });
  fireEvent.keyDown(field, { key: "Enter" });
  fireEvent.click(screen.getByRole("button", { name: "Create project" }));
  expect(posts(fetch)).toEqual([]);
  expect(window.location.pathname).toBe("/new");
});

test("Cancel goes back to All projects and makes nothing", async () => {
  const fetch = serverWithProjects([THESIS]);
  render(<App />);
  fireEvent.click(await screen.findByRole("button", { name: "+ New project" }));
  await nameField();
  fireEvent.click(screen.getByRole("button", { name: "Cancel" }));
  await screen.findByText("All projects", { selector: ".screen__title" });
  expect(window.location.pathname).toBe("/");
  expect(posts(fetch)).toEqual([]);
});

test("Escape does what Cancel does", async () => {
  serverWithProjects([THESIS]);
  render(<App />);
  fireEvent.click(await screen.findByRole("button", { name: "+ New project" }));
  await nameField();
  fireEvent.keyDown(window, { key: "Escape" });
  await screen.findByText("All projects", { selector: ".screen__title" });
  expect(window.location.pathname).toBe("/");
});

test("reached by its address, the naming screen's Cancel goes to All projects", async () => {
  // Typed by hand or reloaded, there is no screen it was reached from.
  serverWithProjects([THESIS]);
  window.history.pushState(null, "", "/new");
  render(<App />);
  await nameField();
  fireEvent.click(screen.getByRole("button", { name: "Cancel" }));
  await screen.findByText("All projects", { selector: ".screen__title" });
  expect(window.location.pathname).toBe("/");
});

test("with no project yet, it asks for the first one and offers no way back", async () => {
  // The design's 195: at the first launch there is nowhere to leave to, so the bar's right is empty.
  stubProjects([]);
  render(<App />);
  await screen.findByText("No projects yet.");
  fireEvent.click(screen.getByRole("button", { name: "+ New project" }));
  expect(await screen.findByLabelText("Name your first project")).toBe(await nameField());
  expect(barExit()).toBeNull();
  fireEvent.keyDown(window, { key: "Escape" });
  expect(window.location.pathname).toBe("/new");
});

test("a project the server will not make says what the server said", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockImplementation((path, options) => {
      if (options?.method === "POST") {
        return Promise.resolve({
          ok: false,
          status: 500,
          text: async () => JSON.stringify({ error: "the store is unreachable" }),
        });
      }
      return ok(path === "/api/projects" ? [THESIS] : []);
    }),
  );
  window.history.pushState(null, "", "/new");
  render(<App />);
  const field = await nameField();
  fireEvent.change(field, { target: { value: "Harbour" } });
  fireEvent.keyDown(field, { key: "Enter" });
  expect(await screen.findByText("the store is unreachable")).toBeTruthy();
  expect(window.location.pathname).toBe("/new");
  // Madde 364: the refusal is said under the name, which is still there to send again.
  expect((await nameField()).value).toBe("Harbour");
});

test("a chat that does not exist leads back to All projects", async () => {
  // Its ← back went to the project screen, and that screen is gone (design 170).
  vi.stubGlobal(
    "fetch",
    vi.fn().mockImplementation((path) => {
      if (path.endsWith("/chats/nope")) return Promise.resolve(NOT_FOUND);
      if (path === "/api/projects") return ok([THESIS]);
      return ok([]);
    }),
  );
  window.history.pushState(null, "", "/p/p1/c/nope");
  render(<App />);
  await screen.findByText("That chat does not exist.");
  fireEvent.click(screen.getByRole("button", { name: "← back" }));
  await screen.findByText("All projects", { selector: ".screen__title" });
  expect(window.location.pathname).toBe("/");
});

test("the skill picked in a draft is what the chat is born with", async () => {
  // The half that separates a label from a behaviour. Without it, a picker that changes its own
  // caption and nothing else reads exactly like a working one.
  const fetch = serverWithProjects([THESIS]);
  window.history.pushState(null, "", "/p/p1/c/new");
  render(<App />);

  fireEvent.click(await screen.findByRole("button", { name: /Skills/ }));
  fireEvent.click(screen.getByText("Edit prompts", { selector: ".menu__item-name" }));
  const box = screen.getByPlaceholderText("Reply...");
  fireEvent.change(box, { target: { value: "Write it" } });
  fireEvent.keyDown(box, { key: "Enter" });

  await waitFor(() => {
    const started = fetch.mock.calls.find(
      ([path, options]) => String(path).endsWith("/messages") && options?.method === "POST",
    );
    expect(started).toBeTruthy();
    expect(JSON.parse(started[1].body).skill).toBe("edit-prompts");
  });
});

// --- the row's ⋯ on All projects (Madde 360) -----------------------------------------------------

const ROW_HOUR = 3600_000;
const hoursAgo = (hours) => new Date(Date.now() - hours * ROW_HOUR).toISOString();
const ROWS = [
  { id: "p1", name: "Thesis", chats: 3, files: 2, pinned: false, lastActivity: hoursAgo(1) },
  { id: "p2", name: "Notes", chats: 1, files: 0, pinned: false, lastActivity: hoursAgo(5) },
];

// A server that keeps its own order -- the pinned first, in the order they were pinned, then the
// most recently used (list_projects.py) -- so where a row stands after a pin or an unpin is the
// server's answer rather than a guess made on the screen. A DELETE takes the project out of it.
function serverForRows(projects) {
  let live = projects.map((project) => ({ pinnedAt: 0, ...project }));
  let pins = 0;
  const listed = () => [
    ...live.filter((project) => project.pinned).sort((a, b) => a.pinnedAt - b.pinnedAt),
    ...live
      .filter((project) => !project.pinned)
      .sort((a, b) => b.lastActivity.localeCompare(a.lastActivity)),
  ];
  const fetch = vi.fn().mockImplementation((path, options) => {
    const one = path.match(/^\/api\/projects\/(\w+)$/);
    if (one && options?.method === "DELETE") {
      live = live.filter((project) => project.id !== one[1]);
      return ok({ trashed: one[1] });
    }
    if (one && options?.method === "PATCH") {
      const changes = JSON.parse(options.body);
      live = live.map((project) =>
        project.id === one[1]
          ? { ...project, ...changes, pinnedAt: changes.pinned ? ++pins : project.pinnedAt }
          : project,
      );
      return ok(live.find((project) => project.id === one[1]));
    }
    if (path === "/api/projects") return ok(listed());
    return ok([]);
  });
  vi.stubGlobal("fetch", fetch);
  return fetch;
}

const actionsFor = (name) =>
  fireEvent.click(screen.getByRole("button", { name: `Actions for ${name}` }));
const onAllProjects = () => screen.findByText("Thesis", { selector: ".all-projects__row-name" });
const sections = (container) =>
  Object.fromEntries(
    [...container.querySelectorAll(".all-projects__section")].map((section) => [
      section.querySelector(".all-projects__label").textContent,
      [...section.querySelectorAll(".all-projects__row-name")].map((name) => name.textContent),
    ]),
  );
const patches = (fetch) => fetch.mock.calls.filter(([, options]) => options?.method === "PATCH");

test("a row's Delete asks first", async () => {
  serverForRows(ROWS);
  render(<App />);
  await onAllProjects();
  actionsFor("Thesis");
  fireEvent.click(screen.getByRole("button", { name: "Delete" }));
  expect(screen.getByText('Delete "Thesis"?')).toBeTruthy();
});

test("the question counts what goes with the project, one of a thing being one", async () => {
  serverForRows(ROWS);
  render(<App />);
  await onAllProjects();
  actionsFor("Thesis");
  fireEvent.click(screen.getByRole("button", { name: "Delete" }));
  expect(
    screen.getByText("The 3 chats and 2 files in this project are deleted with it. This can't be undone."),
  ).toBeTruthy();
  fireEvent.click(screen.getByRole("button", { name: "Cancel" }));

  actionsFor("Notes");
  fireEvent.click(screen.getByRole("button", { name: "Delete" }));
  expect(screen.getByText(/The 1 chat and 0 files/)).toBeTruthy();
});

test("cancelling asks the server nothing", async () => {
  const fetch = serverForRows(ROWS);
  render(<App />);
  await onAllProjects();
  actionsFor("Thesis");
  fireEvent.click(screen.getByRole("button", { name: "Delete" }));
  fireEvent.click(screen.getByRole("button", { name: "Cancel" }));
  expect(fetch.mock.calls.filter(([, options]) => options?.method === "DELETE")).toEqual([]);
  expect(screen.queryByText('Delete "Thesis"?')).toBeNull();
});

test("confirming deletes the project, and All projects stays where it is", async () => {
  const fetch = serverForRows(ROWS);
  render(<App />);
  await onAllProjects();
  actionsFor("Notes");
  fireEvent.click(screen.getByRole("button", { name: "Delete" }));
  // The menu closed on the choice, so the one Delete left is the question's own.
  fireEvent.click(screen.getByRole("button", { name: "Delete" }));
  await waitFor(() => expect(screen.queryByText("Notes")).toBeNull());
  const deletes = fetch.mock.calls.filter(([, options]) => options?.method === "DELETE");
  expect(deletes.map(([path]) => path)).toEqual(["/api/projects/p2"]);
  expect(screen.getByText("Thesis", { selector: ".all-projects__row-name" })).toBeTruthy();
  expect(window.location.pathname).toBe("/");
  // Undo is gone by karar 16: the question was the protection, and the disk keeps the directory.
  expect(screen.queryByText("Undo")).toBeNull();
});

test("deleting the last project leaves No projects yet.", async () => {
  serverForRows([ROWS[0]]);
  render(<App />);
  await onAllProjects();
  actionsFor("Thesis");
  fireEvent.click(screen.getByRole("button", { name: "Delete" }));
  fireEvent.click(screen.getByRole("button", { name: "Delete" }));
  expect(await screen.findByText("No projects yet.")).toBeTruthy();
});

test("Escape closes the menu first, then the question", async () => {
  serverForRows(ROWS);
  const { container } = render(<App />);
  await onAllProjects();

  actionsFor("Thesis");
  expect(container.querySelector(".menu")).toBeTruthy();
  fireEvent.keyDown(window, { key: "Escape" });
  expect(container.querySelector(".menu")).toBeNull();

  actionsFor("Thesis");
  fireEvent.click(screen.getByRole("button", { name: "Delete" }));
  fireEvent.keyDown(window, { key: "Escape" });
  expect(screen.queryByText('Delete "Thesis"?')).toBeNull();
});

test("Rename renames in the row's own place, never through the browser's box", async () => {
  const fetch = serverForRows(ROWS);
  const prompt = vi.fn();
  vi.stubGlobal("prompt", prompt);
  render(<App />);
  await onAllProjects();
  actionsFor("Thesis");
  fireEvent.click(screen.getByRole("button", { name: "Rename" }));
  const field = screen.getByRole("textbox", { name: "Project name" });
  fireEvent.change(field, { target: { value: "Dissertation" } });
  fireEvent.keyDown(field, { key: "Enter" });
  expect(
    await screen.findByText("Dissertation", { selector: ".all-projects__row-name" }),
  ).toBeTruthy();
  expect(patches(fetch).map(([path, options]) => [path, JSON.parse(options.body)])).toEqual([
    ["/api/projects/p1", { name: "Dissertation" }],
  ]);
  expect(prompt).not.toHaveBeenCalled();
});

test("an empty name sends nothing", async () => {
  const fetch = serverForRows(ROWS);
  render(<App />);
  await onAllProjects();
  actionsFor("Thesis");
  fireEvent.click(screen.getByRole("button", { name: "Rename" }));
  const field = screen.getByRole("textbox", { name: "Project name" });
  fireEvent.change(field, { target: { value: "  " } });
  fireEvent.keyDown(field, { key: "Enter" });
  expect(patches(fetch)).toEqual([]);
  expect(screen.getByText("Thesis", { selector: ".all-projects__row-name" })).toBeTruthy();
});

test("Pin puts the project under Pinned", async () => {
  const fetch = serverForRows(ROWS);
  const { container } = render(<App />);
  await onAllProjects();
  actionsFor("Notes");
  fireEvent.click(screen.getByRole("button", { name: "Pin" }));
  await waitFor(() =>
    expect(sections(container)).toEqual({ Pinned: ["Notes"], Recent: ["Thesis"] }),
  );
  expect(patches(fetch).map(([path, options]) => [path, JSON.parse(options.body)])).toEqual([
    ["/api/projects/p2", { pinned: true }],
  ]);
});

test("Unpin puts the project back where the server lists it", async () => {
  // Used longest ago, so the server lists it last among the recent -- not first, where the pinned
  // block it left happened to stand.
  const PIER = {
    id: "p3",
    name: "Old pier",
    chats: 0,
    files: 0,
    pinned: true,
    lastActivity: hoursAgo(30),
  };
  const fetch = serverForRows([PIER, ...ROWS]);
  const { container } = render(<App />);
  await onAllProjects();
  expect(sections(container)).toEqual({ Pinned: ["Old pier"], Recent: ["Thesis", "Notes"] });
  actionsFor("Old pier");
  fireEvent.click(screen.getByRole("button", { name: "Unpin" }));
  await waitFor(() =>
    expect(sections(container)).toEqual({ Recent: ["Thesis", "Notes", "Old pier"] }),
  );
  expect(patches(fetch).map(([path, options]) => [path, JSON.parse(options.body)])).toEqual([
    ["/api/projects/p3", { pinned: false }],
  ]);
});

// --- the archive (Madde 363; the design's items 135, 161, 190, 191) -----------------------------
// serverForRows keeps the mark as it keeps any other: the archive moves no row in the server's
// order and leaves the pin alone (Madde 339).

const tab = (name) => screen.getByRole("button", { name: new RegExp(`^${name}\\b`) });
const rowsOf = (section) =>
  [...section.querySelectorAll(".all-projects__row")].map((row) => row.textContent);
const PIER = { id: "p3", name: "Old pier", chats: 0, files: 0, pinned: true, lastActivity: hoursAgo(30) };

test("Archive asks nothing and leaves Undo where the project stood", async () => {
  const fetch = serverForRows(ROWS);
  const { container } = render(<App />);
  await onAllProjects();
  actionsFor("Notes");
  fireEvent.click(screen.getByRole("button", { name: "Archive" }));
  expect(container.querySelector(".dialog")).toBeNull();
  await screen.findByRole("button", { name: "Archived 1" });
  expect(screen.getByRole("button", { name: "Projects 1" })).toBeTruthy();
  const recent = container.querySelector(".all-projects__section");
  expect(rowsOf(recent)).toEqual([expect.stringContaining("Thesis"), "Notes archived · Undo"]);
  expect(patches(fetch).map(([path, options]) => [path, JSON.parse(options.body)])).toEqual([
    ["/api/projects/p2", { archived: true }],
  ]);
});

test("Undo puts the project back where it was", async () => {
  const fetch = serverForRows(ROWS);
  const { container } = render(<App />);
  await onAllProjects();
  actionsFor("Notes");
  fireEvent.click(screen.getByRole("button", { name: "Archive" }));
  await screen.findByRole("button", { name: "Archived 1" });
  fireEvent.click(screen.getByRole("button", { name: "Undo" }));
  await screen.findByRole("button", { name: "Archived 0" });
  await waitFor(() => expect(screen.queryByRole("button", { name: "Undo" })).toBeNull());
  expect(sections(container)).toEqual({ Recent: ["Thesis", "Notes"] });
  expect(screen.getByRole("button", { name: "Projects 2" })).toBeTruthy();
  expect(patches(fetch).map(([path, options]) => [path, JSON.parse(options.body)])).toEqual([
    ["/api/projects/p2", { archived: true }],
    ["/api/projects/p2", { archived: false }],
  ]);
});

test("a pinned project archived and brought back is pinned still", async () => {
  serverForRows([PIER, ...ROWS]);
  const { container } = render(<App />);
  await onAllProjects();
  actionsFor("Old pier");
  fireEvent.click(screen.getByRole("button", { name: "Archive" }));
  await screen.findByRole("button", { name: "Archived 1" });
  const pinned = container.querySelector(".all-projects__section");
  expect(rowsOf(pinned)).toEqual(["Old pier archived · Undo"]);
  fireEvent.click(screen.getByRole("button", { name: "Undo" }));
  await waitFor(() =>
    expect(sections(container)).toEqual({ Pinned: ["Old pier"], Recent: ["Thesis", "Notes"] }),
  );
});

test("an archived project stands only under Archived, and Unarchive brings it back", async () => {
  const fetch = serverForRows([ROWS[0], { ...ROWS[1], archived: true }]);
  const { container } = render(<App />);
  await onAllProjects();
  expect(sections(container)).toEqual({ Recent: ["Thesis"] });
  fireEvent.click(tab("Archived"));
  expect(screen.getByText("Notes", { selector: ".all-projects__row-name" })).toBeTruthy();
  actionsFor("Notes");
  fireEvent.click(screen.getByRole("button", { name: "Unarchive" }));
  expect(await screen.findByText("No archived projects.")).toBeTruthy();
  expect(patches(fetch).map(([path, options]) => [path, JSON.parse(options.body)])).toEqual([
    ["/api/projects/p2", { archived: false }],
  ]);
  fireEvent.click(tab("Projects"));
  expect(sections(container)).toEqual({ Recent: ["Thesis", "Notes"] });
});

test("an archived project's Delete asks the same question", async () => {
  const fetch = serverForRows([ROWS[0], { ...ROWS[1], archived: true }]);
  render(<App />);
  await onAllProjects();
  fireEvent.click(tab("Archived"));
  actionsFor("Notes");
  fireEvent.click(screen.getByRole("button", { name: "Delete" }));
  expect(screen.getByText('Delete "Notes"?')).toBeTruthy();
  expect(screen.getByText(/The 1 chat and 0 files/)).toBeTruthy();
  fireEvent.click(screen.getByRole("button", { name: "Delete" }));
  expect(await screen.findByText("No archived projects.")).toBeTruthy();
  const deletes = fetch.mock.calls.filter(([, options]) => options?.method === "DELETE");
  expect(deletes.map(([path]) => path)).toEqual(["/api/projects/p2"]);
});

test("with every project archived, the naming screen still counts them", async () => {
  // Madde 361 asks for the first project only when there is none at all: archived ones are still
  // projects, and All projects is still there to go back to.
  serverForRows(ROWS.map((project) => ({ ...project, archived: true })));
  render(<App />);
  expect(await screen.findByText("Every project is archived.")).toBeTruthy();
  fireEvent.click(screen.getByRole("button", { name: "+ New project" }));
  expect(await screen.findByLabelText("Name your project")).toBe(await nameField());
  expect(barExit().textContent).toBe("Cancel");
});

// --- Madde 364: the list that did not come, and a write the server refused ------------------------

const FAILED = { ok: false, status: 500, text: async () => "" };

// The first read of the list fails; the next one waits until the test answers it.
function listFailingOnce(projects) {
  let reads = 0;
  let answer;
  vi.stubGlobal(
    "fetch",
    vi.fn().mockImplementation((path) => {
      if (path !== "/api/projects") return ok([]);
      reads += 1;
      if (reads === 1) return Promise.resolve(FAILED);
      return new Promise((resolve) => {
        answer = () => resolve({ ok: true, status: 200, json: async () => projects });
      });
    }),
  );
  return () => answer();
}

test("Try again reads the list again, with the spinner while it waits", async () => {
  const answer = listFailingOnce([THESIS]);
  render(<App />);
  fireEvent.click(await screen.findByRole("button", { name: "Try again" }));
  // The design's 173: Try again shows the wait too, the frame standing around it.
  expect(await screen.findByText("All projects", { selector: ".screen__title" })).toBeTruthy();
  expect(document.querySelector(".all-projects__spinner [data-testid=spinner]")).toBeTruthy();
  await act(async () => {
    answer();
  });
  expect(await screen.findByText("Thesis", { selector: ".all-projects__row-name" })).toBeTruthy();
  expect(screen.queryByText("Couldn't load projects.")).toBeNull();
});

test("on the naming screen a list that did not come offers Try again, and no way back", async () => {
  // With the list unknown there is no project known to go back to, as in the design's failed.
  const answer = listFailingOnce([THESIS]);
  window.history.pushState(null, "", "/new");
  render(<App />);
  expect(await screen.findByText("Couldn't load projects.")).toBeTruthy();
  expect(barExit()).toBeNull();
  fireEvent.click(screen.getByRole("button", { name: "Try again" }));
  await act(async () => {
    answer();
  });
  expect(await screen.findByLabelText("Name your project")).toBe(await nameField());
});

// serverForRows, with its first rename, pin or delete refused in the server's own words.
function refusingFirstWrite(projects) {
  const fetch = serverForRows(projects);
  const keep = fetch.getMockImplementation();
  let refused = false;
  fetch.mockImplementation((path, options) => {
    if (!refused && ["PATCH", "DELETE"].includes(options?.method)) {
      refused = true;
      return Promise.resolve({
        ok: false,
        status: 500,
        text: async () => JSON.stringify({ error: "the store is unreachable" }),
      });
    }
    return keep(path, options);
  });
  return fetch;
}

const renameTo = (from, to) => {
  actionsFor(from);
  fireEvent.click(screen.getByRole("button", { name: "Rename" }));
  const field = screen.getByRole("textbox", { name: "Project name" });
  fireEvent.change(field, { target: { value: to } });
  fireEvent.keyDown(field, { key: "Enter" });
};

test("a rename the server refuses leaves All projects standing, with the server's words", async () => {
  // The list was read and is still known: a write that did not land is not a list that did not come.
  refusingFirstWrite(ROWS);
  const { container } = render(<App />);
  await onAllProjects();
  renameTo("Thesis", "Dissertation");
  expect((await screen.findByText("the store is unreachable")).className).toBe("list-error");
  expect(sections(container)).toEqual({ Recent: ["Thesis", "Notes"] });
  expect(screen.queryByText("Couldn't load projects.")).toBeNull();
});

test("a delete the server refuses leaves the project where it was", async () => {
  refusingFirstWrite(ROWS);
  const { container } = render(<App />);
  await onAllProjects();
  actionsFor("Notes");
  fireEvent.click(screen.getByRole("button", { name: "Delete" }));
  fireEvent.click(screen.getByRole("button", { name: "Delete" }));
  expect((await screen.findByText("the store is unreachable")).className).toBe("list-error");
  expect(sections(container)).toEqual({ Recent: ["Thesis", "Notes"] });
});

test("the next write that lands takes the refusal's line away", async () => {
  refusingFirstWrite(ROWS);
  const { container } = render(<App />);
  await onAllProjects();
  renameTo("Thesis", "Dissertation");
  await screen.findByText("the store is unreachable");
  actionsFor("Notes");
  fireEvent.click(screen.getByRole("button", { name: "Pin" }));
  await waitFor(() =>
    expect(sections(container)).toEqual({ Pinned: ["Notes"], Recent: ["Thesis"] }),
  );
  expect(screen.queryByText("the store is unreachable")).toBeNull();
});

test("inside a project no ⋯ stands anywhere", async () => {
  // The design's 161: everything done to a project is done from outside it.
  serverForRows(ROWS);
  window.history.pushState(null, "", "/p/p1/c/new");
  const { container } = render(<App />);
  await screen.findByText("Thesis", { selector: ".bar__project" });
  expect(screen.queryByRole("button", { name: /^(More|Actions) for/ })).toBeNull();
  expect(container.querySelector(".sidebar__row-more")).toBeNull();
});

test("a list that fails to load says so instead of claiming there are none", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({ ok: false, status: 500, text: async () => "" }),
  );
  render(<App />);
  expect(await screen.findByText("Couldn't load projects.")).toBeTruthy();
  // The raw words are Copy's, not the screen's (the design's 172).
  expect(screen.queryByText(/HTTP 500/)).toBeNull();
  expect(screen.queryByText(/No projects yet/)).toBeNull();
  // And no way to send a message either -- there is no project for one to land in.
  expect(screen.queryByPlaceholderText(/Ask anything/)).toBeNull();
});

test("a project address that matches nothing says so", async () => {
  stubProjects([]);
  window.history.pushState(null, "", "/p/pabc");
  render(<App />);
  await waitFor(() => expect(screen.getByText("That project does not exist.")).toBeTruthy());
});

test("nothing is asked of a workspace-wide chat address", async () => {
  // A chat is always started from inside a project, and the sidebar lists that project's own chats
  // -- so nothing reaches /api/chats at all, by any method.
  const fetch = stubProjects([]);
  render(<App />);
  await waitFor(() => expect(screen.getByText("No projects yet.")).toBeTruthy());
  expect(fetch.mock.calls.every(([path]) => path !== "/api/chats")).toBe(true);
});

test("New chat opens an empty chat in the project it was pressed in", async () => {
  const fetch = serverWithProjects([PROJECT], {
    p1: [{ id: "c1", title: "Write the intro", lastActivity: NOW }],
  });
  window.history.pushState(null, "", "/p/p1/c/c1");

  render(<App />);
  await waitFor(() => expect(screen.getByRole("button", { name: /New chat/ })).toBeTruthy());
  fireEvent.click(screen.getByRole("button", { name: /New chat/ }));

  await waitFor(() => expect(window.location.pathname).toBe("/p/p1/c/new"));
  expect(screen.getByText("New chat", { selector: ".chat__title" })).toBeTruthy();
  // There is no chat to read yet, so nothing is asked for one.
  expect(fetch.mock.calls.every(([path]) => !String(path).endsWith("/chats/new"))).toBe(true);
});

// Madde 362 (design 151, 152, 168): inside a project the sidebar is that project's own. Its name
// stands once, in the bar, and the other projects are reached from All projects.
test("inside a project the sidebar holds its chats and no other project", async () => {
  const NOTES = { id: "p2", name: "Notes", chats: 0, files: 0, pinned: false, lastActivity: NOW };
  serverWithProjects([THESIS, NOTES], {
    p1: [
      { id: "c1", title: "Write the intro", lastActivity: NOW },
      { id: "c2", title: "Missing values", lastActivity: NOW },
    ],
  });
  window.history.pushState(null, "", "/p/p1/c/c1");
  render(<App />);
  await screen.findByText("Missing values", { selector: ".sidebar__chat" });
  expect(screen.getByText("Write the intro", { selector: ".sidebar__chat" })).toBeTruthy();
  expect(screen.queryByText("Notes")).toBeNull();
  expect(screen.queryByText("Projects")).toBeNull();
  expect(screen.queryByRole("button", { name: "New project" })).toBeNull();
});

test("a project with no chats yet says so in the sidebar", async () => {
  serverWithProjects([THESIS]);
  window.history.pushState(null, "", "/p/p1/c/new");
  render(<App />);
  expect(await screen.findByText("No chats yet.", { selector: ".sidebar__empty" })).toBeTruthy();
});

test("the first message in a draft creates the chat and takes its address", async () => {
  const chat = { id: "c1", title: "Write the intro", messages: [], lastActivity: "x" };
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (path === "/api/projects/p1/messages" && options?.method === "POST") {
      // Madde 88: the answer comes back down this same request, and its first frame is what says
      // which chat was born.
      return Promise.resolve(
        sseResponse(
          `event: chat\ndata: {"chat":"c1"}\n\nevent: done\ndata: ${JSON.stringify(chat)}\n\n`,
        ),
      );
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
  await chatOpened();
  fireEvent.change(screen.getByPlaceholderText("Reply..."), {
    target: { value: "Write the intro" },
  });
  fireEvent.keyDown(screen.getByPlaceholderText("Reply..."), { key: "Enter" });

  await waitFor(() => expect(window.location.pathname).toBe("/p/p1/c/c1"));
  // The draft address is not a place to go back to: it no longer exists.
  expect(push).not.toHaveBeenCalled();
});

// Madde 355, design item 194: a chat opening looks opened -- the sidebar row's name over it, the
// rail beside it, the box shut -- and only where its messages will be does anything wait.
test("a chat whose record has not come yet stands in its own frame", async () => {
  const row = { id: "c1", title: "Write the intro", lastActivity: new Date().toISOString() };
  const file = { name: "plan.md", ext: "md", modifiedAt: new Date().toISOString() };
  vi.stubGlobal(
    "fetch",
    vi.fn().mockImplementation((path) => {
      if (path.endsWith("/chats/c1")) return new Promise(() => {});
      if (path.endsWith("/chats")) {
        return Promise.resolve({ ok: true, status: 200, json: async () => [row] });
      }
      if (path.endsWith("/files")) {
        return Promise.resolve({ ok: true, status: 200, json: async () => [file] });
      }
      return Promise.resolve({ ok: true, status: 200, json: async () => [PROJECT] });
    }),
  );
  window.history.pushState(null, "", "/p/p1/c/c1");

  render(<App />);
  expect(await screen.findByText("Write the intro", { selector: ".chat__title" })).toBeTruthy();
  await waitFor(() => expect(screen.getByTestId("file-rail").textContent).toContain("plan.md"));
  expect(document.querySelector(".chat__spinner [data-testid=spinner]")).toBeTruthy();
  expect(screen.getByPlaceholderText("Reply...").disabled).toBe(true);
  expect(screen.queryByRole("button", { name: "← back" })).toBeNull();
});

test("a newborn chat is named by the trimmed first message, not the whole of it", async () => {
  // Madde 116: the record stood up for the draft carried the whole message as its title. The
  // server's trimmed name only arrives when the turn ends -- minutes later in a flow run -- so
  // the window this test stands in is the turn still running after the first frame moved the
  // address.
  const first = "m".repeat(80);
  const { response } = gatedSse('event: chat\ndata: {"chat":"c1"}\n\n', "event: done\ndata: {}\n\n");
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (path === "/api/projects/p1/messages" && options?.method === "POST") {
      return Promise.resolve(response);
    }
    if (path === "/api/projects/p1/chats") {
      return Promise.resolve({ ok: true, status: 200, json: async () => [] });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [PROJECT] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/new");

  render(<App />);
  await chatOpened();
  fireEvent.change(screen.getByPlaceholderText("Reply..."), { target: { value: first } });
  fireEvent.keyDown(screen.getByPlaceholderText("Reply..."), { key: "Enter" });

  await waitFor(() => expect(window.location.pathname).toBe("/p/p1/c/c1"));
  expect(document.querySelector(".chat__title").textContent).toBe("m".repeat(42) + "…");
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
  await chatOpened();
  fireEvent.change(screen.getByPlaceholderText("Reply..."), { target: { value: "hello" } });
  fireEvent.keyDown(screen.getByPlaceholderText("Reply..."), { key: "Enter" });

  // The design says the bubble appears immediately -- before the request has come back.
  await waitFor(() => expect(screen.getByText("hello")).toBeTruthy());

  refuse();
  await waitFor(() => expect(screen.queryByText("hello")).toBeNull());
  // The server's own sentence, not the method and the code the browser used to write instead --
  // under the same card a failed answer draws (design item 193).
  expect(screen.getByText("a message needs text")).toBeTruthy();
  expect(screen.getByText("Couldn't get a response.")).toBeTruthy();
  expect(document.querySelector(".refused")).toBeNull();
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

// Madde 349: the card says no answer came, and what it came for is the refused sentence -- a
// request with no text would ask the server to answer a question that was never written.
function stubRefusingChat(answers) {
  const records = {
    c1: { id: "c1", title: "Hi", messages: [] },
    c2: { id: "c2", title: "Other", messages: [] },
  };
  const rows = Object.values(records).map(({ id, title }) => ({
    id,
    title,
    lastActivity: new Date().toISOString(),
  }));
  let posts = 0;
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (path.endsWith("/messages") && options?.method === "POST") {
      posts += 1;
      return Promise.resolve(answers(posts));
    }
    const record = records[path.match(/\/chats\/(\w+)$/)?.[1]];
    if (record) return Promise.resolve({ ok: true, status: 200, json: async () => record });
    if (path.endsWith("/chats")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => rows });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/c1");
  return fetch;
}

const NOT_FOUND = {
  ok: false,
  status: 404,
  text: async () => JSON.stringify({ error: "chat not found" }),
};

const messagePosts = (fetch) =>
  fetch.mock.calls
    .filter(([path, options]) => path.endsWith("/messages") && options?.method === "POST")
    .map(([, options]) => JSON.parse(options.body));

test("Try again after a refusal sends the refused message again", async () => {
  const fetch = stubRefusingChat(() => NOT_FOUND);
  render(<App />);
  const box = await chatOpened();
  fireEvent.change(box, { target: { value: "hello" } });
  fireEvent.keyDown(box, { key: "Enter" });
  await screen.findByText("chat not found");

  fireEvent.click(screen.getByRole("button", { name: "Try again" }));
  await waitFor(() => expect(messagePosts(fetch)).toHaveLength(2));
  const [first, again] = messagePosts(fetch);
  expect(again.text).toBe("hello");
  expect(again).toEqual(first);
  // Refused again, the card stands again with what the server said this time.
  expect(await screen.findByText("chat not found")).toBeTruthy();
});

test("a refusal is not carried into a later send's Try again", async () => {
  const fetch = stubRefusingChat((post) =>
    post === 1 ? NOT_FOUND : sseResponse('event: error\ndata: {"error":"401 bad key"}\n\n'),
  );
  render(<App />);
  const box = await chatOpened();
  fireEvent.change(box, { target: { value: "hello" } });
  fireEvent.keyDown(box, { key: "Enter" });
  await screen.findByText("chat not found");

  fireEvent.change(box, { target: { value: "again" } });
  fireEvent.keyDown(box, { key: "Enter" });
  await screen.findByText("401 bad key");

  // The question is on disk now, and it is what Try again asks about -- not the sentence refused
  // two sends ago.
  fireEvent.click(screen.getByRole("button", { name: "Try again" }));
  await waitFor(() => expect(messagePosts(fetch)).toHaveLength(3));
  expect(messagePosts(fetch)[2]).toEqual({ chat: "c1" });
});

// The box is the refused sentence's one owner, so Try again is the box sending it -- left behind
// there as well, it would be sent a second time.
test("a sentence sent again by Try again does not stay in the box", async () => {
  const fetch = stubRefusingChat((post) =>
    post === 1 ? NOT_FOUND : sseResponse('event: chat\ndata: {"chat":"c1"}\n\nevent: done\ndata: {}\n\n'),
  );
  render(<App />);
  const box = await chatOpened();
  fireEvent.change(box, { target: { value: "hello" } });
  fireEvent.keyDown(box, { key: "Enter" });
  await screen.findByText("chat not found");
  expect(box.value).toBe("hello");

  fireEvent.click(screen.getByRole("button", { name: "Try again" }));
  await waitFor(() => expect(messagePosts(fetch)).toHaveLength(2));
  expect(messagePosts(fetch)[1].text).toBe("hello");
  await waitFor(() => expect(screen.queryByText("Couldn't get a response.")).toBeNull());
  expect(box.value).toBe("");
});

async function refuseInFirstChat() {
  stubRefusingChat(() => NOT_FOUND);
  render(<App />);
  const box = await chatOpened();
  fireEvent.change(box, { target: { value: "hello" } });
  fireEvent.keyDown(box, { key: "Enter" });
  await screen.findByText("chat not found");
}

// Design APP-BUGS 3: the card's Try again sends the box, so pressed in another chat it would write
// the refused sentence there.
test("a refusal's card stays in the chat it was said in", async () => {
  await refuseInFirstChat();
  fireEvent.click(await screen.findByText("Other", { selector: ".sidebar__chat" }));
  await waitFor(() => expect(window.location.pathname).toBe("/p/p1/c/c2"));
  expect(screen.queryByText("Couldn't get a response.")).toBeNull();
});

test("a refusal's card does not follow the user into the draft", async () => {
  await refuseInFirstChat();
  fireEvent.click(document.querySelector(".sidebar__new-chat"));
  await waitFor(() => expect(window.location.pathname).toBe("/p/p1/c/new"));
  expect(screen.queryByText("Couldn't get a response.")).toBeNull();
});

// A stream that hands over its first frames, then waits to be released before the rest. The one-shot
// helper cannot serve a test that has to press something *while* the answer is running.
function gatedSse(first, rest) {
  const encoder = new TextEncoder();
  let release;
  const gate = new Promise((resolve) => {
    release = resolve;
  });
  let stage = 0;
  const response = {
    ok: true,
    status: 200,
    body: {
      getReader: () => ({
        read: async () => {
          if (stage === 0) {
            stage = 1;
            return { done: false, value: encoder.encode(first) };
          }
          if (stage === 1) {
            stage = 2;
            await gate;
            return { done: false, value: encoder.encode(rest) };
          }
          return { done: true };
        },
      }),
    },
  };
  return { response, release: () => release() };
}

test("nothing asks for an answer by itself when a chat is opened", async () => {
  // Madde 88 replaced two tests with this one. Both of them proved that a particular kind of chat
  // was spared the browser's own asking -- one stopped mid-word, one stopped before it. There is
  // no asking to be spared from now: opening a chat sends nothing, whatever its last word was.
  const owed = {
    id: "c1",
    title: "hello",
    messages: [{ role: "user", at: new Date().toISOString(), text: "hello" }],
  };
  const fetch = vi.fn().mockImplementation((path) => {
    if (String(path).endsWith("/chats/c1")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => owed });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/c1");

  render(<App />);
  // The title says "hello" too, so the bubble is asked for by name.
  await waitFor(() => expect(screen.getByText("hello", { selector: ".msg__bubble" })).toBeTruthy());
  expect(fetch.mock.calls.filter(([, options]) => options?.method === "POST")).toHaveLength(0);
});

test("a call arrives in the stream and is still there once the record lands", async () => {
  // Madde 66's handover. The stream draws the line before any record exists, and the record that
  // follows carries the same call -- so what the browser piled up has to be dropped rather than
  // added to, or the same step reads as two.
  const owed = {
    id: "c1",
    title: "hello",
    messages: [{ role: "user", at: new Date().toISOString(), text: "hello" }],
  };
  let read = 0;
  const answered = {
    ...owed,
    messages: [
      ...owed.messages,
      {
        role: "ai",
        at: new Date().toISOString(),
        text: "Done.",
        calls: [{ tool: "read_file", target: "plan.md" }],
      },
    ],
  };
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (path.endsWith("/messages") && options?.method === "POST") {
      return Promise.resolve(
        sseResponse(
          `event: chat\ndata: {"chat":"c1"}\n\n` +
            `event: call\ndata: {"tool":"read_file","target":"plan.md"}\n\n` +
            `event: chunk\ndata: {"text":"Do"}\n\nevent: done\ndata: {}\n\n`,
        ),
      );
    }
    if (path.endsWith("/chats/c1")) {
      // Madde 89: the record is read back when the turn closes, so the second read is the one
      // carrying what was written.
      read += 1;
      return Promise.resolve({
        ok: true,
        status: 200,
        json: async () => (read > 1 ? answered : owed),
      });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/c1");

  render(<App />);
  // Madde 88: the answer comes of sending, not of arriving.
  const box = await chatOpened();
  fireEvent.change(box, { target: { value: "hello" } });
  fireEvent.keyDown(box, { key: "Enter" });
  await waitFor(() => expect(screen.getByText("Done.")).toBeTruthy());
  // Since Madde 84 the record's calls sit behind a door, so the claim is asked of what is behind
  // it. Unchanged otherwise, and it is the whole point of the test: one step, kept once, though two
  // places reported it -- the live stream and the record that followed.
  fireEvent.click(screen.getByRole("button", { name: /1 step/ }));
  expect(screen.getAllByText("⏺ read_file(plan.md)")).toHaveLength(1);
});

test("sending a sentence streams the answer and keeps the server's record", async () => {
  // Madde 88: one request. The sentence goes out and the answer comes back down the same
  // connection, so the count below is the whole claim -- nothing opened a second one.
  const empty = { id: "c1", title: "hello", messages: [] };
  const answered = {
    ...empty,
    messages: [
      { role: "user", at: new Date().toISOString(), text: "hello" },
      { role: "ai", at: new Date().toISOString(), text: "Done." },
    ],
  };
  let read = 0;
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (path.endsWith("/messages") && options?.method === "POST") {
      return Promise.resolve(
        sseResponse(
          `event: chat\ndata: {"chat":"c1"}\n\n` +
            `event: chunk\ndata: {"text":"Do"}\n\nevent: done\ndata: {}\n\n`,
        ),
      );
    }
    if (path.endsWith("/chats/c1")) {
      read += 1;
      return Promise.resolve({
        ok: true,
        status: 200,
        json: async () => (read > 1 ? answered : empty),
      });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/c1");

  render(<App />);
  const box = await chatOpened();
  fireEvent.change(box, { target: { value: "hello" } });
  fireEvent.keyDown(box, { key: "Enter" });

  await waitFor(() => expect(screen.getByText("Done.")).toBeTruthy());
  expect(fetch.mock.calls.filter(([, options]) => options?.method === "POST")).toHaveLength(1);
});

test("a call frame takes the dashed card down", async () => {
  // The dashed card lives between "the model asked" and "the tool answered", and a call frame is
  // the second. Until Madde 69 only a born file took it down, so a tool that wrote nothing left it
  // spinning until the turn ended -- rare then, and the ordinary case now that create_file refuses
  // a name that is taken.
  const owed = { id: "c1", title: "hello", messages: [] };
  const { response, release } = gatedSse(
    'event: chat\ndata: {"chat":"c1"}\n\n' +
      "event: file-start\ndata: {}\n\n" +
      'event: call\ndata: {"tool":"create_file","target":"plan.md","outcome":"Already there"}\n\n',
    `event: done\ndata: ${JSON.stringify(owed)}\n\n`,
  );
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (path.endsWith("/messages") && options?.method === "POST") return Promise.resolve(response);
    if (path.endsWith("/chats/c1"))
      return Promise.resolve({ ok: true, status: 200, json: async () => owed });
    return Promise.resolve({ ok: true, status: 200, json: async () => [] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/c1");

  render(<App />);
  const box = await chatOpened();
  fireEvent.change(box, { target: { value: "fix the plan" } });
  fireEvent.keyDown(box, { key: "Enter" });

  // The handle is what says the tool answered -- while a turn runs it carries the newest call, and
  // the outcome itself is behind the door. Waiting for it is what makes the dashed card's absence
  // mean something: without it this would also pass on a card that never went up.
  await waitFor(() => expect(screen.getByText("⏺ create_file(plan.md)")).toBeTruthy());
  expect(screen.queryByText("creating file…")).toBeNull();
  release();
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
    if (path.endsWith("/messages") && options?.method === "POST") {
      onDisk = [{ name: "outline.md", ext: "md", modifiedAt: new Date().toISOString() }];
      return Promise.resolve(
        sseResponse(
          'event: chat\ndata: {"chat":"c1"}\n\n' +
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
  const box = await chatOpened();
  fireEvent.change(box, { target: { value: "write the outline" } });
  fireEvent.keyDown(box, { key: "Enter" });
  await waitFor(() => expect(screen.getByTestId("file-rail").textContent).toContain("outline.md"));
});

// Madde 192. Until now a `file` frame was the only thing that brought the two lists up to date, so
// anything that wrote without announcing one -- or a file the user dropped into the Drive folder
// mid-turn -- stayed invisible until the screen was left and come back to.
test("a turn ending brings the file list up to date, whatever wrote the file", async () => {
  const owed = { id: "c1", title: "hello", messages: [] };
  let onDisk = [];
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (path.endsWith("/messages") && options?.method === "POST") {
      onDisk = [{ name: "plan.md", ext: "md", modifiedAt: new Date().toISOString() }];
      // No file frame at all: this stream announces nothing it wrote.
      return Promise.resolve(
        sseResponse('event: chat\ndata: {"chat":"c1"}\n\nevent: done\ndata: {}\n\n'),
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
  const box = await chatOpened();
  // Asked before the turn: without this the assertion below would pass on a rail that was never
  // stale in the first place.
  await waitFor(() =>
    expect(screen.getByTestId("file-rail").textContent).toContain("No files yet"),
  );

  fireEvent.change(box, { target: { value: "write the plan" } });
  fireEvent.keyDown(box, { key: "Enter" });
  await waitFor(() => expect(screen.getByTestId("file-rail").textContent).toContain("plan.md"));
});

test("a turn ending reads the file that is open again", async () => {
  // The heavier of the two: a stale list hides a name, a stale panel shows the wrong text under
  // the right one.
  const owed = { id: "c1", title: "hello", messages: [] };
  const file = { name: "plan.md", ext: "md", modifiedAt: new Date().toISOString() };
  let text = "the first draft";
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (path.endsWith("/messages") && options?.method === "POST") {
      text = "the second draft";
      return Promise.resolve(
        sseResponse('event: chat\ndata: {"chat":"c1"}\n\nevent: done\ndata: {}\n\n'),
      );
    }
    if (path.endsWith("/files/plan.md")) {
      return Promise.resolve({
        ok: true,
        status: 200,
        json: async () => ({ ...file, size: text.length, text }),
      });
    }
    if (path.endsWith("/files")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => [file] });
    }
    if (path.endsWith("/chats/c1")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => owed });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/c1");

  render(<App />);
  fireEvent.click(await screen.findByText("plan.md"));
  await waitFor(() => expect(screen.getByText("the first draft")).toBeTruthy());

  const box = await chatOpened();
  fireEvent.change(box, { target: { value: "rewrite it" } });
  fireEvent.keyDown(box, { key: "Enter" });
  await waitFor(() => expect(screen.getByText("the second draft")).toBeTruthy());
});

test("Refresh asks again with no turn to hang it on", async () => {
  // What a turn's end cannot cover: a file put into the Drive folder by hand, and a look taken in
  // the middle of a turn that is still running.
  let onDisk = [];
  const fetch = vi.fn().mockImplementation((path) => {
    if (String(path).endsWith("/files")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => onDisk });
    }
    return ok(path === "/api/projects" ? [PROJECT] : []);
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/new");

  render(<App />);
  await waitFor(() => expect(screen.getByText(/No files yet/)).toBeTruthy());

  onDisk = [{ name: "plan.md", ext: "md", modifiedAt: new Date().toISOString() }];
  fireEvent.click(screen.getByRole("button", { name: "Refresh" }));
  await waitFor(() => expect(screen.getByText("plan.md")).toBeTruthy());
});

// Madde 194: everything between the question and the answer used to be three blinking dots, however
// long the turn took.
function _turnThatReports() {
  const owed = { id: "c1", title: "hello", messages: [] };
  let record = owed;
  const { response, release } = gatedSse(
    'event: chat\ndata: {"chat":"c1"}\n\n' +
      'event: progress\ndata: {"round":1,"of":16,"tokens":0}\n\n' +
      'event: progress\ndata: {"round":2,"of":16,"tokens":12300}\n\n',
    "event: done\ndata: {}\n\n",
  );
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (path.endsWith("/messages") && options?.method === "POST") {
      record = {
        ...owed,
        messages: [
          {
            role: "ai",
            at: new Date().toISOString(),
            text: "Done.",
            usage: { sent: 9000, cached: 3000, answered: 100 },
          },
        ],
      };
      return Promise.resolve(response);
    }
    if (path.endsWith("/chats/c1")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => record });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/c1");
  return release;
}

test("a running turn counts its rounds and its tokens on screen", async () => {
  _turnThatReports();
  render(<App />);
  const box = await chatOpened();
  fireEvent.change(box, { target: { value: "go" } });
  fireEvent.keyDown(box, { key: "Enter" });

  const strip = await screen.findByTestId("live-strip");
  await waitFor(() => expect(strip.textContent).toContain("round 2/16"));
  expect(strip.textContent).toContain("12.3k tokens");
});

test("when the turn ends the strip is gone and the stamp is in its place", async () => {
  const release = _turnThatReports();
  render(<App />);
  const box = await chatOpened();
  fireEvent.change(box, { target: { value: "go" } });
  fireEvent.keyDown(box, { key: "Enter" });
  await screen.findByTestId("live-strip");

  release();
  await waitFor(() => expect(screen.queryByTestId("live-strip")).toBeNull());
  // What it cost rather than how big it got, and that difference is on purpose: the strip answers
  // how big the turn got, the stamp what came from the cache and what missed it (Madde 354). 9000
  // sent, 3000 of it cached; the 100 the model wrote is not shown.
  expect(screen.getByText("3.0k cached")).toBeTruthy();
  expect(screen.getByText("6.0k missed")).toBeTruthy();
});

test("a fault inside the stream shows the card and Try again asks through the one door", async () => {
  // Madde 88 kept the button and took away the finger that pressed it. It goes to the same
  // address as a sentence does, and carries no sentence: the question is already on disk.
  const empty = { id: "c1", title: "hello", messages: [] };
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (path.endsWith("/messages") && options?.method === "POST") {
      return Promise.resolve(
        sseResponse(
          'event: chat\ndata: {"chat":"c1"}\n\nevent: error\ndata: {"error":"401 bad key"}\n\n',
        ),
      );
    }
    if (path.endsWith("/chats/c1")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => empty });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/c1");

  render(<App />);
  const box = await chatOpened();
  fireEvent.change(box, { target: { value: "hello" } });
  fireEvent.keyDown(box, { key: "Enter" });
  await waitFor(() => expect(screen.getByText("401 bad key")).toBeTruthy());

  fireEvent.click(screen.getByRole("button", { name: "Try again" }));
  await waitFor(() => {
    const posts = fetch.mock.calls.filter(([, options]) => options?.method === "POST");
    expect(posts).toHaveLength(2);
    // No sentence in it: the one on disk must not be written twice.
    expect(JSON.parse(posts[1][1].body)).toEqual({ chat: "c1" });
  });
});

test("a broken engine is reported and nothing asks again by itself", async () => {
  const empty = { id: "c1", title: "hello", messages: [] };
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (path.endsWith("/messages") && options?.method === "POST") {
      return Promise.resolve({ ok: false, status: 502, text: async () => "" });
    }
    if (path.endsWith("/chats/c1")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => empty });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/c1");

  render(<App />);
  const box = await chatOpened();
  fireEvent.change(box, { target: { value: "hello" } });
  fireEvent.keyDown(box, { key: "Enter" });

  await waitFor(() => expect(screen.getByText(/HTTP 502/)).toBeTruthy());
  // Asking again is the user's to do. A broken engine used to become an endless retry here.
  expect(fetch.mock.calls.filter(([, options]) => options?.method === "POST")).toHaveLength(1);
});

// The app speaks one deletion language: ask, then delete. The browser's box is gone from it. A
// chat is not among what it deletes since Madde 353: its one place was the project screen.
function withFile() {
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
    return ok(path === "/api/projects" ? [PROJECT] : []);
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/new");
  return fetch;
}

test("answering the question takes the file, and nothing is offered back", async () => {
  withFile();
  render(<App />);
  await waitFor(() => expect(screen.getByText("plan.md")).toBeTruthy());

  fireEvent.click(screen.getByRole("button", { name: "Delete plan.md" }));
  expect(screen.getByText('Delete "plan.md"?')).toBeTruthy();
  fireEvent.click(screen.getByRole("button", { name: "Delete file" }));
  await waitFor(() => expect(screen.queryByText("plan.md")).toBeNull());
  // The question was the protection, and the disk keeps the file.
  expect(screen.queryByText("Undo")).toBeNull();
  expect(screen.queryByText("File deleted.")).toBeNull();
});

test("a file open in the panel cannot be asked to go, and closing it brings the row back", async () => {
  // The delete lives on the row, and the row lives in the rail the reader took over. So reading a
  // file is not a state a file can be deleted from.
  withFile();
  render(<App />);
  await waitFor(() => expect(screen.getByText("plan.md")).toBeTruthy());
  fireEvent.click(screen.getByText("plan.md"));
  await waitFor(() => expect(screen.getByText("body")).toBeTruthy());

  expect(screen.queryByRole("button", { name: "Delete plan.md" })).toBeNull();
  fireEvent.click(screen.getByRole("button", { name: "←" }));
  await waitFor(() => expect(screen.getByRole("button", { name: "Delete plan.md" })).toBeTruthy());
});

test("a file is opened, the icon is pressed, and the text is on the clipboard", async () => {
  // Madde 193's own how-it-is-seen, on a real screen. jsdom ships no clipboard, so the test hands
  // one over and watches what goes into it.
  const writeText = vi.fn(() => Promise.resolve());
  Object.defineProperty(navigator, "clipboard", { value: { writeText }, configurable: true });
  withFile();
  render(<App />);
  await waitFor(() => expect(screen.getByText("plan.md")).toBeTruthy());
  fireEvent.click(screen.getByText("plan.md"));
  await waitFor(() => expect(screen.getByText("body")).toBeTruthy());

  fireEvent.click(screen.getByRole("button", { name: "Copy" }));
  expect(writeText).toHaveBeenCalledWith("body");
});

test("a file is not deleted until the question is answered", async () => {
  const file = { name: "plan.md", ext: "md", modifiedAt: new Date().toISOString() };
  const fetch = vi.fn().mockImplementation((path) => {
    if (path.endsWith("/files")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => [file] });
    }
    return ok(path === "/api/projects" ? [PROJECT] : []);
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/new");

  render(<App />);
  await waitFor(() => expect(screen.getByText("plan.md")).toBeTruthy());
  fireEvent.click(screen.getByRole("button", { name: "Delete plan.md" }));
  fireEvent.click(screen.getByRole("button", { name: "Cancel" }));
  expect(fetch.mock.calls.every(([, options]) => options?.method !== "DELETE")).toBe(true);
});

// --- folding the rail --------------------------------------------------------------------------

function withRail() {
  const file = { name: "plan.md", ext: "md", modifiedAt: new Date().toISOString() };
  const chats = [{ id: "c1", title: "Write the intro", lastActivity: new Date().toISOString() }];
  const chat = { id: "c1", title: "Write the intro", messages: [] };
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
    if (path.endsWith("/chats/c1")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => chat });
    }
    if (path.endsWith("/chats")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => chats });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [PROJECT] });
  });
  vi.stubGlobal("fetch", fetch);
  return fetch;
}

const fold = () => fireEvent.click(screen.getByRole("button", { name: /Project files/ }));
// The open sidebar is told by its chat row: folded, the icon column has no rows. The chat's header
// carries the same title, hence the selector.
const sidebarOpen = () => screen.queryByText("Write the intro", { selector: ".sidebar__chat" });

test("the rail stays folded when the chat changes under it", async () => {
  // The design asks for the state to last the session, so it cannot live in a component that is
  // rebuilt every time the address does.
  withRail();
  window.history.pushState(null, "", "/p/p1/c/c1");
  render(<App />);
  await waitFor(() => expect(screen.getByText("plan.md")).toBeTruthy());

  fold();
  await waitFor(() => expect(screen.queryByText("plan.md")).toBeNull());

  fireEvent.click(screen.getByRole("button", { name: /New chat/ }));
  await waitFor(() => expect(window.location.pathname).toBe("/p/p1/c/new"));
  expect(screen.queryByText("plan.md")).toBeNull();
});

test("the sidebar folds away and comes back, and stays folded across an address", async () => {
  // Madde 51: one button, and the state outlives the screen the way the rail's does.
  withRail();
  window.history.pushState(null, "", "/p/p1/c/c1");
  render(<App />);
  await waitFor(() => expect(sidebarOpen()).toBeTruthy());

  fireEvent.click(screen.getByRole("button", { name: "Hide the sidebar" }));
  await waitFor(() => expect(sidebarOpen()).toBeNull());

  // Folded, the column still carries New chat (Madde 351); All projects has no sidebar to fold, so
  // the draft is the other address.
  fireEvent.click(screen.getByRole("button", { name: "New chat" }));
  await waitFor(() => expect(window.location.pathname).toBe("/p/p1/c/new"));
  expect(sidebarOpen()).toBeNull();

  fireEvent.click(screen.getByRole("button", { name: "Show the sidebar" }));
  await waitFor(() => expect(sidebarOpen()).toBeTruthy());
});

// Madde 351: Ctrl + . folds the sidebar and brings it back, as on claude.ai (design 174, 187) --
// wherever the focus stands, the composer included.
test("Ctrl + . folds the sidebar and brings it back", async () => {
  withRail();
  window.history.pushState(null, "", "/p/p1/c/c1");
  render(<App />);
  await waitFor(() => expect(sidebarOpen()).toBeTruthy());

  fireEvent.keyDown(window, { key: ".", ctrlKey: true });
  await waitFor(() => expect(sidebarOpen()).toBeNull());
  expect(screen.getByRole("button", { name: "Show the sidebar" })).toBeTruthy();

  fireEvent.keyDown(window, { key: ".", ctrlKey: true });
  await waitFor(() => expect(sidebarOpen()).toBeTruthy());
});

test("Ctrl + . works while typing, and types nothing", async () => {
  withRail();
  window.history.pushState(null, "", "/p/p1/c/c1");
  render(<App />);
  const box = await chatOpened();
  await waitFor(() => expect(sidebarOpen()).toBeTruthy());
  fireEvent.change(box, { target: { value: "hello" } });

  // false: the default was prevented, so the browser has nothing of its own left to do with it.
  expect(fireEvent.keyDown(box, { key: ".", ctrlKey: true })).toBe(false);
  await waitFor(() => expect(sidebarOpen()).toBeNull());
  expect(box.value).toBe("hello");
});

test("a full stop typed alone is only a full stop", async () => {
  withRail();
  window.history.pushState(null, "", "/p/p1/c/c1");
  render(<App />);
  const box = await chatOpened();
  await waitFor(() => expect(sidebarOpen()).toBeTruthy());
  expect(fireEvent.keyDown(box, { key: "." })).toBe(true);
  expect(sidebarOpen()).toBeTruthy();
});

test("dragging the rail's edge widens it, and the width crosses chats", async () => {
  // Madde 50: the width lasts the session for the same reason the folded state does.
  withRail();
  window.history.pushState(null, "", "/p/p1/c/c1");
  render(<App />);
  await waitFor(() => expect(screen.getByText("plan.md")).toBeTruthy());

  fireEvent.mouseDown(screen.getByRole("separator"), { clientX: 600 });
  fireEvent.mouseMove(window, { clientX: 520 });
  fireEvent.mouseUp(window);
  await waitFor(() => expect(screen.getByTestId("file-rail").style.width).toBe("400px"));

  fireEvent.click(screen.getByRole("button", { name: /New chat/ }));
  await waitFor(() => expect(window.location.pathname).toBe("/p/p1/c/new"));
  expect(screen.getByTestId("file-rail").style.width).toBe("400px");
});

test("dragging it past its minimum folds it instead of leaving a sliver", async () => {
  withRail();
  window.history.pushState(null, "", "/p/p1/c/c1");
  render(<App />);
  await waitFor(() => expect(screen.getByText("plan.md")).toBeTruthy());

  // 320 - 200 is under the 220 the rail needs, so this is not a narrower rail -- it is a closed one.
  fireEvent.mouseDown(screen.getByRole("separator"), { clientX: 400 });
  fireEvent.mouseMove(window, { clientX: 600 });
  await waitFor(() => expect(screen.queryByText("plan.md")).toBeNull());
  expect(screen.getByTestId("file-rail").className).toContain("rail--collapsed");
  // Folded, it is the strip again -- and the strip has no edge to pull.
  expect(screen.queryByRole("separator")).toBeNull();
});

// Madde 356 (the design's items 158 and 177): the list and the open file are one width, held in App.
test("a file opens at the width the list was dragged to", async () => {
  withRail();
  window.history.pushState(null, "", "/p/p1/c/c1");
  render(<App />);
  await waitFor(() => expect(screen.getByText("plan.md")).toBeTruthy());

  fireEvent.mouseDown(screen.getByRole("separator"), { clientX: 600 });
  fireEvent.mouseMove(window, { clientX: 520 });
  fireEvent.mouseUp(window);
  fireEvent.click(screen.getByText("plan.md"));
  await waitFor(() => expect(screen.getByText("body")).toBeTruthy());
  const rail = screen.getByTestId("file-rail");
  expect(rail.className).toContain("rail--open");
  expect(rail.style.width).toBe("400px");
});

test("the open file's edge is pulled too, and the list keeps that width once it closes", async () => {
  withRail();
  window.history.pushState(null, "", "/p/p1/c/c1");
  render(<App />);
  await waitFor(() => expect(screen.getByText("plan.md")).toBeTruthy());
  fireEvent.click(screen.getByText("plan.md"));
  await waitFor(() => expect(screen.getByText("body")).toBeTruthy());

  fireEvent.mouseDown(screen.getByRole("separator"), { clientX: 600 });
  fireEvent.mouseMove(window, { clientX: 520 });
  fireEvent.mouseUp(window);
  await waitFor(() => expect(screen.getByTestId("file-rail").style.width).toBe("400px"));

  fireEvent.click(screen.getByRole("button", { name: "←" }));
  await waitFor(() => expect(screen.getByText("Project files")).toBeTruthy());
  expect(screen.getByTestId("file-rail").style.width).toBe("400px");
});

test("pulled past its minimum while reading, the file stays and the fold shows once it closes", async () => {
  withRail();
  window.history.pushState(null, "", "/p/p1/c/c1");
  render(<App />);
  await waitFor(() => expect(screen.getByText("plan.md")).toBeTruthy());
  fireEvent.click(screen.getByText("plan.md"));
  await waitFor(() => expect(screen.getByText("body")).toBeTruthy());

  // 320 - 200 is under the 220 the rail needs: the rail folds, but what is being read stays.
  fireEvent.mouseDown(screen.getByRole("separator"), { clientX: 400 });
  fireEvent.mouseMove(window, { clientX: 600 });
  fireEvent.mouseUp(window);
  expect(screen.getByText("body")).toBeTruthy();
  expect(screen.getByTestId("file-rail").style.width).toBe("320px");

  fireEvent.click(screen.getByRole("button", { name: "←" }));
  await waitFor(() =>
    expect(screen.getByTestId("file-rail").className).toContain("rail--collapsed"),
  );
});

test("opening a file empties the rail, and ← brings the list back", async () => {
  // Madde 63, end to end -- and the whole decision rests on the second half. Giving the rail over to
  // the document is only acceptable because the list is one press away, so the press is asked for
  // here rather than assumed. App's, not the rail's: the rail calls close, App is what it does.
  withRail();
  window.history.pushState(null, "", "/p/p1/c/c1");
  const { container } = render(<App />);
  await waitFor(() => expect(screen.getByText("plan.md")).toBeTruthy());

  fireEvent.click(screen.getByText("plan.md"));
  await waitFor(() => expect(screen.getByText("body")).toBeTruthy());
  expect(screen.queryByText("Project files")).toBeNull();
  // The row rather than the name: the reader's own header says "plan.md" too.
  expect(container.querySelector(".file-row")).toBeNull();

  fireEvent.click(screen.getByRole("button", { name: "←" }));
  await waitFor(() => expect(screen.getByText("Project files")).toBeTruthy());
  expect(container.querySelector(".file-row")).toBeTruthy();
});

test("the card in the transcript opens the file, unfolding the rail on the way", async () => {
  const file = { name: "plan.md", ext: "md", modifiedAt: new Date().toISOString() };
  const chat = {
    id: "c1",
    title: "Write the intro",
    messages: [
      { role: "user", at: new Date().toISOString(), text: "write it" },
      { role: "ai", at: new Date().toISOString(), text: "Done.", files: ["plan.md"] },
    ],
  };
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
    if (path.endsWith("/chats/c1")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => chat });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [PROJECT] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/c1");

  render(<App />);
  await waitFor(() => expect(screen.getByText("Done.")).toBeTruthy());
  fold();
  await waitFor(() => expect(screen.queryByText("project file · just now")).toBeNull());

  // The card is the second caller of the rule Madde 20 put in one place.
  fireEvent.click(screen.getByRole("button", { name: /plan\.md/ }));
  await waitFor(() => expect(screen.getByText("body")).toBeTruthy());
  expect(screen.getByTestId("file-rail").className).toContain("rail--open");
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
    return ok(path === "/api/projects" ? [PROJECT] : []);
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/new");

  render(<App />);
  await waitFor(() => expect(screen.getByText("plan.md")).toBeTruthy());
  await screen.findByText("Write the intro", { selector: ".sidebar__chat" });
  expect(screen.queryByRole("button", { name: "Rename plan.md" })).toBeNull();
  expect(screen.queryByRole("button", { name: "Rename Write the intro" })).toBeNull();
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
    return ok(path === "/api/projects" ? [PROJECT] : []);
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/new");

  render(<App />);
  await waitFor(() => expect(screen.getByText("plan.md")).toBeTruthy());
  fireEvent.click(screen.getByText("plan.md"));
  await waitFor(() => expect(screen.getByText("body")).toBeTruthy());

  fireEvent.keyDown(window, { key: "Escape" });
  await waitFor(() => expect(screen.queryByText("body")).toBeNull());
  // Escape closes; it never steps backwards.
  expect(window.location.pathname).toBe("/p/p1/c/new");
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
  // Inside a project, because that is the only place a composer stands.
  serverWithProjects([PROJECT]);
  window.history.pushState(null, "", "/p/p1/c/new");
  render(<App />);
  await waitFor(() => expect(screen.getByTestId("offline")).toBeTruthy());
  // The composer is not taken away: what is offline is the engine, not the machine.
  expect(screen.getByPlaceholderText("Reply...")).toBeTruthy();
  goOffline(false);
  await waitFor(() => expect(screen.queryByTestId("offline")).toBeNull());
});

test("offline nothing is sent, and coming back online sends nothing either", async () => {
  // The second half used to be the point: a chat owed an answer got one the moment the connection
  // returned. Madde 88 took that away -- an answer is something the user asks for, and a
  // connection coming back is not them asking.
  const owed = {
    id: "c1",
    title: "hello",
    messages: [{ role: "user", at: new Date().toISOString(), text: "hello" }],
  };
  const fetch = vi.fn().mockImplementation((path) => {
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
  expect(fetch.mock.calls.some(([, options]) => options?.method === "POST")).toBe(false);

  goOffline(false);
  await waitFor(() => expect(screen.queryByTestId("offline")).toBeNull());
  expect(fetch.mock.calls.some(([, options]) => options?.method === "POST")).toBe(false);
});

// --- one model, and the server names it (Madde 358) ----------------------------------------------

// Named for what it sets up rather than for the model it used to carry: a project with one chat in
// it, answering whatever the server is wired to.
function withChat() {
  const chats = [{ id: "c1", title: "Write the intro", lastActivity: new Date().toISOString() }];
  let chat = { id: "c1", title: "Write the intro", messages: [] };
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (path.endsWith("/chats/c1") && options?.method === "PATCH") {
      // Merged, the way the server merges: it writes the field it was given and leaves the other
      // alone -- the shape the server has, and the one a chat carrying more than a skill needed.
      chat = { ...chat, ...JSON.parse(options.body) };
      return Promise.resolve({ ok: true, status: 200, json: async () => chat });
    }
    if (path.endsWith("/chats/c1")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => chat });
    }
    if (path.endsWith("/messages") && options?.method === "POST") {
      return Promise.resolve({
        ok: true,
        status: 201,
        json: async () => ({ id: "c2", title: "new", messages: [] }),
      });
    }
    if (path.includes("/chats/")) {
      return Promise.resolve({
        ok: true,
        status: 200,
        json: async () => ({ id: "c2", title: "new", messages: [] }),
      });
    }
    if (path.endsWith("/chats")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => chats });
    }
    if (path.endsWith("/files")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => [] });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [PROJECT] });
  });
  vi.stubGlobal("fetch", fetch);
  return fetch;
}

// Its own fake rather than withChat's: this one serves a chat whose record carries a skill, which
// is the only way the picker and the session can disagree.
function withStoredSkill(stored = "edit-prompts") {
  const chat = { id: "c1", title: "Write the intro", skill: stored, messages: [] };
  const fetch = vi.fn().mockImplementation((path, options) => {
    // Today's app still PATCHes here. The fake answers it so a failure is the assertion below
    // rather than a screen that crashed on a shape it did not expect.
    if (String(path).endsWith("/chats/c1") && options?.method === "PATCH") {
      return Promise.resolve({
        ok: true,
        status: 200,
        json: async () => ({ ...chat, ...JSON.parse(options.body) }),
      });
    }
    // Both doors: the one the app uses today and the one Madde 87 moves it to. Kept together so a
    // test about the address fails on its own assertion rather than on a request that went nowhere.
    if (String(path).endsWith("/messages") && options?.method === "POST") {
      return Promise.resolve({ ok: true, status: 200, json: async () => chat });
    }
    if (String(path).endsWith("/chats/c1")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => chat });
    }
    if (String(path).endsWith("/chats")) {
      return Promise.resolve({
        ok: true,
        status: 200,
        json: async () => [
          { id: "c1", title: "Write the intro", lastActivity: new Date().toISOString() },
        ],
      });
    }
    if (String(path).endsWith("/files")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => [] });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [PROJECT] });
  });
  vi.stubGlobal("fetch", fetch);
  return fetch;
}

test("the app never asks which model to use", async () => {
  // One model, and it is the server's to name (Madde 358): there is nothing to ask about.
  const fetch = withChat();
  window.history.pushState(null, "", "/p/p1/c/c1");
  render(<App />);
  await chatOpened();
  expect(fetch.mock.calls.filter(([path]) => String(path) === "/api/model")).toHaveLength(0);
});

test("no model is named on the chat screen", async () => {
  // Madde 358, the user's words: no model is to be seen. Not as a picker, and not as a label.
  withChat();
  window.history.pushState(null, "", "/p/p1/c/c1");
  render(<App />);
  await chatOpened();
  expect(screen.queryByText(/Queen Flash/)).toBeNull();
  expect(screen.queryByText("MODELS")).toBeNull();
});

test("a chat is born naming no model", async () => {
  // Which model answers is the server's rule (FOUNDATION, Decision 4), so the message carries none.
  const fetch = withChat();
  window.history.pushState(null, "", "/p/p1/c/new");
  render(<App />);
  const box = await screen.findByPlaceholderText("Reply...");
  fireEvent.change(box, { target: { value: "hello" } });
  fireEvent.keyDown(box, { key: "Enter" });

  await waitFor(() => {
    const born = fetch.mock.calls.find(
      ([path, options]) => options?.method === "POST" && String(path).endsWith("/messages"),
    );
    expect(born).toBeTruthy();
    expect("model" in JSON.parse(born[1].body)).toBe(false);
  });
});

// --- which skill is selected ---------------------------------------------------------------------

test("picking a skill asks the server for nothing", async () => {
  // Madde 86: there is no field to write, so there is no request. The choice is the session's.
  const fetch = withStoredSkill("");
  window.history.pushState(null, "", "/p/p1/c/c1");
  render(<App />);
  await chatOpened();

  fireEvent.click(screen.getByRole("button", { name: /Skills/ }));
  fireEvent.click(screen.getByText("Edit prompts"));

  await waitFor(() => expect(screen.getByRole("button", { name: /Edit prompts/ })).toBeTruthy());
  expect(fetch.mock.calls.filter(([, options]) => options?.method === "PATCH")).toHaveLength(0);
});

test("a chat that stored a skill does not put it in the picker", async () => {
  // Opening an old chat says nothing about what this session picked -- and this session picked
  // nothing yet, so the picker is where it started.
  withStoredSkill();
  window.history.pushState(null, "", "/p/p1/c/c1");
  render(<App />);
  await chatOpened();
  expect(screen.queryByRole("button", { name: /Edit prompts/ })).toBeNull();
});

test("what the picker shows is what the message carries", async () => {
  // The bug Madde 86 closes: the picker read the record, the send read the session, and a chat
  // opened after a reload made the two say different things at the same moment.
  const fetch = withStoredSkill();
  window.history.pushState(null, "", "/p/p1/c/c1");
  render(<App />);
  const box = await chatOpened();
  fireEvent.change(box, { target: { value: "more" } });
  fireEvent.keyDown(box, { key: "Enter" });

  await waitFor(() => {
    const sent = fetch.mock.calls.find(
      ([path, options]) => String(path).endsWith("/messages") && options?.method === "POST",
    );
    expect(sent).toBeTruthy();
    expect(JSON.parse(sent[1].body).skill).toBe("");
  });
  expect(screen.queryByRole("button", { name: /Edit prompts/ })).toBeNull();
});

// --- one door for every sentence (Madde 87) ------------------------------------------------------

test("the first sentence goes through the one door with no chat named", async () => {
  // Madde 87: the browser stopped choosing between two addresses. A draft has no chat yet, and
  // that is a field in the body rather than a different endpoint.
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (String(path).endsWith("/messages") && options?.method === "POST") {
      return Promise.resolve({
        ok: true,
        status: 201,
        json: async () => ({ id: "c1", title: "hello", messages: [] }),
      });
    }
    if (String(path).endsWith("/chats")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => [] });
    }
    if (String(path).endsWith("/files")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => [] });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [PROJECT] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/new");

  render(<App />);
  const box = await screen.findByPlaceholderText("Reply...");
  fireEvent.change(box, { target: { value: "hello" } });
  fireEvent.keyDown(box, { key: "Enter" });

  await waitFor(() => {
    const sent = fetch.mock.calls.find(
      ([path, options]) => String(path).endsWith("/messages") && options?.method === "POST",
    );
    expect(sent).toBeTruthy();
    expect(String(sent[0])).toBe("/api/projects/p1/messages");
    expect(JSON.parse(sent[1].body).chat).toBeFalsy();
  });
});

test("a reply goes through the same door and names its chat", async () => {
  // The other half: same address, and the chat's id is what tells the two apart.
  const fetch = withStoredSkill("");
  window.history.pushState(null, "", "/p/p1/c/c1");
  render(<App />);
  const box = await chatOpened();
  fireEvent.change(box, { target: { value: "more" } });
  fireEvent.keyDown(box, { key: "Enter" });

  await waitFor(() => {
    const sent = fetch.mock.calls.find(
      ([path, options]) => String(path).endsWith("/messages") && options?.method === "POST",
    );
    expect(sent).toBeTruthy();
    expect(String(sent[0])).toBe("/api/projects/p1/messages");
    expect(JSON.parse(sent[1].body).chat).toBe("c1");
  });
});

test("the draft streams its first answer and moves to the new address", async () => {
  // Madde 88: the first frame carries the id, so the address changes while the answer is still
  // arriving. What has already arrived stays on the screen rather than being reloaded away -- the
  // hook knows it is streaming into that chat and does not go back to disk for it.
  const answered = {
    id: "c1",
    title: "hello",
    messages: [
      { role: "user", at: new Date().toISOString(), text: "hello" },
      { role: "ai", at: new Date().toISOString(), text: "Done." },
    ],
  };
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (String(path).endsWith("/messages") && options?.method === "POST") {
      return Promise.resolve(
        sseResponse(
          `event: chat\ndata: {"chat":"c1"}\n\n` +
            `event: chunk\ndata: {"text":"Done."}\n\nevent: done\ndata: {}\n\n`,
        ),
      );
    }
    // Read once when the turn closes, since Madde 89 -- and not before.
    if (String(path).endsWith("/chats/c1")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => answered });
    }
    if (String(path).endsWith("/files")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => [] });
    }
    if (String(path).endsWith("/chats")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => [] });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [PROJECT] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/new");

  render(<App />);
  const box = await chatOpened();
  fireEvent.change(box, { target: { value: "hello" } });
  fireEvent.keyDown(box, { key: "Enter" });

  await waitFor(() => expect(window.location.pathname).toBe("/p/p1/c/c1"));
  expect(screen.getByText("Done.")).toBeTruthy();
  // Read once, at the end of the turn -- Madde 89. Twice would mean the loading effect stepped in
  // while the answer was still arriving, which is the thing 88's guard exists to prevent.
  await waitFor(() =>
    expect(fetch.mock.calls.filter(([path]) => String(path).endsWith("/chats/c1"))).toHaveLength(1),
  );
});

// --- the record has one home (Madde 89) ----------------------------------------------------------

test("when the turn ends the record is read, and what it says is what is drawn", async () => {
  // What streamed is a guess and what was written is the record, so the screen ends up showing the
  // one the server can still hand back. The two are made to differ here on purpose.
  const empty = { id: "c1", title: "hello", messages: [] };
  const written = {
    id: "c1",
    title: "hello",
    messages: [
      { role: "user", at: new Date().toISOString(), text: "hello" },
      { role: "ai", at: new Date().toISOString(), text: "What the record says." },
    ],
  };
  let read = 0;
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (String(path).endsWith("/messages") && options?.method === "POST") {
      return Promise.resolve(
        sseResponse(
          `event: chat\ndata: {"chat":"c1"}\n\n` +
            `event: chunk\ndata: {"text":"What the stream said."}\n\n` +
            `event: done\ndata: {}\n\n`,
        ),
      );
    }
    if (String(path).endsWith("/chats/c1")) {
      read += 1;
      return Promise.resolve({
        ok: true,
        status: 200,
        json: async () => (read > 1 ? written : empty),
      });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/c1");

  render(<App />);
  const box = await chatOpened();
  fireEvent.change(box, { target: { value: "hello" } });
  fireEvent.keyDown(box, { key: "Enter" });

  await waitFor(() => expect(screen.getByText("What the record says.")).toBeTruthy());
  expect(screen.queryByText("What the stream said.")).toBeNull();
});

test("a chat that was just born is read by the id the first frame gave", async () => {
  const written = {
    id: "c1",
    title: "hello",
    messages: [
      { role: "user", at: new Date().toISOString(), text: "hello" },
      { role: "ai", at: new Date().toISOString(), text: "Done." },
    ],
  };
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (String(path).endsWith("/messages") && options?.method === "POST") {
      return Promise.resolve(
        sseResponse(`event: chat\ndata: {"chat":"c1"}\n\nevent: done\ndata: {}\n\n`),
      );
    }
    if (String(path).endsWith("/chats/c1")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => written });
    }
    if (String(path).endsWith("/files")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => [] });
    }
    if (String(path).endsWith("/chats")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => [] });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [PROJECT] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/new");

  render(<App />);
  const box = await chatOpened();
  fireEvent.change(box, { target: { value: "hello" } });
  fireEvent.keyDown(box, { key: "Enter" });

  await waitFor(() => expect(screen.getByText("Done.")).toBeTruthy());
});

test("a turn that ended in a fault is read back too", async () => {
  // The answer never came, but the question did reach disk -- and it has to stay on the screen.
  const written = {
    id: "c1",
    title: "hello",
    messages: [{ role: "user", at: new Date().toISOString(), text: "hello" }],
  };
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (String(path).endsWith("/messages") && options?.method === "POST") {
      return Promise.resolve(
        sseResponse(
          `event: chat\ndata: {"chat":"c1"}\n\nevent: error\ndata: {"error":"401 bad key"}\n\n`,
        ),
      );
    }
    if (String(path).endsWith("/chats/c1")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => written });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/c1");

  render(<App />);
  const box = await chatOpened();
  fireEvent.change(box, { target: { value: "hello" } });
  fireEvent.keyDown(box, { key: "Enter" });

  await waitFor(() => expect(screen.getByText("401 bad key")).toBeTruthy());
  expect(screen.getByText("hello", { selector: ".msg__bubble" })).toBeTruthy();
  // Twice: once on opening, once when the turn closed.
  await waitFor(() =>
    expect(fetch.mock.calls.filter(([path]) => String(path).endsWith("/chats/c1"))).toHaveLength(2),
  );
});

test("a record that cannot be read back says so in the read's own words", async () => {
  const empty = { id: "c1", title: "hello", messages: [] };
  let read = 0;
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (String(path).endsWith("/messages") && options?.method === "POST") {
      return Promise.resolve(
        sseResponse(`event: chat\ndata: {"chat":"c1"}\n\nevent: done\ndata: {}\n\n`),
      );
    }
    if (String(path).endsWith("/chats/c1")) {
      read += 1;
      if (read > 1) {
        return Promise.resolve({
          ok: false,
          status: 500,
          text: async () => JSON.stringify({ error: "the disk went away" }),
        });
      }
      return Promise.resolve({ ok: true, status: 200, json: async () => empty });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/c1");

  render(<App />);
  const box = await chatOpened();
  fireEvent.change(box, { target: { value: "hello" } });
  fireEvent.keyDown(box, { key: "Enter" });

  // The read's own sentence, not a guess about what went wrong.
  await waitFor(() => expect(screen.getByText("the disk went away")).toBeTruthy());
});

test("the skill picked in a draft survives landing in the chat it created", async () => {
  // The accepted cost, written down: the choice belongs to the session, so it crosses into the
  // chat that was just born even though that chat's record says otherwise.
  // A name Madde 94 deleted, on purpose: the record has to say something other than what the
  // session picked, and an old record saying a gone name is exactly what happens on disk.
  const born = { id: "c1", title: "Write it", skill: "verify-prompts", messages: [] };
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (String(path).endsWith("/messages") && options?.method === "POST") {
      return Promise.resolve(
        sseResponse(
          `event: chat\ndata: {"chat":"c1"}\n\nevent: done\ndata: ${JSON.stringify(born)}\n\n`,
        ),
      );
    }
    if (String(path).endsWith("/chats/c1")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => born });
    }
    if (String(path).endsWith("/chats")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => [] });
    }
    if (String(path).endsWith("/files")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => [] });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [PROJECT] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/new");

  render(<App />);
  await chatOpened();
  fireEvent.click(screen.getByRole("button", { name: /Skills/ }));
  fireEvent.click(screen.getByText("Edit prompts", { selector: ".menu__item-name" }));

  const box = await chatOpened();
  fireEvent.change(box, { target: { value: "Write it" } });
  fireEvent.keyDown(box, { key: "Enter" });

  await waitFor(() => expect(window.location.pathname).toBe("/p/p1/c/c1"));
  expect(screen.getByRole("button", { name: /Edit prompts/ })).toBeTruthy();
});

test("a draft's first answer never wears the old chat's transcript", async () => {
  // Madde 104. The screen stood in an old chat, moved to the draft, and sent. The address follows
  // the newborn chat (Madde 88); what must not follow is the old chat's record, which the hook was
  // still holding and the first bubble was appended to. The stream is held open so the assertion
  // lands mid-answer, where the wrong transcript used to show.
  const old = {
    id: "c1",
    title: "The old chat",
    messages: [
      { role: "user", at: new Date().toISOString(), text: "old question" },
      { role: "ai", at: new Date().toISOString(), text: "The old answer." },
    ],
  };
  const born = {
    id: "c2",
    title: "hello",
    messages: [
      { role: "user", at: new Date().toISOString(), text: "hello" },
      { role: "ai", at: new Date().toISOString(), text: "Fresh." },
    ],
  };
  const { response, release } = gatedSse(
    `event: chat\ndata: {"chat":"c2"}\n\nevent: chunk\ndata: {"text":"Fresh"}\n\n`,
    `event: done\ndata: {}\n\n`,
  );
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (String(path).endsWith("/messages") && options?.method === "POST") {
      return Promise.resolve(response);
    }
    if (String(path).endsWith("/chats/c1")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => old });
    }
    if (String(path).endsWith("/chats/c2")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => born });
    }
    if (String(path).endsWith("/chats")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => [] });
    }
    if (String(path).endsWith("/files")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => [] });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [PROJECT] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/c1");

  render(<App />);
  await waitFor(() => expect(screen.getByText("The old answer.")).toBeTruthy());

  fireEvent.click(screen.getByRole("button", { name: /New chat/ }));
  const box = await chatOpened();
  fireEvent.change(box, { target: { value: "hello" } });
  fireEvent.keyDown(box, { key: "Enter" });

  // The address moves to the newborn while the answer still runs...
  await waitFor(() => expect(window.location.pathname).toBe("/p/p1/c/c2"));
  // ...and the screen is the newborn's: the user's own sentence, never the chat that was left.
  expect(screen.queryByText("The old answer.")).toBeNull();
  expect(screen.getByText("hello", { selector: ".msg__bubble" })).toBeTruthy();

  await act(async () => {
    release();
  });
  await waitFor(() => expect(screen.getByText("Fresh.")).toBeTruthy());
});

test("an answer streaming in one chat does not show in another", async () => {
  // Madde 106. What the stream draws belongs to the chat it runs into: standing in another chat,
  // none of it shows -- and coming back, it shows again.
  const records = {
    c1: { id: "c1", title: "First", messages: [] },
    c2: { id: "c2", title: "Second", messages: [] },
  };
  const rows = [
    { id: "c1", title: "First", lastActivity: new Date().toISOString() },
    { id: "c2", title: "Second", lastActivity: new Date().toISOString() },
  ];
  const { response, release } = gatedSse(
    `event: chat\ndata: {"chat":"c1"}\n\nevent: chunk\ndata: {"text":"Halfway there"}\n\n`,
    `event: done\ndata: {}\n\n`,
  );
  vi.stubGlobal(
    "fetch",
    vi.fn().mockImplementation((path, options) => {
      if (String(path).endsWith("/messages") && options?.method === "POST") {
        return Promise.resolve(response);
      }
      if (String(path).endsWith("/chats/c1")) {
        return Promise.resolve({ ok: true, status: 200, json: async () => records.c1 });
      }
      if (String(path).endsWith("/chats/c2")) {
        return Promise.resolve({ ok: true, status: 200, json: async () => records.c2 });
      }
      if (String(path).endsWith("/chats")) {
        return Promise.resolve({ ok: true, status: 200, json: async () => rows });
      }
      if (String(path).endsWith("/files")) {
        return Promise.resolve({ ok: true, status: 200, json: async () => [] });
      }
      return Promise.resolve({ ok: true, status: 200, json: async () => [PROJECT] });
    }),
  );
  window.history.pushState(null, "", "/p/p1/c/c1");

  render(<App />);
  const box = await chatOpened();
  fireEvent.change(box, { target: { value: "go" } });
  fireEvent.keyDown(box, { key: "Enter" });
  await waitFor(() => expect(screen.getByText("Halfway there")).toBeTruthy());

  fireEvent.click(screen.getByText("Second", { selector: ".sidebar__chat" }));
  await waitFor(() => expect(window.location.pathname).toBe("/p/p1/c/c2"));
  expect(screen.queryByText("Halfway there")).toBeNull();
  expect(screen.queryByTestId("thinking")).toBeNull();

  fireEvent.click(screen.getByText("First", { selector: ".sidebar__chat" }));
  await waitFor(() => expect(screen.getByText("Halfway there")).toBeTruthy());

  await act(async () => {
    release();
  });
});

test("a turn that ends in a left chat does not repaint the one the user is standing in", async () => {
  // Madde 106. The turn still ends by reading the record (Madde 89) -- what changed is that the
  // read dresses only the screen standing in the chat it landed in. The wait below is two claims
  // on purpose: the read has happened AND the streamed line has gone dark, which is the finally
  // that runs after the repaint used to land.
  const finished = {
    id: "c1",
    title: "First",
    messages: [
      { role: "user", at: new Date().toISOString(), text: "go" },
      { role: "ai", at: new Date().toISOString(), text: "The finished answer." },
    ],
  };
  const second = {
    id: "c2",
    title: "Second",
    messages: [{ role: "user", at: new Date().toISOString(), text: "Second's own words" }],
  };
  const rows = [
    { id: "c1", title: "First", lastActivity: new Date().toISOString() },
    { id: "c2", title: "Second", lastActivity: new Date().toISOString() },
  ];
  let c1Reads = 0;
  const { response, release } = gatedSse(
    `event: chat\ndata: {"chat":"c1"}\n\nevent: chunk\ndata: {"text":"running"}\n\n`,
    `event: done\ndata: {}\n\n`,
  );
  vi.stubGlobal(
    "fetch",
    vi.fn().mockImplementation((path, options) => {
      if (String(path).endsWith("/messages") && options?.method === "POST") {
        return Promise.resolve(response);
      }
      if (String(path).endsWith("/chats/c1")) {
        c1Reads += 1;
        return Promise.resolve({
          ok: true,
          status: 200,
          json: async () => (c1Reads > 1 ? finished : { id: "c1", title: "First", messages: [] }),
        });
      }
      if (String(path).endsWith("/chats/c2")) {
        return Promise.resolve({ ok: true, status: 200, json: async () => second });
      }
      if (String(path).endsWith("/chats")) {
        return Promise.resolve({ ok: true, status: 200, json: async () => rows });
      }
      if (String(path).endsWith("/files")) {
        return Promise.resolve({ ok: true, status: 200, json: async () => [] });
      }
      return Promise.resolve({ ok: true, status: 200, json: async () => [PROJECT] });
    }),
  );
  window.history.pushState(null, "", "/p/p1/c/c1");

  render(<App />);
  const box = await chatOpened();
  fireEvent.change(box, { target: { value: "go" } });
  fireEvent.keyDown(box, { key: "Enter" });
  await waitFor(() => expect(screen.getByText("running")).toBeTruthy());

  fireEvent.click(screen.getByText("Second", { selector: ".sidebar__chat" }));
  await waitFor(() => expect(screen.getByText("Second's own words")).toBeTruthy());

  await act(async () => {
    release();
  });
  await waitFor(() => {
    expect(c1Reads).toBeGreaterThan(1);
    expect(screen.queryByText("running")).toBeNull();
  });
  expect(screen.queryByText("The finished answer.")).toBeNull();
  expect(screen.getByText("Second's own words")).toBeTruthy();

  fireEvent.click(screen.getByText("First", { selector: ".sidebar__chat" }));
  await waitFor(() => expect(screen.getByText("The finished answer.")).toBeTruthy());
});

test("coming back to a streaming chat finds its transcript and its stream", async () => {
  // Madde 106's third face. The birth guard (Madde 88) kept the load away while a stream ran; a
  // return from another chat needs it -- what stands in the state is the other chat's record, and
  // the transcript on this screen has to be this chat's own, from disk, with the stream on top.
  const first = {
    id: "c1",
    title: "First",
    messages: [{ role: "user", at: new Date().toISOString(), text: "First words on disk" }],
  };
  const second = {
    id: "c2",
    title: "Second",
    messages: [{ role: "user", at: new Date().toISOString(), text: "Second's own words" }],
  };
  const rows = [
    { id: "c1", title: "First", lastActivity: new Date().toISOString() },
    { id: "c2", title: "Second", lastActivity: new Date().toISOString() },
  ];
  const { response, release } = gatedSse(
    `event: chat\ndata: {"chat":"c1"}\n\nevent: chunk\ndata: {"text":"Live tail"}\n\n`,
    `event: done\ndata: {}\n\n`,
  );
  vi.stubGlobal(
    "fetch",
    vi.fn().mockImplementation((path, options) => {
      if (String(path).endsWith("/messages") && options?.method === "POST") {
        return Promise.resolve(response);
      }
      if (String(path).endsWith("/chats/c1")) {
        return Promise.resolve({ ok: true, status: 200, json: async () => first });
      }
      if (String(path).endsWith("/chats/c2")) {
        return Promise.resolve({ ok: true, status: 200, json: async () => second });
      }
      if (String(path).endsWith("/chats")) {
        return Promise.resolve({ ok: true, status: 200, json: async () => rows });
      }
      if (String(path).endsWith("/files")) {
        return Promise.resolve({ ok: true, status: 200, json: async () => [] });
      }
      return Promise.resolve({ ok: true, status: 200, json: async () => [PROJECT] });
    }),
  );
  window.history.pushState(null, "", "/p/p1/c/c1");

  render(<App />);
  const box = await chatOpened();
  fireEvent.change(box, { target: { value: "go" } });
  fireEvent.keyDown(box, { key: "Enter" });
  await waitFor(() => expect(screen.getByText("Live tail")).toBeTruthy());

  fireEvent.click(screen.getByText("Second", { selector: ".sidebar__chat" }));
  await waitFor(() => expect(screen.getByText("Second's own words")).toBeTruthy());

  fireEvent.click(screen.getByText("First", { selector: ".sidebar__chat" }));
  await waitFor(() =>
    expect(screen.getByText("First words on disk", { selector: ".msg__bubble" })).toBeTruthy(),
  );
  expect(screen.queryByText("Second's own words")).toBeNull();
  expect(screen.getByText("Live tail")).toBeTruthy();

  await act(async () => {
    release();
  });
});

test("a skill picked in a chat does not ride into a chat born in the draft", async () => {
  // Madde 105 overturned Madde 86 here: the selection was the session's, so a skill picked in one
  // chat rode into every chat born after it. The selection is the chat's own now.
  const fetch = withChat();
  window.history.pushState(null, "", "/p/p1/c/c1");
  render(<App />);
  await chatOpened();
  fireEvent.click(screen.getByRole("button", { name: /Skills/ }));
  fireEvent.click(screen.getByText("Edit prompts"));
  await waitFor(() => expect(screen.getByRole("button", { name: /Edit prompts/ })).toBeTruthy());

  fireEvent.click(screen.getByRole("button", { name: /New chat/ }));
  await waitFor(() => expect(window.location.pathname).toBe("/p/p1/c/new"));
  const box = screen.getByPlaceholderText("Reply...");
  fireEvent.change(box, { target: { value: "hello" } });
  fireEvent.keyDown(box, { key: "Enter" });

  await waitFor(() => {
    const sent = fetch.mock.calls.find(
      ([path, options]) => String(path).endsWith("/messages") && options?.method === "POST",
    );
    expect(sent).toBeTruthy();
    expect(JSON.parse(sent[1].body).skill).toBe("");
  });
});

test("a skill picked in one chat stays that chat's own", async () => {
  // Madde 105. Two chats, one picker: what is picked while standing in the first shows only
  // there -- and is still standing when the user comes back.
  const records = {
    c1: { id: "c1", title: "First", messages: [] },
    c2: { id: "c2", title: "Second", messages: [] },
  };
  const rows = [
    { id: "c1", title: "First", lastActivity: new Date().toISOString() },
    { id: "c2", title: "Second", lastActivity: new Date().toISOString() },
  ];
  vi.stubGlobal(
    "fetch",
    vi.fn().mockImplementation((path) => {
      if (String(path).endsWith("/chats/c1")) {
        return Promise.resolve({ ok: true, status: 200, json: async () => records.c1 });
      }
      if (String(path).endsWith("/chats/c2")) {
        return Promise.resolve({ ok: true, status: 200, json: async () => records.c2 });
      }
      if (String(path).endsWith("/chats")) {
        return Promise.resolve({ ok: true, status: 200, json: async () => rows });
      }
      if (String(path).endsWith("/files")) {
        return Promise.resolve({ ok: true, status: 200, json: async () => [] });
      }
      return Promise.resolve({ ok: true, status: 200, json: async () => [PROJECT] });
    }),
  );
  window.history.pushState(null, "", "/p/p1/c/c1");

  render(<App />);
  await chatOpened();
  fireEvent.click(screen.getByRole("button", { name: /Skills/ }));
  fireEvent.click(screen.getByText("Edit prompts", { selector: ".menu__item-name" }));
  await waitFor(() =>
    expect(screen.getByRole("button", { name: /Edit prompts/ })).toBeTruthy(),
  );

  fireEvent.click(screen.getByText("Second", { selector: ".sidebar__chat" }));
  await waitFor(() => expect(window.location.pathname).toBe("/p/p1/c/c2"));
  expect(screen.getByRole("button", { name: /Skills/ })).toBeTruthy();
  expect(screen.queryByRole("button", { name: /Edit prompts/ })).toBeNull();

  fireEvent.click(screen.getByText("First", { selector: ".sidebar__chat" }));
  await waitFor(() => expect(window.location.pathname).toBe("/p/p1/c/c1"));
  expect(screen.getByRole("button", { name: /Edit prompts/ })).toBeTruthy();
});

test("a second draft does not wear the first one's skill", async () => {
  // Madde 105. The draft's selection is what the chat about to be born will own; once it is born,
  // the next draft starts with nothing.
  const born = { id: "c1", title: "Write it", skill: "edit-prompts", messages: [] };
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (String(path).endsWith("/messages") && options?.method === "POST") {
      return Promise.resolve(
        sseResponse(`event: chat\ndata: {"chat":"c1"}\n\nevent: done\ndata: {}\n\n`),
      );
    }
    if (String(path).endsWith("/chats/c1")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => born });
    }
    if (String(path).endsWith("/chats")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => [] });
    }
    if (String(path).endsWith("/files")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => [] });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [PROJECT] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/new");

  render(<App />);
  await chatOpened();
  fireEvent.click(screen.getByRole("button", { name: /Skills/ }));
  fireEvent.click(screen.getByText("Edit prompts", { selector: ".menu__item-name" }));

  const box = await chatOpened();
  fireEvent.change(box, { target: { value: "Write it" } });
  fireEvent.keyDown(box, { key: "Enter" });
  await waitFor(() => expect(window.location.pathname).toBe("/p/p1/c/c1"));

  fireEvent.click(screen.getByRole("button", { name: /New chat/ }));
  await waitFor(() => expect(window.location.pathname).toBe("/p/p1/c/new"));
  expect(screen.getByRole("button", { name: /Skills/ })).toBeTruthy();
  expect(screen.queryByRole("button", { name: /Edit prompts/ })).toBeNull();
});

test("picking a skill closes the menu", async () => {
  // Closing was written twice -- once in Menu, once in App -- and the two landed in the same batch,
  // so the toggle re-opened what the other had just closed.
  withChat();
  window.history.pushState(null, "", "/p/p1/c/c1");
  render(<App />);
  await chatOpened();

  fireEvent.click(screen.getByRole("button", { name: /Skills/ }));
  fireEvent.click(screen.getByText("Edit prompts", { selector: ".menu__item-name" }));
  await waitFor(() => expect(screen.queryByText("SKILLS")).toBeNull());
});

test("in a draft, picking a skill closes the menu too", async () => {
  // A draft has no chat to write to, so it takes a different path out of the same menu.
  withChat();
  window.history.pushState(null, "", "/p/p1/c/new");
  render(<App />);
  await chatOpened();

  fireEvent.click(screen.getByRole("button", { name: /Skills/ }));
  fireEvent.click(screen.getByText("Edit prompts", { selector: ".menu__item-name" }));
  await waitFor(() => expect(screen.queryByText("SKILLS")).toBeNull());
});

test("Escape closes the picker", async () => {
  // fark 67 put five things in order: project menu -> confirm box -> Skills -> model -> open panel.
  // The model has no picker (Madde 358), and the pickers left share one place in the order.
  withChat();
  window.history.pushState(null, "", "/p/p1/c/c1");
  render(<App />);
  await chatOpened();

  fireEvent.click(screen.getByRole("button", { name: /Skills/ }));
  expect(screen.getByText("SKILLS")).toBeTruthy();
  fireEvent.keyDown(window, { key: "Escape" });
  expect(screen.queryByText("SKILLS")).toBeNull();
});

// --- which mode a turn is sent in (Madde 91) -----------------------------------------------------

test("the mode in force is what the message is sent with", async () => {
  const fetch = withChat();
  window.history.pushState(null, "", "/p/p1/c/c1");
  render(<App />);
  await chatOpened();

  fireEvent.click(screen.getByText("Edit", { selector: ".picker__name" }));
  fireEvent.click(screen.getByText("Ask", { selector: ".menu__item-name" }));
  const box = await chatOpened();
  fireEvent.change(box, { target: { value: "hello" } });
  fireEvent.keyDown(box, { key: "Enter" });

  await waitFor(() => {
    const sent = fetch.mock.calls.find(
      ([path, options]) => String(path).endsWith("/messages") && options?.method === "POST",
    );
    expect(sent).toBeTruthy();
    expect(JSON.parse(sent[1].body).mode).toBe("ask");
  });
});

test("opening one picker closes the other", async () => {
  // One value owns which picker is open rather than one boolean each: two booleans can both be
  // true, and then two menus stand over the same corner of the screen.
  withChat();
  window.history.pushState(null, "", "/p/p1/c/c1");
  render(<App />);
  await chatOpened();

  fireEvent.click(screen.getByRole("button", { name: /Skills/ }));
  expect(screen.getByText("SKILLS")).toBeTruthy();
  fireEvent.click(screen.getByText("Edit", { selector: ".picker__name" }));
  expect(screen.queryByText("SKILLS")).toBeNull();
  expect(screen.getByText("MODE")).toBeTruthy();
});

// --- the question the screen asks (Madde 102) ----------------------------------------------------

const ASKING =
  'event: chat\ndata: {"chat":"c1"}\n\n' +
  'event: permission\ndata: {"tool":"create_file","arguments":"{\\"name\\": \\"plan.md\\"}"}\n\n';

function paused(onAnswer) {
  /* A chat mid-answer, stopped on a question. The gate is released by whatever answers the door,
     so the turn only finishes once the test has pressed something -- the same shape the stop test
     uses, and nothing in it depends on timing. */
  const owed = { id: "c1", title: "hello", messages: [] };
  const { response, release } = gatedSse(ASKING, `event: done\ndata: ${JSON.stringify(owed)}\n\n`);
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (path.endsWith("/messages") && options?.method === "POST") return Promise.resolve(response);
    if (path.endsWith("/permission") && options?.method === "POST") {
      onAnswer?.(path, JSON.parse(options.body));
      release();
      return Promise.resolve({ ok: true, status: 200, json: async () => ({}) });
    }
    if (path.endsWith("/chats/c1"))
      return Promise.resolve({ ok: true, status: 200, json: async () => owed });
    return Promise.resolve({ ok: true, status: 200, json: async () => [] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/c1");
  return { fetch, release };
}

async function asked() {
  render(<App />);
  const box = await chatOpened();
  /* Sent in ask mode, which is the mode the question exists for -- and it is also what makes the
     picker's move afterwards something to see: the app starts in edit, where nothing is asked. */
  fireEvent.click(screen.getByText("Edit", { selector: ".picker__name" }));
  fireEvent.click(screen.getByText("Ask", { selector: ".menu__item-name" }));
  fireEvent.change(box, { target: { value: "write the plan" } });
  fireEvent.keyDown(box, { key: "Enter" });
  return screen.findByText("QueenAgent wants to run create_file");
}

test("a permission frame puts the card up while the answer is still running", async () => {
  const { release } = paused();
  await asked();
  expect(screen.getByText('{"name": "plan.md"}')).toBeTruthy();
  release();
});

test("allowing sends the yes to the chat's own door", async () => {
  let sent = null;
  const { release } = paused((path, body) => {
    sent = { path, body };
  });
  await asked();
  fireEvent.click(screen.getByText("Allow"));
  await waitFor(() => expect(sent).toBeTruthy());
  expect(sent.path).toContain("/api/projects/p1/chats/c1/permission");
  expect(sent.body).toEqual({ allowed: true });
  release();
});

test("allowing moves the mode picker to edit", async () => {
  // The answer settles this one call; the picker is what settles the next turn. Left on Ask, the
  // very next message would raise the same question again.
  paused();
  await asked();
  expect(screen.getByText("Ask", { selector: ".picker__name" })).toBeTruthy();
  fireEvent.click(screen.getByText("Allow"));
  await waitFor(() => expect(screen.getByText("Edit", { selector: ".picker__name" })).toBeTruthy());
});

test("denying carries the reason the user typed", async () => {
  let sent = null;
  paused((path, body) => {
    sent = body;
  });
  await asked();
  fireEvent.change(screen.getByPlaceholderText("Why not? (optional)"), {
    target: { value: "not that file" },
  });
  fireEvent.click(screen.getByText("Deny"));
  await waitFor(() => expect(sent).toBeTruthy());
  expect(sent).toEqual({ allowed: false, reason: "not that file" });
});

test("answering takes the card down", async () => {
  paused();
  await asked();
  fireEvent.click(screen.getByText("Allow"));
  await waitFor(() => expect(screen.queryByText("QueenAgent wants to run create_file")).toBeNull());
});

test("the send button is still a stop while the card stands", async () => {
  // The wait has no end and no timeout, so the way out is the button that was already there.
  const { release } = paused();
  await asked();
  expect(screen.getByTitle("Stop")).toBeTruthy();
  release();
});

test("a turn that ends unanswered takes the card with it", async () => {
  // A stop, or a stream that died. Left standing, the card would hang over the next turn offering
  // to allow something nobody is waiting on any more.
  //
  // The card has to be seen standing before its absence means anything -- without that half this
  // would also pass on a card that was never drawn.
  const { fetch, release } = paused();
  await asked();
  release();
  await waitFor(() => expect(screen.queryByText("QueenAgent wants to run create_file")).toBeNull());
  expect(fetch.mock.calls.some(([path]) => String(path).endsWith("/permission"))).toBe(false);
});

// --- the selection the browser keeps (Madde 100) -------------------------------------------------

async function reborn() {
  /* The app mounted a second time over the same browser. A reload is what this stands for: React
     state is gone and only what was written down survives. */
  cleanup();
  render(<App />);
  return chatOpened();
}

async function picked() {
  render(<App />);
  await chatOpened();
  fireEvent.click(screen.getByRole("button", { name: /Skills/ }));
  fireEvent.click(screen.getByText("Edit prompts", { selector: ".menu__item-name" }));
  return waitFor(() =>
    expect(screen.getByRole("button", { name: /Edit prompts/ })).toBeTruthy(),
  );
}

test("a skill picked survives the app being mounted again", async () => {
  withChat();
  window.history.pushState(null, "", "/p/p1/c/c1");
  await picked();

  await reborn();
  expect(screen.getByRole("button", { name: /Edit prompts/ })).toBeTruthy();
});

test("the message sent after a reload carries the remembered skill", async () => {
  // The point of the item: mid-flow, a turn that goes without its instruction is a turn nobody
  // asked for, and nothing on screen would have said so.
  withChat();
  window.history.pushState(null, "", "/p/p1/c/c1");
  await picked();

  const fetch = withChat();
  await reborn();
  const box = await chatOpened();
  fireEvent.change(box, { target: { value: "carry on" } });
  fireEvent.keyDown(box, { key: "Enter" });

  await waitFor(() => {
    const sent = fetch.mock.calls.find(
      ([path, options]) => String(path).endsWith("/messages") && options?.method === "POST",
    );
    expect(sent).toBeTruthy();
    expect(JSON.parse(sent[1].body).skill).toBe("edit-prompts");
  });
});

// Letting the skill go is not asked about here. On this screen an empty selection and no selection
// draw the same button, so the claim cannot fail whatever the code does -- and a test that cannot
// fail is noise. It is asked where the two are told apart: the hook's own test, with a fallback
// that is not the empty string.

test("Escape closes the mode picker too", async () => {
  // The order fark 67 settled had two pickers in it and lost one in Madde 82. A second picker is
  // back, so the same key has to reach it.
  withChat();
  window.history.pushState(null, "", "/p/p1/c/c1");
  render(<App />);
  await chatOpened();

  fireEvent.click(screen.getByText("Edit", { selector: ".picker__name" }));
  expect(screen.getByText("MODE")).toBeTruthy();
  fireEvent.keyDown(window, { key: "Escape" });
  expect(screen.queryByText("MODE")).toBeNull();
});

// --- editing a message and stepping between the versions (Madde 195) -----------------------------

test("a message is edited, the chat carries on from there, and the arrow goes back", async () => {
  // The madde's own "how it is seen", on the real screen: the old line is not gone, and the answer
  // it was given is still the answer it was given.
  const at = new Date().toISOString();
  const alone = { index: 0, of: 1, versions: [""] };
  const first = {
    id: "c1",
    title: "Write the intro",
    messages: [
      { role: "user", at, text: "Write the intro", variants: alone },
      { role: "ai", at, text: "Here it is.", variants: alone },
    ],
  };
  const edited = {
    ...first,
    messages: [
      {
        role: "user",
        at,
        text: "Write a shorter intro",
        variants: { index: 1, of: 2, versions: ["", "l2"] },
      },
      { role: "ai", at, text: "Shorter.", variants: alone },
    ],
  };
  // Which line the server would answer with. The browser never decides this: it asks for a version
  // and reads back whatever came.
  let open = first;
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (path.endsWith("/messages") && options?.method === "POST") {
      open = edited;
      return Promise.resolve(
        sseResponse(`event: chat\ndata: {"chat":"c1"}\n\nevent: done\ndata: {}\n\n`),
      );
    }
    if (path.endsWith("/version") && options?.method === "POST") {
      open = JSON.parse(options.body).version === "" ? first : edited;
      return Promise.resolve({ ok: true, status: 200, json: async () => ({}) });
    }
    if (path.endsWith("/chats/c1")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => open });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/c1");

  const { container } = render(<App />);
  await waitFor(() => expect(screen.getByText("Here it is.")).toBeTruthy());
  fireEvent.click(await screen.findByRole("button", { name: "Edit message" }));
  // Madde 197: corrected where it stands, and the composer is left alone.
  const field = container.querySelector(".msg__editing-input");
  expect(field.value).toBe("Write the intro");
  expect(screen.getByPlaceholderText("Reply...").value).toBe("");
  fireEvent.change(field, { target: { value: "Write a shorter intro" } });
  fireEvent.click(screen.getByRole("button", { name: "Confirm edit" }));

  await waitFor(() => expect(screen.getByText("Shorter.")).toBeTruthy());
  const sent = JSON.parse(
    fetch.mock.calls.find(([path, options]) => path.endsWith("/messages") && options?.method === "POST")[1].body,
  );
  expect(sent.from).toBe(0);
  expect(screen.getByText("2/2")).toBeTruthy();

  fireEvent.click(screen.getByRole("button", { name: "Previous version" }));
  await waitFor(() => expect(screen.getByText("Here it is.")).toBeTruthy());
  expect(screen.queryByText("Shorter.")).toBeNull();
});

// --- the full chat's notice (Madde 352) ----------------------------------------------------------

const turn = (answer) => [
  { role: "user", at: new Date().toISOString(), text: "go on" },
  { role: "ai", at: new Date().toISOString(), text: answer },
];

// A chat the server calls full until the trim door is knocked on; `trim` is what the door answers.
function stubFullChat(trim = { ok: true, status: 200, json: async () => ({}) }) {
  let record = {
    id: "c1",
    title: "Long",
    full: true,
    trimmed: 0,
    context: { sent: 50000, ceiling: 50000 },
    messages: [...turn("First answer."), ...turn("Last answer.")],
  };
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (path.endsWith("/trim") && options?.method === "POST") {
      if (trim.ok) {
        record = { ...record, full: false, trimmed: 2, context: { sent: 9000, ceiling: 50000 } };
      }
      return Promise.resolve(trim);
    }
    if (path.endsWith("/chats/c1")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => record });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/c1");
  return fetch;
}

test("the notice's New chat opens the project's draft", async () => {
  stubFullChat();
  render(<App />);
  await screen.findByText("This chat is full.");
  fireEvent.click(within(document.querySelector(".full")).getByRole("button", { name: "New chat" }));
  await waitFor(() => expect(window.location.pathname).toBe("/p/p1/c/new"));
});

test("Continue here trims the chat, and it takes messages again with every message still drawn", async () => {
  const fetch = stubFullChat();
  render(<App />);
  await screen.findByText("This chat is full.");
  expect(screen.queryByRole("textbox")).toBeNull();

  // Asked nothing first and undone by nothing after (the owner's call, 29 September).
  fireEvent.click(screen.getByRole("button", { name: "Continue here" }));
  await waitFor(() => expect(screen.queryByText("This chat is full.")).toBeNull());
  const posts = fetch.mock.calls.filter(([, options]) => options?.method === "POST");
  expect(posts.map(([path]) => path)).toEqual(["/api/projects/p1/chats/c1/trim"]);
  expect(screen.getByRole("textbox")).toBeTruthy();
  expect(screen.getByText("First answer.")).toBeTruthy();
  expect(screen.getByText("Last answer.")).toBeTruthy();
});

test("a refusal met while the chat was full goes with Continue here", async () => {
  // The question filled the chat and its answer never came; Try again then met the ceiling. What
  // the refusal said stops being true the moment the chat is trimmed.
  let record = { id: "c1", title: "Long", full: false, trimmed: 0, messages: turn("Last answer.") };
  let posts = 0;
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (path.endsWith("/messages") && options?.method === "POST") {
      posts += 1;
      if (posts === 1) {
        const asked = { role: "user", at: new Date().toISOString(), text: "and more" };
        record = { ...record, full: true, messages: [...record.messages, asked] };
        return Promise.resolve(
          sseResponse('event: chat\ndata: {"chat":"c1"}\n\nevent: error\ndata: {"error":"502 upstream"}\n\n'),
        );
      }
      return Promise.resolve({
        ok: false,
        status: 400,
        text: async () => JSON.stringify({ error: "this chat has reached its context ceiling" }),
      });
    }
    if (path.endsWith("/trim") && options?.method === "POST") {
      record = { ...record, full: false, trimmed: 2 };
      return Promise.resolve({ ok: true, status: 200, json: async () => ({}) });
    }
    if (path.endsWith("/chats/c1")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => record });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/c1");

  render(<App />);
  const box = await chatOpened();
  fireEvent.change(box, { target: { value: "and more" } });
  fireEvent.keyDown(box, { key: "Enter" });
  await screen.findByText("502 upstream");
  await screen.findByText("This chat is full.");

  fireEvent.click(screen.getByRole("button", { name: "Try again" }));
  await screen.findByText("this chat has reached its context ceiling");

  fireEvent.click(screen.getByRole("button", { name: "Continue here" }));
  await waitFor(() => expect(screen.queryByText("This chat is full.")).toBeNull());
  expect(screen.queryByText("Couldn't get a response.")).toBeNull();
});

test("a trim the server refuses says so in the server's own words", async () => {
  stubFullChat({
    ok: false,
    status: 400,
    text: async () => JSON.stringify({ error: "this chat is not full" }),
  });
  render(<App />);
  await screen.findByText("This chat is full.");
  fireEvent.click(screen.getByRole("button", { name: "Continue here" }));
  expect(await screen.findByText("this chat is not full")).toBeTruthy();
});

// --- the trim's line (Madde 357) -----------------------------------------------------------------

test("after Continue here a line parts the messages no longer sent from the rest", async () => {
  stubFullChat();
  const { container } = render(<App />);
  await screen.findByText("This chat is full.");
  expect(container.querySelector(".trimmed")).toBeNull();

  fireEvent.click(screen.getByRole("button", { name: "Continue here" }));
  const line = await screen.findByText("Messages above this line are no longer sent to the model");
  // The trimmed record says 2: the first turn stays on screen above the line, the last below it.
  expect(line.previousElementSibling.textContent).toContain("First answer.");
  expect(line.nextElementSibling.querySelector(".msg__bubble").textContent).toBe("go on");
});
