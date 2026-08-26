import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";

import App from "./App.jsx";

afterEach(() => {
  vi.unstubAllGlobals();
  // jsdom shares one document across tests, so a pushed address has to be put back.
  window.history.pushState(null, "", "/");
  Object.defineProperty(window.navigator, "onLine", { value: true, configurable: true });
});

const PROJECT = { id: "p1", name: "Old", chats: 0, files: 0 };
// The fork lands on the first project, so a test about where the fork did NOT send the user needs
// a second one -- going to the first would read the same either way.
const PROJECT_2 = { id: "p2", name: "Newer", chats: 0, files: 0 };

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

test("the first load is one skeleton and no screen at all", async () => {
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
  expect(screen.getByTestId("skeleton")).toBeTruthy();
  // The navigation stays usable while the middle waits.
  expect(screen.getByText("QueenAgent")).toBeTruthy();
  expect(screen.queryByText(/No projects yet/)).toBeNull();

  await act(async () => {
    answer();
  });
  await waitFor(() => expect(screen.queryByTestId("skeleton")).toBeNull());
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

test("the fork asks the browser where we are, not the render it was built from", async () => {
  // Madde 52, and the hazard behind finding 15. A React effect carries the values of the commit that
  // scheduled it, so a list arriving in the same batch as a move can fire a fork that was decided
  // for an address the user has already left. Here the address moves without React being told --
  // which is exactly the stale commit, made deterministic.
  //
  // This was one of a pair. Its sibling moved through the app instead of behind its back, and its
  // only way to do that before the list arrived was the Settings row -- gone with Madde 62, and
  // nothing else at the fork navigates. Nothing is lost: an in-app move updates the address React
  // holds, so the fork's own dependency turns null and the effect never runs at all. This test is
  // the harder half, where the effect does run and has to decline.
  window.history.pushState(null, "", "/");
  let answer;
  vi.stubGlobal(
    "fetch",
    vi.fn().mockReturnValue(
      new Promise((resolve) => {
        answer = () => resolve({ ok: true, status: 200, json: async () => [PROJECT, PROJECT_2] });
      }),
    ),
  );
  render(<App />);

  window.history.pushState(null, "", "/p/p2");
  await act(async () => {
    answer();
  });
  expect(window.location.pathname).toBe("/p/p2");
});

test("/settings is an address like any other unknown one: the fork lands it on the project", async () => {
  // Madde 62's trap. Deleting the route alone would leave the address parsing to the fork while the
  // fork's own guard still asked for a literal "/" -- no redirect, no screen, a blank page. The two
  // pieces are each correct on their own and open a hole together.
  stubProjects([PROJECT]);
  window.history.pushState(null, "", "/settings");
  render(<App />);

  // PROJECT is the one the fork lands on, and it is called Old.
  await screen.findByText("Old", { selector: ".screen__title" });
  expect(window.location.pathname).toBe("/p/p1");
});

test("the app never asks the server for settings", async () => {
  // There is no endpoint left to ask. Said as a test because the call was made on mount, before any
  // screen was drawn -- so nothing on screen would have shown it was still happening.
  const fetch = stubProjects([PROJECT]);
  render(<App />);

  // Any drawn screen will do -- the claim is about a call made on mount.
  await screen.findByText("Old", { selector: ".screen__title" });
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

test("the app opens on the first project's screen", async () => {
  // "/" is a fork, not a screen: with a project to show, the app lands on it. Madde 65 sent the
  // landing to the draft chat instead, because the project screen carried no picker -- Madde 77 put
  // the pickers here and gave the landing back.
  stubProjects([{ id: "p1", name: "Thesis", chats: 0, files: 0 }]);
  render(<App />);
  await waitFor(() => expect(window.location.pathname).toBe("/p/p1"));
  // The sidebar row reads the project list, so the name stands there whichever screen is open.
  expect(screen.getByText("Thesis", { selector: ".sidebar__row-name" })).toBeTruthy();
  // Named by what is drawn rather than by what is missing: the project screen carries the project's
  // title, and the draft's own title is the thing that must not be here.
  expect(screen.getByText("Thesis", { selector: ".screen__title" })).toBeTruthy();
  expect(screen.queryByText("New chat", { selector: ".chat__title" })).toBeNull();
});

test("a skill can be picked before anything is typed", async () => {
  // The item's whole point, and the question Madde 65 answered in the wrong place. The landing has
  // to carry the picker; only pressing it proves that it does.
  stubProjects([{ id: "p1", name: "Thesis", chats: 0, files: 0 }]);
  render(<App />);
  await waitFor(() => expect(window.location.pathname).toBe("/p/p1"));

  fireEvent.click(screen.getByRole("button", { name: /Skills/ }));
  fireEvent.click(screen.getByText("Create scenario", { selector: ".menu__item-name" }));

  // No chat exists yet, so the choice is held for the one that will be born -- what the screen owes
  // is that the button now says what was picked.
  await waitFor(() =>
    expect(screen.getByText("Create scenario", { selector: ".picker__name" })).toBeTruthy(),
  );
});

test("the skill picked on the project screen is what the chat is born with", async () => {
  // The half that separates a label from a behaviour. Without it, a picker that changes its own
  // caption and nothing else reads exactly like a working one.
  const born = { id: "c9", title: "Write it", messages: [] };
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (String(path).endsWith("/messages") && options?.method === "POST") {
      return Promise.resolve({ ok: true, status: 201, json: async () => born });
    }
    // The chat the app moves to once it exists. Answering with a list here would hand the screen
    // something shaped like nothing it can draw, and the test would pass over a console full of
    // crashes.
    if (String(path).endsWith("/chats/c9")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => born });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [] });
  });
  vi.stubGlobal("fetch", vi.fn().mockResolvedValueOnce({
    ok: true,
    status: 200,
    json: async () => [{ id: "p1", name: "Thesis", chats: 0, files: 0 }],
  }).mockImplementation(fetch));
  render(<App />);
  await waitFor(() => expect(window.location.pathname).toBe("/p/p1"));

  fireEvent.click(screen.getByRole("button", { name: /Skills/ }));
  fireEvent.click(screen.getByText("Create scenario", { selector: ".menu__item-name" }));
  fireEvent.change(screen.getByPlaceholderText("Start a new chat in this project..."), {
    target: { value: "Write it" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Start" }));

  await waitFor(() => {
    const started = fetch.mock.calls.find(
      ([path, options]) => String(path).endsWith("/messages") && options?.method === "POST",
    );
    expect(started).toBeTruthy();
    expect(JSON.parse(started[1].body).skill).toBe("create-scenario");
  });
});

test("the draft chat is still reached from the sidebar", async () => {
  // The item's cost, the other way round from Madde 65. Now that the project screen is the landing,
  // "the landing moved back" and "the draft chat is gone" would be the same green without this.
  stubProjects([{ id: "p1", name: "Thesis", chats: 0, files: 0 }]);
  render(<App />);
  await waitFor(() => expect(window.location.pathname).toBe("/p/p1"));

  // The button wears a + before its words, so it is asked for by what it contains.
  fireEvent.click(screen.getByRole("button", { name: /New chat/ }));

  await waitFor(() => expect(window.location.pathname).toBe("/p/p1/c/new"));
  expect(screen.getByText("New chat", { selector: ".chat__title" })).toBeTruthy();
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

// Every test below opens at a project's own address rather than letting the fork place it. The fork
// lands on the project screen again since Madde 77, so waiting for it would work -- and would only
// be testing the landing a ninth time. Pushing the address says what these tests are about.

test("the sidebar menu and the header open the same question", async () => {
  serverWith(TWO);
  window.history.pushState(null, "", "/p/p1");
  render(<App />);
  await screen.findByText("Thesis", { selector: ".screen__title" });

  openMenuFor("Thesis");
  fireEvent.click(screen.getByRole("button", { name: "Delete project" }));
  expect(screen.getByText('Delete "Thesis"?')).toBeTruthy();
  fireEvent.click(screen.getByRole("button", { name: "Cancel" }));

  fireEvent.click(screen.getByRole("button", { name: "Delete" }));
  expect(screen.getByText('Delete "Thesis"?')).toBeTruthy();
});

test("the box counts what goes with the project", async () => {
  serverWith(TWO);
  window.history.pushState(null, "", "/p/p1");
  render(<App />);
  await screen.findByText("Thesis", { selector: ".screen__title" });
  openMenuFor("Thesis");
  fireEvent.click(screen.getByRole("button", { name: "Delete project" }));
  expect(
    screen.getByText("The 3 chats and 2 files in this project are deleted with it. This can't be undone."),
  ).toBeTruthy();
});

test("one of a thing is one, not one of them", async () => {
  serverWith(TWO);
  window.history.pushState(null, "", "/p/p1");
  render(<App />);
  await screen.findByText("Thesis", { selector: ".screen__title" });
  openMenuFor("Notes");
  fireEvent.click(screen.getByRole("button", { name: "Delete project" }));
  expect(screen.getByText(/The 1 chat and 0 files/)).toBeTruthy();
});

test("cancelling asks the server nothing", async () => {
  const fetch = serverWith(TWO);
  window.history.pushState(null, "", "/p/p1");
  render(<App />);
  await screen.findByText("Thesis", { selector: ".screen__title" });
  openMenuFor("Thesis");
  fireEvent.click(screen.getByRole("button", { name: "Delete project" }));
  fireEvent.click(screen.getByRole("button", { name: "Cancel" }));
  expect(fetch.mock.calls.filter(([, options]) => options?.method === "DELETE")).toEqual([]);
  expect(screen.queryByText('Delete "Thesis"?')).toBeNull();
});

test("deleting the project you are in moves to the first one left", async () => {
  serverWith(TWO);
  window.history.pushState(null, "", "/p/p1");
  render(<App />);
  await screen.findByText("Thesis", { selector: ".screen__title" });
  openMenuFor("Thesis");
  fireEvent.click(screen.getByRole("button", { name: "Delete project" }));
  fireEvent.click(screen.getByRole("button", { name: "Delete project" }));
  await waitFor(() => expect(window.location.pathname).toBe("/p/p2"));
  expect(screen.queryByText("Thesis")).toBeNull();
});

test("deleting the last project leaves the empty screen", async () => {
  serverWith([TWO[0]]);
  window.history.pushState(null, "", "/p/p1");
  render(<App />);
  await screen.findByText("Thesis", { selector: ".screen__title" });
  openMenuFor("Thesis");
  fireEvent.click(screen.getByRole("button", { name: "Delete project" }));
  fireEvent.click(screen.getByRole("button", { name: "Delete project" }));
  await waitFor(() => expect(screen.getByText("No projects yet")).toBeTruthy());
});

test("deleting another project leaves where you are alone", async () => {
  serverWith(TWO);
  window.history.pushState(null, "", "/p/p1");
  render(<App />);
  await screen.findByText("Thesis", { selector: ".screen__title" });
  openMenuFor("Notes");
  fireEvent.click(screen.getByRole("button", { name: "Delete project" }));
  fireEvent.click(screen.getByRole("button", { name: "Delete project" }));
  await waitFor(() => expect(screen.queryByText("Notes")).toBeNull());
  // Nothing about the screen the user was on has any business changing.
  expect(window.location.pathname).toBe("/p/p1");
});

test("a deleted project is not offered back", async () => {
  serverWith(TWO);
  window.history.pushState(null, "", "/p/p1");
  render(<App />);
  await screen.findByText("Thesis", { selector: ".screen__title" });
  openMenuFor("Notes");
  fireEvent.click(screen.getByRole("button", { name: "Delete project" }));
  fireEvent.click(screen.getByRole("button", { name: "Delete project" }));
  await waitFor(() => expect(screen.queryByText("Notes")).toBeNull());
  // Undo is gone by karar 16: the question was the protection, and the disk keeps the directory.
  expect(screen.queryByText("Undo")).toBeNull();
});

test("Escape closes the menu first, then the question", async () => {
  serverWith(TWO);
  window.history.pushState(null, "", "/p/p1");
  const { container } = render(<App />);
  await screen.findByText("Thesis", { selector: ".screen__title" });

  openMenuFor("Thesis");
  expect(container.querySelector(".menu")).toBeTruthy();
  fireEvent.keyDown(window, { key: "Escape" });
  // Asked for by shape rather than by name: the project header carries a Rename of its own.
  expect(container.querySelector(".menu")).toBeNull();

  openMenuFor("Thesis");
  fireEvent.click(screen.getByRole("button", { name: "Delete project" }));
  fireEvent.keyDown(window, { key: "Escape" });
  expect(screen.queryByText('Delete "Thesis"?')).toBeNull();
});

test("no screen is drawn while the list is still on its way", () => {
  // An empty array cannot tell "none" from "not here yet", and guessing shows the wrong screen.
  vi.stubGlobal("fetch", vi.fn().mockReturnValue(new Promise(() => {})));
  render(<App />);
  expect(screen.queryByText("No projects yet")).toBeNull();
  expect(screen.queryByRole("button", { name: "Rename" })).toBeNull();
  // Madde 34 moved this line: the area used to sit empty, which said nothing about why. It now
  // carries the skeleton, and still no screen.
  expect(screen.getByTestId("skeleton")).toBeTruthy();
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
  const box = await screen.findByPlaceholderText("Reply...");
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
  const box = await screen.findByPlaceholderText("Reply...");
  fireEvent.change(box, { target: { value: "hello" } });
  fireEvent.keyDown(box, { key: "Enter" });

  await waitFor(() => expect(screen.getByText("Done.")).toBeTruthy());
  expect(fetch.mock.calls.filter(([, options]) => options?.method === "POST")).toHaveLength(1);
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
  const box = await screen.findByPlaceholderText("Reply...");
  fireEvent.change(box, { target: { value: "write the outline" } });
  fireEvent.keyDown(box, { key: "Enter" });
  await waitFor(() => expect(screen.getByTestId("file-rail").textContent).toContain("outline.md"));
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
  const box = await screen.findByPlaceholderText("Reply...");
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
  const box = await screen.findByPlaceholderText("Reply...");
  fireEvent.change(box, { target: { value: "hello" } });
  fireEvent.keyDown(box, { key: "Enter" });

  await waitFor(() => expect(screen.getByText(/HTTP 502/)).toBeTruthy());
  // Asking again is the user's to do. A broken engine used to become an endless retry here.
  expect(fetch.mock.calls.filter(([, options]) => options?.method === "POST")).toHaveLength(1);
});

// The app speaks one deletion language now: ask, then delete. The browser's box is gone from it.
function withChats(chats) {
  const live = [...chats];
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (options?.method === "DELETE") {
      live.length = 0;
      return Promise.resolve({ ok: true, status: 200, json: async () => ({}) });
    }
    if (path === "/api/projects/p1/chats") {
      return Promise.resolve({ ok: true, status: 200, json: async () => [...live] });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [PROJECT] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1");
  return fetch;
}

const CHAT_ROW = [{ id: "c1", title: "Write the intro", lastActivity: new Date().toISOString() }];

test("deleting a chat asks in the app's own box, not the browser's", async () => {
  const fetch = withChats(CHAT_ROW);
  vi.stubGlobal("confirm", vi.fn());
  render(<App />);
  // Asked for by its control: the title itself now stands twice, in the row and in the sidebar.
  await waitFor(() =>
    expect(screen.getByRole("button", { name: "Delete Write the intro" })).toBeTruthy(),
  );
  fireEvent.click(screen.getByRole("button", { name: "Delete Write the intro" }));

  expect(screen.getByText("Delete this chat?")).toBeTruthy();
  expect(screen.getByText("Its files stay in the project.")).toBeTruthy();
  expect(window.confirm).not.toHaveBeenCalled();
  expect(fetch.mock.calls.every(([, options]) => options?.method !== "DELETE")).toBe(true);
});

test("cancelling a chat deletion sends nothing", async () => {
  const fetch = withChats(CHAT_ROW);
  render(<App />);
  await waitFor(() =>
    expect(screen.getByRole("button", { name: "Delete Write the intro" })).toBeTruthy(),
  );
  fireEvent.click(screen.getByRole("button", { name: "Delete Write the intro" }));
  fireEvent.click(screen.getByRole("button", { name: "Cancel" }));
  expect(fetch.mock.calls.every(([, options]) => options?.method !== "DELETE")).toBe(true);
});

test("a chat the user confirms is deleted and leaves the list", async () => {
  withChats(CHAT_ROW);
  render(<App />);
  await waitFor(() => expect(screen.getAllByText("Write the intro").length).toBeGreaterThan(0));
  fireEvent.click(screen.getByRole("button", { name: "Delete Write the intro" }));
  fireEvent.click(screen.getByRole("button", { name: "Delete chat" }));
  await waitFor(() => expect(screen.queryByText("Write the intro")).toBeNull());
});

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
    return Promise.resolve({ ok: true, status: 200, json: async () => [PROJECT] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1");
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
  // The delete lives on the row, and the row lives in the column the panel replaced. So reading a
  // file is not a state a file can be deleted from -- on either screen.
  withFile();
  render(<App />);
  await waitFor(() => expect(screen.getByText("plan.md")).toBeTruthy());
  fireEvent.click(screen.getByText("plan.md"));
  await waitFor(() => expect(screen.getByText("body")).toBeTruthy());

  expect(screen.queryByRole("button", { name: "Delete plan.md" })).toBeNull();
  fireEvent.click(screen.getByRole("button", { name: "×" }));
  await waitFor(() => expect(screen.getByRole("button", { name: "Delete plan.md" })).toBeTruthy());
});

test("a file is not deleted until the question is answered", async () => {
  const file = { name: "plan.md", ext: "md", modifiedAt: new Date().toISOString() };
  const fetch = vi.fn().mockImplementation((path) => {
    if (path.endsWith("/files")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => [file] });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [PROJECT] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1");

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
  await waitFor(() => expect(screen.getByText("Projects")).toBeTruthy());

  fireEvent.click(screen.getByRole("button", { name: "Hide the sidebar" }));
  await waitFor(() => expect(screen.queryByText("Projects")).toBeNull());

  fireEvent.click(screen.getByRole("button", { name: "← Old" }));
  await waitFor(() => expect(window.location.pathname).toBe("/p/p1"));
  expect(screen.queryByText("Projects")).toBeNull();

  fireEvent.click(screen.getByRole("button", { name: "Show the sidebar" }));
  await waitFor(() => expect(screen.getByText("Projects")).toBeTruthy());
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

test("opening a file unfolds the rail rather than hiding what was opened", async () => {
  // A file can be opened from the project screen while the chat's rail is folded, and closing it
  // must not drop the reader back into a folded rail.
  withRail();
  window.history.pushState(null, "", "/p/p1/c/c1");
  render(<App />);
  await waitFor(() => expect(screen.getByText("plan.md")).toBeTruthy());
  fold();
  await waitFor(() => expect(screen.queryByText("plan.md")).toBeNull());

  fireEvent.click(screen.getByRole("button", { name: "← Old" }));
  await waitFor(() => expect(window.location.pathname).toBe("/p/p1"));
  fireEvent.click(screen.getByText("plan.md"));
  await waitFor(() => expect(screen.getByText("body")).toBeTruthy());

  fireEvent.click(screen.getByRole("button", { name: "Write the intro" }));
  await waitFor(() => expect(window.location.pathname).toBe("/p/p1/c/c1"));
  fireEvent.click(screen.getByRole("button", { name: "←" }));
  // Folded, this list would not be here.
  await waitFor(() => expect(screen.getByText("plan.md")).toBeTruthy());
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

// --- one model, and nothing asks about it (Madde 82) ---------------------------------------------

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
function withStoredSkill(stored = "verify-prompts") {
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
  // The setting has one value and the wiring names it once, in config.py. There is nothing for the
  // browser to fetch and nothing for it to hold.
  const fetch = withChat();
  window.history.pushState(null, "", "/p/p1/c/c1");
  render(<App />);
  await waitFor(() => expect(screen.getByText("Grok Build")).toBeTruthy());
  expect(fetch.mock.calls.filter(([path]) => String(path) === "/api/model")).toHaveLength(0);
});

test("a chat is born without a model", async () => {
  // Nothing to send: there is one, and the server already knows which.
  const fetch = withChat();
  window.history.pushState(null, "", "/p/p1");
  render(<App />);
  const box = await screen.findByPlaceholderText("Start a new chat in this project...");
  fireEvent.change(box, { target: { value: "hello" } });
  fireEvent.keyDown(box, { key: "Enter" });

  await waitFor(() => {
    const born = fetch.mock.calls.find(
      ([path, options]) => options?.method === "POST" && String(path).endsWith("/messages"),
    );
    expect(born).toBeTruthy();
    expect(JSON.parse(born[1].body)).not.toHaveProperty("model");
  });
});

// --- which skill is selected ---------------------------------------------------------------------

test("picking a skill asks the server for nothing", async () => {
  // Madde 86: there is no field to write, so there is no request. The choice is the session's.
  const fetch = withStoredSkill("");
  window.history.pushState(null, "", "/p/p1/c/c1");
  render(<App />);
  await waitFor(() => expect(screen.getByRole("button", { name: /Skills/ })).toBeTruthy());

  fireEvent.click(screen.getByRole("button", { name: /Skills/ }));
  fireEvent.click(screen.getByText("Verify prompts"));

  await waitFor(() => expect(screen.getByRole("button", { name: /Verify prompts/ })).toBeTruthy());
  expect(fetch.mock.calls.filter(([, options]) => options?.method === "PATCH")).toHaveLength(0);
});

test("a chat that stored a skill does not put it in the picker", async () => {
  // Opening an old chat says nothing about what this session picked -- and this session picked
  // nothing yet, so the picker is where it started.
  withStoredSkill();
  window.history.pushState(null, "", "/p/p1/c/c1");
  render(<App />);
  await waitFor(() => expect(screen.getByRole("button", { name: /Skills/ })).toBeTruthy());
  expect(screen.queryByRole("button", { name: /Verify prompts/ })).toBeNull();
});

test("what the picker shows is what the message carries", async () => {
  // The bug Madde 86 closes: the picker read the record, the send read the session, and a chat
  // opened after a reload made the two say different things at the same moment.
  const fetch = withStoredSkill();
  window.history.pushState(null, "", "/p/p1/c/c1");
  render(<App />);
  const box = await screen.findByPlaceholderText("Reply...");
  fireEvent.change(box, { target: { value: "more" } });
  fireEvent.keyDown(box, { key: "Enter" });

  await waitFor(() => {
    const sent = fetch.mock.calls.find(
      ([path, options]) => String(path).endsWith("/messages") && options?.method === "POST",
    );
    expect(sent).toBeTruthy();
    expect(JSON.parse(sent[1].body).skill).toBe("");
  });
  expect(screen.queryByRole("button", { name: /Verify prompts/ })).toBeNull();
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
  window.history.pushState(null, "", "/p/p1");

  render(<App />);
  const box = await screen.findByPlaceholderText("Start a new chat in this project...");
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
  const box = await screen.findByPlaceholderText("Reply...");
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
  const box = await screen.findByPlaceholderText("Reply...");
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
  const box = await screen.findByPlaceholderText("Reply...");
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
  const box = await screen.findByPlaceholderText("Reply...");
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
  const box = await screen.findByPlaceholderText("Reply...");
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
  const box = await screen.findByPlaceholderText("Reply...");
  fireEvent.change(box, { target: { value: "hello" } });
  fireEvent.keyDown(box, { key: "Enter" });

  // The read's own sentence, not a guess about what went wrong.
  await waitFor(() => expect(screen.getByText("the disk went away")).toBeTruthy());
});

test("the skill picked in a draft survives landing in the chat it created", async () => {
  // The accepted cost, written down: the choice belongs to the session, so it crosses into the
  // chat that was just born even though that chat's record says otherwise.
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
  await waitFor(() => expect(screen.getByRole("button", { name: /Skills/ })).toBeTruthy());
  fireEvent.click(screen.getByRole("button", { name: /Skills/ }));
  fireEvent.click(screen.getByText("Split into frames", { selector: ".menu__item-name" }));

  const box = screen.getByPlaceholderText("Reply...");
  fireEvent.change(box, { target: { value: "Write it" } });
  fireEvent.keyDown(box, { key: "Enter" });

  await waitFor(() => expect(window.location.pathname).toBe("/p/p1/c/c1"));
  expect(screen.getByRole("button", { name: /Split into frames/ })).toBeTruthy();
});

test("a new chat is born with the last skill picked in this session", async () => {
  const fetch = withChat();
  window.history.pushState(null, "", "/p/p1/c/c1");
  render(<App />);
  await waitFor(() => expect(screen.getByRole("button", { name: /Skills/ })).toBeTruthy());
  fireEvent.click(screen.getByRole("button", { name: /Skills/ }));
  fireEvent.click(screen.getByText("Split into frames"));
  await waitFor(() => expect(screen.getByRole("button", { name: /Split into frames/ })).toBeTruthy());

  fireEvent.click(screen.getByRole("button", { name: "← Old" }));
  await waitFor(() => expect(window.location.pathname).toBe("/p/p1"));
  const box = screen.getByPlaceholderText("Start a new chat in this project...");
  fireEvent.change(box, { target: { value: "hello" } });
  fireEvent.keyDown(box, { key: "Enter" });

  await waitFor(() =>
    expect(
      fetch.mock.calls.some(
        ([path, options]) =>
          options?.method === "POST" &&
          path.endsWith("/messages") &&
          JSON.parse(options.body).skill === "split-into-frames",
      ),
    ).toBe(true),
  );
});

test("picking a skill closes the menu", async () => {
  // Closing was written twice -- once in Menu, once in App -- and the two landed in the same batch,
  // so the toggle re-opened what the other had just closed.
  withChat();
  window.history.pushState(null, "", "/p/p1/c/c1");
  render(<App />);
  await waitFor(() => expect(screen.getByRole("button", { name: /Skills/ })).toBeTruthy());

  fireEvent.click(screen.getByRole("button", { name: /Skills/ }));
  fireEvent.click(screen.getByText("Create scenario", { selector: ".menu__item-name" }));
  await waitFor(() => expect(screen.queryByText("SKILLS")).toBeNull());
});

test("in a draft, picking a skill closes the menu too", async () => {
  // A draft has no chat to write to, so it takes a different path out of the same menu.
  withChat();
  window.history.pushState(null, "", "/p/p1/c/new");
  render(<App />);
  await waitFor(() => expect(screen.getByRole("button", { name: /Skills/ })).toBeTruthy());

  fireEvent.click(screen.getByRole("button", { name: /Skills/ }));
  fireEvent.click(screen.getByText("Create scenario", { selector: ".menu__item-name" }));
  await waitFor(() => expect(screen.queryByText("SKILLS")).toBeNull());
});

test("Escape closes the picker", async () => {
  // fark 67 put five things in order: project menu -> confirm box -> Skills -> model -> open panel.
  // Madde 82 took the model out and the order is four; the ones around it did not move.
  withChat();
  window.history.pushState(null, "", "/p/p1/c/c1");
  render(<App />);
  await waitFor(() => expect(screen.getByRole("button", { name: /Skills/ })).toBeTruthy());

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
  await waitFor(() =>
    expect(screen.getByText("Edit", { selector: ".picker__name" })).toBeTruthy(),
  );

  fireEvent.click(screen.getByText("Edit", { selector: ".picker__name" }));
  fireEvent.click(screen.getByText("Ask", { selector: ".menu__item-name" }));
  const box = screen.getByPlaceholderText("Reply...");
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
  await waitFor(() => expect(screen.getByRole("button", { name: /Skills/ })).toBeTruthy());

  fireEvent.click(screen.getByRole("button", { name: /Skills/ }));
  expect(screen.getByText("SKILLS")).toBeTruthy();
  fireEvent.click(screen.getByText("Edit", { selector: ".picker__name" }));
  expect(screen.queryByText("SKILLS")).toBeNull();
  expect(screen.getByText("MODE")).toBeTruthy();
});

test("Escape closes the mode picker too", async () => {
  // The order fark 67 settled had two pickers in it and lost one in Madde 82. A second picker is
  // back, so the same key has to reach it.
  withChat();
  window.history.pushState(null, "", "/p/p1/c/c1");
  render(<App />);
  await waitFor(() =>
    expect(screen.getByText("Edit", { selector: ".picker__name" })).toBeTruthy(),
  );

  fireEvent.click(screen.getByText("Edit", { selector: ".picker__name" }));
  expect(screen.getByText("MODE")).toBeTruthy();
  fireEvent.keyDown(window, { key: "Escape" });
  expect(screen.queryByText("MODE")).toBeNull();
});

test("a draft says which model will answer it", async () => {
  // Nothing has been sent yet and there is still one model, so the name is there from the start.
  withChat();
  window.history.pushState(null, "", "/p/p1/c/new");
  render(<App />);
  await waitFor(() => expect(screen.getByText("Grok Build")).toBeTruthy());
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
