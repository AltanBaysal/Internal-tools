import { act, fireEvent, render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import AllProjectsScreen from "./AllProjectsScreen.jsx";

// Madde 353: the screen the app opens on (the design's items 135, 142, 167). The order is the
// server's (Madde 346); the screen only splits it where the pins end.

const HOUR = 3600_000;
const ago = (hours) => new Date(Date.now() - hours * HOUR).toISOString();

const PINNED = {
  id: "p1",
  name: "Harbour at dusk",
  chats: 3,
  files: 2,
  pinned: true,
  lastActivity: ago(2),
};
const RECENT = {
  id: "p2",
  name: "Night market",
  chats: 1,
  files: 1,
  pinned: false,
  lastActivity: ago(5),
};
const OLDER = { id: "p3", name: "Old pier", chats: 0, files: 0, pinned: false, lastActivity: ago(30) };

const labels = (container) =>
  [...container.querySelectorAll(".all-projects__label")].map((label) => label.textContent);
const names = (section) =>
  [...section.querySelectorAll(".all-projects__row-name")].map((name) => name.textContent);

test("the head carries the title and + New project", () => {
  const onNewProject = vi.fn();
  render(<AllProjectsScreen projects={[]} onNewProject={onNewProject} />);
  expect(screen.getByText("All projects", { selector: ".screen__title" })).toBeTruthy();
  const button = screen.getByRole("button", { name: "+ New project" });
  // The app's filled button: the one primary action on this screen.
  expect(button.classList.contains("empty__action")).toBe(true);
  fireEvent.click(button);
  expect(onNewProject).toHaveBeenCalled();
});

test("the pinned stand under Pinned, the rest under Recent, in the server's order", () => {
  const { container } = render(<AllProjectsScreen projects={[PINNED, RECENT, OLDER]} />);
  // Written as the design writes it; the stylesheet turns it to PINNED and RECENT.
  expect(labels(container)).toEqual(["Pinned", "Recent"]);
  const [pinned, recent] = container.querySelectorAll(".all-projects__section");
  expect(names(pinned)).toEqual(["Harbour at dusk"]);
  expect(names(recent)).toEqual(["Night market", "Old pier"]);
});

test("with nothing pinned there is no Pinned section", () => {
  const { container } = render(<AllProjectsScreen projects={[RECENT, OLDER]} />);
  expect(labels(container)).toEqual(["Recent"]);
});

test("a row says how many chats and files, and when it was last used", () => {
  render(<AllProjectsScreen projects={[PINNED, RECENT, OLDER]} />);
  expect(screen.getByText("3 chats · 2 files")).toBeTruthy();
  expect(screen.getByText("2h ago")).toBeTruthy();
  // One of a thing is one, as the delete question counts it.
  expect(screen.getByText("1 chat · 1 file")).toBeTruthy();
  expect(screen.getByText("0 chats · 0 files")).toBeTruthy();
});

test("pressing a row opens that project", () => {
  const onOpenProject = vi.fn();
  render(<AllProjectsScreen projects={[PINNED, RECENT]} onOpenProject={onOpenProject} />);
  // From the start of the name: the row's ⋯ is named after the project too (Madde 360).
  fireEvent.click(screen.getByRole("button", { name: /^Night market/ }));
  expect(onOpenProject).toHaveBeenCalledWith("p2");
});

test("with no projects the screen says so", () => {
  render(<AllProjectsScreen projects={[]} />);
  expect(screen.getByText("No projects yet.")).toBeTruthy();
});

test("while the list loads, the head stands and nothing claims the list is empty", () => {
  // An empty array cannot tell "none" from "not here yet".
  const { container } = render(<AllProjectsScreen projects={[]} loading />);
  expect(screen.getByText("All projects", { selector: ".screen__title" })).toBeTruthy();
  expect(screen.getByRole("button", { name: "+ New project" })).toBeTruthy();
  expect(screen.queryByText("No projects yet.")).toBeNull();
  expect(container.querySelector(".all-projects__row")).toBeNull();
});

// --- Madde 359: the search (the design's items 135, 142, 167) ------------------------------------

const search = () => screen.getByRole("textbox", { name: "Search projects" });
const type = (text) => fireEvent.change(search(), { target: { value: text } });

test("the search stands under the head, named Search projects", () => {
  render(<AllProjectsScreen projects={[PINNED, RECENT]} />);
  const box = search();
  expect(box.getAttribute("placeholder")).toBe("Search projects");
  expect(box.classList.contains("all-projects__search")).toBe(true);
  // The tabs stand in this row too (Madde 363).
  const tools = box.closest(".all-projects__tools");
  expect(tools.previousElementSibling.classList.contains("all-projects__head")).toBe(true);
});

test("the search has the focus when the screen opens", () => {
  render(<AllProjectsScreen projects={[PINNED, RECENT]} />);
  expect(document.activeElement).toBe(search());
});

test("while the list loads the search already stands, and has the focus", () => {
  // Given when the screen opens, not when the list comes: by then the user may be elsewhere.
  render(<AllProjectsScreen projects={[]} loading />);
  expect(document.activeElement).toBe(search());
});

test("typing narrows the list by name, and a section left empty goes", () => {
  const { container } = render(<AllProjectsScreen projects={[PINNED, RECENT, OLDER]} />);
  type("night");
  expect(names(container)).toEqual(["Night market"]);
  expect(labels(container)).toEqual(["Recent"]);
});

test("the search ignores case, accents and the spaces around it", () => {
  const CAFE = { ...OLDER, id: "p4", name: "Café noir" };
  const { container } = render(<AllProjectsScreen projects={[PINNED, RECENT, OLDER, CAFE]} />);
  type("HARBOUR");
  expect(names(container)).toEqual(["Harbour at dusk"]);
  type("cafe");
  expect(names(container)).toEqual(["Café noir"]);
  type("  pier  ");
  expect(names(container)).toEqual(["Old pier"]);
});

test("only the name is searched", () => {
  const { container } = render(<AllProjectsScreen projects={[PINNED, RECENT, OLDER]} />);
  type("chats");
  expect(names(container)).toEqual([]);
  type("2h");
  expect(names(container)).toEqual([]);
});

test("with no match the screen says so, with what was typed", () => {
  const { container } = render(<AllProjectsScreen projects={[PINNED, RECENT]} />);
  type("  zzz ");
  expect(screen.getByText('No projects match "zzz".', { selector: ".all-projects__empty" })).toBeTruthy();
  expect(container.querySelector(".all-projects__row")).toBeNull();
  expect(screen.queryByText("No projects yet.")).toBeNull();
});

test("emptying the box brings the whole list back", () => {
  const { container } = render(<AllProjectsScreen projects={[PINNED, RECENT, OLDER]} />);
  type("zzz");
  type("");
  expect(labels(container)).toEqual(["Pinned", "Recent"]);
  expect(names(container)).toEqual(["Harbour at dusk", "Night market", "Old pier"]);
});

test("with no projects at all a search still says there are none", () => {
  // Not a match that failed: there is nothing to match.
  render(<AllProjectsScreen projects={[]} />);
  type("zzz");
  expect(screen.getByText("No projects yet.")).toBeTruthy();
  expect(screen.queryByText(/No projects match/)).toBeNull();
});

// Madde 360: the menu's open state is App's, whose one listener owns Escape.
test("every row carries its ⋯, and only the row whose menu is open has one", () => {
  const { container } = render(<AllProjectsScreen projects={[PINNED, RECENT]} menuFor="p2" />);
  expect(screen.getByRole("button", { name: "Actions for Harbour at dusk" })).toBeTruthy();
  expect(screen.getByRole("button", { name: "Actions for Night market" })).toBeTruthy();
  const menus = container.querySelectorAll(".menu");
  expect(menus.length).toBe(1);
  expect(menus[0].closest(".all-projects__row").textContent).toContain("Night market");
});

// --- Madde 363: the archive (the design's items 135, 161, 190, 191) ------------------------------

// Where the server lists it: its pin is its own, and it is not pinned, so it stands by its last use.
const SHELVED = {
  id: "p5",
  name: "Shelved reel",
  chats: 2,
  files: 4,
  pinned: false,
  archived: true,
  lastActivity: ago(3),
};
const tab = (name) => screen.getByRole("button", { name: new RegExp(`^${name}\\b`) });
const counts = (container) =>
  [...container.querySelectorAll(".all-projects__count")].map((count) => count.textContent);
const undoRow = (container) => container.querySelector(".all-projects__undo");

test("the tabs stand beside the search, each with its count", () => {
  const { container } = render(<AllProjectsScreen projects={[PINNED, SHELVED, RECENT, OLDER]} />);
  const tabs = container.querySelector(".all-projects__tabs");
  expect(tabs.parentElement.classList.contains("all-projects__tools")).toBe(true);
  expect(tabs.previousElementSibling).toBe(search());
  expect(screen.getByRole("button", { name: "Projects 3" }).className).toContain("all-projects__tab");
  expect(screen.getByRole("button", { name: "Archived 1" }).className).toContain("all-projects__tab");
  expect(counts(container)).toEqual(["3", "1"]);
  // The screen opens on the projects the user is working on.
  expect(tab("Projects").classList.contains("is-on")).toBe(true);
  expect(tab("Archived").classList.contains("is-on")).toBe(false);
});

test("Projects leaves the archived out", () => {
  const { container } = render(<AllProjectsScreen projects={[PINNED, SHELVED, RECENT, OLDER]} />);
  expect(labels(container)).toEqual(["Pinned", "Recent"]);
  expect(names(container)).toEqual(["Harbour at dusk", "Night market", "Old pier"]);
});

test("Archived lists only the archived, in one list with no heading, and none of them opens", () => {
  const { container } = render(<AllProjectsScreen projects={[PINNED, SHELVED, RECENT, OLDER]} />);
  fireEvent.click(tab("Archived"));
  expect(names(container)).toEqual(["Shelved reel"]);
  expect(labels(container)).toEqual([]);
  expect(container.querySelectorAll(".all-projects__list").length).toBe(1);
  expect(container.querySelectorAll(".all-projects__row-text").length).toBe(1);
  expect(container.querySelector(".all-projects__row-open")).toBeNull();
  expect(tab("Archived").classList.contains("is-on")).toBe(true);
  expect(tab("Projects").classList.contains("is-on")).toBe(false);

  fireEvent.click(tab("Projects"));
  expect(names(container)).toEqual(["Harbour at dusk", "Night market", "Old pier"]);
});

test("with nothing archived, Archived says so", () => {
  render(<AllProjectsScreen projects={[PINNED, RECENT]} />);
  fireEvent.click(tab("Archived"));
  expect(screen.getByText("No archived projects.", { selector: ".all-projects__empty" })).toBeTruthy();
});

test("with every project archived, Projects says so and Archived holds them all", () => {
  const { container } = render(
    <AllProjectsScreen
      projects={[
        { ...RECENT, archived: true },
        { ...OLDER, archived: true },
      ]}
    />,
  );
  expect(screen.getByText("Every project is archived.", { selector: ".all-projects__empty" })).toBeTruthy();
  expect(counts(container)).toEqual(["0", "2"]);
  fireEvent.click(tab("Archived"));
  expect(names(container)).toEqual(["Night market", "Old pier"]);
});

test("with no projects at all, both tabs say there are none", () => {
  const { container } = render(<AllProjectsScreen projects={[]} />);
  expect(counts(container)).toEqual(["0", "0"]);
  expect(screen.getByText("No projects yet.")).toBeTruthy();
  fireEvent.click(tab("Archived"));
  expect(screen.getByText("No projects yet.")).toBeTruthy();
  expect(screen.queryByText("No archived projects.")).toBeNull();
});

test("the search narrows the open tab, and stays when the tab changes", () => {
  const { container } = render(
    <AllProjectsScreen projects={[PINNED, SHELVED, RECENT, { ...OLDER, archived: true }]} />,
  );
  fireEvent.click(tab("Archived"));
  type("shelved");
  expect(names(container)).toEqual(["Shelved reel"]);
  type("zzz");
  expect(screen.getByText('No projects match "zzz".', { selector: ".all-projects__empty" })).toBeTruthy();
  expect(screen.queryByText("No archived projects.")).toBeNull();
  fireEvent.click(tab("Projects"));
  expect(search().value).toBe("zzz");
});

test("while the list loads the tabs stand, and count nothing yet", () => {
  // A list that has not come has an unknown count, not a count of none.
  const { container } = render(<AllProjectsScreen projects={[]} loading />);
  expect(tab("Projects")).toBeTruthy();
  expect(tab("Archived")).toBeTruthy();
  expect(counts(container)).toEqual(["", ""]);
});

// The menu is open on the row, as App opens it; Archive then asks App for the change.
function archiving(projects, id, extra = {}) {
  const props = { onCloseMenu: () => {}, onArchiveProject: vi.fn(), ...extra };
  const view = render(<AllProjectsScreen projects={projects} menuFor={id} {...props} />);
  fireEvent.click(screen.getByRole("button", { name: "Archive" }));
  // Once chosen, App closes the menu; the list the server sends back comes as new props.
  const answer = (next) => view.rerender(<AllProjectsScreen projects={next} {...props} />);
  answer(projects);
  return { ...view, props, answer };
}

test("Archive asks nothing, and leaves Undo in the project's place", () => {
  const { container, props } = archiving([PINNED, RECENT, OLDER], "p2");
  expect(props.onArchiveProject).toHaveBeenCalledWith("p2", true);
  // No question: the archive is undone, not confirmed (the design's 135).
  expect(container.querySelector(".dialog")).toBeNull();
  const [, recent] = container.querySelectorAll(".all-projects__section");
  const rows = recent.querySelectorAll(".all-projects__row");
  expect(rows[0].classList.contains("all-projects__undo")).toBe(true);
  expect(rows[0].textContent).toBe("Night market archived · Undo");
  expect(rows[0].querySelector("strong").textContent).toBe("Night market");
  expect(rows[1].textContent).toContain("Old pier");
  // The row the user just acted on keeps the keyboard, on its one action.
  expect(document.activeElement).toBe(screen.getByRole("button", { name: "Undo" }));
});

test("once the server says it is archived, Undo still holds its place and the counts move", () => {
  const { container, answer } = archiving([PINNED, RECENT, OLDER], "p2");
  answer([PINNED, { ...RECENT, archived: true }, OLDER]);
  const [, recent] = container.querySelectorAll(".all-projects__section");
  expect(recent.querySelector(".all-projects__row").textContent).toBe("Night market archived · Undo");
  expect(counts(container)).toEqual(["2", "1"]);
});

test("a pinned project's Undo stands under Pinned, in its place among the pins", () => {
  // Madde 382: the archive lets the pin go, so the server lists the project unpinned -- but still
  // where its pin had it, which is where the design's projectsWithUndo draws the line.
  const SECOND = { id: "p6", name: "Second pin", chats: 0, files: 0, pinned: true, lastActivity: ago(40) };
  const { container, answer } = archiving([PINNED, SECOND, RECENT], "p1");
  answer([{ ...PINNED, pinned: false, archived: true }, SECOND, RECENT]);
  const [pinned] = container.querySelectorAll(".all-projects__section");
  expect(pinned.querySelector(".all-projects__label").textContent).toBe("Pinned");
  const rows = [...pinned.querySelectorAll(".all-projects__row")].map((row) => row.textContent);
  expect(rows).toEqual(["Harbour at dusk archived · Undo", expect.stringContaining("Second pin")]);
});

test("a pinned project's Undo asks for its pin back", () => {
  // The design's restoreProject(id, pinnedAt): the pin the project had when Archive was pressed.
  const { props, answer } = archiving([PINNED, RECENT], "p1", { onRestoreProject: vi.fn() });
  answer([{ ...PINNED, pinned: false, archived: true }, RECENT]);
  fireEvent.click(screen.getByRole("button", { name: "Undo" }));
  expect(props.onRestoreProject).toHaveBeenCalledWith("p1", true);
  expect(props.onArchiveProject.mock.calls).toEqual([["p1", true]]);
});

test("Undo brings it back, and its line holds until the list does", async () => {
  let settle;
  const onRestoreProject = vi.fn(() => new Promise((resolve) => (settle = resolve)));
  const { container, answer } = archiving([PINNED, RECENT, OLDER], "p2", { onRestoreProject });
  answer([PINNED, { ...RECENT, archived: true }, OLDER]);
  fireEvent.click(screen.getByRole("button", { name: "Undo" }));
  expect(onRestoreProject).toHaveBeenCalledWith("p2", false);
  // Let go before the list comes back, the project would vanish for a moment and then return.
  expect(undoRow(container)).toBeTruthy();

  answer([PINNED, RECENT, OLDER]);
  await act(async () => settle());
  expect(undoRow(container)).toBeNull();
  expect(names(container)).toEqual(["Harbour at dusk", "Night market", "Old pier"]);
});

test("opening another row's menu settles the offer", () => {
  const onOpenMenu = vi.fn();
  const { container, answer } = archiving([PINNED, RECENT, OLDER], "p2", { onOpenMenu });
  answer([PINNED, { ...RECENT, archived: true }, OLDER]);
  fireEvent.click(screen.getByRole("button", { name: "Actions for Old pier" }));
  expect(onOpenMenu).toHaveBeenCalledWith("p3");
  expect(undoRow(container)).toBeNull();
  expect(names(container)).toEqual(["Harbour at dusk", "Old pier"]);
});

test("changing the tab settles the offer", () => {
  const { container, answer } = archiving([PINNED, RECENT, OLDER], "p2");
  answer([PINNED, { ...RECENT, archived: true }, OLDER]);
  fireEvent.click(tab("Archived"));
  fireEvent.click(tab("Projects"));
  expect(undoRow(container)).toBeNull();
  expect(names(container)).toEqual(["Harbour at dusk", "Old pier"]);
});

test("Unarchive asks for the project back, and leaves no Undo", () => {
  const onArchiveProject = vi.fn();
  const { container } = render(
    <AllProjectsScreen
      projects={[PINNED, SHELVED]}
      menuFor="p5"
      onCloseMenu={() => {}}
      onArchiveProject={onArchiveProject}
    />,
  );
  fireEvent.click(tab("Archived"));
  fireEvent.click(screen.getByRole("button", { name: "Unarchive" }));
  expect(onArchiveProject).toHaveBeenCalledWith("p5", false);
  expect(undoRow(container)).toBeNull();
});

// --- Madde 364: while the list loads, and when it cannot be read (the design's 172, 173) ---------

// jsdom ships no clipboard, so the test supplies one and watches what it is handed.
function stubClipboard(answer) {
  const writeText = vi.fn(() => answer);
  Object.defineProperty(navigator, "clipboard", { value: { writeText }, configurable: true });
  return writeText;
}

// What failure.js makes of a Flask 500 page: the code and the body, as they came.
const RAW = "HTTP 500: <!doctype html>\n<title>500 Internal Server Error</title>";

test("while the list loads a spinner turns where the list will be", () => {
  // The head, + New project and the search stand as they will once the list is real; only the
  // list's own place waits (the design's 173).
  const { container } = render(<AllProjectsScreen projects={[]} loading />);
  const spot = container.querySelector(".all-projects__tools").nextElementSibling;
  expect(spot.className).toBe("all-projects__spinner");
  expect(spot.querySelector("[data-testid=spinner]")).toBeTruthy();
});

test("a list that could not be read says so in one sentence, and nothing else stands", () => {
  // A failed list means the count is unknown, not zero. The raw words are Copy's, not the
  // screen's: one plain sentence (the design's 172).
  const { container } = render(<AllProjectsScreen projects={[]} error={RAW} />);
  expect(container.querySelector(".empty > .empty__error").textContent).toBe(
    "Couldn't load projects.",
  );
  expect(screen.queryByText(/HTTP 500/)).toBeNull();
  expect(screen.queryByText("All projects")).toBeNull();
  expect(screen.queryByRole("textbox", { name: "Search projects" })).toBeNull();
  expect(screen.queryByText("No projects yet.")).toBeNull();
});

test("under the sentence stand Try again and Copy, and Try again asks for the list again", () => {
  const onRetry = vi.fn();
  const { container } = render(<AllProjectsScreen projects={[]} error={RAW} onRetry={onRetry} />);
  const buttons = [...container.querySelectorAll(".empty > .empty__actions > button")];
  expect(buttons.map((one) => one.textContent)).toEqual(["Try again", "Copy"]);
  // Brown as every failure's Try again is; Copy is the framed button the file's header carries.
  expect(buttons[0].className).toBe("failure__retry");
  expect(buttons[1].className).toBe("ghost empty__copy");
  fireEvent.click(buttons[0]);
  expect(onRetry).toHaveBeenCalled();
});

test("Copy puts the error on the clipboard exactly as it came, and says it landed", async () => {
  // Pasted elsewhere, it still shows the real error.
  const writeText = stubClipboard(Promise.resolve());
  render(<AllProjectsScreen projects={[]} error={RAW} />);
  fireEvent.click(screen.getByRole("button", { name: "Copy" }));
  expect(writeText).toHaveBeenCalledWith(RAW);
  expect(await screen.findByRole("button", { name: "Copied" })).toBeTruthy();
});

test("a copy that did not land says so in Copy's place", async () => {
  stubClipboard(Promise.reject(new Error("denied")));
  render(<AllProjectsScreen projects={[]} error={RAW} />);
  fireEvent.click(screen.getByRole("button", { name: "Copy" }));
  expect(await screen.findByRole("button", { name: "Could not copy" })).toBeTruthy();
});

test("while Try again reads the list, the frame and its spinner stand again", () => {
  // The wait is a wait whatever came before it (the design's 173: Try again shows it too).
  const { container } = render(<AllProjectsScreen projects={[]} loading error={RAW} />);
  expect(screen.getByText("All projects", { selector: ".screen__title" })).toBeTruthy();
  expect(container.querySelector(".all-projects__spinner")).toBeTruthy();
  expect(screen.queryByText("Couldn't load projects.")).toBeNull();
});

test("a write the server refused leaves the list standing, with the server's words over it", () => {
  // A rename that did not land says nothing about the list, which is still known.
  const { container } = render(
    <AllProjectsScreen projects={[PINNED, RECENT]} writeError="the store is unreachable" />,
  );
  const line = screen.getByText("the store is unreachable");
  expect(line.className).toBe("list-error");
  expect(line.previousElementSibling.className).toBe("all-projects__tools");
  expect(names(container)).toEqual(["Harbour at dusk", "Night market"]);
  expect(screen.queryByText("Couldn't load projects.")).toBeNull();
});
