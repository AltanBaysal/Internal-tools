import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { listProducers } from "../../shared/api.js";
import { COLAB_INSTALL, useProducers } from "./useProducers.js";

vi.mock("../../shared/api.js", () => ({ listProducers: vi.fn() }));

const THREE = [
  { id: "photo", name: "Fotoğraf üreticisi", installed: true },
  { id: "video", name: "Video üreticisi", installed: false },
];

async function settle() {
  await act(async () => { await Promise.resolve(); });
}

beforeEach(() => {
  vi.clearAllMocks();
  listProducers.mockResolvedValue(THREE);
});

describe("useProducers", () => {
  it("reads the machine once and does not keep asking", async () => {
    // Nothing installs while the app is up -- the notebook does it before this process starts --
    // so a second read could only return the same answer.
    renderHook(() => useProducers());
    await settle();

    expect(listProducers).toHaveBeenCalledTimes(1);
  });

  it("answers Kur with where the install happens, and asks the server nothing", async () => {
    const { result } = renderHook(() => useProducers());
    await settle();

    act(() => { result.current.install("video"); });

    expect(result.current.producers[1].note).toBe(COLAB_INSTALL);
    expect(result.current.producers[0].note).toBeUndefined();
    expect(listProducers).toHaveBeenCalledTimes(1);
  });

  it("keeps the reason on screen when the list cannot be read", async () => {
    listProducers.mockRejectedValue(new Error("Sunucuya ulaşılamadı."));
    const { result } = renderHook(() => useProducers());
    await settle();

    expect(result.current.error).toBe("Sunucuya ulaşılamadı.");
    expect(result.current.producers).toBeNull();
  });
});
