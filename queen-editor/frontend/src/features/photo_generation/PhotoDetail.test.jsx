import { act, fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import {
  getStatus,
  listFrames,
  regenerateFrame,
  removeFrames,
  removeLayer,
  retryFrame,
} from "../../shared/api.js";
import { navigate } from "../../shared/router.js";
import PhotoDetail from "./PhotoDetail.jsx";

vi.mock("../../shared/api.js", () => ({
  cancelGeneration: vi.fn(),
  generateBatch: vi.fn(),
  getStatus: vi.fn(),
  listFrames: vi.fn(),
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
const RUNNING = { status: "running", project: "düğün", current: { id: "2_a" } };

// Advancing the fake clock inside act() flushes both the timers and the promises they unblock --
// the detail page is live now, so a poll tick is what moves it forward.
async function settle(ms = 0) {
  await act(async () => { await vi.advanceTimersByTimeAsync(ms); });
}

// The page is opened by the frame's identity: that is what the address carries.
async function open(fid, { frames = PHOTOS, status = IDLE } = {}) {
  listFrames.mockResolvedValue(frames);
  getStatus.mockResolvedValue(status);
  render(<PhotoDetail project="düğün" frame={fid} />);
  await settle();
}

// The panel's own Sil comes first in the document; the modal's is the one added on top.
function confirmButton() {
  return screen.getAllByText("Sil").at(-1);
}

const LAYERED = {
  id: "P0_0", file: "P0_0.png", status: "done", prompt: "kırmızı elbise", negative: "bulanık",
  layers: { photo: "P0_0.png", video: "P0_0_V1_0.mp4", audio: "P0_0_V1_0_S1_0.wav" },
  failed: [], owed: [],
  prompts: { photo: "kırmızı elbise", video: "kadın dönüyor", audio: "kumaş hışırtısı" },
};

// The frame the arrows move on to: its own words, so a box that kept the first frame's text shows.
const SECOND = { id: "P1_0", file: "P1_0.png", status: "done", prompt: "mavi elbise", negative: "",
                 layers: { photo: "P1_0.png" }, failed: [], owed: [],
                 prompts: { photo: "mavi elbise" } };

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
});

// The frame the worker is holding a layer of: its photo is on disk, its video is not yet.
const RENDERING = { ...LAYERED, layers: { photo: "P0_0.png" }, owed: ["video"],
                    prompts: { photo: "kırmızı elbise" } };

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
    // the identity would be nowhere on screen (karar 23).
    await open("P0_0", { frames: [LAYERED] });
    expect(screen.getByText("Dosya adı")).toBeTruthy();

    fireEvent.click(tab("Video"));
    expect(screen.getByText("Dosya adı")).toBeTruthy();
    expect(screen.getByText("P0_0.png")).toBeTruthy();
    expect(screen.getByText("1 / 1")).toBeTruthy();

    fireEvent.click(tab("Ses"));
    expect(screen.getByText("Dosya adı")).toBeTruthy();
  });

  it("keeps nothing else in the top group", async () => {
    // Read as a list rather than one row at a time: naming the rows that went says nothing about
    // the rows that stayed, and what this item promises is the whole group.
    await open("P0_0", { frames: [LAYERED] });

    fireEvent.click(tab("Video"));

    expect([...document.querySelectorAll("[data-field]")].map((one) => one.textContent))
      .toEqual(["Sıra", "Dosya adı"]);
  });

  it("centres the one line a waiting box holds", async () => {
    // The box is never left blank -- an empty one reads as a prompt someone deleted (karar 24).
    await open("P0_1", { frames: [QUEUED_COPY] });

    fireEvent.click(tab("Video"));

    expect(screen.getByText("Prompt yok — üretim sırası geldiğinde eklenecek.").style.textAlign)
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
});

describe("PhotoDetail — how the video was made", () => {
  const LOOPED = { ...LAYERED, modes: { video: "loop" } };
  const LINKED = { ...LAYERED, modes: { video: "linked" }, endsOn: { video: "P1_0.png" } };

  it("says which mode made this video", async () => {
    await open("P0_0", { frames: [LOOPED] });

    fireEvent.click(tab("Video"));

    // Read off the row itself: Loop is also one of the options in the Yeni mod box below, and a
    // bare text match would be happy with either.
    expect(screen.getByText("Üretim modu").parentElement.textContent).toContain("Loop");
  });

  it("names the picture a linked video ended on", async () => {
    // The file rather than the frame's number: the sequence can be dragged, and then the number
    // would be a lie about a video nobody touched.
    await open("P0_0", { frames: [LINKED] });

    fireEvent.click(tab("Video"));

    expect(screen.getByText("Sonrakine bağla → P1_0.png")).toBeTruthy();
  });

  it("says it and nothing more -- there is nothing here to press", async () => {
    // Changing the mode is making the video again, and that is the form below.
    await open("P0_0", { frames: [LOOPED] });

    fireEvent.click(tab("Video"));

    expect(screen.getByText("Üretim modu").parentElement.querySelector("button")).toBeNull();
    expect(screen.getByText("Üretim modu").parentElement.querySelector("select")).toBeNull();
  });

  it("never draws the row on the sound tab", async () => {
    // The sound tab shows the video's file name, because the sound was laid over it -- but the
    // video's mode is not a fact about the sound.
    await open("P0_0", { frames: [LOOPED] });

    fireEvent.click(tab("Ses"));

    expect(screen.queryByText("Üretim modu")).toBeNull();
  });

  it("never draws it on the photo tab either", async () => {
    await open("P0_0", { frames: [LOOPED] });

    expect(screen.queryByText("Üretim modu")).toBeNull();
  });

  it("stays quiet about a video whose line never named a mode", async () => {
    // Videos already on Drive were produced before modes existed. An empty row would be a question
    // rather than an answer.
    await open("P0_0", { frames: [LAYERED] });

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

    expect(screen.getByText("Dosya adı (planlanan)")).toBeTruthy();
    expect(screen.queryByText("Dosya adı")).toBeNull();
  });

  it("keeps the plain label on a produced photo", async () => {
    await open("0_a", { frames: MIXED });

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

describe("PhotoDetail — one destructive action per tab", () => {
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

    expect(screen.getByText("Prompt yok — üretim sırası geldiğinde eklenecek.")).toBeTruthy();
    // Nothing to make again and nothing to delete: the layer is not there yet.
    expect(screen.queryByText("Yeniden üret — yeni kare")).toBeNull();
    expect(screen.queryByText("Videoyu sil — kare kalır")).toBeNull();
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

  it("splits the column into two groups with nothing between them", async () => {
    await open("P0_0", { frames: [LAYERED] });

    // Fark 91: what the frame is, then what can be made of it. No group heading and no rule
    // between them -- the split is where the eye rests, not a line it reads.
    const side = document.querySelector("[data-side]");
    expect([...side.children].map((one) => one.getAttribute("data-group")))
      .toEqual(["info", "production"]);
  });

  it("keeps one vertical rhythm down the column", async () => {
    await open("P0_0", { frames: [LAYERED] });

    // Fark 91: three measures became two -- 16 between blocks, 6 between a label and what it
    // labels. The information group wraps on a 300px panel, so its own rows answer to the 16 too.
    const side = document.querySelector("[data-side]");
    expect(side.style.gap).toBe("16px");
    expect(side.children[0].style.rowGap).toBe("16px");
    expect(side.children[1].style.gap).toBe("16px");
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
