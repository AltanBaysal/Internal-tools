import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import Gallery from "./Gallery.jsx";

const PHOTOS = [{ file: "2_a.png" }, { file: "1_a.png" }, { file: "0_a.png" }];

// jsdom has no DataTransfer, so the component must not depend on one: it tracks the dragged tile
// in its own state, which is also what makes the drop slot possible.
function tileOf(name) {
  return screen.getByText(name).closest("[draggable]");
}

function dragTile(fromName, toName) {
  fireEvent.dragStart(tileOf(fromName));
  fireEvent.dragOver(tileOf(toName));
  fireEvent.drop(tileOf(toName));
}

describe("Gallery sıralama", () => {
  it("her kareye sıra rozetini basar", () => {
    render(<Gallery project="düğün" photos={PHOTOS} current={null} onReorder={() => {}} />);

    expect(screen.getByText("1")).toBeTruthy();
    expect(screen.getByText("2")).toBeTruthy();
    expect(screen.getByText("3")).toBeTruthy();
  });

  it("kare bırakıldığında yeni sırayı bildirir", () => {
    const onReorder = vi.fn();
    render(<Gallery project="düğün" photos={PHOTOS} current={null} onReorder={onReorder} />);

    dragTile("0_a.png", "2_a.png");

    expect(onReorder).toHaveBeenCalledWith(["0_a.png", "2_a.png", "1_a.png"]);
  });

  it("aynı yere bırakılan kare için sunucuya gitmez", () => {
    const onReorder = vi.fn();
    render(<Gallery project="düğün" photos={PHOTOS} current={null} onReorder={onReorder} />);

    dragTile("1_a.png", "1_a.png");

    expect(onReorder).not.toHaveBeenCalled();
  });

  it("kareye tıklayınca detay sayfasına gider", () => {
    render(<Gallery project="düğün" photos={PHOTOS} current={null} onReorder={() => {}} />);

    const link = screen.getByText("2_a.png").closest("[draggable]").querySelector("a");
    expect(link.getAttribute("href")).toBe(
      `/projects/${encodeURIComponent("düğün")}/photos/2_a.png`);
  });

  it("üretilen kare rozet almaz", () => {
    render(<Gallery project="düğün" photos={PHOTOS} onReorder={() => {}}
                    current={{ number: 3, letter: "a", prompt: "p" }} />);

    // Three photos, three badges -- the spinner tile is not in the record and has no place yet.
    expect(screen.queryByText("4")).toBeNull();
  });
});
