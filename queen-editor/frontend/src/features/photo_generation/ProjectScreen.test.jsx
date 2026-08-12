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

function renderScreen() {
  return render(
    <ProjectScreen project="düğün" settings={SETTINGS} onSaveSettings={() => Promise.resolve()} />,
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

describe("ProjectScreen — an open project carries its queue on", () => {
  const OWED = [{ id: "0_a", file: "0_a.png", status: "pending", owed: ["photo"], failed: [] }];

  beforeEach(() => {
    vi.useFakeTimers();
    resumeBatch.mockResolvedValue({});
  });
  afterEach(() => vi.useRealTimers());

  async function settle(ms = 0) {
    await act(async () => { await vi.advanceTimersByTimeAsync(ms); });
  }

  it("asks the server to go on when frames are owed and nobody is working", async () => {
    listFrames.mockResolvedValue(OWED);
    getStatus.mockResolvedValue({ status: "idle" });

    renderScreen();
    await settle();

    expect(resumeBatch).toHaveBeenCalledWith("düğün");
  });

  it("asks once, not on every poll", async () => {
    listFrames.mockResolvedValue(OWED);
    getStatus.mockResolvedValue({ status: "idle" });

    renderScreen();
    await settle();
    await settle(10_000);

    expect(resumeBatch).toHaveBeenCalledTimes(1);
  });

  it("carries a waiting queue on by itself once its producer has landed", async () => {
    listFrames.mockResolvedValue(OWED);
    getStatus.mockResolvedValue({ status: "waiting", project: "düğün", waitingFor: "video" });
    listProducers.mockResolvedValue([
      { id: "video", name: "Video üreticisi", installed: true }]);

    renderScreen();
    await settle();

    expect(resumeBatch).toHaveBeenCalledWith("düğün");
  });

  it("leaves a waiting queue where it is while its producer is still missing", async () => {
    listFrames.mockResolvedValue([]);
    getStatus.mockResolvedValue({ status: "waiting", project: "düğün", waitingFor: "video" });
    listProducers.mockResolvedValue([
      { id: "video", name: "Video üreticisi", installed: false }]);

    renderScreen();
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
    getStatus.mockResolvedValue({ status: "error", project: "düğün", error: "boom" });

    renderScreen();
    await settle();

    expect(resumeBatch).not.toHaveBeenCalled();
  });

  it("says nothing when the queue is empty", async () => {
    listFrames.mockResolvedValue([{ id: "0_a", file: "0_a.png", status: "done" }]);
    getStatus.mockResolvedValue({ status: "idle" });

    renderScreen();
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
