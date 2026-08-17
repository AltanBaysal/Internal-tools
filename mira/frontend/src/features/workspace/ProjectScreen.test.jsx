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
  expect(screen.getByText("Files QueenAgent created")).toBeTruthy();
});

test("an empty file column teaches instead of sitting blank", () => {
  render(<ProjectScreen project={PROJECT} />);
  expect(screen.getByText(/No files yet/)).toBeTruthy();
});

test("while the lists load there are blocks and no teaching line", () => {
  render(<ProjectScreen project={PROJECT} loadingChats loadingFiles />);
  expect(screen.getAllByTestId("skeleton").length).toBe(2);
  // "No files yet" before the answer arrives would be a guess stated as a fact.
  expect(screen.queryByText(/No files yet/)).toBeNull();
});

test("the file column lists what the project holds", () => {
  const files = [{ name: "outline.md", ext: "md", modifiedAt: new Date().toISOString() }];
  render(<ProjectScreen project={PROJECT} files={files} />);
  expect(screen.getByText("outline.md")).toBeTruthy();
  // The teaching line is for an empty project; a full one has better things to say.
  expect(screen.queryByText(/No files yet/)).toBeNull();
});

test("clicking a file opens it beside the grid, which drops to one column", () => {
  const files = [{ name: "outline.md", ext: "md", modifiedAt: new Date().toISOString() }];
  const open = vi.fn();
  const { container, rerender } = render(
    <ProjectScreen project={PROJECT} files={files} reading={{ open }} />,
  );
  fireEvent.click(screen.getByText("outline.md"));
  expect(open).toHaveBeenCalledWith("outline.md");

  const reading = { name: "outline.md", file: { ...files[0], size: 7, text: "read me" } };
  rerender(<ProjectScreen project={PROJECT} files={files} reading={reading} />);
  expect(screen.getByText("read me")).toBeTruthy();
  expect(container.querySelector(".project-grid").className).toContain("project-grid--reading");
});

test("a chat row can be asked to go, and asking is all the row does", () => {
  const chats = [{ id: "c1", title: "Write the intro", lastActivity: new Date().toISOString() }];
  const onDeleteChat = vi.fn();
  const onOpenChat = vi.fn();
  render(
    <ProjectScreen
      project={PROJECT}
      chats={chats}
      onDeleteChat={onDeleteChat}
      onOpenChat={onOpenChat}
    />,
  );
  fireEvent.click(screen.getByRole("button", { name: "Delete Write the intro" }));
  expect(onDeleteChat).toHaveBeenCalledWith("c1");
  // The confirmation is App's to ask; the row does not open the chat on its way out.
  expect(onOpenChat).not.toHaveBeenCalled();
});

test("a chat row can be asked for a new title", () => {
  const chats = [{ id: "c1", title: "Write the intro", lastActivity: new Date().toISOString() }];
  const onRenameChat = vi.fn();
  const onOpenChat = vi.fn();
  render(
    <ProjectScreen
      project={PROJECT}
      chats={chats}
      onRenameChat={onRenameChat}
      onOpenChat={onOpenChat}
    />,
  );
  fireEvent.click(screen.getByRole("button", { name: "Rename Write the intro" }));
  expect(onRenameChat).toHaveBeenCalledWith("c1");
  expect(onOpenChat).not.toHaveBeenCalled();
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
