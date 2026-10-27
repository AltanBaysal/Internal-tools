# v11 Görev 3 — duran üretim kuyrukta görünmez: TEST döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Beş yeni test ve güncellenmiş beş iddia; hepsi kırmızı. Kod bu döngüde değişmiyor.

**Architecture:** Galeri testleri kuyruğun akıp akmadığını artık açıkça söylüyor (`running`), ekran
testleri ise işin durumundan galeriye ne geçtiğini sınıyor — bugün hiçbir şey geçmiyor.

**Tech Stack:** vitest + @testing-library/react, jsdom.

**Tasarım:** [test spec'i](../specs/2026-08-13-queen-editor-v11-gorev-3-testler-design.md)

## Global Constraints

- **Kod değişmiyor.** `Gallery.jsx`, `frame_status.jsx`, `ProjectScreen.jsx` bu commit'te olduğu
  gibi kalır. `dist/` yeniden derlenmez.
- **Kırmızı bırakılır.**
- Test adları ve yorumlar **İngilizce**; ekrandan okunan metinler Türkçe.
- Commit mesajında **çift tırnak yok**.
- Test komutu: `npm test --prefix queen-editor/frontend`

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `.../photo_generation/Gallery.test.jsx` | etiketin kelimesi | 5 iddia güncellenir, 2 test eklenir |
| `.../photo_generation/ProjectScreen.test.jsx` | ekranın galeriye ne söylediği | 1 describe (3 test) eklenir |

---

### Task 1: Galeri testleri kuyruğun hâlini söyler

**Files:**
- Test: `queen-editor/frontend/src/features/photo_generation/Gallery.test.jsx`

**Interfaces:**
- Consumes: dosyanın `renderGallery()`, `pillOf()`, `done()`, `pending()`, `MIXED` yardımcıları.
- Produces: `running` prop'u — Görev 3'ün implementasyonunun uyacağı ad.

- [ ] **Step 1: Kuyruğun aktığı üç teste `running: true` ekle**

`"says the layer and the state in one pill, in the corner"`:

```js
    renderGallery({ frames: MIXED, current: "3_a", running: true });
```

`"turns the frame the worker is holding into a spinner without moving it"`:

```js
    renderGallery({ frames: MIXED, current: "3_a", running: true });
```

`"keeps the photo on screen while the video is queued"`:

```js
    renderGallery({ frames: [done("P0_0.png", { owed: ["video"] })], running: true });
```

Bu üçünün beklediği metinler **değişmiyor** — üçü de akan bir kuyruğu anlatıyor, ve testin adı da
öyle diyor.

- [ ] **Step 2: Kuyruğun akmadığı iki iddianın metnini çevir**

`"draws a failed frame once, red, with its own way back"` (`current: null`):

```js
    expect(screen.getAllByText("foto bekliyor")).toHaveLength(2);
```

`"does not claim the gallery is empty when only waiting frames are in it"`:

```js
    expect(screen.getByText("foto bekliyor")).toBeTruthy();
```

- [ ] **Step 3: İki yeni testi pill describe'ının sonuna ekle**

```js
  it("calls a frame queued only while the queue is flowing", () => {
    renderGallery({ frames: [done("P0_0.png", { owed: ["video"] })], running: true });

    expect(pillOf("P0_0.png").textContent).toBe("video kuyrukta");
  });

  it("calls the same frame waiting once the queue has stopped", () => {
    // The debt is real: pressing Devam et still produces this video. What is not real is movement,
    // and "kuyrukta" claims movement -- which is what a stopped run looked like on 2026-08-13.
    renderGallery({ frames: [done("P0_0.png", { owed: ["video"] })], running: false });

    expect(pillOf("P0_0.png").textContent).toBe("video bekliyor");
  });
```

- [ ] **Step 4: Yediyi de çalıştır**

Run: `npm test --prefix queen-editor/frontend`
Expected: `Gallery.test.jsx` içinde 3 düşen — iki yeni testten "bekliyor" bekleyeni ve iki
güncellenen iddia. `running: true` eklenen üçü geçmeye devam eder (bileşen prop'u henüz yok sayıyor,
sonuç aynı).

---

### Task 2: Ekran testi işin hâlini galeriye taşıdığını sınar

**Files:**
- Test: `queen-editor/frontend/src/features/photo_generation/ProjectScreen.test.jsx`

**Interfaces:**
- Consumes: `renderScreen()`, `listFrames`, `getStatus`, dosyanın mock kurulumu.
- Produces: yok.

- [ ] **Step 1: Yeni describe'ı dosyanın sonuna ekle**

```jsx
// What the gallery is told about the queue. The pill's word is the only place on screen where a
// frame says whether anything is coming for it, and the gallery cannot know that by itself.
describe("ProjectScreen — a stopped queue does not look like a moving one", () => {
  beforeEach(() => { vi.useFakeTimers(); });
  afterEach(() => vi.useRealTimers());

  const OWES_VIDEO = [{ id: "P0_0", file: "P0_0.png", status: "done", layers: { photo: "P0_0.png" },
                        owed: ["video"], failed: [] }];

  async function open(status, project) {
    listFrames.mockResolvedValue(OWES_VIDEO);
    getStatus.mockResolvedValue(status);
    renderScreen(project);
    await act(async () => { await vi.advanceTimersByTimeAsync(0); });
  }

  it("says queued while this project's queue is flowing", async () => {
    await open({ status: "running", project: "akan" }, "akan");

    expect(screen.getByText("video kuyrukta")).toBeTruthy();
  });

  it("says waiting once an error has stopped the queue", async () => {
    // 2026-08-13: a dead xAI key stopped the run and every frame went on saying it was queued.
    await open({ status: "error", project: "duran", error: "xAI HTTP 400" }, "duran");

    expect(screen.getByText("video bekliyor")).toBeTruthy();
  });

  it("says waiting while it is another project's queue that is flowing", async () => {
    // The worker is global: a batch belonging to someone else moves nothing here.
    await open({ status: "running", project: "komşu" }, "bizim");

    expect(screen.getByText("video bekliyor")).toBeTruthy();
  });
});
```

- [ ] **Step 2: Üçünün de doğru sebeple düştüğünü gör**

Run: `npm test --prefix queen-editor/frontend`
Expected: ikisi düşer (`"video bekliyor"` bulunamaz, ekranda `"video kuyrukta"` yazıyor); ilki
("akan") geçer — bugün de kuyrukta yazıyor, ama yanlış sebeple değil, doğru cevabı yanlış yoldan
veriyor. Üçü birlikte kuralı tarif ediyor.

---

### Task 3: Kırmızıyı doğrula ve commit'le

- [ ] **Step 1: Tam ön yüz takımı**

Run: `npm test --prefix queen-editor/frontend`
Expected: 309 + 5 yeni = 314; 5 düşen (Gallery'de 3, ProjectScreen'de 2), 309 geçen.

- [ ] **Step 2: Kaynak koda dokunulmadığını doğrula**

Run: `git status --short`
Expected: yalnız iki test dosyası ve `docs/superpowers`.

- [ ] **Step 3: Commit**

```bash
git add queen-editor/frontend/src docs/superpowers
git commit -F - <<'EOF'
test(queen-editor): tell a stopped queue apart from a moving one

THESE FIVE TESTS FAIL ON PURPOSE. The fix is the next commit.

A run that stopped on a dead xAI key left every frame saying video kuyrukta,
which claims movement where there is none. The debt itself is real -- pressing
Devam et still produces those videos -- so the word is what is wrong, and the
gallery cannot pick a better one because nobody tells it whether the queue is
flowing.

Two new gallery tests ask for both words from the same frame, and three screen
tests pin what the gallery should be told: this project running, this project
stopped by an error, and someone else's project running -- the last because the
worker is global and a neighbour's batch moves nothing here.

Five older assertions had frozen the missing knowledge into a habit: they all
expected kuyrukta because the gallery says kuyrukta always. The three that mean
a flowing queue now say so out loud; the two that do not now expect bekliyor.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** A1→Task 1 Step 3 birinci · A2→ikinci · A3→Task 1 Step 2'nin ikinci iddiası
(yalnız bekleyen kareler) · A4→Task 1 Step 1 ve 2 · B1, B2, B3→Task 2. Spec'te olup planda olmayan
vaka yok.

**Ad tutarlılığı:** Galeriye eklenen prop'un adı `running` — `ProjectScreen.jsx`'te aynı anlamı
taşıyan değişken zaten `running` (satır 39), yani implementasyon iki ucu aynı isimle bağlayacak.
`statusOf`'un ikinci parametresi de bugün `running` adını taşıyor ama başka bir şeyi anlatıyor (bu
karenin işlenmekte olan katmanı); implementasyon döngüsünün onu gölgelememesi gerekiyor.

**Beklenen kırmızı sayısı:** 5. Üç testin geçmeye devam etmesi bilerek — `running: true` bugünkü
davranışla aynı cevabı veriyor, ve o üç testin işi kuralın öteki yarısını korumak.

**İzlenecek madde:** `Gallery.test.jsx`'te *"leaves the middle of a waiting card wordless"* testi
`queryByText("bekliyor")`'un boş dönmesini bekliyor. Yeni etiket `"foto bekliyor"` yazacak ve
`getByText` tam eşleşme aradığı için test kırılmamalı. Kırılırsa dokunulacak yer o testin **hedefi**
(kartın ortası), beklediği kelime değil — çünkü "bekliyor" artık köşede meşru bir kelime.
