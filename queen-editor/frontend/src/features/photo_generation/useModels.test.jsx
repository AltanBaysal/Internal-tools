import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { listModels } from "../../shared/api.js";
import { useModels } from "./useModels.js";

vi.mock("../../shared/api.js", () => ({
  listModels: vi.fn(),
}));

async function settle() {
  await act(async () => { await Promise.resolve(); });
}

beforeEach(() => {
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
});
