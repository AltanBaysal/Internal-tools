import { act, fireEvent, render, screen, within } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import {
  listReferences,
  removeReference,
  saveReferenceOrder,
  uploadReferences,
} from "../../shared/api.js";
import ReferencePanel from "./ReferencePanel.jsx";

vi.mock("../../shared/api.js", () => ({
  listReferences: vi.fn(),
  removeReference: vi.fn(),
  saveReferenceOrder: vi.fn(),
  uploadReferences: vi.fn(),
  referenceUrl: (project, name) => `/references/${project}/${name}`,
}));

const LIMITS = { picture: 9, video: 3, audio: 3 };

const POOL = {
  references: [{ name: "kedi.png", kind: "picture", seconds: null, slot: 1 }],
  limits: LIMITS,
};

function pool(references) {
  return { references, limits: LIMITS };
}

async function open(answer = POOL) {
  listReferences.mockResolvedValue(answer);
  const view = render(<ReferencePanel project="düğün" onClose={() => {}} />);
  await act(async () => {});
  return view;
}

function pick(files) {
  fireEvent.change(screen.getByLabelText("Ekle"), { target: { files } });
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe("ReferencePanel", () => {
  it("heads each row with how full it is", async () => {
    // The limits come down with the pool: a copy of them here would go on being right about the
    // old numbers the day they change (madde 298 owns them).
    await open();

    expect(screen.getByText("Fotoğraflar 1/9")).toBeTruthy();
    expect(screen.getByText("Videolar 0/3")).toBeTruthy();
    expect(screen.getByText("Sesler 0/3")).toBeTruthy();
  });

  it("keeps the rows when the pool is empty", async () => {
    // The panel's job is to build the pool, so it has to say what can go in it.
    await open(pool([]));

    expect(screen.getByText("Fotoğraflar 0/9")).toBeTruthy();
  });

  it("draws a picture from the server", async () => {
    await open();

    expect(screen.getByAltText("kedi.png").getAttribute("src"))
      .toBe("/references/düğün/kedi.png");
  });

  it("says how long a clip runs", async () => {
    await open(pool([{ name: "dans.mp4", kind: "video", seconds: 4.2, slot: 1 }]));

    expect(screen.getByText("4,2 sn")).toBeTruthy();
  });

  it("draws the slot a deleted reference left empty", async () => {
    // The gap is the point of madde 300: what is left does not slide up, so the user can see the
    // hole and drag it closed.
    await open(pool([{ name: "bir.png", kind: "picture", seconds: null, slot: 1 },
                     { name: "üç.png", kind: "picture", seconds: null, slot: 3 }]));

    expect(screen.getByLabelText("2. yuva boş")).toBeTruthy();
    expect(screen.queryByLabelText("1. yuva boş")).toBeNull();
  });

  it("sends the order a drag makes", async () => {
    const { container } = await open(pool([
      { name: "bir.png", kind: "picture", seconds: null, slot: 1 },
      { name: "iki.png", kind: "picture", seconds: null, slot: 2 },
    ]));
    saveReferenceOrder.mockResolvedValue(pool([]));
    const tile = (name) => container.querySelector(`[data-reference="${name}"]`);

    await act(async () => {
      fireEvent.dragStart(tile("iki.png"));
      fireEvent.dragOver(tile("bir.png"));
      fireEvent.drop(tile("bir.png"));
    });

    // The whole row goes down, because a slot is a place in a sequence and the sequence is what
    // the server stores.
    expect(saveReferenceOrder).toHaveBeenCalledWith("düğün",
                                                    { picture: ["iki.png", "bir.png"] });
  });

  it("sends the files that were picked, and draws what comes back", async () => {
    await open(pool([]));
    const file = new File([new Uint8Array([1])], "kedi.png", { type: "image/png" });
    uploadReferences.mockResolvedValue(POOL);

    await act(async () => { pick([file]); });

    expect(uploadReferences).toHaveBeenCalledWith("düğün", [file]);
    expect(screen.getByText("Fotoğraflar 1/9")).toBeTruthy();
  });

  it("shows the server's own refusal", async () => {
    await open(pool([]));
    uploadReferences.mockRejectedValue(new Error("uzun.mp4 20 saniye — bir referans klibi 2-15 "
                                                 + "saniye arası olmalı."));

    await act(async () => { pick([new File([new Uint8Array([1])], "uzun.mp4")]); });

    // The sentence lives in the backend and the screen prints it: one place for the rule and its
    // wording.
    expect(screen.getByText(/2-15 saniye arası olmalı/)).toBeTruthy();
  });

  it("asks before taking a reference out", async () => {
    await open();
    removeReference.mockResolvedValue(pool([]));

    fireEvent.click(screen.getByLabelText("kedi.png referansını sil"));

    expect(screen.getByText("kedi.png silinsin mi?")).toBeTruthy();
    expect(removeReference).not.toHaveBeenCalled();

    await act(async () => { fireEvent.click(screen.getAllByText("Sil").at(-1)); });

    expect(removeReference).toHaveBeenCalledWith("düğün", "kedi.png");
    expect(screen.getByText("Fotoğraflar 0/9")).toBeTruthy();
  });
});

describe("ReferencePanel — what a row shows (madde 319)", () => {
  const tile = (container, name) => container.querySelector(`[data-reference="${name}"]`);
  const addCard = (container, kind) => container.querySelector(`[data-add="${kind}"]`);

  it("draws each reference at 144 × 108 with its slot number on it", async () => {
    const { container } = await open(pool([
      { name: "bir.png", kind: "picture", seconds: null, slot: 1 },
      { name: "iki.png", kind: "picture", seconds: null, slot: 2 },
    ]));

    // The number a prompt calls it by: the N of <Picture N>.
    expect(within(tile(container, "iki.png")).getByText("2")).toBeTruthy();
    const face = screen.getByAltText("iki.png");
    expect(face.style.width).toBe("144px");
    expect(face.style.height).toBe("108px");
  });

  it("follows a row's last reference with one Ekle card", async () => {
    const { container } = await open();

    const card = addCard(container, "picture");
    expect(card.textContent).toContain("Ekle");
    // After the reference, not before it: a new one goes in at the end.
    expect(card.previousElementSibling).toBe(tile(container, "kedi.png"));
  });

  it("gives a full row no Ekle card", async () => {
    const { container } = await open(pool([1, 2, 3].map((slot) => (
      { name: `klip-${slot}.mp4`, kind: "video", seconds: 3, slot }))));

    expect(addCard(container, "video")).toBeNull();
    expect(addCard(container, "picture")).toBeTruthy();
  });

  it("shows an empty pool as three rows holding only their Ekle cards", async () => {
    const { container } = await open(pool([]));

    expect(["picture", "video", "audio"].map((kind) => Boolean(addCard(container, kind))))
      .toEqual([true, true, true]);
    expect(container.querySelector("[data-reference]")).toBeNull();
  });
});
