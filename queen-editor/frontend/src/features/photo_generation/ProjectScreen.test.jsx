import { act, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { getStatus, listFrames, listProducers, resumeBatch } from "../../shared/api.js";
import { navigate } from "../../shared/router.js";
import ProjectScreen from "./ProjectScreen.jsx";

vi.mock("../../shared/router.js", () => ({
  navigate: vi.fn(),
  photoPath: (project, frame) => `/projects/${encodeURIComponent(project)}/photos/${frame}`,
  exportPath: (project) => `/projects/${encodeURIComponent(project)}/export`,
}));

vi.mock("../../shared/api.js", () => ({
  cancelGeneration: vi.fn(),
  deletePhotos: vi.fn(),
  generateBatch: vi.fn(),
  getStatus: vi.fn().mockResolvedValue({ status: "idle" }),
  listFrames: vi.fn().mockResolvedValue([]),
  listModels: vi.fn().mockResolvedValue(["nova.safetensors"]),
  listProducers: vi.fn().mockResolvedValue([]),
  fileUrl: (project, file) => `/photos/${project}/${file}`,
  resumeBatch: vi.fn(),
  retryFailed: vi.fn(),
  retryFrame: vi.fn(),
  saveOrder: vi.fn(),
  stopGeneration: vi.fn(),
}));

const SETTINGS = { prompts: "", negative: "", variants: 4 };

// The gallery a project last answered with is remembered across mounts, so a test that must start
// from nothing asks for a project name no other test has filled.
function renderScreen(project = "düğün") {
  return render(
    <ProjectScreen project={project} settings={SETTINGS} onSaveSettings={() => Promise.resolve()} />,
  );
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe("ProjectScreen app bar", () => {
  it("opens the export screen instead of downloading a file", () => {
    renderScreen();

    fireEvent.click(screen.getByText("Export"));

    expect(navigate).toHaveBeenCalledWith(`/projects/${encodeURIComponent("düğün")}/export`);
  });

  it("leaves for the projects screen without asking first", () => {
    renderScreen();

    fireEvent.click(screen.getByText("Projeden çık"));

    // Nothing is at risk: the queue is the server's and the frames are on disk (madde 10).
    expect(screen.queryByText("Projeden çıkılsın mı?")).toBeNull();
    expect(navigate).toHaveBeenCalledWith("/");
  });

  it("places Export to the left of the leave button", () => {
    renderScreen();

    const exportEl = screen.getByText("Export");
    const exitEl = screen.getByText("Projeden çık");
    // compareDocumentPosition's FOLLOWING bit: the exit button comes later in document order.
    expect(exportEl.compareDocumentPosition(exitEl) & Node.DOCUMENT_POSITION_FOLLOWING)
      .toBeTruthy();
  });
});

describe("ProjectScreen — what leaving says while the queue flows", () => {
  const BUBBLE = "Projeden çıksan da pencereyi kapatsan da kuyruk durmaz. "
                 + "Döndüğünde biten kareleri galeride bulursun.";

  beforeEach(() => {
    vi.useFakeTimers();
  });
  afterEach(() => vi.useRealTimers());

  async function openWith(status) {
    getStatus.mockResolvedValue(status);
    renderScreen();
    await act(async () => { await vi.advanceTimersByTimeAsync(0); });
  }

  it("explains itself over the button while production runs", async () => {
    await openWith({ status: "running", project: "düğün" });

    fireEvent.mouseEnter(screen.getByText("Projeden çık"));

    expect(screen.getByText("Üretim arka planda sürüyor")).toBeTruthy();
    expect(screen.getByText(BUBBLE)).toBeTruthy();
  });

  it("takes the bubble away when the pointer leaves", async () => {
    await openWith({ status: "running", project: "düğün" });
    fireEvent.mouseEnter(screen.getByText("Projeden çık"));

    fireEvent.mouseLeave(screen.getByText("Projeden çık"));

    expect(screen.queryByText("Üretim arka planda sürüyor")).toBeNull();
  });

  it("says nothing when there is no production to speak of", async () => {
    await openWith({ status: "idle" });

    fireEvent.mouseEnter(screen.getByText("Projeden çık"));

    expect(screen.queryByText("Üretim arka planda sürüyor")).toBeNull();
  });

  it("says nothing while the queue is paused: a stopped queue does not go on", async () => {
    await openWith({ status: "paused", project: "düğün" });

    fireEvent.mouseEnter(screen.getByText("Projeden çık"));

    expect(screen.queryByText("Üretim arka planda sürüyor")).toBeNull();
  });
});

describe("ProjectScreen — an open project waits for the user", () => {
  const OWED = [{ id: "0_a", file: "0_a.png", status: "pending", owed: ["photo"], failed: [] }];

  beforeEach(() => {
    vi.useFakeTimers();
    resumeBatch.mockResolvedValue({});
  });
  afterEach(() => vi.useRealTimers());

  async function settle(ms = 0) {
    await act(async () => { await vi.advanceTimersByTimeAsync(ms); });
  }

  it("starts nothing on its own, however many frames are owed", async () => {
    listFrames.mockResolvedValue(OWED);
    getStatus.mockResolvedValue({ status: "idle" });

    renderScreen();
    await settle();
    await settle(10_000);

    expect(resumeBatch).not.toHaveBeenCalled();
  });

  it("leaves a waiting queue where it is even once its producer has landed", async () => {
    listFrames.mockResolvedValue(OWED);
    getStatus.mockResolvedValue({ status: "waiting", project: "düğün", waitingFor: "video" });
    listProducers.mockResolvedValue([
      { id: "video", name: "Video üreticisi", installed: true }]);

    renderScreen();
    await settle();

    expect(resumeBatch).not.toHaveBeenCalled();
  });

  it("leaves a waiting queue where it is while its producer is still missing", async () => {
    listFrames.mockResolvedValue([]);
    getStatus.mockResolvedValue({ status: "waiting", project: "boş 1", waitingFor: "video" });
    listProducers.mockResolvedValue([
      { id: "video", name: "Video üreticisi", installed: false }]);

    renderScreen("boş 1");
    await settle();

    expect(resumeBatch).not.toHaveBeenCalled();
  });

  it("leaves a paused queue alone -- it has its own Devam et", async () => {
    listFrames.mockResolvedValue(OWED);
    getStatus.mockResolvedValue({ status: "paused", project: "düğün" });

    renderScreen();
    await settle();

    expect(resumeBatch).not.toHaveBeenCalled();
  });

  it("leaves a queue a fatal error stopped alone", async () => {
    listFrames.mockResolvedValue(OWED);
    getStatus.mockResolvedValue({ status: "error", project: "boş 2", error: "boom" });

    renderScreen("boş 2");
    await settle();

    expect(resumeBatch).not.toHaveBeenCalled();
  });

  it("says nothing when the queue is empty", async () => {
    listFrames.mockResolvedValue([{ id: "0_a", file: "0_a.png", status: "done" }]);
    getStatus.mockResolvedValue({ status: "idle" });

    renderScreen("boş 3");
    await settle();

    expect(resumeBatch).not.toHaveBeenCalled();
  });

  it("does not touch a queue that is already going", async () => {
    listFrames.mockResolvedValue(OWED);
    getStatus.mockResolvedValue({ status: "running", project: "düğün" });

    renderScreen();
    await settle();

    expect(resumeBatch).not.toHaveBeenCalled();
  });
});

// The first test in this file that drives the gallery. Everything above renders the screen and
// reads it; this one uses it -- which is where the bugs turned out to live: each piece was tested
// against inputs handed to it by hand, and the wire between them by nothing at all.
describe("ProjectScreen — the gallery's selection reaches the video panel", () => {
  beforeEach(() => { vi.useFakeTimers(); });
  afterEach(() => vi.useRealTimers());

  const done = (file) => ({ id: file.replace(".png", ""), file, status: "done", layers: {},
                            owed: [], failed: [] });
  const FRAMES = [done("1_a.png"), done("0_a.png")];

  async function settle(ms = 0) {
    await act(async () => { await vi.advanceTimersByTimeAsync(ms); });
  }

  it("counts a frame picked in the gallery, and stops counting it when it is let go", async () => {
    listFrames.mockResolvedValue(FRAMES);
    renderScreen("seçim");
    await settle();
    fireEvent.click(screen.getByLabelText("Video üret"));
    // By identity, because that is what a tile is keyed by -- and the identity is the whole point
    // of this test.
    const ring = () => document.getElementById("tile-0_a").querySelector("[data-check]");
    const scope = () => screen.getByText("Seçili kareler").closest("button");

    await act(async () => { fireEvent.click(ring()); });

    expect(scope().textContent).toContain("1");

    await act(async () => { fireEvent.click(ring()); });

    // The second assertion needs the first: a count that is always 0 would pass this line alone.
    expect(scope().textContent).toContain("0");
  });
});

// What the gallery is told about the queue. The pill's word is the only place on screen where a
// frame says whether anything is coming for it, and the gallery cannot know that by itself.
describe("ProjectScreen — a stopped queue does not look like a moving one", () => {
  beforeEach(() => { vi.useFakeTimers(); });
  afterEach(() => vi.useRealTimers());

  const OWES_VIDEO = [{ id: "P0_0", file: "P0_0.png", status: "done", layers: { photo: "P0_0.png" },
                        owed: ["video"], failed: [] }];

  async function open(status, project) {
    listFrames.mockResolvedValue(OWES_VIDEO);
    getStatus.mockResolvedValue(status);
    renderScreen(project);
    await act(async () => { await vi.advanceTimersByTimeAsync(0); });
  }

  it("says queued while this project's queue is flowing", async () => {
    await open({ status: "running", project: "akan" }, "akan");

    expect(screen.getByText("video kuyrukta")).toBeTruthy();
  });

  it("says waiting once an error has stopped the queue", async () => {
    // 2026-08-13: a dead xAI key stopped the run and every frame went on saying it was queued.
    await open({ status: "error", project: "duran", error: "xAI HTTP 400" }, "duran");

    expect(screen.getByText("video bekliyor")).toBeTruthy();
  });

  it("says waiting while it is another project's queue that is flowing", async () => {
    // The worker is global: a batch belonging to someone else moves nothing here.
    await open({ status: "running", project: "komşu" }, "bizim");

    expect(screen.getByText("video bekliyor")).toBeTruthy();
  });
});
