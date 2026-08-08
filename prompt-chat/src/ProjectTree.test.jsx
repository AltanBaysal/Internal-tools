import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import ProjectTree from "./ProjectTree.jsx";

const PROJECTS = [
  { id: 1, name: "Kış çekimi" },
  { id: 2, name: "Yaz kampanyası" },
];
const FILES = [
  { id: 1, projectId: 1, name: "plan.md", content: "" },
  { id: 2, projectId: 2, name: "baska.md", content: "" },
];
const CHATS = [
  { id: 1, projectId: 1, messages: [{ role: "user", content: "kar manzarası" }], draft: "" },
  { id: 2, projectId: 2, messages: [], draft: "" },
];

function draw() {
  const on = {
    openProject: vi.fn(),
    newProject: vi.fn(),
    deleteProject: vi.fn(),
    openFile: vi.fn(),
    newFile: vi.fn(),
    deleteFile: vi.fn(),
    openChat: vi.fn(),
    newChat: vi.fn(),
    deleteChat: vi.fn(),
  };
  render(
    <ProjectTree
      projects={PROJECTS}
      files={FILES}
      chats={CHATS}
      active={{ projectId: 1, chatId: 1, fileId: null }}
      on={on}
    />
  );
  return on;
}

describe("ProjectTree", () => {
  it("lists every project", () => {
    draw();
    expect(screen.getByText(/Kış çekimi/)).toBeTruthy();
    expect(screen.getByText(/Yaz kampanyası/)).toBeTruthy();
  });

  it("shows the open project's files and chats, and nobody else's", () => {
    draw();
    expect(screen.getByText("plan.md")).toBeTruthy();
    expect(screen.queryByText("baska.md")).toBeNull();
    expect(screen.getByText("kar manzarası")).toBeTruthy();
  });

  it("opens a project when its name is clicked", () => {
    const on = draw();
    fireEvent.click(screen.getByText(/Yaz kampanyası/));
    expect(on.openProject).toHaveBeenCalledWith(2);
  });

  it("opens a file and a chat by their rows", () => {
    const on = draw();
    fireEvent.click(screen.getByText("plan.md"));
    expect(on.openFile).toHaveBeenCalledWith(1);
    fireEvent.click(screen.getByText("kar manzarası"));
    expect(on.openChat).toHaveBeenCalledWith(1);
  });

  it("names what a delete would take, so the two lists never mix up", () => {
    const on = draw();
    fireEvent.click(screen.getByRole("button", { name: "plan.md dosyasını sil" }));
    expect(on.deleteFile).toHaveBeenCalledWith(1);
    fireEvent.click(screen.getByRole("button", { name: /kar manzarası sohbetini sil/ }));
    expect(on.deleteChat).toHaveBeenCalledWith(1);
  });

  it("counts out loud what deleting a project would cost", () => {
    const on = draw();
    fireEvent.click(screen.getByRole("button", { name: "Kış çekimi projesini sil" }));
    expect(on.deleteProject).toHaveBeenCalledWith(1, { files: 1, chats: 1 });
  });

  it("offers a way to add each of the three", () => {
    const on = draw();
    fireEvent.click(screen.getByRole("button", { name: /Yeni proje/ }));
    fireEvent.click(screen.getByRole("button", { name: /Yeni dosya/ }));
    fireEvent.click(screen.getByRole("button", { name: /Yeni sohbet/ }));
    expect(on.newProject).toHaveBeenCalled();
    expect(on.newFile).toHaveBeenCalled();
    expect(on.newChat).toHaveBeenCalled();
  });
});
