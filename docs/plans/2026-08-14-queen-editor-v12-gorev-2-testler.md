# v12 Görev 2 — Sürükleme: TEST döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Karonun **basıldığı anda** sürüklenebilir olmasını sınayan testleri yazmak ve takımı
kırmızı commit'lemek.

**Architecture:** Tek dosya, tek blok. `describe("Gallery — picking a tile up")` bugünkü tutuşu
sınıyor; tarayıcının gerçekte sorduğu şeyi sınayacak şekilde yeniden yazılıyor.

**Tech Stack:** React 18, vitest, jsdom.

**Tasarım:** [test spec'i](../specs/2026-08-14-queen-editor-v12-gorev-2-testler-design.md)

## Global Constraints

- **Bu döngüde üretim kodu değişmiyor.** `src/` altında `.test.jsx` dışında tek satır bile.
- Test adları ve yorumlar **İngilizce**.
- Commit mesajında **çift tırnak yok**.
- Komut: `npm test --prefix queen-editor/frontend`
- `dist/` **derlenmiyor** — ön yüz kodu değişmedi.
- Commit **kırmızı gider**.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `.../photo_generation/Gallery.test.jsx` | galerinin davranışı | bir `describe` bloğu değişir |

---

### Task 1: Tutuşu sınayan blok, basış anını sınayan blokla değişir

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/Gallery.test.jsx`

- [ ] **Step 1: `describe("Gallery — picking a tile up")` bloğunu tümüyle değiştir**

Blok bugün `beforeEach`/`afterEach` ile sahte zamanlayıcı kuruyor ve dört testi de basış + 250 ms
üstüne yazıyor. Tamamı şununla değişir:

```jsx
// The browser decides at mousedown whether a press may become a drag, so the only question worth
// asking is whether the tile is draggable BEFORE anything presses it. Arming it 250 ms later --
// which is what these tests used to check -- is a state the browser has already stopped looking
// for, and it is why the gallery could not be reordered at all (2026-08-14).
describe("Gallery — picking a tile up", () => {
  it("offers a tile to the drag before anything has touched it", () => {
    renderGallery();

    expect(tileOf("1_a.png").draggable).toBe(true);
  });

  it("does not make a press part of the gesture", () => {
    renderGallery();

    fireEvent.mouseDown(tileOf("1_a.png"));

    // Pressing wins the tile nothing it did not already have: that is how this says there is no
    // step between the press and the drag for a timer to sit in.
    expect(tileOf("1_a.png").draggable).toBe(true);
  });

  it("lifts a waiting frame too -- the drag is what decides when it is produced", () => {
    renderGallery({ frames: [pending("9_a.png"), done("0_a.png")] });

    expect(tileOf("9_a.png").draggable).toBe(true);
    expect(screen.queryByText("üretilince sıralanabilir")).toBeNull();
  });

  it("lifts a failed frame too", () => {
    renderGallery({ frames: [broken("9_a.png"), done("0_a.png")] });

    expect(tileOf("9_a.png").draggable).toBe(true);
  });

  it("lifts the frame the worker is holding, without asking it to stop", () => {
    renderGallery({ frames: [pending("9_a.png"), done("0_a.png")],
                    current: "9_a" });

    expect(tileOf("9_a.png").draggable).toBe(true);
  });

  it("lets nothing be dragged while a selection is open", () => {
    renderGallery();

    fireEvent.click(checkOf("0_a.png"));

    // One gesture cannot mean two things: while frames are being picked, a press is a pick.
    expect(tileOf("1_a.png").draggable).toBe(false);
  });
});
```

- [ ] **Step 2: Sahte zamanlayıcı artık kullanılmıyor mu, bak**

`vi.useFakeTimers` bu dosyada yalnız bu bloktaydı; blokla birlikte gitti. `act` başka testlerde
(silme onayı) kullanılıyor, import kalır.

- [ ] **Step 3: Ön yüz takımı**

Run: `npm test --prefix queen-editor/frontend`
Expected: 5 düşen — 1, 2, 3, 4, 5 numaralı testler `draggable` `false` gördüğü için. Altıncı
(seçim açıkken) geçer. Geri kalan takım yeşil.

---

### Task 2: Kırmızı commit

- [ ] **Step 1: Commit**

```bash
git add queen-editor/frontend/src docs/superpowers
git commit -F - <<'EOF'
test(queen-editor): ask whether a tile is draggable when it is pressed

Red on purpose -- the implementation cycle turns these green.

The gallery could not be reordered at all, and these tests said it could. They
pressed a tile, advanced a fake clock 250 ms, and then read the draggable
attribute -- by which time the browser has long since decided the press was a
text selection, not a drag. A test can measure the right thing at the wrong
moment and stay green for months.

So the block now asks what the browser asks: is this tile draggable before
anything touches it. Five of the six fail today, because a tile only becomes
draggable after it has been held.

The sixth stays green: nothing can be dragged while a selection is open. It
passes for the wrong reason today, since nothing can be dragged at all, and
becomes a real guard once the others go green.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** 1 → Step 1'in ilk testi · 2 → ikinci · 3, 4, 5 → kare durumları · 6 → seçim
kuralı. Eksik yok.

**Kontrol edilen tuzak:** `beforeEach(() => vi.useFakeTimers(...))` silinmezse blok sahte saat
altında koşmaya devam eder ve dosyadaki başka testlere sızabilir. Blokla birlikte gidiyor.

**Kontrol edilen tuzak 2:** altıncı test bugün de geçiyor ama **yanlış sebeple** — bugün hiçbir şey
sürüklenemiyor. Commit mesajı bunu söylüyor, yoksa yeşil bir test doğru şeyi koruyormuş gibi
okunur.

**Kontrol edilen kapsam:** `reports the new order when a frame is dropped` ve
`does not go to the server for a frame dropped where it already was` bloğun dışında ve
değişmiyor — bırakma tarafı çalışıyor.
