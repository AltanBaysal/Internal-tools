import { act, fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { listReferences, removeReference, uploadReferences } from "../../shared/api.js";
import ReferencePanel from "./ReferencePanel.jsx";

vi.mock("../../shared/api.js", () => ({
  listReferences: vi.fn(),
  removeReference: vi.fn(),
  uploadReferences: vi.fn(),
  referenceUrl: (project, name) => `/references/${project}/${name}`,
}));

const LIMITS = { picture: 9, video: 3, audio: 3 };

const POOL = {
  references: [{ name: "kedi.png", kind: "picture", seconds: null }],
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
    await open(pool([{ name: "dans.mp4", kind: "video", seconds: 4.2 }]));

    expect(screen.getByText("4,2 sn")).toBeTruthy();
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
