import { fireEvent, render, screen } from "@testing-library/react";
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
  fireEvent.click(screen.getByRole("button", { name: /Night market/ }));
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

test("a list that could not be read says what the server said, and nothing else", () => {
  // A failed list means the count is unknown, not zero.
  render(<AllProjectsScreen projects={[]} error="the store is unreachable" />);
  expect(screen.getByText("the store is unreachable")).toBeTruthy();
  expect(screen.queryByText("No projects yet.")).toBeNull();
  expect(screen.queryByText("All projects")).toBeNull();
});

test("no row carries a menu yet", () => {
  // The row's ⋯ is Madde 360's.
  const { container } = render(<AllProjectsScreen projects={[PINNED]} />);
  expect(container.querySelector(".all-projects__row-more")).toBeNull();
});

// --- Madde 359: the search (the design's items 135, 142, 167) ------------------------------------

const search = () => screen.getByRole("textbox", { name: "Search projects" });
const type = (text) => fireEvent.change(search(), { target: { value: text } });

test("the search stands under the head, named Search projects", () => {
  render(<AllProjectsScreen projects={[PINNED, RECENT]} />);
  const box = search();
  expect(box.getAttribute("placeholder")).toBe("Search projects");
  expect(box.classList.contains("all-projects__search")).toBe(true);
  // The tabs join this row with Madde 363.
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
