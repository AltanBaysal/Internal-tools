import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { generateBatch, getStatus, listPhotos, stopGeneration } from "../../shared/api.js";
import { useGeneration } from "./useGeneration.js";

vi.mock("../../shared/api.js", () => ({
  generateBatch: vi.fn(),
  getStatus: vi.fn(),
  listPhotos: vi.fn(),
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
  it("açılışta fotoğrafları bilinmez sayar ve ilk poll'da hem durumu hem fotoğrafları ister", async () => {
    getStatus.mockResolvedValue({ status: "idle" });
    listPhotos.mockResolvedValue([]);

    const { result } = renderHook(() => useGeneration("düğün"));
    expect(result.current.photos).toBeNull();

    await settle();

    expect(result.current.photos).toEqual([]);
    expect(getStatus).toHaveBeenCalledTimes(1);
    expect(listPhotos).toHaveBeenCalledWith("düğün");
  });

  it("üretim sürerken 2 saniyede bir sorar, bitince zinciri durdurur", async () => {
    getStatus.mockResolvedValue(RUNNING);
    listPhotos.mockResolvedValue([]);

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

  it("poll patlarsa hatayı gösterir, denemeyi sürdürür ve bağlantı dönünce hatayı siler", async () => {
    const dead = new Error("Sunucuya ulaşılamadı — bağlantıyı kontrol et.\nZaman aşımı (10 sn)");
    getStatus.mockRejectedValue(dead);
    listPhotos.mockRejectedValue(dead);

    const { result } = renderHook(() => useGeneration("düğün"));
    await settle();
    expect(result.current.error).toContain("Sunucuya ulaşılamadı");

    await settle(2000);
    expect(getStatus).toHaveBeenCalledTimes(2);

    getStatus.mockResolvedValue({ status: "idle" });
    listPhotos.mockResolvedValue([]);
    await settle(2000);
    expect(result.current.error).toBeNull();
  });

  it("üretim biterken fotoğrafları bir kez daha ister", async () => {
    getStatus.mockResolvedValue(RUNNING);
    listPhotos.mockResolvedValue([]);

    renderHook(() => useGeneration("düğün"));
    await settle();
    const afterFirstPoll = listPhotos.mock.calls.length;

    getStatus.mockResolvedValue(DONE);
    await settle(2000);

    // The poll's own refresh plus one extra for the frame still landing on Drive.
    expect(listPhotos.mock.calls.length).toBe(afterFirstPoll + 2);
  });

  it("cevap gelmeden ekrandan çıkılırsa zincir kendini diriltmez", async () => {
    // Unmounting while a poll is still in flight is the only way the chain can outlive the screen:
    // the effect's cleanup clears the pending timer, but the failing request that lands afterwards
    // would arm a brand new one that nobody owns.
    let rejectStatus;
    getStatus.mockReturnValue(new Promise((_, reject) => { rejectStatus = reject; }));
    listPhotos.mockRejectedValue(new Error("kopuk"));

    const { unmount } = renderHook(() => useGeneration("düğün"));
    const callsBefore = getStatus.mock.calls.length;

    unmount();
    await act(async () => { rejectStatus(new Error("kopuk")); });
    await settle(10_000);

    expect(getStatus.mock.calls.length).toBe(callsBefore);
  });

  it("üretim başlayınca panel beklemeden üretim durumuna geçer", async () => {
    getStatus.mockResolvedValue({ status: "idle" });
    listPhotos.mockResolvedValue([]);
    generateBatch.mockResolvedValue({ started: true });

    const { result } = renderHook(() => useGeneration("düğün"));
    await settle();

    await act(async () => {
      await result.current.generate({ prompts: '["a"]', negative: "", variants: 4 });
    });

    expect(result.current.job).toEqual({
      status: "running", project: "düğün", done: 0, failed: 0, total: 0,
    });
  });

  it("durdura basıldığı an butonu pasifler, sunucu cevabını beklemez", async () => {
    getStatus.mockResolvedValue(RUNNING);
    listPhotos.mockResolvedValue([]);
    let resolveStop;
    stopGeneration.mockReturnValue(new Promise((resolve) => { resolveStop = resolve; }));

    const { result } = renderHook(() => useGeneration("düğün"));
    await settle();

    act(() => { result.current.stop(); });
    expect(result.current.stopping).toBe(true);

    await act(async () => { resolveStop({ ...RUNNING, stopping: true }); });
    expect(result.current.stopping).toBe(true);
  });

  it("sunucunun bildirdiği durduruluyor bilgisi de butonu pasif tutar", async () => {
    getStatus.mockResolvedValue({ ...RUNNING, stopping: true });
    listPhotos.mockResolvedValue([]);

    const { result } = renderHook(() => useGeneration("düğün"));
    await settle();

    expect(result.current.stopping).toBe(true);
  });
});
