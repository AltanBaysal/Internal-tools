import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import ProjectScreen from "./ProjectScreen.jsx";

vi.mock("../../shared/api.js", () => ({
  exportUrl: (project) => `/api/projects/${encodeURIComponent(project)}/export`,
  generateBatch: vi.fn(),
  getStatus: vi.fn().mockResolvedValue({ status: "idle" }),
  listPhotos: vi.fn().mockResolvedValue([]),
  photoUrl: (project, file) => `/photos/${project}/${file}`,
  saveOrder: vi.fn(),
  stopGeneration: vi.fn(),
}));

const SETTINGS = { prompts: "", negative: "", variants: 4 };

function renderScreen() {
  return render(
    <ProjectScreen project="düğün" settings={SETTINGS} onSaveSettings={() => Promise.resolve()} />,
  );
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe("ProjectScreen app bar", () => {
  it("Export'u indirme bağlantısı olarak sunar", () => {
    renderScreen();

    const link = screen.getByText("Export").closest("a");
    expect(link.getAttribute("href")).toBe(
      `/api/projects/${encodeURIComponent("düğün")}/export`);
    expect(link.hasAttribute("download")).toBe(true);
  });

  it("Export'u Projeden çık'ın soluna koyar", () => {
    renderScreen();

    const exportEl = screen.getByText("Export");
    const exitEl = screen.getByText("Projeden çık");
    // compareDocumentPosition's FOLLOWING bit: the exit button comes later in document order.
    expect(exportEl.compareDocumentPosition(exitEl) & Node.DOCUMENT_POSITION_FOLLOWING)
      .toBeTruthy();
  });
});
