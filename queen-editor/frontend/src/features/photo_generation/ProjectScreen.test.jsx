import { act, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { generateBatch, getStatus, listFrames, listProducers, listReferences, produceFromReferences,
         resumeBatch, saveReferenceSettings, uploadReferences } from "../../shared/api.js";
import { navigate } from "../../shared/router.js";
import ProjectScreen from "./ProjectScreen.jsx";

vi.mock("../../shared/router.js", () => ({
  navigate: vi.fn(),
  photoPath: (project, frame) => `/projects/${encodeURIComponent(project)}/photos/${frame}`,
  exportPath: (project) => `/projects/${encodeURIComponent(project)}/export`,
}));

vi.mock("../../shared/api.js", () => ({
  cancelGeneration: vi.fn(),
  deletePhotos: vi.fn(),
  generateBatch: vi.fn(),
  getReferenceSettings: vi.fn().mockResolvedValue({ prompts: "", variants: null }),
  getStatus: vi.fn().mockResolvedValue({ status: "idle" }),
  listFrames: vi.fn().mockResolvedValue([]),
  listModels: vi.fn().mockResolvedValue({
    models: [{ value: "nova3dcg", label: "Nova 3DCG XL" }],
    loras: [{ value: "usnr", label: "USNR" }, { value: "slime", label: "Slime" },
            { value: "none", label: "Boş" }],
  }),
  listProducers: vi.fn().mockResolvedValue([]),
  produceFromReferences: vi.fn(),
  listReferences: vi.fn(),
  removeReference: vi.fn(),
  uploadReferences: vi.fn(),
  referenceUrl: (project, name) => `/references/${project}/${name}`,
  fileUrl: (project, file) => `/photos/${project}/${file}`,
  resumeBatch: vi.fn(),
  retryFailed: vi.fn(),
  retryFrame: vi.fn(),
  saveOrder: vi.fn(),
  saveReferenceSettings: vi.fn(),
  stopGeneration: vi.fn(),
}));

const SETTINGS = { prompts: "", negative: "", variants: 4 };

// The gallery a project last answered with is remembered across mounts, so a test that must start
// from nothing asks for a project name no other test has filled.
function renderScreen(project = "düğün") {
  return render(
    <ProjectScreen project={project} settings={SETTINGS} onSaveSettings={() => Promise.resolve()} />,
  );
}

const LIMITS = { picture: 9, video: 3, audio: 3 };
const KEDI = { name: "kedi.png", kind: "picture", seconds: null, slot: 1 };

// The pool the way the server keeps it: a file that goes up is in every listing after it. The video
// panel's missing line reads the pool (madde 324), so a test that presses from it says what it holds.
function poolServer(references) {
  let held = references;
  listReferences.mockImplementation(async () => ({ references: held, limits: LIMITS }));
  // One file per pick, at the end of its own row (madde 320).
  uploadReferences.mockImplementation(async (project, [file], kind) => {
    held = [...held, { name: file.name, kind, seconds: null,
                       slot: held.filter((one) => one.kind === kind).length + 1 }];
    return { references: held, limits: LIMITS };
  });
}

beforeEach(() => {
  vi.clearAllMocks();
  poolServer([]);
});

describe("ProjectScreen — the card panel", () => {
  it("gives the card panel no way to close", async () => {
    // The user's decision: the pool is closable, the cards' own panel is not.
    renderScreen();
    await act(async () => {});

    expect(screen.queryByLabelText("Kart panelini kapat")).toBeNull();
  });
});

describe("ProjectScreen — the pool opens in place of the cards (madde 318)", () => {
  // The pool's first row heading, and the empty gallery's own sentence: one says the pool is in
  // the middle, the other whether the cards are hidden there.
  const pool = () => screen.queryByText("Fotoğraflar 0/9");
  const cardsHidden = () => Boolean(screen.getByText("henüz kare yok").closest("[hidden]"));
  const tab = (name) => screen.getByRole("button", { name });

  async function open(project) {
    renderScreen(project);
    await act(async () => {});
  }

  async function openReferanstan() {
    fireEvent.click(screen.getByLabelText("Video üret"));
    await act(async () => { fireEvent.click(tab("Referanstan")); });
  }

  it("keeps no pool column beside the cards", async () => {
    await open("havuz-a");

    expect(screen.queryByLabelText("Referans panelini kapat")).toBeNull();
    expect(screen.queryByLabelText("Referans panelini aç")).toBeNull();
    expect(pool()).toBeNull();
    expect(cardsHidden()).toBe(false);
  });

  it("opens the pool in the middle on Referanstan, with the panel beside it", async () => {
    await open("havuz-b");

    await openReferanstan();

    expect(pool()).toBeTruthy();
    expect(cardsHidden()).toBe(true);
    expect(screen.getByRole("heading", { name: "Video üret" })).toBeTruthy();
  });

  it("closes the pool and opens it again with one button", async () => {
    await open("havuz-c");
    await openReferanstan();

    fireEvent.click(screen.getByText("Referansları kapat"));

    expect(pool()).toBeNull();
    expect(cardsHidden()).toBe(false);

    await act(async () => { fireEvent.click(screen.getByText("Referansları aç")); });

    expect(pool()).toBeTruthy();
  });

  it("gives the cards back on Kareden, and Referanstan opens a closed pool again", async () => {
    await open("havuz-d");
    await openReferanstan();
    fireEvent.click(screen.getByText("Referansları kapat"));

    fireEvent.click(tab("Kareden"));
    expect(pool()).toBeNull();

    await act(async () => { fireEvent.click(tab("Referanstan")); });
    expect(pool()).toBeTruthy();
  });

  it("gives the cards back when another panel opens, or the panel closes", async () => {
    await open("havuz-e");
    await openReferanstan();

    fireEvent.click(screen.getByLabelText("Ses üret"));
    expect(pool()).toBeNull();
    expect(cardsHidden()).toBe(false);

    fireEvent.click(screen.getByLabelText("Video üret"));
    // A panel opened from the rail starts on Kareden (madde 317), so the cards stay.
    expect(tab("Kareden").className).toContain("is-on");
    expect(pool()).toBeNull();

    await act(async () => { fireEvent.click(tab("Referanstan")); });
    // The video panel's own icon closes it.
    fireEvent.click(screen.getByLabelText("Video üret"));
    expect(pool()).toBeNull();
  });
});

describe("ProjectScreen — a prompt list the server cannot read (madde 323)", () => {
  it("says the server's own sentence under the button", async () => {
    // The screen reads the list only to count it. What cannot be read goes to the server, which
    // refuses it in the photo panel's words, and the answer lands in the panel that was pressed.
    // With a reference in the pool: an empty one closes the button before any press (madde 324).
    poolServer([KEDI]);
    saveReferenceSettings.mockResolvedValueOnce(null);
    produceFromReferences.mockRejectedValueOnce(new Error("Format hatası — liste okunamadı"));
    renderScreen("liste-a");
    await act(async () => {});
    fireEvent.click(screen.getByLabelText("Video üret"));
    await act(async () => { fireEvent.click(screen.getByRole("button", { name: "Referanstan" })); });
    fireEvent.change(screen.getByLabelText("Prompt listesi"), { target: { value: "gotik kız" } });

    await act(async () => { fireEvent.click(screen.getByText("Kuyruğa ekle")); });

    expect(produceFromReferences).toHaveBeenCalledWith("liste-a", "gotik kız", 1);
    expect(screen.getByText("Format hatası — liste okunamadı")).toBeTruthy();
  });
});

describe("ProjectScreen — what stops a run from the pool (madde 324)", () => {
  const NO_REFERENCES = "Havuzda referans yok — önce en az bir referans ekle.";
  const button = () => screen.getByText("Kuyruğa ekle").closest("button");

  it("lets the line go once a reference lands in the middle, and opens the button for a list",
     async () => {
    // The pool in the middle and the line in the panel read the same pool. The wire between them is
    // what this test is for: the panel's own tests hand it the pool by hand.
    renderScreen("boş-havuz");
    await act(async () => {});
    fireEvent.click(screen.getByLabelText("Video üret"));
    await act(async () => { fireEvent.click(screen.getByRole("button", { name: "Referanstan" })); });
    expect(screen.getByText(NO_REFERENCES)).toBeTruthy();
    expect(button().disabled).toBe(true);

    const file = new File([new Uint8Array([1])], "kedi.png", { type: "image/png" });
    await act(async () => {
      fireEvent.change(screen.getByLabelText("fotoğraf ekle"), { target: { files: [file] } });
    });

    expect(screen.queryByText(NO_REFERENCES)).toBeNull();
    // Still closed: nothing is written in the prompt box yet.
    expect(button().disabled).toBe(true);
    fireEvent.change(screen.getByLabelText("Prompt listesi"),
                     { target: { value: '["gotik kız"]' } });
    expect(button().disabled).toBe(false);
  });
});

describe("ProjectScreen app bar", () => {
  it("puts the version next to the name", () => {
    // The shape, not the value: the number is shared/version.js's to say (madde 248).
    renderScreen();

    expect(screen.getByText(/^Queen Editor V\d+$/)).toBeTruthy();
  });

  it("opens the export screen instead of downloading a file", () => {
    renderScreen();

    fireEvent.click(screen.getByText("Export"));

    expect(navigate).toHaveBeenCalledWith(`/projects/${encodeURIComponent("düğün")}/export`);
  });

  it("leaves for the projects screen without asking first", () => {
    renderScreen();

    fireEvent.click(screen.getByText("Projeden çık"));

    // Nothing is at risk: the queue is the server's and the frames are on disk (madde 10).
    expect(screen.queryByText("Projeden çıkılsın mı?")).toBeNull();
    expect(navigate).toHaveBeenCalledWith("/");
  });

  it("places Export to the left of the leave button", () => {
    renderScreen();

    const exportEl = screen.getByText("Export");
    const exitEl = screen.getByText("Projeden çık");
    // compareDocumentPosition's FOLLOWING bit: the exit button comes later in document order.
    expect(exportEl.compareDocumentPosition(exitEl) & Node.DOCUMENT_POSITION_FOLLOWING)
      .toBeTruthy();
  });
});

describe("ProjectScreen — what leaving says while the queue flows", () => {
  const BUBBLE = "Projeden çıksan da pencereyi kapatsan da kuyruk durmaz. "
                 + "Döndüğünde biten kareleri galeride bulursun.";

  beforeEach(() => {
    vi.useFakeTimers();
  });
  afterEach(() => vi.useRealTimers());

  async function openWith(status) {
    getStatus.mockResolvedValue(status);
    renderScreen();
    await act(async () => { await vi.advanceTimersByTimeAsync(0); });
  }

  it("explains itself over the button while production runs", async () => {
    await openWith({ status: "running", project: "düğün" });

    fireEvent.mouseEnter(screen.getByText("Projeden çık"));

    expect(screen.getByText("Üretim arka planda sürüyor")).toBeTruthy();
    expect(screen.getByText(BUBBLE)).toBeTruthy();
  });

  it("takes the bubble away when the pointer leaves", async () => {
    await openWith({ status: "running", project: "düğün" });
    fireEvent.mouseEnter(screen.getByText("Projeden çık"));

    fireEvent.mouseLeave(screen.getByText("Projeden çık"));

    expect(screen.queryByText("Üretim arka planda sürüyor")).toBeNull();
  });

  it("says nothing when there is no production to speak of", async () => {
    await openWith({ status: "idle" });

    fireEvent.mouseEnter(screen.getByText("Projeden çık"));

    expect(screen.queryByText("Üretim arka planda sürüyor")).toBeNull();
  });

  it("says nothing while the queue is paused: a stopped queue does not go on", async () => {
    await openWith({ status: "paused", project: "düğün" });

    fireEvent.mouseEnter(screen.getByText("Projeden çık"));

    expect(screen.queryByText("Üretim arka planda sürüyor")).toBeNull();
  });
});

describe("ProjectScreen — an open project waits for the user", () => {
  const OWED = [{ id: "0_a", file: "0_a.png", status: "pending", owed: ["photo"], failed: [] }];

  beforeEach(() => {
    vi.useFakeTimers();
    resumeBatch.mockResolvedValue({});
  });
  afterEach(() => vi.useRealTimers());

  async function settle(ms = 0) {
    await act(async () => { await vi.advanceTimersByTimeAsync(ms); });
  }

  it("starts nothing on its own, however many frames are owed", async () => {
    listFrames.mockResolvedValue(OWED);
    getStatus.mockResolvedValue({ status: "idle" });

    renderScreen();
    await settle();
    await settle(10_000);

    expect(resumeBatch).not.toHaveBeenCalled();
  });

  it("leaves a waiting queue where it is even once its producer has landed", async () => {
    listFrames.mockResolvedValue(OWED);
    getStatus.mockResolvedValue({ status: "waiting", project: "düğün", waitingFor: "video" });
    listProducers.mockResolvedValue([
      { id: "video", name: "Video üreticisi", installed: true }]);

    renderScreen();
    await settle();

    expect(resumeBatch).not.toHaveBeenCalled();
  });

  it("leaves a waiting queue where it is while its producer is still missing", async () => {
    listFrames.mockResolvedValue([]);
    getStatus.mockResolvedValue({ status: "waiting", project: "boş 1", waitingFor: "video" });
    listProducers.mockResolvedValue([
      { id: "video", name: "Video üreticisi", installed: false }]);

    renderScreen("boş 1");
    await settle();

    expect(resumeBatch).not.toHaveBeenCalled();
  });

  it("leaves a paused queue alone -- it has its own Devam et", async () => {
    listFrames.mockResolvedValue(OWED);
    getStatus.mockResolvedValue({ status: "paused", project: "düğün" });

    renderScreen();
    await settle();

    expect(resumeBatch).not.toHaveBeenCalled();
  });

  it("leaves a queue a fatal error stopped alone", async () => {
    listFrames.mockResolvedValue(OWED);
    getStatus.mockResolvedValue({ status: "error", project: "boş 2", error: "boom" });

    renderScreen("boş 2");
    await settle();

    expect(resumeBatch).not.toHaveBeenCalled();
  });

  it("says nothing when the queue is empty", async () => {
    listFrames.mockResolvedValue([{ id: "0_a", file: "0_a.png", status: "done" }]);
    getStatus.mockResolvedValue({ status: "idle" });

    renderScreen("boş 3");
    await settle();

    expect(resumeBatch).not.toHaveBeenCalled();
  });

  it("does not touch a queue that is already going", async () => {
    listFrames.mockResolvedValue(OWED);
    getStatus.mockResolvedValue({ status: "running", project: "düğün" });

    renderScreen();
    await settle();

    expect(resumeBatch).not.toHaveBeenCalled();
  });
});

// The first test in this file that drives the gallery. Everything above renders the screen and
// reads it; this one uses it -- which is where the bugs turned out to live: each piece was tested
// against inputs handed to it by hand, and the wire between them by nothing at all.
describe("ProjectScreen — the gallery's selection reaches the video panel", () => {
  beforeEach(() => { vi.useFakeTimers(); });
  afterEach(() => vi.useRealTimers());

  const done = (file) => ({ id: file.replace(".png", ""), file, status: "done", layers: {},
                            owed: [], failed: [] });
  const FRAMES = [done("1_a.png"), done("0_a.png")];

  async function settle(ms = 0) {
    await act(async () => { await vi.advanceTimersByTimeAsync(ms); });
  }

  it("counts a frame picked in the gallery, and stops counting it when it is let go", async () => {
    listFrames.mockResolvedValue(FRAMES);
    renderScreen("seçim");
    await settle();
    fireEvent.click(screen.getByLabelText("Video üret"));
    // By identity, because that is what a tile is keyed by -- and the identity is the whole point
    // of this test.
    const ring = () => document.getElementById("tile-0_a").querySelector("[data-check]");
    const scope = () => screen.getByText("Seçili kareler").closest("button");

    await act(async () => { fireEvent.click(ring()); });

    expect(scope().textContent).toContain("1");

    await act(async () => { fireEvent.click(ring()); });

    // The second assertion needs the first: a count that is always 0 would pass this line alone.
    expect(scope().textContent).toContain("0");
  });
});

// What the gallery is told about the queue. The pill's word is the only place on screen where a
// frame says whether anything is coming for it, and the gallery cannot know that by itself.
describe("ProjectScreen — a stopped queue does not look like a moving one", () => {
  beforeEach(() => { vi.useFakeTimers(); });
  afterEach(() => vi.useRealTimers());

  const OWES_VIDEO = [{ id: "P0_0", file: "P0_0.png", status: "done", layers: { photo: "P0_0.png" },
                        owed: ["video"], failed: [] }];

  async function open(status, project) {
    listFrames.mockResolvedValue(OWES_VIDEO);
    getStatus.mockResolvedValue(status);
    renderScreen(project);
    await act(async () => { await vi.advanceTimersByTimeAsync(0); });
  }

  it("says queued while this project's queue is flowing", async () => {
    await open({ status: "running", project: "akan" }, "akan");

    expect(screen.getByText("video kuyrukta")).toBeTruthy();
  });

  it("says waiting once an error has stopped the queue", async () => {
    // 2026-08-13: a dead xAI key stopped the run and every frame went on saying it was queued.
    await open({ status: "error", project: "duran", error: "xAI HTTP 400" }, "duran");

    expect(screen.getByText("video bekliyor")).toBeTruthy();
  });

  it("says waiting while it is another project's queue that is flowing", async () => {
    // The worker is global: a batch belonging to someone else moves nothing here.
    await open({ status: "running", project: "komşu" }, "bizim");

    expect(screen.getByText("video bekliyor")).toBeTruthy();
  });
});

// What the user actually saw on 2026-08-14: a green report from a batch of photos, on a page they
// had just opened to queue sound.
describe("ProjectScreen — a report nobody on this page watched", () => {
  beforeEach(() => { vi.useFakeTimers(); });
  afterEach(() => vi.useRealTimers());

  it("opens on a finished run without repeating its good news", async () => {
    listFrames.mockResolvedValue([]);
    getStatus.mockResolvedValue({ status: "done", project: "eski", done: 20, failed: 0,
                                  total: 20 });

    renderScreen("eski");
    await act(async () => { await vi.advanceTimersByTimeAsync(0); });
    fireEvent.click(screen.getByLabelText("Kuyruğu takip et"));

    expect(screen.queryByText("Kuyruk tamamlandı")).toBeNull();
    expect(screen.getByText("Kuyruk boş")).toBeTruthy();
  });
});

describe("ProjectScreen — coming back to where the gallery was", () => {
  const boxOf = () => document.querySelector("[data-scroll]");

  it("opens the gallery at the place the screen was left at", () => {
    const first = renderScreen("kayma");
    boxOf().scrollTop = 640;

    first.unmount();
    renderScreen("kayma");

    // The list was already remembered across mounts; this is the other half of standing still.
    expect(boxOf().scrollTop).toBe(640);
  });
});

describe("ProjectScreen — the lora is kept with the project (madde 238)", () => {
  beforeEach(() => { vi.useFakeTimers(); });
  afterEach(() => vi.useRealTimers());

  it("saves the pick with the rest of the panel when the batch is sent", async () => {
    // The record is what a project opens on, and the model has always been in it. The lora is a
    // real choice now, so it rides along: a Slime project opens on Slime.
    const onSaveSettings = vi.fn().mockResolvedValue();
    generateBatch.mockResolvedValue({ job: "running", added: 1, frames: [] });
    render(<ProjectScreen project="lora" onSaveSettings={onSaveSettings}
                          settings={{ ...SETTINGS, prompts: '["a"]', model: "nova3dcg",
                                      lora: "slime" }} />);
    await act(async () => { await vi.advanceTimersByTimeAsync(0); });

    await act(async () => { fireEvent.click(screen.getByText("Kuyruğa ekle")); });

    expect(onSaveSettings).toHaveBeenCalledWith(expect.objectContaining({ lora: "slime" }));
  });
});

describe("ProjectScreen — the queue panel before the first answer", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });
  afterEach(() => vi.useRealTimers());

  it("keeps it quiet until the server has said something", async () => {
    // The answer never lands: what the panel says now is what it says with nothing reported.
    getStatus.mockImplementation(() => new Promise(() => {}));
    renderScreen("sessiz");
    await act(async () => { await vi.advanceTimersByTimeAsync(0); });

    fireEvent.click(screen.getByLabelText("Kuyruğu takip et"));

    // useGeneration has carried this answer all along and nobody was reading it. The wire is the
    // whole of this item, and a wire that is missing fails quietly -- which is why it is tested
    // from the screen and not only from the panel.
    expect(screen.queryByText("Kuyruk boş")).toBeNull();
  });
});
