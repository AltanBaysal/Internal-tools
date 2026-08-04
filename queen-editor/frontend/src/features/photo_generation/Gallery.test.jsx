import { act, fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { navigate } from "../../shared/router.js";
import Gallery from "./Gallery.jsx";

vi.mock("../../shared/api.js", () => ({
  photoUrl: (project, file) => `/photos/${project}/${file}`,
}));
vi.mock("../../shared/router.js", () => ({
  navigate: vi.fn(),
  photoPath: (project, file) => `/projects/${encodeURIComponent(project)}/photos/${file}`,
}));

const PHOTOS = [{ file: "2_a.png" }, { file: "1_a.png" }, { file: "0_a.png" }];

beforeEach(() => {
  vi.clearAllMocks();
});

// jsdom has no DataTransfer, so the component must not depend on one: it tracks the dragged tile
// in its own state, which is also what makes the drop slot possible.
function tileOf(name) {
  return screen.getByText(name).closest("[data-tile]");
}

function checkOf(name) {
  return tileOf(name).querySelector("[data-check]");
}

// What the user actually presses is the photo, which is a link -- clicking the tile's padding
// would miss the very handler that has to know about selection mode.
function photoOf(name) {
  return tileOf(name).querySelector("a");
}

function renderGallery(props) {
  return render(
    <Gallery project="düğün" photos={PHOTOS} current={null} onReorder={() => {}}
             onDelete={() => Promise.resolve()} {...props} />,
  );
}

function dragTile(fromName, toName) {
  fireEvent.dragStart(tileOf(fromName));
  fireEvent.dragOver(tileOf(toName));
  fireEvent.drop(tileOf(toName));
}

describe("Gallery sıralama", () => {
  it("her kareye sıra rozetini basar", () => {
    renderGallery();

    expect(screen.getByText("1")).toBeTruthy();
    expect(screen.getByText("2")).toBeTruthy();
    expect(screen.getByText("3")).toBeTruthy();
  });

  it("kare bırakıldığında yeni sırayı bildirir", () => {
    const onReorder = vi.fn();
    renderGallery({ onReorder });

    dragTile("0_a.png", "2_a.png");

    expect(onReorder).toHaveBeenCalledWith(["0_a.png", "2_a.png", "1_a.png"]);
  });

  it("aynı yere bırakılan kare için sunucuya gitmez", () => {
    const onReorder = vi.fn();
    renderGallery({ onReorder });

    dragTile("1_a.png", "1_a.png");

    expect(onReorder).not.toHaveBeenCalled();
  });

  it("kareye tıklayınca detay sayfasına gider", () => {
    renderGallery();

    const link = tileOf("2_a.png").querySelector("a");
    expect(link.getAttribute("href")).toBe(
      `/projects/${encodeURIComponent("düğün")}/photos/2_a.png`);
  });

  it("üretilen kare rozet almaz", () => {
    renderGallery({ current: { number: 3, letter: "a", prompt: "p" } });

    // Three photos, three badges -- the spinner tile is not in the record and has no place yet.
    expect(screen.queryByText("4")).toBeNull();
  });
});

describe("Gallery seçim modu", () => {
  it("halkaya tıklayınca mod açılır ve o kare seçilir", () => {
    renderGallery();

    fireEvent.click(checkOf("1_a.png"));

    expect(screen.getByText("1 seçili")).toBeTruthy();
    expect(navigate).not.toHaveBeenCalled();
  });

  it("modda kareye tıklamak seçer, kaldırır ve detaya gitmez", () => {
    renderGallery();
    fireEvent.click(checkOf("1_a.png"));

    fireEvent.click(photoOf("2_a.png"));
    expect(screen.getByText("2 seçili")).toBeTruthy();

    fireEvent.click(photoOf("2_a.png"));
    expect(screen.getByText("1 seçili")).toBeTruthy();
    expect(navigate).not.toHaveBeenCalled();
  });

  it("Tümünü seç hepsini seçer, ikinci basış temizler", () => {
    renderGallery();
    fireEvent.click(checkOf("1_a.png"));

    fireEvent.click(screen.getByText("Tümünü seç"));
    expect(screen.getByText("3 seçili")).toBeTruthy();

    fireEvent.click(screen.getByText("Tümünü seç"));
    expect(screen.getByText("0 seçili")).toBeTruthy();
  });

  it("Vazgeç ve Esc modu kapatır", () => {
    const { unmount } = renderGallery();
    fireEvent.click(checkOf("1_a.png"));

    fireEvent.click(screen.getByText("Vazgeç"));
    expect(screen.queryByText("1 seçili")).toBeNull();
    unmount();

    renderGallery();
    fireEvent.click(checkOf("1_a.png"));
    fireEvent.keyDown(window, { key: "Escape" });
    expect(screen.queryByText("1 seçili")).toBeNull();
  });

  it("Sil önce onay ister, onayda seçilenleri bildirir", async () => {
    const onDelete = vi.fn().mockResolvedValue(null);
    renderGallery({ onDelete });
    fireEvent.click(checkOf("1_a.png"));
    fireEvent.click(photoOf("0_a.png"));

    fireEvent.click(screen.getByText("Sil"));
    expect(screen.getByText("2 fotoğraf silinsin mi?")).toBeTruthy();
    expect(onDelete).not.toHaveBeenCalled();

    // The modal's confirm is the second Sil on screen; the bar's is the first.
    await act(async () => { fireEvent.click(screen.getAllByText("Sil").at(-1)); });

    expect(onDelete).toHaveBeenCalledWith(["1_a.png", "0_a.png"]);
  });

  it("seçim yokken Sil pasiftir", () => {
    renderGallery();
    fireEvent.click(checkOf("1_a.png"));
    fireEvent.click(photoOf("1_a.png"));  // deselect: the mode stays open, the button goes dead

    expect(screen.getByText("0 seçili")).toBeTruthy();
    expect(screen.getByText("Sil").closest("button").disabled).toBe(true);
  });
});
