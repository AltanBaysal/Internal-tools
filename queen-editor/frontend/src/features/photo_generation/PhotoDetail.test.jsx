import { act, fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import {
  getStatus,
  listFrames,
  regenerateFrame,
  removeFrames,
  removeLayer,
  retryFrame,
} from "../../shared/api.js";
import { navigate } from "../../shared/router.js";
import PhotoDetail from "./PhotoDetail.jsx";

vi.mock("../../shared/api.js", () => ({
  cancelGeneration: vi.fn(),
  generateBatch: vi.fn(),
  getStatus: vi.fn(),
  listFrames: vi.fn(),
  regenerateFrame: vi.fn(),
  removeFrames: vi.fn(),
  removeLayer: vi.fn(),
  resumeBatch: vi.fn(),
  retryFrame: vi.fn(),
  saveOrder: vi.fn(),
  stopGeneration: vi.fn(),
  fileUrl: (project, file) => `/photos/${project}/${file}`,
}));
vi.mock("../../shared/router.js", () => ({
  navigate: vi.fn(),
  photoPath: (project, file) => `/projects/${project}/photos/${file}`,
  projectPath: (project) => `/projects/${project}`,
}));

// A frame is named by its identity; the file is only what it shows. These fixtures name a frame
// after its own picture, which is the ordinary case -- the copy frames that break the tie have
// their own tests.
const done = (file, prompt, negative = "") => ({ id: file.replace(".png", ""), file,
                                                 status: "done", prompt, negative,
                                                 layers: { photo: file }, owed: [], failed: [] });
const waiting = (file, prompt, negative = "") => ({ id: file.replace(".png", ""), file,
                                                    status: "pending", prompt, negative,
                                                    layers: {}, owed: ["photo"], failed: [] });

const PHOTOS = [done("2_a.png", "üçüncü", "bulanık"),
                done("1_a.png", "ikinci"),
                done("0_a.png", "ilk", "gürültü")];

// The gallery as Madde 5 leaves it: one sequence, every state in its own place. 2_a is the one the
// live worker holds -- that is a pending frame with no line on disk, so only /api/status says so.
const MIXED = [waiting("3_a.png", "dördüncü", "bulanık"),
               waiting("2_a.png", "üçüncü"),
               { id: "1_a", file: "1_a.png", status: "failed", prompt: "ikinci",
                 negative: "gürültü", layers: {}, owed: [], failed: ["photo"],
                 errors: { photo: "node 41: OOM — 3 kez denendi" } },
               done("0_a.png", "ilk", "düşük çözünürlük")];

const IDLE = { status: "idle" };
const RUNNING = { status: "running", project: "düğün", current: { id: "2_a" } };

// Advancing the fake clock inside act() flushes both the timers and the promises they unblock --
// the detail page is live now, so a poll tick is what moves it forward.
async function settle(ms = 0) {
  await act(async () => { await vi.advanceTimersByTimeAsync(ms); });
}

// The page is opened by the frame's identity: that is what the address carries.
async function open(fid, { frames = PHOTOS, status = IDLE } = {}) {
  listFrames.mockResolvedValue(frames);
  getStatus.mockResolvedValue(status);
  render(<PhotoDetail project="düğün" frame={fid} />);
  await settle();
}

// The panel's own Sil comes first in the document; the modal's is the one added on top.
function confirmButton() {
  return screen.getAllByText("Sil").at(-1);
}

const LAYERED = {
  id: "P0_0", file: "P0_0.png", status: "done", prompt: "kırmızı elbise", negative: "bulanık",
  layers: { photo: "P0_0.png", video: "P0_0_V1_0.mp4", audio: "P0_0_V1_0_S1_0.wav" },
  failed: [], owed: [],
  prompts: { photo: "kırmızı elbise", video: "kadın dönüyor", audio: "kumaş hışırtısı" },
};

// The frame the arrows move on to: its own words, so a box that kept the first frame's text shows.
const SECOND = { id: "P1_0", file: "P1_0.png", status: "done", prompt: "mavi elbise", negative: "",
                 layers: { photo: "P1_0.png" }, failed: [], owed: [],
                 prompts: { photo: "mavi elbise" } };

// A frame whose photo blew up: nothing on disk, and the record's own sentence about why.
const BROKEN = { id: "P0_0", file: "P0_0.png", status: "failed", prompt: "kırmızı elbise",
                 negative: "", layers: {}, failed: ["photo"], owed: [],
                 prompts: { photo: "kırmızı elbise" },
                 errors: { photo: "CUDA out of memory — 3 kez denendi" } };

// A copy frame waiting for its video: it holds its source's picture and owns no file of its own.
const QUEUED_COPY = { id: "P0_1", file: "P0_0.png", status: "done", prompt: "kırmızı elbise",
                      negative: "", layers: { photo: "P0_0.png" }, failed: [], owed: ["video"],
                      prompts: { photo: "kırmızı elbise" }, errors: {} };

const tab = (name) => screen.getByRole("button", { name });
const regenButton = () => screen.getByText("Yeniden üret — yeni kare").closest("button");

beforeEach(() => {
  vi.clearAllMocks();
  vi.useFakeTimers();
  // jsdom has no media pipeline: the player's own calls are stubbed so a tab can be opened.
  vi.spyOn(window.HTMLMediaElement.prototype, "play").mockResolvedValue(undefined);
  vi.spyOn(window.HTMLMediaElement.prototype, "pause").mockImplementation(() => {});
});

describe("PhotoDetail — the layer tabs", () => {
  it("opens on the photo and offers a tab per layer", async () => {
    await open("P0_0", { frames: [LAYERED] });

    expect(tab("Foto").getAttribute("aria-current")).toBe("page");
    expect(tab("Video").disabled).toBe(false);
    expect(tab("Ses").disabled).toBe(false);
  });

  it("leaves the tab of a layer the frame does not have disabled rather than hidden", async () => {
    await open("P0_0", { frames: [{ ...LAYERED, layers: { photo: "P0_0.png" },
                                        prompts: { photo: "kırmızı elbise" } }] });

    expect(tab("Video").disabled).toBe(true);
    expect(tab("Ses").disabled).toBe(true);
  });

  it("opens the tab of a layer that blew up, so its reason can be read", async () => {
    await open("P0_0", { frames: [{ ...LAYERED, failed: ["audio"],
                                    errors: { audio: "ComfyUI 500 — 3 kez denendi" } }] });

    expect(tab("Ses").disabled).toBe(false);
    fireEvent.click(tab("Ses"));

    expect(screen.getByText("ComfyUI 500 — 3 kez denendi")).toBeTruthy();
  });

  it("shows the open layer's own prompt and the ones under it", async () => {
    await open("P0_0", { frames: [LAYERED] });

    fireEvent.click(tab("Video"));

    // The open layer's prompt is the editable box; the ones under it are read-only (madde 75).
    expect(screen.getByDisplayValue("kadın dönüyor")).toBeTruthy();
    expect(screen.getByText("kırmızı elbise")).toBeTruthy();
    expect(screen.getByText("P0_0_V1_0.mp4")).toBeTruthy();
    // The negative belongs to the photo alone: video and sound jobs carry none.
    expect(screen.queryByText("Negatif")).toBeNull();
  });

  it("repeats the skeleton for sound", async () => {
    await open("P0_0", { frames: [LAYERED] });

    fireEvent.click(tab("Ses"));

    expect(screen.getByDisplayValue("kumaş hışırtısı")).toBeTruthy();
    expect(screen.getByText("P0_0_V1_0_S1_0.wav")).toBeTruthy();
    expect(screen.getByText("kadın dönüyor")).toBeTruthy();
  });

  it("plays the video on its own tab", async () => {
    await open("P0_0", { frames: [LAYERED] });

    fireEvent.click(tab("Video"));

    expect(document.querySelector("video").getAttribute("src"))
      .toBe("/photos/düğün/P0_0_V1_0.mp4");
    expect(document.querySelector("audio")).toBeNull();
  });

  it("brings the sound along on the sound tab", async () => {
    await open("P0_0", { frames: [LAYERED] });

    fireEvent.click(tab("Ses"));

    expect(document.querySelector("video")).toBeTruthy();
    expect(document.querySelector("audio").getAttribute("src"))
      .toBe("/photos/düğün/P0_0_V1_0_S1_0.wav");
  });

  it("leaves the photo tab as it was", async () => {
    await open("P0_0", { frames: [LAYERED] });

    expect(document.querySelector("video")).toBeNull();
    expect(screen.getByAltText("P0_0.png")).toBeTruthy();
  });

  it("draws a waiting frame's two lines faintly", async () => {
    await open("P0_0", { frames: [{ id: "P0_0", file: "P0_0.png", status: "pending", prompt: "p",
                                    layers: {}, failed: [], owed: ["photo"], prompts: {} }] });

    expect(screen.getByText("bekliyor").closest("[data-holder]").style.opacity).toBe("0.45");
  });
});

describe("PhotoDetail", () => {
  it("shows the position, the file name and the prompt", async () => {
    await open("1_a");

    expect(screen.getByText("2 / 3")).toBeTruthy();
    expect(screen.getByText("1_a.png")).toBeTruthy();
    expect(screen.getByDisplayValue("ikinci")).toBeTruthy();
  });

  it("moves to the next photo with the arrow", async () => {
    await open("1_a");

    fireEvent.click(screen.getByText("›"));

    expect(navigate).toHaveBeenCalledWith("/projects/düğün/photos/0_a");
  });

  it("leaves the back arrow dead on the first photo", async () => {
    await open("2_a");

    fireEvent.click(screen.getByText("‹"));

    expect(navigate).not.toHaveBeenCalled();
  });

  it("responds to the arrow keys and Esc", async () => {
    await open("1_a");

    fireEvent.keyDown(window, { key: "ArrowLeft" });
    expect(navigate).toHaveBeenCalledWith("/projects/düğün/photos/2_a");

    fireEvent.keyDown(window, { key: "Escape" });
    expect(navigate).toHaveBeenCalledWith("/projects/düğün");
  });

  it("asks before deleting, then opens the next photo", async () => {
    removeFrames.mockResolvedValue({ deleted: ["1_a.png"], removed: [] });
    await open("1_a");

    fireEvent.click(screen.getByText("Sil"));
    expect(screen.getByText("Bu fotoğraf silinsin mi?")).toBeTruthy();
    expect(removeFrames).not.toHaveBeenCalled();

    await act(async () => { fireEvent.click(confirmButton()); });

    expect(removeFrames).toHaveBeenCalledWith("düğün", ["1_a"]);
    expect(navigate).toHaveBeenCalledWith("/projects/düğün/photos/0_a");
  });

  it("falls back to the previous photo when the last one is deleted", async () => {
    removeFrames.mockResolvedValue({ deleted: ["0_a.png"], removed: [] });
    await open("0_a");

    fireEvent.click(screen.getByText("Sil"));
    await act(async () => { fireEvent.click(confirmButton()); });

    expect(navigate).toHaveBeenCalledWith("/projects/düğün/photos/1_a");
  });

  it("shows an error card for a file that is not in the list", async () => {
    await open("yok");

    expect(screen.getByText("Fotoğraf bulunamadı")).toBeTruthy();
  });
});

describe("PhotoDetail — the counter is the gallery's badge", () => {
  it("gives the newest frame the largest number, the same one its tile carries", async () => {
    await open("2_a");

    expect(screen.getByText("3 / 3")).toBeTruthy();
  });

  it("gives the oldest frame 1, and leaves the forward arrow dead there", async () => {
    await open("0_a");

    expect(screen.getByText("1 / 3")).toBeTruthy();
    fireEvent.click(screen.getByText("›"));
    expect(navigate).not.toHaveBeenCalled();
  });

  it("walks the whole sequence, pending and failed frames included", async () => {
    await open("3_a", { frames: MIXED });

    expect(screen.getByText("4 / 4")).toBeTruthy();
    fireEvent.click(screen.getByText("›"));

    expect(navigate).toHaveBeenCalledWith("/projects/düğün/photos/2_a");
  });
});

describe("PhotoDetail — a frame that is not a photo yet", () => {
  it("says the frame is not produced instead of claiming it is missing", async () => {
    await open("3_a", { frames: MIXED });

    expect(screen.queryByText("Fotoğraf bulunamadı")).toBeNull();
    expect(screen.getByText("henüz üretilmedi")).toBeTruthy();
    expect(screen.getByText(/dördüncü/)).toBeTruthy();
  });

  it("calls the file name planned, and only for the frames that have no file", async () => {
    await open("3_a", { frames: MIXED });

    expect(screen.getByText("Dosya adı (planlanan)")).toBeTruthy();
    expect(screen.queryByText("Dosya adı")).toBeNull();
  });

  it("keeps the plain label on a produced photo", async () => {
    await open("0_a", { frames: MIXED });

    expect(screen.getByText("Dosya adı")).toBeTruthy();
    expect(screen.queryByText("Dosya adı (planlanan)")).toBeNull();
  });

  it("takes the frame out of the queue without asking, then opens the next one", async () => {
    removeFrames.mockResolvedValue({ deleted: [], removed: ["3_a.png"] });
    await open("3_a", { frames: MIXED });

    await act(async () => { fireEvent.click(screen.getByText("Kuyruktan çıkar")); });

    expect(removeFrames).toHaveBeenCalledWith("düğün", ["3_a"]);
    expect(navigate).toHaveBeenCalledWith("/projects/düğün/photos/2_a");
  });

  it("stays on the page and says so when the server refuses to remove it", async () => {
    removeFrames.mockRejectedValue(new Error("Proje yok: düğün"));
    await open("3_a", { frames: MIXED });

    await act(async () => { fireEvent.click(screen.getByText("Kuyruktan çıkar")); });

    expect(navigate).not.toHaveBeenCalled();
    expect(screen.getByText("Kare kuyruktan çıkarılamadı")).toBeTruthy();
    expect(screen.getByText(/Proje yok/)).toBeTruthy();
  });

  it("leaves the refusal behind when the arrows move on to another frame", async () => {
    removeFrames.mockRejectedValue(new Error("Proje yok: düğün"));
    listFrames.mockResolvedValue(MIXED);
    getStatus.mockResolvedValue(IDLE);
    const { rerender } = render(<PhotoDetail project="düğün" frame="3_a" />);
    await settle();
    await act(async () => { fireEvent.click(screen.getByText("Kuyruktan çıkar")); });
    expect(screen.getByText("Kare kuyruktan çıkarılamadı")).toBeTruthy();

    // The page stays mounted while the router swaps the frame under it.
    rerender(<PhotoDetail project="düğün" frame="1_a" />);
    await settle();

    expect(screen.queryByText("Kare kuyruktan çıkarılamadı")).toBeNull();
  });

  it("draws a failed frame red and offers to delete it, not to dequeue it", async () => {
    await open("1_a", { frames: MIXED });

    expect(screen.getByText("Bu kare üretilemedi")).toBeTruthy();
    // Nothing is coming for it any more, so it is not in the queue to be taken out of.
    expect(screen.getByText("Kareyi sil")).toBeTruthy();
    expect(screen.queryByText("Sil")).toBeNull();
  });
});

describe("PhotoDetail — the frame the worker is holding", () => {
  it("spins instead of showing a photo, and lets nothing be pressed", async () => {
    await open("2_a", { frames: MIXED, status: RUNNING });

    expect(document.querySelector(".wf-spinner")).toBeTruthy();
    expect(screen.queryByText("Çalışıyor")).toBeNull();
    expect(screen.queryByText("henüz üretilmedi")).toBeNull();
    expect(screen.getByText("Kuyruktan çıkar").disabled).toBe(true);
  });

  it("becomes the photo in place when the render lands, with no reload", async () => {
    await open("2_a", { frames: MIXED, status: RUNNING });
    expect(screen.queryByAltText("2_a.png")).toBeNull();

    // The next poll: the worker moved on and the frame now has a line on disk.
    listFrames.mockResolvedValue(MIXED.map((frame) => (frame.file === "2_a.png"
      ? { ...frame, status: "done" }
      : frame)));
    getStatus.mockResolvedValue(IDLE);
    await settle(2000);

    expect(screen.getByAltText("2_a.png")).toBeTruthy();
    expect(screen.queryByText("Çalışıyor")).toBeNull();
  });
});

describe("PhotoDetail — regenerating", () => {
  it("lets the open layer's prompt be edited and marks the box as changed", async () => {
    await open("P0_0", { frames: [LAYERED] });
    const box = screen.getByDisplayValue("kırmızı elbise");
    expect(box.style.borderColor).not.toBe("var(--accent)");

    fireEvent.change(box, { target: { value: "mavi elbise" } });

    expect(screen.getByDisplayValue("mavi elbise").style.borderColor).toBe("var(--accent)");
  });

  it("leaves the box unmarked when only the space around the words changed", async () => {
    await open("P0_0", { frames: [LAYERED] });
    // The same node all the way through: the box is queried before the edit, because a display
    // value is matched with its whitespace collapsed and could not tell the two apart.
    const box = screen.getByDisplayValue("kırmızı elbise");

    fireEvent.change(box, { target: { value: "  kırmızı elbise\n" } });

    expect(box.value).toBe("  kırmızı elbise\n");
    expect(box.style.borderColor).not.toBe("var(--accent)");
  });

  it("keeps the button accent whether the prompt was touched or not", async () => {
    await open("P0_0", { frames: [LAYERED] });

    expect(regenButton().className).toContain("wf-btn--hl");
    expect(regenButton().disabled).toBe(false);
  });

  it("sends the open layer and the edited text", async () => {
    regenerateFrame.mockResolvedValue({ frame: "P0_1" });
    await open("P0_0", { frames: [LAYERED] });

    fireEvent.click(tab("Video"));
    fireEvent.change(screen.getByDisplayValue("kadın dönüyor"),
                     { target: { value: "kadın yürüyor" } });
    await act(async () => { fireEvent.click(regenButton()); });

    // The frame's identity, not its file: a copy frame shares its source's picture.
    expect(regenerateFrame).toHaveBeenCalledWith("düğün", "P0_0", "video", "kadın yürüyor");
  });

  it("says the job went into the queue and refuses a second press", async () => {
    regenerateFrame.mockResolvedValue({ frame: "P0_1" });
    await open("P0_0", { frames: [LAYERED] });

    await act(async () => { fireEvent.click(regenButton()); });

    expect(screen.getByText("Kuyruğa eklendi").closest("button").disabled).toBe(true);
    // And the frame says what is coming: the work landed on a frame of its own.
    expect(screen.getByText("yeniden üretilecek — kuyrukta")).toBeTruthy();
  });

  it("keeps the other tabs pressable after one layer was sent", async () => {
    regenerateFrame.mockResolvedValue({ frame: "P0_1" });
    await open("P0_0", { frames: [LAYERED] });
    await act(async () => { fireEvent.click(regenButton()); });

    fireEvent.click(tab("Video"));

    expect(regenButton().disabled).toBe(false);
  });

  it("stays on the frame and says so when the server refuses", async () => {
    regenerateFrame.mockRejectedValue(new Error("Proje yok: düğün"));
    await open("P0_0", { frames: [LAYERED] });

    await act(async () => { fireEvent.click(regenButton()); });

    expect(screen.getByText("Kare yeniden üretilemedi")).toBeTruthy();
    expect(screen.getByText(/Proje yok/)).toBeTruthy();
    expect(regenButton().disabled).toBe(false);
  });

  it("forgets the editing when another frame is opened", async () => {
    // The arrows swap the frame under a mounted page: the box belongs to the frame, not the page.
    listFrames.mockResolvedValue([LAYERED, SECOND]);
    getStatus.mockResolvedValue(IDLE);
    const { rerender } = render(<PhotoDetail project="düğün" frame="P0_0" />);
    await settle();
    fireEvent.change(screen.getByDisplayValue("kırmızı elbise"),
                     { target: { value: "yeşil elbise" } });

    rerender(<PhotoDetail project="düğün" frame="P1_0" />);
    await settle();

    expect(screen.getByDisplayValue("mavi elbise")).toBeTruthy();
    expect(screen.queryByDisplayValue("yeşil elbise")).toBeNull();
  });

  it("offers nothing to make again on a frame that was never produced", async () => {
    await open("3_a", { frames: MIXED });

    expect(screen.queryByText("Yeniden üret — yeni kare")).toBeNull();
  });
});

describe("PhotoDetail — one destructive action per tab", () => {
  it("offers the frame on the photo tab and the layer on the others", async () => {
    await open("P0_0", { frames: [LAYERED] });
    expect(screen.getByText("Sil")).toBeTruthy();

    fireEvent.click(tab("Video"));
    expect(screen.getByText("Videoyu sil — kare kalır")).toBeTruthy();
    expect(screen.queryByText("Sil")).toBeNull();

    fireEvent.click(tab("Ses"));
    expect(screen.getByText("Sesi sil — video kalır")).toBeTruthy();
    expect(screen.queryByText("Videoyu sil — kare kalır")).toBeNull();
  });

  it("asks with the design's own words before taking a video", async () => {
    await open("P0_0", { frames: [LAYERED] });

    fireEvent.click(tab("Video"));
    fireEvent.click(screen.getByText("Videoyu sil — kare kalır"));

    expect(screen.getByText("Video silinsin mi?")).toBeTruthy();
    expect(screen.getByText(/üzerindeki ses kalıcı olarak silinir/)).toBeTruthy();
    expect(removeLayer).not.toHaveBeenCalled();
  });

  it("says what a sound costs instead", async () => {
    await open("P0_0", { frames: [LAYERED] });

    fireEvent.click(tab("Ses"));
    fireEvent.click(screen.getByText("Sesi sil — video kalır"));

    expect(screen.getByText("Ses silinsin mi?")).toBeTruthy();
    expect(screen.getByText(/video sessiz oynar/)).toBeTruthy();
  });

  it("deletes the open layer and comes back to the photo tab", async () => {
    removeLayer.mockResolvedValue({ deleted: ["P0_0_V1_0.mp4"] });
    await open("P0_0", { frames: [LAYERED] });

    fireEvent.click(tab("Video"));
    fireEvent.click(screen.getByText("Videoyu sil — kare kalır"));
    await act(async () => { fireEvent.click(confirmButton()); });

    expect(removeLayer).toHaveBeenCalledWith("düğün", "P0_0", "video");
    // The frame is still the gallery's, so the page stays on it.
    expect(navigate).not.toHaveBeenCalled();
    expect(tab("Foto").getAttribute("aria-current")).toBe("page");
  });

  it("stays on the frame and says so when the server refuses", async () => {
    removeLayer.mockRejectedValue(new Error("Proje yok: düğün"));
    await open("P0_0", { frames: [LAYERED] });

    fireEvent.click(tab("Video"));
    fireEvent.click(screen.getByText("Videoyu sil — kare kalır"));
    await act(async () => { fireEvent.click(confirmButton()); });

    expect(screen.getByText("Video silinemedi")).toBeTruthy();
    expect(screen.getByText(/Proje yok/)).toBeTruthy();
  });

  it("leaves no fill under any of them (madde 83)", async () => {
    await open("P0_0", { frames: [LAYERED] });
    expect(screen.getByText("Sil").closest("button").style.background).toBe("none");

    fireEvent.click(tab("Video"));
    expect(screen.getByText("Videoyu sil — kare kalır").closest("button").style.background)
      .toBe("none");
  });
});

describe("PhotoDetail — a frame that blew up", () => {
  it("says what the renderer said, once", async () => {
    await open("P0_0", { frames: [BROKEN] });

    expect(screen.getByText("Bu kare üretilemedi")).toBeTruthy();
    expect(screen.getByText("CUDA out of memory — 3 kez denendi")).toBeTruthy();
  });

  it("puts the frame back in line without asking", async () => {
    retryFrame.mockResolvedValue({ job: "running" });
    await open("P0_0", { frames: [BROKEN] });

    await act(async () => { fireEvent.click(screen.getByText("Tekrar dene")); });

    expect(retryFrame).toHaveBeenCalledWith("düğün", "P0_0");
    expect(screen.getByText("Kuyruğa eklendi").closest("button").disabled).toBe(true);
  });

  it("calls the frame gone rather than pretending it is queued", async () => {
    await open("P0_0", { frames: [BROKEN] });

    expect(screen.getByText("Kareyi sil")).toBeTruthy();
    expect(screen.queryByText("Kuyruktan çıkar")).toBeNull();
  });

  it("leaves the prompt read-only there", async () => {
    await open("P0_0", { frames: [BROKEN] });

    expect(screen.queryByDisplayValue("kırmızı elbise")).toBeNull();
    expect(screen.getByText("kırmızı elbise")).toBeTruthy();
    expect(screen.queryByText("Yeniden üret — yeni kare")).toBeNull();
  });
});

describe("PhotoDetail — a copy frame waiting in the queue", () => {
  it("shows the picture it holds and says what is coming", async () => {
    await open("P0_1", { frames: [QUEUED_COPY] });

    expect(screen.getByAltText("P0_0.png")).toBeTruthy();
    expect(screen.getByText("video kuyrukta")).toBeTruthy();
  });

  it("opens the tab of the layer it is waiting for, with an empty box", async () => {
    await open("P0_1", { frames: [QUEUED_COPY] });

    fireEvent.click(tab("Video"));

    expect(screen.getByText("üretim sırası gelince LLM yazacak")).toBeTruthy();
    // Nothing to make again and nothing to delete: the layer is not there yet.
    expect(screen.queryByText("Yeniden üret — yeni kare")).toBeNull();
    expect(screen.queryByText("Videoyu sil — kare kalır")).toBeNull();
  });

  it("takes it out of the queue without asking", async () => {
    removeFrames.mockResolvedValue({ deleted: [], removed: ["P0_1"] });
    await open("P0_1", { frames: [QUEUED_COPY] });

    await act(async () => { fireEvent.click(screen.getByText("Kuyruktan çıkar")); });

    // Its identity, not the picture it shares with its source.
    expect(removeFrames).toHaveBeenCalledWith("düğün", ["P0_1"]);
    expect(screen.queryByText("Bu fotoğraf silinsin mi?")).toBeNull();
  });
});

describe("PhotoDetail — the negative prompt", () => {
  it("shows the negative next to the prompt", async () => {
    await open("3_a", { frames: MIXED });

    expect(screen.getByText("Negatif")).toBeTruthy();
    expect(screen.getByText(/bulanık/)).toBeTruthy();
  });

  it("draws the box even when there is no negative, rather than hiding it", async () => {
    await open("1_a");

    expect(screen.getByText("Negatif")).toBeTruthy();
    expect(screen.getByText("—")).toBeTruthy();
  });
});
