# v11 Görev 2 — seçili kare sayısı: TEST döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Beş test — ikisi yeni, üçü düzeltilmiş — hepsi kırmızı. Kod bu döngüde değişmiyor.

**Architecture:** Panel testleri seçimi artık kimlikle veriyor (bugüne kadar dosya adıyla veriyordu
ve kodun yanlış varsayımını doğruluyorlardı). Ekran testi, galeride bir kareye tıklayıp video
panelindeki sayıyı okuyarak dikişin kendisini sınıyor.

**Tech Stack:** vitest + @testing-library/react, jsdom.

**Tasarım:** [test spec'i](../specs/2026-08-13-queen-editor-v11-gorev-2-testler-design.md)

## Global Constraints

- **Kod değişmiyor.** `LayerPanel.jsx`, `Gallery.jsx`, `ProjectScreen.jsx` bu commit'te olduğu gibi
  kalır. `dist/` yeniden derlenmez.
- **Kırmızı bırakılır.** `it.fails`/`skip` yok.
- Test adları ve yorumlar **İngilizce**; ekrandan okunan metinler Türkçe (arayüz Türkçe).
- Commit mesajında **çift tırnak yok**.
- Test komutu: `npm test --prefix queen-editor/frontend`

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `queen-editor/frontend/src/features/photo_generation/LayerPanel.test.jsx` | panelin seçimi nasıl anladığı | 3 test düzeltilir, 1 eklenir |
| `queen-editor/frontend/src/features/photo_generation/ProjectScreen.test.jsx` | galeri ile panel arasındaki dikiş | 1 describe eklenir |

---

### Task 1: Panel testleri seçimi kimlikle verir

**Files:**
- Test: `queen-editor/frontend/src/features/photo_generation/LayerPanel.test.jsx`

**Interfaces:**
- Consumes: dosyanın kendi `done()` yardımcısı (`id` = dosya adının uzantısız hâli), `FRAMES`,
  `renderPanel()`.
- Produces: yok.

- [ ] **Step 1: Üç testin seçim değerini kimliğe çevir**

`"follows the gallery's selection rather than keeping one of its own"` (satır ~40):

```js
    renderPanel({ selected: ["0_a"] });
```

`"counts a selected frame that already has a video"` (satır ~80):

```js
    renderPanel({ selected: ["1_a"] });
```

`"asks only for what is selected when that is the scope"` (satır ~100) — **girdi kimlik, beklenti
dosya adı olarak kalır**; testin bütün değeri bu ikisinin farkında:

```js
    renderPanel({ selected: ["0_a"], onQueue });

    await act(async () => { fireEvent.click(screen.getByText("Kuyruğa ekle")); });

    expect(onQueue).toHaveBeenCalledWith(["0_a.png"], 1);
```

- [ ] **Step 2: İkiz kare testini `LayerPanel — variants` describe'ının sonuna ekle**

```js
  it("counts the frame that was picked, not the one showing the same picture", () => {
    // Asking for a second video makes a copy frame, and the copy shows the same photo -- so a file
    // name cannot tell the two apart and an identity can. This is the whole reason the panel must
    // match on identity, and without this case the bug could be closed from the wrong end.
    const twin = { id: "0_a-2", file: "0_a.png", status: "done", layers: {}, failed: [] };

    renderPanel({ frames: [...FRAMES, twin], selected: ["0_a-2"] });

    expect(screen.getByText("Seçili kareler").closest("button").textContent).toContain("1");
  });
```

- [ ] **Step 3: Dördünün de düştüğünü gör**

Run: `npm test --prefix queen-editor/frontend`
Expected: `LayerPanel.test.jsx` içinde 4 düşen — üçü "Seçili kareler 0 diyor", biri ikiz karede aynı
sebep. Hiçbiri `ReferenceError`/`TypeError` değil.

---

### Task 2: Ekran testi dikişi sürükler

**Files:**
- Test: `queen-editor/frontend/src/features/photo_generation/ProjectScreen.test.jsx`

**Interfaces:**
- Consumes: dosyanın mevcut `vi.mock("../../shared/api.js")` kurulumu, `renderScreen()`,
  `listFrames`.
- Produces: yok.

- [ ] **Step 1: Yeni describe'ı dosyanın sonuna ekle**

```jsx
// The first test in this file that drives the gallery. Everything above renders the screen and
// reads it; this one uses it -- which is where the bugs turned out to live: each piece was tested
// against inputs handed to it by hand, and the wire between them by nothing at all.
describe("ProjectScreen — the gallery's selection reaches the video panel", () => {
  beforeEach(() => { vi.useFakeTimers(); });
  afterEach(() => vi.useRealTimers());

  const done = (file) => ({ id: file.replace(".png", ""), file, status: "done", layers: {},
                            owed: [], failed: [] });
  const FRAMES = [done("1_a.png"), done("0_a.png")];

  async function settle(ms = 0) {
    await act(async () => { await vi.advanceTimersByTimeAsync(ms); });
  }

  it("counts a frame picked in the gallery, and stops counting it when it is let go",
     async () => {
    listFrames.mockResolvedValue(FRAMES);
    renderScreen("seçim");
    await settle();
    fireEvent.click(screen.getByLabelText("Video üret"));
    // By identity, because that is what a tile is keyed by -- and the identity is the whole point
    // of this test.
    const ring = () => document.getElementById("tile-0_a").querySelector("[data-check]");
    const scope = () => screen.getByText("Seçili kareler").closest("button");

    await act(async () => { fireEvent.click(ring()); });

    expect(scope().textContent).toContain("1");

    await act(async () => { fireEvent.click(ring()); });

    // The second assertion needs the first: a count that is always 0 would pass this line alone.
    expect(scope().textContent).toContain("0");
  });
});
```

- [ ] **Step 2: Düştüğünü ve doğru sebeple düştüğünü gör**

Run: `npm test --prefix queen-editor/frontend`
Expected: bu test de düşer, ilk iddiada — `"Seçili kareler0"` içinde `"1"` yok. `tile-0_a` ya da
`Video üret` bulunamadığı için düşerse test yanlış yazılmıştır, önce o düzeltilir.

---

### Task 3: Kırmızıyı doğrula ve commit'le

- [ ] **Step 1: Tam ön yüz takımı**

Run: `npm test --prefix queen-editor/frontend`
Expected: 304 geçen, 5 düşen (307 + 2 yeni = 309).

- [ ] **Step 2: Backend'e ve `dist/`e dokunulmadığını doğrula**

Run: `git status --short`
Expected: yalnız iki test dosyası ve `docs/superpowers`.

- [ ] **Step 3: Commit**

```bash
git add queen-editor/frontend/src docs/superpowers
git commit -F - <<'EOF'
test(queen-editor): say which key the video panel matches a selection by

THESE FIVE TESTS FAIL ON PURPOSE. The fix is the next commit.

The gallery holds a selection by frame identity and the video panel compares it
against file names, so the count never moved off zero. Three of these tests are
older ones that handed the panel file names and agreed with it -- a test written
in the same breath as the code, agreeing with the code about the wrong thing.
They now hand identities, and go red for it.

The fourth is the case that explains why the distinction exists: asking for a
second video makes a copy frame showing the same photo, so a file name cannot
tell two frames apart. Without it, the bug could be closed from the wrong end.

The fifth is the first test in this repo to drive the gallery rather than read
it: click a tile, read the panel. That wire had no test at all, which is exactly
where the bug was.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** A1→Task 1 birinci düzeltme · A2→ikinci · A3→üçüncü · A4→Task 1 Step 2 ·
B1→Task 2. Spec'te olup planda olmayan vaka yok.

**Ad tutarlılığı:** `done()` yardımcısı iki dosyada ayrı ayrı tanımlı ve ikisi de `id`'yi dosya
adının uzantısız hâli yapıyor — `LayerPanel.test.jsx`'te zaten böyleydi, `ProjectScreen.test.jsx`'e
aynı kuralla ekleniyor, yani `0_a.png` → `0_a` ve tile'ın id'si `tile-0_a`.

**Sayı kontrolü:** bugün 307 geçiyor; iki test ekleniyor (309), beşi düşüyor → 304 geçen.

**Kırılganlık notu:** ekran testi `document.getElementById("tile-0_a")` ile kareyi buluyor. Bu, id
tabanlı ve galeri sırasından bağımsız; `getAllByTestId`/indeks kullanmak sıra değişince sessizce
başka kareyi seçerdi.
