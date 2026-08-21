import { readFileSync } from "node:fs";

import { act, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { navigate } from "../../shared/router.js";
import Gallery from "./Gallery.jsx";

vi.mock("../../shared/api.js", () => ({
  fileUrl: (project, file) => `/photos/${project}/${file}`,
}));
vi.mock("../../shared/router.js", () => ({
  navigate: vi.fn(),
  photoPath: (project, file) => `/projects/${encodeURIComponent(project)}/photos/${file}`,
}));

// What the server answers with: a frame's identity and status, plus which of its layers are still
// owed and which blew up. The identity is what the gallery keys everything by; the file is only
// what it shows. These fixtures name a frame after its own picture, which is the ordinary case --
// the copy frames that break the tie have their own tests.
const idOf = (file) => file.replace(".png", "");
const done = (file, extra = {}) => ({ id: idOf(file), file, status: "done", ...extra });
const pending = (file, extra = {}) => ({ id: idOf(file), file, status: "pending",
                                         owed: ["photo"], ...extra });
const broken = (file, extra = {}) => ({ id: idOf(file), file, status: "failed",
                                        failed: ["photo"], ...extra });
const FRAMES = [done("2_a.png"), done("1_a.png"), done("0_a.png")];
const withVideo = (file, extra = {}) => done(file, {
  layers: { photo: file, video: file.replace(".png", "_V1_0.mp4") }, ...extra,
});

beforeEach(() => {
  vi.clearAllMocks();
});

// jsdom has no DataTransfer, so the component must not depend on one: it tracks the dragged tile
// in its own state, which is also what makes the drop slot possible.
//
// Tiles are found by the file the test is talking about; the grid keys them by identity, and these
// fixtures name a frame after its own picture.
function tileOf(name) {
  return document.getElementById(`tile-${idOf(name)}`);
}

function checkOf(name) {
  return tileOf(name).querySelector("[data-check]");
}

// What the user actually presses is the photo, which is a link -- clicking the tile's padding
// would miss the very handler that has to know about selection mode.
function photoOf(name) {
  return tileOf(name).querySelector("a");
}

function renderGallery(props) {
  return render(
    <Gallery project="düğün" frames={FRAMES} current={null} onReorder={() => {}}
             onDelete={() => Promise.resolve()} {...props} />,
  );
}

function dragTile(fromName, toName) {
  fireEvent.dragStart(tileOf(fromName));
  fireEvent.dragOver(tileOf(toName));
  fireEvent.drop(tileOf(toName));
}

describe("Gallery — the empty project", () => {
  it("points at the button by the name the button actually carries", () => {
    renderGallery({ frames: [] });

    expect(screen.getByText("henüz kare yok")).toBeTruthy();
    expect(screen.getByText(
      "Prompt'ları yaz, Kuyruğa ekle'ye bas — kareler burada belirecek",
    )).toBeTruthy();
  });
});

describe("Gallery ordering", () => {
  it("counts the badge up from the bottom, so the newest frame carries the largest number", () => {
    renderGallery();

    expect(tileOf("2_a.png").textContent).toContain("3");
    expect(tileOf("1_a.png").textContent).toContain("2");
    expect(tileOf("0_a.png").textContent).toContain("1");
  });

  it("reports the new order when a frame is dropped", () => {
    const onReorder = vi.fn();
    renderGallery({ onReorder });

    dragTile("0_a.png", "2_a.png");

    expect(onReorder).toHaveBeenCalledWith(["0_a", "2_a", "1_a"]);
  });

  it("does not go to the server for a frame dropped where it already was", () => {
    const onReorder = vi.fn();
    renderGallery({ onReorder });

    dragTile("1_a.png", "1_a.png");

    expect(onReorder).not.toHaveBeenCalled();
  });

  it("goes to the detail page when a frame is clicked", () => {
    renderGallery();

    const link = tileOf("2_a.png").querySelector("a");
    expect(link.getAttribute("href")).toBe(
      `/projects/${encodeURIComponent("düğün")}/photos/2_a`);
  });

});

describe("Gallery — dragging a selection", () => {
  // Five, not three: a scattered selection needs cards left standing between its members, and with
  // three there is only one such card.
  const FIVE = [done("4_a.png"), done("3_a.png"), done("2_a.png"), done("1_a.png"),
                done("0_a.png")];

  function selectAll(...names) {
    names.forEach((name) => fireEvent.click(checkOf(name)));
  }

  it("takes the whole selection along when one of its cards is dragged", () => {
    const onReorder = vi.fn();
    renderGallery({ frames: FIVE, onReorder });
    selectAll("4_a.png", "3_a.png");

    dragTile("4_a.png", "2_a.png");

    expect(onReorder).toHaveBeenCalledWith(["2_a", "1_a", "4_a", "3_a", "0_a"]);
  });

  it("keeps the block in the gallery's order, not the order it was clicked in", () => {
    // The selection is a list of presses; the sequence is the gallery's. Reading the presses would
    // reverse a block whenever the user picked its cards from the bottom up.
    const onReorder = vi.fn();
    renderGallery({ frames: FIVE, onReorder });
    selectAll("0_a.png", "4_a.png");

    dragTile("4_a.png", "2_a.png");

    expect(onReorder).toHaveBeenCalledWith(["3_a", "2_a", "4_a", "0_a", "1_a"]);
  });

  it("gathers a scattered selection where it was dropped and closes the gap behind it", () => {
    const onReorder = vi.fn();
    renderGallery({ frames: FIVE, onReorder });
    selectAll("4_a.png", "2_a.png", "0_a.png");

    dragTile("4_a.png", "3_a.png");

    expect(onReorder).toHaveBeenCalledWith(["3_a", "4_a", "2_a", "0_a", "1_a"]);
  });

  it("moves only the card that was dragged when it is not in the selection", () => {
    const onReorder = vi.fn();
    renderGallery({ frames: FIVE, onReorder });
    selectAll("4_a.png", "3_a.png");

    dragTile("0_a.png", "2_a.png");

    expect(onReorder).toHaveBeenCalledWith(["4_a", "3_a", "0_a", "2_a", "1_a"]);
  });

  it("leaves the selection where it was when an unselected card is dragged", () => {
    renderGallery({ frames: FIVE });
    selectAll("4_a.png", "3_a.png");

    dragTile("0_a.png", "2_a.png");

    expect(screen.getByText("2 seçili")).toBeTruthy();
  });

  it("lets a card be picked up at all while frames are selected", () => {
    // Until now dragging was switched off for the whole gallery as soon as anything was selected,
    // which is the reason the sequence could not be moved without breaking the selection first.
    renderGallery({ frames: FIVE });
    selectAll("4_a.png");

    expect(tileOf("4_a.png").getAttribute("draggable")).toBe("true");
  });

  it("puts the dragged look on every card in the block", () => {
    renderGallery({ frames: FIVE });
    selectAll("4_a.png", "3_a.png");

    fireEvent.dragStart(tileOf("4_a.png"));

    expect(tileOf("3_a.png").style.transform).toContain("rotate(-3deg)");
    expect(tileOf("2_a.png").style.transform).toBe("");
  });

  it("adds nothing to the screen while the block is moving", () => {
    // No count badge, no stack, no ghost card: the design asks for the single-card effect applied
    // to the selection and nothing more.
    renderGallery({ frames: FIVE });
    selectAll("4_a.png", "3_a.png");
    const before = document.querySelectorAll("[data-tile]").length;

    fireEvent.dragStart(tileOf("4_a.png"));

    expect(document.querySelectorAll("[data-tile]").length).toBe(before);
  });

  it("does not go to the server when the block lands where it already was", () => {
    // from and to differ here -- the second card of the block was dropped on the first -- and the
    // sequence still comes out unchanged. Comparing indices would miss it.
    const onReorder = vi.fn();
    renderGallery({ frames: FIVE, onReorder });
    selectAll("4_a.png", "3_a.png");

    dragTile("3_a.png", "4_a.png");

    expect(onReorder).not.toHaveBeenCalled();
  });
});

describe("Gallery — one sequence, four states", () => {
  const MIXED = [
    pending("4_a.png"),
    pending("3_a.png"),                       // this one is the live worker's
    broken("2_a.png"),
    done("1_a.png"),
    done("0_a.png"),
  ];

  const pillOf = (name) => tileOf(name).querySelector("[data-pill]");

  it("says the layer and the state in one pill, in the corner", () => {
    renderGallery({ frames: MIXED, current: "3_a", running: true });

    expect(pillOf("4_a.png").textContent).toBe("foto kuyrukta");
    expect(pillOf("3_a.png").textContent).toBe("foto üretiliyor");
    expect(pillOf("2_a.png").textContent).toBe("foto hata");
  });

  it("writes a waiting frame's label in the brightest ink there is", () => {
    // 9px over a photograph: the palette's third grey is not a quiet label there, it is one nobody
    // can read. The other two states carry their own bright colours already.
    renderGallery({ frames: MIXED, current: "3_a" });

    expect(pillOf("4_a.png").style.color).toBe("var(--ink)");
    expect(pillOf("3_a.png").style.color).toBe("var(--accent)");
    expect(pillOf("2_a.png").style.color).toBe("var(--danger)");
  });

  it("puts the state pill in the top left, where the design asks for it", () => {
    // It used to sit at the bottom because the select ring owned this corner and appeared under
    // the pointer, so the pill had to get out of the way. The ring moved to the other side
    // (2026-08-13), and the corner is the pill's again.
    renderGallery({ frames: MIXED, current: "3_a", running: true });

    expect(pillOf("4_a.png").style.top).toBe("6px");
    expect(pillOf("4_a.png").style.left).toBe("6px");
    expect(pillOf("4_a.png").style.bottom).toBe("");
  });

  const badgeOf = (name) => tileOf(name).querySelector(".qe-badge");

  it("puts the select ring in the top right, opposite the pill", () => {
    renderGallery({ frames: MIXED, current: "3_a", running: true });

    expect(checkOf("4_a.png").style.top).toBe("6px");
    expect(checkOf("4_a.png").style.right).toBe("6px");
    expect(checkOf("4_a.png").style.left).toBe("");
  });

  it("leaves the order badge in the top right and gives it a name to be hidden by", () => {
    // The ring lands on the badge's corner, so one of them has to give way. The badge does -- what
    // is being looked at while picking frames is the pictures, not the numbering.
    renderGallery({ frames: MIXED, current: "3_a", running: true });

    expect(badgeOf("4_a.png").style.top).toBe("6px");
    expect(badgeOf("4_a.png").style.right).toBe("6px");
  });

  it("hides the number wherever the stylesheet shows the ring", () => {
    // A text check, and it says so: jsdom applies no stylesheet, so this catches the rule being
    // deleted, not the rule being wrong. The ring appears on hover and in selection mode, and the
    // number has to leave in both -- otherwise they sit on top of each other.
    // Read off disk, relative to the project vitest was started in. Importing it would hand back
    // an empty stub -- vitest does not process CSS, and ?raw does not escape that. A wrong path
    // throws here rather than passing quietly.
    const css = readFileSync("src/shared/app.css", "utf-8");

    expect(css).toMatch(/\.qe-tile:hover \.qe-badge/);
    expect(css).toMatch(/\.qe-tile--selecting \.qe-badge/);
  });

  it("does not move the pill when the selection mode opens", () => {
    // The whole point of the new layout: something appearing is not something moving, so nothing
    // in the card shifts under the pointer.
    renderGallery({ frames: MIXED, current: null });
    const before = pillOf("4_a.png").style.top;

    fireEvent.click(checkOf("4_a.png"));

    expect(pillOf("4_a.png").style.top).toBe(before);
    expect(pillOf("4_a.png").style.top).toBe("6px");
  });

  it("gives a produced frame no pill -- the photo is the answer", () => {
    renderGallery({ frames: MIXED, current: "3_a" });

    expect(pillOf("1_a.png")).toBeNull();
  });

  it("never puts two pills on one frame", () => {
    renderGallery({ frames: MIXED, current: "3_a" });

    for (const frame of MIXED) {
      expect(tileOf(frame.file).querySelectorAll("[data-pill]").length).toBeLessThan(2);
    }
  });

  it("keeps every frame in its own place whatever became of it", () => {
    renderGallery({ frames: MIXED, current: "3_a" });

    const sequence = [...document.querySelectorAll("[data-tile]")]
      .map((tile) => tile.id.slice("tile-".length));
    expect(sequence).toEqual(["4_a", "3_a", "2_a", "1_a", "0_a"]);
  });

  it("badges the waiting and failed frames too, from the same sequence", () => {
    renderGallery({ frames: MIXED, current: "3_a" });

    expect(tileOf("4_a.png").textContent).toContain("5");
    expect(tileOf("2_a.png").textContent).toContain("3");
    expect(tileOf("0_a.png").textContent).toContain("1");
  });

  it("draws a failed frame once, red, with its own way back", () => {
    const onRetry = vi.fn();
    renderGallery({ frames: MIXED, current: null, onRetry });

    // Once: not a red tile and a dashed one at the same time. Nothing is flowing here, so the two
    // waiting frames say so.
    expect(screen.getAllByText("foto bekliyor")).toHaveLength(2);
    fireEvent.click(screen.getByText("Tekrar dene"));

    expect(onRetry).toHaveBeenCalledWith("2_a");
  });

  it("turns the frame the worker is holding into a spinner without moving it", () => {
    renderGallery({ frames: MIXED, current: "3_a", running: true });

    // Four of the five are not photos; only the one the worker holds leaves the waiting pill.
    expect(screen.getAllByText("foto kuyrukta")).toHaveLength(1);
    expect(tileOf("3_a.png").textContent).toContain("4");
  });

  it("does not claim the gallery is empty when only waiting frames are in it", () => {
    renderGallery({ frames: [pending("0_a.png")] });

    expect(screen.queryByText("henüz kare yok")).toBeNull();
    expect(screen.getByText("foto bekliyor")).toBeTruthy();
  });

  it("calls a frame queued only while the queue is flowing", () => {
    renderGallery({ frames: [done("P0_0.png", { owed: ["video"] })], running: true });

    expect(pillOf("P0_0.png").textContent).toBe("video kuyrukta");
  });

  it("calls the same frame waiting once the queue has stopped", () => {
    // The debt is real: pressing Devam et still produces this video. What is not real is movement,
    // and "kuyrukta" claims movement -- which is what a stopped run looked like on 2026-08-13.
    renderGallery({ frames: [done("P0_0.png", { owed: ["video"] })], running: false });

    expect(pillOf("P0_0.png").textContent).toBe("video bekliyor");
  });

  it("leaves the middle of a waiting card wordless -- the dashed border says it", () => {
    renderGallery({ frames: MIXED, current: "3_a" });

    expect(screen.queryByText("bekliyor")).toBeNull();
  });

  it("leaves the rendering card to the spinner alone", () => {
    renderGallery({ frames: MIXED, current: "3_a" });

    expect(screen.queryByText("Çalışıyor")).toBeNull();
    expect(tileOf("3_a.png").querySelector(".wf-spinner")).toBeTruthy();
  });
});

describe("Gallery selection mode", () => {
  it("opens the mode and selects that frame when the ring is clicked", () => {
    renderGallery();

    fireEvent.click(checkOf("1_a.png"));

    expect(screen.getByText("1 seçili")).toBeTruthy();
    expect(navigate).not.toHaveBeenCalled();
  });

  it("selects and deselects in the mode without opening the detail page", () => {
    renderGallery();
    fireEvent.click(checkOf("1_a.png"));

    fireEvent.click(photoOf("2_a.png"));
    expect(screen.getByText("2 seçili")).toBeTruthy();

    fireEvent.click(photoOf("2_a.png"));
    expect(screen.getByText("1 seçili")).toBeTruthy();
    expect(navigate).not.toHaveBeenCalled();
  });

  it("selects everything, and clears the selection on a second press", () => {
    renderGallery();
    fireEvent.click(checkOf("1_a.png"));

    fireEvent.click(screen.getByText("Tümünü seç"));
    expect(screen.getByText("3 seçili")).toBeTruthy();

    fireEvent.click(screen.getByText("Tümünü seç"));
    // The bar belongs to a selection: with nothing selected it has nothing to say.
    expect(screen.queryByText("0 seçili")).toBeNull();
    expect(screen.queryByText("Tümünü seç")).toBeNull();
  });

  it("closes the mode on cancel and on Esc", () => {
    const { unmount } = renderGallery();
    fireEvent.click(checkOf("1_a.png"));

    fireEvent.click(screen.getByText("Vazgeç"));
    expect(screen.queryByText("1 seçili")).toBeNull();
    unmount();

    renderGallery();
    fireEvent.click(checkOf("1_a.png"));
    fireEvent.keyDown(window, { key: "Escape" });
    expect(screen.queryByText("1 seçili")).toBeNull();
  });

  it("asks before deleting, then reports what was selected", async () => {
    const onDelete = vi.fn().mockResolvedValue(null);
    renderGallery({ onDelete });
    fireEvent.click(checkOf("1_a.png"));
    fireEvent.click(photoOf("0_a.png"));

    fireEvent.click(screen.getByText("Sil"));
    expect(screen.getByText("2 kare silinsin mi?")).toBeTruthy();
    // The shortest of the three: it keeps the standard width (madde 105).
    expect(screen.getByText("2 kare silinsin mi?").closest(".wf-card").style.width).toBe("320px");
    expect(onDelete).not.toHaveBeenCalled();

    // The modal's confirm is the second Sil on screen; the bar's is the first.
    await act(async () => { fireEvent.click(screen.getAllByText("Sil").at(-1)); });

    expect(onDelete).toHaveBeenCalledWith(["1_a", "0_a"]);
  });

  it("promises the layers that would go with the frames", () => {
    renderGallery({ frames: [withVideo("2_a.png"), withVideo("1_a.png",
      { layers: { photo: "1_a.png", video: "1_a_V1_0.mp4", audio: "1_a_V1_0_S1_0.wav" } }),
      done("0_a.png")] });
    fireEvent.click(checkOf("2_a.png"));
    fireEvent.click(photoOf("1_a.png"));

    fireEvent.click(screen.getByText("Sil"));

    expect(screen.getByText(
      "Karelerin videosu ve sesi de birlikte silinir (2 video · 1 ses). "
      + "Bu işlem geri alınamaz.")).toBeTruthy();
  });

  it("leaves out a layer nobody in the selection has", () => {
    renderGallery({ frames: [withVideo("2_a.png"), done("1_a.png"), done("0_a.png")] });
    fireEvent.click(checkOf("2_a.png"));

    fireEvent.click(screen.getByText("Sil"));

    // One frame, one kind: singular subject, and no "ses" clause for a sound nobody has.
    expect(screen.getByText(
      "Karenin videosu da birlikte silinir (1 video). Bu işlem geri alınamaz.")).toBeTruthy();
  });

  it("promises nothing extra when the frames are pictures and nothing else", () => {
    renderGallery();
    fireEvent.click(checkOf("1_a.png"));

    fireEvent.click(screen.getByText("Sil"));

    expect(screen.getByText("Bu işlem geri alınamaz.")).toBeTruthy();
    expect(screen.queryByText(/birlikte silinir/)).toBeNull();
  });

  it("does not count a layer that blew up", () => {
    renderGallery({ frames: [withVideo("2_a.png", { failed: ["video"] }), done("1_a.png"),
                             done("0_a.png")] });
    fireEvent.click(checkOf("2_a.png"));

    fireEvent.click(screen.getByText("Sil"));

    // The tile shows no video badge for it, so the window must not promise one either.
    expect(screen.queryByText(/birlikte silinir/)).toBeNull();
  });

  it("floats the selection bar clear of the bottom edge", () => {
    renderGallery();
    fireEvent.click(checkOf("1_a.png"));

    // Its own rail, not the window's floor: the bar hangs above the last row (madde 108).
    expect(screen.getByText("1 seçili").closest("[style*='sticky']").style.bottom).toBe("28px");
  });

  it("takes the bar away when the selection is emptied", () => {
    renderGallery();
    fireEvent.click(checkOf("1_a.png"));
    fireEvent.click(photoOf("1_a.png"));  // deselect: the bar goes, and so does the mode

    expect(screen.queryByText(/seçili/)).toBeNull();
  });

  // The mode is the selection: rings on the cards while there is one, nothing while there is not.
  // It used to outlive the selection, which left a gallery covered in rings and a bar that had
  // already gone -- no way to tell whether a selection was still open (2026-08-13).
  const inSelectMode = () => document.querySelectorAll(".qe-tile--selecting").length;

  it("puts the cards in selection mode as soon as one is picked", () => {
    renderGallery();

    fireEvent.click(checkOf("1_a.png"));

    expect(inSelectMode()).toBe(FRAMES.length);
  });

  it("takes the cards out of selection mode when the last one is let go", () => {
    renderGallery();
    fireEvent.click(checkOf("1_a.png"));

    fireEvent.click(checkOf("1_a.png"));

    expect(inSelectMode()).toBe(0);
  });

  it("takes the cards out of selection mode on cancel", () => {
    renderGallery();
    fireEvent.click(checkOf("1_a.png"));

    fireEvent.click(screen.getByText("Vazgeç"));

    expect(inSelectMode()).toBe(0);
  });

  it("takes the cards out of selection mode when the whole list is emptied", () => {
    // Emptying the selection has two doors -- letting the last card go, and the button that clears
    // the list -- and they are different lines of code.
    renderGallery();
    fireEvent.click(checkOf("1_a.png"));
    fireEvent.click(screen.getByText("Tümünü seç"));

    fireEvent.click(screen.getByText("Tümünü seç"));

    expect(inSelectMode()).toBe(0);
  });
});

describe("Gallery — copying a card", () => {
  const twins = (copies) => vi.fn().mockResolvedValue(copies);

  it("puts Kopyala in the bar, to the left of Sil", () => {
    renderGallery({ onCopy: twins(["C1_1_a"]) });
    fireEvent.click(checkOf("1_a.png"));

    const bar = screen.getByText("1 seçili").parentElement;
    // Trimmed: Sil carries its trash glyph, so its text starts with a space. What is being read
    // here is the order of the words, not the spacing around them.
    const words = [...bar.querySelectorAll("button")].map((one) => one.textContent.trim());
    expect(words).toEqual(["Tümünü seç", "Kopyala", "Sil", "Vazgeç"]);
  });

  it("draws no Kopyala when only frames that are not produced are selected", () => {
    renderGallery({ frames: [pending("2_a.png"), done("1_a.png")], onCopy: twins([]) });
    fireEvent.click(checkOf("2_a.png"));

    // Nothing in the selection owns a layer, so there is nothing to press (Fark 79).
    expect(screen.queryByText("Kopyala")).toBeNull();
    expect(screen.getByText("Sil")).toBeTruthy();
  });

  it("copies only the produced frames of a mixed selection", async () => {
    const onCopy = twins(["C1_1_a"]);
    renderGallery({ frames: [pending("2_a.png"), done("1_a.png")], onCopy });
    fireEvent.click(checkOf("2_a.png"));
    fireEvent.click(checkOf("1_a.png"));

    await act(async () => { fireEvent.click(screen.getByText("Kopyala")); });

    expect(onCopy).toHaveBeenCalledWith(["1_a"]);
  });

  it("moves the selection onto the twins", async () => {
    const onCopy = twins(["C1_1_a"]);
    renderGallery({ frames: [done("2_a.png"), done("C1_1_a.png"), done("1_a.png")], onCopy });
    fireEvent.click(checkOf("1_a.png"));

    await act(async () => { fireEvent.click(screen.getByText("Kopyala")); });

    // How the copy is noticed: no notification of its own (Fark 77).
    expect(screen.getByText("1 seçili")).toBeTruthy();
    expect(checkOf("C1_1_a.png").className).toContain("qe-check--on");
    expect(checkOf("1_a.png").className).not.toContain("qe-check--on");
  });

  it("copies with Ctrl + D as well as with the button", async () => {
    const onCopy = twins(["C1_1_a"]);
    renderGallery({ onCopy });
    fireEvent.click(checkOf("1_a.png"));

    await act(async () => { fireEvent.keyDown(window, { key: "d", ctrlKey: true }); });

    expect(onCopy).toHaveBeenCalledWith(["1_a"]);
  });

  it("takes Ctrl + D away from the browser", () => {
    renderGallery({ onCopy: twins(["C1_1_a"]) });
    fireEvent.click(checkOf("1_a.png"));

    // Left alone it opens the bookmark window, which is never what was meant over a selection.
    const taken = !fireEvent.keyDown(window, { key: "d", ctrlKey: true, cancelable: true });

    expect(taken).toBe(true);
  });

  it("leaves Ctrl + D alone while the confirm window is open", () => {
    const onCopy = twins(["C1_1_a"]);
    renderGallery({ onCopy });
    fireEvent.click(checkOf("1_a.png"));
    fireEvent.click(screen.getByText("Sil"));

    fireEvent.keyDown(window, { key: "d", ctrlKey: true });

    // The window owns the keyboard while it is up -- the same rule Esc follows.
    expect(onCopy).not.toHaveBeenCalled();
  });

  it("presses nothing when the shortcut is used on a selection with nothing to copy", () => {
    const onCopy = twins([]);
    renderGallery({ frames: [pending("2_a.png"), done("1_a.png")], onCopy });
    fireEvent.click(checkOf("2_a.png"));

    fireEvent.keyDown(window, { key: "d", ctrlKey: true });

    expect(onCopy).not.toHaveBeenCalled();
  });
});

describe("Gallery — selecting frames that are not photos yet", () => {
  const MIXED = [
    pending("4_a.png"),
    pending("3_a.png"),                       // the live worker is holding this one
    broken("2_a.png"),
    done("1_a.png"),
    done("0_a.png"),
  ];

  function renderMixed(props) {
    return renderGallery({ frames: MIXED, current: "3_a", ...props });
  }

  it("puts a ring on a waiting frame and none on the one being rendered", () => {
    renderMixed();

    expect(checkOf("4_a.png")).toBeTruthy();
    expect(checkOf("2_a.png")).toBeTruthy();
    expect(checkOf("3_a.png")).toBeNull();
  });

  it("counts a mixed selection as one number", () => {
    renderMixed();

    fireEvent.click(checkOf("4_a.png"));
    fireEvent.click(checkOf("1_a.png"));

    expect(screen.getByText("2 seçili")).toBeTruthy();
  });

  it("skips the frame being rendered when everything is selected", () => {
    renderMixed();
    fireEvent.click(checkOf("4_a.png"));

    fireEvent.click(screen.getByText("Tümünü seç"));

    expect(screen.getByText("4 seçili")).toBeTruthy();   // five frames, one is the worker's
  });

  it("asks about waiting frames without claiming anything is unrecoverable", () => {
    renderMixed();
    fireEvent.click(checkOf("4_a.png"));

    // The bar says "Sil" here too (madde 65); only the window that opens knows the difference.
    fireEvent.click(screen.getByText("Sil"));

    expect(screen.getByText("1 kare kuyruktan çıkarılsın mı?")).toBeTruthy();
    expect(screen.getByText("1 kare kuyruktan çıkarılsın mı?").closest(".wf-card").style.width)
      .toBe("400px");
    expect(screen.getByText(
      "Bu kareler üretilmeyecek. Üretilmiş karelere ve dosyalarına dokunulmaz.")).toBeTruthy();
    expect(screen.queryByText(/geri alınamaz/)).toBeNull();
    // What it does is still "Çıkar" -- nothing is deleted.
    expect(screen.getByText("Çıkar")).toBeTruthy();
  });

  it("says both halves in the title and leaves the window at that", () => {
    renderMixed();
    fireEvent.click(checkOf("4_a.png"));
    fireEvent.click(checkOf("1_a.png"));

    fireEvent.click(screen.getByText("Sil"));

    const title = screen.getByText("1 kare silinsin, 1 bekleyen kare kuyruktan çıkarılsın mı?");
    expect(title).toBeTruthy();
    // The longest of the three titles gets the widest window (madde 105).
    expect(title.closest(".wf-card").style.width).toBe("420px");
    // No explaining line at all in this one (karar 64): title and buttons, nothing else.
    expect(screen.queryByText(/kuyruktan çıkar\./)).toBeNull();
    expect(screen.queryByText(/geri alınamaz/)).toBeNull();
  });

  it("sends photos and waiting frames in the same request", async () => {
    const onDelete = vi.fn().mockResolvedValue(null);
    renderMixed({ onDelete });
    fireEvent.click(checkOf("4_a.png"));
    fireEvent.click(checkOf("1_a.png"));
    fireEvent.click(screen.getByText("Sil"));

    await act(async () => { fireEvent.click(screen.getAllByText("Sil").at(-1)); });

    expect(onDelete).toHaveBeenCalledWith(["4_a", "1_a"]);
  });
});

describe("Gallery — every frame opens its own detail page", () => {
  const MIXED = [
    pending("3_a.png"),
    pending("2_a.png"),                       // the live worker is holding this one
    broken("1_a.png"),
    done("0_a.png"),
  ];

  function renderMixed(props) {
    return renderGallery({ frames: MIXED, current: "2_a", ...props });
  }

  it("links a waiting frame to the same address a photo would have", () => {
    renderMixed();

    expect(photoOf("3_a.png").getAttribute("href")).toBe(
      `/projects/${encodeURIComponent("düğün")}/photos/3_a`);
    fireEvent.click(photoOf("3_a.png"));

    expect(navigate).toHaveBeenCalledWith(
      `/projects/${encodeURIComponent("düğün")}/photos/3_a`);
  });

  it("links the frame being rendered and the failed one too", () => {
    renderMixed();

    fireEvent.click(photoOf("2_a.png"));
    expect(navigate).toHaveBeenCalledWith(
      `/projects/${encodeURIComponent("düğün")}/photos/2_a`);

    fireEvent.click(photoOf("1_a.png"));
    expect(navigate).toHaveBeenCalledWith(
      `/projects/${encodeURIComponent("düğün")}/photos/1_a`);
  });

  it("selects a waiting frame instead of opening it while the mode is on", () => {
    renderMixed();
    fireEvent.click(checkOf("0_a.png"));

    fireEvent.click(photoOf("3_a.png"));

    expect(screen.getByText("2 seçili")).toBeTruthy();
    expect(navigate).not.toHaveBeenCalled();
  });

  it("retries a failed frame without opening its page", () => {
    const onRetry = vi.fn();
    renderMixed({ onRetry });

    fireEvent.click(screen.getByText("Tekrar dene"));

    expect(onRetry).toHaveBeenCalledWith("1_a");
    expect(navigate).not.toHaveBeenCalled();
  });
});

// The browser decides at mousedown whether a press may become a drag, so the only question worth
// asking is whether the tile is draggable BEFORE anything presses it. Arming it 250 ms later --
// which is what these tests used to check -- is a state the browser has already stopped looking
// for, and it is why the gallery could not be reordered at all (2026-08-14).
describe("Gallery — picking a tile up", () => {
  it("offers a tile to the drag before anything has touched it", () => {
    renderGallery();

    expect(tileOf("1_a.png").draggable).toBe(true);
  });

  it("does not make a press part of the gesture", () => {
    renderGallery();

    fireEvent.mouseDown(tileOf("1_a.png"));

    // Pressing wins the tile nothing it did not already have: that is how this says there is no
    // step between the press and the drag for a timer to sit in.
    expect(tileOf("1_a.png").draggable).toBe(true);
  });

  it("lifts a waiting frame too -- the drag is what decides when it is produced", () => {
    renderGallery({ frames: [pending("9_a.png"), done("0_a.png")] });

    expect(tileOf("9_a.png").draggable).toBe(true);
    expect(screen.queryByText("üretilince sıralanabilir")).toBeNull();
  });

  it("lifts a failed frame too", () => {
    renderGallery({ frames: [broken("9_a.png"), done("0_a.png")] });

    expect(tileOf("9_a.png").draggable).toBe(true);
  });

  it("lifts the frame the worker is holding, without asking it to stop", () => {
    renderGallery({ frames: [pending("9_a.png"), done("0_a.png")],
                    current: "9_a" });

    expect(tileOf("9_a.png").draggable).toBe(true);
  });

});

describe("Gallery — a layer that blew up", () => {
  const brokenVideo = withVideo("P0_0.png", { failed: ["video"] });

  it("offers the way back over the photo instead of covering it", () => {
    renderGallery({ frames: [brokenVideo], onRetry: () => {} });

    // The picture stays; the button rides an overlay that CSS only shows under the pointer.
    expect(screen.getByAltText("P0_0.png")).toBeTruthy();
    expect(tileOf("P0_0.png").querySelector("[data-veil]")).toBeTruthy();
    expect(screen.getByText("Tekrar dene")).toBeTruthy();
  });

  it("keeps the middle of an empty red card for its own button", () => {
    renderGallery({ frames: [broken("P0_0.png")], onRetry: () => {} });

    expect(tileOf("P0_0.png").querySelector("[data-veil]")).toBeNull();
    expect(screen.getByText("Tekrar dene")).toBeTruthy();
  });

  it("says the job went into the queue and refuses a second press", () => {
    const onRetry = vi.fn();
    renderGallery({ frames: [brokenVideo], onRetry });

    fireEvent.click(screen.getByText("Tekrar dene"));

    expect(onRetry).toHaveBeenCalledWith("P0_0");
    expect(screen.getByText("Kuyruğa eklendi").closest("button").disabled).toBe(true);
    fireEvent.click(screen.getByText("Kuyruğa eklendi"));
    expect(onRetry).toHaveBeenCalledTimes(1);
  });

  it("says the same thing on an empty red card", () => {
    const onRetry = vi.fn();
    renderGallery({ frames: [broken("P0_0.png")], onRetry });

    fireEvent.click(screen.getByText("Tekrar dene"));

    expect(screen.getByText("Kuyruğa eklendi").closest("button").disabled).toBe(true);
  });
});

describe("Gallery — what a frame owns", () => {
  it("marks a frame that has a video", () => {
    renderGallery({ frames: [withVideo("P0_0.png")] });

    expect(screen.getByText("video")).toBeTruthy();
    expect(document.querySelector("[data-glyph=play]")).toBeTruthy();
  });

  it("marks a frame that has a sound as well", () => {
    renderGallery({ frames: [withVideo("P0_0.png", {
      layers: { photo: "P0_0.png", video: "P0_0_V1_0.mp4", audio: "P0_0_V1_0_S1_0.wav" } })] });

    expect(screen.getByText("video")).toBeTruthy();
    expect(screen.getByText("ses")).toBeTruthy();
    expect(document.querySelector("[data-glyph=sound]")).toBeTruthy();
  });

  it("does not call a failed sound something the frame owns", () => {
    renderGallery({ frames: [withVideo("P0_0.png", {
      layers: { photo: "P0_0.png", video: "P0_0_V1_0.mp4", audio: "P0_0_V1_0_S1_0.wav" },
      failed: ["audio"] })] });

    expect(screen.getByText("video")).toBeTruthy();
    expect(screen.queryByText("ses")).toBeNull();
  });

  it("leaves a frame with no video unmarked", () => {
    renderGallery({ frames: [done("P0_0.png")] });

    expect(screen.queryByText("video")).toBeNull();
  });

  it("does not call a failed render a video the frame owns", () => {
    renderGallery({ frames: [withVideo("P0_0.png", { failed: ["video"] })] });

    expect(screen.queryByText("video")).toBeNull();
    expect(screen.getByText("video hata")).toBeTruthy();
  });

  it("marks a loop video with its own word", () => {
    renderGallery({ frames: [withVideo("P0_0.png", { modes: { video: "loop" } })] });

    expect(screen.getByText("loop")).toBeTruthy();
  });

  it("never shows both words on one frame", () => {
    // They share the corner: the badge is one row per layer, and loop takes the video row's word
    // rather than standing beside it.
    renderGallery({ frames: [withVideo("P0_0.png", { modes: { video: "loop" } })] });

    expect(screen.queryByText("video")).toBeNull();
  });

  it("leaves a video made the plain way saying video", () => {
    renderGallery({ frames: [withVideo("P0_0.png", { modes: { video: "standard" } })] });

    expect(screen.getByText("video")).toBeTruthy();
    expect(screen.queryByText("loop")).toBeNull();
  });

  it("adds the sound beside the loop, not instead of it", () => {
    renderGallery({ frames: [withVideo("P0_0.png", {
      layers: { photo: "P0_0.png", video: "P0_0_V1_0.mp4", audio: "P0_0_V1_0_S1_0.wav" },
      modes: { video: "loop" } })] });

    expect(screen.getByText("loop")).toBeTruthy();
    expect(screen.getByText("ses")).toBeTruthy();
  });

  it("says nothing about a loop video that blew up", () => {
    // A failed layer holds its slot but is not owned -- that tile is the pill's to speak for, and
    // the mode must not smuggle a word past that rule.
    renderGallery({ frames: [withVideo("P0_0.png", { modes: { video: "loop" },
                                                     failed: ["video"] })] });

    expect(screen.queryByText("loop")).toBeNull();
    expect(screen.queryByText("video")).toBeNull();
  });

  it("keeps the photo on screen while the video is queued", () => {
    renderGallery({ frames: [done("P0_0.png", { owed: ["video"] })], running: true });

    expect(screen.getByAltText("P0_0.png")).toBeTruthy();
    expect(screen.getByText("video kuyrukta")).toBeTruthy();
  });

  it("keeps the photo on screen while the video is being made", () => {
    renderGallery({ frames: [done("P0_0.png", { owed: ["video"] })],
                    current: "P0_0", currentLayer: "video" });

    expect(screen.getByAltText("P0_0.png")).toBeTruthy();
    expect(screen.getByText("video üretiliyor")).toBeTruthy();
  });

  it("still draws the loading holder while the photo itself is being made", () => {
    renderGallery({ frames: [pending("P0_0.png")],
                    current: "P0_0", currentLayer: "photo" });

    expect(screen.queryByAltText("P0_0.png")).toBeNull();
    expect(screen.getByText("foto üretiliyor")).toBeTruthy();
  });
});
