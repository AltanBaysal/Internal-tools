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
  // The box the pills stand in. A frame can owe two layers, and the second label reads under the
  // first rather than beside it -- so the corner is a box of its own, not the pill's own position.
  const cornerOf = (name) => tileOf(name).querySelector("[data-corner]");

  it("says the layer and the state in one pill, in the corner", () => {
    renderGallery({ frames: MIXED, current: "3_a", running: true });

    expect(pillOf("4_a.png").textContent).toBe("foto kuyrukta");
    expect(pillOf("3_a.png").textContent).toBe("foto üretiliyor");
    expect(pillOf("2_a.png").textContent).toBe("foto hata");
  });

  it("writes a waiting frame's label in a quieter ink than the ones that carry a colour", () => {
    // The design's soft tone, read as the palette's second grey rather than its third: the badge in
    // the opposite corner already carries that one at this very size, so it is the faint tone whose
    // readability this card has already proved. The other two states say what they are in colour.
    renderGallery({ frames: MIXED, current: "3_a" });

    expect(pillOf("4_a.png").style.color).toBe("var(--ink-2)");
    expect(pillOf("3_a.png").style.color).toBe("var(--accent)");
    expect(pillOf("2_a.png").style.color).toBe("var(--danger)");
  });

  it("gives the label a lighter ground and more room inside it", () => {
    // Measure belongs to the mould and colour to the state: a stack of two must not show two
    // different grounds, so the ground and the padding change on every pill and the ink only on the
    // one the design speaks of. The digits are matched loosely -- what is fixed is the tone, not
    // how a browser spells it back.
    renderGallery({ frames: MIXED, current: "3_a" });

    expect(pillOf("4_a.png").style.background).toMatch(/10,\s*8,\s*7,\s*0?\.7\)/);
    expect(pillOf("4_a.png").style.padding).toBe("3px 7px");
  });

  it("puts the state pill in the top left, where the design asks for it", () => {
    // It used to sit at the bottom because the select ring owned this corner and appeared under
    // the pointer, so the pill had to get out of the way. The ring moved to the other side
    // (2026-08-13), and the corner is the pill's again. The corner is the box now, not the pill: a
    // frame can be waiting for two layers and both of them stand in it (Fark 64).
    renderGallery({ frames: MIXED, current: "3_a", running: true });

    expect(cornerOf("4_a.png").style.top).toBe("6px");
    expect(cornerOf("4_a.png").style.left).toBe("6px");
    expect(cornerOf("4_a.png").style.bottom).toBe("");
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
    const before = cornerOf("4_a.png").style.top;

    fireEvent.click(checkOf("4_a.png"));

    expect(cornerOf("4_a.png").style.top).toBe(before);
    expect(cornerOf("4_a.png").style.top).toBe("6px");
  });

  it("gives a produced frame no pill -- the photo is the answer", () => {
    renderGallery({ frames: MIXED, current: "3_a" });

    expect(pillOf("1_a.png")).toBeNull();
  });

  it("gives a frame that owes two layers a label for each", () => {
    renderGallery({ frames: [done("P0_0.png", { owed: ["video", "audio"] })], running: true });

    expect([...tileOf("P0_0.png").querySelectorAll("[data-pill]")].map((one) => one.textContent))
      .toEqual(["video kuyrukta", "ses kuyrukta"]);
  });

  it("stacks the second label under the first", () => {
    // In the queue's own order, which is the order owed already comes in: the labels read the way
    // the work will happen.
    renderGallery({ frames: [done("P0_0.png", { owed: ["video", "audio"] })], running: true });

    expect(cornerOf("P0_0.png").style.flexDirection).toBe("column");
    expect(cornerOf("P0_0.png").querySelectorAll("[data-pill]")).toHaveLength(2);
  });

  it("says one thing while a layer is being made, however much is still owed", () => {
    // Only the debt became a list. What the worker is holding is one job, and a card naming it
    // beside two more would bury the picture under it.
    renderGallery({ frames: [done("P0_0.png", { owed: ["video", "audio"] })],
                    current: "P0_0", currentLayer: "video", running: true });

    expect([...tileOf("P0_0.png").querySelectorAll("[data-pill]")].map((one) => one.textContent))
      .toEqual(["video üretiliyor"]);
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

  it("narrows the space between the bar's items", () => {
    renderGallery();
    fireEvent.click(checkOf("1_a.png"));

    // Six buttons now, and 14 was a bar with three (Fark 83).
    expect(screen.getByText("1 seçili").parentElement.style.gap).toBe("10px");
  });

  it("keeps every button's words on one line", () => {
    renderGallery();
    fireEvent.click(checkOf("1_a.png"));

    // Whether the bar really fits on one line is a question jsdom cannot answer -- it computes no
    // layout. What it can hold is the rule that keeps a label from breaking in two, and that also
    // stops a flex item shrinking below its own text.
    expect(screen.getByText("1 seçili").parentElement.style.whiteSpace).toBe("nowrap");
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

describe("Gallery — taking a layer off many frames", () => {
  // A frame that carries all three layers. withVideo spreads its extra after its own map, so this
  // replaces that map rather than adding to it.
  const withSound = (file) => withVideo(file, {
    layers: { photo: file, video: file.replace(".png", "_V1_0.mp4"),
              audio: file.replace(".png", "_V1_0_S1_0.wav") },
  });
  // Three frames, three answers to "does it carry this layer": both, video only, neither.
  const MIXED = [withSound("2_a.png"), withVideo("1_a.png"), done("0_a.png")];
  const remover = () => vi.fn().mockResolvedValue({ deleted: [] });

  function pick(...names) {
    names.forEach((name) => fireEvent.click(checkOf(name)));
  }

  it("puts the two layer buttons to the right of Sil", () => {
    renderGallery({ frames: MIXED, onCopy: vi.fn(), onRemoveLayer: remover() });
    pick("2_a.png");

    const bar = screen.getByText("1 seçili").parentElement;
    const words = [...bar.querySelectorAll("button")].map((one) => one.textContent.trim());
    expect(words).toEqual(["Tümünü seç", "Kopyala", "Sil", "Videoları sil", "Sesleri sil",
                           "Vazgeç"]);
  });

  it("draws no Videoları sil when nothing selected carries a video", () => {
    renderGallery({ frames: MIXED, onRemoveLayer: remover() });
    pick("0_a.png");

    // A window asking about 0 frames is not a window, so the button is simply not there.
    expect(screen.queryByText("Videoları sil")).toBeNull();
    expect(screen.queryByText("Sesleri sil")).toBeNull();
  });

  it("draws no Sesleri sil when nothing selected carries a sound", () => {
    renderGallery({ frames: MIXED, onRemoveLayer: remover() });
    pick("1_a.png");

    expect(screen.getByText("Videoları sil")).toBeTruthy();
    expect(screen.queryByText("Sesleri sil")).toBeNull();
  });

  it("counts only the frames that carry the layer", () => {
    renderGallery({ frames: MIXED, onRemoveLayer: remover() });
    pick("2_a.png", "1_a.png", "0_a.png");

    fireEvent.click(screen.getByText("Videoları sil"));

    expect(screen.getByText("2 karenin videosu silinsin mi?")).toBeTruthy();
  });

  it("names the frames it will skip", () => {
    renderGallery({ frames: MIXED, onRemoveLayer: remover() });
    pick("2_a.png", "1_a.png", "0_a.png");

    fireEvent.click(screen.getByText("Videoları sil"));

    // First, because it is what explains the number in the title.
    expect(screen.getByText(
      "Seçili 3 kareden videosu olmayan 1 kare atlanır. "
      + "Kareler ve fotoğrafları kalır. Videoya bindirilen sesler de gider.")).toBeTruthy();
  });

  it("says nothing about skipping when every selected frame carries the layer", () => {
    renderGallery({ frames: MIXED, onRemoveLayer: remover() });
    pick("2_a.png", "1_a.png");

    fireEvent.click(screen.getByText("Videoları sil"));

    expect(screen.queryByText(/atlanır/)).toBeNull();
  });

  it("promises the video stays when the sound is the one going", () => {
    renderGallery({ frames: MIXED, onRemoveLayer: remover() });
    pick("2_a.png");

    fireEvent.click(screen.getByText("Sesleri sil"));

    expect(screen.getByText("1 karenin sesi silinsin mi?")).toBeTruthy();
    expect(screen.getByText("Kareler, fotoğrafları ve videoları kalır.")).toBeTruthy();
  });

  it("sends only the frames that carry the layer", async () => {
    const onRemoveLayer = remover();
    renderGallery({ frames: MIXED, onRemoveLayer });
    pick("2_a.png", "1_a.png", "0_a.png");

    fireEvent.click(screen.getByText("Videoları sil"));
    // The window's own Sil is the last one on screen; the bar's is the first.
    await act(async () => { fireEvent.click(screen.getAllByText("Sil").at(-1)); });

    expect(onRemoveLayer).toHaveBeenCalledWith(["2_a", "1_a"], "video");
  });

  it("sends nothing when the window is cancelled", () => {
    const onRemoveLayer = remover();
    renderGallery({ frames: MIXED, onRemoveLayer });
    pick("2_a.png");

    fireEvent.click(screen.getByText("Videoları sil"));
    // The window's own Vazgeç, not the bar's -- what is being cancelled is the deletion, and the
    // selection behind it stays.
    fireEvent.click(screen.getAllByText("Vazgeç").at(-1));

    expect(onRemoveLayer).not.toHaveBeenCalled();
    expect(screen.queryByText("1 karenin videosu silinsin mi?")).toBeNull();
  });

  it("closes the selection once the layer is gone", async () => {
    renderGallery({ frames: MIXED, onRemoveLayer: remover() });
    pick("2_a.png", "1_a.png");

    fireEvent.click(screen.getByText("Videoları sil"));
    await act(async () => { fireEvent.click(screen.getAllByText("Sil").at(-1)); });

    expect(screen.queryByText("2 seçili")).toBeNull();
  });

  it("does not count a video that blew up", () => {
    // The tile shows no video badge for a red layer, and the window has to agree with the tile.
    renderGallery({ frames: [withVideo("2_a.png"), withVideo("1_a.png", { failed: ["video"] })],
                    onRemoveLayer: remover() });
    pick("2_a.png", "1_a.png");

    fireEvent.click(screen.getByText("Videoları sil"));

    expect(screen.getByText("1 karenin videosu silinsin mi?")).toBeTruthy();
    expect(screen.getByText(/videosu olmayan 1 kare atlanır/)).toBeTruthy();
  });

  it("draws no layer buttons while a frame that is not produced is in the selection", () => {
    // What these two take off is a finished stack, and the queue is still writing into that one.
    renderGallery({ frames: [withSound("2_a.png"), pending("1_a.png")],
                    onRemoveLayer: remover() });
    pick("2_a.png", "1_a.png");

    expect(screen.queryByText("Videoları sil")).toBeNull();
    expect(screen.queryByText("Sesleri sil")).toBeNull();
    // The frames themselves can still go, and the produced one can still be copied.
    expect(screen.getByText("Sil")).toBeTruthy();
    expect(screen.getByText("Kopyala")).toBeTruthy();
  });

  it("leaves three buttons in the bar when only frames that are not produced are selected", () => {
    renderGallery({ frames: [pending("2_a.png"), pending("1_a.png")],
                    onCopy: vi.fn(), onRemoveLayer: remover() });
    pick("2_a.png");

    const bar = screen.getByText("1 seçili").parentElement;
    const words = [...bar.querySelectorAll("button")].map((one) => one.textContent.trim());
    expect(words).toEqual(["Tümünü seç", "Sil", "Vazgeç"]);
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

  it("brings the veil down in the app's own brown black", () => {
    // The tone every other label on this card already stands on, rather than a pure black that
    // belongs to no palette here. Only the tone changes; how much of the photo shows through does
    // not.
    renderGallery({ frames: [brokenVideo], onRetry: () => {} });

    expect(tileOf("P0_0.png").querySelector("[data-veil]").style.background)
      .toMatch(/10,\s*8,\s*7/);
  });

  it("stands the way back on the card's own ground", () => {
    renderGallery({ frames: [brokenVideo], onRetry: () => {} });

    expect(screen.getByText("Tekrar dene").closest("button").style.background).toBe("var(--bg-2)");
  });

  it("leaves the button on an empty red card without one", () => {
    // The ground belongs to the veil's button alone: this one already stands on a card of its own,
    // and a second ground would be a box drawn inside a box.
    renderGallery({ frames: [broken("P0_0.png")], onRetry: () => {} });

    expect(screen.getByText("Tekrar dene").closest("button").style.background).toBe("transparent");
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
  const ownsOf = (name) => tileOf(name).querySelector("[data-owns]");
  const badgesOf = (name) => [...tileOf(name).querySelectorAll("[data-own]")];
  const HAS_BOTH = withVideo("P0_0.png", {
    layers: { photo: "P0_0.png", video: "P0_0_V1_0.mp4", audio: "P0_0_V1_0_S1_0.wav" } });

  it("marks a frame that has a video", () => {
    renderGallery({ frames: [withVideo("P0_0.png")] });

    expect(screen.getByText("video")).toBeTruthy();
  });

  it("marks a frame that has a sound as well", () => {
    renderGallery({ frames: [HAS_BOTH] });

    expect(screen.getByText("video")).toBeTruthy();
    expect(screen.getByText("ses")).toBeTruthy();
  });

  it("puts what the frame owns in the bottom left, and leaves the corner across from it empty",
     () => {
       // Four corners, four meanings: the state pill top left, the number and the select ring top
       // right, what the frame owns bottom left. The fourth is left empty on purpose, so no two of
       // them ever land on each other.
       renderGallery({ frames: [withVideo("P0_0.png")] });

       expect(ownsOf("P0_0.png").style.bottom).toBe("6px");
       expect(ownsOf("P0_0.png").style.left).toBe("6px");
       expect(ownsOf("P0_0.png").style.right).toBe("");
     });

  it("writes the word by itself -- no icon rides with it", () => {
    renderGallery({ frames: [HAS_BOTH] });

    expect(screen.getByText("video")).toBeTruthy();
    expect(screen.getByText("ses")).toBeTruthy();
    expect(document.querySelector("[data-glyph=play]")).toBeNull();
    expect(document.querySelector("[data-glyph=sound]")).toBeNull();
  });

  it("gives each layer a box of its own", () => {
    // Two words inside one dark box read as one thing the frame has. Each layer carries its own
    // box, with a thin space between them.
    renderGallery({ frames: [HAS_BOTH] });

    expect(badgesOf("P0_0.png").map((one) => one.textContent)).toEqual(["video", "ses"]);
    expect(ownsOf("P0_0.png").style.gap).toBe("4px");
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
