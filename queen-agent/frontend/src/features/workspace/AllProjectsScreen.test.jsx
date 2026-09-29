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

test("a list that could not be read says what the server said, and nothing else", () => {
  // A failed list means the count is unknown, not zero.
  render(<AllProjectsScreen projects={[]} error="the store is unreachable" />);
  expect(screen.getByText("the store is unreachable")).toBeTruthy();
  expect(screen.queryByText("No projects yet.")).toBeNull();
  expect(screen.queryByText("All projects")).toBeNull();
});

test("the screen carries no search yet", () => {
  // The search is Madde 359's.
  render(<AllProjectsScreen projects={[PINNED]} />);
  expect(screen.queryByPlaceholderText("Search projects")).toBeNull();
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
