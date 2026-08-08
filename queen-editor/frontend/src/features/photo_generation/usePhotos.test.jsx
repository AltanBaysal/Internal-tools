import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { deletePhotos, listPhotos } from "../../shared/api.js";
import { usePhotos } from "./usePhotos.js";

vi.mock("../../shared/api.js", () => ({
  deletePhotos: vi.fn(),
  listPhotos: vi.fn(),
}));

async function settle() {
  await act(async () => { await Promise.resolve(); });
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe("usePhotos", () => {
  it("reads the list in gallery order", async () => {
    listPhotos.mockResolvedValue([{ file: "1_a.png" }, { file: "0_a.png" }]);

    const { result } = renderHook(() => usePhotos("düğün"));
    expect(result.current.photos).toBeNull();
    await settle();

    expect(result.current.photos.map((p) => p.file)).toEqual(["1_a.png", "0_a.png"]);
  });

  it("drops a deleted photo from the list", async () => {
    listPhotos.mockResolvedValue([{ file: "1_a.png" }, { file: "0_a.png" }]);
    deletePhotos.mockResolvedValue({ deleted: ["1_a.png"] });

    const { result } = renderHook(() => usePhotos("düğün"));
    await settle();
    await act(async () => { await result.current.remove("1_a.png"); });

    expect(deletePhotos).toHaveBeenCalledWith("düğün", ["1_a.png"]);
    expect(result.current.photos.map((p) => p.file)).toEqual(["0_a.png"]);
  });

  it("leaves the list alone and reports the error when a delete fails", async () => {
    listPhotos.mockResolvedValue([{ file: "0_a.png" }]);
    deletePhotos.mockRejectedValue(new Error("Fotoğraf yok: 0_a.png"));

    const { result } = renderHook(() => usePhotos("düğün"));
    await settle();
    await act(async () => { await result.current.remove("0_a.png"); });

    expect(result.current.error).toContain("Fotoğraf yok");
    expect(result.current.photos.map((p) => p.file)).toEqual(["0_a.png"]);
  });
});
