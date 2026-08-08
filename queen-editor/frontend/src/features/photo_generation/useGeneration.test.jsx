import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { generateBatch, getStatus, listFrames, saveOrder, stopGeneration } from "../../shared/api.js";
import { useGeneration } from "./useGeneration.js";

vi.mock("../../shared/api.js", () => ({
  cancelGeneration: vi.fn(),
  deletePhotos: vi.fn(),
  generateBatch: vi.fn(),
  getStatus: vi.fn(),
  listFrames: vi.fn(),
  resumeBatch: vi.fn(),
  retryFrame: vi.fn(),
  saveOrder: vi.fn(),
  stopGeneration: vi.fn(),
}));

// Testing Library's waitFor only understands Jest's fake clock, so with vitest's it would wait
// forever. Advancing the fake clock inside act() flushes both the timers and the promises they
// unblock, which is exactly what a poll tick is.
async function settle(ms = 0) {
  await act(async () => { await vi.advanceTimersByTimeAsync(ms); });
}

const RUNNING = { status: "running", project: "düğün", done: 1, failed: 0, total: 4 };
const DONE = { status: "done", project: "düğün", done: 4, failed: 0, total: 4 };

beforeEach(() => {
  vi.clearAllMocks();
  vi.useFakeTimers();
});

describe("useGeneration", () => {
  it("treats the photos as unknown at first and asks for both status and photos on the first poll", async () => {
    getStatus.mockResolvedValue({ status: "idle" });
    listFrames.mockResolvedValue([]);

    const { result } = renderHook(() => useGeneration("düğün"));
    expect(result.current.frames).toBeNull();

    await settle();

    expect(result.current.frames).toEqual([]);
    expect(getStatus).toHaveBeenCalledTimes(1);
    expect(listFrames).toHaveBeenCalledWith("düğün");
  });

  it("asks every 2 seconds while a run is going and stops the chain when it ends", async () => {
    getStatus.mockResolvedValue(RUNNING);
    listFrames.mockResolvedValue([]);

    renderHook(() => useGeneration("düğün"));
    await settle();
    expect(getStatus).toHaveBeenCalledTimes(1);

    await settle(2000);
    expect(getStatus).toHaveBeenCalledTimes(2);

    getStatus.mockResolvedValue(DONE);
    await settle(2000);
    expect(getStatus).toHaveBeenCalledTimes(3);

    await settle(10_000);
    expect(getStatus).toHaveBeenCalledTimes(3);
  });

  it("shows the error when a poll fails, keeps trying, and clears it once the connection returns", async () => {
    const dead = new Error("Sunucuya ulaşılamadı — bağlantıyı kontrol et.\nZaman aşımı (10 sn)");
    getStatus.mockRejectedValue(dead);
    listFrames.mockRejectedValue(dead);

    const { result } = renderHook(() => useGeneration("düğün"));
    await settle();
    expect(result.current.error).toContain("Sunucuya ulaşılamadı");

    await settle(2000);
    expect(getStatus).toHaveBeenCalledTimes(2);

    getStatus.mockResolvedValue({ status: "idle" });
    listFrames.mockResolvedValue([]);
    await settle(2000);
    expect(result.current.error).toBeNull();
  });

  it("asks for the photos once more as the run finishes", async () => {
    getStatus.mockResolvedValue(RUNNING);
    listFrames.mockResolvedValue([]);

    renderHook(() => useGeneration("düğün"));
    await settle();
    const afterFirstPoll = listFrames.mock.calls.length;

    getStatus.mockResolvedValue(DONE);
    await settle(2000);

    // The poll's own refresh plus one extra for the frame still landing on Drive.
    expect(listFrames.mock.calls.length).toBe(afterFirstPoll + 2);
  });

  it("does not revive the chain when the screen is left before an answer arrives", async () => {
    // Unmounting while a poll is still in flight is the only way the chain can outlive the screen:
    // the effect's cleanup clears the pending timer, but the failing request that lands afterwards
    // would arm a brand new one that nobody owns.
    let rejectStatus;
    getStatus.mockReturnValue(new Promise((_, reject) => { rejectStatus = reject; }));
    listFrames.mockRejectedValue(new Error("kopuk"));

    const { unmount } = renderHook(() => useGeneration("düğün"));
    const callsBefore = getStatus.mock.calls.length;

    unmount();
    await act(async () => { rejectStatus(new Error("kopuk")); });
    await settle(10_000);

    expect(getStatus.mock.calls.length).toBe(callsBefore);
  });

  it("puts the panel into the running state without waiting for the server", async () => {
    getStatus.mockResolvedValue({ status: "idle" });
    listFrames.mockResolvedValue([]);
    generateBatch.mockResolvedValue({ started: true });

    const { result } = renderHook(() => useGeneration("düğün"));
    await settle();

    await act(async () => {
      await result.current.generate({ prompts: '["a"]', negative: "", variants: 4 });
    });

    expect(result.current.job).toEqual({ status: "running", project: "düğün" });
  });

  it("disables the button the moment stop is pressed, without waiting for the server", async () => {
    getStatus.mockResolvedValue(RUNNING);
    listFrames.mockResolvedValue([]);
    let resolveStop;
    stopGeneration.mockReturnValue(new Promise((resolve) => { resolveStop = resolve; }));

    const { result } = renderHook(() => useGeneration("düğün"));
    await settle();

    act(() => { result.current.stop(); });
    expect(result.current.stopping).toBe(true);

    await act(async () => { resolveStop({ ...RUNNING, stopping: true }); });
    expect(result.current.stopping).toBe(true);
  });

  it("shows the new order straight after a drag and writes it to the server", async () => {
    getStatus.mockResolvedValue({ status: "idle" });
    listFrames.mockResolvedValue([{ file: "1_a.png" }, { file: "0_a.png" }]);
    saveOrder.mockResolvedValue({ order: ["0_a.png", "1_a.png"] });

    const { result } = renderHook(() => useGeneration("düğün"));
    await settle();

    await act(async () => { await result.current.reorder(["0_a.png", "1_a.png"]); });

    expect(result.current.frames.map((p) => p.file)).toEqual(["0_a.png", "1_a.png"]);
    expect(saveOrder).toHaveBeenCalledWith("düğün", ["0_a.png", "1_a.png"]);
  });

  it("shows the error and falls back to the server's order when the ordering cannot be saved", async () => {
    getStatus.mockResolvedValue({ status: "idle" });
    listFrames.mockResolvedValue([{ file: "1_a.png" }, { file: "0_a.png" }]);
    saveOrder.mockRejectedValue(new Error("Sunucuya ulaşılamadı — bağlantıyı kontrol et.\nkopuk"));

    const { result } = renderHook(() => useGeneration("düğün"));
    await settle();

    await act(async () => { await result.current.reorder(["0_a.png", "1_a.png"]); });
    await settle();

    expect(result.current.error).toContain("Sıra kaydedilemedi");
    expect(result.current.frames.map((p) => p.file)).toEqual(["1_a.png", "0_a.png"]);
  });

  it("does not let a poll answer during a save bounce the order back", async () => {
    getStatus.mockResolvedValue(RUNNING);
    listFrames.mockResolvedValue([{ file: "1_a.png" }, { file: "0_a.png" }]);
    let finishSave;
    saveOrder.mockReturnValue(new Promise((resolve) => { finishSave = resolve; }));

    const { result } = renderHook(() => useGeneration("düğün"));
    await settle();

    act(() => { result.current.reorder(["0_a.png", "1_a.png"]); });
    await settle(2000);   // a poll lands mid-save carrying the server's older order

    expect(result.current.frames.map((p) => p.file)).toEqual(["0_a.png", "1_a.png"]);

    await act(async () => { finishSave({ order: ["0_a.png", "1_a.png"] }); });
  });

  it("keeps the button disabled while the server reports it is stopping", async () => {
    getStatus.mockResolvedValue({ ...RUNNING, stopping: true });
    listFrames.mockResolvedValue([]);

    const { result } = renderHook(() => useGeneration("düğün"));
    await settle();

    expect(result.current.stopping).toBe(true);
  });
});
