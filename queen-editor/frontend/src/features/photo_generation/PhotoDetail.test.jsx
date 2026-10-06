import { act, fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import {
  getStatus,
  getVideoLength,
  listFrames,
  listModels,
  listProducers,
  regenerateFrame,
  removeFrames,
  removeLayer,
  retryFrame,
} from "../../shared/api.js";
import { navigate } from "../../shared/router.js";
import { VERSION } from "../../shared/version.js";
import PhotoDetail from "./PhotoDetail.jsx";

vi.mock("../../shared/api.js", () => ({
  cancelGeneration: vi.fn(),
  generateBatch: vi.fn(),
  getStatus: vi.fn(),
  getVideoLength: vi.fn(),
  listFrames: vi.fn(),
  listModels: vi.fn(),
  listProducers: vi.fn(),
  regenerateFrame: vi.fn(),
  removeFrames: vi.fn(),
  removeLayer: vi.fn(),
  resumeBatch: vi.fn(),
  retryFrame: vi.fn(),
  saveOrder: vi.fn(),
  stopGeneration: vi.fn(),
  fileUrl: (project, file) => `/photos/${project}/${file}`,
}));
vi.mock("../../shared/router.js", () => ({
  navigate: vi.fn(),
  photoPath: (project, file) => `/projects/${project}/photos/${file}`,
  projectPath: (project) => `/projects/${project}`,
}));

// A frame is named by its identity; the file is only what it shows. These fixtures name a frame
// after its own picture, which is the ordinary case -- the copy frames that break the tie have
// their own tests.
const done = (file, prompt, negative = "") => ({ id: file.replace(".png", ""), file,
                                                 status: "done", prompt, negative,
                                                 layers: { photo: file }, owed: [], failed: [] });
const waiting = (file, prompt, negative = "") => ({ id: file.replace(".png", ""), file,
                                                    status: "pending", prompt, negative,
                                                    layers: {}, owed: ["photo"], failed: [] });

const PHOTOS = [done("2_a.png", "üçüncü", "bulanık"),
                done("1_a.png", "ikinci"),
                done("0_a.png", "ilk", "gürültü")];

// The gallery as Madde 5 leaves it: one sequence, every state in its own place. 2_a is the one the
// live worker holds -- that is a pending frame with no line on disk, so only /api/status says so.
const MIXED = [waiting("3_a.png", "dördüncü", "bulanık"),
               waiting("2_a.png", "üçüncü"),
               { id: "1_a", file: "1_a.png", status: "failed", prompt: "ikinci",
                 negative: "gürültü", layers: {}, owed: [], failed: ["photo"],
                 errors: { photo: "node 41: OOM — 3 kez denendi" } },
               done("0_a.png", "ilk", "düşük çözünürlük")];

const IDLE = { status: "idle" };
const LORAS = [{ value: "usnr", label: "USNR" }, { value: "slime", label: "Slime" },
               { value: "none", label: "Boş" }];
const RUNNING = { status: "running", project: "düğün", current: { id: "2_a" } };

// Advancing the fake clock inside act() flushes both the timers and the promises they unblock --
// the detail page is live now, so a poll tick is what moves it forward.
async function settle(ms = 0) {
  await act(async () => { await vi.advanceTimersByTimeAsync(ms); });
}

// The page is opened by the frame's identity: that is what the address carries.
async function open(fid, { frames = PHOTOS, status = IDLE, models = [], loras = LORAS } = {}) {
  listFrames.mockResolvedValue(frames);
  getStatus.mockResolvedValue(status);
  // The rows the renderer offers. Needed here because the stored value is an id -- the name the
  // user chose it by lives in this list and nowhere else. The loras ride in the same answer.
  listModels.mockResolvedValue({ models, loras });
  render(<PhotoDetail project="düğün" frame={fid} />);
  await settle();
}

// The panel's own Sil comes first in the document; the modal's is the one added on top.
function confirmButton() {
  return screen.getAllByText("Sil").at(-1);
}

const LAYERED = {
  id: "P0_0", file: "P0_0.png", status: "done", prompt: "kırmızı elbise", negative: "bulanık",
  // The plan row's own shape: list_frames spreads that row into the frame, so the name arrives with
  // the extension it is stored under and trimming it is the panel's job.
  model: "novaAnimeXL_ilV190.safetensors",
  lora: "usnr",
  layers: { photo: "P0_0.png", video: "P0_0_V1_0.mp4", audio: "P0_0_V1_0_S1_0.wav" },
  failed: [], owed: [],
  prompts: { photo: "kırmızı elbise", video: "kadın dönüyor", audio: "kumaş hışırtısı" },
};

// The frame the arrows move on to: its own words, so a box that kept the first frame's text shows.
const SECOND = { id: "P1_0", file: "P1_0.png", status: "done", prompt: "mavi elbise", negative: "",
                 layers: { photo: "P1_0.png" }, failed: [], owed: [],
                 prompts: { photo: "mavi elbise" } };

// The same second frame with a video of its own: a run of videos is what the user is stepping
// through when the open tab matters, and no fixture in this file was one before.
const SECOND_VIDEO = { id: "P1_0", file: "P1_0.png", status: "done", prompt: "mavi elbise",
                       negative: "", layers: { photo: "P1_0.png", video: "P1_0_V1_0.mp4" },
                       failed: [], owed: [],
                       prompts: { photo: "mavi elbise", video: "kadın yürüyor" } };

// A frame whose photo blew up: nothing on disk, and the record's own sentence about why.
const BROKEN = { id: "P0_0", file: "P0_0.png", status: "failed", prompt: "kırmızı elbise",
                 negative: "", layers: {}, failed: ["photo"], owed: [],
                 prompts: { photo: "kırmızı elbise" },
                 errors: { photo: "CUDA out of memory — 3 kez denendi" } };

// A copy frame waiting for its video: it holds its source's picture and owns no file of its own.
const QUEUED_COPY = { id: "P0_1", file: "P0_0.png", status: "done", prompt: "kırmızı elbise",
                      negative: "", layers: { photo: "P0_0.png" }, failed: [], owed: ["video"],
                      prompts: { photo: "kırmızı elbise" }, errors: {} };

const tab = (name) => screen.getByRole("button", { name });
const regenButton = () => screen.getByText("Yeniden üret — yeni kare").closest("button");
// The row that folds the frame's facts away (madde 399), and the facts' labels in the order the
// column draws them -- the whole column's, or one part's.
const details = () => screen.getByRole("button", { name: "Ayrıntılar" });
const facts = (root = document) =>
  [...root.querySelectorAll("[data-field]")].map((one) => one.textContent);
// The frame's scenario (madde 401): the sentence QueenAgent's list gave it, for checking the
// prompts against the picture. Two of them, so a card that kept the first frame's sentence shows.
const SCENE = "Kraliçe tahtında oturuyor; salon boş ve karanlık.";
const SECOND_SCENE = "Kraliçe gece bahçede yürüyor, fenerler yanıyor.";
const scenario = () => screen.getByRole("button", { name: "Senaryo" });
const sceneCard = () => document.querySelector("[data-scenario]");

// jsdom ships no clipboard, so the test supplies one and watches what it is handed. The answer is
// made at the call and not before it: a page has to be opened between the stub and the press, and a
// rejected promise sitting through those ticks with nothing waiting on it is an unhandled rejection
// -- which vitest fails the whole run over, however green the tests are.
function stubClipboard(answer) {
  const writeText = vi.fn(() => answer());
  Object.defineProperty(navigator, "clipboard", { value: { writeText }, configurable: true });
  return writeText;
}

beforeEach(() => {
  vi.clearAllMocks();
  vi.useFakeTimers();
  // jsdom has no media pipeline: the player's own calls are stubbed so a tab can be opened.
  vi.spyOn(window.HTMLMediaElement.prototype, "play").mockResolvedValue(undefined);
  vi.spyOn(window.HTMLMediaElement.prototype, "pause").mockImplementation(() => {});
  // No video row: the model is not known, so no note promises a length -- every older test reads
  // the page as it was.
  listProducers.mockResolvedValue([]);
  getVideoLength.mockResolvedValue(8);
});

// The frame the worker is holding a layer of: its photo is on disk, its video is not yet.
const RENDERING = { ...LAYERED, layers: { photo: "P0_0.png" }, owed: ["video"],
                    prompts: { photo: "kırmızı elbise" } };

describe("PhotoDetail — the header", () => {
  it("puts the version next to the name", async () => {
    // The module's value, not a pattern: the number is shared/version.js's to say (madde 248), and
    // a number typed into this screen would pass a pattern just as well (madde 412, as 285 did for
    // the export screen). The value itself is not pinned here: it is a decision, and pinning it
    // would put one decision in two places.
    await open("0_a");

    expect(screen.getByText(`Queen Editor ${VERSION}`)).toBeTruthy();
  });
});

describe("PhotoDetail — the stage", () => {
  it("opens the stage from the top and drops the strip closer to it", async () => {
    await open("P0_0", { frames: [LAYERED] });

    // Fark 103: the tabs sat 16px down over a stage padded evenly on all four sides, so the strip
    // and the picture crowded the same band. The top opens, the other three stay.
    const stage = document.querySelector("[data-stage]");
    expect(stage.style.paddingTop).toBe("48px");
    expect([stage.style.paddingRight, stage.style.paddingBottom, stage.style.paddingLeft])
      .toEqual(["24px", "24px", "24px"]);
    expect(document.querySelector("[data-strip]").style.top).toBe("12px");
  });

  it("puts a step between a waiting frame's two lines", async () => {
    await open("P0_0", { frames: [{ id: "P0_0", file: "P0_0.png", status: "pending", prompt: "p",
                                    layers: {}, failed: [], owed: ["photo"], prompts: {} }] });

    // Fark 105: both lines read at the same size, so neither was the heading. The word is the
    // heading now and the sentence under it steps back.
    expect(screen.getByText("bekliyor").style.fontSize).toBe("14px");
    expect(screen.getByText("henüz üretilmedi").style.fontSize).toBe("10px");
    expect(screen.getByText("henüz üretilmedi").style.color).toBe("var(--ink-4)");
  });

  it("swaps the fonts of the failed stage's title and reason", async () => {
    await open("P0_0", { frames: [BROKEN] });

    // Fark 106: exactly the other way round from today. The two words are a heading and read as
    // one; what the renderer said is machine output and reads as machine output.
    expect(screen.getByText("Bu kare üretilemedi").className).toContain("wf-note");
    expect(screen.getByText("CUDA out of memory — 3 kez denendi").className).toContain("wf-mono");
  });

  it("keeps the picture and lays a box over it while a layer is made", async () => {
    // `type` is the job's own field for which layer it is making -- the same word the queue uses.
    await open("P0_0", { frames: [RENDERING],
                         status: { status: "running", project: "düğün",
                                   current: { id: "P0_0", type: "video" } } });

    fireEvent.click(tab("Video"));

    // Fark 113: the photo used to be swapped for a spinner, so the one thing the user could still
    // look at went away for the length of the render. On the layer's own tab -- the photo tab has
    // nothing being made on it.
    expect(screen.getByAltText("P0_0.png")).toBeTruthy();
    expect(document.querySelector("[data-making]").textContent).toContain("video üretiliyor");
    expect(document.querySelector("[data-making] .qe-dot--alive")).toBeTruthy();
  });

  it("still spins where there is no picture yet", async () => {
    await open("2_a", { frames: MIXED, status: RUNNING });

    // The exception the fark does not name: a photo being made has nothing to keep on screen, so
    // the holder stays what it was.
    expect(document.querySelector(".wf-spinner")).toBeTruthy();
    expect(document.querySelector("[data-making]")).toBeNull();
  });

  it("says whose picture a copy frame is showing", async () => {
    await open("P0_1", { frames: [QUEUED_COPY] });

    // Fark 112: the stage is full of the source's photo and nothing said so (karar 37).
    expect(screen.getByText("kaynak foto · kopya kare")).toBeTruthy();
  });
});

describe("PhotoDetail — the layer tabs", () => {
  it("opens on the photo and offers a tab per layer", async () => {
    await open("P0_0", { frames: [LAYERED] });

    expect(tab("Foto").getAttribute("aria-current")).toBe("page");
    expect(tab("Video").disabled).toBe(false);
    expect(tab("Ses").disabled).toBe(false);
  });

  it("leaves the tab of a layer the frame does not have disabled rather than hidden", async () => {
    await open("P0_0", { frames: [{ ...LAYERED, layers: { photo: "P0_0.png" },
                                        prompts: { photo: "kırmızı elbise" } }] });

    expect(tab("Video").disabled).toBe(true);
    expect(tab("Ses").disabled).toBe(true);
  });

  it("sets eight pixels between the three tabs", async () => {
    await open("P0_0", { frames: [LAYERED] });

    // The strip's own measure, not the buttons': three buttons have two gaps between them, and a
    // margin would write the number three times to get two of them (Fark 85).
    expect(document.querySelector("[data-strip]").style.gap).toBe("8px");
  });

  it("pulls no tab onto the one before it", async () => {
    await open("P0_0", { frames: [LAYERED] });

    // Each tab already owns a corner radius -- the stroke class draws it. What hid the radius was
    // the overlap: two rounded corners meeting on the same pixel read as a pinch, not a corner.
    expect([tab("Foto"), tab("Video"), tab("Ses")].map((one) => one.style.marginLeft))
      .toEqual(["", "", ""]);
  });

  it("tells the open tab by its colour and adds nothing else to it", async () => {
    await open("P0_0", { frames: [LAYERED] });

    const shut = { held: tab("Video").childElementCount, said: tab("Video").textContent };
    expect(tab("Video").style.color).toBe("var(--ink-3)");

    fireEvent.click(tab("Video"));

    expect(tab("Video").style.color).toBe("var(--accent)");
    expect(tab("Foto").style.color).toBe("var(--ink-3)");
    // No underline, no dot, no caret: opening a tab changes what colour it is and nothing about
    // what it holds. Separating the three is what makes that temptation appear (Fark 85).
    expect(tab("Video").childElementCount).toBe(shut.held);
    expect(tab("Video").textContent).toBe(shut.said);
  });

  it("opens the tab of a layer that blew up, so its reason can be read", async () => {
    await open("P0_0", { frames: [{ ...LAYERED, failed: ["audio"],
                                    errors: { audio: "ComfyUI 500 — 3 kez denendi" } }] });

    expect(tab("Ses").disabled).toBe(false);
    fireEvent.click(tab("Ses"));

    expect(screen.getByText("ComfyUI 500 — 3 kez denendi")).toBeTruthy();
  });

  it("shows the open layer's own prompt and nothing under it", async () => {
    await open("P0_0", { frames: [LAYERED] });

    fireEvent.click(tab("Video"));

    // Its own words are the editable box; what it was made from is not this page's to show any
    // more -- the decision that put it here was taken back (madde 87).
    expect(screen.getByDisplayValue("kadın dönüyor")).toBeTruthy();
    expect(screen.queryByText("kırmızı elbise")).toBeNull();
    expect(screen.queryByText("P0_0_V1_0.mp4")).toBeNull();
    // The negative belongs to the photo alone: video and sound jobs carry none.
    expect(screen.queryByText("Foto negatif prompt'u")).toBeNull();
  });

  it("repeats the skeleton for sound", async () => {
    await open("P0_0", { frames: [LAYERED] });

    fireEvent.click(tab("Ses"));

    expect(screen.getByDisplayValue("kumaş hışırtısı")).toBeTruthy();
    expect(screen.queryByText("kadın dönüyor")).toBeNull();
    expect(screen.queryByText("P0_0_V1_0_S1_0.wav")).toBeNull();
  });

  it("keeps the frame's own name and its place on every tab", async () => {
    // The page's own header carries the project's name, not the frame's -- so if this row went,
    // the identity would be nowhere on screen (karar 23). Behind the details row since madde 399,
    // which stays open across the tabs.
    await open("P0_0", { frames: [LAYERED] });
    fireEvent.click(details());
    expect(screen.getByText("Dosya adı")).toBeTruthy();

    fireEvent.click(tab("Video"));
    expect(screen.getByText("Dosya adı")).toBeTruthy();
    expect(screen.getByText("P0_0.png")).toBeTruthy();
    expect(screen.getByText("1 / 1")).toBeTruthy();

    fireEvent.click(tab("Ses"));
    expect(screen.getByText("Dosya adı")).toBeTruthy();
  });

  it("keeps nothing else behind the row on the video tab", async () => {
    // Read as a list rather than one row at a time: naming the rows that went says nothing about
    // the rows that stayed, and what this item promises is the whole group.
    await open("P0_0", { frames: [LAYERED] });
    fireEvent.click(details());

    fireEvent.click(tab("Video"));

    expect(facts()).toEqual(["Sıra", "Dosya adı"]);
  });

  it("says which model the frame was made with", async () => {
    // Madde 140 made the checkpoint a choice, and three of them render into one gallery. Nothing on
    // screen said which one a frame came from, so a comparison could only be read from memory.
    await open("P0_0", { frames: [LAYERED] });
    fireEvent.click(details());

    expect(screen.getByText("Model").parentElement.textContent).toContain("novaAnimeXL_ilV190");
    // Without this the line above would pass on the stored name as well: it is a prefix match, and
    // the extension is noise in a 300px column that already carries a file name of its own.
    expect(screen.queryByText(/\.safetensors/)).toBeNull();
  });

  it("says a model by the name it was picked by", async () => {
    // A model is stored as its id, because that is what survives a renamed label. `dasiwa` on
    // screen would be an address shown to the person who chose it from a list.
    await open("P0_0", {
      frames: [{ ...LAYERED, model: "dasiwa" }],
      models: [{ value: "dasiwa", label: "DaSiWa Illustrious | Anime" }],
    });
    fireEvent.click(details());

    expect(screen.getByText("Model").parentElement.textContent)
      .toContain("DaSiWa Illustrious | Anime");
  });

  it("falls back to what the frame stored when the row list is not there", async () => {
    // The list is a fetch of its own and it can fail. Drawing nothing would lose a row the frame
    // really does carry; the stored value is worse than the label and better than silence.
    await open("P0_0", { frames: [{ ...LAYERED, model: "dasiwa" }], models: [] });
    fireEvent.click(details());

    expect(screen.getByText("Model").parentElement.textContent).toContain("dasiwa");
  });

  it("says which lora the frame was made with (madde 237)", async () => {
    await open("P0_0", {
      frames: [{ ...LAYERED, model: "nova3dcg", lora: "slime" }],
      models: [{ value: "nova3dcg", label: "Nova 3DCG XL" }],
    });
    fireEvent.click(details());

    expect(screen.getByText("LoRA").parentElement.textContent).toContain("Slime");
  });

  it.each([["usnr", "USNR"], ["none", "Boş"]])(
    "says the lora %s by the name it was picked by (madde 238)", async (value, label) => {
      await open("P0_0", { frames: [{ ...LAYERED, model: "nova3dcg", lora: value }],
                           models: [{ value: "nova3dcg", label: "Nova 3DCG XL" }] });
      fireEvent.click(details());

      expect(screen.getByText("LoRA").parentElement.textContent).toContain(label);
    });

  it("draws no lora row for a frame that never named one", async () => {
    // A name there would be a guess: a recipe:slime frame names no lora and was made with Slime,
    // and a DaSiWa frame sent under Standart was made with none. The model row follows the same
    // rule for a frame that never carried a model (madde 238).
    await open("P0_0", { frames: [{ ...LAYERED, model: "nova3dcg", lora: "" }],
                         models: [{ value: "nova3dcg", label: "Nova 3DCG XL" }] });
    fireEvent.click(details());

    expect(screen.getByText("Model")).toBeTruthy();
    expect(screen.queryByText("LoRA")).toBeNull();
  });

  it("draws no model row for a frame that never carried one", async () => {
    // Frames planned before models could be chosen carry none, and no record says which checkpoint
    // the graph shipped that day. Naming one would be inventing it; the row is simply not drawn --
    // the rule "Üretim modu" already follows. Its lora goes with it for the same reason.
    await open("0_a", { frames: PHOTOS });
    fireEvent.click(details());

    expect(screen.queryByText("Model")).toBeNull();
    expect(screen.queryByText("LoRA")).toBeNull();
  });

  it("keeps the model and the lora on the photo tab alone", async () => {
    // Both are the photo's: video and sound jobs are planned with neither. On their tabs the names
    // would read as what made THAT layer.
    await open("P0_0", { frames: [LAYERED] });
    fireEvent.click(details());

    fireEvent.click(tab("Video"));
    expect(screen.queryByText("Model")).toBeNull();
    expect(screen.queryByText("LoRA")).toBeNull();

    fireEvent.click(tab("Ses"));
    expect(screen.queryByText("Model")).toBeNull();
    expect(screen.queryByText("LoRA")).toBeNull();
  });

  it("keeps the photo tab's facts to their four rows", async () => {
    // The video tab's own list is pinned above. This is the photo tab's, and it pins the order too:
    // the model and its lora go last, behind the two rows that say which frame this is.
    await open("P0_0", { frames: [LAYERED] });
    fireEvent.click(details());

    expect(facts()).toEqual(["Sıra", "Dosya adı", "Model", "LoRA"]);
  });

  it("centres the one line a waiting box holds", async () => {
    // The box is never left blank -- an empty one reads as a prompt someone deleted (karar 24).
    await open("P0_1", { frames: [QUEUED_COPY] });

    fireEvent.click(tab("Video"));

    expect(screen.getByText("Prompt yok — üretimden önce yazılacak.").style.textAlign)
      .toBe("center");
  });

  it("plays the video on its own tab", async () => {
    await open("P0_0", { frames: [LAYERED] });

    fireEvent.click(tab("Video"));

    expect(document.querySelector("video").getAttribute("src"))
      .toBe("/photos/düğün/P0_0_V1_0.mp4");
    expect(document.querySelector("audio")).toBeNull();
  });

  it("brings the sound along on the sound tab", async () => {
    await open("P0_0", { frames: [LAYERED] });

    fireEvent.click(tab("Ses"));

    expect(document.querySelector("video")).toBeTruthy();
    expect(document.querySelector("audio").getAttribute("src"))
      .toBe("/photos/düğün/P0_0_V1_0_S1_0.wav");
  });

  it("leaves the photo tab as it was", async () => {
    await open("P0_0", { frames: [LAYERED] });

    expect(document.querySelector("video")).toBeNull();
    expect(screen.getByAltText("P0_0.png")).toBeTruthy();
  });

  it("draws a waiting frame's two lines faintly", async () => {
    await open("P0_0", { frames: [{ id: "P0_0", file: "P0_0.png", status: "pending", prompt: "p",
                                    layers: {}, failed: [], owed: ["photo"], prompts: {} }] });

    expect(screen.getByText("bekliyor").closest("[data-holder]").style.opacity).toBe("0.45");
  });

  it("keeps the open tab when the next frame has that layer too", async () => {
    // The arrows swap the frame under a mounted page. Stepping through a run of videos should not
    // drop the user back on the photo at every step and make them pick the video again.
    listFrames.mockResolvedValue([LAYERED, SECOND_VIDEO]);
    getStatus.mockResolvedValue(IDLE);
    const { rerender } = render(<PhotoDetail project="düğün" frame="P0_0" />);
    await settle();
    fireEvent.click(tab("Video"));

    rerender(<PhotoDetail project="düğün" frame="P1_0" />);
    await settle();

    expect(tab("Video").getAttribute("aria-current")).toBe("page");
    expect(screen.getByText("1 / 2")).toBeTruthy();         // it really is the next frame
  });

  it("falls back to the photo when the next frame has no such layer", async () => {
    listFrames.mockResolvedValue([LAYERED, SECOND]);
    getStatus.mockResolvedValue(IDLE);
    const { rerender } = render(<PhotoDetail project="düğün" frame="P0_0" />);
    await settle();
    fireEvent.click(tab("Video"));

    rerender(<PhotoDetail project="düğün" frame="P1_0" />);
    await settle();

    // This is what the reset was for, and it is the half that stays: an open tab on a layer the
    // frame never had would be a tab on nothing.
    expect(tab("Foto").getAttribute("aria-current")).toBe("page");
    expect(tab("Video").disabled).toBe(true);
  });
});

describe("PhotoDetail — the details section (madde 399)", () => {
  // The owner found the column crowded: the counter stays on top, and what made the frame folds
  // away behind one row that starts closed -- the design's own (tasarım 200).
  it("opens the column with the counter alone and the section closed", async () => {
    await open("P0_0", { frames: [LAYERED] });

    expect(facts()).toEqual(["Sıra"]);
    expect(details().getAttribute("aria-expanded")).toBe("false");
    expect(screen.queryByText("Dosya adı")).toBeNull();
  });

  it("opens the frame's facts under the row on a press, and folds them on the next", async () => {
    await open("P0_0", { frames: [LAYERED] });

    fireEvent.click(details());

    expect(details().getAttribute("aria-expanded")).toBe("true");
    // Under the row, in the order they always had -- not back in the counter's group.
    expect(facts(document.querySelector('[data-group="details"]')))
      .toEqual(["Dosya adı", "Model", "LoRA"]);

    fireEvent.click(details());

    expect(details().getAttribute("aria-expanded")).toBe("false");
    expect(facts()).toEqual(["Sıra"]);
  });

  it("turns the caret up while the section is open", async () => {
    await open("P0_0", { frames: [LAYERED] });
    const caret = () => details().querySelector("[data-caret]");

    expect(caret().querySelector("svg")).toBeTruthy();
    expect(caret().style.transform).not.toContain("rotate");

    fireEvent.click(details());

    expect(caret().style.transform).toBe("rotate(180deg)");
  });

  it("keeps the section open when the tab changes", async () => {
    await open("P0_0", { frames: [{ ...LAYERED, modes: { video: "loop" } }] });
    fireEvent.click(details());

    fireEvent.click(tab("Video"));

    expect(details().getAttribute("aria-expanded")).toBe("true");
    // The video tab's own facts, each under the condition it always had.
    expect(facts()).toEqual(["Sıra", "Dosya adı", "Üretim modu"]);
  });

  it("keeps the section open while the arrows walk to another frame", async () => {
    // The arrows swap the frame under a page that stays mounted. The press was the user's, not
    // the frame's, so it walks on with them.
    listFrames.mockResolvedValue([LAYERED, SECOND]);
    getStatus.mockResolvedValue(IDLE);
    listModels.mockResolvedValue({ models: [], loras: LORAS });
    const { rerender } = render(<PhotoDetail project="düğün" frame="P0_0" />);
    await settle();
    fireEvent.click(details());

    rerender(<PhotoDetail project="düğün" frame="P1_0" />);
    await settle();

    expect(details().getAttribute("aria-expanded")).toBe("true");
    expect(screen.getByText("P1_0.png")).toBeTruthy();
  });

  it("draws the row as a label, with no box", async () => {
    await open("P0_0", { frames: [LAYERED] });

    // The column's own label face, and nothing drawn around it.
    expect(details().style.background).toBe("none");
    expect(screen.getByText("Ayrıntılar").style.textTransform).toBe("uppercase");
  });
});

describe("PhotoDetail — the frame's scenario (madde 401)", () => {
  // The frame carries its scenario so the user can see whether the prompts match the picture. One
  // press lays it over the picture and the next takes it away; nothing here writes it (tasarım 196).
  const SCENED = { ...LAYERED, scene: SCENE };

  it("puts a Senaryo button after the three tabs, set apart by a thin line", async () => {
    await open("P0_0", { frames: [SCENED] });

    const [line, button] = [...document.querySelector("[data-strip]").children].slice(-2);
    expect(button).toBe(scenario());
    expect(line.style.width).toBe("1px");
    expect(line.style.background).toBe("var(--border)");
    // Its own look rather than a fourth tab's: no stroke box and no ground.
    expect(button.className).not.toContain("wf-stroke");
    expect(button.style.background).toBe("none");
    expect(button.querySelector("[data-glyph=scenario]")).toBeTruthy();
  });

  it("starts closed, with nothing laid over the picture", async () => {
    await open("P0_0", { frames: [SCENED] });

    expect(scenario().getAttribute("aria-pressed")).toBe("false");
    expect(sceneCard()).toBeNull();
  });

  it("opens the frame's scenario over the picture on a press, and closes it on the next", async () => {
    await open("P0_0", { frames: [SCENED] });

    fireEvent.click(scenario());

    expect(sceneCard().textContent).toBe(SCENE);
    // Read, never written: the scenario came with QueenAgent's list and no box here holds it.
    expect(screen.queryByDisplayValue(SCENE)).toBeNull();

    fireEvent.click(scenario());

    expect(sceneCard()).toBeNull();
  });

  it("lights the button while the card is open", async () => {
    await open("P0_0", { frames: [SCENED] });
    expect(scenario().style.color).toBe("var(--ink-3)");

    fireEvent.click(scenario());

    expect(scenario().getAttribute("aria-pressed")).toBe("true");
    expect(scenario().style.color).toBe("var(--accent)");
  });

  it("lays the card along the photo's bottom edge, in the page's translucent dark", async () => {
    await open("P0_0", { frames: [SCENED] });

    fireEvent.click(scenario());

    // The owner's pick of the design's three places: the bottom edge. Inside the picture's own box,
    // so the 12 is measured from the photo and not from the stage around it.
    const card = sceneCard();
    expect(card.parentElement.contains(screen.getByAltText("P0_0.png"))).toBe(true);
    expect(card.parentElement.style.position).toBe("relative");
    expect(card.style.position).toBe("absolute");
    expect([card.style.left, card.style.right, card.style.bottom])
      .toEqual(["12px", "12px", "12px"]);
    // The same dark the page's other boxes over the picture stand on.
    expect(card.style.background).toMatch(/rgba\(10,\s*8,\s*7,\s*0?\.72\)/);
    // The player takes a click on the picture to play and pause; the card must never take it.
    expect(card.style.pointerEvents).toBe("none");
  });

  it.each(["Video", "Ses"])("lifts the card over the player's clock on the %s tab", async (name) => {
    await open("P0_0", { frames: [SCENED] });
    fireEvent.click(scenario());

    fireEvent.click(tab(name));

    // The clock and its line, or the waveform, run along the player's bottom: the card stands above
    // that strip instead of covering it.
    expect(sceneCard().parentElement.hasAttribute("data-scene")).toBe(true);
    expect(sceneCard().style.bottom).toBe("40px");
  });

  it("keeps the card on the picture while a layer is made over it", async () => {
    await open("P0_0", { frames: [{ ...RENDERING, scene: SCENE }],
                         status: { status: "running", project: "düğün",
                                   current: { id: "P0_0", type: "video" } } });
    fireEvent.click(scenario());

    fireEvent.click(tab("Video"));

    const box = sceneCard().parentElement;
    expect(box.contains(screen.getByAltText("P0_0.png"))).toBe(true);
    expect(box.querySelector("[data-making]")).toBeTruthy();
    expect(sceneCard().style.bottom).toBe("12px");
  });

  // A frame with no picture yet still has its scenario: it says what the picture is going to be.
  const HELD = { id: "P0_0", file: "P0_0.png", status: "pending", prompt: "p", negative: "",
                 layers: {}, failed: [], owed: ["photo"], prompts: {}, scene: SCENE };
  it.each([
    ["waiting", HELD, IDLE],
    ["being made", HELD, { status: "running", project: "düğün", current: { id: "P0_0" } }],
    ["broken", { ...BROKEN, scene: SCENE }, IDLE],
  ])("lays the card on the holder of a frame that is %s", async (_, frame, status) => {
    await open("P0_0", { frames: [frame], status });

    fireEvent.click(scenario());

    expect(sceneCard().parentElement.className).toContain("wf-img");
    expect(sceneCard().textContent).toBe(SCENE);
  });

  it("says so, dimmed, on a frame with no scenario", async () => {
    await open("P0_0", { frames: [{ ...LAYERED, scene: "" }] });

    fireEvent.click(scenario());

    expect(sceneCard().textContent).toBe("Bu karenin senaryosu yok");
    // Dimmed: a notice about an absence, not a sentence of the frame's own.
    expect(sceneCard().style.color).toMatch(/rgba\(255,\s*255,\s*255,\s*0?\.55\)/);
  });

  it("keeps the card open when the tab changes", async () => {
    await open("P0_0", { frames: [SCENED] });
    fireEvent.click(scenario());

    fireEvent.click(tab("Video"));

    expect(scenario().getAttribute("aria-pressed")).toBe("true");
    expect(sceneCard().textContent).toBe(SCENE);
  });

  it("keeps the card open while the arrows walk to another frame, and reads the new one's", async () => {
    // The arrows swap the frame under a page that stays mounted. The press was the user's, not the
    // frame's, so it walks on with them -- a run of frames checked against their scenarios costs
    // one press.
    listFrames.mockResolvedValue([SCENED, { ...SECOND, scene: SECOND_SCENE }]);
    getStatus.mockResolvedValue(IDLE);
    listModels.mockResolvedValue({ models: [], loras: LORAS });
    const { rerender } = render(<PhotoDetail project="düğün" frame="P0_0" />);
    await settle();
    fireEvent.click(scenario());

    rerender(<PhotoDetail project="düğün" frame="P1_0" />);
    await settle();

    expect(scenario().getAttribute("aria-pressed")).toBe("true");
    expect(sceneCard().textContent).toBe(SECOND_SCENE);
  });
});

// The second frame with a sound of its own, for the sound tab to step onto.
const SECOND_SOUND = { ...SECOND_VIDEO,
                       layers: { ...SECOND_VIDEO.layers, audio: "P1_0_V1_0_S1_0.wav" },
                       prompts: { ...SECOND_VIDEO.prompts, audio: "adım sesleri" } };

describe("PhotoDetail — the stage follows the frame (madde 232)", () => {
  // Opens the first frame on the given tab and hands back the way to step onto the second.
  async function stepping(frames, tabName) {
    listFrames.mockResolvedValue(frames);
    getStatus.mockResolvedValue(IDLE);
    listModels.mockResolvedValue({ models: [], loras: LORAS });
    const { rerender } = render(<PhotoDetail project="düğün" frame="P0_0" />);
    await settle();
    if (tabName) fireEvent.click(tab(tabName));
    return async () => {
      rerender(<PhotoDetail project="düğün" frame="P1_0" />);
      await settle();
    };
  }

  it("throws the old picture away when the frame changes", async () => {
    // A kept <img> with a new src goes on drawing the old picture until the new one loads -- the
    // column says one frame while the stage shows another.
    const next = await stepping([LAYERED, SECOND]);
    const before = screen.getByAltText("P0_0.png");

    await next();

    expect(before.isConnected).toBe(false);
    expect(screen.getByAltText("P1_0.png")).toBeTruthy();
  });

  it("says it is loading until the new picture arrives", async () => {
    const next = await stepping([LAYERED, SECOND]);
    fireEvent.load(screen.getByAltText("P0_0.png"));

    await next();

    expect(screen.getByText("yükleniyor…")).toBeTruthy();
    fireEvent.load(screen.getByAltText("P1_0.png"));
    expect(screen.queryByText("yükleniyor…")).toBeNull();
  });

  it("says so when the picture does not come, and which one", async () => {
    const next = await stepping([LAYERED, SECOND]);

    await next();
    fireEvent.error(screen.getByAltText("P1_0.png"));

    expect(screen.getByText("Dosya yüklenemedi")).toBeTruthy();
    expect(screen.queryByText("yükleniyor…")).toBeNull();
    // The browser gives no reason for a failed image, so the address is what is known -- and what
    // the copy button hands over.
    expect(document.querySelector("[data-raw]").textContent).toContain("/photos/düğün/P1_0.png");
  });

  it("throws the old video away when the frame changes", async () => {
    const next = await stepping([LAYERED, SECOND_VIDEO], "Video");
    const before = document.querySelector("video");

    await next();

    expect(before.isConnected).toBe(false);
    expect(document.querySelector("video").getAttribute("src")).toBe("/photos/düğün/P1_0_V1_0.mp4");
  });

  it("throws the old sound away when the frame changes", async () => {
    const next = await stepping([LAYERED, SECOND_SOUND], "Ses");
    const before = document.querySelector("audio");

    await next();

    expect(before.isConnected).toBe(false);
    expect(document.querySelector("audio").getAttribute("src"))
      .toBe("/photos/düğün/P1_0_V1_0_S1_0.wav");
  });

  it("says it is loading until the video arrives", async () => {
    const next = await stepping([LAYERED, SECOND_VIDEO], "Video");

    await next();

    expect(screen.getByText("yükleniyor…")).toBeTruthy();
    fireEvent.loadedData(document.querySelector("video"));
    expect(screen.queryByText("yükleniyor…")).toBeNull();
  });

  it("says so when the video does not come, and which one", async () => {
    const next = await stepping([LAYERED, SECOND_VIDEO], "Video");

    await next();
    fireEvent.error(document.querySelector("video"));

    expect(screen.getByText("Dosya yüklenemedi")).toBeTruthy();
    expect(document.querySelector("[data-raw]").textContent)
      .toContain("/photos/düğün/P1_0_V1_0.mp4");
  });
});

describe("PhotoDetail — how the video was made", () => {
  const LOOPED = { ...LAYERED, modes: { video: "loop" } };
  const LINKED = { ...LAYERED, modes: { video: "linked" }, endsOn: { video: "P1_0.png" } };

  it("says which mode made this video", async () => {
    await open("P0_0", { frames: [LOOPED] });
    fireEvent.click(details());

    fireEvent.click(tab("Video"));

    // Read off the row itself: Loop is also one of the options in the Yeni mod box below, and a
    // bare text match would be happy with either.
    expect(screen.getByText("Üretim modu").parentElement.textContent).toContain("Loop");
  });

  it("names the picture a linked video ended on", async () => {
    // The file rather than the frame's number: the sequence can be dragged, and then the number
    // would be a lie about a video nobody touched.
    await open("P0_0", { frames: [LINKED] });
    fireEvent.click(details());

    fireEvent.click(tab("Video"));

    expect(screen.getByText("Sonrakine bağla → P1_0.png")).toBeTruthy();
  });

  it("says it and nothing more -- there is nothing here to press", async () => {
    // Changing the mode is making the video again, and that is the form below.
    await open("P0_0", { frames: [LOOPED] });
    fireEvent.click(details());

    fireEvent.click(tab("Video"));

    expect(screen.getByText("Üretim modu").parentElement.querySelector("button")).toBeNull();
    expect(screen.getByText("Üretim modu").parentElement.querySelector("select")).toBeNull();
  });

  it("never draws the row on the sound tab", async () => {
    // The sound tab shows the video's file name, because the sound was laid over it -- but the
    // video's mode is not a fact about the sound.
    await open("P0_0", { frames: [LOOPED] });
    fireEvent.click(details());

    fireEvent.click(tab("Ses"));

    expect(screen.queryByText("Üretim modu")).toBeNull();
  });

  it("never draws it on the photo tab either", async () => {
    await open("P0_0", { frames: [LOOPED] });
    fireEvent.click(details());

    expect(screen.queryByText("Üretim modu")).toBeNull();
  });

  it("stays quiet about a video whose line never named a mode", async () => {
    // Videos already on Drive were produced before modes existed. An empty row would be a question
    // rather than an answer.
    await open("P0_0", { frames: [LAYERED] });
    fireEvent.click(details());

    fireEvent.click(tab("Video"));

    expect(screen.queryByText("Üretim modu")).toBeNull();
  });
});

describe("PhotoDetail — the new mode", () => {
  // The gallery's top is the film's last frame: the export stitches it reversed. NEWER stands above
  // P0_0, so P0_0 has somewhere to link to and NEWER has not.
  const LOOPED = { ...LAYERED, modes: { video: "loop" } };
  const NEWER = { id: "P1_0", file: "P1_0.png", status: "done", prompt: "sonraki", negative: "",
                  layers: { photo: "P1_0.png" }, failed: [], owed: [], prompts: {} };
  const UNMADE = { ...NEWER, status: "pending", layers: {}, owed: ["photo"] };
  const modeBox = () => screen.getByLabelText("Yeni mod");

  async function openVideo(frames) {
    await open("P0_0", { frames });
    fireEvent.click(tab("Video"));
  }

  it("offers the new mode, opened on the one this video was made in", async () => {
    await openVideo([NEWER, LOOPED]);

    expect(modeBox().value).toBe("loop");
  });

  it("opens on the plain one when the video's line never named a mode", async () => {
    await openVideo([NEWER, LAYERED]);

    expect(modeBox().value).toBe("standard");
  });

  it("keeps the video's own mode when nobody touched the box", async () => {
    // The point of the default: a user who only edited the prompt gets the video they had.
    regenerateFrame.mockResolvedValue({ job: "running", frame: "P0_1" });
    await openVideo([NEWER, LOOPED]);

    await act(async () => { fireEvent.click(regenButton()); });

    // No negative on a video: only a photo is made from one (Fark 98).
    expect(regenerateFrame)
      .toHaveBeenCalledWith("düğün", "P0_0", "video", "kadın dönüyor", "loop", undefined);
  });

  it("sends the mode that was picked", async () => {
    regenerateFrame.mockResolvedValue({ job: "running", frame: "P0_1" });
    await openVideo([NEWER, LOOPED]);

    fireEvent.change(modeBox(), { target: { value: "standard" } });
    await act(async () => { fireEvent.click(regenButton()); });

    expect(regenerateFrame).toHaveBeenCalledWith("düğün", "P0_0", "video", "kadın dönüyor",
                                                 "standard", undefined);
  });

  it("marks the box once the mode is no longer the video's own", async () => {
    await openVideo([NEWER, LOOPED]);

    fireEvent.change(modeBox(), { target: { value: "standard" } });

    expect(modeBox().style.borderColor).toBe("var(--accent)");
  });

  it("closes production when the film's last frame is asked to link", async () => {
    // The gallery's top. The design refused both a disabled option and an error after the press:
    // the option is pickable, and picking it says why and shuts the button.
    await openVideo([LOOPED]);

    fireEvent.change(modeBox(), { target: { value: "linked" } });

    expect(modeBox().style.borderColor).toBe("var(--danger)");
    expect(screen.getByText("Bu son kare — bağlanacak sonraki kare yok.")).toBeTruthy();
    expect(regenButton().disabled).toBe(true);
  });

  it("closes it too when the next frame has no picture yet", async () => {
    // The design never named this one. Letting it through would be the error-after-the-press it
    // refused, so it closes the same way and says its own reason.
    await openVideo([UNMADE, LOOPED]);

    fireEvent.change(modeBox(), { target: { value: "linked" } });

    expect(screen.getByText("Sonraki karenin fotoğrafı henüz üretilmedi.")).toBeTruthy();
    expect(regenButton().disabled).toBe(true);
  });

  it("leaves linking alive where there is something to link to", async () => {
    await openVideo([NEWER, LOOPED]);

    fireEvent.change(modeBox(), { target: { value: "linked" } });

    expect(regenButton().disabled).toBe(false);
    expect(screen.queryByText(/bağlanacak sonraki kare yok/)).toBeNull();
  });

  it("says what pressing would open", async () => {
    await openVideo([NEWER, LOOPED]);

    expect(screen.getByText("Yeni bir kare açılır — P0_0 kopyası, loop video.")).toBeTruthy();
  });

  it("follows the mode with that line", async () => {
    await openVideo([NEWER, LOOPED]);

    fireEvent.change(modeBox(), { target: { value: "linked" } });

    expect(screen.getByText("Yeni bir kare açılır — P0_0 kopyası, bağlı video.")).toBeTruthy();
  });

  it("puts none of it on the photo tab", async () => {
    // A photo arrives nowhere, and the design wrote no sentence for what its regenerate would open.
    await open("P0_0", { frames: [NEWER, LOOPED] });

    expect(screen.queryByLabelText("Yeni mod")).toBeNull();
    expect(screen.queryByText(/Yeni bir kare açılır/)).toBeNull();
  });

  it("puts none of it on the sound tab either", async () => {
    await open("P0_0", { frames: [NEWER, LOOPED] });

    fireEvent.click(tab("Ses"));

    expect(screen.queryByLabelText("Yeni mod")).toBeNull();
    expect(screen.queryByText(/Yeni bir kare açılır/)).toBeNull();
  });
});

describe("PhotoDetail", () => {
  it("shows the position, the file name and the prompt", async () => {
    await open("1_a");
    fireEvent.click(details());

    expect(screen.getByText("2 / 3")).toBeTruthy();
    expect(screen.getByText("1_a.png")).toBeTruthy();
    expect(screen.getByDisplayValue("ikinci")).toBeTruthy();
  });

  it("moves to the next photo with the arrow", async () => {
    await open("1_a");

    fireEvent.click(screen.getByText("›"));

    expect(navigate).toHaveBeenCalledWith("/projects/düğün/photos/0_a");
  });

  it("leaves the back arrow dead on the first photo", async () => {
    await open("2_a");

    fireEvent.click(screen.getByText("‹"));

    expect(navigate).not.toHaveBeenCalled();
  });

  it("responds to the arrow keys and Esc", async () => {
    await open("1_a");

    fireEvent.keyDown(window, { key: "ArrowLeft" });
    expect(navigate).toHaveBeenCalledWith("/projects/düğün/photos/2_a");

    fireEvent.keyDown(window, { key: "Escape" });
    expect(navigate).toHaveBeenCalledWith("/projects/düğün");
  });

  it("asks before deleting, then opens the next photo", async () => {
    removeFrames.mockResolvedValue({ deleted: ["1_a.png"], removed: [] });
    await open("1_a");

    fireEvent.click(screen.getByText("Sil"));
    expect(screen.getByText("1 kare silinsin mi?")).toBeTruthy();
    // Nothing but a picture on this one, so the window promises nothing beyond the frame.
    expect(screen.getByText("Bu işlem geri alınamaz.")).toBeTruthy();
    expect(removeFrames).not.toHaveBeenCalled();

    await act(async () => { fireEvent.click(confirmButton()); });

    expect(removeFrames).toHaveBeenCalledWith("düğün", ["1_a"]);
    expect(navigate).toHaveBeenCalledWith("/projects/düğün/photos/0_a");
  });

  it("falls back to the previous photo when the last one is deleted", async () => {
    removeFrames.mockResolvedValue({ deleted: ["0_a.png"], removed: [] });
    await open("0_a");

    fireEvent.click(screen.getByText("Sil"));
    await act(async () => { fireEvent.click(confirmButton()); });

    expect(navigate).toHaveBeenCalledWith("/projects/düğün/photos/1_a");
  });

  it("counts the frame's own layers before deleting it", async () => {
    await open("1_a", { frames: [{ ...done("1_a.png", "ikinci"),
                                   layers: { photo: "1_a.png", video: "1_a_V1_0.mp4" } }] });

    fireEvent.click(screen.getByText("Sil"));

    expect(screen.getByText(
      "Karenin videosu da birlikte silinir (1 video). Bu işlem geri alınamaz.")).toBeTruthy();
  });

  it("shows an error card for a file that is not in the list", async () => {
    await open("yok");

    expect(screen.getByText("Kare bulunamadı")).toBeTruthy();
  });
});

describe("PhotoDetail — deleting keeps the direction (madde 234)", () => {
  // Newest first, as the gallery stands: ‹ steps to the frame above in this list, › to the one below.
  const FIVE = [done("4_a.png", "beşinci"), done("3_a.png", "dördüncü"), done("2_a.png", "üçüncü"),
                done("1_a.png", "ikinci"), done("0_a.png", "ilk")];

  // The router swaps the frame under a page that stays mounted, so a test does the same: one
  // render, then rerender on the frame the press navigated to.
  async function mount(fid, frames = FIVE) {
    listFrames.mockResolvedValue(frames);
    getStatus.mockResolvedValue(IDLE);
    listModels.mockResolvedValue({ models: [], loras: LORAS });
    const view = render(<PhotoDetail project="düğün" frame={fid} />);
    await settle();
    return (next) => { view.rerender(<PhotoDetail project="düğün" frame={next} />); return settle(); };
  }

  // The answer names the frame by identity, so the hook takes it out of its own list and the next
  // deletion looks at the neighbours that are really left.
  async function remove(fid) {
    removeFrames.mockResolvedValue({ deleted: [fid], removed: [] });
    navigate.mockClear();
    fireEvent.click(screen.getByText("Sil"));
    await act(async () => { fireEvent.click(confirmButton()); });
  }

  it("after the back arrow, deleting opens the frame before it", async () => {
    const goTo = await mount("1_a");
    fireEvent.click(screen.getByText("‹"));
    await goTo("2_a");

    await remove("2_a");

    expect(navigate).toHaveBeenCalledWith("/projects/düğün/photos/3_a");
  });

  it("after the left key, deleting opens the frame before it", async () => {
    const goTo = await mount("1_a");
    fireEvent.keyDown(window, { key: "ArrowLeft" });
    await goTo("2_a");

    await remove("2_a");

    expect(navigate).toHaveBeenCalledWith("/projects/düğün/photos/3_a");
  });

  it("after the forward arrow, deleting opens the frame after it", async () => {
    const goTo = await mount("3_a");
    fireEvent.click(screen.getByText("›"));
    await goTo("2_a");

    await remove("2_a");

    expect(navigate).toHaveBeenCalledWith("/projects/düğün/photos/1_a");
  });

  it("a second deletion keeps walking backwards", async () => {
    const goTo = await mount("1_a");
    fireEvent.keyDown(window, { key: "ArrowLeft" });
    await goTo("2_a");
    await remove("2_a");
    await goTo("3_a");

    await remove("3_a");

    expect(navigate).toHaveBeenCalledWith("/projects/düğün/photos/4_a");
  });

  it("walking backwards off the end, deleting falls to the frame after it", async () => {
    const goTo = await mount("3_a");
    fireEvent.click(screen.getByText("‹"));
    await goTo("4_a");

    await remove("4_a");

    expect(navigate).toHaveBeenCalledWith("/projects/düğün/photos/3_a");
  });
});

describe("PhotoDetail — the counter is the gallery's badge", () => {
  it("gives the newest frame the largest number, the same one its tile carries", async () => {
    await open("2_a");

    expect(screen.getByText("3 / 3")).toBeTruthy();
  });

  it("gives the oldest frame 1, and leaves the forward arrow dead there", async () => {
    await open("0_a");

    expect(screen.getByText("1 / 3")).toBeTruthy();
    fireEvent.click(screen.getByText("›"));
    expect(navigate).not.toHaveBeenCalled();
  });

  it("walks the whole sequence, pending and failed frames included", async () => {
    await open("3_a", { frames: MIXED });

    expect(screen.getByText("4 / 4")).toBeTruthy();
    fireEvent.click(screen.getByText("›"));

    expect(navigate).toHaveBeenCalledWith("/projects/düğün/photos/2_a");
  });
});

describe("PhotoDetail — a frame that is not a photo yet", () => {
  it("says the frame is not produced instead of claiming it is missing", async () => {
    await open("3_a", { frames: MIXED });

    expect(screen.queryByText("Kare bulunamadı")).toBeNull();
    expect(screen.getByText("henüz üretilmedi")).toBeTruthy();
    expect(screen.getByText(/dördüncü/)).toBeTruthy();
  });

  it("calls the file name planned, and only for the frames that have no file", async () => {
    await open("3_a", { frames: MIXED });
    fireEvent.click(details());

    expect(screen.getByText("Dosya adı (planlanan)")).toBeTruthy();
    expect(screen.queryByText("Dosya adı")).toBeNull();
  });

  it("keeps the plain label on a produced photo", async () => {
    await open("0_a", { frames: MIXED });
    fireEvent.click(details());

    expect(screen.getByText("Dosya adı")).toBeTruthy();
    expect(screen.queryByText("Dosya adı (planlanan)")).toBeNull();
  });

  it("takes the frame out of the queue without asking, then opens the next one", async () => {
    removeFrames.mockResolvedValue({ deleted: [], removed: ["3_a.png"] });
    await open("3_a", { frames: MIXED });

    await act(async () => { fireEvent.click(screen.getByText("Kuyruktan çıkar")); });

    expect(removeFrames).toHaveBeenCalledWith("düğün", ["3_a"]);
    expect(navigate).toHaveBeenCalledWith("/projects/düğün/photos/2_a");
  });

  it("stays on the page and says so when the server refuses to remove it", async () => {
    removeFrames.mockRejectedValue(new Error("Proje yok: düğün"));
    await open("3_a", { frames: MIXED });

    await act(async () => { fireEvent.click(screen.getByText("Kuyruktan çıkar")); });

    expect(navigate).not.toHaveBeenCalled();
    expect(screen.getByText("Kare kuyruktan çıkarılamadı")).toBeTruthy();
    expect(screen.getByText(/Proje yok/)).toBeTruthy();
  });

  it("leaves the refusal behind when the arrows move on to another frame", async () => {
    removeFrames.mockRejectedValue(new Error("Proje yok: düğün"));
    listFrames.mockResolvedValue(MIXED);
    getStatus.mockResolvedValue(IDLE);
    const { rerender } = render(<PhotoDetail project="düğün" frame="3_a" />);
    await settle();
    await act(async () => { fireEvent.click(screen.getByText("Kuyruktan çıkar")); });
    expect(screen.getByText("Kare kuyruktan çıkarılamadı")).toBeTruthy();

    // The page stays mounted while the router swaps the frame under it.
    rerender(<PhotoDetail project="düğün" frame="1_a" />);
    await settle();

    expect(screen.queryByText("Kare kuyruktan çıkarılamadı")).toBeNull();
  });

  it("draws a failed frame red and offers to delete it, not to dequeue it", async () => {
    await open("1_a", { frames: MIXED });

    expect(screen.getByText("Bu kare üretilemedi")).toBeTruthy();
    // Nothing is coming for it any more, so it is not in the queue to be taken out of.
    expect(screen.getByText("Kareyi sil")).toBeTruthy();
    expect(screen.queryByText("Sil")).toBeNull();
  });
});

describe("PhotoDetail — the frame the worker is holding", () => {
  it("spins instead of showing a photo, and lets nothing be pressed", async () => {
    await open("2_a", { frames: MIXED, status: RUNNING });

    expect(document.querySelector(".wf-spinner")).toBeTruthy();
    expect(screen.queryByText("Çalışıyor")).toBeNull();
    expect(screen.queryByText("henüz üretilmedi")).toBeNull();
    expect(screen.getByText("Kuyruktan çıkar").disabled).toBe(true);
  });

  it("becomes the photo in place when the render lands, with no reload", async () => {
    await open("2_a", { frames: MIXED, status: RUNNING });
    expect(screen.queryByAltText("2_a.png")).toBeNull();

    // The next poll: the worker moved on and the frame now has a line on disk.
    listFrames.mockResolvedValue(MIXED.map((frame) => (frame.file === "2_a.png"
      ? { ...frame, status: "done" }
      : frame)));
    getStatus.mockResolvedValue(IDLE);
    await settle(2000);

    expect(screen.getByAltText("2_a.png")).toBeTruthy();
    expect(screen.queryByText("Çalışıyor")).toBeNull();
  });
});

describe("PhotoDetail — regenerating", () => {
  it("lets the open layer's prompt be edited and marks the box as changed", async () => {
    await open("P0_0", { frames: [LAYERED] });
    const box = screen.getByDisplayValue("kırmızı elbise");
    expect(box.style.borderColor).not.toBe("var(--accent)");

    fireEvent.change(box, { target: { value: "mavi elbise" } });

    expect(screen.getByDisplayValue("mavi elbise").style.borderColor).toBe("var(--accent)");
  });

  it("leaves the box unmarked when only the space around the words changed", async () => {
    await open("P0_0", { frames: [LAYERED] });
    // The same node all the way through: the box is queried before the edit, because a display
    // value is matched with its whitespace collapsed and could not tell the two apart.
    const box = screen.getByDisplayValue("kırmızı elbise");

    fireEvent.change(box, { target: { value: "  kırmızı elbise\n" } });

    expect(box.value).toBe("  kırmızı elbise\n");
    expect(box.style.borderColor).not.toBe("var(--accent)");
  });

  it("keeps the button accent whether the prompt was touched or not", async () => {
    await open("P0_0", { frames: [LAYERED] });

    expect(regenButton().className).toContain("wf-btn--hl");
    expect(regenButton().disabled).toBe(false);
  });

  it("sends the open layer and the edited text", async () => {
    regenerateFrame.mockResolvedValue({ frame: "P0_1" });
    await open("P0_0", { frames: [LAYERED] });

    fireEvent.click(tab("Video"));
    fireEvent.change(screen.getByDisplayValue("kadın dönüyor"),
                     { target: { value: "kadın yürüyor" } });
    await act(async () => { fireEvent.click(regenButton()); });

    // The frame's identity, not its file: a copy frame shares its source's picture.
    expect(regenerateFrame).toHaveBeenCalledWith("düğün", "P0_0", "video", "kadın yürüyor",
                                                 "standard", undefined);
  });

  it("says the job went into the queue and refuses a second press", async () => {
    regenerateFrame.mockResolvedValue({ frame: "P0_1" });
    await open("P0_0", { frames: [LAYERED] });

    await act(async () => { fireEvent.click(regenButton()); });

    expect(screen.getByText("Kuyruğa eklendi").closest("button").disabled).toBe(true);
    // And the frame says what is coming: the work landed on a frame of its own.
    expect(screen.getByText("yeniden üretilecek — kuyrukta")).toBeTruthy();
  });

  it("keeps the other tabs pressable after one layer was sent", async () => {
    regenerateFrame.mockResolvedValue({ frame: "P0_1" });
    await open("P0_0", { frames: [LAYERED] });
    await act(async () => { fireEvent.click(regenButton()); });

    fireEvent.click(tab("Video"));

    expect(regenButton().disabled).toBe(false);
  });

  it("stays on the frame and says so when the server refuses", async () => {
    regenerateFrame.mockRejectedValue(new Error("Proje yok: düğün"));
    await open("P0_0", { frames: [LAYERED] });

    await act(async () => { fireEvent.click(regenButton()); });

    expect(screen.getByText("Kare yeniden üretilemedi")).toBeTruthy();
    expect(screen.getByText(/Proje yok/)).toBeTruthy();
    expect(regenButton().disabled).toBe(false);
  });

  it("forgets the editing when another frame is opened", async () => {
    // The arrows swap the frame under a mounted page: the box belongs to the frame, not the page.
    listFrames.mockResolvedValue([LAYERED, SECOND]);
    getStatus.mockResolvedValue(IDLE);
    const { rerender } = render(<PhotoDetail project="düğün" frame="P0_0" />);
    await settle();
    fireEvent.change(screen.getByDisplayValue("kırmızı elbise"),
                     { target: { value: "yeşil elbise" } });

    rerender(<PhotoDetail project="düğün" frame="P1_0" />);
    await settle();

    expect(screen.getByDisplayValue("mavi elbise")).toBeTruthy();
    expect(screen.queryByDisplayValue("yeşil elbise")).toBeNull();
  });

  it("offers nothing to make again on a frame that was never produced", async () => {
    await open("3_a", { frames: MIXED });

    expect(screen.queryByText("Yeniden üret — yeni kare")).toBeNull();
  });
});

describe("PhotoDetail — what the page says it did", () => {
  it("makes the queued pill beat", async () => {
    regenerateFrame.mockResolvedValue({ frame: "P0_2" });
    await open("P0_0", { frames: [LAYERED] });

    await act(async () => { fireEvent.click(regenButton()); });

    // Fark 107: the same live dot the gallery's own running pill carries. Its place does not
    // change -- the corner is fixed to the stage and a photo drawn to fit has no edge to aim at
    // (karar 39).
    expect(screen.getByText("yeniden üretilecek — kuyrukta")
      .querySelector(".qe-dot--alive")).toBeTruthy();
  });

  it("says a retry was a retry and not a new frame", async () => {
    retryFrame.mockResolvedValue({ job: "running" });
    await open("P0_0", { frames: [BROKEN] });

    await act(async () => { fireEvent.click(screen.getByText("Tekrar dene — bu kareye")); });

    // Fark 108: both presses used to leave the same sentence in the corner, and only one of them
    // opens a frame of its own.
    expect(screen.getByText("kuyrukta — tekrar denenecek")).toBeTruthy();
    expect(screen.queryByText("yeniden üretilecek — kuyrukta")).toBeNull();
  });

  it("says on the button that a retry opens no new frame", async () => {
    await open("P0_0", { frames: [BROKEN] });

    // Fark 109: retry is the one exception to uret = ekle, and the button is where that is read.
    expect(screen.getByText("Tekrar dene — bu kareye")).toBeTruthy();
  });

  it("offers a second way out of a failed layer", async () => {
    await open("P0_0", { frames: [{ ...LAYERED, layers: { photo: "P0_0.png" }, failed: ["video"],
                                    errors: { video: "ComfyUI 500 — 3 kez denendi" },
                                    prompts: { photo: "kırmızı elbise" } }] });

    fireEvent.click(tab("Video"));

    // Fark 100: a copy with no video is pointless, so the way out stands beside the way back.
    expect(screen.getByText("Tekrar dene — bu kareye")).toBeTruthy();
    expect(screen.getByText("Kareyi sil")).toBeTruthy();
  });

  it("puts the way out of the queue on the waiting layer's own tab", async () => {
    await open("P0_1", { frames: [QUEUED_COPY] });

    fireEvent.click(tab("Video"));

    // Fark 99: the button lived on the photo tab alone, which is not the tab the user is on when
    // they are looking at what they are waiting for. The words are the photo tab's own -- the
    // queue takes frames out, not layers (karar 38).
    expect(screen.getByText("Kuyruktan çıkar")).toBeTruthy();
  });

  it("draws the regenerate button full size and the delete one small", async () => {
    await open("P0_0", { frames: [LAYERED] });

    // Fark 110: one of the two is what the page is for and the other is the way out. Drawn at the
    // same size, they said they weigh the same.
    expect(regenButton().className).toContain("wf-btn--hl");
    expect(regenButton().className).not.toContain("wf-btn--sm");
    expect(screen.getByText("Sil").closest("button").className).toContain("wf-btn--sm");
  });

  it("drops the red from the delete button while the frame is being made", async () => {
    await open("2_a", { frames: MIXED, status: RUNNING });

    // Fark 111: a disabled button in the destructive colour reads as a refusal rather than a wait.
    const bin = screen.getByText("Kuyruktan çıkar").closest("button");
    expect(bin.disabled).toBe(true);
    expect(bin.style.color).not.toBe("var(--danger)");
    expect(bin.style.borderColor).not.toBe("var(--danger)");
  });
});

describe("PhotoDetail — what each tab offers to destroy", () => {
  it("offers the frame on the photo tab and the layer on the others", async () => {
    await open("P0_0", { frames: [LAYERED] });
    expect(screen.getByText("Sil")).toBeTruthy();

    fireEvent.click(tab("Video"));
    expect(screen.getByText("Videoyu sil — kare kalır")).toBeTruthy();
    expect(screen.queryByText("Sil")).toBeNull();

    fireEvent.click(tab("Ses"));
    expect(screen.getByText("Sesi sil — video kalır")).toBeTruthy();
    expect(screen.queryByText("Videoyu sil — kare kalır")).toBeNull();
  });

  it("keeps the card's own way out on every tab", async () => {
    // Madde 295, the user's own words: going back to the photo tab to throw the card away is the
    // detour. The layer's way out stays beside it -- both are wanted, and they cost different
    // things.
    await open("P0_0", { frames: [LAYERED] });

    fireEvent.click(tab("Video"));
    expect(screen.getByText("Kareyi sil")).toBeTruthy();

    fireEvent.click(tab("Ses"));
    expect(screen.getByText("Kareyi sil")).toBeTruthy();
  });

  it("takes the card and not the layer when that way out is pressed", async () => {
    removeFrames.mockResolvedValue({ deleted: ["P0_0"], removed: [] });
    await open("P0_0", { frames: [LAYERED] });

    fireEvent.click(tab("Video"));
    fireEvent.click(screen.getByText("Kareyi sil"));

    // The selection bar's own window, counting what the card loses with it (Fark 102).
    expect(screen.getByText("1 kare silinsin mi?")).toBeTruthy();
    expect(screen.getByText(/Karenin videosu ve sesi de birlikte silinir/)).toBeTruthy();

    await act(async () => { fireEvent.click(confirmButton()); });

    expect(removeLayer).not.toHaveBeenCalled();
    expect(removeFrames).toHaveBeenCalledWith("düğün", ["P0_0"]);
  });

  it("asks with the design's own words before taking a video", async () => {
    await open("P0_0", { frames: [LAYERED] });

    fireEvent.click(tab("Video"));
    fireEvent.click(screen.getByText("Videoyu sil — kare kalır"));

    expect(screen.getByText("Video silinsin mi?")).toBeTruthy();
    expect(screen.getByText(/üzerindeki ses kalıcı olarak silinir/)).toBeTruthy();
    expect(removeLayer).not.toHaveBeenCalled();
  });

  it("names the file the layer confirm is about to take", async () => {
    await open("P0_0", { frames: [LAYERED] });

    fireEvent.click(tab("Video"));
    fireEvent.click(screen.getByText("Videoyu sil — kare kalır"));

    // Fark 101: a frame carries more than one video across its history, and the window that says
    // one of them is going should say which.
    expect(screen.getByText(/^P0_0_V1_0\.mp4 ve üzerindeki ses/)).toBeTruthy();
  });

  it("counts the frame in the confirm the way the selection bar does", async () => {
    await open("1_a");

    fireEvent.click(screen.getByText("Sil"));

    // Fark 102: one window, one language. The bar says 2 kare silinsin mi and this said something
    // else about one.
    expect(screen.getByText("1 kare silinsin mi?")).toBeTruthy();
  });

  it("says what a sound costs instead", async () => {
    await open("P0_0", { frames: [LAYERED] });

    fireEvent.click(tab("Ses"));
    fireEvent.click(screen.getByText("Sesi sil — video kalır"));

    expect(screen.getByText("Ses silinsin mi?")).toBeTruthy();
    expect(screen.getByText(/video sessiz oynar/)).toBeTruthy();
  });

  it("deletes the open layer and comes back to the photo tab", async () => {
    removeLayer.mockResolvedValue({ deleted: ["P0_0_V1_0.mp4"] });
    await open("P0_0", { frames: [LAYERED] });

    fireEvent.click(tab("Video"));
    fireEvent.click(screen.getByText("Videoyu sil — kare kalır"));
    await act(async () => { fireEvent.click(confirmButton()); });

    expect(removeLayer).toHaveBeenCalledWith("düğün", ["P0_0"], "video");
    // The frame is still the gallery's, so the page stays on it.
    expect(navigate).not.toHaveBeenCalled();
    expect(tab("Foto").getAttribute("aria-current")).toBe("page");
  });

  it("stays on the frame and says so when the server refuses", async () => {
    removeLayer.mockRejectedValue(new Error("Proje yok: düğün"));
    await open("P0_0", { frames: [LAYERED] });

    fireEvent.click(tab("Video"));
    fireEvent.click(screen.getByText("Videoyu sil — kare kalır"));
    await act(async () => { fireEvent.click(confirmButton()); });

    expect(screen.getByText("Video silinemedi")).toBeTruthy();
    expect(screen.getByText(/Proje yok/)).toBeTruthy();
  });

  it("leaves no fill under any of them (madde 83)", async () => {
    await open("P0_0", { frames: [LAYERED] });
    expect(screen.getByText("Sil").closest("button").style.background).toBe("none");

    fireEvent.click(tab("Video"));
    expect(screen.getByText("Videoyu sil — kare kalır").closest("button").style.background)
      .toBe("none");
  });
});

describe("PhotoDetail — a frame that blew up", () => {
  it("says what the renderer said, once", async () => {
    await open("P0_0", { frames: [BROKEN] });

    expect(screen.getByText("Bu kare üretilemedi")).toBeTruthy();
    expect(screen.getByText("CUDA out of memory — 3 kez denendi")).toBeTruthy();
  });

  it("puts the frame back in line without asking", async () => {
    retryFrame.mockResolvedValue({ job: "running" });
    await open("P0_0", { frames: [BROKEN] });

    await act(async () => { fireEvent.click(screen.getByText("Tekrar dene — bu kareye")); });

    expect(retryFrame).toHaveBeenCalledWith("düğün", "P0_0");
    expect(screen.getByText("Kuyruğa eklendi").closest("button").disabled).toBe(true);
  });

  it("calls the frame gone rather than pretending it is queued", async () => {
    await open("P0_0", { frames: [BROKEN] });

    expect(screen.getByText("Kareyi sil")).toBeTruthy();
    expect(screen.queryByText("Kuyruktan çıkar")).toBeNull();
  });

  it("leaves the prompt read-only there", async () => {
    await open("P0_0", { frames: [BROKEN] });

    expect(screen.queryByDisplayValue("kırmızı elbise")).toBeNull();
    expect(screen.getByText("kırmızı elbise")).toBeTruthy();
    expect(screen.queryByText("Yeniden üret — yeni kare")).toBeNull();
  });
});

describe("PhotoDetail — a copy frame waiting in the queue", () => {
  it("shows the picture it holds and says what is coming", async () => {
    await open("P0_1", { frames: [QUEUED_COPY] });

    expect(screen.getByAltText("P0_0.png")).toBeTruthy();
    expect(screen.getByText("video kuyrukta")).toBeTruthy();
  });

  it("keeps the stage's own label in the corner", async () => {
    // The corner became a box of its own so the gallery could stack two labels in it (Fark 64).
    // This page shows one at a time -- and it has to be the same corner, or the label lands
    // wherever the stage's own flexbox puts it.
    await open("P0_1", { frames: [QUEUED_COPY] });

    const corner = document.querySelector("[data-corner]");
    expect(corner.style.top).toBe("6px");
    expect(corner.style.left).toBe("6px");
  });

  it("opens the tab of the layer it is waiting for, with an empty box", async () => {
    await open("P0_1", { frames: [QUEUED_COPY] });

    fireEvent.click(tab("Video"));

    expect(screen.getByText("Prompt yok — üretimden önce yazılacak.")).toBeTruthy();
    // Nothing to make again and nothing to delete: the layer is not there yet.
    expect(screen.queryByText("Yeniden üret — yeni kare")).toBeNull();
    expect(screen.queryByText("Videoyu sil — kare kalır")).toBeNull();
  });

  it("shows the prompt written for the layer it is waiting for", async () => {
    // Madde 403: the prompt is written as the layer is queued, so a waiting video already has its
    // words -- and the box shows them rather than a notice.
    await open("P0_1", { frames: [{ ...QUEUED_COPY,
      prompts: { photo: "kırmızı elbise", video: "kadın başını çeviriyor" } }] });

    fireEvent.click(tab("Video"));

    expect(screen.getByText("kadın başını çeviriyor")).toBeTruthy();
    expect(screen.queryByText("Prompt yok — üretimden önce yazılacak.")).toBeNull();
  });

  it("takes it out of the queue without asking", async () => {
    removeFrames.mockResolvedValue({ deleted: [], removed: ["P0_1"] });
    await open("P0_1", { frames: [QUEUED_COPY] });

    await act(async () => { fireEvent.click(screen.getByText("Kuyruktan çıkar")); });

    // Its identity, not the picture it shares with its source.
    expect(removeFrames).toHaveBeenCalledWith("düğün", ["P0_1"]);
    expect(screen.queryByText("1 kare silinsin mi?")).toBeNull();
  });
});

describe("PhotoDetail — the right column", () => {
  it("names the layer every prompt heading belongs to", async () => {
    await open("P0_0", { frames: [LAYERED] });

    // Fark 88: all three tabs drew the same two words, so the heading said nothing about which
    // layer was under it. The words come off the tabs, so a layer cannot end up with two names.
    expect(screen.getByText("Foto prompt'u")).toBeTruthy();
    expect(screen.getByText("Foto negatif prompt'u")).toBeTruthy();

    fireEvent.click(tab("Video"));
    expect(screen.getByText("Video prompt'u")).toBeTruthy();

    fireEvent.click(tab("Ses"));
    expect(screen.getByText("Ses prompt'u")).toBeTruthy();
  });

  it("gives the photo tab's two boxes their own heights", async () => {
    await open("P0_0", { frames: [LAYERED] });

    // Fark 89: the two boxes used to share whatever the window left over, so a short window
    // squeezed both of them. Their own measure now, and a long text folds inside it.
    const [prompt, negative] = [...document.querySelectorAll("[data-box]")];
    expect([prompt.style.height, negative.style.height]).toEqual(["162px", "96px"]);
    expect([prompt.style.overflowY, negative.style.overflowY]).toEqual(["auto", "auto"]);
  });

  it("gives the video and sound boxes the same measure", async () => {
    await open("P0_0", { frames: [LAYERED] });

    fireEvent.click(tab("Video"));
    expect(document.querySelector("[data-box]").style.height).toBe("150px");

    fireEvent.click(tab("Ses"));
    expect(document.querySelector("[data-box]").style.height).toBe("150px");
  });

  it("puts a copy icon beside every prompt heading", async () => {
    await open("P0_0", { frames: [LAYERED] });

    // Fark 90. The negative is a prompt box too, so it carries one as well.
    expect(screen.getByLabelText("Foto prompt'u — kopyala")).toBeTruthy();
    expect(screen.getByLabelText("Foto negatif prompt'u — kopyala")).toBeTruthy();

    fireEvent.click(tab("Video"));
    expect(screen.getByLabelText("Video prompt'u — kopyala")).toBeTruthy();
  });

  it("copies the box's own text and says so", async () => {
    const writeText = stubClipboard(() => Promise.resolve());
    await open("P0_0", { frames: [LAYERED] });

    fireEvent.click(tab("Video"));
    fireEvent.click(screen.getByLabelText("Video prompt'u — kopyala"));
    await settle();

    // The open layer's words, not the photo's -- there are three boxes on this page across the
    // three tabs and each icon belongs to the one beside it.
    expect(writeText).toHaveBeenCalledWith("kadın dönüyor");
    expect(screen.getByLabelText("Kopyalandı")).toBeTruthy();
  });

  it("says so when the clipboard refuses", async () => {
    stubClipboard(() => Promise.reject(new Error("denied")));
    await open("P0_0", { frames: [LAYERED] });

    fireEvent.click(tab("Video"));
    fireEvent.click(screen.getByLabelText("Video prompt'u — kopyala"));
    await settle();

    // Silence would leave the user believing they had the text, and the box is still selectable
    // by hand -- saying it failed is also saying take it yourself (karar 33).
    expect(screen.getByLabelText("Kopyalanamadı")).toBeTruthy();
  });

  it("leaves the icon unpressable when the box is empty", async () => {
    await open("P0_1", { frames: [QUEUED_COPY] });

    fireEvent.click(tab("Video"));

    // A copy button that copies nothing is a lie; one that comes and goes as the user types makes
    // the heading twitch. It stays and it dims (karar 34).
    expect(screen.getByLabelText("Video prompt'u — kopyala").disabled).toBe(true);
  });

  it("splits the column into its facts, the section and what can be made of it", async () => {
    await open("P0_0", { frames: [LAYERED] });

    // Fark 91: what the frame is, then what can be made of it. No group heading and no rule
    // between them -- the split is where the eye rests, not a line it reads. Madde 399 folds what
    // made the frame into a section of its own between the two.
    const side = document.querySelector("[data-side]");
    expect([...side.children].map((one) => one.getAttribute("data-group")))
      .toEqual(["info", "details", "production"]);
  });

  it("keeps one vertical rhythm down the column", async () => {
    await open("P0_0", { frames: [LAYERED] });
    fireEvent.click(details());

    // Fark 91: three measures became two -- 16 between blocks, 6 between a label and what it
    // labels. The information group wraps on a 300px panel, so its own rows answer to the 16 too.
    // The details section keeps its rows 12 under its own row, and they wrap by the same 16.
    const side = document.querySelector("[data-side]");
    expect(side.style.gap).toBe("16px");
    expect(side.children[0].style.rowGap).toBe("16px");
    expect(side.children[1].style.gap).toBe("12px");
    expect(side.children[1].children[1].style.rowGap).toBe("16px");
    expect(side.children[2].style.gap).toBe("16px");
    expect(document.querySelector("[data-field]").parentElement.style.gap).toBe("6px");
  });

  it("lets the panel scroll rather than clip its own buttons", async () => {
    await open("P0_0", { frames: [LAYERED] });

    // With every box at a fixed height the column has a fixed total, and a window shorter than
    // that would put the delete button somewhere nobody can reach (karar 35).
    expect(document.querySelector("[data-side]").style.overflowY).toBe("auto");
  });
});

describe("PhotoDetail — the negative prompt", () => {
  it("shows the negative next to the prompt", async () => {
    await open("3_a", { frames: MIXED });

    expect(screen.getByText("Foto negatif prompt'u")).toBeTruthy();
    expect(screen.getByText(/bulanık/)).toBeTruthy();
  });

  it("draws the box even when there is no negative, rather than hiding it", async () => {
    await open("1_a");

    // Fark 98 made it writable, so an empty one is an empty box: the dash was what a read-only box
    // said when it had nothing to show.
    expect(screen.getByText("Foto negatif prompt'u")).toBeTruthy();
    expect(document.querySelectorAll("[data-box]")[1].value).toBe("");
  });

  it("lets the negative be edited", async () => {
    await open("P0_0", { frames: [LAYERED] });

    // Fark 98: the prompt was the user's and the negative was not, though the two travel into the
    // same job together.
    fireEvent.change(screen.getByDisplayValue("bulanık"), { target: { value: "bulanık, gürültü" } });

    expect(screen.getByDisplayValue("bulanık, gürültü")).toBeTruthy();
  });

  it("marks the negative's box once it is no longer the frame's own", async () => {
    await open("P0_0", { frames: [LAYERED] });

    const box = screen.getByDisplayValue("bulanık");
    expect(box.style.borderColor).not.toBe("var(--accent)");

    fireEvent.change(box, { target: { value: "bulanık, gürültü" } });

    expect(screen.getByDisplayValue("bulanık, gürültü").style.borderColor).toBe("var(--accent)");
  });

  it("sends the negative that was typed", async () => {
    regenerateFrame.mockResolvedValue({ frame: "P1_0" });
    await open("P0_0", { frames: [LAYERED] });

    fireEvent.change(screen.getByDisplayValue("bulanık"), { target: { value: "gürültü" } });
    await act(async () => { fireEvent.click(regenButton()); });

    // An accent border promising a different frame while the negative never leaves the screen
    // would be the box lying about what it did.
    expect(regenerateFrame)
      .toHaveBeenCalledWith("düğün", "P0_0", "photo", "kırmızı elbise", undefined, "gürültü");
  });

  it("reads a prompt in the same face the panel reads it in", async () => {
    await open("P0_0", { frames: [LAYERED] });

    // Fark 117: the visual language says a prompt box is monospace wherever it stands, and the
    // production panel already obeys it. The same words read in two faces on two screens.
    expect(screen.getByDisplayValue("kırmızı elbise").className).toContain("wf-mono");
  });

  it("keeps the face when the box is only there to be read", async () => {
    await open("3_a", { frames: MIXED });

    expect(screen.getByText("dördüncü").className).toContain("wf-mono");
  });
});

describe("PhotoDetail — the keyboard while a prompt is being typed", () => {
  const promptBox = () => document.querySelector("[data-box]");

  it("leaves the arrow keys to the text they are moving through", async () => {
    // The user's own report: the caret moved AND the page changed frame under it, so what they
    // were writing went with it.
    await open("1_a");

    fireEvent.keyDown(promptBox(), { key: "ArrowRight" });
    fireEvent.keyDown(promptBox(), { key: "ArrowLeft" });

    expect(navigate).not.toHaveBeenCalled();
  });

  it("leaves Escape to the text box as well", async () => {
    // The same mistake seen from the other side: Escape closed the page mid-sentence.
    await open("1_a");

    fireEvent.keyDown(promptBox(), { key: "Escape" });

    expect(navigate).not.toHaveBeenCalled();
  });

  it("still walks the frames when the keys come from outside a box", async () => {
    await open("1_a");

    fireEvent.keyDown(window, { key: "ArrowLeft" });

    expect(navigate).toHaveBeenCalledWith("/projects/düğün/photos/2_a");
  });
});

describe("PhotoDetail — the production time (madde 408)", () => {
  // The fake clock's wall time, and starts measured back from it.
  const NOW = new Date("2026-10-01T10:00:00Z");
  const AGO_46 = "2026-10-01T09:59:14+00:00";
  const timeShown = () => document.querySelector("[data-time]");
  const infoFacts = () => facts(document.querySelector('[data-group="info"]'));
  const making = (extra = {}) => ({ status: "running", project: "düğün",
                                    current: { id: "P0_0", type: "video" }, ...extra });

  beforeEach(() => { vi.setSystemTime(NOW); });

  it("puts the open layer's recorded time beside the counter, with no layer word", async () => {
    await open("P0_0", { frames: [{ ...LAYERED, renderSeconds: { photo: 46.3 } }] });

    expect(infoFacts()).toEqual(["Sıra", "Üretim süresi"]);
    expect(timeShown().textContent).toBe("0:46");
  });

  it("says the time of the layer whose tab is open", async () => {
    await open("P0_0", { frames: [{ ...LAYERED,
                                    renderSeconds: { photo: 46.3, video: 212.0, audio: 19.4 } }] });

    fireEvent.click(tab("Video"));
    expect(timeShown().textContent).toBe("3:32");

    fireEvent.click(tab("Ses"));
    expect(timeShown().textContent).toBe("0:19");
  });

  it("draws no field for a frame made before times were recorded", async () => {
    await open("P0_0", { frames: [LAYERED] });

    expect(infoFacts()).toEqual(["Sıra"]);
    expect(screen.queryByText("Üretim süresi")).toBeNull();
  });

  it("draws no field for a layer that failed", async () => {
    await open("P0_0", { frames: [{ ...LAYERED, layers: { photo: "P0_0.png" },
                                    failed: ["video"], errors: { video: "node 41: OOM" },
                                    renderSeconds: { photo: 46.3 } }] });
    expect(timeShown().textContent).toBe("0:46");

    fireEvent.click(tab("Video"));

    expect(screen.queryByText("Üretim süresi")).toBeNull();
  });

  it("says a queued layer has not started yet", async () => {
    await open("P0_1", { frames: [QUEUED_COPY] });

    fireEvent.click(tab("Video"));

    expect(timeShown().textContent).toBe("henüz başlamadı");
  });

  it("counts the layer being made, live", async () => {
    await open("P0_0", { frames: [RENDERING], status: making({ startedAt: AGO_46 }) });
    fireEvent.click(tab("Video"));

    expect(timeShown().textContent).toBe("0:46");
    expect(timeShown().style.color).toBe("var(--accent)");

    await settle(2000);

    expect(timeShown().textContent).toBe("0:48");
  });

  it("picks up from the server's start when the page is opened mid-render", async () => {
    // A reload must not start the count again from nothing.
    await open("P0_0", { frames: [RENDERING],
                         status: making({ startedAt: "2026-10-01T09:57:00+00:00" }) });
    fireEvent.click(tab("Video"));

    expect(timeShown().textContent).toBe("3:00");
  });

  it("says 0:00 while the model has not been handed the layer yet", async () => {
    await open("P0_0", { frames: [RENDERING], status: making() });
    fireEvent.click(tab("Video"));

    expect(timeShown().textContent).toBe("0:00");
  });

  it("never counts below zero when the two clocks disagree", async () => {
    await open("P0_0", { frames: [RENDERING],
                         status: making({ startedAt: "2026-10-01T10:00:05+00:00" }) });
    fireEvent.click(tab("Video"));

    expect(timeShown().textContent).toBe("0:00");
  });

  it("keeps the recorded time once the layer lands", async () => {
    await open("P0_0", { frames: [RENDERING], status: making({ startedAt: AGO_46 }) });
    fireEvent.click(tab("Video"));
    listFrames.mockResolvedValue([{ ...LAYERED, renderSeconds: { photo: 46.3, video: 47.2 } }]);
    getStatus.mockResolvedValue({ status: "done", project: "düğün" });

    await settle(2000);

    expect(timeShown().textContent).toBe("0:47");
    expect(timeShown().style.color).not.toBe("var(--accent)");
  });
});

describe("PhotoDetail — a frame its batch is making (madde 411)", () => {
  const AGO_46 = "2026-10-01T09:59:14+00:00";
  const timeShown = () => document.querySelector("[data-time]");

  beforeEach(() => { vi.setSystemTime(new Date("2026-10-01T10:00:00Z")); });

  it("counts the batch's time live on every frame it is making", async () => {
    await open("P0_1", {
      frames: [waiting("P0_1.png", "kırmızı elbise"), waiting("P0_0.png", "kırmızı elbise")],
      status: { status: "running", project: "düğün", current: { id: "P0_0", type: "photo" },
                batch: ["P0_1"], startedAt: AGO_46 },
    });

    expect(timeShown().textContent).toBe("0:46");
    expect(timeShown().style.color).toBe("var(--accent)");
  });
});

describe("PhotoDetail — the length a new video gets (madde 424)", () => {
  // The video row the way the server gives it: whether the session's model is H3 is its to say.
  const H3_ROWS = [{ id: "video", name: "Video üreticisi", installed: true, model: "MiniMax H3",
                     reads_references: true }];
  const WAN_ROWS = [{ ...H3_ROWS[0], model: "WAN 2.2 I2V", reads_references: false }];
  const LOOPED = { ...LAYERED, modes: { video: "loop" } };
  const RED_VIDEO = { ...LAYERED, layers: { photo: "P0_0.png" }, failed: ["video"],
                      errors: { video: "ComfyUI 500 — 3 kez denendi" },
                      prompts: { photo: "kırmızı elbise" } };
  const NOTE = "Yeni bir kare açılır — P0_0 kopyası, loop video.";

  // The session's model and then the project's length are two answers in a row, so the page is
  // given two turns to take them.
  async function openIn({ rows, frames, project = "düğün", video = true }) {
    listProducers.mockResolvedValue(rows);
    listFrames.mockResolvedValue(frames);
    getStatus.mockResolvedValue(IDLE);
    listModels.mockResolvedValue({ models: [], loras: LORAS });
    render(<PhotoDetail project={project} frame="P0_0" />);
    await settle();
    await settle();
    if (video) fireEvent.click(tab("Video"));
  }

  it("ends the note under Yeniden üret with the project's length in an H3 session", async () => {
    // The project's length, not the frame's: a new video is made at what the project says now.
    getVideoLength.mockResolvedValue(12);
    await openIn({ rows: H3_ROWS, frames: [LOOPED] });

    expect(screen.getByText(`${NOTE} 12 sn.`)).toBeTruthy();
  });

  it("leaves that note as it was in a WAN session", async () => {
    await openIn({ rows: WAN_ROWS, frames: [LOOPED] });

    expect(screen.getByText(NOTE)).toBeTruthy();
  });

  it("puts a note under a red video's Tekrar dene in an H3 session", async () => {
    await openIn({ rows: H3_ROWS, frames: [RED_VIDEO] });

    const note = screen.getByText("Aynı kare yeniden denenir. 8 sn.");
    expect(screen.getByText("Tekrar dene — bu kareye").compareDocumentPosition(note)
           & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
  });

  it("gives Tekrar dene no note in a WAN session", async () => {
    await openIn({ rows: WAN_ROWS, frames: [RED_VIDEO] });

    expect(screen.getByText("Tekrar dene — bu kareye")).toBeTruthy();
    expect(screen.queryByText(/Aynı kare yeniden denenir/)).toBeNull();
  });

  it("gives the photo tab's Tekrar dene no note", async () => {
    await openIn({ rows: H3_ROWS, frames: [BROKEN], video: false });

    expect(screen.getByText("Tekrar dene — bu kareye")).toBeTruthy();
    expect(screen.queryByText(/Aynı kare yeniden denenir/)).toBeNull();
  });

  it("promises no length under Yeniden üret while the length cannot be read", async () => {
    getVideoLength.mockRejectedValue(new Error("Sunucuya ulaşılamadı — bağlantıyı kontrol et."));
    await openIn({ rows: H3_ROWS, frames: [LOOPED], project: "kına-424a" });

    expect(screen.getByText(NOTE)).toBeTruthy();
  });

  it("gives Tekrar dene no note while the length cannot be read", async () => {
    getVideoLength.mockRejectedValue(new Error("Sunucuya ulaşılamadı — bağlantıyı kontrol et."));
    await openIn({ rows: H3_ROWS, frames: [RED_VIDEO], project: "kına-424b" });

    expect(screen.queryByText(/Aynı kare yeniden denenir/)).toBeNull();
  });
});
