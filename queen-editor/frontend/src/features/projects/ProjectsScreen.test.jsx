import { act, fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { deleteProject, listProjects } from "../../shared/api.js";
import { navigate } from "../../shared/router.js";
import ProjectsScreen from "./ProjectsScreen.jsx";

vi.mock("../../shared/api.js", () => ({
  createProject: vi.fn(),
  deleteProject: vi.fn(),
  listProjects: vi.fn(),
}));
vi.mock("../../shared/router.js", () => ({
  navigate: vi.fn(),
  projectPath: (project) => `/projects/${encodeURIComponent(project)}`,
}));

async function settle() {
  await act(async () => { await Promise.resolve(); });
}

async function openScreen() {
  listProjects.mockResolvedValue([{ name: "düğün", modifiedAt: 1754300000 }]);
  render(<ProjectsScreen />);
  await settle();
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe("ProjectsScreen proje silme", () => {
  it("çöpe basmak projeyi açmaz, önce onay sorar", async () => {
    await openScreen();

    fireEvent.click(screen.getByLabelText("Projeyi sil"));

    expect(navigate).not.toHaveBeenCalled();
    expect(screen.getByText('"düğün" projesi silinsin mi?')).toBeTruthy();
    expect(deleteProject).not.toHaveBeenCalled();
  });

  it("onaylayınca projeyi siler ve listeyi tazeler", async () => {
    await openScreen();
    deleteProject.mockResolvedValue(null);
    listProjects.mockResolvedValue([]);

    fireEvent.click(screen.getByLabelText("Projeyi sil"));
    await act(async () => { fireEvent.click(screen.getByText("Sil")); });

    expect(deleteProject).toHaveBeenCalledWith("düğün");
    expect(listProjects).toHaveBeenCalledTimes(2);
    expect(screen.queryByText("düğün")).toBeNull();
  });

  it("karta tıklamak projeyi açar", async () => {
    await openScreen();

    fireEvent.click(screen.getByText("düğün"));

    expect(navigate).toHaveBeenCalledWith(`/projects/${encodeURIComponent("düğün")}`);
  });
});
