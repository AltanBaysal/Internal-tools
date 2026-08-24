import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("../../shared/api.js", () => ({
  listModels: vi.fn(),
}));

async function settle() {
  await act(async () => { await Promise.resolve(); });
}

// What the machine last answered is remembered for the length of a visit, and that memory lives in
// the module. So each test gets the module itself fresh -- otherwise one test's answer would be
// the next test's starting point. Both are imported from the same fresh registry: taking the hook
// from the new one and the fake from the old would leave them talking to two different mocks.
let listModels;
let useModels;

beforeEach(async () => {
  vi.resetModules();
  ({ listModels } = await import("../../shared/api.js"));
  ({ useModels } = await import("./useModels.js"));
  // resetModules does not re-run a vi.mock factory, so the fake is the same object every test and
  // carries its calls over. The hook beside it really is new; only its history has to be cleared.
  vi.clearAllMocks();
});

describe("useModels", () => {
  it("reports what the renderer has, in the order it reported it", async () => {
    listModels.mockResolvedValue(["nova.safetensors", "başka.safetensors"]);

    const { result } = renderHook(() => useModels());
    expect(result.current.models).toBeNull();      // not known yet, not "none installed"
    await settle();

    expect(result.current.models).toEqual(["nova.safetensors", "başka.safetensors"]);
    expect(result.current.error).toBeNull();
  });

  it("answers an unreadable list with an empty one and the server's own words", async () => {
    listModels.mockRejectedValue(new Error("Sunucuya ulaşılamadı — bağlantıyı kontrol et."));

    const { result } = renderHook(() => useModels());
    await settle();

    // Empty, not null: the panel has to stop waiting and let the queue be used regardless.
    expect(result.current.models).toEqual([]);
    expect(result.current.error).toContain("Sunucuya ulaşılamadı");
  });

  it("opens with the list it already learned", async () => {
    listModels.mockResolvedValue(["nova.safetensors"]);

    const first = renderHook(() => useModels());
    await settle();
    first.unmount();

    // Coming back from a frame builds this hook again. The box saying yükleniyor… over a list the
    // screen already had is the flicker this removes.
    const { result } = renderHook(() => useModels());
    expect(result.current.models).toEqual(["nova.safetensors"]);
  });

  it("keeps the learned list when the next read cannot be made", async () => {
    listModels.mockResolvedValue(["nova.safetensors"]);

    const first = renderHook(() => useModels());
    await settle();
    first.unmount();

    listModels.mockRejectedValue(new Error("Sunucuya ulaşılamadı."));
    const { result } = renderHook(() => useModels());
    await settle();

    // Emptying a box over a refresh that fell over is not quiet. With nothing remembered yet the
    // answer is still the empty list -- that is the test above this one.
    expect(result.current.models).toEqual(["nova.safetensors"]);
  });
});
