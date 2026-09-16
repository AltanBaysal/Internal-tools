import { act, fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import {
  archiveProject,
  deleteProject,
  listArchivedProjects,
  listProjects,
  renameProject,
  restoreProject,
} from "../../shared/api.js";
import { navigate } from "../../shared/router.js";
import ProjectsScreen from "./ProjectsScreen.jsx";

vi.mock("../../shared/api.js", () => ({
  archiveProject: vi.fn(),
  checkProjectName: vi.fn().mockResolvedValue({ error: null }),
  createProject: vi.fn(),
  deleteProject: vi.fn(),
  listArchivedProjects: vi.fn().mockResolvedValue([]),
  listProjects: vi.fn(),
  renameProject: vi.fn(),
  restoreProject: vi.fn(),
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

// The list at a given length. The names only have to be different from each other; what the test
// is looking at is the box they sit in.
async function openWith(count) {
  listProjects.mockResolvedValue(
    Array.from({ length: count }, (_, i) => ({ name: `p${i + 1}`, modifiedAt: 1754300000 })),
  );
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

describe("ProjectsScreen opening a new project", () => {
  it("opens the window at the one measure both windows share", async () => {
    await openScreen();

    fireEvent.click(screen.getByText("Yeni proje"));

    // Fark 6: 400 was the wider of two measures; there is only one now, and it belongs to the
    // window rather than to whoever opens it.
    const title = screen.getByText("Yeni proje", { selector: ".wf-hand" });
    expect(title.closest(".wf-card").style.width).toBe("380px");
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

describe("ProjectsScreen archiving a project", () => {
  it("offers archiving beside the pencil and the bin", async () => {
    await openScreen();

    // Neither red nor a question: archiving takes nothing away, it only moves the folder. The bin
    // keeps its mark by being the only one wearing it.
    const button = screen.getByLabelText("Projeyi arşivle");
    expect(button.style.color).not.toBe("var(--danger)");
  });

  it("archives without asking, and reads the list again", async () => {
    await openScreen();
    archiveProject.mockResolvedValue(null);
    listProjects.mockResolvedValue([]);

    await act(async () => { fireEvent.click(screen.getByLabelText("Projeyi arşivle")); });

    expect(archiveProject).toHaveBeenCalledWith("düğün");
    // Drive is the single source of truth: re-read rather than guess which card left.
    expect(listProjects).toHaveBeenCalledTimes(2);
    expect(navigate).not.toHaveBeenCalled();
  });

  it("opens the archive from the header and shows what is in it", async () => {
    await openScreen();
    listArchivedProjects.mockResolvedValue([{ name: "eski iş", modifiedAt: 1754300000 }]);

    await act(async () => { fireEvent.click(screen.getByText("Arşiv")); });

    expect(screen.getByText("eski iş")).toBeTruthy();
    // One list at a time: the archive is where the projects were, not beside them.
    expect(screen.queryByText("düğün")).toBeNull();
  });

  it("an archived card offers only the way back", async () => {
    await openScreen();
    listArchivedProjects.mockResolvedValue([{ name: "eski iş", modifiedAt: 1754300000 }]);

    await act(async () => { fireEvent.click(screen.getByText("Arşiv")); });

    expect(screen.getByLabelText("Projeyi geri al")).toBeTruthy();
    // Nothing is deleted or renamed from in here: it is out of the way, and that is all it is.
    expect(screen.queryByLabelText("Projeyi sil")).toBeNull();
    expect(screen.queryByLabelText("Projeyi yeniden adlandır")).toBeNull();
    expect(screen.queryByLabelText("Projeyi arşivle")).toBeNull();
  });

  it("restores and reads both lists again", async () => {
    await openScreen();
    listArchivedProjects.mockResolvedValue([{ name: "eski iş", modifiedAt: 1754300000 }]);
    await act(async () => { fireEvent.click(screen.getByText("Arşiv")); });
    restoreProject.mockResolvedValue(null);
    listArchivedProjects.mockResolvedValue([]);

    await act(async () => { fireEvent.click(screen.getByLabelText("Projeyi geri al")); });

    expect(restoreProject).toHaveBeenCalledWith("eski iş");
    expect(screen.queryByText("eski iş")).toBeNull();
  });

  it("says the archive is empty rather than showing the projects' own empty state", async () => {
    await openScreen();
    listArchivedProjects.mockResolvedValue([]);

    await act(async () => { fireEvent.click(screen.getByText("Arşiv")); });

    expect(screen.getByText("arşivde proje yok")).toBeTruthy();
    // The projects' empty state invites a first project, which is the wrong invitation here.
    expect(screen.queryByText("İlk projeni oluştur, karelerin burada toplansın")).toBeNull();
  });

  // Madde 224. The archive is a place that is entered, so its header is its own: nothing that makes
  // a project, and a way out worded the way every other place in this app words it.
  it("has no way to make a project from inside the archive", async () => {
    await openScreen();
    listArchivedProjects.mockResolvedValue([{ name: "eski iş", modifiedAt: 1754300000 }]);

    await act(async () => { fireEvent.click(screen.getByText("Arşiv")); });

    // Not disabled -- drawn at all it would say a project could be made here, and what it makes
    // lands among the projects rather than in the list being looked at.
    expect(screen.queryByText("Yeni proje")).toBeNull();
  });

  it("offers nothing to press in an empty archive either", async () => {
    // The projects' own empty state carries a create button, and this is where it would sneak in.
    await openScreen();
    listArchivedProjects.mockResolvedValue([]);

    await act(async () => { fireEvent.click(screen.getByText("Arşiv")); });

    expect(screen.queryByText("Yeni proje")).toBeNull();
    expect(screen.queryByText("İlk projeyi oluştur")).toBeNull();
  });

  it("is left the way every other place in this app is left", async () => {
    await openScreen();

    await act(async () => { fireEvent.click(screen.getByText("Arşiv")); });

    // The project screen's own word (Projeden çık). A toggle reads both ways; this is an exit.
    expect(screen.getByText("Arşivden çık")).toBeTruthy();
  });

  it("comes back to the projects when the way out is pressed", async () => {
    await openScreen();
    listArchivedProjects.mockResolvedValue([{ name: "eski iş", modifiedAt: 1754300000 }]);
    await act(async () => { fireEvent.click(screen.getByText("Arşiv")); });

    await act(async () => { fireEvent.click(screen.getByText("Arşivden çık")); });

    expect(screen.getByText("düğün")).toBeTruthy();
    expect(screen.queryByText("eski iş")).toBeNull();
  });

  // Madde 223. Every failure here was silent: neither handler caught, so the server's sentence
  // became an unhandled rejection and the user saw a button that did nothing at all.
  it("says what the server said when archiving fails", async () => {
    await openScreen();
    archiveProject.mockRejectedValue(new Error("Arşivde düğün adlı bir proje var."));

    await act(async () => { fireEvent.click(screen.getByLabelText("Projeyi arşivle")); });

    expect(screen.getByText("Arşivde düğün adlı bir proje var.")).toBeTruthy();
  });

  it("leaves the list where it is when archiving fails", async () => {
    // An action that failed is not a list that failed: taking the cards away would cost the user
    // the thing they were about to try again.
    await openScreen();
    archiveProject.mockRejectedValue(new Error("Arşivde düğün adlı bir proje var."));

    await act(async () => { fireEvent.click(screen.getByLabelText("Projeyi arşivle")); });

    expect(screen.getByText("düğün")).toBeTruthy();
  });

  it("says what the server said when restoring fails", async () => {
    await openScreen();
    listArchivedProjects.mockResolvedValue([{ name: "eski iş", modifiedAt: 1754300000 }]);
    await act(async () => { fireEvent.click(screen.getByText("Arşiv")); });
    restoreProject.mockRejectedValue(new Error("Bu ad zaten kullanılıyor. Başka bir ad dene."));

    await act(async () => { fireEvent.click(screen.getByLabelText("Projeyi geri al")); });

    expect(screen.getByText("Bu ad zaten kullanılıyor. Başka bir ad dene.")).toBeTruthy();
  });

  it("clears the sentence once something works", async () => {
    await openScreen();
    archiveProject.mockRejectedValueOnce(new Error("Arşivde düğün adlı bir proje var."));
    await act(async () => { fireEvent.click(screen.getByLabelText("Projeyi arşivle")); });
    // There first, or the question below answers itself.
    expect(screen.getByText("Arşivde düğün adlı bir proje var.")).toBeTruthy();
    archiveProject.mockResolvedValue(null);
    listProjects.mockResolvedValue([]);

    await act(async () => { fireEvent.click(screen.getByLabelText("Projeyi arşivle")); });

    expect(screen.queryByText("Arşivde düğün adlı bir proje var.")).toBeNull();
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

  it("draws the bin in the clothes every destructive button in the app wears", async () => {
    await openScreen();

    // Fark 5, karar 1: the design's own texts disagreed -- the rules document counts project
    // delete among the destructive standard's examples, the card drawing shows a bare icon. The
    // rules document won. Unfilled, red border, red icon.
    const bin = screen.getByLabelText("Projeyi sil");
    expect(bin.style.borderColor).toBe("var(--danger)");
    expect(bin.style.color).toBe("var(--danger)");
    expect(bin.style.background).toBe("none");
    expect(bin.querySelector("svg")).toBeTruthy();
  });

  it("leaves the pencil beside it without a line of its own", async () => {
    await openScreen();

    // Karar 43: the red frame is a mark, and a mark only marks while the thing next to it has
    // none. Ghost draws nothing but keeps the box, so the two sit level.
    const pencil = screen.getByLabelText("Projeyi yeniden adlandır");
    expect(pencil.className).toContain("wf-btn--ghost");
    expect(pencil.style.color).not.toBe("var(--danger)");
    expect(pencil.style.borderColor).not.toBe("var(--danger)");
  });

  it("says what happens to the production first, then what leaves with the project", async () => {
    await openScreen();

    fireEvent.click(screen.getByLabelText("Projeyi sil"));

    // Fark 9: the sentences are the same, their order is not. What is running stops first.
    expect(screen.getByText(
      "Çalışan üretim durdurulur, kuyruktaki işler atılır. İçindeki tüm kareler — fotoğraf, video "
      + "ve ses dosyalarıyla birlikte — kalıcı olarak silinir. Bu işlem geri alınamaz."))
      .toBeTruthy();
  });

  it("opens the project when the card is clicked", async () => {
    await openScreen();

    fireEvent.click(screen.getByText("düğün"));

    expect(navigate).toHaveBeenCalledWith(`/projects/${encodeURIComponent("düğün")}`);
  });
});

describe("ProjectsScreen with a long list", () => {
  it("scrolls the list in its own box rather than the page", async () => {
    await openWith(12);

    // Fark 8, karar 44: the header stays put and the projects move under it -- the way the app's
    // other four screens are built. The 2026-08-09 decision that the page scrolls was given
    // against a design that drew no handle at all.
    expect(document.querySelector("[data-list]").style.overflowY).toBe("auto");
  });

  it("gives the list a handle of its own, a thin one", async () => {
    await openWith(12);

    // The rule is in app.css because it is a scrollbar pseudo-element; what the screen owes is the
    // class. Nothing is drawn while there is nothing to scroll, so the handle needs no condition
    // of its own (karar 45).
    expect(document.querySelector("[data-list]").className).toContain("qe-thin-scroll");
  });

  it("fades the foot of the list once it has passed eight", async () => {
    await openWith(9);

    // Karar 45: eight is two rows of four, and it is a count because the design gives a count --
    // measuring the overflow would mean a test that fakes layout.
    const fade = document.querySelector("[data-fade]");
    expect(fade).toBeTruthy();
    // A band nobody can see must not swallow the click meant for the card under it.
    expect(fade.style.pointerEvents).toBe("none");
  });

  it("fades nothing while eight still fit", async () => {
    await openWith(8);

    expect(document.querySelector("[data-fade]")).toBeNull();
  });
});
