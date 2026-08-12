import { act, fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { getExportSummary } from "../../shared/api.js";
import { navigate } from "../../shared/router.js";
import ExportScreen from "./ExportScreen.jsx";

vi.mock("../../shared/api.js", () => ({ getExportSummary: vi.fn() }));
vi.mock("../../shared/router.js", () => ({
  navigate: vi.fn(),
  projectPath: (project) => `/projects/${project}`,
}));

const SUMMARY = { videos: 22, seconds: 110, folder: "/drive/düğün/export" };
const EMPTY = { videos: 0, seconds: 0, folder: "/drive/düğün/export" };

const button = (label) => screen.getByText(label).closest("button");

async function open(summary = SUMMARY) {
  getExportSummary.mockResolvedValue(summary);
  render(<ExportScreen project="düğün" />);
  await act(async () => {});
}

beforeEach(() => {
  vi.clearAllMocks();
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

  it("says so when the summary cannot be read", async () => {
    getExportSummary.mockRejectedValue(new Error("Proje yok: düğün"));
    render(<ExportScreen project="düğün" />);
    await act(async () => {});

    expect(screen.getByText("Export özeti yüklenemedi")).toBeTruthy();
    expect(screen.getByText(/Proje yok/)).toBeTruthy();
  });
});
