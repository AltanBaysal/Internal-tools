# Madde 399 — Ayrıntılar bölümü, test turunun planı

> **Koşum:** bu oturumda, satır satır. Takımı ve kırmızı commit'i maddeyi koşan ajan yapıyor
> *(yol haritası, Dalga 1)*.

**Hedef:** Spec'in altı yeni testi ve bölüme basan değişen testler — kırmızı; bir bekçi yeniden
yazımı yeşil.

**Spec:** [m399 test turu](../specs/2026-09-30-queen-editor-m399-ayrintilar-testler-design.md)

## Her yere geçerli kurallar

- Tek dosya: `queen-editor/frontend/src/features/photo_generation/PhotoDetail.test.jsx`. Kaynak kod
  değişmiyor.
- Test adı ve yorum **İngilizce**; ekrandaki sözler tasarımdan harfi harfine (*"Ayrıntılar"*).
- Uygulamanın tutacağı adlar bu planda sabitleniyor: düğmenin adı `Ayrıntılar`, açık mı —
  `aria-expanded`; bölüm `data-group="details"`, sütunun ikinci çocuğu; ok `[data-caret]`.

---

## Görev 1: İki yardımcı

`regenButton`'ın altına:

```js
// The row that folds the frame's facts away (madde 399), and the facts' labels in the order the
// column draws them -- the whole column's, or one part's.
const details = () => screen.getByRole("button", { name: "Ayrıntılar" });
const facts = (root = document) =>
  [...root.querySelectorAll("[data-field]")].map((one) => one.textContent);
```

## Görev 2: Yeni blok

*the layer tabs* bloğunun ardına, `SECOND_SOUND`'dan önce:

```js
describe("PhotoDetail — the details section (madde 399)", () => {
  // The owner found the column crowded: the counter stays on top, and what made the frame folds
  // away behind one row that starts closed -- the design's own (tasarım 200).
  it("opens the column with the counter alone and the section closed", async () => {
    await open("P0_0", { frames: [LAYERED] });

    expect(facts()).toEqual(["Sıra"]);
    expect(details().getAttribute("aria-expanded")).toBe("false");
    expect(screen.queryByText("Dosya adı")).toBeNull();
  });

  it("opens the frame's facts under the row on a press, and folds them on the next", async () => {
    await open("P0_0", { frames: [LAYERED] });

    fireEvent.click(details());

    expect(details().getAttribute("aria-expanded")).toBe("true");
    // Under the row, in the order they always had -- not back in the counter's group.
    expect(facts(document.querySelector('[data-group="details"]')))
      .toEqual(["Dosya adı", "Model", "LoRA"]);

    fireEvent.click(details());

    expect(details().getAttribute("aria-expanded")).toBe("false");
    expect(facts()).toEqual(["Sıra"]);
  });

  it("turns the caret up while the section is open", async () => {
    await open("P0_0", { frames: [LAYERED] });
    const caret = () => details().querySelector("[data-caret]");

    expect(caret().querySelector("svg")).toBeTruthy();
    expect(caret().style.transform).not.toContain("rotate");

    fireEvent.click(details());

    expect(caret().style.transform).toBe("rotate(180deg)");
  });

  it("keeps the section open when the tab changes", async () => {
    await open("P0_0", { frames: [{ ...LAYERED, modes: { video: "loop" } }] });
    fireEvent.click(details());

    fireEvent.click(tab("Video"));

    expect(details().getAttribute("aria-expanded")).toBe("true");
    // The video tab's own facts, each under the condition it always had.
    expect(facts()).toEqual(["Sıra", "Dosya adı", "Üretim modu"]);
  });

  it("keeps the section open while the arrows walk to another frame", async () => {
    // The arrows swap the frame under a page that stays mounted. The press was the user's, not
    // the frame's, so it walks on with them.
    listFrames.mockResolvedValue([LAYERED, SECOND]);
    getStatus.mockResolvedValue(IDLE);
    listModels.mockResolvedValue({ models: [], loras: LORAS });
    const { rerender } = render(<PhotoDetail project="düğün" frame="P0_0" />);
    await settle();
    fireEvent.click(details());

    rerender(<PhotoDetail project="düğün" frame="P1_0" />);
    await settle();

    expect(details().getAttribute("aria-expanded")).toBe("true");
    expect(screen.getByText("P1_0.png")).toBeTruthy();
  });

  it("draws the row as a label, with no box", async () => {
    await open("P0_0", { frames: [LAYERED] });

    // The column's own label face, and nothing drawn around it.
    expect(details().style.background).toBe("none");
    expect(screen.getByText("Ayrıntılar").style.textTransform).toBe("uppercase");
  });
});
```

## Görev 3: Bilgileri okuyan testler önce basar

Her birinde `await open(…)`'ın hemen altına `fireEvent.click(details());`. Beklentiler aynı.

- *the layer tabs*:
  - `keeps the frame's own name and its place on every tab` — yorumuna: *"Behind the details row
    since madde 399, which stays open across the tabs."*
  - `says which model the frame was made with`, `says a model by the name it was picked by`,
    `falls back to what the frame stored when the row list is not there`,
    `says which lora the frame was made with (madde 237)`, `it.each` *(madde 238)*,
    `draws no lora row for a frame that never named one`,
    `draws no model row for a frame that never carried one`,
    `keeps the model and the lora on the photo tab alone`.
- *how the video was made*: altı testin altısı.
- *PhotoDetail*: `shows the position, the file name and the prompt`.
- *a frame that is not a photo yet*: `calls the file name planned, and only for the frames that have
  no file`, `keeps the plain label on a produced photo`.

İki liste testi yeniden adlanır ve `facts()` okur:

```js
  it("keeps nothing else behind the row on the video tab", async () => {
    // Read as a list rather than one row at a time: naming the rows that went says nothing about
    // the rows that stayed, and what this item promises is the whole group.
    await open("P0_0", { frames: [LAYERED] });
    fireEvent.click(details());

    fireEvent.click(tab("Video"));

    expect(facts()).toEqual(["Sıra", "Dosya adı"]);
  });
```

```js
  it("keeps the photo tab's facts to their four rows", async () => {
    // The video tab's own list is pinned above. This is the photo tab's, and it pins the order too:
    // the model and its lora go last, behind the two rows that say which frame this is.
    await open("P0_0", { frames: [LAYERED] });
    fireEvent.click(details());

    expect(facts()).toEqual(["Sıra", "Dosya adı", "Model", "LoRA"]);
  });
```

## Görev 4: Bekçi — tabı soran test bölüme basmaz

`keeps the open tab when the next frame has that layer too`'nun son satırı:

```js
    expect(screen.getByText("1 / 2")).toBeTruthy();         // it really is the next frame
```

## Görev 5: Sütunun parçaları

```js
  it("splits the column into its facts, the section and what can be made of it", async () => {
    await open("P0_0", { frames: [LAYERED] });

    // Fark 91: what the frame is, then what can be made of it. No group heading and no rule
    // between them -- the split is where the eye rests, not a line it reads. Madde 399 folds what
    // made the frame into a section of its own between the two.
    const side = document.querySelector("[data-side]");
    expect([...side.children].map((one) => one.getAttribute("data-group")))
      .toEqual(["info", "details", "production"]);
  });

  it("keeps one vertical rhythm down the column", async () => {
    await open("P0_0", { frames: [LAYERED] });
    fireEvent.click(details());

    // Fark 91: three measures became two -- 16 between blocks, 6 between a label and what it
    // labels. The information group wraps on a 300px panel, so its own rows answer to the 16 too.
    // The details section keeps its rows 12 under its own row, and they wrap by the same 16.
    const side = document.querySelector("[data-side]");
    expect(side.style.gap).toBe("16px");
    expect(side.children[0].style.rowGap).toBe("16px");
    expect(side.children[1].style.gap).toBe("12px");
    expect(side.children[1].children[1].style.rowGap).toBe("16px");
    expect(side.children[2].style.gap).toBe("16px");
    expect(document.querySelector("[data-field]").parentElement.style.gap).toBe("6px");
  });
```

## Görev 6: Koşu ve kırmızı commit

- [ ] Dört satır, paralel. `queen-editor/frontend`: altı yeni test, Görev 3'ün 21'i ve Görev 5'in
      ikisi kırmızı *(düğme yok, bölüm yok)*; Görev 4'ün bekçisi yeşil. Öteki üç satır yeşil.
- [ ] `test(queen-editor): Madde 399 red -- …`.
