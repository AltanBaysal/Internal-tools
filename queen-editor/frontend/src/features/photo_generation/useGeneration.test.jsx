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
  it("names the frame being rendered from the job's identity", async () => {
    getStatus.mockResolvedValue({ ...RUNNING, current: { id: "P11_3", prompt: "a" } });
    listFrames.mockResolvedValue([]);

    const { result } = renderHook(() => useGeneration("düğün"));
    await settle();

    expect(result.current.current).toBe("P11_3");
  });

  it("says which layer the worker is making, not just which frame", async () => {
    getStatus.mockResolvedValue({ ...RUNNING, current: { id: "P0_0", type: "video" } });
    listFrames.mockResolvedValue([]);

    const { result } = renderHook(() => useGeneration("düğün"));
    await settle();

    expect(result.current.current).toBe("P0_0");
    expect(result.current.currentLayer).toBe("video");
  });

  it("counts what is owed for each kind of job, not one lump", async () => {
    // Three frames with no line on disk; one of them is the one the worker is on right now.
    getStatus.mockResolvedValue({ ...RUNNING, current: { id: "P0_0" } });
    listFrames.mockResolvedValue([
      { id: "P0_0", file: "P0_0.png", status: "pending", owed: ["photo"], failed: [] },
      { id: "P1_0", file: "P1_0.png", status: "pending", owed: ["photo"], failed: [] },
      { id: "P2_0", file: "P2_0.png", status: "pending", owed: ["photo"], failed: [] },
    ]);

    const { result } = renderHook(() => useGeneration("düğün"));
    await settle();

    expect(result.current.queue).toEqual([{ layer: "photo", owed: 2 }]);
  });

  it("counts the half-done job again once the queue is paused", async () => {
    // Paused: the worker reports no current job, so the frame it cut is owed again -- 2 becomes 3.
    getStatus.mockResolvedValue({ status: "paused", project: "düğün" });
    listFrames.mockResolvedValue([
      { id: "P0_0", file: "P0_0.png", status: "pending", owed: ["photo"], failed: [] },
      { id: "P1_0", file: "P1_0.png", status: "pending", owed: ["photo"], failed: [] },
      { id: "P2_0", file: "P2_0.png", status: "pending", owed: ["photo"], failed: [] },
    ]);

    const { result } = renderHook(() => useGeneration("düğün"));
    await settle();

    expect(result.current.current).toBeNull();
    expect(result.current.queue).toEqual([{ layer: "photo", owed: 3 }]);
  });

  it("counts what failed for each kind of job", async () => {
    getStatus.mockResolvedValue({ status: "done", project: "düğün" });
    listFrames.mockResolvedValue([
      { id: "P0_0", file: "P0_0.png", status: "failed", owed: [], failed: ["photo"] },
      { id: "P1_0", file: "P1_0.png", status: "failed", owed: [], failed: ["photo"] },
      { id: "P2_0", file: "P2_0.png", status: "done", owed: [], failed: [] },
    ]);

    const { result } = renderHook(() => useGeneration("düğün"));
    await settle();

    expect(result.current.failures).toEqual([{ layer: "photo", count: 2 }]);
  });

  it("counts the video jobs the frames say they are owed", async () => {
    getStatus.mockResolvedValue({ status: "done", project: "düğün" });
    listFrames.mockResolvedValue([
      { id: "P0_0", file: "P0_0.png", status: "done", layers: {}, owed: ["video"], failed: [] },
      { id: "P1_0", file: "P1_0.png", status: "done", layers: {}, owed: [], failed: ["video"] },
    ]);

    const { result } = renderHook(() => useGeneration("düğün"));
    await settle();

    expect(result.current.queue).toEqual([{ layer: "video", owed: 1 }]);
    expect(result.current.failures).toEqual([{ layer: "video", count: 1 }]);
  });

  it("leaves out a kind with nothing owed", async () => {
    getStatus.mockResolvedValue({ status: "idle" });
    listFrames.mockResolvedValue([{ id: "P0_0", file: "P0_0.png", status: "done",
                                    owed: [], failed: [] }]);

    const { result } = renderHook(() => useGeneration("düğün"));
    await settle();

    expect(result.current.queue).toEqual([]);
  });

  it("treats the photos as unknown at first and asks for both status and photos on the first poll", async () => {
    getStatus.mockResolvedValue({ status: "idle" });
    listFrames.mockResolvedValue([]);

    // Its own project name: a gallery already answered for is remembered across mounts, so only a
    // project nothing has seen still starts out unknown.
    const { result } = renderHook(() => useGeneration("hiç görülmemiş"));
    expect(result.current.frames).toBeNull();

    await settle();

    expect(result.current.frames).toEqual([]);
    expect(getStatus).toHaveBeenCalledTimes(1);
    expect(listFrames).toHaveBeenCalledWith("hiç görülmemiş");
  });

  it("draws the gallery it already had the moment it is mounted again", async () => {
    const rows = [{ id: "P0_0", file: "P0_0.png", status: "done", owed: [], failed: [] }];
    getStatus.mockResolvedValue({ status: "idle" });
    listFrames.mockResolvedValue(rows);

    const first = renderHook(() => useGeneration("hatırlanan"));
    await settle();
    first.unmount();

    // Nothing has answered yet on this mount -- opening a frame's detail and coming back must not
    // blank the screen and start over.
    listFrames.mockReturnValue(new Promise(() => {}));
    const { result } = renderHook(() => useGeneration("hatırlanan"));

    expect(result.current.frames).toEqual(rows);
  });

  it("never hands one project's gallery to another", async () => {
    getStatus.mockResolvedValue({ status: "idle" });
    listFrames.mockResolvedValue([
      { id: "P0_0", file: "P0_0.png", status: "done", owed: [], failed: [] }]);

    const first = renderHook(() => useGeneration("birinci"));
    await settle();
    first.unmount();

    listFrames.mockReturnValue(new Promise(() => {}));
    const { result } = renderHook(() => useGeneration("ikinci"));

    expect(result.current.frames).toBeNull();
  });

  it("remembers the order the tiles were dropped into, not the one before it", async () => {
    const rows = [
      { id: "P0_0", file: "P0_0.png", status: "done", owed: [], failed: [] },
      { id: "P1_0", file: "P1_0.png", status: "done", owed: [], failed: [] },
    ];
    getStatus.mockResolvedValue({ status: "idle" });
    listFrames.mockResolvedValue(rows);
    saveOrder.mockResolvedValue({});

    const first = renderHook(() => useGeneration("sıralı"));
    await settle();
    await act(async () => { await first.result.current.reorder(["P1_0", "P0_0"]); });
    first.unmount();

    listFrames.mockReturnValue(new Promise(() => {}));
    const { result } = renderHook(() => useGeneration("sıralı"));

    expect(result.current.frames.map((frame) => frame.id)).toEqual(["P1_0", "P0_0"]);
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
    listFrames.mockResolvedValue([{ id: "1_a", file: "1_a.png" }, { id: "0_a", file: "0_a.png" }]);
    saveOrder.mockResolvedValue({ order: ["0_a", "1_a"] });

    const { result } = renderHook(() => useGeneration("düğün"));
    await settle();

    await act(async () => { await result.current.reorder(["0_a", "1_a"]); });

    expect(result.current.frames.map((p) => p.id)).toEqual(["0_a", "1_a"]);
    expect(saveOrder).toHaveBeenCalledWith("düğün", ["0_a", "1_a"]);
  });

  it("shows the error and falls back to the server's order when the ordering cannot be saved", async () => {
    getStatus.mockResolvedValue({ status: "idle" });
    listFrames.mockResolvedValue([{ id: "1_a", file: "1_a.png" }, { id: "0_a", file: "0_a.png" }]);
    saveOrder.mockRejectedValue(new Error("Sunucuya ulaşılamadı — bağlantıyı kontrol et.\nkopuk"));

    const { result } = renderHook(() => useGeneration("düğün"));
    await settle();

    await act(async () => { await result.current.reorder(["0_a", "1_a"]); });
    await settle();

    expect(result.current.error).toContain("Sıra kaydedilemedi");
    expect(result.current.frames.map((p) => p.id)).toEqual(["1_a", "0_a"]);
  });

  it("does not let a poll answer during a save bounce the order back", async () => {
    getStatus.mockResolvedValue(RUNNING);
    listFrames.mockResolvedValue([{ id: "1_a", file: "1_a.png" }, { id: "0_a", file: "0_a.png" }]);
    let finishSave;
    saveOrder.mockReturnValue(new Promise((resolve) => { finishSave = resolve; }));

    const { result } = renderHook(() => useGeneration("düğün"));
    await settle();

    act(() => { result.current.reorder(["0_a", "1_a"]); });
    await settle(2000);   // a poll lands mid-save carrying the server's older order

    expect(result.current.frames.map((p) => p.id)).toEqual(["0_a", "1_a"]);

    await act(async () => { finishSave({ order: ["0_a", "1_a"] }); });
  });

  it("keeps the button disabled while the server reports it is stopping", async () => {
    getStatus.mockResolvedValue({ ...RUNNING, stopping: true });
    listFrames.mockResolvedValue([]);

    const { result } = renderHook(() => useGeneration("düğün"));
    await settle();

    expect(result.current.stopping).toBe(true);
  });
});
