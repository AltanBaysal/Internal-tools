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
    renderGallery({ frames: MIXED, current: "3_a" });

    expect(pillOf("4_a.png").textContent).toBe("foto kuyrukta");
    expect(pillOf("3_a.png").textContent).toBe("foto üretiliyor");
    expect(pillOf("2_a.png").textContent).toBe("foto hata");
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

    // Once: not a red tile and a dashed one at the same time.
    expect(screen.getAllByText("foto kuyrukta")).toHaveLength(2);
    fireEvent.click(screen.getByText("Tekrar dene"));

    expect(onRetry).toHaveBeenCalledWith("2_a");
  });

  it("turns the frame the worker is holding into a spinner without moving it", () => {
    renderGallery({ frames: MIXED, current: "3_a" });

    // Four of the five are not photos; only the one the worker holds leaves the waiting pill.
    expect(screen.getAllByText("foto kuyrukta")).toHaveLength(1);
    expect(tileOf("3_a.png").textContent).toContain("4");
  });

  it("does not claim the gallery is empty when only waiting frames are in it", () => {
    renderGallery({ frames: [pending("0_a.png")] });

    expect(screen.queryByText("henüz kare yok")).toBeNull();
    expect(screen.getByText("foto kuyrukta")).toBeTruthy();
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

  it("takes the bar away when the selection is emptied", () => {
    renderGallery();
    fireEvent.click(checkOf("1_a.png"));
    fireEvent.click(photoOf("1_a.png"));  // deselect: the mode stays open, the bar goes

    expect(screen.queryByText(/seçili/)).toBeNull();
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

    expect(screen.getByText(
      "1 kare silinsin, 1 bekleyen kare kuyruktan çıkarılsın mı?")).toBeTruthy();
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

describe("Gallery — picking a tile up", () => {
  beforeEach(() => vi.useFakeTimers({ shouldAdvanceTime: true }));
  afterEach(() => vi.useRealTimers());

  it("does not let go of a tile that was only tapped", () => {
    renderGallery();

    fireEvent.mouseDown(tileOf("1_a.png"));

    expect(tileOf("1_a.png").draggable).toBe(false);
  });

  it("arms the tile once it has been held", () => {
    renderGallery();

    fireEvent.mouseDown(tileOf("1_a.png"));
    act(() => { vi.advanceTimersByTime(250); });

    expect(tileOf("1_a.png").draggable).toBe(true);
  });

  it("lifts a waiting frame too -- the drag is what decides when it is produced", () => {
    renderGallery({ frames: [pending("9_a.png"), done("0_a.png")] });

    fireEvent.mouseDown(tileOf("9_a.png"));
    act(() => { vi.advanceTimersByTime(250); });

    expect(tileOf("9_a.png").draggable).toBe(true);
    expect(screen.queryByText("üretilince sıralanabilir")).toBeNull();
  });

  it("lifts a failed frame too", () => {
    renderGallery({ frames: [broken("9_a.png"), done("0_a.png")] });

    fireEvent.mouseDown(tileOf("9_a.png"));
    act(() => { vi.advanceTimersByTime(250); });

    expect(tileOf("9_a.png").draggable).toBe(true);
  });

  it("lifts the frame the worker is holding, without asking it to stop", () => {
    renderGallery({ frames: [pending("9_a.png"), done("0_a.png")],
                    current: "9_a" });

    fireEvent.mouseDown(tileOf("9_a.png"));
    act(() => { vi.advanceTimersByTime(250); });

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

  it("keeps the photo on screen while the video is queued", () => {
    renderGallery({ frames: [done("P0_0.png", { owed: ["video"] })] });

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
