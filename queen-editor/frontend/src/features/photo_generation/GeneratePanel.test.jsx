import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

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
