import { act, fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { deletePhotos, listPhotos } from "../../shared/api.js";
import { navigate } from "../../shared/router.js";
import PhotoDetail from "./PhotoDetail.jsx";

vi.mock("../../shared/api.js", () => ({
  deletePhotos: vi.fn(),
  listPhotos: vi.fn(),
  photoUrl: (project, file) => `/photos/${project}/${file}`,
}));
vi.mock("../../shared/router.js", () => ({
  navigate: vi.fn(),
  photoPath: (project, file) => `/projects/${project}/photos/${file}`,
  projectPath: (project) => `/projects/${project}`,
}));

const PHOTOS = [{ file: "2_a.png", prompt: "üçüncü" },
                { file: "1_a.png", prompt: "ikinci" },
                { file: "0_a.png", prompt: "ilk" }];

async function settle() {
  await act(async () => { await Promise.resolve(); });
}

async function open(file) {
  listPhotos.mockResolvedValue(PHOTOS);
  render(<PhotoDetail project="düğün" file={file} />);
  await settle();
}

// The panel's own Sil comes first in the document; the modal's is the one added on top.
function confirmButton() {
  return screen.getAllByText("Sil").at(-1);
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe("PhotoDetail", () => {
  it("shows the position, the file name and the prompt", async () => {
    await open("1_a.png");

    expect(screen.getByText("2 / 3")).toBeTruthy();
    expect(screen.getByText("1_a.png")).toBeTruthy();
    expect(screen.getByText(/ikinci/)).toBeTruthy();
  });

  it("moves to the next photo with the arrow", async () => {
    await open("1_a.png");

    fireEvent.click(screen.getByText("›"));

    expect(navigate).toHaveBeenCalledWith("/projects/düğün/photos/0_a.png");
  });

  it("leaves the back arrow dead on the first photo", async () => {
    await open("2_a.png");

    fireEvent.click(screen.getByText("‹"));

    expect(navigate).not.toHaveBeenCalled();
  });

  it("responds to the arrow keys and Esc", async () => {
    await open("1_a.png");

    fireEvent.keyDown(window, { key: "ArrowLeft" });
    expect(navigate).toHaveBeenCalledWith("/projects/düğün/photos/2_a.png");

    fireEvent.keyDown(window, { key: "Escape" });
    expect(navigate).toHaveBeenCalledWith("/projects/düğün");
  });

  it("asks before deleting, then opens the next photo", async () => {
    deletePhotos.mockResolvedValue({ deleted: [] });
    await open("1_a.png");

    fireEvent.click(screen.getByText("Sil"));
    expect(screen.getByText("Bu fotoğraf silinsin mi?")).toBeTruthy();
    expect(deletePhotos).not.toHaveBeenCalled();

    await act(async () => { fireEvent.click(confirmButton()); });

    expect(deletePhotos).toHaveBeenCalledWith("düğün", ["1_a.png"]);
    expect(navigate).toHaveBeenCalledWith("/projects/düğün/photos/0_a.png");
  });

  it("falls back to the previous photo when the last one is deleted", async () => {
    deletePhotos.mockResolvedValue({ deleted: [] });
    await open("0_a.png");

    fireEvent.click(screen.getByText("Sil"));
    await act(async () => { fireEvent.click(confirmButton()); });

    expect(navigate).toHaveBeenCalledWith("/projects/düğün/photos/1_a.png");
  });

  it("shows an error card for a file that is not in the list", async () => {
    await open("yok.png");

    expect(screen.getByText("Fotoğraf bulunamadı")).toBeTruthy();
  });
});
