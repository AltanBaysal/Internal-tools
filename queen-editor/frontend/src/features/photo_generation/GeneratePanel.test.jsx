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

describe("GeneratePanel — duraklatılmış üretim", () => {
  const PAUSED = { status: "paused", project: "düğün", done: 7, failed: 0, total: 48 };

  it("devam et, durum kartı ve iptal et sunar", () => {
    renderPanel({ job: PAUSED });

    expect(screen.getByText("Devam et")).toBeTruthy();
    expect(screen.getByText("Üretim duraklatıldı — 7/48 tamamlandı")).toBeTruthy();
    expect(screen.getByText("İptal et")).toBeTruthy();
    expect(screen.queryByText("Üret")).toBeNull();
  });

  it("düğmeler kendi işlerini çağırır", () => {
    const onResume = vi.fn();
    const onCancel = vi.fn();
    renderPanel({ job: PAUSED, onResume, onCancel });

    fireEvent.click(screen.getByText("Devam et"));
    fireEvent.click(screen.getByText("İptal et"));

    expect(onResume).toHaveBeenCalled();
    expect(onCancel).toHaveBeenCalled();
  });
});

describe("GeneratePanel — alan hatası", () => {
  const IDLE = { status: "idle" };

  it("sunucunun işaret ettiği kutuyu kızartır ve metnini altına yazar", () => {
    renderPanel({ job: IDLE, error: "Prompt listesi boş.", errorField: "prompts" });

    expect(screen.getByText("Prompt listesi boş.")).toBeTruthy();
    expect(screen.getByPlaceholderText('["ilk prompt", "ikinci prompt"]').style.borderColor)
      .toBe("var(--danger)");
  });

  it("yazmaya başlayınca hatayı temizler", () => {
    const onClearError = vi.fn();
    renderPanel({ job: IDLE, error: "Prompt listesi boş.", errorField: "prompts", onClearError });

    fireEvent.change(screen.getByPlaceholderText('["ilk prompt", "ikinci prompt"]'),
                     { target: { value: '["a"]' } });

    expect(onClearError).toHaveBeenCalled();
  });
});

describe("GeneratePanel — üretim sürerken bağlantı", () => {
  it("bağlantı koptuğunda son bilinen ilerlemeyi söyler ve çubuğu soluklaştırır", () => {
    renderPanel({ error: DEAD });

    expect(screen.getByText("Sunucuya ulaşılamıyor — son bilinen: 7/48")).toBeTruthy();
    expect(isDimmed(screen.getByText("7 / 48"))).toBe(true);
  });

  it("bağlantı sağlamken ne uyarı yazar ne çubuğu soluklaştırır", () => {
    renderPanel();

    expect(screen.queryByText(/son bilinen/)).toBeNull();
    expect(isDimmed(screen.getByText("7 / 48"))).toBe(false);
  });
});
