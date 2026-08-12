import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import QueuePanel from "./QueuePanel.jsx";

const DEAD = "Sunucuya ulaşılamadı — bağlantıyı kontrol et.\nZaman aşımı (10 sn)";
const RUNNING = { status: "running", project: "düğün", done: 7, failed: 0, total: 48 };

function renderPanel(props) {
  return render(
    <QueuePanel
      job={RUNNING}
      error={null}
      busyElsewhere={false}
      project="düğün"
      stopping={false}
      pending={["8_a.png", "9_a.png"]}
      failures={[]}
      onStop={() => {}}
      onResume={() => {}}
      onCancel={() => {}}
      onShowFailures={() => {}}
      {...props}
    />,
  );
}

const button = (label) => screen.getByRole("button", { name: label });

describe("QueuePanel — a flowing queue", () => {
  it("shows one honest number and the pause button", () => {
    renderPanel();

    expect(screen.getByText("Üretiliyor")).toBeTruthy();
    expect(screen.getByText("2")).toBeTruthy();
    expect(screen.getByText("kare bekliyor")).toBeTruthy();
    expect(screen.getByText("Duraklat")).toBeTruthy();
  });

  it("drops the denominator, the percentage, the bar and the current prompt", () => {
    renderPanel({ job: { ...RUNNING, current: { prompt: "kraliçe tahtta" } } });

    expect(screen.queryByText("7 / 48")).toBeNull();
    expect(screen.queryByText(/%/)).toBeNull();
    expect(screen.queryByText(/şimdi:/)).toBeNull();
  });

  it("has no clear-queue button while the queue flows", () => {
    renderPanel();

    expect(screen.queryByText("Kuyruğu boşalt")).toBeNull();
  });

  it("holds the button and says so in the card while the pause is in flight", () => {
    renderPanel({ stopping: true });

    // Both the card's status line and the held button say it.
    expect(screen.getAllByText("Duraklatılıyor…").length).toBe(2);
    expect(button("Duraklatılıyor…").disabled).toBe(true);
  });

  it("asks the server to pause", () => {
    const onStop = vi.fn();
    renderPanel({ onStop });

    fireEvent.click(screen.getByText("Duraklat"));

    expect(onStop).toHaveBeenCalled();
  });
});

describe("QueuePanel — a paused queue", () => {
  const PAUSED = { status: "paused", project: "düğün", done: 7, failed: 0, total: 48 };

  it("counts the cut frame back in and offers the way out", () => {
    renderPanel({ job: PAUSED, pending: ["7_a.png", "8_a.png", "9_a.png"] });

    expect(screen.getByText("Duraklatıldı")).toBeTruthy();
    expect(screen.getByText("3")).toBeTruthy();
    expect(screen.getByText("Devam et")).toBeTruthy();
    expect(screen.getByText("Kuyruğu boşalt")).toBeTruthy();
  });

  it("asks before emptying the queue and never says it cannot be undone", () => {
    renderPanel({ job: PAUSED, pending: ["7_a.png", "8_a.png"] });

    fireEvent.click(screen.getByText("Kuyruğu boşalt"));

    expect(screen.getByText("Kuyruk boşaltılsın mı?")).toBeTruthy();
    expect(screen.getByText(/Bekleyen 2 kare üretilmeden kuyruktan çıkar/)).toBeTruthy();
    expect(screen.queryByText(/geri alınamaz/)).toBeNull();
  });

  it("empties the queue once the confirm is taken", () => {
    const onCancel = vi.fn();
    renderPanel({ job: PAUSED, onCancel });

    fireEvent.click(screen.getByText("Kuyruğu boşalt"));
    fireEvent.click(screen.getByText("Boşalt"));

    expect(onCancel).toHaveBeenCalled();
  });
});

describe("QueuePanel — a stopped queue", () => {
  it("offers the way back and prints the server's own reason", () => {
    renderPanel({
      job: { status: "error", project: "düğün", done: 7, total: 48,
             error: "Bağlantı hatası — sunucuya ulaşılamadı" },
    });

    expect(screen.getByText("Üretim durdu")).toBeTruthy();
    expect(screen.getByText("Bağlantı hatası — sunucuya ulaşılamadı")).toBeTruthy();
    expect(screen.getByText("Kaldığı yerden devam et")).toBeTruthy();
    expect(screen.getByText("Kuyruğu boşalt")).toBeTruthy();
  });

  it("invents no reason for a run that died with its session", () => {
    renderPanel({ job: { status: "idle" }, pending: ["7_a.png", "8_a.png"] });

    expect(screen.getByText("Üretim durdu")).toBeTruthy();
    expect(screen.getByText("Kaldığı yerden devam et")).toBeTruthy();
    expect(screen.queryByText(/yarım kaldı/)).toBeNull();
  });
});

describe("QueuePanel — a finished queue", () => {
  it("confirms in one sentence", () => {
    renderPanel({ job: { status: "done", project: "düğün", done: 20, failed: 0, total: 20 },
                  pending: [] });

    expect(screen.getByText("Kuyruk tamamlandı")).toBeTruthy();
    expect(screen.getByText("20 kare üretildi")).toBeTruthy();
  });

  it("says the failures inside the same sentence, not in a red card of its own", () => {
    renderPanel({ job: { status: "done", project: "düğün", done: 20, failed: 3, total: 23 },
                  pending: [], failures: ["1_a.png", "2_a.png", "3_a.png"] });

    expect(screen.getByText("Kuyruk tamamlandı")).toBeTruthy();
    expect(screen.getByText("20 kare üretildi")).toBeTruthy();
    expect(screen.getByText(", 3 hatalı")).toBeTruthy();
    expect(screen.queryByText(/yarım kaldı/)).toBeNull();
  });
});

describe("QueuePanel — an empty queue", () => {
  it("points at the panel that fills it", () => {
    renderPanel({ job: { status: "idle" }, pending: [] });

    expect(screen.getByText("Kuyruk boş")).toBeTruthy();
    expect(screen.getByText("Fotoğraf üret panelinden kare gönder.")).toBeTruthy();
    expect(screen.queryByText("Kuyruğu boşalt")).toBeNull();
  });

  it("says whose run is holding the worker when it is another project's", () => {
    renderPanel({ job: { status: "running", project: "balo" }, busyElsewhere: true, pending: [] });

    expect(screen.getByText("Üretim sürüyor: balo — bitmesini bekle.")).toBeTruthy();
  });
});

describe("QueuePanel — the failures line", () => {
  it("takes the user to the frame in the gallery", () => {
    const onShowFailures = vi.fn();
    renderPanel({ failures: ["1_a.png", "2_a.png", "3_a.png"], onShowFailures });

    fireEvent.click(screen.getByText("3 kare üretilemedi — galeride göster"));

    expect(onShowFailures).toHaveBeenCalled();
  });

  it("stays away when nothing failed", () => {
    renderPanel();

    expect(screen.queryByText(/üretilemedi/)).toBeNull();
  });
});

describe("QueuePanel — the connection", () => {
  it("reports the last known count in the new counter's language", () => {
    renderPanel({ error: DEAD });

    expect(screen.getByText("Sunucuya ulaşılamıyor — son bilinen: 2 kare bekliyor")).toBeTruthy();
  });

  it("stays quiet while the connection holds", () => {
    renderPanel();

    expect(screen.queryByText(/son bilinen/)).toBeNull();
  });

  it("leaves a field error to the form panel", () => {
    renderPanel({ job: { status: "idle" }, pending: [],
                  error: "Format hatası — liste okunamadı", errorField: "prompts" });

    expect(screen.queryByText("Format hatası — liste okunamadı")).toBeNull();
  });
});
