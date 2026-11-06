import { act, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { getSettings, listFrames } from "./shared/api.js";
import { navigate } from "./shared/router.js";
import App from "./App.jsx";

// Every export the tree imports has to be here: imports are hoisted, so App pulling in the
// projects, export and detail screens evaluates their api imports whether or not they render.
vi.mock("./shared/api.js", () => ({
  cancelExport: vi.fn(),
  cancelGeneration: vi.fn(),
  checkProjectName: vi.fn(),
  copyFrames: vi.fn(),
  createProject: vi.fn(),
  deleteProject: vi.fn(),
  fileUrl: (project, file) => `/photos/${project}/${file}`,
  referenceUrl: (project, name) => `/references/${project}/${name}`,
  listReferences: vi.fn().mockResolvedValue({
    references: [], limits: { picture: 9, video: 3, audio: 3 },
  }),
  removeReference: vi.fn(),
  uploadReferences: vi.fn(),
  generateBatch: vi.fn(),
  getExportState: vi.fn(),
  getExportSummary: vi.fn(),
  getMuted: vi.fn().mockResolvedValue([]),
  getSettings: vi.fn(),
  getStatus: vi.fn().mockResolvedValue({ status: "idle" }),
  listFrames: vi.fn().mockResolvedValue([]),
  listModels: vi.fn().mockResolvedValue({ models: [], loras: [] }),
  listProducers: vi.fn().mockResolvedValue([]),
  listProjects: vi.fn().mockResolvedValue([]),
  queueLayer: vi.fn(),
  regenerateFrame: vi.fn(),
  removeFrames: vi.fn(),
  removeLayer: vi.fn(),
  dequeueLayer: vi.fn(),
  renameProject: vi.fn(),
  resumeBatch: vi.fn(),
  retryFailed: vi.fn(),
  retryFrame: vi.fn(),
  saveMuted: vi.fn(),
  saveOrder: vi.fn(),
  saveSettings: vi.fn(),
  startExport: vi.fn(),
  stopGeneration: vi.fn(),
  waitForQueue: vi.fn((seen) => new Promise((resolve) => { heldAsks.push({ seen, resolve }); })),
}));

// The queue watch's asks, answered by the test that wants the queue started or ended.
const heldAsks = [];

const FRAME = { id: "1_a", file: "1_a.png", status: "done" };

// The gallery a project last answered with is remembered across mounts, so every test here asks
// for a project name no other test has filled.
function openProject(project) {
  window.history.pushState({}, "", `/projects/${encodeURIComponent(project)}`);
  return render(<App />);
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe("App — the project screen while its record is on its way", () => {
  it("draws the gallery without waiting for the record", async () => {
    // The record never lands: what stays on screen is what the screen can do without it.
    getSettings.mockImplementation(() => new Promise(() => {}));
    listFrames.mockResolvedValue([FRAME]);

    openProject("bekleyen");

    // The tile's caption -- the gallery really drew a frame, not a holder over an empty grid.
    expect(await screen.findByText("1_a.png")).toBeTruthy();
  });

  it("keeps the bar and the rail instead of collapsing to one spinner", async () => {
    getSettings.mockImplementation(() => new Promise(() => {}));
    listFrames.mockResolvedValue([FRAME]);

    openProject("baslikli");
    await screen.findByText("1_a.png");

    // The loading screen borrowed the bar but had no Export and no rail. These three say the
    // project screen itself is up.
    expect(screen.getByText("baslikli")).toBeTruthy();
    expect(screen.getByText("Export")).toBeTruthy();
    expect(screen.getByLabelText("Kuyruğu takip et")).toBeTruthy();
  });

  it("keeps the screen when the record cannot be read", async () => {
    getSettings.mockRejectedValue(new Error("Proje bulunamadı: hatali"));
    listFrames.mockResolvedValue([FRAME]);

    openProject("hatali");
    await screen.findByText("Proje ayarları yüklenemedi");

    // The card used to stand alone in the middle of an otherwise empty page. One panel's answer
    // is not the screen's answer.
    expect(screen.getByText("1_a.png")).toBeTruthy();
    expect(screen.getByText("Export")).toBeTruthy();
  });
});

describe("App — the queue's notification on every screen (madde 509)", () => {
  // The browser's Notification, faked: the titles of those shown.
  let shown;
  class FakeNotification {
    static permission = "granted";
    constructor(title) { shown.push(title); }
  }

  beforeEach(() => {
    heldAsks.length = 0;
    shown = [];
    vi.stubGlobal("Notification", FakeNotification);
    // The photo panel's record is no business of the notification's.
    getSettings.mockImplementation(() => new Promise(() => {}));
  });

  // The first ask, with no counts, answered at once: where they stand when the page opens.
  async function openOn(path) {
    window.history.pushState({}, "", path);
    render(<App />);
    await act(async () => {});
    await act(async () => { heldAsks.at(-1).resolve({ started: 0, ended: 0, last: null }); });
  }

  it("rings over the projects list, and asks nobody whether they are there", async () => {
    await openOn("/");

    await act(async () => {
      heldAsks.at(-1).resolve({ started: 0, ended: 1, last: { status: "done" } });
    });

    expect(shown).toEqual(["Queen Editor"]);
    expect(screen.queryByText("Orada mısın?")).toBeNull();
  });

  it("keeps the one ask it holds while moving between screens", async () => {
    await openOn("/");

    act(() => navigate(`/projects/${encodeURIComponent("sayan")}`));
    await act(async () => {});
    expect(heldAsks.map((one) => one.seen)).toEqual(
      [null, { started: 0, ended: 0, last: null }]);

    await act(async () => {
      heldAsks.at(-1).resolve({ started: 0, ended: 1, last: { status: "done" } });
    });

    expect(shown).toEqual(["Queen Editor"]);
    expect(screen.getByText("sayan")).toBeTruthy();
  });
});

// Madde 518: a page left open while the queue is idle never asked again, so a frame the agent or
// another tab queued stayed out of sight until a reload.
describe("App — work added elsewhere while the page stands idle", () => {
  beforeEach(() => {
    heldAsks.length = 0;
    getSettings.mockImplementation(() => new Promise(() => {}));
  });

  it("shows a frame queued elsewhere on the open project page, without a reload", async () => {
    listFrames.mockResolvedValue([FRAME]);
    openProject("bosta-proje");
    await screen.findByText("1_a.png");
    await act(async () => { heldAsks.at(-1).resolve({ started: 0, ended: 0, last: null }); });

    listFrames.mockResolvedValue([{ id: "2_a", file: "2_a.png", status: "pending",
                                    owed: ["photo"], failed: [] }, FRAME]);
    await act(async () => { heldAsks.at(-1).resolve({ started: 1, ended: 0, last: null }); });

    expect(await screen.findByText("2_a.png")).toBeTruthy();
  });
});
