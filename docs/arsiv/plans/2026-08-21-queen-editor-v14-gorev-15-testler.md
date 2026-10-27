# v14 Görev 15 — Galeri kartının görsel hizalaması: TEST döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Altı görsel farkı ölçen testleri yazmak, dördünü kararla kapatmak, takımı kırmızı
commit'lemek.

**Architecture:** İki test dosyası. Galeri karosunun dört köşesi, durum hapının kutusu ve hatalı
katmanın perdesi — hepsi zaten var olan `describe` bloklarının içine giriyor.

**Tech Stack:** vitest, @testing-library/react, jsdom.

**Spec:** [test turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-15-galeri-karti-testler-design.md)

## Global Constraints

- **Bu döngüde ürün kodu değişmiyor.** Yalnız test dosyaları ve belgeler.
- `skip` / `xfail` yok — kırmızı kırmızı commit ediliyor.
- Yorumlar **İngilizce**, ekran metni **Türkçe**.
- Commit mesajında **çift tırnak yok**, ve **amend yok**.
- Komut: dört satır, birebir, boru yok.
- Renk ve zemin ölçerken **rakamlar gevşek eşleniyor**: `rgba` yazımını tarayıcı normalleştiriyor,
  ölçülen şey tonun kendisi.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `.../photo_generation/Gallery.test.jsx` | karonun dört köşesi ve perdesi | 10 yeni, 1 silinen, 5 düzeltilen |
| `.../photo_generation/PhotoDetail.test.jsx` | sahnenin kendi köşe etiketi | 1 yeni |
| `research/…-tasarim-v4-farklari.md` | 28–31. kararlar | **yazıldı** |

---

### Task 1: Hapın kutusu ve iki katmanlı borç

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/Gallery.test.jsx`

**Interfaces:**
- Consumes: `Corner` kutusunun DOM işareti `data-corner`, hapın kendisi `data-pill` kalıyor.

- [ ] **Step 1: Köşe için yardımcı**

`pillOf`'un hemen altına (bugün 230. satır):

```jsx
  // The box the pills stand in. A frame can owe two layers, and the second label reads under the
  // first rather than beside it -- so the corner is a box of its own, not the pill's own position.
  const cornerOf = (name) => tileOf(name).querySelector("[data-corner]");
```

- [ ] **Step 2: Konumu ölçen iki testin adresini değiştir**

`puts the state pill in the top left, where the design asks for it` içinde üç `pillOf` → `cornerOf`,
ve yorumun sonuna bir cümle:

```jsx
    // The corner is the box now, not the pill: a frame can be waiting for two layers and both of
    // them stand in it (Fark 64).
    expect(cornerOf("4_a.png").style.top).toBe("6px");
    expect(cornerOf("4_a.png").style.left).toBe("6px");
    expect(cornerOf("4_a.png").style.bottom).toBe("");
```

`does not move the pill when the selection mode opens` içinde de aynısı:

```jsx
    renderGallery({ frames: MIXED, current: null });
    const before = cornerOf("4_a.png").style.top;

    fireEvent.click(checkOf("4_a.png"));

    expect(cornerOf("4_a.png").style.top).toBe(before);
    expect(cornerOf("4_a.png").style.top).toBe("6px");
```

- [ ] **Step 3: `never puts two pills on one frame` testini sil**

Kuralı 64. fark değiştiriyor. Yerine gelen üç test bir sonraki adımda.

- [ ] **Step 4: Borcun listeye dönmesi**

`gives a produced frame no pill -- the photo is the answer` testinin altına:

```jsx
  it("gives a frame that owes two layers a label for each", () => {
    renderGallery({ frames: [done("P0_0.png", { owed: ["video", "audio"] })], running: true });

    expect([...tileOf("P0_0.png").querySelectorAll("[data-pill]")].map((one) => one.textContent))
      .toEqual(["video kuyrukta", "ses kuyrukta"]);
  });

  it("stacks the second label under the first", () => {
    // In the queue's own order, which is the order owed already comes in: the labels read the way
    // the work will happen.
    renderGallery({ frames: [done("P0_0.png", { owed: ["video", "audio"] })], running: true });

    expect(cornerOf("P0_0.png").style.flexDirection).toBe("column");
    expect(cornerOf("P0_0.png").querySelectorAll("[data-pill]")).toHaveLength(2);
  });

  it("says one thing while a layer is being made, however much is still owed", () => {
    // Only the debt became a list. What the worker is holding is one job, and a card naming it
    // beside two more would bury the picture under it.
    renderGallery({ frames: [done("P0_0.png", { owed: ["video", "audio"] })],
                    current: "P0_0", currentLayer: "video", running: true });

    expect([...tileOf("P0_0.png").querySelectorAll("[data-pill]")].map((one) => one.textContent))
      .toEqual(["video üretiliyor"]);
  });
```

- [ ] **Step 5: Takımı koştur**

Run: `npm test --prefix queen-editor/frontend`
Expected: `stacks the second label under the first` ve iki konum testi `[data-corner]`
bulamadığı için, `gives a frame that owes two layers a label for each` de tek hap gördüğü için
kırmızı. `says one thing while a layer is being made` bugün de geçiyor.

---

### Task 2: Bekleyen hapın tonu ve ölçüsü

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/Gallery.test.jsx`

- [ ] **Step 1: Rengi söyleyen testi ters çevir**

`writes a waiting frame's label in the brightest ink there is` bütünüyle şununla değişiyor:

```jsx
  it("writes a waiting frame's label in a quieter ink than the ones that carry a colour", () => {
    // The design's soft tone, read as the palette's second grey rather than its third: the badge in
    // the opposite corner already carries that one at this very size, so it is the faint tone whose
    // readability this card has already proved. The other two states say what they are in colour.
    renderGallery({ frames: MIXED, current: "3_a" });

    expect(pillOf("4_a.png").style.color).toBe("var(--ink-2)");
    expect(pillOf("3_a.png").style.color).toBe("var(--accent)");
    expect(pillOf("2_a.png").style.color).toBe("var(--danger)");
  });
```

- [ ] **Step 2: Ölçüyü söyleyen testi ekle**

Hemen altına:

```jsx
  it("gives the label a lighter ground and more room inside it", () => {
    // Measure belongs to the mould and colour to the state: a stack of two must not show two
    // different grounds, so the ground and the padding change on every pill and the ink only on the
    // one the design speaks of. The digits are matched loosely -- what is fixed is the tone, not
    // how a browser spells it back.
    renderGallery({ frames: MIXED, current: "3_a" });

    expect(pillOf("4_a.png").style.background).toMatch(/10,\s*8,\s*7,\s*0?\.7\)/);
    expect(pillOf("4_a.png").style.padding).toBe("3px 7px");
  });
```

- [ ] **Step 3: Takımı koştur**

Run: `npm test --prefix queen-editor/frontend`
Expected: ikisi de kırmızı — bugünkü ton `var(--ink)`, zemin `.85`, iç boşluk `2px 5px`.

---

### Task 3: Sahiplik rozetleri

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/Gallery.test.jsx`

**Interfaces:**
- Consumes: rozet satırı `data-owns`, tek rozet `data-own`.

- [ ] **Step 1: Yardımcılar ve iki katmanlı kare**

`describe("Gallery — what a frame owns")`'un başına:

```jsx
  const ownsOf = (name) => tileOf(name).querySelector("[data-owns]");
  const badgesOf = (name) => [...tileOf(name).querySelectorAll("[data-own]")];
  const HAS_BOTH = withVideo("P0_0.png", {
    layers: { photo: "P0_0.png", video: "P0_0_V1_0.mp4", audio: "P0_0_V1_0_S1_0.wav" } });
```

- [ ] **Step 2: İkon bekleyen iki testten beklentiyi kaldır**

`marks a frame that has a video` içinden `expect(document.querySelector("[data-glyph=play]"))…`
satırı, `marks a frame that has a sound as well` içinden
`expect(document.querySelector("[data-glyph=sound]"))…` satırı siliniyor. İkinci test artık
`HAS_BOTH`'u kullanıyor:

```jsx
  it("marks a frame that has a sound as well", () => {
    renderGallery({ frames: [HAS_BOTH] });

    expect(screen.getByText("video")).toBeTruthy();
    expect(screen.getByText("ses")).toBeTruthy();
  });
```

- [ ] **Step 3: Üç yeni test**

```jsx
  it("puts what the frame owns in the bottom left, and leaves the corner across from it empty", () => {
    // Four corners, four meanings: the state pill top left, the number and the select ring top
    // right, what the frame owns bottom left. The fourth is left empty on purpose, so no two of
    // them ever land on each other.
    renderGallery({ frames: [withVideo("P0_0.png")] });

    expect(ownsOf("P0_0.png").style.bottom).toBe("6px");
    expect(ownsOf("P0_0.png").style.left).toBe("6px");
    expect(ownsOf("P0_0.png").style.right).toBe("");
  });

  it("writes the word by itself -- no icon rides with it", () => {
    renderGallery({ frames: [HAS_BOTH] });

    expect(screen.getByText("video")).toBeTruthy();
    expect(screen.getByText("ses")).toBeTruthy();
    expect(document.querySelector("[data-glyph=play]")).toBeNull();
    expect(document.querySelector("[data-glyph=sound]")).toBeNull();
  });

  it("gives each layer a box of its own", () => {
    // Two words inside one dark box read as one thing the frame has. Each layer carries its own
    // box, with a thin space between them.
    renderGallery({ frames: [HAS_BOTH] });

    expect(badgesOf("P0_0.png").map((one) => one.textContent)).toEqual(["video", "ses"]);
    expect(ownsOf("P0_0.png").style.gap).toBe("4px");
  });
```

- [ ] **Step 4: Takımı koştur**

Run: `npm test --prefix queen-editor/frontend`
Expected: üçü de kırmızı — bugün `data-owns` ve `data-own` yok, ve iki ikon yerinde duruyor.

---

### Task 4: Perde ve altındaki düğme

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/Gallery.test.jsx`

- [ ] **Step 1: Üç test**

`describe("Gallery — a layer that blew up")` içine, `offers the way back over the photo instead of
covering it` testinin altına:

```jsx
  it("brings the veil down in the app's own brown black", () => {
    // The tone every other label on this card already stands on, rather than a pure black that
    // belongs to no palette here. Only the tone changes; how much of the photo shows through does
    // not.
    renderGallery({ frames: [brokenVideo], onRetry: () => {} });

    expect(tileOf("P0_0.png").querySelector("[data-veil]").style.background)
      .toMatch(/10,\s*8,\s*7/);
  });

  it("stands the way back on the card's own ground", () => {
    renderGallery({ frames: [brokenVideo], onRetry: () => {} });

    expect(screen.getByText("Tekrar dene").closest("button").style.background).toBe("var(--bg-2)");
  });

  it("leaves the button on an empty red card without one", () => {
    // The ground belongs to the veil's button alone: this one already stands on a card of its own,
    // and a second ground would be a box drawn inside a box.
    renderGallery({ frames: [broken("P0_0.png")], onRetry: () => {} });

    expect(screen.getByText("Tekrar dene").closest("button").style.background).toBe("transparent");
  });
```

- [ ] **Step 2: Takımı koştur**

Run: `npm test --prefix queen-editor/frontend`
Expected: ilk ikisi kırmızı; üçüncüsü bugün de geçiyor.

---

### Task 5: Detay sayfasının kendi köşesi

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/PhotoDetail.test.jsx`

- [ ] **Step 1: Test**

`describe("PhotoDetail — a copy frame waiting in the queue")` içine, `shows the picture it holds and
says what is coming` testinin altına:

```jsx
  it("keeps the stage's own label in the corner", async () => {
    // The corner became a box of its own so the gallery could stack two labels in it (Fark 64).
    // This page shows one at a time -- and it has to be the same corner, or the label lands
    // wherever the stage's own flexbox puts it.
    await open("P0_1", { frames: [QUEUED_COPY] });

    const corner = document.querySelector("[data-corner]");
    expect(corner.style.top).toBe("6px");
    expect(corner.style.left).toBe("6px");
  });
```

- [ ] **Step 2: Dört komutu koştur**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Expected: üçü yeşil (384 / 474 / 694), queen-editor frontend'de **454 testin 12'si kırmızı**.

---

### Task 6: Kırmızı commit

- [ ] **Step 1: Commit**

```bash
git add queen-editor docs/superpowers
git commit -F - <<'EOF'
test(queen-editor): the gallery card's four corners, measured

Ten differences on one card. Six of them are drawn and get a test here: what the frame owns
moves to the bottom left, drops its icons and takes a box per layer; a frame that owes two
layers gets a label for each, stacked; the waiting label loses the brightest ink and gains
room; the veil turns the brown black every other label on the card already stands on, and
the way back under it stands on the card's own ground.

The pills' corner becomes a box of its own. Two labels cannot stack while the position
lives inside the pill, and the detail page shows one in the same corner -- so both screens
read it from one place. Two tests that measured the pill's own top and left now measure the
box.

Four are closed by decision instead, and the reasons are written into the v4 difference
list as 28 to 31. Hold to drag was removed on 14 August after the user reported the gallery
could not be dragged at all -- the browser decides at mousedown, so a tile armed later was
never a drag source. The number already leaves on hover; that rule was written on 13 August,
a week before the difference was observed. A drop does not start production: the engine
rereads the order every turn, so a frame pulled forward really is made from where it landed,
and a card claiming otherwise before the worker has it would be a lie. The mixed delete
confirm keeps only its title, which the user decided on 12 August.

Two of the new tests are green the day they are written. Both draw a boundary: one says the
debt becoming a list does not push aside the layer being made, the other that the card's
ground does not spread to every Tekrar dene. Neither is forced red -- what they measure is
true today and they will say so when it stops being.

454 tests, 12 red.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** spec'in altı çizilen farkı Task 1 (64), Task 2 (65), Task 3 (60, 61, 62),
Task 4 (75), Task 5 (64'ün detay sayfasındaki yüzü). Dört kararı belgeye yazıldı.

**Tip tutarlılığı:** `data-corner` kutunun, `data-pill` hapın; `data-owns` satırın, `data-own` tek
rozetin. Testler yalnız bu dört işareti kullanıyor.

**Kontrol edilen tuzak:** `rgba` yazımı. `style.background` tarayıcıya göre `rgba(10,8,7,.7)` ya da
`rgba(10, 8, 7, 0.7)` dönebiliyor; ölçüm bu yüzden düzenli ifade.

**Kontrol edilen tuzak 2:** `writes the word by itself` testi bugün var olan bir şeyi ölçüyor —
ikonun kendisini. `data-owns` içinde svg aramak bugün boş küme döndürür ve test doğuştan yeşil
olurdu.

**Kontrol edilen tuzak 3:** üç haplı bir kare yok. Fotoğrafı olmayan kareye katman kuyruğa
girmiyor, yani foto borcu ile katman borcu aynı karede buluşamıyor — testler iki katmanla
sınırlı, çünkü kod da öyle.

**Değişmeyen:** `frame_status.jsx`, `Gallery.jsx`, `app.css`. Bu döngüde ürün kodu yok.
