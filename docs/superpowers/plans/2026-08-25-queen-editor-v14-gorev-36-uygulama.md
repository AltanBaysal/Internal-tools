# v14 Görev 36 — Fotoğraf inerken karonun bekleme hâli: UYGULAMA döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Önceki commit'in iki kırmızı testini yeşile döndürmek, tutucuyu yeşil bırakarak.

**Architecture:** Tek dosya, tek bileşen. `Rendering` çağıranın style'ını önce, kendi yerleşimini
sonra yazıyor; çizgiyi boyayan sınıfı bırakıyor ve zeminini açıkça sakinleştiriyor.

**Tech Stack:** React 18, Vite, Vitest + jsdom.

**Spec:** [Görev 36 uygulama spec'i](../specs/2026-08-25-queen-editor-v14-gorev-36-uygulama-design.md)

## Global Constraints

- **Test dosyası değişmiyor.** `TileImage.test.jsx` bir önceki commit'te ne yazıldıysa o kalır.
- **`vendor/styles.css` açılmıyor** — elle düzenlenmiyor.
- **`TileImage.jsx` ve `Gallery.jsx` açılmıyor** — çare bileşende, çağıranda değil.
- **Çağıranın style'ı önce yazılır**, bileşenin kendi yerleşimi sonra. Sıra kararın kendisi.
- Dil: kod ve yorumlar **İngilizce**; commit mesajı **İngilizce**; belgeler **Türkçe**.
- Commit mesajında **çift tırnak yok** — PowerShell here-string'i kırıyor (CLAUDE.md).
- Test: `npm test --prefix queen-editor/frontend` · Derleme:
  `npm run build --prefix queen-editor/frontend` · **`dist` aynı commit'e girer.**

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `queen-editor/frontend/src/features/photo_generation/frame_status.jsx` | bir karenin hâlinin nasıl çizildiği | `Rendering`: yerleşim, zemin, yorum |

Tek dosya, tek fonksiyon. `Rendering`'in üç çağıranı var ve üçü de dokunulmadan doğru çalışıyor:
çare tam olarak bu yüzden burada.

---

### Task 1: `Rendering` kendi yerleşiminin sahibi olur

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/frame_status.jsx:117-128`

**Interfaces:**
- Consumes: `Rendering({ style })` — bugünkü imzanın aynısı. Değişmiyor.
- Produces: dışarıya yeni bir şey değil. Üç çağıran (`TileImage`, `Gallery`, `PhotoDetail`) aynı
  şekilde çağırmaya devam ediyor.

- [ ] **Step 1: Bileşeni ve yorumunu yaz**

Dosyanın 117–128. satırları bugün:

```jsx
/** The kit's loading holder without its word.
 *
 * vendor/ is never hand-edited, and the kit's own version writes "Çalışıyor" across the middle of
 * the card -- which is exactly what the design takes away. Same classes, same spinner, no words.
 */
export function Rendering({ style }) {
  return (
    <div className="wf-img wf-img--loading" style={style}>
      <span className="wf-spinner" style={{ position: "relative", zIndex: 1 }} />
    </div>
  );
}
```

Yerine:

```jsx
/** The kit's loading holder without its word, and without its stripes.
 *
 * vendor/ is never hand-edited, and the kit's own version writes "Çalışıyor" across the middle of
 * the card -- which is exactly what the design takes away. The spinner is the kit's; the ground is
 * not, because the kit's loading class paints diagonal stripes and this holder must not.
 *
 * Stripes are how the gallery says there are no pixels here: a frame still queued, one that failed,
 * a picture that never came. A ring says the opposite -- something is on its way. Saying both at
 * once left the two states telling one difference through the ring alone (madde 36).
 *
 * The caller's style is written first and the centring after it, so no caller can take the ring out
 * of the middle. That is not a hypothetical: the gallery hands a tile the img's own style, and an
 * img's style says display block. Block is right for an img and wrong for this box -- it stops the
 * ring being a flex item, the ring falls back to inline, and width and height do not apply to an
 * inline span. The ring landed in the top left corner as a deformed arc.
 */
export function Rendering({ style }) {
  return (
    <div className="wf-img"
         style={{ ...style, backgroundImage: "none",
                  display: "flex", alignItems: "center", justifyContent: "center" }}>
      <span className="wf-spinner" />
    </div>
  );
}
```

Üç değişiklik bir arada:

1. **`wf-img--loading` gitti** ve yerine `backgroundImage: "none"` geldi. Sınıf tek başına çıkarılsa
   `.wf-img`'in kendi gri çizgisi ortaya çıkardı. Aynı yol `Gallery.jsx`'in hata karosunda zaten
   kullanılıyor.
2. **Çağıranın style'ı önce, yerleşim sonra.** `...style` başta olduğu için ölçü, en boy oranı ve
   kenarlık çağıranın kalıyor; `display`/`alignItems`/`justifyContent` sonra yazıldığı için ortalama
   artık kimseye bırakılmıyor.
3. **Halkanın `position: relative, zIndex: 1`'i düştü.** Kaldırılan sınıfın kendi
   `position: relative; overflow: hidden` kuralının yanında anlamlıydı; o gidince halkanın üstünde
   duracağı bir şey kalmıyor. `Rendering`'in tek çocuğu o.

- [ ] **Step 2: Takımın tamamen yeşil olduğunu gör**

Run: `npm test --prefix queen-editor/frontend`

Expected: **0 failed**, 582 tests. Özellikle:

- `TileImage.test.jsx` **19 tests, 0 failed** — iki kırmızı yeşile döndü, tutucu yeşil kaldı.
- `Gallery.test.jsx` **112 tests, 0 failed** ve `PhotoDetail.test.jsx` **108 tests, 0 failed**.
  Diğer iki çağıran bu turda hiç açılmıyor ve `.wf-spinner`'ın varlığından başka bir şey iddia
  etmiyorlar.

*leaves the stripes where they mean there are no pixels* düşerse dur: `backgroundImage: "none"`
yanlışlıkla gelmeyen fotoğrafın kutusuna da uygulanmış demektir, ve o kutuyu `TileImage` çiziyor —
bu turda açılmaması gereken dosya.

- [ ] **Step 3: Ön yüzü derle**

Run: `npm run build --prefix queen-editor/frontend`

Expected: hatasız biter ve `queen-editor/frontend/dist/` tazelenir.

- [ ] **Step 4: Arka yüz takımının da yeşil olduğunu gör**

Run: `python -m pytest queen-editor -q`

Expected: **711 passed.** Bu döngü arka yüze hiç dokunmuyor; koşulma sebebi CLAUDE.md'nin iki sabit
satırı.

- [ ] **Step 5: Yol haritasını işaretle**

Modify: `docs/superpowers/plans/2026-08-20-queen-editor-v14-roadmap.md`

36. maddenin satırındaki iş adının başına `✅ ` ekle — 33, 34 ve 35'in satırlarındaki biçimin aynısı:

```
| 36 | ✅ **Fotoğraf inerken karonun bekleme hâli.** …
```

Aynı belgenin başlığındaki ilerleme sayısını da bir artır: `33/35` yazan yer `34/35` olur.

**Not:** Madde bu adımda kodda bitiyor ama turda bitmiyor — 30. maddenin Colab turu onu görecek.
33, 34 ve 35 için de aynısı yapıldı.

- [ ] **Step 6: Colab turu listesine satır ekle**

Modify: `docs/superpowers/plans/2026-08-24-queen-editor-v14-colab-turu.md`

`## 3 · Galeri ve seçim barı` bölümünde, 35'in satırının **altına**, aynı biçimde:

```markdown
- [ ] **İnerken bekleme hâli** (36). Çok kareli bir projede fotoğraflar inerken her karonun tam
      ortasında yuvarlak bir halka dönmeli — sol üstte ezilmiş bir yay değil — ve arkasında çapraz
      çizgi olmamalı. Çizgi yalnız piksel olmayan karolarda: kuyrukta bekleyen, hata almış, ve
      fotoğrafı hiç gelmeyen.
```

- [ ] **Step 7: Değişen her şeyi gör**

Run: `git status --short`

Expected: `frame_status.jsx`, `dist/` altındakiler, `docs/superpowers` altındaki iki yeni belge ve
iki değişen belge. `TileImage.test.jsx`, `TileImage.jsx` ve `Gallery.jsx` bu listede **olmamalı.**

- [ ] **Step 8: Commit**

```bash
git add queen-editor/frontend/src queen-editor/frontend/dist docs/superpowers
git commit -F - <<'EOF'
feat(queen-editor): the waiting tile holds its ring in the middle

The holder a downloading tile draws now owns its own centring, and waits on a
calm ground.

The gallery hands a tile the img's own style, and an img's style says display
block. That is right for an img and wrong for the div that stands in for one
while the picture is on its way: the div's whole job is to centre the ring, and
block took the centring away. The ring stopped being a flex item, fell back to
inline, and width and height do not apply to an inline span -- so it landed in
the top left corner as a deformed arc. One cause, both halves of the complaint.

Fixed in the component rather than in the caller. The caller was not wrong; the
same style was being used for two things, one of them not an image. Rendering
has three callers and a fourth would fall into the same hole, and asking
TileImage to split a style into the parts a holder may have would put the shape
of a picture in two places. A thing that centres should own its centring.

The stripes go with it. They are how the gallery says there are no pixels here
-- a frame still queued, one that failed, a picture that never came -- and
saying that behind a ring that says the opposite left one difference resting on
the ring alone. Now stripes mean no pixels and a ring means something is
coming.

Dropping the kit's loading class would have uncovered the plain grey stripes
underneath it, so the ground is turned off outright. The failed tile next door
already does exactly that.

The ring loses a position and a z-index that meant something beside the class
that was removed. Nothing is left for it to stand over: it is this holder's
only child.

The two callers that were never broken keep working, and lose their stripes
too. Their style is written first, so the detail page's column and gap survive.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:**

| Spec'te ne diyor | Planda nerede |
|---|---|
| Çağıranın style'ı önce, yerleşim sonra | Task 1 Step 1, değişiklik 2 |
| Çare çağıranda değil bileşende | Task 1 Step 1'in yorumu, Global Constraints, commit mesajı |
| `wf-img--loading` gidiyor, `backgroundImage: none` geliyor | Task 1 Step 1, değişiklik 1 |
| Halkanın `zIndex`'i düşüyor | Task 1 Step 1, değişiklik 3 |
| Yorum düzeltiliyor | Task 1 Step 1 |
| Diğer iki çağıran bozulmuyor | Task 1 Step 2'nin beklentisi |
| Test dosyası değişmiyor | Global Constraints, Task 1 Step 7 |
| `vendor/styles.css` açılmıyor | Global Constraints |
| Derlenmiş çıktı aynı commit'te | Task 1 Step 3 ve Step 8 |

Spec'te olup planda karşılığı olmayan madde yok. Yol haritası ve Colab turu adımları spec'te değil,
CLAUDE.md'nin numaralandırma ve tur kuralından geliyor.

**Yer tutucu yok:** Tek adımda çalıştırılacak gerçek kod, diğerlerinde gerçek komut var; beklenen
sayılar (19, 582, 711, 112, 108) yazılı.

**Ad tutarlılığı:** `Rendering`, `wf-img`, `wf-img--loading`, `wf-spinner` — hepsi depoda bugün duran
adlar ve planın her yerinde aynı yazımla geçiyor. Bileşenin imzası (`{ style }`) değişmiyor,
dolayısıyla çağıranlarla arasında uyumsuzluk doğacak bir yer yok.

**Bilerek dışarıda:** `TileImage.jsx`, `Gallery.jsx`, `PhotoDetail.jsx` ve `vendor/styles.css`.
Gerekçeleri spec'te.
