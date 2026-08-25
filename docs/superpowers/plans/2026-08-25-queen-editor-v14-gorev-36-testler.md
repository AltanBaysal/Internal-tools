# v14 Görev 36 — Fotoğraf inerken karonun bekleme hâli: TEST döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bekleyen karonun halkasını sol üste düşürdüğünü ve arkasında ikinci bir gösterge
taşıdığını anlatan iki kırmızı test ile bir yeşil tutucuyu yazmak — kod hiç değişmeden.

**Architecture:** Tek dosya, tek blok. `TileImage.test.jsx`'in *what the tile shows* bloğuna üç test
giriyor; üçü de karoyu **galerinin verdiği style ile** çiziyor, çünkü hatayı doğuran şey o style'ın
içindeki `display: "block"`.

**Tech Stack:** React 18, Vite, Vitest + jsdom, @testing-library/react.

**Spec:** [Görev 36 test spec'i](../specs/2026-08-25-queen-editor-v14-gorev-36-testler-design.md)

## Global Constraints

- **Kod değişmiyor.** `frame_status.jsx` ve `TileImage.jsx` bu döngüde hiç açılmıyor. İki test
  kırmızı commit'lenir; `skip`/`xfail` yok.
- **Mevcut 16 testin cümlesi değişmiyor.** Yeni testler yalnız ekleniyor.
- **`vendor/styles.css` açılmıyor** — elle düzenlenmiyor.
- **Dil:** test kodu ve yorumlar **İngilizce**; commit mesajı **İngilizce**; belgeler **Türkçe**.
- **Commit mesajında çift tırnak yok** — PowerShell here-string'i kırıyor (CLAUDE.md).
- **Test komutu birebir:** `npm test --prefix queen-editor/frontend`. Boru yok, yönlendirme yok.
- **`dist` tazelenmiyor** — ön yüz kaynağı değişmiyor.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `queen-editor/frontend/src/features/photo_generation/TileImage.test.jsx` | karonun indirme protokolü ve neye benzediği | *what the tile shows* bloğuna üç test |

Tek dosya, yeni dosya yok. Bozuk olan bileşenin adı `Rendering` ve `frame_status.jsx`'te duruyor ama
o dosyanın kendi test dosyası hiç olmadı: `Rendering` bugün de `TileImage`, `Gallery` ve
`PhotoDetail` üzerinden test ediliyor. Yalnız bu iş için bir test dosyası açmak, kullanıcının
gördüğü şeyi — karoyu — anlatan bloktan uzağa yazmak olurdu.

---

### Task 1: Üç testi yaz, ikisini kırmızı gör, commit'le

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/TileImage.test.jsx:120-174`
  (*what the tile shows* bloğunun sonu)

**Interfaces:**
- Consumes: dosyada zaten duran yardımcılar — `holder()` (`document.querySelector(".wf-img")`),
  `turning()` (`.wf-spinner`), `picture()` (`getByAltText("1_a.png")`), `grant()`; ve dosyanın
  `beforeEach`'i, `queue` sahtesi, `shownPictures.clear()`.
- Produces: dışarıya bir şey değil. Bu üç testin iki kırmızısı, uygulama döngüsünün yeşile
  döndüreceği tam liste.

- [ ] **Step 1: Galerinin style'ını sabit olarak yaz**

`TileImage.test.jsx`'in yardımcılarının arasına — `releases` tanımının **altına**, `beforeEach`'in
**üstüne**:

```jsx
// The style the gallery really hands a tile. It is an img's style, and `display: block` is right
// for an img -- the holder that stands in for the picture is not one, and that is where this item's
// fault begins. Written out rather than imported: a test that reads the value from the code it
// tests cannot say the value is wrong.
const GALLERY_STYLE = { width: "100%", aspectRatio: "1/1", objectFit: "cover",
                        border: "1px solid var(--border)", borderRadius: "var(--r-sm)",
                        display: "block" };
```

- [ ] **Step 2: Üç testi bloğun sonuna ekle**

*what the tile shows* bloğunun son testi (*leaves a quiet holder where a picture never arrived*)
kapandıktan **sonra**, bloğun kendi `});`'inden **önce**:

```jsx
  it("keeps the ring in the middle of the tile, whatever shape the gallery asks for", () => {
    render(<TileImage project="düğün" file="1_a.png" style={GALLERY_STYLE} />);

    // The gallery's style is an img's, and it says display: block. The holder is a div whose whole
    // job is to centre the ring, and block takes the centring away -- the ring stops being a flex
    // item, falls back to inline, and an inline span is a box that width and height do not apply
    // to. That is the same fault twice over: the ring lands in the top left corner AND collapses
    // into a deformed arc. One assertion, because they have one cause.
    expect(holder().style.display).toBe("flex");
    expect(holder().style.alignItems).toBe("center");
    expect(holder().style.justifyContent).toBe("center");
  });

  it("waits on a calm ground rather than a striped one", () => {
    render(<TileImage project="düğün" file="1_a.png" style={GALLERY_STYLE} />);

    // Two indicators for one wait: diagonal stripes behind a turning ring. The stripes are how the
    // gallery says there are no pixels here -- a frame still queued, one that failed, a picture
    // that never came. Saying it behind a ring that says the opposite is what makes the tile noisy.
    expect(holder().style.backgroundImage).toBe("none");
    expect(holder().className).not.toContain("wf-img--loading");
  });

  it("leaves the stripes where they mean there are no pixels", () => {
    render(<TileImage project="düğün" file="1_a.png" style={GALLERY_STYLE} />);
    grant();

    fireEvent.error(picture());

    // The holder for a picture that never arrived keeps its stripes and loses its ring. Taking the
    // stripes from this one too would make the two states look alike again, from the other side.
    expect(holder().style.backgroundImage).toBe("");
    expect(turning()).toBeNull();
  });
```

`fireEvent` ve `grant` üçüncü testin ihtiyacı ve ikisi de dosyada zaten var — yeni bir içe aktarma
gerekmiyor.

- [ ] **Step 3: İkisinin kırmızı, birinin yeşil olduğunu gör**

Run: `npm test --prefix queen-editor/frontend`

Expected: `TileImage.test.jsx` **19 tests, 2 failed.** Düşenler:

- *keeps the ring in the middle of the tile, whatever shape the gallery asks for* — beklenen
  `"flex"`, gelen `"block"`. Galerinin style'ı `.wf-img`'in `display: flex`'ini eziyor ve satır içi
  style sınıfın önüne geçiyor.
- *waits on a calm ground rather than a striped one* — beklenen `"none"`, gelen `""`. Bugün hiçbir
  satır içi `backgroundImage` yok; çizgiyi `wf-img--loading` sınıfı boyuyor, ve o sınıf da orada.

Yeşil kalması gereken: *leaves the stripes where they mean there are no pixels*.

Dosyanın toplamı **19**, takımın toplamı **582** (bugünkü 579 + 3).

**İki değil üç düşerse dur.** Üçüncü test bugünün davranışını anlatıyor ve bugün doğrulamalı;
düşüyorsa yazılışında hata var.

- [ ] **Step 4: Arka yüz takımını da koştur**

Run: `python -m pytest queen-editor -q`

Expected: **711 passed.** Bu döngü arka yüze hiç dokunmuyor; koşulma sebebi CLAUDE.md'nin iki sabit
satırı.

- [ ] **Step 5: Değişen her şeyi gör**

Run: `git status --short`

Expected: `TileImage.test.jsx`, yol haritası, ve `docs/superpowers` altındaki iki yeni belge.
`frame_status.jsx`, `TileImage.jsx` ve `dist/` bu listede **olmamalı.**

Yol haritası listede çünkü 36. madde ona bu turda yazıldı — spec kaynağından türer, tersi değil.

- [ ] **Step 6: Commit**

```bash
git add queen-editor/frontend/src docs/superpowers
git commit -F - <<'EOF'
test(queen-editor): red for a ring that falls into the corner while it waits

A tile downloading its picture puts a turning ring on a holder, and the holder
is handed the img's own style -- the gallery's, which says display block,
because that is right for an img. The holder is not one. It is the div whose
whole job is to centre the ring, and block takes its centring away: the ring
stops being a flex item, falls back to inline, and width and height do not
apply to an inline span. It lands in the top left corner and collapses into a
deformed arc, which is one fault with one cause, not two.

Three tests, two of them red: the holder centres the ring whatever shape the
gallery asks for, and it waits on a calm ground. The second is the other half
of the complaint -- stripes behind a turning ring is two indicators for one
wait, and the stripes are already how the gallery says there are no pixels
here.

The green one is a holder. A picture that never arrived keeps its stripes and
loses its ring; taking the stripes from that one too would make the two states
look alike again, from the other side.

All three draw the tile with the style the gallery really hands it. No test in
this file passed a style before, so no test in it could have caught this: with
no style there is no display to override, and nothing breaks.

jsdom computes no layout, so no test can see a ring drawn round. It can read
the inline style, and that is exactly where the cause is -- a centring box
makes the ring a block level flex item and its size applies. Asserting the box
is asserting both halves at once, which is why there is one test and not two.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:**

| Spec'te ne diyor | Planda nerede |
|---|---|
| Halka sol üstte ve deforme — tek sebep | Task 1 Step 2, test 1 ve yorumu |
| Aynı anda çizgi ve halka | Task 1 Step 2, test 2 |
| Gelmeyen fotoğrafın çizgisi korunuyor | Task 1 Step 2, test 3 |
| Galerinin style'ı ile çağrılıyor | Task 1 Step 1 ve Step 2 |
| Bugünkü testlerin hiçbiri style geçirmiyor | Task 1 Step 6 commit mesajı |
| jsdom yerleşim hesaplamıyor, satır içi style okunuyor | Task 1 Step 2 test 1'in yorumu, commit mesajı |
| Halkanın varlığı için yeni test yok | Global Constraints (mevcut testler değişmiyor) |
| Kod değişmiyor | Global Constraints, Task 1 Step 5 |
| `vendor/styles.css` açılmıyor | Global Constraints |
| `dist` tazelenmiyor | Global Constraints, Task 1 Step 5 |

Spec'te olup planda karşılığı olmayan madde yok.

**Yer tutucu yok:** Her adımda çalıştırılacak gerçek kod ve gerçek komut var; beklenen sayılar
(16 → 19, 579 → 582, 711) ve beklenen hata değerleri (`"block"`, `""`) yazılı.

**Ad tutarlılığı:** `holder`, `turning`, `picture`, `grant`, `fireEvent` — hepsi dosyada bugün duran
adlar. `GALLERY_STYLE` yalnız bu dosyada geçiyor ve iki adımda aynı yazımla kullanılıyor; değerleri
`Gallery.jsx`'in `TileImage`'a verdiğinin birebir kopyası.

**Bilerek dışarıda:** `Gallery.test.jsx` ve `PhotoDetail.test.jsx`. İkisinin de bekleme hâli bugün
doğru çiziliyor — çağıranları `display` taşımayan bir style veriyor — ve bu iş onları değiştirmiyor.
