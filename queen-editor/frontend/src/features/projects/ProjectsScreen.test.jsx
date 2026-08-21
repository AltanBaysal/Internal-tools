import { act, fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { deleteProject, listProjects, renameProject } from "../../shared/api.js";
import { navigate } from "../../shared/router.js";
import ProjectsScreen from "./ProjectsScreen.jsx";

vi.mock("../../shared/api.js", () => ({
  checkProjectName: vi.fn().mockResolvedValue({ error: null }),
  createProject: vi.fn(),
  deleteProject: vi.fn(),
  listProjects: vi.fn(),
  renameProject: vi.fn(),
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

describe("ProjectsScreen renaming a project", () => {
  it("offers a pencil beside the bin", async () => {
    await openScreen();

    // Fark 1: the only way in. Neutral, not red -- renaming takes nothing away.
    const pencil = screen.getByLabelText("Projeyi yeniden adlandır");
    expect(pencil.style.color).not.toBe("var(--danger)");
  });

  it("opens the window on the name that is there, with the whole of it selected", async () => {
    await openScreen();

    fireEvent.click(screen.getByLabelText("Projeyi yeniden adlandır"));

    const box = screen.getByDisplayValue("düğün");
    // One keystroke replaces the name instead of landing next to it (fark 4).
    expect([box.selectionStart, box.selectionEnd]).toEqual([0, "düğün".length]);
    expect(navigate).not.toHaveBeenCalled();
  });

  it("draws the window at the measure and in the words the design gives it", async () => {
    await openScreen();

    fireEvent.click(screen.getByLabelText("Projeyi yeniden adlandır"));

    // Fark 4. One window drawn twice rather than two windows that have to be kept alike: the
    // heading, the button and the measure all come from whoever opened it.
    const title = screen.getByText("Projeyi yeniden adlandır", { selector: ".wf-hand" });
    expect(title.closest(".wf-card").style.width).toBe("380px");
    expect(screen.getByText("Kaydet")).toBeTruthy();
  });

  it("asks nothing before renaming: it takes nothing away", async () => {
    await openScreen();

    fireEvent.click(screen.getByLabelText("Projeyi yeniden adlandır"));

    // Fark 3: no confirm window, no red button, no bin inside it.
    expect(screen.queryByText("Sil")).toBeNull();
    expect(screen.getByText("Vazgeç")).toBeTruthy();
  });

  it("renames the project and reads the list again", async () => {
    await openScreen();
    renameProject.mockResolvedValue({ name: "nikah" });
    listProjects.mockResolvedValue([{ name: "nikah", modifiedAt: 1754300000 }]);

    fireEvent.click(screen.getByLabelText("Projeyi yeniden adlandır"));
    fireEvent.change(screen.getByDisplayValue("düğün"), { target: { value: "nikah" } });
    await act(async () => { fireEvent.click(screen.getByText("Kaydet")); });

    // Drive is the single source of truth here too: re-read rather than guess which card moved.
    expect(renameProject).toHaveBeenCalledWith("düğün", "nikah");
    expect(screen.getByText("nikah")).toBeTruthy();
  });

  it("says under the box when the name is already somebody's", async () => {
    await openScreen();
    renameProject.mockRejectedValue(new Error("Bu ad zaten kullanılıyor. Başka bir ad dene."));

    fireEvent.click(screen.getByLabelText("Projeyi yeniden adlandır"));
    fireEvent.change(screen.getByDisplayValue("düğün"), { target: { value: "nikah" } });
    await act(async () => { fireEvent.click(screen.getByText("Kaydet")); });

    // Fark 2: the field reddens and the sentence stands under it.
    expect(screen.getByText("Bu ad zaten kullanılıyor. Başka bir ad dene.")).toBeTruthy();
    expect(screen.getByDisplayValue("nikah").style.borderColor).toBe("var(--danger)");
  });

  it("takes the warning away again once the name is being typed", async () => {
    await openScreen();
    renameProject.mockRejectedValue(new Error("Bu ad zaten kullanılıyor. Başka bir ad dene."));

    fireEvent.click(screen.getByLabelText("Projeyi yeniden adlandır"));
    fireEvent.change(screen.getByDisplayValue("düğün"), { target: { value: "nikah" } });
    await act(async () => { fireEvent.click(screen.getByText("Kaydet")); });
    expect(screen.getByText("Bu ad zaten kullanılıyor. Başka bir ad dene.")).toBeTruthy();

    fireEvent.change(screen.getByDisplayValue("nikah"), { target: { value: "nikah töreni" } });

    expect(screen.queryByText("Bu ad zaten kullanılıyor. Başka bir ad dene.")).toBeNull();
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
