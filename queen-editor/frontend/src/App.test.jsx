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
  renameProject: vi.fn(),
  resumeBatch: vi.fn(),
  retryFailed: vi.fn(),
  retryFrame: vi.fn(),
  saveMuted: vi.fn(),
  saveOrder: vi.fn(),
  saveSettings: vi.fn(),
  startExport: vi.fn(),
  stopGeneration: vi.fn(),
  waitForEnded: vi.fn((after) => new Promise((resolve) => { heldAsks.push({ after, resolve }); })),
}));

// The queue-ended asks, answered by the test that wants the queue ended.
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

  // The first ask, with no count, answered at once: where the count stands when the page opens.
  async function openOn(path) {
    window.history.pushState({}, "", path);
    render(<App />);
    await act(async () => {});
    await act(async () => { heldAsks.at(-1).resolve({ ended: 0, last: null }); });
  }

  it("rings over the projects list, and asks nobody whether they are there", async () => {
    await openOn("/");

    await act(async () => { heldAsks.at(-1).resolve({ ended: 1, last: { status: "done" } }); });

    expect(shown).toEqual(["Queen Editor"]);
    expect(screen.queryByText("Orada mısın?")).toBeNull();
  });

  it("keeps the one ask it holds while moving between screens", async () => {
    await openOn("/");

    act(() => navigate(`/projects/${encodeURIComponent("sayan")}`));
    await act(async () => {});
    expect(heldAsks.map((one) => one.after)).toEqual([null, 0]);

    await act(async () => { heldAsks.at(-1).resolve({ ended: 1, last: { status: "done" } }); });

    expect(shown).toEqual(["Queen Editor"]);
    expect(screen.getByText("sayan")).toBeTruthy();
  });
});
