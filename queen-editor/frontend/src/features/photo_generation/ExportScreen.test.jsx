import { act, fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import {
  cancelExport,
  getExportState,
  getExportSummary,
  startExport,
} from "../../shared/api.js";
import { navigate } from "../../shared/router.js";
import ExportScreen from "./ExportScreen.jsx";
import { useGeneration } from "./useGeneration.js";

vi.mock("../../shared/api.js", () => ({
  cancelExport: vi.fn(),
  getExportState: vi.fn(),
  getExportSummary: vi.fn(),
  startExport: vi.fn(),
}));
vi.mock("../../shared/router.js", () => ({
  navigate: vi.fn(),
  projectPath: (project) => `/projects/${project}`,
}));
// The queue's state comes from the hook the whole app reads it with; the screen adds no second
// count of its own.
vi.mock("./useGeneration.js", () => ({ useGeneration: vi.fn() }));

const SUMMARY = { videos: 22, seconds: 110, silent: 0, withoutVideo: 0,
                  folder: "/drive/düğün/export" };
const EMPTY = { videos: 0, seconds: 0, silent: 0, withoutVideo: 0,
                folder: "/drive/düğün/export" };

const IDLE = { job: { status: "idle" }, frames: [], queue: [] };
const FLOWING = { job: { status: "running", project: "düğün" }, frames: [],
                  queue: [{ layer: "video", owed: 5 }] };
const PAUSED = { job: { status: "paused", project: "düğün" }, frames: [],
                 queue: [{ layer: "video", owed: 5 }] };

const button = (label) => screen.getByText(label).closest("button");

const NOTHING = { merged: { state: "idle" }, separate: { state: "idle" } };

async function open(summary = SUMMARY, generation = IDLE, exportState = NOTHING) {
  getExportSummary.mockResolvedValue(summary);
  getExportState.mockResolvedValue(exportState);
  startExport.mockResolvedValue({ job: "running" });
  cancelExport.mockResolvedValue({ job: "cancelling" });
  useGeneration.mockReturnValue(generation);
  render(<ExportScreen project="düğün" />);
  await act(async () => {});
}

// Press an export button and let the answer it triggers land.
async function press(label) {
  await act(async () => { fireEvent.click(button(label)); });
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe("ExportScreen", () => {
  it("says how many videos there are and how long they run", async () => {
    await open();

    expect(screen.getByText("22 video export edilecek · 1:50 dk")).toBeTruthy();
  });

  it("names the folder the export would be written to", async () => {
    await open();

    expect(screen.getByText("Şuraya yazılacak:")).toBeTruthy();
    expect(screen.getByText("/drive/düğün/export")).toBeTruthy();
  });

  it("offers the two exports side by side, both accent", async () => {
    await open();

    expect(button("Birleşik videoyu export et").className).toContain("wf-btn--hl");
    expect(button("Videoları ayrı export et").className).toContain("wf-btn--hl");
    expect(button("Birleşik videoyu export et").disabled).toBe(false);
  });

  it("turns into guidance when the project has no video", async () => {
    await open(EMPTY);

    expect(screen.getByText("Export edilecek video yok")).toBeTruthy();
    expect(screen.getByText(/önce Video üret panelinden/)).toBeTruthy();
    expect(button("Birleşik videoyu export et").disabled).toBe(true);
    expect(button("Videoları ayrı export et").disabled).toBe(true);
  });

  it("carries the project's name and its own app bar", async () => {
    await open();

    expect(screen.getByText("düğün · Export")).toBeTruthy();
  });

  it("goes back to the gallery", async () => {
    await open();

    fireEvent.click(screen.getByText("Galeriye dön"));

    expect(navigate).toHaveBeenCalledWith("/projects/düğün");
  });

  it("says how many videos have no sound", async () => {
    await open({ ...SUMMARY, silent: 16 });

    expect(screen.getByText("⚠ 16 videonun sesi yok")).toBeTruthy();
  });

  it("says which frames the sequence will not hold", async () => {
    await open({ ...SUMMARY, withoutVideo: 3 });

    expect(screen.getByText("⚠ 3 videosuz kare diziye girmeyecek")).toBeTruthy();
  });

  it("draws no row for a condition that is not there", async () => {
    await open();

    expect(screen.queryByText(/sesi yok/)).toBeNull();
    expect(screen.queryByText(/diziye girmeyecek/)).toBeNull();
  });

  it("blocks the export while the queue flows, and says why", async () => {
    await open(SUMMARY, FLOWING);

    expect(screen.getByText(/Üretim sürüyor — 5 video kuyrukta/)).toBeTruthy();
    expect(button("Birleşik videoyu export et").disabled).toBe(true);
    expect(button("Videoları ayrı export et").disabled).toBe(true);
  });

  it("lets the export run once the queue is paused", async () => {
    await open(SUMMARY, PAUSED);

    expect(button("Birleşik videoyu export et").disabled).toBe(false);
    expect(screen.queryByText(/Üretim sürüyor/)).toBeNull();
    // What was a blocking card is now one more line in the summary.
    expect(screen.getByText("⚠ 5 karenin videosu kuyrukta bekliyor — diziye girmeyecek"))
      .toBeTruthy();
  });

  it("starts the export the button names", async () => {
    await open();

    await press("Videoları ayrı export et");

    expect(startExport).toHaveBeenCalledWith("düğün", "separate");
  });

  it("reads the progress in the button's own place", async () => {
    await open(SUMMARY, IDLE,
               { ...NOTHING, separate: { state: "running", written: 7, total: 22 } });

    await press("Videoları ayrı export et");

    expect(screen.getByText("7 / 22 yazıldı…")).toBeTruthy();
    // The other one stays pressable: the two exports can run side by side (madde 93).
    expect(button("Birleşik videoyu export et").disabled).toBe(false);
  });

  it("says it is joining the pieces while the merged one finishes", async () => {
    await open(SUMMARY, IDLE, { ...NOTHING, merged: { state: "merging", written: 22, total: 22 } });

    await press("Birleşik videoyu export et");

    expect(screen.getByText("birleştiriliyor…")).toBeTruthy();
  });

  it("says where the finished export went", async () => {
    await open(SUMMARY, IDLE, { ...NOTHING,
                                separate: { state: "done", written: 3, total: 3,
                                            target: "/drive/düğün/export/2026-08-12 14-32" } });

    await press("Videoları ayrı export et");

    expect(screen.getByText("✓ Export tamamlandı")).toBeTruthy();
    expect(screen.getByText(/2026-08-12 14-32/)).toBeTruthy();
  });

  it("says why an export failed, in the tool's own words", async () => {
    await open(SUMMARY, IDLE, { ...NOTHING,
                                separate: { state: "error", error: "ffmpeg: disk dolu" } });

    await press("Videoları ayrı export et");

    expect(screen.getByText("Export başarısız")).toBeTruthy();
    expect(screen.getByText("ffmpeg: disk dolu")).toBeTruthy();
    // No retry of its own: the buttons are still there and a new press opens a new folder.
    expect(screen.queryByText("Tekrar dene")).toBeNull();
    expect(button("Videoları ayrı export et").disabled).toBe(false);
  });

  it("asks before leaving while an export is running, and cancels it", async () => {
    await open(SUMMARY, IDLE,
               { ...NOTHING, separate: { state: "running", written: 1, total: 3 } });
    await press("Videoları ayrı export et");

    fireEvent.click(screen.getByText("Galeriye dön"));
    expect(screen.getByText("Export sürüyor — çıkılsın mı?")).toBeTruthy();
    expect(screen.getByText("Export sürüyor — çıkılsın mı?").closest(".wf-card").style.width)
      .toBe("380px");
    expect(navigate).not.toHaveBeenCalled();

    await act(async () => { fireEvent.click(screen.getByText("Çık")); });

    expect(cancelExport).toHaveBeenCalledWith("düğün");
    expect(navigate).toHaveBeenCalledWith("/projects/düğün");
  });

  it("leaves without asking when nothing is running", async () => {
    await open();

    fireEvent.click(screen.getByText("Galeriye dön"));

    expect(navigate).toHaveBeenCalledWith("/projects/düğün");
    expect(cancelExport).not.toHaveBeenCalled();
  });

  it("says so when the summary cannot be read", async () => {
    getExportSummary.mockRejectedValue(new Error("Proje yok: düğün"));
    render(<ExportScreen project="düğün" />);
    await act(async () => {});

    expect(screen.getByText("Export özeti yüklenemedi")).toBeTruthy();
    expect(screen.getByText(/Proje yok/)).toBeTruthy();
  });
});
