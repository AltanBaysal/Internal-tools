import { fireEvent, render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import NoProjectsScreen from "./NoProjectsScreen.jsx";

test("it says there are none yet", () => {
  render(<NoProjectsScreen />);
  expect(screen.getByRole("heading", { level: 1 }).textContent).toBe("No projects yet");
});

test("the line under it says why a project comes first", () => {
  render(<NoProjectsScreen />);
  expect(
    screen.getByText(
      "Chats live inside a project, and the files they create stay there. Create a project to start.",
    ),
  ).toBeTruthy();
});

test("New project asks for one", () => {
  const onNewProject = vi.fn();
  render(<NoProjectsScreen onNewProject={onNewProject} />);
  fireEvent.click(screen.getByRole("button", { name: "+ New project" }));
  expect(onNewProject).toHaveBeenCalled();
});

test("there is nothing to type into", () => {
  // A message is always written from inside a project, so this screen offers no way to send one.
  render(<NoProjectsScreen />);
  expect(screen.queryByPlaceholderText(/Ask anything/)).toBeNull();
  expect(screen.queryByRole("button", { name: "Send" })).toBeNull();
});

test("there is no grid and nothing standing in for one", () => {
  render(<NoProjectsScreen />);
  expect(screen.queryByTestId("skeleton")).toBeNull();
});

test("a list that failed to load says so instead of claiming there are none", () => {
  // A 500 means the count is unknown, not zero -- and the offer to create one would be a guess.
  render(<NoProjectsScreen error="GET /api/projects failed with 500" />);
  expect(screen.getByText("GET /api/projects failed with 500")).toBeTruthy();
  expect(screen.queryByText("No projects yet")).toBeNull();
  expect(screen.queryByRole("button", { name: "+ New project" })).toBeNull();
});
