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

test("Archived lists only the archived, in one list with no heading", () => {
  const { container } = render(<AllProjectsScreen projects={[PINNED, SHELVED, RECENT, OLDER]} />);
  fireEvent.click(tab("Archived"));
  expect(names(container)).toEqual(["Shelved reel"]);
  expect(labels(container)).toEqual([]);
  expect(container.querySelectorAll(".all-projects__list").length).toBe(1);
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

// --- Madde 441: Archive takes the row out at once (the design's 217) -----------------------------

// The screen as App draws it. `archive` and `unarchive` press a row's Archive or Unarchive from its
// ⋯, which App opens and, once chosen, closes; Unarchive is on the Archived tab. The server takes
// its time (Madde 446), so each answer waits for `answer`, in the order pressed, as editProject
// sends them (Madde 450): the list it reads again, then the hand-back.
function onScreen(projects, extra = {}) {
  const answers = [];
  const onArchiveProject = vi.fn(() => new Promise((resolve) => answers.push(resolve)));
  const props = { onCloseMenu: () => {}, onArchiveProject, ...extra };
  let listed = projects;
  const view = render(<AllProjectsScreen projects={listed} {...props} />);
  const press = (id, label) => {
    view.rerender(<AllProjectsScreen projects={listed} menuFor={id} {...props} />);
    fireEvent.click(screen.getByRole("button", { name: label }));
    view.rerender(<AllProjectsScreen projects={listed} {...props} />);
  };
  const archive = (id) => press(id, "Archive");
  const unarchive = (id) => press(id, "Unarchive");
  const answer = async (next) => {
    listed = next;
    view.rerender(<AllProjectsScreen projects={listed} {...props} />);
    await act(async () => answers.shift()());
  };
  return { ...view, props, archive, unarchive, answer };
}
const moreOf = (name) => screen.getByRole("button", { name: `Actions for ${name}` });

test("Archive asks nothing, and the project leaves Projects for Archived before the server answers", () => {
  const { container, props, archive } = onScreen([PINNED, RECENT, OLDER]);
  archive("p2");
  expect(props.onArchiveProject).toHaveBeenCalledWith("p2", true);
  expect(container.querySelector(".dialog")).toBeNull();
  // Nothing is drawn in its place: no Undo, anywhere.
  expect(names(container)).toEqual(["Harbour at dusk", "Old pier"]);
  expect(screen.queryByText(/Undo/)).toBeNull();
  expect(counts(container)).toEqual(["2", "1"]);
  fireEvent.click(tab("Archived"));
  expect(names(container)).toEqual(["Night market"]);
});

test("the keyboard goes to the ⋯ of the row that now stands where it stood", () => {
  const { archive } = onScreen([PINNED, RECENT, OLDER]);
  const focus = vi.spyOn(moreOf("Old pier"), "focus");
  archive("p2");
  expect(document.activeElement).toBe(moreOf("Old pier"));
  // It moves into the place being looked at, so the window stays where it is.
  expect(focus).toHaveBeenCalledWith({ preventScroll: true });
});

test("from the last pinned row the keyboard goes on to the first recent one", () => {
  const { archive } = onScreen([PINNED, RECENT, OLDER]);
  archive("p1");
  expect(document.activeElement).toBe(moreOf("Night market"));
});

test("searched, the keyboard goes to the next row the search left", () => {
  const OWL = { ...OLDER, id: "p4", name: "Night owl", lastActivity: ago(50) };
  const { archive } = onScreen([PINNED, RECENT, OLDER, OWL]);
  type("night");
  archive("p2");
  expect(document.activeElement).toBe(moreOf("Night owl"));
});

test("with no row after it, the keyboard goes to the search", () => {
  const { archive } = onScreen([PINNED, RECENT, OLDER]);
  moreOf("Night market").focus();
  const focus = vi.spyOn(search(), "focus");
  archive("p3");
  expect(document.activeElement).toBe(search());
  // The search may be far above a long list's last row: it is scrolled into view, not left off it.
  expect(focus).toHaveBeenCalledWith();
});

test("the last project archived, Projects says every project is archived at once", () => {
  const { container, archive } = onScreen([RECENT]);
  archive("p2");
  expect(screen.getByText("Every project is archived.", { selector: ".all-projects__empty" })).toBeTruthy();
  expect(counts(container)).toEqual(["0", "1"]);
  expect(document.activeElement).toBe(search());
});

test("once the server has answered, the list it sends stands, and only the archive was asked", async () => {
  // Madde 384: the server takes the pin away with the archive; the screen asks for nothing else and
  // draws where the server lists the project.
  const { container, props, archive, answer } = onScreen([PINNED, RECENT, OLDER]);
  archive("p1");
  await answer([RECENT, { ...PINNED, pinned: false, archived: true }, OLDER]);
  expect(labels(container)).toEqual(["Recent"]);
  expect(names(container)).toEqual(["Night market", "Old pier"]);
  expect(counts(container)).toEqual(["2", "1"]);
  expect(props.onArchiveProject.mock.calls).toEqual([["p1", true]]);
});

test("an archive the server refused brings the project back to Projects", async () => {
  // editProject keeps the refusal's words for the line over the list, and hands back the list as
  // the server still has it.
  const { container, archive, answer } = onScreen([PINNED, RECENT, OLDER]);
  archive("p2");
  await answer([PINNED, RECENT, OLDER]);
  expect(names(container)).toEqual(["Harbour at dusk", "Night market", "Old pier"]);
  expect(counts(container)).toEqual(["3", "0"]);
});

test("two archives in a row each leave at once, and each waits for its own answer", async () => {
  const { container, archive, answer } = onScreen([PINNED, RECENT, OLDER]);
  archive("p2");
  archive("p3");
  expect(names(container)).toEqual(["Harbour at dusk"]);
  expect(counts(container)).toEqual(["1", "2"]);
  // The first answer's list does not have the second archive yet.
  await answer([PINNED, { ...RECENT, archived: true }, OLDER]);
  expect(names(container)).toEqual(["Harbour at dusk"]);
  await answer([PINNED, { ...RECENT, archived: true }, { ...OLDER, archived: true }]);
  expect(names(container)).toEqual(["Harbour at dusk"]);
  expect(counts(container)).toEqual(["1", "2"]);
});

test("Unarchive asks for the project back", () => {
  const onArchiveProject = vi.fn();
  render(
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
});

// --- Madde 450: the last press stands ------------------------------------------------------------

test("Unarchive takes the row out of Archived before the server answers", () => {
  const { container, unarchive } = onScreen([PINNED, SHELVED, RECENT]);
  fireEvent.click(tab("Archived"));
  unarchive("p5");
  expect(screen.getByText("No archived projects.", { selector: ".all-projects__empty" })).toBeTruthy();
  expect(counts(container)).toEqual(["3", "0"]);
});

test("an unarchive the server refused brings the project back to Archived", async () => {
  const { container, unarchive, answer } = onScreen([PINNED, SHELVED, RECENT]);
  fireEvent.click(tab("Archived"));
  unarchive("p5");
  await answer([PINNED, SHELVED, RECENT]);
  expect(names(container)).toEqual(["Shelved reel"]);
  expect(counts(container)).toEqual(["2", "1"]);
});

test("Unarchive pressed while the archive is on its way keeps the project on Projects", async () => {
  const { container, props, archive, unarchive, answer } = onScreen([PINNED, RECENT, OLDER]);
  archive("p2");
  fireEvent.click(tab("Archived"));
  unarchive("p2");
  expect(screen.getByText("No archived projects.", { selector: ".all-projects__empty" })).toBeTruthy();
  fireEvent.click(tab("Projects"));
  expect(names(container)).toEqual(["Harbour at dusk", "Night market", "Old pier"]);
  // The archive's answer is the list as it stood after the archive: the later press still stands.
  await answer([PINNED, { ...RECENT, archived: true }, OLDER]);
  expect(names(container)).toEqual(["Harbour at dusk", "Night market", "Old pier"]);
  expect(counts(container)).toEqual(["3", "0"]);
  await answer([PINNED, RECENT, OLDER]);
  expect(names(container)).toEqual(["Harbour at dusk", "Night market", "Old pier"]);
  expect(props.onArchiveProject.mock.calls).toEqual([
    ["p2", true],
    ["p2", false],
  ]);
});

test("Archive pressed while the unarchive is on its way keeps the project on Archived", async () => {
  const { container, unarchive, archive, answer } = onScreen([PINNED, SHELVED, RECENT]);
  fireEvent.click(tab("Archived"));
  unarchive("p5");
  fireEvent.click(tab("Projects"));
  archive("p5");
  expect(names(container)).toEqual(["Harbour at dusk", "Night market"]);
  await answer([PINNED, { ...SHELVED, archived: false }, RECENT]);
  expect(names(container)).toEqual(["Harbour at dusk", "Night market"]);
  expect(counts(container)).toEqual(["2", "1"]);
  await answer([PINNED, SHELVED, RECENT]);
  fireEvent.click(tab("Archived"));
  expect(names(container)).toEqual(["Shelved reel"]);
});

// --- Madde 451: Unarchive hands the keyboard over as Archive does --------------------------------

const STORED = { ...SHELVED, id: "p7", name: "Stored cut", lastActivity: ago(40) };
const SHELF = { ...SHELVED, id: "p8", name: "Shelf talk", lastActivity: ago(60) };

test("after Unarchive the keyboard goes to the ⋯ of the archived row that now stands where it stood", () => {
  const { unarchive } = onScreen([PINNED, SHELVED, STORED, RECENT]);
  fireEvent.click(tab("Archived"));
  const focus = vi.spyOn(moreOf("Stored cut"), "focus");
  unarchive("p5");
  expect(document.activeElement).toBe(moreOf("Stored cut"));
  expect(focus).toHaveBeenCalledWith({ preventScroll: true });
});

test("searched, Unarchive hands the keyboard to the next archived row the search left", () => {
  const { unarchive } = onScreen([SHELVED, STORED, SHELF]);
  fireEvent.click(tab("Archived"));
  type("shel");
  unarchive("p5");
  expect(document.activeElement).toBe(moreOf("Shelf talk"));
});

test("with no archived row after it, Unarchive hands the keyboard to the search", () => {
  const { unarchive } = onScreen([PINNED, SHELVED, STORED]);
  fireEvent.click(tab("Archived"));
  moreOf("Shelved reel").focus();
  const focus = vi.spyOn(search(), "focus");
  unarchive("p7");
  expect(document.activeElement).toBe(search());
  // Scrolled into view, as after the last Archive: a long archive's last row may be far below it.
  expect(focus).toHaveBeenCalledWith();
});

test("the last archived project back, the keyboard is on the search", () => {
  const { unarchive } = onScreen([PINNED, SHELVED]);
  fireEvent.click(tab("Archived"));
  // The search took the keyboard as the screen opened; the press is made from the row's own ⋯.
  moreOf("Shelved reel").focus();
  unarchive("p5");
  expect(screen.getByText("No archived projects.", { selector: ".all-projects__empty" })).toBeTruthy();
  expect(document.activeElement).toBe(search());
});

test("an unarchive the server refused brings the row back, and the keyboard stays where it went", async () => {
  // The answer can come seconds later, when the user may be elsewhere: it does not pull the keyboard.
  const { container, unarchive, answer } = onScreen([PINNED, SHELVED, STORED]);
  fireEvent.click(tab("Archived"));
  unarchive("p5");
  await answer([PINNED, SHELVED, STORED]);
  expect(names(container)).toEqual(["Shelved reel", "Stored cut"]);
  expect(document.activeElement).toBe(moreOf("Stored cut"));
});

test("a pressed row not among the drawn ⋯ hands the keyboard to the search, not the first ⋯", () => {
  const { archive } = onScreen([PINNED, RECENT, OLDER]);
  // The hand-over finds the pressed row by its ⋯; one it cannot find has no next row to name.
  moreOf("Night market").removeAttribute("data-project");
  moreOf("Old pier").focus();
  archive("p2");
  expect(document.activeElement).toBe(search());
});

// --- Madde 443: an archived project opens, and Enter opens the first match (the design's 218) -----

test("pressing an archived row opens that project, as any row does", () => {
  const onOpenProject = vi.fn();
  render(<AllProjectsScreen projects={[PINNED, SHELVED]} onOpenProject={onOpenProject} />);
  fireEvent.click(tab("Archived"));
  fireEvent.click(screen.getByRole("button", { name: /^Shelved reel/ }));
  expect(onOpenProject).toHaveBeenCalledWith("p5");
});

const enter = () => fireEvent.keyDown(search(), { key: "Enter" });

test("on Projects, Enter opens the first row the search left, the pinned before the recent", () => {
  const NIGHT_PIN = { ...PINNED, id: "p6", name: "Night shift" };
  const onOpenProject = vi.fn();
  render(
    <AllProjectsScreen projects={[NIGHT_PIN, PINNED, RECENT, OLDER]} onOpenProject={onOpenProject} />,
  );
  type("night");
  enter();
  expect(onOpenProject.mock.calls).toEqual([["p6"]]);
  type("pier");
  enter();
  expect(onOpenProject).toHaveBeenLastCalledWith("p3");
});

test("on Archived, Enter opens the first archived row the search left", () => {
  const DUSTY = { ...SHELVED, id: "p7", name: "Dusty reel", lastActivity: ago(40) };
  const onOpenProject = vi.fn();
  render(
    <AllProjectsScreen projects={[PINNED, SHELVED, RECENT, DUSTY]} onOpenProject={onOpenProject} />,
  );
  fireEvent.click(tab("Archived"));
  type("dusty");
  enter();
  expect(onOpenProject.mock.calls).toEqual([["p7"]]);
});

test("with the box empty, Enter opens the tab's first row", () => {
  const onOpenProject = vi.fn();
  render(<AllProjectsScreen projects={[PINNED, SHELVED, RECENT]} onOpenProject={onOpenProject} />);
  enter();
  expect(onOpenProject).toHaveBeenLastCalledWith("p1");
  fireEvent.click(tab("Archived"));
  enter();
  expect(onOpenProject).toHaveBeenLastCalledWith("p5");
});

test("with no match, and while the list loads, Enter opens nothing", () => {
  const onOpenProject = vi.fn();
  const { rerender } = render(
    <AllProjectsScreen projects={[PINNED, RECENT]} onOpenProject={onOpenProject} />,
  );
  type("zzz");
  enter();
  // Try again after a failed read waits with the list it last had: the spinner stands, and no row.
  rerender(<AllProjectsScreen projects={[PINNED, RECENT]} loading onOpenProject={onOpenProject} />);
  type("");
  enter();
  expect(onOpenProject).not.toHaveBeenCalled();
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
