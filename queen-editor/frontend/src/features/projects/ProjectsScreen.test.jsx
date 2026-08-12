import { act, fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { deleteProject, listProjects } from "../../shared/api.js";
import { navigate } from "../../shared/router.js";
import ProjectsScreen from "./ProjectsScreen.jsx";

vi.mock("../../shared/api.js", () => ({
  checkProjectName: vi.fn().mockResolvedValue({ error: null }),
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

describe("ProjectsScreen with nothing in it yet", () => {
  it("says what a project would fill up with", async () => {
    listProjects.mockResolvedValue([]);
    render(<ProjectsScreen />);
    await settle();

    expect(screen.getByText("İlk projeni oluştur, karelerin burada toplansın")).toBeTruthy();
  });
});

describe("ProjectsScreen deleting a project", () => {
  it("does not open the project when the bin is pressed, it asks first", async () => {
    await openScreen();

    fireEvent.click(screen.getByLabelText("Projeyi sil"));

    expect(navigate).not.toHaveBeenCalled();
    expect(screen.getByText('"düğün" projesi silinsin mi?')).toBeTruthy();
    expect(deleteProject).not.toHaveBeenCalled();
  });

  it("deletes the project and refreshes the list once confirmed", async () => {
    await openScreen();
    deleteProject.mockResolvedValue(null);
    listProjects.mockResolvedValue([]);

    fireEvent.click(screen.getByLabelText("Projeyi sil"));
    await act(async () => { fireEvent.click(screen.getByText("Sil")); });

    expect(deleteProject).toHaveBeenCalledWith("düğün");
    expect(listProjects).toHaveBeenCalledTimes(2);
    expect(screen.queryByText("düğün")).toBeNull();
  });

  it("draws the bin as a red icon and nothing else: no box of its own", async () => {
    await openScreen();

    const bin = screen.getByLabelText("Projeyi sil");
    expect(bin.style.color).toBe("var(--danger)");
    // border:none expands, and the part that decides whether a line is drawn is the style.
    expect(bin.style.borderStyle).toBe("none");
    expect(bin.style.background).toBe("none");
  });

  it("says what leaves with the project and what happens to the production", async () => {
    await openScreen();

    fireEvent.click(screen.getByLabelText("Projeyi sil"));

    expect(screen.getByText(
      "İçindeki tüm kareler — fotoğraf, video ve ses dosyalarıyla birlikte — kalıcı olarak "
      + "silinir. Çalışan üretim durdurulur, kuyruktaki işler atılır. Bu işlem geri alınamaz."))
      .toBeTruthy();
  });

  it("opens the project when the card is clicked", async () => {
    await openScreen();

    fireEvent.click(screen.getByText("düğün"));

    expect(navigate).toHaveBeenCalledWith(`/projects/${encodeURIComponent("düğün")}`);
  });
});
