import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { getMuted, saveMuted } from "../../shared/api.js";
import { useMuted } from "./useMuted.js";

vi.mock("../../shared/api.js", () => ({
  getMuted: vi.fn(),
  saveMuted: vi.fn(),
}));

async function settle() {
  await act(async () => { await Promise.resolve(); });
}

// A promise the test answers when it chooses, so two presses can be in flight at once.
function pending() {
  let answer;
  let refuse;
  const promise = new Promise((resolve, reject) => { answer = resolve; refuse = reject; });
  return { promise, answer, refuse };
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe("useMuted (madde 510)", () => {
  it("reads the project's turned-off sounds once, and knows nothing until then", async () => {
    getMuted.mockResolvedValue(["P0_0"]);

    const { result, rerender } = renderHook(() => useMuted("düğün"));
    expect(result.current.muted).toBeNull();
    await settle();
    rerender();

    expect(result.current.muted).toEqual(["P0_0"]);
    expect(getMuted).toHaveBeenCalledTimes(1);
    expect(getMuted).toHaveBeenCalledWith("düğün");
  });

  it("stays unknown when the list cannot be read", async () => {
    getMuted.mockRejectedValue(new Error("düğün/muted.json okunamıyor: bozuk"));

    const { result } = renderHook(() => useMuted("düğün"));
    await settle();

    expect(result.current.muted).toBeNull();
  });

  it("shows a press at once, writes it, and takes the server's answer for that frame", async () => {
    getMuted.mockResolvedValue([]);
    const write = pending();
    saveMuted.mockReturnValue(write.promise);
    const { result } = renderHook(() => useMuted("düğün"));
    await settle();

    act(() => { result.current.mute("P0_0", true); });

    expect(result.current.muted).toEqual(["P0_0"]);
    expect(saveMuted).toHaveBeenCalledWith("düğün", "P0_0", true);
    // The answer speaks for the frame pressed: whatever else it lists is another press's to say.
    await act(async () => { write.answer(["P1_0", "P0_0"]); });
    expect(result.current.muted).toEqual(["P0_0"]);
  });

  it("takes the server's word for the frame pressed when it differs from the press", async () => {
    getMuted.mockResolvedValue([]);
    saveMuted.mockResolvedValue([]);
    const { result } = renderHook(() => useMuted("düğün"));
    await settle();

    await act(async () => { await result.current.mute("P0_0", true); });

    expect(result.current.muted).toEqual([]);
  });

  it("turns a sound back on the same way", async () => {
    getMuted.mockResolvedValue(["P0_0", "P1_0"]);
    saveMuted.mockResolvedValue(["P1_0"]);
    const { result } = renderHook(() => useMuted("düğün"));
    await settle();

    await act(async () => { await result.current.mute("P0_0", false); });

    expect(saveMuted).toHaveBeenCalledWith("düğün", "P0_0", false);
    expect(result.current.muted).toEqual(["P1_0"]);
  });

  it("puts a refused press back and passes the refusal on", async () => {
    getMuted.mockResolvedValue(["P1_0"]);
    saveMuted.mockRejectedValue(new Error("Bu karenin sesi yok: P0_0"));
    const { result } = renderHook(() => useMuted("düğün"));
    await settle();

    let said;
    await act(async () => {
      await result.current.mute("P0_0", true).catch((err) => { said = err.message; });
    });

    expect(result.current.muted).toEqual(["P1_0"]);
    expect(said).toBe("Bu karenin sesi yok: P0_0");
  });

  it("lets only the last press's answer stand", async () => {
    // Off, then on again before the first answer came: the first answer arriving last must not
    // turn the sound off again on screen.
    getMuted.mockResolvedValue([]);
    const first = pending();
    const second = pending();
    saveMuted.mockReturnValueOnce(first.promise).mockReturnValueOnce(second.promise);
    const { result } = renderHook(() => useMuted("düğün"));
    await settle();

    act(() => { result.current.mute("P0_0", true); });
    act(() => { result.current.mute("P0_0", false); });
    await act(async () => { second.answer([]); });
    await act(async () => { first.answer(["P0_0"]); });

    expect(result.current.muted).toEqual([]);
  });

  it("does not put back, nor report, a press a later one on the same frame replaced", async () => {
    // Its refusal is about a state nobody is looking at any more: no card for it, and no unhandled
    // rejection either -- the press is fired and forgotten here, as a click is.
    getMuted.mockResolvedValue([]);
    const first = pending();
    const second = pending();
    saveMuted.mockReturnValueOnce(first.promise).mockReturnValueOnce(second.promise);
    const { result } = renderHook(() => useMuted("düğün"));
    await settle();

    act(() => { result.current.mute("P0_0", true); });
    act(() => { result.current.mute("P0_0", false); });
    await act(async () => { second.answer([]); });
    await act(async () => { first.refuse(new Error("Sunucuya ulaşılamadı")); });

    expect(result.current.muted).toEqual([]);
  });

  it("keeps a press on one frame when a press on another is answered first", async () => {
    // Off on P0_0, a step with the arrow, off on P1_0 -- and the server serves P1_0 first. Its
    // answer does not know P0_0 yet; P0_0's own answer, arriving last, is the one that does.
    getMuted.mockResolvedValue([]);
    const first = pending();
    const second = pending();
    saveMuted.mockReturnValueOnce(first.promise).mockReturnValueOnce(second.promise);
    const { result } = renderHook(() => useMuted("düğün"));
    await settle();

    act(() => { result.current.mute("P0_0", true); });
    act(() => { result.current.mute("P1_0", true); });
    await act(async () => { second.answer(["P1_0"]); });
    expect([...result.current.muted].sort()).toEqual(["P0_0", "P1_0"]);
    await act(async () => { first.answer(["P1_0", "P0_0"]); });

    expect([...result.current.muted].sort()).toEqual(["P0_0", "P1_0"]);
  });

  it("puts back only the refused frame, and reports it though another frame was pressed since",
     async () => {
    getMuted.mockResolvedValue([]);
    const first = pending();
    const second = pending();
    saveMuted.mockReturnValueOnce(first.promise).mockReturnValueOnce(second.promise);
    const { result } = renderHook(() => useMuted("düğün"));
    await settle();

    let refusedA;
    act(() => {
      result.current.mute("P0_0", true).catch((err) => { refusedA = err.message; });
    });
    act(() => { result.current.mute("P1_0", true); });
    await act(async () => { second.answer(["P1_0"]); });
    await act(async () => { first.refuse(new Error("Sunucuya ulaşılamadı")); });

    expect(result.current.muted).toEqual(["P1_0"]);
    expect(refusedA).toBe("Sunucuya ulaşılamadı");
  });
});
