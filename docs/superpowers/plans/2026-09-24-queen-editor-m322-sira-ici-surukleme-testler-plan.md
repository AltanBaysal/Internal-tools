# Madde 322 — Sıranın içinde sürükleme, test turunun planı

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*. Takımı ve commit'i
> orkestratör koşuyor *(yol haritası, Kol A)*.

**Hedef:** Spec'in dört ekran testi — üçü kırmızı, biri bugün de geçen bekçi. Değişen test yok,
sunucu testi yok.

**Spec:** [m322 test turu](../specs/2026-09-24-queen-editor-m322-sira-ici-surukleme-testler-design.md)

## Her yere geçerli kurallar

- Test adı ve yorum **İngilizce**. Kaynak kod değişmiyor.
- Galerinin sürükleme testleri gibi: `fireEvent.dragStart` / `dragOver` / `dragEnd` doğrudan —
  React Testing Library onları zaten `act`'e sarıyor; yalnız `drop`, arkasından bir istek
  bekleyebileceği için `await act(async …)` içinde, dosyanın bugünkü sürükleme testi gibi.
- Yuva tek yerden tanınıyor: çizgisi `2px dashed var(--accent)` *(Gallery.jsx `SLOT`)*. `Ekle`
  kartının kendi çizgisi `1px dashed var(--border)`, yardımcıya takılmıyor.
- Bir yerin *"yer açması"* tarayıcının anlamıyla okunuyor: `dragOver`'ın varsayılanı iptal
  edildiyse orası bırakmayı kabul ediyor — `fireEvent` `dispatchEvent`'in dönüşünü veriyor.

---

## Görev 1: `ReferencePanel.test.jsx`

Dosyanın sonuna, 321'in bloğundan sonra. Dosyanın başındaki `open`, `pool` ve `saveReferenceOrder`
kullanılıyor; yeni import yok.

```js
describe("ReferencePanel — dragging within a row (madde 322)", () => {
  const tile = (container, name) => container.querySelector(`[data-reference="${name}"]`);
  const picture = (name, slot) => ({ name, kind: "picture", seconds: null, slot });
  const ROWS = pool([picture("bir.png", 1), picture("iki.png", 2),
                     { name: "dans.mp4", kind: "video", seconds: 4, slot: 1 }]);
  // The gallery's own slot: the dashed accent box a tile gives its place to (Gallery.jsx, SLOT).
  // The Ekle card's dashed line is 1px and the border's colour, so it is never taken for one.
  const slotIn = (element) => [element, ...element.querySelectorAll("*")]
    .find((one) => one.style.border === "2px dashed var(--accent)") ?? null;
  // A place is open where the browser is told a drop may land: the dragover's default is
  // cancelled. Anywhere else the browser shows no drop and never fires one.
  const opens = (element) => !fireEvent.dragOver(element);

  it("lifts the tile in flight the way the gallery does, until the drag ends", async () => {
    const { container } = await open(ROWS);

    fireEvent.dragStart(tile(container, "iki.png"));

    expect(tile(container, "iki.png").style.transform).toContain("rotate(-3deg)");
    expect(tile(container, "bir.png").style.transform).toBe("");

    fireEvent.dragEnd(tile(container, "iki.png"));

    expect(tile(container, "iki.png").style.transform).toBe("");
  });

  it("opens the gallery's dashed slot under the pointer, until the drag ends", async () => {
    const { container } = await open(ROWS);
    fireEvent.dragStart(tile(container, "iki.png"));

    expect(opens(tile(container, "bir.png"))).toBe(true);
    expect(slotIn(tile(container, "bir.png"))).toBeTruthy();

    fireEvent.dragEnd(tile(container, "iki.png"));

    expect(slotIn(container)).toBeNull();
  });

  it("opens no place in another row, and a drop there sends nothing", async () => {
    const { container } = await open(ROWS);
    fireEvent.dragStart(tile(container, "iki.png"));

    expect(opens(tile(container, "dans.mp4"))).toBe(false);
    expect(slotIn(container)).toBeNull();

    await act(async () => { fireEvent.drop(tile(container, "dans.mp4")); });

    expect(saveReferenceOrder).not.toHaveBeenCalled();
  });

  it("opens no place on the Ekle card, and a drop there sends nothing", async () => {
    // A row made into one drop zone -- to drop at its end, say -- would open a place on the card
    // too.
    const { container } = await open(ROWS);
    const card = container.querySelector('[data-add="picture"]');
    fireEvent.dragStart(tile(container, "iki.png"));

    expect(opens(card)).toBe(false);
    expect(slotIn(container)).toBeNull();

    await act(async () => { fireEvent.drop(card); });

    expect(saveReferenceOrder).not.toHaveBeenCalled();
  });
});
```

Bugün ne olacağı, test test:

1. `lifts …` — `iki`'nin `style.transform`'u `""`: `toContain("rotate(-3deg)")` düşer.
2. `opens the gallery's dashed slot …` — `opens(bir)` `true` *(bugün her kutu kabul ediyor)*;
   `slotIn(bir)` `null`: `toBeTruthy()` düşer.
3. `opens no place in another row …` — `dans.mp4`'ün `onDragOver`'ı `preventDefault` çağırıyor,
   `opens` `true`: `toBe(false)` düşer.
4. `opens no place on the Ekle card …` — kartta ve atalarında `onDragOver` yok; `drop`'u dinleyen de
   yok: geçer.

## Görev 2: Koşu ve kırmızı commit *(orkestratör)*

- [ ] Dört satır — vitest'te üç test kırmızı *(1–3)*, `opens no place on the Ekle card …` yeşil;
      `queen-editor` pytest'i ve `queen-agent` satırları yeşil.
- [ ] `test(m322): …(red)`.
