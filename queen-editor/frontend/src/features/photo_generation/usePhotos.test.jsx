import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { deletePhoto, listPhotos } from "../../shared/api.js";
import { usePhotos } from "./usePhotos.js";

vi.mock("../../shared/api.js", () => ({
  deletePhoto: vi.fn(),
  listPhotos: vi.fn(),
}));

async function settle() {
  await act(async () => { await Promise.resolve(); });
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe("usePhotos", () => {
  it("listeyi galeri sırasıyla okur", async () => {
    listPhotos.mockResolvedValue([{ file: "1_a.png" }, { file: "0_a.png" }]);

    const { result } = renderHook(() => usePhotos("düğün"));
    expect(result.current.photos).toBeNull();
    await settle();

    expect(result.current.photos.map((p) => p.file)).toEqual(["1_a.png", "0_a.png"]);
  });

  it("silinen fotoğrafı listeden çıkarır", async () => {
    listPhotos.mockResolvedValue([{ file: "1_a.png" }, { file: "0_a.png" }]);
    deletePhoto.mockResolvedValue(null);

    const { result } = renderHook(() => usePhotos("düğün"));
    await settle();
    await act(async () => { await result.current.remove("1_a.png"); });

    expect(deletePhoto).toHaveBeenCalledWith("düğün", "1_a.png");
    expect(result.current.photos.map((p) => p.file)).toEqual(["0_a.png"]);
  });

  it("silme başarısızsa listeyi olduğu gibi bırakır ve hatayı söyler", async () => {
    listPhotos.mockResolvedValue([{ file: "0_a.png" }]);
    deletePhoto.mockRejectedValue(new Error("Fotoğraf yok: 0_a.png"));

    const { result } = renderHook(() => usePhotos("düğün"));
    await settle();
    await act(async () => { await result.current.remove("0_a.png"); });

    expect(result.current.error).toContain("Fotoğraf yok");
    expect(result.current.photos.map((p) => p.file)).toEqual(["0_a.png"]);
  });
});
