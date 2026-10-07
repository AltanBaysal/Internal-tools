# Madde 408 — Süre kartta, test planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Üretim süresinin karenin sayfasında ve galerinin etiketinde göründüğünü, ve durum raporunun
modelin başladığı anı söylediğini anlatan testleri yazmak, kırmızı koşmak, kırmızı commit'lemek.

**Architecture:** Backend'de döngünün raporları bir casus runner'la izlenir. Frontend'de kanca
(`useGeneration`), karenin sayfası, galeri ve proje ekranı sahte saatle sınanır. Üretim kodu bu turda
değişmez.

**Tech Stack:** pytest; vitest + jsdom + Testing Library.

**Spec:** [m408 test turu](../specs/2026-10-01-queen-editor-m408-sure-kartta-testler-design.md)

## Global Constraints

- Durum alanı `startedAt`: döngünün `now()`'ı, ISO; model çalışmıyorken `null`.
- Kancanın verdiği değer `startedAt`; galerinin prop'u `startedAt`.
- Süre `m:ss`, saniyeler aşağı yuvarlanır, sıfırın altına inmez.
- Karenin sayfasında alanın etiketi `Üretim süresi`, değeri `data-time` taşıyan öğede.
- Test adları ve yorumlar İngilizce; hiçbir test gerçek bir saniye beklemez.
- Testler yalnız CLAUDE.md'nin dört satırıyla koşulur, aynen, paralel. `skip`, `xfail`, `.skip`,
  `.todo` yok.

---

### Task 1: Döngünün raporu modelin başladığı anı söyler

**Files:**
- Modify: `queen-editor/backend/tests/test_photo_usecases.py` —
  `test_a_retried_layer_carries_the_time_of_the_attempt_that_made_it`'tan sonra

- [ ] **Step 1: Yardımcılar ve dört test**

```python
def watched():
    """A runner whose every report is kept, in order, and still reaches the runner itself."""
    runner, reports = sync_runner(), []
    original = runner.report
    runner.report = lambda patch: (reports.append(patch), original(patch))[1]
    return runner, reports


def merged(reports):
    """The status as the runner holds it: each report laid over the ones before it."""
    state = {}
    for patch in reports:
        state.update(patch)
    return state


def ticking():
    """A wall clock that says t1, t2, ... -- so a test can name which reading went where."""
    said = []

    def now():
        said.append(f"t{len(said) + 1}")
        return said[-1]
    return now


def test_the_report_names_when_the_model_started_and_clears_it_for_the_next_job():
    # t2 is the first row's createdAt; each job's first report clears the start before its own.
    runner, reports = watched()
    plan_store = FakePlanStore(frames=[frame(0), frame(1)])

    make_job(runner, FakeStore(), FakeRecord(), plan_store, {layers.PHOTO: FakeGenerator()},
             ticking(), "düğün")()

    assert [patch["startedAt"] for patch in reports] == [None, "t1", None, "t3"]


class Peeking(FakeStore):
    """Drive, noting what the status said at the moment each file came off it."""

    def __init__(self, reports):
        super().__init__()
        self.reports, self.seen = reports, []

    def read(self, project, filename):
        self.seen.append(merged(self.reports))
        return super().read(project, filename)


def test_no_start_is_reported_while_the_layers_source_is_read():
    # The video is the job in hand, but the model is not working yet.
    _store, record, plan_store = video_job_project(job_prompt="kamera yaklaşır")
    runner, reports = watched()
    store = Peeking(reports)
    store.files["0_a.png"] = b"PNG"

    make_job(runner, store, record, plan_store, {layers.VIDEO: FakeGenerator()}, ticking(),
             "düğün")()

    assert store.seen[0]["current"]["type"] == "video"
    assert store.seen[0]["startedAt"] is None


class PeekingWriter(FakeWriter):
    """A language model noting what the status said while it was asked."""

    def __init__(self, reports):
        super().__init__()
        self.reports, self.seen = reports, []

    def write(self, prompts, mode="standard", source=None, end=None, scene=""):
        self.seen.append(merged(self.reports))
        return super().write(prompts, mode, source, end, scene)


def test_no_start_is_reported_while_a_prompt_is_written():
    store, record, plan_store = video_job_project(prompt="kırmızı elbiseli kadın")
    runner, reports = watched()
    writer = PeekingWriter(reports)

    make_job(runner, store, record, plan_store, {layers.VIDEO: FakeGenerator()}, ticking(),
             "düğün", writers={layers.VIDEO: writer})()

    assert writer.seen[0]["current"] is None
    assert writer.seen[0]["startedAt"] is None


class Glancing(FakeGenerator):
    """A producer noting the start the status gave each attempt; the first `fails` blow up."""

    def __init__(self, reports, fails=0):
        super().__init__()
        self.reports, self.fails, self.seen = reports, fails, []

    def generate(self, prompt, negative, seed, model="", lora="", source=None, end=None,
                 references=()):
        super().generate(prompt, negative, seed, model, lora, source, end, references)
        self.seen.append(merged(self.reports).get("startedAt"))
        if len(self.calls) <= self.fails:
            raise FrameFault(f"node 41: {prompt}")
        return b"PNG"


def test_each_attempt_at_a_layer_reports_its_own_start():
    # The live counter starts again with the attempt, as the recorded time does (madde 405).
    runner, reports = watched()
    producer = Glancing(reports, fails=2)

    make_job(runner, FakeStore(), FakeRecord(), FakePlanStore(frames=[frame(0)]),
             {layers.PHOTO: producer}, ticking(), "düğün")()

    assert producer.seen == ["t1", "t2", "t3"]
```

### Task 2: Kanca anı verir

**Files:** Modify `queen-editor/frontend/src/features/photo_generation/useGeneration.test.jsx` —
`says which layer the worker is making` testinden sonra.

```js
  it("says when the model started on the layer it is making (madde 408)", async () => {
    getStatus.mockResolvedValue({ ...RUNNING, current: { id: "P0_0", type: "video" },
                                  startedAt: "2026-10-01T10:00:00+00:00" });
    listFrames.mockResolvedValue([]);

    const { result } = renderHook(() => useGeneration("düğün"));
    await settle();

    expect(result.current.startedAt).toBe("2026-10-01T10:00:00+00:00");
  });

  it("says no start for another project's run", async () => {
    getStatus.mockResolvedValue({ ...RUNNING, project: "komşu", current: { id: "P0_0" },
                                  startedAt: "2026-10-01T10:00:00+00:00" });
    listFrames.mockResolvedValue([]);

    const { result } = renderHook(() => useGeneration("düğün"));
    await settle();

    expect(result.current.startedAt).toBeNull();
  });
```

### Task 3: Karenin sayfası

**Files:** Modify `queen-editor/frontend/src/features/photo_generation/PhotoDetail.test.jsx` — dosyanın
sonuna yeni bir `describe`.

```js
describe("PhotoDetail — the production time (madde 408)", () => {
  // The fake clock's wall time, and starts measured back from it.
  const NOW = new Date("2026-10-01T10:00:00Z");
  const AGO_46 = "2026-10-01T09:59:14+00:00";
  const timeShown = () => document.querySelector("[data-time]");
  const infoFacts = () => facts(document.querySelector('[data-group="info"]'));
  const making = (extra = {}) => ({ status: "running", project: "düğün",
                                    current: { id: "P0_0", type: "video" }, ...extra });

  beforeEach(() => { vi.setSystemTime(NOW); });

  it("puts the open layer's recorded time beside the counter, with no layer word", async () => {
    await open("P0_0", { frames: [{ ...LAYERED, renderSeconds: { photo: 46.3 } }] });

    expect(infoFacts()).toEqual(["Sıra", "Üretim süresi"]);
    expect(timeShown().textContent).toBe("0:46");
  });

  it("says the time of the layer whose tab is open", async () => {
    await open("P0_0", { frames: [{ ...LAYERED,
                                    renderSeconds: { photo: 46.3, video: 212.0, audio: 19.4 } }] });

    fireEvent.click(tab("Video"));
    expect(timeShown().textContent).toBe("3:32");

    fireEvent.click(tab("Ses"));
    expect(timeShown().textContent).toBe("0:19");
  });

  it("draws no field for a frame made before times were recorded", async () => {
    await open("P0_0", { frames: [LAYERED] });

    expect(infoFacts()).toEqual(["Sıra"]);
    expect(screen.queryByText("Üretim süresi")).toBeNull();
  });

  it("draws no field for a layer that failed", async () => {
    await open("P0_0", { frames: [{ ...LAYERED, layers: { photo: "P0_0.png" },
                                    failed: ["video"], errors: { video: "node 41: OOM" },
                                    renderSeconds: { photo: 46.3 } }] });
    expect(timeShown().textContent).toBe("0:46");

    fireEvent.click(tab("Video"));

    expect(screen.queryByText("Üretim süresi")).toBeNull();
  });

  it("says a queued layer has not started yet", async () => {
    await open("P0_1", { frames: [QUEUED_COPY] });

    fireEvent.click(tab("Video"));

    expect(timeShown().textContent).toBe("henüz başlamadı");
  });

  it("counts the layer being made, live", async () => {
    await open("P0_0", { frames: [RENDERING], status: making({ startedAt: AGO_46 }) });
    fireEvent.click(tab("Video"));

    expect(timeShown().textContent).toBe("0:46");
    expect(timeShown().style.color).toBe("var(--accent)");

    await settle(2000);

    expect(timeShown().textContent).toBe("0:48");
  });

  it("picks up from the server's start when the page is opened mid-render", async () => {
    // A reload must not start the count again from nothing.
    await open("P0_0", { frames: [RENDERING],
                         status: making({ startedAt: "2026-10-01T09:57:00+00:00" }) });
    fireEvent.click(tab("Video"));

    expect(timeShown().textContent).toBe("3:00");
  });

  it("says 0:00 while the model has not been handed the layer yet", async () => {
    await open("P0_0", { frames: [RENDERING], status: making() });
    fireEvent.click(tab("Video"));

    expect(timeShown().textContent).toBe("0:00");
  });

  it("never counts below zero when the two clocks disagree", async () => {
    await open("P0_0", { frames: [RENDERING],
                         status: making({ startedAt: "2026-10-01T10:00:05+00:00" }) });
    fireEvent.click(tab("Video"));

    expect(timeShown().textContent).toBe("0:00");
  });

  it("keeps the recorded time once the layer lands", async () => {
    await open("P0_0", { frames: [RENDERING], status: making({ startedAt: AGO_46 }) });
    fireEvent.click(tab("Video"));
    listFrames.mockResolvedValue([{ ...LAYERED, renderSeconds: { photo: 46.3, video: 47.2 } }]);
    getStatus.mockResolvedValue({ status: "done", project: "düğün" });

    await settle(2000);

    expect(timeShown().textContent).toBe("0:47");
    expect(timeShown().style.color).not.toBe("var(--accent)");
  });
});
```

### Task 4: Galerinin etiketi

**Files:** Modify `queen-editor/frontend/src/features/photo_generation/Gallery.test.jsx` — dosyanın
sonuna yeni bir `describe`.

```js
describe("Gallery — the live time on the tile (madde 408)", () => {
  const AGO_46 = "2026-10-01T09:59:14+00:00";
  const pillOf = (name) => tileOf(name).querySelector("[data-pill]");

  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-10-01T10:00:00Z"));
  });
  afterEach(() => vi.useRealTimers());

  it("puts the time under the words of the tile being made", () => {
    renderGallery({ frames: [pending("P0_0.png")], current: "P0_0", currentLayer: "photo",
                    running: true, startedAt: AGO_46 });

    expect(pillOf("P0_0.png").textContent).toBe("foto üretiliyor0:46");
    expect(pillOf("P0_0.png").style.flexDirection).toBe("column");
  });

  it("moves the time on every second", () => {
    renderGallery({ frames: [pending("P0_0.png")], current: "P0_0", currentLayer: "photo",
                    running: true, startedAt: AGO_46 });

    act(() => { vi.advanceTimersByTime(1000); });

    expect(pillOf("P0_0.png").textContent).toBe("foto üretiliyor0:47");
  });

  it("keeps one line until the model has started", () => {
    renderGallery({ frames: [done("P0_0.png", { owed: ["video"] })], current: "P0_0",
                    currentLayer: "video", running: true });

    expect(pillOf("P0_0.png").textContent).toBe("video üretiliyor");
  });

  it("shows no time on a finished or a queued tile", () => {
    // Only the live time is the gallery's; a recorded one is the frame page's.
    renderGallery({ frames: [done("1_a.png", { renderSeconds: { photo: 46.3 } }),
                             done("0_a.png", { owed: ["video"] })], running: true });

    expect(document.body.textContent).not.toMatch(/\d:\d\d/);
  });
});
```

### Task 5: Proje ekranı anı galeriye verir

**Files:** Modify `queen-editor/frontend/src/features/photo_generation/ProjectScreen.test.jsx` — dosyanın
sonuna yeni bir `describe`.

```js
describe("ProjectScreen — the tile being made shows its time (madde 408)", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-10-01T10:00:00Z"));
  });
  afterEach(() => vi.useRealTimers());

  it("hands the gallery the moment the model started", async () => {
    listFrames.mockResolvedValue([{ id: "P0_0", file: "P0_0.png", status: "pending", layers: {},
                                    owed: ["photo"], failed: [] }]);
    getStatus.mockResolvedValue({ status: "running", project: "süre",
                                  current: { id: "P0_0", type: "photo" },
                                  startedAt: "2026-10-01T09:59:14+00:00" });
    renderScreen("süre");
    await act(async () => { await vi.advanceTimersByTimeAsync(0); });

    expect(document.getElementById("tile-P0_0").querySelector("[data-pill]").textContent)
      .toContain("0:46");
  });
});
```

### Task 6: Kırmızı koş, commit'le

- [ ] Dört satır, aynen, paralel:
  `python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend` ·
  `python -m pytest queen-editor -q` · `npm test --prefix queen-editor/frontend`
- [ ] Beklenen: queen-editor pytest'te Task 1'in dört testi kırmızı; vitest'te kancanın iki testi,
  sayfanın 0:46/3:32/henüz başlamadı/canlı/yeniden açılış/0:00/sıfır/bitince testleri, galerinin ilk
  iki testi ve proje ekranının testi kırmızı. Eski karenin, kırmızı katmanın, tek satırın ve süresiz
  kutucuğun testleri yeşil başlar (bir yokluğu bekliyorlar). queen-agent'ın iki satırı yeşil.
- [ ] Spec, plan ve testler tek commit: `test(queen-editor): Madde 408 red -- ...`
