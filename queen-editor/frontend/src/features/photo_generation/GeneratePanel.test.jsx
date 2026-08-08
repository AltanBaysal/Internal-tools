import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import GeneratePanel from "./GeneratePanel.jsx";

const SETTINGS = { prompts: '["ilk prompt"]', negative: "", variants: 4 };
const RUNNING = { status: "running", project: "düğün", done: 7, failed: 0, total: 48 };
const DEAD = "Sunucuya ulaşılamadı — bağlantıyı kontrol et.\nZaman aşımı (10 sn)";

function renderPanel(props) {
  return render(
    <GeneratePanel
      job={RUNNING}
      error={null}
      busyElsewhere={false}
      settings={SETTINGS}
      project="düğün"
      stopping={false}
      onGenerate={() => Promise.resolve()}
      onStop={() => {}}
      queue={{ pending: [], total: 0 }}
      onResume={() => {}}
      onCancel={() => {}}
      onClearError={() => {}}
      {...props}
    />,
  );
}

// The progress bar is dimmed by a wrapper, so "is it dimmed" is answered by walking up from the
// counter rather than by reaching for a class name that does not exist.
function isDimmed(element) {
  for (let node = element; node; node = node.parentElement) {
    if (node.style && node.style.opacity === "0.45") return true;
  }
  return false;
}

describe("GeneratePanel — an unfinished run", () => {
  it("shows the reason after a fatal stop", () => {
    renderPanel({
      job: { status: "error", project: "düğün", done: 7, total: 48,
             error: "Üst üste 3 hata\nComfyUI 500" },
    });

    expect(screen.getByText("Kaldığı yerden devam et")).toBeTruthy();
    expect(screen.getByText("Üretim durdu — 7/48 tamamlandı")).toBeTruthy();
    expect(screen.getByText(/ComfyUI 500/)).toBeTruthy();
  });

  it("invents no reason after a dead session, it only says how many frames are left", () => {
    renderPanel({
      job: { status: "idle" },
      queue: { pending: ["7_a.png", "7_b.png"], total: 10 },
    });

    expect(screen.getByText("Üretim yarım kaldı — 8/10 tamamlandı")).toBeTruthy();
    expect(screen.getByText("Kaldığı yerden devam et")).toBeTruthy();
  });

  it("shows the ordinary generate button when nothing is half done", () => {
    renderPanel({ job: { status: "idle" } });

    expect(screen.getByText("Üret")).toBeTruthy();
    expect(screen.queryByText("Kaldığı yerden devam et")).toBeNull();
  });
});

describe("GeneratePanel — a paused run", () => {
  const PAUSED = { status: "paused", project: "düğün", done: 7, failed: 0, total: 48 };

  it("offers resume, a status card and cancel", () => {
    renderPanel({ job: PAUSED });

    expect(screen.getByText("Devam et")).toBeTruthy();
    expect(screen.getByText("Üretim duraklatıldı — 7/48 tamamlandı")).toBeTruthy();
    expect(screen.getByText("İptal et")).toBeTruthy();
    expect(screen.queryByText("Üret")).toBeNull();
  });

  it("wires each button to its own action", () => {
    const onResume = vi.fn();
    const onCancel = vi.fn();
    renderPanel({ job: PAUSED, onResume, onCancel });

    fireEvent.click(screen.getByText("Devam et"));
    fireEvent.click(screen.getByText("İptal et"));

    expect(onResume).toHaveBeenCalled();
    expect(onCancel).toHaveBeenCalled();
  });
});

describe("GeneratePanel — a field error", () => {
  const IDLE = { status: "idle" };

  it("reddens the field the server named and writes its text underneath", () => {
    renderPanel({ job: IDLE, error: "Prompt listesi boş.", errorField: "prompts" });

    expect(screen.getByText("Prompt listesi boş.")).toBeTruthy();
    expect(screen.getByPlaceholderText('["ilk prompt", "ikinci prompt"]').style.borderColor)
      .toBe("var(--danger)");
  });

  it("clears the error once typing starts", () => {
    const onClearError = vi.fn();
    renderPanel({ job: IDLE, error: "Prompt listesi boş.", errorField: "prompts", onClearError });

    fireEvent.change(screen.getByPlaceholderText('["ilk prompt", "ikinci prompt"]'),
                     { target: { value: '["a"]' } });

    expect(onClearError).toHaveBeenCalled();
  });
});

describe("GeneratePanel — the connection during a run", () => {
  it("reports the last known progress and dims the bar when the connection drops", () => {
    renderPanel({ error: DEAD });

    expect(screen.getByText("Sunucuya ulaşılamıyor — son bilinen: 7/48")).toBeTruthy();
    expect(isDimmed(screen.getByText("7 / 48"))).toBe(true);
  });

  it("neither warns nor dims while the connection holds", () => {
    renderPanel();

    expect(screen.queryByText(/son bilinen/)).toBeNull();
    expect(isDimmed(screen.getByText("7 / 48"))).toBe(false);
  });
});
