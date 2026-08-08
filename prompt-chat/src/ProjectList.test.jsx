import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import ProjectList from "./ProjectList.jsx";

const PROJECTS = [
  { id: 1, name: "Kış çekimi" },
  { id: 2, name: "Yaz kampanyası" },
];
const FILES = [{ id: 1, projectId: 1, name: "plan.md", content: "" }];
const CHATS = [{ id: 1, projectId: 1, messages: [], draft: "" }];

function draw() {
  const on = { openProject: vi.fn(), newProject: vi.fn(), deleteProject: vi.fn() };
  render(<ProjectList projects={PROJECTS} files={FILES} chats={CHATS} activeId={1} on={on} />);
  return on;
}

describe("ProjectList", () => {
  it("lists every project", () => {
    draw();
    expect(screen.getByText("Kış çekimi")).toBeTruthy();
    expect(screen.getByText("Yaz kampanyası")).toBeTruthy();
  });

  it("marks the open one so switching is a deliberate act", () => {
    draw();
    expect(screen.getByText("Kış çekimi").closest(".row").className).toContain("active");
    expect(screen.getByText("Yaz kampanyası").closest(".row").className).not.toContain("active");
  });

  it("opens a project by its name", () => {
    const on = draw();
    fireEvent.click(screen.getByText("Yaz kampanyası"));
    expect(on.openProject).toHaveBeenCalledWith(2);
  });

  it("counts out loud what deleting a project would cost", () => {
    const on = draw();
    fireEvent.click(screen.getByRole("button", { name: "Kış çekimi projesini sil" }));
    expect(on.deleteProject).toHaveBeenCalledWith(1, { files: 1, chats: 1 });
  });

  it("offers a way to add one", () => {
    const on = draw();
    fireEvent.click(screen.getByRole("button", { name: "+ Yeni proje" }));
    expect(on.newProject).toHaveBeenCalled();
  });
});
