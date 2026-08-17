import { fireEvent, render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import HomeScreen from "./HomeScreen.jsx";

test("blocks stand where the cards will be until the list arrives", () => {
  render(<HomeScreen projects={[]} loading />);
  expect(screen.getByTestId("skeleton")).toBeTruthy();
});

test("the blocks go once the list has arrived", () => {
  render(<HomeScreen projects={[]} />);
  expect(screen.queryByTestId("skeleton")).toBeNull();
});

const ONE = [{ id: "p1", name: "Thesis", desc: "Summaries.", hue: 45, chats: 1, files: 1 }];
const MANY = [{ id: "p2", name: "Notes", desc: "Records.", hue: 150, chats: 2, files: 0 }];

test("the greeting carries no name", () => {
  render(<HomeScreen projects={[]} error={null} />);
  expect(screen.getByRole("heading", { level: 1 }).textContent).toBe("Hi");
});

test("the send button is disabled in this phase", () => {
  // "An empty draft disables Send" is a rule and its home is Madde 8; half of it written twice
  // would be half of it wrong once.
  render(<HomeScreen projects={[]} error={null} />);
  expect(screen.getByRole("button", { name: "Send" }).disabled).toBe(true);
});

test("a single chat and file are written in the singular", () => {
  render(<HomeScreen projects={ONE} error={null} />);
  expect(screen.getByText("1 chat · 1 file")).toBeTruthy();
});

test("two chats and no files are written in the plural", () => {
  render(<HomeScreen projects={MANY} error={null} />);
  expect(screen.getByText("2 chats · 0 files")).toBeTruthy();
});

test("New project asks for one", () => {
  const onNewProject = vi.fn();
  render(<HomeScreen projects={[]} error={null} onNewProject={onNewProject} />);
  fireEvent.click(screen.getByRole("button", { name: "New project" }));
  expect(onNewProject).toHaveBeenCalled();
});

test("clicking a card asks to open that project", () => {
  const onOpenProject = vi.fn();
  render(<HomeScreen projects={ONE} error={null} onOpenProject={onOpenProject} />);
  fireEvent.click(screen.getByText("Thesis"));
  expect(onOpenProject).toHaveBeenCalledWith("p1");
});

test("a load failure is shown instead of an empty screen", () => {
  render(<HomeScreen projects={[]} error="GET /api/projects failed with 500" />);
  expect(screen.getByText(/failed with 500/)).toBeTruthy();
});
