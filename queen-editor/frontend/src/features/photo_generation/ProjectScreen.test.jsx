import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { navigate } from "../../shared/router.js";
import ProjectScreen from "./ProjectScreen.jsx";

vi.mock("../../shared/router.js", () => ({
  navigate: vi.fn(),
  photoPath: (project, file) => `/projects/${encodeURIComponent(project)}/photos/${file}`,
}));

vi.mock("../../shared/api.js", () => ({
  cancelGeneration: vi.fn(),
  deletePhotos: vi.fn(),
  exportUrl: (project) => `/api/projects/${encodeURIComponent(project)}/export`,
  generateBatch: vi.fn(),
  getQueue: vi.fn().mockResolvedValue({ pending: [], total: 0 }),
  getStatus: vi.fn().mockResolvedValue({ status: "idle" }),
  listPhotos: vi.fn().mockResolvedValue([]),
  photoUrl: (project, file) => `/photos/${project}/${file}`,
  resumeBatch: vi.fn(),
  retryFrame: vi.fn(),
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

  it("Projeden çık önce sorar, Vazgeç ekranda tutar", () => {
    renderScreen();

    fireEvent.click(screen.getByText("Projeden çık"));
    expect(screen.getByText("Projeden çıkılsın mı?")).toBeTruthy();
    expect(navigate).not.toHaveBeenCalled();

    fireEvent.click(screen.getByText("Vazgeç"));
    expect(screen.queryByText("Projeden çıkılsın mı?")).toBeNull();
    expect(navigate).not.toHaveBeenCalled();
  });

  it("Çık'a basınca projelerden çıkar", () => {
    renderScreen();

    fireEvent.click(screen.getByText("Projeden çık"));
    fireEvent.click(screen.getByText("Çık"));

    expect(navigate).toHaveBeenCalledWith("/");
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
