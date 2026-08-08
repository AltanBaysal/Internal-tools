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

const done = (file) => ({ file, status: "done" });
const FRAMES = [done("2_a.png"), done("1_a.png"), done("0_a.png")];

beforeEach(() => {
  vi.clearAllMocks();
});

// jsdom has no DataTransfer, so the component must not depend on one: it tracks the dragged tile
// in its own state, which is also what makes the drop slot possible.
function tileOf(name) {
  return document.getElementById(`tile-${name}`);
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
    <Gallery project="düğün" frames={FRAMES} current={null} onReorder={() => {}}
             onDelete={() => Promise.resolve()} {...props} />,
  );
}

function dragTile(fromName, toName) {
  fireEvent.dragStart(tileOf(fromName));
  fireEvent.dragOver(tileOf(toName));
  fireEvent.drop(tileOf(toName));
}

describe("Gallery ordering", () => {
  it("counts the badge up from the bottom, so the newest frame carries the largest number", () => {
    renderGallery();

    expect(tileOf("2_a.png").textContent).toContain("3");
    expect(tileOf("1_a.png").textContent).toContain("2");
    expect(tileOf("0_a.png").textContent).toContain("1");
  });

  it("reports the new order when a frame is dropped", () => {
    const onReorder = vi.fn();
    renderGallery({ onReorder });

    dragTile("0_a.png", "2_a.png");

    expect(onReorder).toHaveBeenCalledWith(["0_a.png", "2_a.png", "1_a.png"]);
  });

  it("does not go to the server for a frame dropped where it already was", () => {
    const onReorder = vi.fn();
    renderGallery({ onReorder });

    dragTile("1_a.png", "1_a.png");

    expect(onReorder).not.toHaveBeenCalled();
  });

  it("goes to the detail page when a frame is clicked", () => {
    renderGallery();

    const link = tileOf("2_a.png").querySelector("a");
    expect(link.getAttribute("href")).toBe(
      `/projects/${encodeURIComponent("düğün")}/photos/2_a.png`);
  });

});

describe("Gallery — one sequence, four states", () => {
  const MIXED = [
    { file: "4_a.png", status: "pending" },
    { file: "3_a.png", status: "pending" },   // this one is the live worker's
    { file: "2_a.png", status: "failed" },
    done("1_a.png"),
    done("0_a.png"),
  ];

  it("keeps every frame in its own place whatever became of it", () => {
    renderGallery({ frames: MIXED, current: "3_a.png" });

    const files = [...document.querySelectorAll("[data-tile]")]
      .map((tile) => tile.id.slice("tile-".length));
    expect(files).toEqual(["4_a.png", "3_a.png", "2_a.png", "1_a.png", "0_a.png"]);
  });

  it("badges the waiting and failed frames too, from the same sequence", () => {
    renderGallery({ frames: MIXED, current: "3_a.png" });

    expect(tileOf("4_a.png").textContent).toContain("5");
    expect(tileOf("2_a.png").textContent).toContain("3");
    expect(tileOf("0_a.png").textContent).toContain("1");
  });

  it("draws a failed frame once, red, with its own way back", () => {
    const onRetry = vi.fn();
    renderGallery({ frames: MIXED, current: null, onRetry });

    // Once: not a red tile and a dashed one at the same time.
    expect(screen.getAllByText("bekliyor")).toHaveLength(2);
    fireEvent.click(screen.getByText("Tekrar dene"));

    expect(onRetry).toHaveBeenCalledWith("2_a.png");
  });

  it("turns the frame the worker is holding into a spinner without moving it", () => {
    renderGallery({ frames: MIXED, current: "3_a.png" });

    // Four of the five are not photos; only the one the worker holds stops saying "bekliyor".
    expect(screen.getAllByText("bekliyor")).toHaveLength(1);
    expect(tileOf("3_a.png").textContent).toContain("4");
  });

  it("lets only a produced frame be picked up", () => {
    renderGallery({ frames: MIXED, current: null });

    expect(tileOf("1_a.png").draggable).toBe(true);
    expect(tileOf("4_a.png").draggable).toBe(false);
    expect(tileOf("2_a.png").draggable).toBe(false);
  });

  it("does not claim the gallery is empty when only waiting frames are in it", () => {
    renderGallery({ frames: [{ file: "0_a.png", status: "pending" }] });

    expect(screen.queryByText("henüz fotoğraf yok")).toBeNull();
    expect(screen.getByText("bekliyor")).toBeTruthy();
  });
});

describe("Gallery selection mode", () => {
  it("opens the mode and selects that frame when the ring is clicked", () => {
    renderGallery();

    fireEvent.click(checkOf("1_a.png"));

    expect(screen.getByText("1 seçili")).toBeTruthy();
    expect(navigate).not.toHaveBeenCalled();
  });

  it("selects and deselects in the mode without opening the detail page", () => {
    renderGallery();
    fireEvent.click(checkOf("1_a.png"));

    fireEvent.click(photoOf("2_a.png"));
    expect(screen.getByText("2 seçili")).toBeTruthy();

    fireEvent.click(photoOf("2_a.png"));
    expect(screen.getByText("1 seçili")).toBeTruthy();
    expect(navigate).not.toHaveBeenCalled();
  });

  it("selects everything, and clears the selection on a second press", () => {
    renderGallery();
    fireEvent.click(checkOf("1_a.png"));

    fireEvent.click(screen.getByText("Tümünü seç"));
    expect(screen.getByText("3 seçili")).toBeTruthy();

    fireEvent.click(screen.getByText("Tümünü seç"));
    expect(screen.getByText("0 seçili")).toBeTruthy();
  });

  it("closes the mode on cancel and on Esc", () => {
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

  it("asks before deleting, then reports what was selected", async () => {
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

  it("disables delete while nothing is selected", () => {
    renderGallery();
    fireEvent.click(checkOf("1_a.png"));
    fireEvent.click(photoOf("1_a.png"));  // deselect: the mode stays open, the button goes dead

    expect(screen.getByText("0 seçili")).toBeTruthy();
    expect(screen.getByText("Sil").closest("button").disabled).toBe(true);
  });
});
