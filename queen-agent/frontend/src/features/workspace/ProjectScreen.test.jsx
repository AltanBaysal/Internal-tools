import { fireEvent, render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import ProjectScreen from "./ProjectScreen.jsx";

// The second of the two doors the design opens onto the same box.
test("the header offers to delete the project", () => {
  const onDelete = vi.fn();
  render(<ProjectScreen project={{ id: "p1", name: "Thesis research" }} onDelete={onDelete} />);
  fireEvent.click(screen.getByRole("button", { name: "Delete" }));
  expect(onDelete).toHaveBeenCalled();
});

test("the header does not delete anything by itself", () => {
  // It opens the question; the answer belongs to the box.
  const onDelete = vi.fn();
  render(<ProjectScreen project={{ id: "p1", name: "Thesis research" }} onDelete={onDelete} />);
  expect(screen.queryByText(/can't be undone/)).toBeNull();
});

const PROJECT = {
  id: "p1",
  name: "Thesis research",
  desc: "Source summaries.",
  chats: 0,
  files: 0,
};

test("the title and both column headings are drawn", () => {
  render(<ProjectScreen project={PROJECT} />);
  expect(screen.getByRole("heading", { level: 1 }).textContent).toBe("Thesis research");
  expect(screen.getByText("Chats")).toBeTruthy();
  expect(screen.getByText("Files QueenAgent created")).toBeTruthy();
});

test("a chat row is a real button and its × is a sibling", () => {
  const chats = [{ id: "c1", title: "First chat", lastActivity: new Date().toISOString() }];
  const { container } = render(
    <ProjectScreen project={PROJECT} chats={chats} onOpenChat={vi.fn()} onDeleteChat={vi.fn()} />,
  );
  // Anchored: the × next to it is named "Delete First chat".
  const opener = screen.getByRole("button", { name: /^First chat/ });
  expect(opener.tagName).toBe("BUTTON");
  const remove = screen.getByRole("button", { name: "Delete First chat" });
  expect(container.querySelector(".chat-row__open").contains(remove)).toBe(false);
  expect(remove.title).toBe("Delete First chat");
});

test("the layout says when something is being read", () => {
  const { container } = render(<ProjectScreen project={PROJECT} reading={{ name: "a.md" }} />);
  expect(container.querySelector(".screen-layout--reading")).toBeTruthy();
});

test("with nothing open the layout says nothing", () => {
  const { container } = render(<ProjectScreen project={PROJECT} />);
  expect(container.querySelector(".screen-layout--reading")).toBeNull();
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

test("a file list that could not be read says so instead of teaching", () => {
  render(<ProjectScreen project={PROJECT} filesError="the store is unreachable" />);
  expect(screen.getByText("the store is unreachable")).toBeTruthy();
  expect(screen.queryByText(/No files yet/)).toBeNull();
});

test("a chat list that could not be read no longer empties in silence", () => {
  // The quieter of the two lies: no list, no sentence, no reason.
  render(<ProjectScreen project={PROJECT} chatsError="the store is unreachable" />);
  expect(screen.getByText("the store is unreachable")).toBeTruthy();
});

test("a failure and a refused delete are two lines, not one", () => {
  const { container } = render(
    <ProjectScreen
      project={PROJECT}
      filesError="the store is unreachable"
      deleting={{ error: "HTTP 409", remove: vi.fn() }}
    />,
  );
  expect(container.querySelectorAll(".list-error").length).toBe(2);
});

test("the file column lists what the project holds", () => {
  const files = [{ name: "outline.md", ext: "md", modifiedAt: new Date().toISOString() }];
  render(<ProjectScreen project={PROJECT} files={files} />);
  expect(screen.getByText("outline.md")).toBeTruthy();
  // The teaching line is for an empty project; a full one has better things to say.
  expect(screen.queryByText(/No files yet/)).toBeNull();
});

test("a file row says whose file it is here too", () => {
  // The row is one shape wherever it stands: a file belongs to the project, never to a chat.
  const files = [
    { name: "outline.md", ext: "md", modifiedAt: new Date(Date.now() - 2 * 3600_000).toISOString() },
  ];
  render(<ProjectScreen project={PROJECT} files={files} />);
  expect(screen.getByText("project file · 2h ago")).toBeTruthy();
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

// The panel is showing the files column's subject, so leaving the column standing would put the
// same list on the screen twice. The chat rail keeps its list for the opposite reason: there the
// reader is the rail widened, and the list is its neighbour rather than its copy.
test("with the panel open the files column is not drawn at all", () => {
  const files = [{ name: "outline.md", ext: "md", modifiedAt: new Date().toISOString() }];
  const reading = { name: "outline.md", file: { ...files[0], size: 7, text: "read me" } };
  const chats = [{ id: "c1", title: "Write the intro", lastActivity: new Date().toISOString() }];
  render(<ProjectScreen project={PROJECT} chats={chats} files={files} reading={reading} />);
  expect(screen.queryByText("Files QueenAgent created")).toBeNull();
  // What stays: the title row, the composer and the chats.
  expect(screen.getByRole("heading", { level: 1 }).textContent).toBe("Thesis research");
  expect(screen.getByRole("button", { name: "Start" })).toBeTruthy();
  expect(screen.getByText("Chats")).toBeTruthy();
  expect(screen.getByText("Write the intro")).toBeTruthy();
});

test("nothing can be deleted from a column that is not there", () => {
  const files = [{ name: "outline.md", ext: "md", modifiedAt: new Date().toISOString() }];
  const reading = { name: "outline.md", file: { ...files[0], size: 7, text: "read me" } };
  render(
    <ProjectScreen project={PROJECT} files={files} reading={reading} deleting={{ remove: vi.fn() }} />,
  );
  expect(screen.queryByRole("button", { name: "Delete outline.md" })).toBeNull();
});

test("closing the panel brings the column back", () => {
  const files = [{ name: "outline.md", ext: "md", modifiedAt: new Date().toISOString() }];
  const reading = { name: "outline.md", file: { ...files[0], size: 7, text: "read me" } };
  const { rerender } = render(<ProjectScreen project={PROJECT} files={files} reading={reading} />);
  rerender(<ProjectScreen project={PROJECT} files={files} reading={{}} />);
  expect(screen.getByText("Files QueenAgent created")).toBeTruthy();
  expect(screen.getByText("outline.md")).toBeTruthy();
});

test("the panel beside the grid closes rather than going back", () => {
  // There is nothing to go back to: the grid is still there under it.
  const files = [{ name: "outline.md", ext: "md", modifiedAt: new Date().toISOString() }];
  const close = vi.fn();
  const reading = { name: "outline.md", file: { ...files[0], size: 7, text: "read me" }, close };
  render(<ProjectScreen project={PROJECT} files={files} reading={reading} />);
  fireEvent.click(screen.getByRole("button", { name: "×" }));
  expect(close).toHaveBeenCalled();
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

test("a chat row offers no rename", () => {
  // Renaming lives on the project alone; the row opens and deletes, nothing else.
  const chats = [{ id: "c1", title: "Write the intro", lastActivity: new Date().toISOString() }];
  render(<ProjectScreen project={PROJECT} chats={chats} onOpenChat={vi.fn()} />);
  expect(screen.queryByRole("button", { name: "Rename Write the intro" })).toBeNull();
});

// --- the pickers, moved here (Madde 77) ----------------------------------------------------------
//
// They used to be on the chat composer alone, and this file had a test saying so. That is what
// Madde 65 tried to work around by landing somewhere else; the screen was not missing a visit, it
// was missing these two controls.

test("the composer here carries both pickers, in the chat screen's order", () => {
  // The same order as the chat screen -- two orders for the same three controls is the same thing
  // learned twice.
  const { container } = render(<ProjectScreen project={PROJECT} model="grok-4.6" />);
  const buttons = [...container.querySelectorAll(".composer__foot button")];
  expect(buttons.map((button) => button.textContent)).toEqual(["Skills⌄", "Grok 4.6⌄", "Start"]);
});

test("picking a skill is passed up rather than kept here", () => {
  // There is no chat yet, so there is no record to write to. The choice belongs to the session, and
  // App is what holds it.
  const onSkillChange = vi.fn();
  render(<ProjectScreen project={PROJECT} picker="skills" onSkillChange={onSkillChange} />);
  fireEvent.click(screen.getByText("Create scenario", { selector: ".menu__item-name" }));
  expect(onSkillChange).toHaveBeenCalledWith("create-scenario");
});

test("picking a model is passed up rather than kept here", () => {
  const onModelChange = vi.fn();
  render(
    <ProjectScreen
      project={PROJECT}
      model="grok-4.6"
      picker="model"
      onModelChange={onModelChange}
    />,
  );
  fireEvent.click(screen.getByText("Grok Build"));
  expect(onModelChange).toHaveBeenCalledWith("grok-build-0.1");
});

test("which picker is open is told to the screen rather than decided by it", () => {
  // Escape closes them in a fixed order and one listener owns it, so the open one cannot be a
  // secret this screen keeps.
  const onPicker = vi.fn();
  render(<ProjectScreen project={PROJECT} onPicker={onPicker} />);
  expect(screen.queryByText("Create scenario", { selector: ".menu__item-name" })).toBeNull();
  fireEvent.click(screen.getByRole("button", { name: /Skills/ }));
  expect(onPicker).toHaveBeenCalledWith("skills");
});

test("the screen starts with its title", () => {
  render(<ProjectScreen project={PROJECT} onBack={vi.fn()} />);
  expect(screen.queryByRole("button", { name: "← back" })).toBeNull();
});

test("a project that is not there says so and offers no way back", () => {
  render(<ProjectScreen project={null} onBack={vi.fn()} />);
  expect(screen.queryByRole("button", { name: "← back" })).toBeNull();
});

test("nothing is written under the composer", () => {
  render(<ProjectScreen project={PROJECT} />);
  expect(screen.queryByText("the answer is saved as a file")).toBeNull();
});

test("a file list carries no advice under it", () => {
  const files = [{ name: "plan.md", ext: "md", modifiedAt: new Date().toISOString() }];
  render(<ProjectScreen project={PROJECT} files={files} />);
  expect(screen.queryByText(/Chats create the files/)).toBeNull();
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

test("the screen carries no description to click", () => {
  // PROJECT still holds a desc on purpose: a field the server no longer sends must not be drawn
  // even if one turns up.
  render(<ProjectScreen project={PROJECT} />);
  expect(screen.queryByText("Source summaries.")).toBeNull();
});
