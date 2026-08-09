import { fireEvent, render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import ProjectScreen from "./ProjectScreen.jsx";

const PROJECT = {
  id: "p1",
  name: "Thesis research",
  desc: "Source summaries.",
  hue: 45,
  chats: 0,
  files: 0,
};

test("the title, the description and both column headings are drawn", () => {
  render(<ProjectScreen project={PROJECT} />);
  expect(screen.getByRole("heading", { level: 1 }).textContent).toBe("Thesis research");
  expect(screen.getByText("Source summaries.")).toBeTruthy();
  expect(screen.getByText("Chats")).toBeTruthy();
  expect(screen.getByText("Files Mira created")).toBeTruthy();
});

test("an empty file column teaches instead of sitting blank", () => {
  render(<ProjectScreen project={PROJECT} />);
  expect(screen.getByText(/No files yet/)).toBeTruthy();
});

test("a project that does not exist says so instead of crashing", () => {
  // The address bar is something a person can type into, so a wrong id has to be survivable.
  render(<ProjectScreen project={null} />);
  expect(screen.getByText("That project does not exist.")).toBeTruthy();
});

test("Rename asks for a new name", () => {
  const onRename = vi.fn();
  render(<ProjectScreen project={PROJECT} onRename={onRename} />);
  fireEvent.click(screen.getByRole("button", { name: "Rename" }));
  expect(onRename).toHaveBeenCalled();
});

test("clicking the description asks to change it", () => {
  const onDescribe = vi.fn();
  render(<ProjectScreen project={PROJECT} onDescribe={onDescribe} />);
  fireEvent.click(screen.getByText("Source summaries."));
  expect(onDescribe).toHaveBeenCalled();
});
