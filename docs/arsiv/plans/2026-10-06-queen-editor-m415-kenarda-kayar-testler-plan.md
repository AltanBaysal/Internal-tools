# Madde 415 — Kart sürüklenirken galeri kenarda kayar, test turunun planı

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*. Commit kendi dalında, kırmızı.

**Hedef:** Galeride bir kart sürüklenirken, imleç galerinin kutusunun alt kenarına yaklaşınca kutunun
aşağı, üst kenarına yaklaşınca yukarı kaydığını, kenarda durdukça kaymanın sürdüğünü, kenarlardan
uzakta durduğunu ve referans havuzunun bugünkü gibi kaldığını anlatan testler.

**Yaklaşım:** Ekran testi: `ProjectScreen` gerçek kutusu ve gerçek galerisiyle açılır. Kutunun
ekrandaki yeri sahte (`getBoundingClientRect`: üst 100, alt 700), kaydırma yeri 300'den başlar.
İmlecin yüksekliği `dragover` adlı bir `MouseEvent`'le gider — jsdom'da `DragEvent` yok.

**Araçlar:** vitest + jsdom, Testing Library, sahte saat.

**Spec:** [m415 test turu](../specs/2026-10-06-queen-editor-m415-kenarda-kayar-testler-design.md)

## Her yere geçerli kurallar

- Test adları ve yorumlar **İngilizce**.
- Testler dört satırla koşulur, paralel, yazıldığı gibi; `.skip` / `.todo` yok. Bu turda kaynak kod
  değişmiyor.
- Kenar 80 px, adım 20 px — testler bu sayılara bağlanmaz: kenarın 10 px içi ve kutunun ortası,
  hangi makul kenar seçilse de aynı cevabı verir.

**Arayüz — uygulama turunun vereceği:** `data-scroll` kutusu, galeri açıkken her `dragover`'da
`event.clientY`'yi kendi `getBoundingClientRect()`'inin `top` ve `bottom`'una göre tartar, ve
`scrollTop`'unu bir adım değiştirir. Havuz açıkken bunu yapmaz.

---

## Görev 1: `ProjectScreen.test.jsx` — beş test

**Dosya:** Değiştir: `queen-editor/frontend/src/features/photo_generation/ProjectScreen.test.jsx`
— dosyanın sonuna yeni bir `describe`. İçe aktarmalar değişmez: `act`, `fireEvent`, `screen`,
`listFrames`, `vi`, `poolServer`, `KEDI` ve `renderScreen` dosyada zaten var.

- [ ] **Adım 1: Dosyanın sonuna.**

```jsx
// Madde 415. The gallery's own box is what scrolls, and the reference pool stands in the same box --
// so both halves of the item are seen from the screen, not from the gallery alone.
describe("ProjectScreen — the gallery scrolls while a card is held at its edge (madde 415)", () => {
  beforeEach(() => { vi.useFakeTimers(); });
  afterEach(() => vi.useRealTimers());

  const done = (file) => ({ id: file.replace(".png", ""), file, status: "done", layers: {},
                            owed: [], failed: [] });
  const FRAMES = [done("2_a.png"), done("1_a.png"), done("0_a.png")];
  const boxOf = () => document.querySelector("[data-scroll]");
  const tileOf = (id) => document.getElementById(`tile-${id}`);

  async function settle() {
    await act(async () => { await vi.advanceTimersByTimeAsync(0); });
  }

  // The gallery open in a box whose top edge stands at 100 and bottom edge at 700, scrolled to 300.
  // jsdom lays nothing out, so where the box stands on screen is told; the scroll position it keeps
  // as it is given.
  async function open(project) {
    listFrames.mockResolvedValue(FRAMES);
    renderScreen(project);
    await settle();
    boxOf().getBoundingClientRect = () => ({ top: 100, bottom: 700 });
    boxOf().scrollTop = 300;
  }

  // jsdom has no DragEvent, and Testing Library's dragOver falls back to a plain Event that drops
  // clientY. A MouseEvent named dragover carries the pointer's height, and React reads it as a drag.
  function holdAt(element, clientY) {
    fireEvent(element, new MouseEvent("dragover", { bubbles: true, cancelable: true, clientY }));
  }

  it("scrolls down while the card is held near the bottom edge", async () => {
    await open("kenar-alt");
    fireEvent.dragStart(tileOf("1_a"));

    holdAt(tileOf("1_a"), 690);

    expect(boxOf().scrollTop).toBeGreaterThan(300);
  });

  it("scrolls up while the card is held near the top edge", async () => {
    await open("kenar-üst");
    fireEvent.dragStart(tileOf("1_a"));

    holdAt(tileOf("1_a"), 110);

    expect(boxOf().scrollTop).toBeLessThan(300);
  });

  it("goes on scrolling for as long as the card stays at the edge", async () => {
    // The browser repeats dragover while a drag is held still, so each one is another step.
    await open("kenar-sürer");
    fireEvent.dragStart(tileOf("1_a"));
    holdAt(tileOf("1_a"), 690);
    const once = boxOf().scrollTop;

    holdAt(tileOf("1_a"), 690);

    expect(once).toBeGreaterThan(300);
    expect(boxOf().scrollTop).toBeGreaterThan(once);
  });

  it("stands still while the card is away from both edges", async () => {
    await open("kenar-orta");
    fireEvent.dragStart(tileOf("1_a"));

    holdAt(tileOf("1_a"), 400);

    expect(boxOf().scrollTop).toBe(300);
  });

  it("leaves the reference pool as it is", async () => {
    // The pool's rows were not part of the ask (the user: "bu promplem değil").
    poolServer([KEDI]);
    await open("kenar-havuz");
    fireEvent.click(screen.getByLabelText("Video üret"));
    await act(async () => { fireEvent.click(screen.getByRole("button", { name: "Referanstan" })); });
    await settle();
    const card = document.querySelector('[data-reference="kedi.png"]');
    fireEvent.dragStart(card);

    holdAt(card, 690);

    expect(boxOf().scrollTop).toBe(300);
  });
});
```

## Görev 2: Koşu — kırmızı, commit

- [ ] **Adım 1: Dört satırı koş**, paralel, yazıldığı gibi:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: `queen-editor` vitest'inde üç yeni test kırmızı — *scrolls down*, *scrolls up*, *goes on
scrolling* (`scrollTop` 300'de kalıyor). *Stands still* ve *leaves the reference pool* yeşil. Öteki
her şey yeşil; öteki üç satır yeşil.

- [ ] **Adım 2: Commit** — testler, spec ve bu plan:

```powershell
git add docs/specs/2026-10-06-queen-editor-m415-kenarda-kayar-testler-design.md docs/plans/2026-10-06-queen-editor-m415-kenarda-kayar-testler-plan.md queen-editor/frontend/src/features/photo_generation/ProjectScreen.test.jsx
git commit -m @'
test(queen-editor): Madde 415 red -- the gallery scrolls while a card is held at its edge

Five screen tests on the real scroll box: down at the bottom edge, up at the top, on for as long
as the card stays there, still in the middle, and the reference pool as it is. The last two are
green today and lock it.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
