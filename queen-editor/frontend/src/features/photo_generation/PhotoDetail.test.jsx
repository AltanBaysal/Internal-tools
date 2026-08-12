import { act, fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { getStatus, listFrames, removeFrames } from "../../shared/api.js";
import { navigate } from "../../shared/router.js";
import PhotoDetail from "./PhotoDetail.jsx";

vi.mock("../../shared/api.js", () => ({
  cancelGeneration: vi.fn(),
  generateBatch: vi.fn(),
  getStatus: vi.fn(),
  listFrames: vi.fn(),
  removeFrames: vi.fn(),
  resumeBatch: vi.fn(),
  retryFrame: vi.fn(),
  saveOrder: vi.fn(),
  stopGeneration: vi.fn(),
  photoUrl: (project, file) => `/photos/${project}/${file}`,
}));
vi.mock("../../shared/router.js", () => ({
  navigate: vi.fn(),
  photoPath: (project, file) => `/projects/${project}/photos/${file}`,
  projectPath: (project) => `/projects/${project}`,
}));

const done = (file, prompt, negative = "") => ({ file, status: "done", prompt, negative });

const PHOTOS = [done("2_a.png", "üçüncü", "bulanık"),
                done("1_a.png", "ikinci"),
                done("0_a.png", "ilk", "gürültü")];

// The gallery as Madde 5 leaves it: one sequence, every state in its own place. 2_a.png is the one
// the live worker holds -- that is a pending frame with no line on disk, so only /api/status says so.
const MIXED = [{ file: "3_a.png", status: "pending", prompt: "dördüncü", negative: "bulanık" },
               { file: "2_a.png", status: "pending", prompt: "üçüncü", negative: "" },
               { file: "1_a.png", status: "failed", prompt: "ikinci", negative: "gürültü" },
               done("0_a.png", "ilk", "düşük çözünürlük")];

const IDLE = { status: "idle" };
const RUNNING = { status: "running", project: "düğün", current: { id: "2_a" } };

// Advancing the fake clock inside act() flushes both the timers and the promises they unblock --
// the detail page is live now, so a poll tick is what moves it forward.
async function settle(ms = 0) {
  await act(async () => { await vi.advanceTimersByTimeAsync(ms); });
}

async function open(file, { frames = PHOTOS, status = IDLE } = {}) {
  listFrames.mockResolvedValue(frames);
  getStatus.mockResolvedValue(status);
  render(<PhotoDetail project="düğün" file={file} />);
  await settle();
}

// The panel's own Sil comes first in the document; the modal's is the one added on top.
function confirmButton() {
  return screen.getAllByText("Sil").at(-1);
}

beforeEach(() => {
  vi.clearAllMocks();
  vi.useFakeTimers();
});

describe("PhotoDetail", () => {
  it("shows the position, the file name and the prompt", async () => {
    await open("1_a.png");

    expect(screen.getByText("2 / 3")).toBeTruthy();
    expect(screen.getByText("1_a.png")).toBeTruthy();
    expect(screen.getByText(/ikinci/)).toBeTruthy();
  });

  it("moves to the next photo with the arrow", async () => {
    await open("1_a.png");

    fireEvent.click(screen.getByText("›"));

    expect(navigate).toHaveBeenCalledWith("/projects/düğün/photos/0_a.png");
  });

  it("leaves the back arrow dead on the first photo", async () => {
    await open("2_a.png");

    fireEvent.click(screen.getByText("‹"));

    expect(navigate).not.toHaveBeenCalled();
  });

  it("responds to the arrow keys and Esc", async () => {
    await open("1_a.png");

    fireEvent.keyDown(window, { key: "ArrowLeft" });
    expect(navigate).toHaveBeenCalledWith("/projects/düğün/photos/2_a.png");

    fireEvent.keyDown(window, { key: "Escape" });
    expect(navigate).toHaveBeenCalledWith("/projects/düğün");
  });

  it("asks before deleting, then opens the next photo", async () => {
    removeFrames.mockResolvedValue({ deleted: ["1_a.png"], removed: [] });
    await open("1_a.png");

    fireEvent.click(screen.getByText("Sil"));
    expect(screen.getByText("Bu fotoğraf silinsin mi?")).toBeTruthy();
    expect(removeFrames).not.toHaveBeenCalled();

    await act(async () => { fireEvent.click(confirmButton()); });

    expect(removeFrames).toHaveBeenCalledWith("düğün", ["1_a.png"]);
    expect(navigate).toHaveBeenCalledWith("/projects/düğün/photos/0_a.png");
  });

  it("falls back to the previous photo when the last one is deleted", async () => {
    removeFrames.mockResolvedValue({ deleted: ["0_a.png"], removed: [] });
    await open("0_a.png");

    fireEvent.click(screen.getByText("Sil"));
    await act(async () => { fireEvent.click(confirmButton()); });

    expect(navigate).toHaveBeenCalledWith("/projects/düğün/photos/1_a.png");
  });

  it("shows an error card for a file that is not in the list", async () => {
    await open("yok.png");

    expect(screen.getByText("Fotoğraf bulunamadı")).toBeTruthy();
  });
});

describe("PhotoDetail — the counter is the gallery's badge", () => {
  it("gives the newest frame the largest number, the same one its tile carries", async () => {
    await open("2_a.png");

    expect(screen.getByText("3 / 3")).toBeTruthy();
  });

  it("gives the oldest frame 1, and leaves the forward arrow dead there", async () => {
    await open("0_a.png");

    expect(screen.getByText("1 / 3")).toBeTruthy();
    fireEvent.click(screen.getByText("›"));
    expect(navigate).not.toHaveBeenCalled();
  });

  it("walks the whole sequence, pending and failed frames included", async () => {
    await open("3_a.png", { frames: MIXED });

    expect(screen.getByText("4 / 4")).toBeTruthy();
    fireEvent.click(screen.getByText("›"));

    expect(navigate).toHaveBeenCalledWith("/projects/düğün/photos/2_a.png");
  });
});

describe("PhotoDetail — a frame that is not a photo yet", () => {
  it("says the frame is not produced instead of claiming it is missing", async () => {
    await open("3_a.png", { frames: MIXED });

    expect(screen.queryByText("Fotoğraf bulunamadı")).toBeNull();
    expect(screen.getByText("henüz üretilmedi")).toBeTruthy();
    expect(screen.getByText(/dördüncü/)).toBeTruthy();
  });

  it("calls the file name planned, and only for the frames that have no file", async () => {
    await open("3_a.png", { frames: MIXED });

    expect(screen.getByText("Dosya adı (planlanan)")).toBeTruthy();
    expect(screen.queryByText("Dosya adı")).toBeNull();
  });

  it("keeps the plain label on a produced photo", async () => {
    await open("0_a.png", { frames: MIXED });

    expect(screen.getByText("Dosya adı")).toBeTruthy();
    expect(screen.queryByText("Dosya adı (planlanan)")).toBeNull();
  });

  it("takes the frame out of the queue without asking, then opens the next one", async () => {
    removeFrames.mockResolvedValue({ deleted: [], removed: ["3_a.png"] });
    await open("3_a.png", { frames: MIXED });

    await act(async () => { fireEvent.click(screen.getByText("Kuyruktan çıkar")); });

    expect(removeFrames).toHaveBeenCalledWith("düğün", ["3_a.png"]);
    expect(navigate).toHaveBeenCalledWith("/projects/düğün/photos/2_a.png");
  });

  it("stays on the page and says so when the server refuses to remove it", async () => {
    removeFrames.mockRejectedValue(new Error("Proje yok: düğün"));
    await open("3_a.png", { frames: MIXED });

    await act(async () => { fireEvent.click(screen.getByText("Kuyruktan çıkar")); });

    expect(navigate).not.toHaveBeenCalled();
    expect(screen.getByText("Kare kuyruktan çıkarılamadı")).toBeTruthy();
    expect(screen.getByText(/Proje yok/)).toBeTruthy();
  });

  it("leaves the refusal behind when the arrows move on to another frame", async () => {
    removeFrames.mockRejectedValue(new Error("Proje yok: düğün"));
    listFrames.mockResolvedValue(MIXED);
    getStatus.mockResolvedValue(IDLE);
    const { rerender } = render(<PhotoDetail project="düğün" file="3_a.png" />);
    await settle();
    await act(async () => { fireEvent.click(screen.getByText("Kuyruktan çıkar")); });
    expect(screen.getByText("Kare kuyruktan çıkarılamadı")).toBeTruthy();

    // The page stays mounted while the router swaps the file under it.
    rerender(<PhotoDetail project="düğün" file="1_a.png" />);
    await settle();

    expect(screen.queryByText("Kare kuyruktan çıkarılamadı")).toBeNull();
  });

  it("draws a failed frame red and still offers to take it out of the queue", async () => {
    await open("1_a.png", { frames: MIXED });

    expect(screen.getByText("üretilemedi")).toBeTruthy();
    expect(screen.getByText("Kuyruktan çıkar")).toBeTruthy();
    expect(screen.queryByText("Sil")).toBeNull();
  });
});

describe("PhotoDetail — the frame the worker is holding", () => {
  it("spins instead of showing a photo, and lets nothing be pressed", async () => {
    await open("2_a.png", { frames: MIXED, status: RUNNING });

    expect(screen.getByText("Çalışıyor")).toBeTruthy();
    expect(screen.queryByText("henüz üretilmedi")).toBeNull();
    expect(screen.getByText("Kuyruktan çıkar").disabled).toBe(true);
  });

  it("becomes the photo in place when the render lands, with no reload", async () => {
    await open("2_a.png", { frames: MIXED, status: RUNNING });
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

describe("PhotoDetail — the negative prompt", () => {
  it("shows the negative next to the prompt", async () => {
    await open("3_a.png", { frames: MIXED });

    expect(screen.getByText("Negatif")).toBeTruthy();
    expect(screen.getByText(/bulanık/)).toBeTruthy();
  });

  it("draws the box even when there is no negative, rather than hiding it", async () => {
    await open("1_a.png");

    expect(screen.getByText("Negatif")).toBeTruthy();
    expect(screen.getByText("—")).toBeTruthy();
  });
});
