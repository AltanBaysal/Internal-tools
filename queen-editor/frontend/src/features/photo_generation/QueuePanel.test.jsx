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
      queue={[{ layer: "photo", owed: 2 }]}
      failures={[]}
      onStop={() => {}}
      onResume={() => {}}
      onCancel={() => {}}
      onRetryAll={() => {}}
      {...props}
    />,
  );
}

const button = (label) => screen.getByRole("button", { name: label });

describe("QueuePanel — a flowing queue", () => {
  it("draws the kind's own card and no run card of its own", () => {
    renderPanel();

    expect(screen.getByText("Foto · üretiliyor")).toBeTruthy();
    expect(screen.getByText("2")).toBeTruthy();
    expect(screen.getByText("kare bekliyor")).toBeTruthy();
    expect(screen.getByText("Duraklat")).toBeTruthy();
    expect(screen.queryByText("Üretiliyor")).toBeNull();
  });

  it("draws one card per kind, in the order the engine works in", () => {
    renderPanel({ queue: [{ layer: "video", owed: 3 }, { layer: "photo", owed: 1 }] });

    const cards = [...document.querySelectorAll("[data-kind]")].map((c) => c.dataset.kind);
    expect(cards).toEqual(["photo", "video"]);
  });

  it("counts jobs rather than frames for the layers that do not open one", () => {
    renderPanel({ queue: [{ layer: "photo", owed: 1 }, { layer: "video", owed: 3 }] });

    expect(screen.getByText("kare bekliyor")).toBeTruthy();
    expect(screen.getByText("iş bekliyor")).toBeTruthy();
  });

  it("leaves only the kind the worker is on alive", () => {
    renderPanel({ job: { ...RUNNING, current: { id: "P0_0", type: "photo" } },
                  queue: [{ layer: "photo", owed: 1 }, { layer: "video", owed: 3 }] });

    const alive = [...document.querySelectorAll("[data-kind]")]
      .filter((card) => card.querySelector(".qe-dot--alive"))
      .map((card) => card.dataset.kind);
    expect(alive).toEqual(["photo"]);
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
    renderPanel({ job: PAUSED, queue: [{ layer: "photo", owed: 3 }] });

    expect(screen.getByText("Duraklatıldı")).toBeTruthy();
    expect(screen.getByText("3")).toBeTruthy();
    expect(screen.getByText("Devam et")).toBeTruthy();
    expect(screen.getByText("Kuyruğu boşalt")).toBeTruthy();
  });

  it("puts the queue's own card beside the run's, each answering its own question", () => {
    renderPanel({ job: PAUSED, queue: [{ layer: "photo", owed: 3 }] });

    expect(screen.getByText("Duraklatıldı")).toBeTruthy();
    expect(screen.getByText("Foto · sırada")).toBeTruthy();
  });

  it("keeps the destructive button at the foot of the panel", () => {
    renderPanel({ job: PAUSED, queue: [{ layer: "photo", owed: 2 }] });

    const clear = screen.getByText("Kuyruğu boşalt");
    const resume = screen.getByText("Devam et");
    expect(resume.compareDocumentPosition(clear) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
  });

  it("asks before emptying the queue and never says it cannot be undone", () => {
    renderPanel({ job: PAUSED, queue: [{ layer: "photo", owed: 2 }] });

    fireEvent.click(screen.getByText("Kuyruğu boşalt"));

    expect(screen.getByText("Kuyruk boşaltılsın mı?")).toBeTruthy();
    expect(screen.getByText(
      "Bekleyen 2 kare üretilmeden kuyruktan çıkar. Üretilmiş kareler galeride kalır."))
      .toBeTruthy();
    expect(screen.queryByText(/geri alınamaz/)).toBeNull();
    // Each window is as wide as its own sentence (madde 105).
    expect(screen.getByText("Kuyruk boşaltılsın mı?").closest(".wf-card").style.width)
      .toBe("380px");
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
    renderPanel({ job: { status: "idle" }, queue: [{ layer: "photo", owed: 2 }] });

    expect(screen.getByText("Duraklatıldı")).toBeTruthy();
    expect(screen.getByText("Kaldığı yerden devam et")).toBeTruthy();
    expect(screen.queryByText(/yarım kaldı/)).toBeNull();
  });
});

describe("QueuePanel — a finished queue", () => {
  it("confirms in one sentence", () => {
    renderPanel({ job: { status: "done", project: "düğün", done: 20, failed: 0, total: 20 },
                  queue: [] });

    expect(screen.getByText("Kuyruk tamamlandı")).toBeTruthy();
    expect(screen.getByText("20 kare üretildi")).toBeTruthy();
  });

});

describe("QueuePanel — an empty queue", () => {
  it("points at the panel that fills it", () => {
    renderPanel({ job: { status: "idle" }, queue: [] });

    expect(screen.getByText("Kuyruk boş")).toBeTruthy();
    expect(screen.getByText("Fotoğraf üret panelinden kare gönder.")).toBeTruthy();
    expect(screen.queryByText("Kuyruğu boşalt")).toBeNull();
  });

  it("says whose run is holding the worker when it is another project's", () => {
    renderPanel({ job: { status: "running", project: "balo" }, busyElsewhere: true, queue: [] });

    expect(screen.getByText("Üretim sürüyor: balo — bitmesini bekle.")).toBeTruthy();
  });
});

describe("QueuePanel — the failures card", () => {
  it("keeps the good news to itself and gives the failures their own card", () => {
    renderPanel({ job: { status: "done", project: "düğün", done: 20, failed: 3, total: 23 },
                  queue: [], failures: [{ layer: "photo", count: 3 }] });

    expect(screen.getByText("Kuyruk tamamlandı")).toBeTruthy();
    expect(screen.getByText("20 kare üretildi")).toBeTruthy();
    expect(screen.queryByText(", 3 hatalı")).toBeNull();
    expect(screen.getByText("3 kare üretilemedi")).toBeTruthy();
    expect(screen.getByText("Hepsini tekrar dene")).toBeTruthy();
  });

  it("breaks the total down only when more than one kind failed", () => {
    renderPanel({ failures: [{ layer: "photo", count: 2 }, { layer: "video", count: 1 }] });

    expect(screen.getByText("3 kare üretilemedi — 2 foto · 1 video")).toBeTruthy();
  });

  it("puts every red job back in line at once, instead of pointing at the gallery", () => {
    const onRetryAll = vi.fn();
    renderPanel({ failures: [{ layer: "photo", count: 3 }], onRetryAll });

    fireEvent.click(screen.getByText("Hepsini tekrar dene"));

    expect(onRetryAll).toHaveBeenCalled();
    expect(screen.queryByText(/galeride göster/)).toBeNull();
  });

  it("stays away when nothing failed", () => {
    renderPanel();

    expect(screen.queryByText(/üretilemedi/)).toBeNull();
  });

  it("dresses the finished card in green and the stopped one in red", () => {
    const finished = renderPanel({
      job: { status: "done", project: "düğün", done: 20, failed: 0, total: 20 },
      queue: [], failures: [] });
    expect(finished.container.querySelector("[data-run-card]").style.borderColor)
      .toBe("var(--ok)");
    finished.unmount();

    const stopped = renderPanel({ job: { status: "error", project: "düğün", done: 1, total: 3 },
                                  queue: [{ layer: "photo", owed: 2 }] });
    expect(stopped.container.querySelector("[data-run-card]").style.borderColor)
      .toBe("var(--danger)");
  });

  it("draws a queue its session left behind as paused, not as a failure", () => {
    // Nothing broke: the runtime went away. Sharing the red card with a run the engine stopped
    // told the user something had gone wrong when nothing had.
    const { container } = renderPanel({ job: { status: "idle", project: "düğün" },
                                        queue: [{ layer: "photo", owed: 2 }] });

    expect(screen.getByText("Duraklatıldı")).toBeTruthy();
    expect(screen.getByText("Kaldığı yerden devam et")).toBeTruthy();
    expect(container.querySelector("[data-run-card]").style.borderColor).not.toBe("var(--danger)");
  });
});

describe("QueuePanel — a queue with nobody to do the work", () => {
  const WAITING = { status: "waiting", project: "düğün", waitingFor: "video" };

  it("says what it is waiting for rather than calling it a failure", () => {
    renderPanel({ job: WAITING, queue: [{ layer: "video", owed: 5 }] });

    expect(screen.getByText("Bekliyor — üretici kurulu değil")).toBeTruthy();
    expect(screen.getByText("5 video")).toBeTruthy();
    expect(screen.queryByText("Üretim durdu")).toBeNull();
  });

  it("offers the one button that would unblock it, by name", () => {
    const onInstall = vi.fn();
    renderPanel({ job: WAITING, queue: [{ layer: "video", owed: 5 }], onInstall });

    fireEvent.click(screen.getByText("Video üreticisini kur"));

    expect(onInstall).toHaveBeenCalledWith("video");
  });

  it("promises no longer to carry itself on", () => {
    renderPanel({ job: WAITING, queue: [{ layer: "video", owed: 5 }] });

    expect(screen.queryByText("Kurulum bitince kuyruk kendiliğinden sürer.")).toBeNull();
    expect(screen.queryByText("Kaldığı yerden devam et")).toBeNull();
  });

  it("offers the way on only once the producer is really here", () => {
    const onResume = vi.fn();
    renderPanel({ job: WAITING, queue: [{ layer: "video", owed: 5 }],
                  producerReady: true, onResume });

    fireEvent.click(screen.getByText("Kaldığı yerden devam et"));

    expect(onResume).toHaveBeenCalled();
    // The install button steps aside: what is missing is a press, not a model.
    expect(screen.queryByText("Video üreticisini kur")).toBeNull();
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
    renderPanel({ job: { status: "idle" }, queue: [],
                  error: "Format hatası — liste okunamadı", errorField: "prompts" });

    expect(screen.queryByText("Format hatası — liste okunamadı")).toBeNull();
  });
});

// 2026-08-14: ComfyUI refused four nodes at once and the engine printed the sixty lines it
// answered with. The panel does not scroll, the block had no ceiling, and both buttons went off
// the bottom -- the run could neither be continued nor emptied.
describe("QueuePanel — a stopped run with a lot to say", () => {
  const NOISE = ["POST /prompt -> node_errors", "{"]
    .concat(Array.from({ length: 60 }, (_, i) => `  "node ${i}": "value_not_in_list",`))
    .concat(["}"])
    .join("\n");
  const RULE = "Aynı kare 3 kez denendi — üretim durduruldu";
  const HALTED = { status: "error", project: "düğün", error: `${RULE}\n${NOISE}` };

  function renderHalted() {
    return renderPanel({ job: HALTED, queue: [{ layer: "video", owed: 8 }] });
  }

  it("does not let the output push the buttons off the panel", () => {
    renderHalted();

    expect(document.querySelector("[data-raw]")).toBeTruthy();
    expect(screen.getByText("Kuyruğu boşalt")).toBeTruthy();
    expect(screen.getByText("Kaldığı yerden devam et")).toBeTruthy();
  });

  it("leaves the rule's own sentence outside the box", () => {
    // Two different things: one is read, the other is folded away and copied. Inside one block
    // they read as a single technical dump and the sentence is lost in it.
    renderHalted();

    expect(screen.getByText(RULE)).toBeTruthy();
    expect(document.querySelector("[data-raw]").textContent).toBe(NOISE);
  });
});
