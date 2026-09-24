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

// A row's own Ekle card picks into that row (madde 320); the picture row's unless said otherwise.
function pick(files, card = "fotoğraf ekle") {
  fireEvent.change(screen.getByLabelText(card), { target: { files } });
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

    expect(uploadReferences).toHaveBeenCalledWith("düğün", [file], "picture");
    expect(screen.getByText("Fotoğraflar 1/9")).toBeTruthy();
  });

  it("shows the server's own refusal", async () => {
    await open(pool([]));
    uploadReferences.mockRejectedValue(new Error("uzun.mp4 20 saniye — bir referans klibi 2-15 "
                                                 + "saniye arası olmalı."));

    await act(async () => { pick([new File([new Uint8Array([1])], "uzun.mp4")], "video ekle"); });

    // The sentence lives in the backend and the screen prints it: one place for the rule and its
    // wording.
    expect(screen.getByText(/2-15 saniye arası olmalı/)).toBeTruthy();
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

describe("ReferencePanel — adding from a row's card (madde 320)", () => {
  const input = (label) => screen.getByLabelText(label);
  const LABELS = ["fotoğraf ekle", "video ekle", "ses ekle"];

  it("opens a picker for the row's own kind, one file at a time", async () => {
    await open(pool([]));

    expect(LABELS.map((label) => [input(label).accept, input(label).multiple])).toEqual(
      [["image/*", false], ["video/*", false], ["audio/*", false]]);
  });

  it("sends the file with the kind of the row it was picked into", async () => {
    await open(pool([]));
    uploadReferences.mockResolvedValue(pool([]));
    const file = new File([new Uint8Array([1])], "dans.mp4", { type: "video/mp4" });

    await act(async () => { pick([file], "video ekle"); });

    expect(uploadReferences).toHaveBeenCalledWith("düğün", [file], "video");
  });

  it("says Yükleniyor on the card in flight, and no card takes a press", async () => {
    const { container } = await open(pool([]));
    uploadReferences.mockReturnValue(new Promise(() => {}));

    await act(async () => { pick([new File([new Uint8Array([1])], "dans.mp4")], "video ekle"); });

    expect(container.querySelector('[data-add="video"]').textContent).toContain("Yükleniyor…");
    expect(container.querySelector('[data-add="picture"]').textContent)
      .not.toContain("Yükleniyor…");
    expect(LABELS.map((label) => input(label).disabled)).toEqual([true, true, true]);
  });

  it("puts a refusal at the top of the pool, and the next pick clears it", async () => {
    await open(pool([]));
    uploadReferences.mockRejectedValueOnce(
      new Error("kisa-2.wav fotoğraf yuvasına giremez — bu dosya ses."));

    await act(async () => { pick([new File([new Uint8Array([1])], "kisa-2.wav")]); });

    const said = screen.getByText(/yuvasına giremez/);
    // Above the rows, where the eye is when the pick comes back.
    expect(said.compareDocumentPosition(screen.getByText("Fotoğraflar 0/9"))
           & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();

    uploadReferences.mockReturnValue(new Promise(() => {}));
    await act(async () => { pick([new File([new Uint8Array([1])], "kedi.png")]); });

    expect(screen.queryByText(/yuvasına giremez/)).toBeNull();
  });

  it("has no shared Ekle for every kind any more", async () => {
    await open(pool([]));

    expect(screen.queryByLabelText("Ekle")).toBeNull();
  });
});

describe("ReferencePanel — deleting at once (madde 321)", () => {
  const tile = (container, name) => container.querySelector(`[data-reference="${name}"]`);
  const picture = (name, slot) => ({ name, kind: "picture", seconds: null, slot });
  const bin = (name) => screen.getByLabelText(`${name} referansını sil`);

  it("deletes at once, with no window", async () => {
    await open();
    removeReference.mockResolvedValue(pool([]));

    await act(async () => { fireEvent.click(bin("kedi.png")); });

    expect(removeReference).toHaveBeenCalledWith("düğün", "kedi.png");
    expect(screen.queryByText("kedi.png silinsin mi?")).toBeNull();
    expect(screen.getByText("Fotoğraflar 0/9")).toBeTruthy();
  });

  it("numbers the row the way the server answers after a delete", async () => {
    const { container } = await open(pool([picture("bir.png", 1), picture("iki.png", 2),
                                            picture("üç.png", 3)]));
    removeReference.mockResolvedValue(pool([picture("bir.png", 1), picture("üç.png", 2)]));

    await act(async () => { fireEvent.click(bin("iki.png")); });

    // The ones after it move up. The server packs the row, so the N of <Picture N> is its to say.
    expect(within(tile(container, "üç.png")).getByText("2")).toBeTruthy();
    expect(tile(container, "iki.png")).toBeNull();
  });

  it("clears the refusal at the top of the pool", async () => {
    await open();
    uploadReferences.mockRejectedValueOnce(
      new Error("kisa-2.wav fotoğraf yuvasına giremez — bu dosya ses."));
    await act(async () => { pick([new File([new Uint8Array([1])], "kisa-2.wav")]); });
    removeReference.mockResolvedValue(pool([]));

    await act(async () => { fireEvent.click(bin("kedi.png")); });

    // Madde 320's rule: the next pick or delete clears it.
    expect(screen.queryByText(/yuvasına giremez/)).toBeNull();
  });
});
