# Madde 424 — Uzunluk seçimi, test turu planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 424'ün davranışını — H3'te video panelinde *Video uzunluğu*, cümlelerin ve notların uzunlukla
bitmesi, yazılamayan seçimin kartı — kod yazılmadan önce testlerle tarif etmek, ve testleri kırmızı
commit'lemek.

**Architecture:** Yalnız test dosyaları değişir. `shared/api.js`'in iki yeni fonksiyonu sahte `fetch`'le;
`LayerPanel` ve `PhotoDetail` taklit edilen `shared/api.js`'le, video satırı sunucunun biçiminde
(`reads_references`).

**Tech Stack:** vitest + jsdom, Testing Library.

**Spec:** [m424 test turu](../specs/2026-10-06-queen-editor-m424-uzunluk-secimi-testler-design.md)

## Global Constraints

- Yalnız testler; `src/`'in test olmayan dosyalarına dokunulmaz.
- Test adları İngilizce, ekrandaki sözler Türkçe ve birebir.
- Sayıyla birimi arasındaki boşluk ` `.
- `skip`, `.todo` yok. Dört satır yazıldığı gibi, paralel.
- Commit mesajında çift tırnak yok; amend yok.

---

### Görev 1: `api.test.js` — kapının iki fonksiyonu

**Files:** Modify: `queen-editor/frontend/src/shared/api.test.js` (Referanstan'ın kaydı testinin
altına).

**Interfaces:** Produces — `getVideoLength(project) → number`, `saveVideoLength(project, seconds)`.

- [ ] **Adım 1: Testi yaz**

```js
  it("reads and writes the project's video length at its own address", async () => {
    const fetchMock = vi.fn().mockResolvedValue(okResponse({ seconds: 12 }));
    vi.stubGlobal("fetch", fetchMock);

    // Through the module, so a missing export fails this test rather than the file.
    expect(await api.getVideoLength("düğün")).toBe(12);
    await api.saveVideoLength("düğün", 4);

    const url = `/api/projects/${encodeURIComponent("düğün")}/video-length`;
    expect(fetchMock.mock.calls[0][0]).toBe(url);
    expect(fetchMock.mock.calls[0][1].method).toBeUndefined();
    const [putUrl, put] = fetchMock.mock.calls[1];
    expect(putUrl).toBe(url);
    expect(put.method).toBe("PUT");
    expect(JSON.parse(put.body)).toEqual({ seconds: 4 });
  });
```

### Görev 2: `LayerPanel.test.jsx` — taklit, değişen dört satır, yeni bölüm

**Files:** Modify: `queen-editor/frontend/src/features/photo_generation/LayerPanel.test.jsx`.

**Interfaces:** Consumes — Görev 1'in iki fonksiyonu (taklit). Uygulama turunun vereceği: H3'te
*"Video uzunluğu"* başlığı `data-label`'lı, düğmelerin adı `"<n> saniye"`, metni `"<n> sn"`, seçili
olan `is-on`.

- [ ] **Adım 1: Taklide iki fonksiyon, her testin başında cevapları**

```js
import { getReferenceSettings, getVideoLength, saveReferenceSettings,
         saveVideoLength } from "../../shared/api.js";

vi.mock("../../shared/api.js", async (importOriginal) => ({
  ...(await importOriginal()),
  getReferenceSettings: vi.fn(),
  getVideoLength: vi.fn(),
  saveReferenceSettings: vi.fn(),
  saveVideoLength: vi.fn(),
}));

beforeEach(() => {
  vi.clearAllMocks();
  getReferenceSettings.mockResolvedValue({ prompts: "", variants: null });
  saveReferenceSettings.mockResolvedValue(null);
  // The project's length as the server says it when nothing is saved.
  getVideoLength.mockResolvedValue(8);
  saveVideoLength.mockResolvedValue(null);
});
```

- [ ] **Adım 2: Referanstan'ın satırı noktayla** — dört testte beklenen metin: `"2 prompt × 3 varyant = 6
  kart."` ve üç kez `"2 prompt × 1 varyant = 2 kart."`.

- [ ] **Adım 3: Yeni bölüm, dosyanın sonuna**

```js
describe("LayerPanel — the H3 video length (madde 424)", () => {
  // The video row the way the server gives it: whether the session's model is H3 is the server's to
  // say (reads_references), never read off the name in the box.
  const H3 = { id: "video", name: "Video üreticisi", installed: true, model: "MiniMax H3",
               reads_references: true };
  const WAN = { ...H3, model: "WAN 2.2 I2V", reads_references: false };
  const AUDIO = { id: "audio", name: "Ses üreticisi", installed: true, model: "MMAudio v2" };
  const PLAIN = ["Model", "Kapsam", "Üretim modu", "Varyant"];
  const LOOP_LINE = "2 loop video üretilecek — her video kendine döner.";

  const lengthButton = (seconds) => screen.getByRole("button", { name: `${seconds} saniye` });
  const chosen = () => [4, 8, 12].map((one) => lengthButton(one).className.includes("is-on"));

  // An H3 session unless told otherwise, with the project's length already read.
  async function renderReady(props) {
    const view = renderPanel({ producer: H3, ...props });
    await act(async () => {});
    return view;
  }

  it("sits right under the Model box in an H3 session, the project's 8 chosen", async () => {
    const project = freshProject();
    const view = await renderReady({ project });

    expect(labels(view)).toEqual(["Model", "Video uzunluğu", "Kapsam", "Üretim modu", "Varyant"]);
    // One segment, in the design's order; the number and its unit never part.
    const segment = lengthButton(8).parentElement;
    expect(segment.className).toContain("wf-segment");
    expect([...segment.children].map((one) => one.textContent))
      .toEqual(["4 sn", "8 sn", "12 sn"]);
    expect(chosen()).toEqual([false, true, false]);
    expect(getVideoLength).toHaveBeenCalledWith(project);
  });

  it("stands in the same place on Referanstan", async () => {
    const view = await renderReady();

    await act(async () => { fireEvent.click(tab("Referanstan")); });

    expect(labels(view))
      .toEqual(["Model", "Video uzunluğu", "Referanslar", "Prompt listesi", "Varyant"]);
  });

  it("opens on the length the project saved", async () => {
    getVideoLength.mockResolvedValue(12);
    await renderReady();

    expect(chosen()).toEqual([false, false, true]);
  });

  it("marks the pressed length at once and writes it to the project", async () => {
    saveVideoLength.mockReturnValue(new Promise(() => {}));
    const project = freshProject();
    await renderReady({ project });

    fireEvent.click(lengthButton(12));

    expect(chosen()).toEqual([false, false, true]);
    expect(saveVideoLength).toHaveBeenCalledWith(project, 12);
  });

  it("stays where it is, with its choice, when the tab changes", async () => {
    await renderReady();
    await act(async () => { fireEvent.click(lengthButton(12)); });

    await act(async () => { fireEvent.click(tab("Referanstan")); });
    expect(chosen()).toEqual([false, false, true]);
    await act(async () => { fireEvent.click(tab("Kareden")); });
    expect(chosen()).toEqual([false, false, true]);
  });

  it("leaves every other box as it was", async () => {
    await renderReady();
    fireEvent.click(screen.getByText("Standart").closest("button"));
    fireEvent.change(variantBox(), { target: { value: "3" } });

    await act(async () => { fireEvent.click(lengthButton(12)); });

    expect(variantBox().value).toBe("3");
    expect(screen.getByText("6 video üretilecek — her kare kendi videosunu alır. 12 sn."))
      .toBeTruthy();
  });

  it("opens a rebuilt panel on the length it knew, and the server's answer stands", async () => {
    getVideoLength.mockResolvedValue(12);
    (await renderReady({ project: "uzunluk-a" })).unmount();
    let answer;
    getVideoLength.mockReturnValue(new Promise((resolve) => { answer = resolve; }));

    await renderReady({ project: "uzunluk-a" });
    // Drawn at once: a block that came in a beat after every opening would push the panel down.
    expect(chosen()).toEqual([false, false, true]);

    await act(async () => { answer(4); });
    expect(chosen()).toEqual([true, false, false]);
  });

  it("keeps a length pressed while the read is on its way", async () => {
    (await renderReady({ project: "uzunluk-b" })).unmount();
    let answer;
    getVideoLength.mockReturnValue(new Promise((resolve) => { answer = resolve; }));
    await renderReady({ project: "uzunluk-b" });

    await act(async () => { fireEvent.click(lengthButton(4)); });
    await act(async () => { answer(12); });

    expect(chosen()).toEqual([true, false, false]);
  });

  it("is not drawn in a WAN session, and nobody asks for the length", async () => {
    const view = await renderReady({ producer: WAN });

    expect(labels(view)).toEqual(PLAIN);
    expect(screen.getByText(LOOP_LINE)).toBeTruthy();
    expect(getVideoLength).not.toHaveBeenCalled();
  });

  it("is not drawn while the model is not read yet", async () => {
    const view = await renderReady({ producer: null });

    expect(labels(view)).toEqual(PLAIN);
    expect(screen.getByText(LOOP_LINE)).toBeTruthy();
    expect(getVideoLength).not.toHaveBeenCalled();
  });

  it("is drawn in an H3 session whose video producer is not installed yet", async () => {
    // The Model box names H3 either way, and the length is the project's, not the producer's.
    const view = await renderReady({ producer: { ...H3, installed: false } });

    expect(labels(view)).toContain("Video uzunluğu");
  });

  it("waits for the project's length before it draws the choice or says the length", async () => {
    getVideoLength.mockReturnValue(new Promise(() => {}));
    const view = await renderReady();

    expect(labels(view)).toEqual(PLAIN);
    expect(screen.getByText(LOOP_LINE)).toBeTruthy();
  });

  it("leaves the choice out, and says nothing of its own, when the length cannot be read",
     async () => {
    getVideoLength.mockRejectedValue(new Error("Sunucuya ulaşılamadı — bağlantıyı kontrol et."));
    const view = await renderReady();

    expect(labels(view)).toEqual(PLAIN);
    expect(screen.getByText(LOOP_LINE)).toBeTruthy();
    expect(screen.queryByText("Sunucuya ulaşılamadı — bağlantıyı kontrol et.")).toBeNull();
  });

  it("has no length on the sound panel", async () => {
    const view = await renderReady({ layer: "audio", producer: AUDIO,
                                     frames: [done("0_a.png", { video: "0_a_V1_0.mp4" })] });

    expect(labels(view)).toEqual(["Model", "Kapsam", "Varyant"]);
    expect(screen.getByText("1 ses üretilecek — her kare kendi sesini alır.")).toBeTruthy();
    expect(getVideoLength).not.toHaveBeenCalled();
  });

  it.each([
    ["Loop", "2 loop video üretilecek — her video kendine döner. 8 sn."],
    ["Sonrakine bağla", "2 bağlı video üretilecek — her video sıradaki karede biter. 8 sn."],
    ["Standart", "2 video üretilecek — her kare kendi videosunu alır. 8 sn."],
  ])("ends the line under the button with the length on %s", async (mode, line) => {
    await renderReady();

    fireEvent.click(screen.getByText(mode).closest("button"));

    // The space is unbreakable: the number never ends a line with its unit alone on the next.
    expect(screen.getByText(line).textContent.endsWith(" 8 sn.")).toBe(true);
  });

  it("ends the copy warning with the length too", async () => {
    await renderReady({ selected: ["1_a"] });

    expect(screen.getByText("1 loop video üretilecek — videolu 1 kare için yeniler kopya kare "
                            + "olur, eskisi durur. 8 sn.")).toBeTruthy();
  });

  it("says the length that was chosen", async () => {
    await renderReady();

    await act(async () => { fireEvent.click(lengthButton(12)); });

    expect(screen.getByText(`${LOOP_LINE} 12 sn.`)).toBeTruthy();
  });

  it("ends Referanstan's line with the length", async () => {
    await renderReady();
    await act(async () => { fireEvent.click(tab("Referanstan")); });

    fireEvent.change(screen.getByLabelText("Prompt listesi"),
                     { target: { value: '["gotik kız", "dans"]' } });
    fireEvent.change(variantBox(), { target: { value: "3" } });

    expect(screen.getByText("2 prompt × 3 varyant = 6 kart. 8 sn.")).toBeTruthy();
  });

  it("puts no length on the card that says what the queue took", async () => {
    await renderReady({ onQueue: () => Promise.resolve({ added: 2 }) });

    await act(async () => { fireEvent.click(screen.getByText("Kuyruğa ekle")); });

    expect(screen.getByText("2 loop video kuyruğa eklendi")).toBeTruthy();
  });

  it("says the server's sentence when the length cannot be written, and goes back to the saved one",
     async () => {
    saveVideoLength.mockRejectedValue(new Error("Proje yok: düğün"));
    await renderReady();

    await act(async () => { fireEvent.click(lengthButton(12)); });

    // The panel's own red card under the button, where its other failures are said.
    const card = screen.getByText("Proje yok: düğün");
    expect(card.closest(".wf-stroke").style.borderColor).toBe("var(--danger)");
    expect(screen.getByText("Kuyruğa ekle").compareDocumentPosition(card)
           & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(chosen()).toEqual([false, true, false]);
  });

  it("takes the card away with the next press that is written", async () => {
    saveVideoLength.mockRejectedValueOnce(new Error("Proje yok: düğün"));
    await renderReady();
    await act(async () => { fireEvent.click(lengthButton(12)); });

    await act(async () => { fireEvent.click(lengthButton(4)); });

    expect(screen.queryByText("Proje yok: düğün")).toBeNull();
    expect(chosen()).toEqual([true, false, false]);
  });
});
```

### Görev 3: `PhotoDetail.test.jsx` — taklit ve yeni bölüm

**Files:** Modify: `queen-editor/frontend/src/features/photo_generation/PhotoDetail.test.jsx`.

**Interfaces:** Consumes — `getVideoLength`, `listProducers` (taklit). Uygulama turunun vereceği: karenin
sayfası üreticileri ve projenin uzunluğunu kendisi okur.

- [ ] **Adım 1: Taklide iki fonksiyon; her testin başında üreticiler boş, uzunluk 8**

```js
vi.mock("../../shared/api.js", () => ({
  …
  getVideoLength: vi.fn(),
  listProducers: vi.fn(),
  …
}));

beforeEach(() => {
  …
  // No video row: the model is not known, so no note promises a length -- every older test reads
  // the page as it was.
  listProducers.mockResolvedValue([]);
  getVideoLength.mockResolvedValue(8);
});
```

- [ ] **Adım 2: Yeni bölüm, dosyanın sonuna**

```js
describe("PhotoDetail — the length a new video gets (madde 424)", () => {
  const H3_ROWS = [{ id: "video", name: "Video üreticisi", installed: true, model: "MiniMax H3",
                     reads_references: true }];
  const WAN_ROWS = [{ ...H3_ROWS[0], model: "WAN 2.2 I2V", reads_references: false }];
  const LOOPED = { ...LAYERED, modes: { video: "loop" } };
  const RED_VIDEO = { ...LAYERED, layers: { photo: "P0_0.png" }, failed: ["video"],
                      errors: { video: "ComfyUI 500 — 3 kez denendi" },
                      prompts: { photo: "kırmızı elbise" } };
  const NOTE = "Yeni bir kare açılır — P0_0 kopyası, loop video.";

  // The session's model and then the project's length are two answers in a row, so the page is
  // given two turns to take them.
  async function openIn({ rows, frames, project = "düğün", video = true }) {
    listProducers.mockResolvedValue(rows);
    listFrames.mockResolvedValue(frames);
    getStatus.mockResolvedValue(IDLE);
    listModels.mockResolvedValue({ models: [], loras: LORAS });
    render(<PhotoDetail project={project} frame="P0_0" />);
    await settle();
    await settle();
    if (video) fireEvent.click(tab("Video"));
  }

  it("ends the note under Yeniden üret with the project's length in an H3 session", async () => {
    // The project's length, not the frame's: a new video is made at what the project says now.
    getVideoLength.mockResolvedValue(12);
    await openIn({ rows: H3_ROWS, frames: [LOOPED] });

    expect(screen.getByText(`${NOTE} 12 sn.`)).toBeTruthy();
  });

  it("leaves that note as it was in a WAN session", async () => {
    await openIn({ rows: WAN_ROWS, frames: [LOOPED] });

    expect(screen.getByText(NOTE)).toBeTruthy();
  });

  it("puts a note under a red video's Tekrar dene in an H3 session", async () => {
    await openIn({ rows: H3_ROWS, frames: [RED_VIDEO] });

    const note = screen.getByText("Aynı kare yeniden denenir. 8 sn.");
    expect(screen.getByText("Tekrar dene — bu kareye").compareDocumentPosition(note)
           & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
  });

  it("gives Tekrar dene no note in a WAN session", async () => {
    await openIn({ rows: WAN_ROWS, frames: [RED_VIDEO] });

    expect(screen.getByText("Tekrar dene — bu kareye")).toBeTruthy();
    expect(screen.queryByText(/Aynı kare yeniden denenir/)).toBeNull();
  });

  it("gives the photo tab's Tekrar dene no note", async () => {
    await openIn({ rows: H3_ROWS, frames: [BROKEN], video: false });

    expect(screen.getByText("Tekrar dene — bu kareye")).toBeTruthy();
    expect(screen.queryByText(/Aynı kare yeniden denenir/)).toBeNull();
  });

  it("promises no length under Yeniden üret while the length cannot be read", async () => {
    getVideoLength.mockRejectedValue(new Error("Sunucuya ulaşılamadı — bağlantıyı kontrol et."));
    await openIn({ rows: H3_ROWS, frames: [LOOPED], project: "kına-424a" });

    expect(screen.getByText(NOTE)).toBeTruthy();
  });

  it("gives Tekrar dene no note while the length cannot be read", async () => {
    getVideoLength.mockRejectedValue(new Error("Sunucuya ulaşılamadı — bağlantıyı kontrol et."));
    await openIn({ rows: H3_ROWS, frames: [RED_VIDEO], project: "kına-424b" });

    expect(screen.queryByText(/Aynı kare yeniden denenir/)).toBeNull();
  });
});
```

### Görev 4: Kırmızıyı gör ve commit'le

- [ ] **Adım 1: Dört satır, paralel, yazıldığı gibi**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: üç satır yeşil; queen-editor'ün frontend'inde 24 kırmızı — Görev 1'in testi, Görev 2'nin
değişen dördü ve yeni bölümün 17'si, Görev 3'ün ikisi (`ends the note under Yeniden üret…`, `puts a
note under a red video's Tekrar dene…`). Başka kırmızı yok.

- [ ] **Adım 2: Commit**

```
git add docs/superpowers/specs/2026-10-06-queen-editor-m424-uzunluk-secimi-testler-design.md docs/superpowers/plans/2026-10-06-queen-editor-m424-uzunluk-secimi-testler-plan.md queen-editor/frontend/src/shared/api.test.js queen-editor/frontend/src/features/photo_generation/LayerPanel.test.jsx queen-editor/frontend/src/features/photo_generation/PhotoDetail.test.jsx
git commit -m "test(queen-editor): Madde 424 red -- the H3 video length is chosen under the Model box and said at the end of the panel's line and the frame page's notes" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```
