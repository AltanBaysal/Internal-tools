import { act, fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { getExportSummary } from "../../shared/api.js";
import { navigate } from "../../shared/router.js";
import ExportScreen from "./ExportScreen.jsx";
import { useGeneration } from "./useGeneration.js";

vi.mock("../../shared/api.js", () => ({ getExportSummary: vi.fn() }));
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

async function open(summary = SUMMARY, generation = IDLE) {
  getExportSummary.mockResolvedValue(summary);
  useGeneration.mockReturnValue(generation);
  render(<ExportScreen project="düğün" />);
  await act(async () => {});
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

  it("says so when the summary cannot be read", async () => {
    getExportSummary.mockRejectedValue(new Error("Proje yok: düğün"));
    render(<ExportScreen project="düğün" />);
    await act(async () => {});

    expect(screen.getByText("Export özeti yüklenemedi")).toBeTruthy();
    expect(screen.getByText(/Proje yok/)).toBeTruthy();
  });
});
