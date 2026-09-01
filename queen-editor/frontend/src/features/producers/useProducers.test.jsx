import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("../../shared/api.js", () => ({ listProducers: vi.fn() }));

const THREE = [
  { id: "photo", name: "Fotoğraf üreticisi", installed: true },
  { id: "video", name: "Video üreticisi", installed: false },
];

async function settle() {
  await act(async () => { await Promise.resolve(); });
}

// What the machine answered is remembered for the length of a visit, and that memory lives in the
// module -- so each test gets the module itself fresh. Both are imported from the same fresh
// registry: taking the hook from the new one and the fake from the old would leave them talking to
// two different mocks.
let listProducers;
let COLAB_INSTALL;
let useProducers;

beforeEach(async () => {
  vi.resetModules();
  ({ listProducers } = await import("../../shared/api.js"));
  ({ COLAB_INSTALL, useProducers } = await import("./useProducers.js"));
  // resetModules does not re-run a vi.mock factory, so the fake is the same object every test and
  // carries its calls over -- and this file counts them. The hook beside it really is new.
  vi.clearAllMocks();
  listProducers.mockResolvedValue(THREE);
});

describe("useProducers", () => {
  it("reads the machine once and does not keep asking", async () => {
    // Nothing installs while the app is up -- the notebook does it before this process starts --
    // so a second read could only return the same answer.
    renderHook(() => useProducers());
    await settle();

    expect(listProducers).toHaveBeenCalledTimes(1);
  });

  it("names the notebook the user actually has to open", () => {
    // The sentence IS the whole answer Kur gives, and it sends the user to a file by name. Pinned
    // here and nowhere else: every other test reads the constant, so it would agree with whatever
    // name the constant carried -- including one that is not in the repo any more.
    expect(COLAB_INSTALL).toContain("queeneditor.ipynb");
  });

  it("answers Kur with where the install happens, and asks the server nothing", async () => {
    const { result } = renderHook(() => useProducers());
    await settle();

    act(() => { result.current.install("video"); });

    expect(result.current.producers[1].note).toBe(COLAB_INSTALL);
    expect(result.current.producers[0].note).toBeUndefined();
    expect(listProducers).toHaveBeenCalledTimes(1);
  });

  it("keeps the reason on screen when the list cannot be read", async () => {
    listProducers.mockRejectedValue(new Error("Sunucuya ulaşılamadı."));
    const { result } = renderHook(() => useProducers());
    await settle();

    expect(result.current.error).toBe("Sunucuya ulaşılamadı.");
    expect(result.current.producers).toBeNull();
  });

  it("opens with the rows it already read", async () => {
    const first = renderHook(() => useProducers());
    await settle();
    first.unmount();

    // The panel drew neither rows nor an error while this was null, and coming back from a frame
    // put it through that again for an answer that cannot have changed.
    const { result } = renderHook(() => useProducers());
    expect(result.current.producers).toEqual(THREE);
  });

  it("remembers the rows as they stand, not as they arrived", async () => {
    const first = renderHook(() => useProducers());
    await settle();
    act(() => { first.result.current.install("video"); });
    first.unmount();

    const { result } = renderHook(() => useProducers());
    // Kur writes its sentence onto a row, so the answer on screen is no longer the answer the
    // server gave. Remembering the first one would take that sentence away on the way back.
    expect(result.current.producers[1].note).toBe(COLAB_INSTALL);
  });
});
