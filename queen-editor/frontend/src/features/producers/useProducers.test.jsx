import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { installProducer, listProducers } from "../../shared/api.js";
import { useProducers } from "./useProducers.js";

vi.mock("../../shared/api.js", () => ({
  cancelInstall: vi.fn(),
  installProducer: vi.fn(),
  listProducers: vi.fn(),
}));

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
  it("says the install started before the server has answered", async () => {
    // Two round-trips separate the click from any change on screen otherwise, and the user
    // presses Kur again.
    installProducer.mockReturnValue(new Promise(() => {}));
    const { result } = renderHook(() => useProducers());
    await settle();

    act(() => { result.current.install("video"); });

    expect(result.current.producers[1].installing).toBeTruthy();
    expect(result.current.producers[0].installing).toBeFalsy();
  });

  it("takes that back when the request is refused", async () => {
    installProducer.mockRejectedValue(new Error("Video üreticisi zaten kuruluyor."));
    const { result } = renderHook(() => useProducers());
    await settle();

    await act(async () => { await result.current.install("video"); });

    expect(result.current.producers[1].installing).toBeFalsy();
    expect(result.current.error).toBe("Video üreticisi zaten kuruluyor.");
  });
});
