import { act, fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import {
  cancelExport,
  getExportState,
  getExportSummary,
  startExport,
} from "../../shared/api.js";
import { navigate } from "../../shared/router.js";
import { VERSION } from "../../shared/version.js";
import ExportScreen from "./ExportScreen.jsx";
import { useGeneration } from "./useGeneration.js";

vi.mock("../../shared/api.js", () => ({
  cancelExport: vi.fn(),
  getExportState: vi.fn(),
  getExportSummary: vi.fn(),
  startExport: vi.fn(),
}));
vi.mock("../../shared/router.js", () => ({
  navigate: vi.fn(),
  projectPath: (project) => `/projects/${project}`,
}));
// The queue's state comes from the hook the whole app reads it with; the screen adds no second
// count of its own.
vi.mock("./useGeneration.js", () => ({ useGeneration: vi.fn() }));

const SUMMARY = { videos: 22, seconds: 110, silent: 0, withoutVideo: 0,
                  folder: "/drive/düğün/export" };
const EMPTY = { videos: 0, seconds: 0, silent: 0, withoutVideo: 0,
                folder: "/drive/düğün/export" };

const IDLE = { job: { status: "idle" }, frames: [], queue: [] };
const FLOWING = { job: { status: "running", project: "düğün" }, frames: [],
                  queue: [{ layer: "video", owed: 5 }] };
const PAUSED = { job: { status: "paused", project: "düğün" }, frames: [],
                 queue: [{ layer: "video", owed: 5 }] };

const button = (label) => screen.getByText(label).closest("button");

const NOTHING = { merged: { state: "idle" }, separate: { state: "idle" } };

async function open(summary = SUMMARY, generation = IDLE, exportState = NOTHING) {
  getExportSummary.mockResolvedValue(summary);
  getExportState.mockResolvedValue(exportState);
  startExport.mockResolvedValue({ job: "running" });
  cancelExport.mockResolvedValue({ job: "cancelling" });
  useGeneration.mockReturnValue(generation);
  render(<ExportScreen project="düğün" />);
  await act(async () => {});
}

// Press an export button and let the answer it triggers land.
async function press(label) {
  await act(async () => { fireEvent.click(button(label)); });
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe("ExportScreen header", () => {
  it("puts the version next to the name", async () => {
    // The module's value, not a pattern: the number is shared/version.js's to say (madde 248), and
    // nothing held the screen to saying what that module says -- a screen with "V5" typed into it
    // would have passed a pattern test just as well (madde 285). The value itself is still not
    // pinned here: it is a decision, and pinning it would put one decision in two places.
    await open();

    expect(screen.getByText(`Queen Editor ${VERSION}`)).toBeTruthy();
  });
});

describe("ExportScreen", () => {
  it("says how many videos there are and how long they run", async () => {
    await open();

    expect(screen.getByText("22 video export edilecek · 1:50 dk")).toBeTruthy();
  });

  it("names the folder the export would be written to", async () => {
    await open();

    expect(screen.getByText("Şuraya yazılacak:")).toBeTruthy();
    expect(screen.getByText("/drive/düğün/export")).toBeTruthy();
  });

  it("offers the two exports side by side, both accent", async () => {
    await open();

    expect(button("Birleşik videoyu export et").className).toContain("wf-btn--hl");
    expect(button("Videoları ayrı export et").className).toContain("wf-btn--hl");
    expect(button("Birleşik videoyu export et").disabled).toBe(false);
  });

  it("turns into guidance when the project has no video", async () => {
    await open(EMPTY);

    expect(screen.getByText("Export edilecek video yok")).toBeTruthy();
    expect(screen.getByText(/önce Video üret panelinden/)).toBeTruthy();
    expect(button("Birleşik videoyu export et").disabled).toBe(true);
    expect(button("Videoları ayrı export et").disabled).toBe(true);
  });

  it("carries the project's name and its own app bar", async () => {
    await open();

    expect(screen.getByText("düğün · Export")).toBeTruthy();
  });

  it("goes back to the gallery", async () => {
    await open();

    fireEvent.click(screen.getByText("Galeriye dön"));

    expect(navigate).toHaveBeenCalledWith("/projects/düğün");
  });

  it("says how many videos have no sound", async () => {
    await open({ ...SUMMARY, silent: 16 });

    expect(screen.getByText("⚠ 16 videonun sesi yok")).toBeTruthy();
  });

  it("says which frames the sequence will not hold", async () => {
    await open({ ...SUMMARY, withoutVideo: 3 });

    expect(screen.getByText("⚠ 3 videosuz kare diziye girmeyecek")).toBeTruthy();
  });

  it("draws no row for a condition that is not there", async () => {
    await open();

    expect(screen.queryByText(/sesi yok/)).toBeNull();
    expect(screen.queryByText(/diziye girmeyecek/)).toBeNull();
  });

  it("blocks the export while the queue flows, and says why", async () => {
    await open(SUMMARY, FLOWING);

    expect(screen.getByText(/Üretim sürüyor — 5 video kuyrukta/)).toBeTruthy();
    expect(button("Birleşik videoyu export et").disabled).toBe(true);
    expect(button("Videoları ayrı export et").disabled).toBe(true);
  });

  it("lets the export run once the queue is paused", async () => {
    await open(SUMMARY, PAUSED);

    expect(button("Birleşik videoyu export et").disabled).toBe(false);
    expect(screen.queryByText(/Üretim sürüyor/)).toBeNull();
    // What was a blocking card is now one more line in the summary.
    expect(screen.getByText("⚠ 5 karenin videosu kuyrukta bekliyor — diziye girmeyecek"))
      .toBeTruthy();
  });

  it("starts the export the button names", async () => {
    await open();

    await press("Videoları ayrı export et");

    expect(startExport).toHaveBeenCalledWith("düğün", "separate");
  });

  it("reads the progress in the button's own place", async () => {
    await open(SUMMARY, IDLE,
               { ...NOTHING, separate: { state: "running", written: 7, total: 22 } });

    expect(screen.getByText("7 / 22 yazıldı…")).toBeTruthy();
    // The other one stays pressable: the two exports can run side by side (madde 93).
    expect(button("Birleşik videoyu export et").disabled).toBe(false);
  });

  it("asks what the exports are doing as soon as it opens", async () => {
    // Nothing is pressed here. The screen used to learn about a run only from the press that
    // started it, so a refresh mid-export left it blind (madde 290).
    await open();

    expect(getExportState).toHaveBeenCalledWith("düğün");
  });

  it("picks up a run that was already going when the page opened", async () => {
    // What the user hit: the disclaimer step was on screen, they refreshed, and the run vanished
    // from the screen while it carried on in the background (21 Eylül).
    await open(SUMMARY, IDLE,
               { ...NOTHING,
                 merged: { state: "merging", written: 22, total: 22,
                           steps: [{ step: "running", seconds: 21.9 },
                                   { step: "photos", seconds: 0.5 }] } });

    expect(screen.getByText("Disclaimer ekleniyor…")).toBeTruthy();
    expect(button("Disclaimer ekleniyor…").disabled).toBe(true);
    // And what it has cost so far is back too.
    expect(screen.getByText("Videolar")).toBeTruthy();
    expect(screen.getByText("21,9 sn")).toBeTruthy();
  });

  it("says nothing about an export that had already finished", async () => {
    // The user's call: zaten önceden bittiyse gösterme, gerek yok ona -- devam ediyorsa göster
    // çünkü butonu kullanamıyoruz (21 Eylül). The state lives for the whole session, so adopting a
    // finished one would hang an hour-old green card on every open.
    await open(SUMMARY, IDLE, { ...NOTHING,
                                separate: { state: "done", written: 3, total: 3,
                                            target: "/drive/düğün/export/2026-08-12 14-32" } });

    expect(screen.queryByText("✓ Export tamamlandı")).toBeNull();
    expect(button("Videoları ayrı export et").disabled).toBe(false);
  });

  it("says nothing about an export that had already failed", async () => {
    await open(SUMMARY, IDLE,
               { ...NOTHING, separate: { state: "error", error: "ffmpeg: disk dolu" } });

    expect(screen.queryByText("Export başarısız")).toBeNull();
    expect(button("Videoları ayrı export et").disabled).toBe(false);
  });

  it("names the disclaimer step while the merged one finishes", async () => {
    // The user waited past five minutes on "birleştiriliyor…" with nothing on screen saying which
    // work was under way -- and the work that eats the time is the disclaimer, not the join: the
    // overlay is a new picture, so the whole timeline is encoded, on a 1920x1080 canvas since
    // madde 259. So the step is named after it, in the user's own words (madde 255).
    await open(SUMMARY, IDLE, { ...NOTHING, merged: { state: "merging", written: 22, total: 22 } });

    expect(screen.getByText("Disclaimer ekleniyor…")).toBeTruthy();
    // One line in the button, not two: the question was which step, and the counter belongs to the
    // step that writes the pieces.
    expect(screen.queryByText("birleştiriliyor…")).toBeNull();
    expect(screen.queryByText("22 / 22 yazıldı…")).toBeNull();
    // The label's name changed, the step did not: it is still a run in progress. Asked through the
    // sentence rather than the mode's name, because that name is exactly what the running button
    // no longer says -- its own place carries the progress instead (madde 93).
    expect(button("Disclaimer ekleniyor…").disabled).toBe(true);
    expect(button("Videoları ayrı export et").disabled).toBe(false);
  });

  it("names the photos step while the pictures go to Drive", async () => {
    // 289 took the pictures out of the cutting loop, and until this item the screen sat on
    // "N / N yazıldı…" for the whole of that pass -- the counter had finished counting and the
    // work had not.
    await open(SUMMARY, IDLE, { ...NOTHING, merged: { state: "photos", written: 22, total: 22 } });

    expect(screen.getByText("Fotoğraflar ekleniyor…")).toBeTruthy();
    expect(button("Fotoğraflar ekleniyor…").disabled).toBe(true);
    expect(screen.queryByText("22 / 22 yazıldı…")).toBeNull();
  });

  it("names the copy to Drive, which used to run under the disclaimer's name", async () => {
    // 282 moved the join onto the machine's own disk and copied the file over once it was whole.
    // The step the user wonders about most was showing under the wrong name the whole time it ran.
    await open(SUMMARY, IDLE, { ...NOTHING, merged: { state: "saving", written: 22, total: 22 } });

    expect(screen.getByText("Drive'a kopyalanıyor…")).toBeTruthy();
    expect(screen.queryByText("Disclaimer ekleniyor…")).toBeNull();
    expect(button("Drive'a kopyalanıyor…").disabled).toBe(true);
  });

  it("leaves every finished step on screen with its own seconds", async () => {
    // The user's words: neye zaman harcadığımızı görürüz. A name says where the run is; the second
    // says which step is expensive, and that is the question being asked.
    await open(SUMMARY, IDLE, { ...NOTHING,
                                merged: { state: "saving", written: 22, total: 22,
                                          steps: [{ step: "running", seconds: 41.2 },
                                                  { step: "photos", seconds: 8 },
                                                  { step: "merging", seconds: 312.75 }] } });

    // Turkish names and a Turkish decimal comma: the person reading this reads Turkish.
    expect(screen.getByText("Videolar")).toBeTruthy();
    expect(screen.getByText("41,2 sn")).toBeTruthy();
    expect(screen.getByText("Fotoğraflar")).toBeTruthy();
    expect(screen.getByText("8,0 sn")).toBeTruthy();
    expect(screen.getByText("Disclaimer")).toBeTruthy();
    expect(screen.getByText("312,8 sn")).toBeTruthy();
  });

  it("never names the disclaimer while the separate one runs", async () => {
    // Nothing is stamped there: every piece is copied as it is (madde 261), so the sentence would
    // be a lie. Its step counts pieces, which is what it does.
    await open(SUMMARY, IDLE,
               { ...NOTHING, separate: { state: "running", written: 7, total: 22 } });

    expect(screen.queryByText(/Disclaimer/)).toBeNull();
    expect(screen.getByText("7 / 22 yazıldı…")).toBeTruthy();
  });

  it("says where the finished export went", async () => {
    await open(SUMMARY, IDLE, { ...NOTHING,
                                separate: { state: "done", written: 3, total: 3,
                                            target: "/drive/düğün/export/2026-08-12 14-32" } });

    await press("Videoları ayrı export et");

    expect(screen.getByText("✓ Export tamamlandı")).toBeTruthy();
    expect(screen.getByText(/2026-08-12 14-32/)).toBeTruthy();
  });

  it("says why an export failed, in the tool's own words", async () => {
    await open(SUMMARY, IDLE, { ...NOTHING,
                                separate: { state: "error", error: "ffmpeg: disk dolu" } });

    await press("Videoları ayrı export et");

    expect(screen.getByText("Export başarısız")).toBeTruthy();
    expect(screen.getByText("ffmpeg: disk dolu")).toBeTruthy();
    // No retry of its own: the buttons are still there and a new press opens a new folder.
    expect(screen.queryByText("Tekrar dene")).toBeNull();
    expect(button("Videoları ayrı export et").disabled).toBe(false);
  });

  it("asks before leaving while an export is running, and cancels it", async () => {
    await open(SUMMARY, IDLE,
               { ...NOTHING, separate: { state: "running", written: 1, total: 3 } });
    await press("Videoları ayrı export et");

    fireEvent.click(screen.getByText("Galeriye dön"));
    expect(screen.getByText("Export sürüyor — çıkılsın mı?")).toBeTruthy();
    expect(screen.getByText("Export sürüyor — çıkılsın mı?").closest(".wf-card").style.width)
      .toBe("380px");
    expect(navigate).not.toHaveBeenCalled();

    await act(async () => { fireEvent.click(screen.getByText("Çık")); });

    expect(cancelExport).toHaveBeenCalledWith("düğün");
    expect(navigate).toHaveBeenCalledWith("/projects/düğün");
  });

  it("leaves without asking when nothing is running", async () => {
    await open();

    fireEvent.click(screen.getByText("Galeriye dön"));

    expect(navigate).toHaveBeenCalledWith("/projects/düğün");
    expect(cancelExport).not.toHaveBeenCalled();
  });

  it("says so when the summary cannot be read", async () => {
    getExportSummary.mockRejectedValue(new Error("Proje yok: düğün"));
    render(<ExportScreen project="düğün" />);
    await act(async () => {});

    expect(screen.getByText("Export özeti yüklenemedi")).toBeTruthy();
    expect(screen.getByText(/Proje yok/)).toBeTruthy();
  });
});
