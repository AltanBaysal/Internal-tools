# Görev 7 — Galeri kartının durum dili · Uygulama Planı

> **Çalıştıran ajan için:** GEREKLİ ALT BECERİ: superpowers:executing-plans.

**Amaç:** Kartın ortasındaki durum yazıları kalkar; durum sol üstte tek kalıpta bir hap olur —
"foto kuyrukta" · "foto üretiliyor" · "foto hata".

**Mimari:** Yeni dosya `frame_status.jsx` bir karenin durumunun nasıl çizildiğini tutar: hap ve
yazısız üretim tutucusu. Galeri ikisini de, detay sayfası tutucuyu kullanır. Hapın imleçle yer
değiştirmesi `shared/app.css`'te.

**Yığın:** React 18 + Vite · vitest + jsdom.

**Spec:** [Görev 7 tasarımı](../specs/2026-08-12-queen-editor-v5-gorev-7-galeri-durum-dili-design.md)

## Global kısıtlar

- **Full TDD:** önce kırmızı test.
- **`vendor/` elle düzenlenmez** — kitin yükleme tutucusu kullanılmaz, kendi tutucumuz çizilir.
- Katman anahtarları arka ucun sözcükleri: `photo` · `video` · `audio`.
- Dil ayrımı: yorum/test adı/commit **İngilizce**, kullanıcı metni **Türkçe**.
- Test komutları: `npm test --prefix queen-editor/frontend -- --run` ·
  `python -m pytest queen-editor -q` · derleme `npm run build --prefix queen-editor/frontend`.
- **Tek commit**, görevin sonunda, `dist/` ile birlikte.

---

### Görev 1: Durum hapı doğar

**Dosyalar:**
- Oluştur: `queen-editor/frontend/src/features/photo_generation/frame_status.jsx`
- Değiştir: `queen-editor/frontend/src/features/photo_generation/Gallery.jsx` (Tile'a hap eklenir)
- Test: `queen-editor/frontend/src/features/photo_generation/Gallery.test.jsx`

**Arayüzler:**
- Üretir: `StatusPill({ layer, state })` — `data-pill` taşıyan bir `<span>` çizer; `state` `done`
  ya da tanınmayan bir değerse `null` döner.
- Üretir: `Rendering({ style })` — kitin yükleme tutucusunun sözcüksüz eşi.

- [ ] **Adım 1: Testleri yaz (kırmızı test)**

`Gallery.test.jsx` — "Gallery — one sequence, four states" bloğuna, dosyanın kendi `tileOf`
yardımcısını kullanarak:

```jsx
  const pillOf = (name) => tileOf(name).querySelector("[data-pill]");

  it("says the layer and the state in one pill, in the corner", () => {
    renderGallery({ frames: MIXED, current: "3_a.png" });

    expect(pillOf("4_a.png").textContent).toBe("foto kuyrukta");
    expect(pillOf("3_a.png").textContent).toBe("foto üretiliyor");
    expect(pillOf("2_a.png").textContent).toBe("foto hata");
  });

  it("gives a produced frame no pill -- the photo is the answer", () => {
    renderGallery({ frames: MIXED, current: "3_a.png" });

    expect(pillOf("1_a.png")).toBeNull();
  });

  it("never puts two pills on one frame", () => {
    renderGallery({ frames: MIXED, current: "3_a.png" });

    for (const frame of MIXED) {
      expect(tileOf(frame.file).querySelectorAll("[data-pill]").length).toBeLessThan(2);
    }
  });
```

- [ ] **Adım 2: Koş, kırmızıyı gör**

Koş: `npm test --prefix queen-editor/frontend -- --run`
Beklenen: üç FAIL — `[data-pill]` diye bir şey yok.

- [ ] **Adım 3: `frame_status.jsx`'i yaz**

```jsx
// How a frame's state is drawn. One mould for every layer: the pill says "<layer> <state>", so the
// video and audio rows below are the whole of what Blok 5-6 has to add here.
//
// The words are the design's; the keys are the server's own (layers.PHOTO / VIDEO / AUDIO), so a
// job's type can be handed straight to the pill without a translation table in between.
const LAYER_WORD = { photo: "foto", video: "video", audio: "ses" };
const STATE = {
  pending: { word: "kuyrukta", color: "var(--ink-3)", alive: false },
  running: { word: "üretiliyor", color: "var(--accent)", alive: true },
  failed: { word: "hata", color: "var(--danger)", alive: false },
};

const PILL = {
  position: "absolute", top: 6, left: 6, zIndex: 2,
  display: "flex", alignItems: "center", gap: 4,
  background: "rgba(10,8,7,.75)", borderRadius: 3, padding: "2px 5px",
  fontSize: 9, lineHeight: 1.4,
  // The corner is part of the card: a label must not turn it into a dead spot for drag or click.
  pointerEvents: "none",
};

/** The state pill, or nothing at all.
 *
 * A produced frame has no pill: the photo itself is the answer, and what it owns is said by the
 * badges in the opposite corner.
 */
export function StatusPill({ layer, state }) {
  const shown = STATE[state];
  if (!shown) return null;
  return (
    <span data-pill className="qe-pill wf-mono" style={{ ...PILL, color: shown.color }}>
      {shown.alive && (
        <span aria-hidden="true" className="qe-dot qe-dot--alive"
              style={{ background: "currentColor", width: 5, height: 5 }} />
      )}
      {LAYER_WORD[layer]} {shown.word}
    </span>
  );
}

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

- [ ] **Adım 4: Kartın köşesine as**

`Gallery.jsx` — import ve `Tile`'ın içine. `Tile` durumu bilmiyor, o yüzden hap `pill` adıyla
verilir:

```jsx
import { StatusPill } from "./frame_status.jsx";
```

`Tile`'ın imzasına `pill` eklenir ve `badge`in yanına çizilir:

```jsx
function Tile({ name, muted, danger, badge, pill, selected, onCheck, hint, children }) {
```

```jsx
        {pill}
        {selected && <div style={TINT} />}
```

Çağrı yerinde:

```jsx
                <Tile name={frame.file} badge={badge} muted={!produced}
                      danger={state === "failed"}
                      pill={<StatusPill layer="photo" state={state} />}
                      onCheck={state === "running" ? undefined : () => toggle(frame.file)}
```

- [ ] **Adım 5: Koş, yeşili gör**

Koş: `npm test --prefix queen-editor/frontend -- --run`
Beklenen: üç yeni test PASS; "bekliyor" sayan eski testler hâlâ PASS (orta yazı henüz duruyor).

---

### Görev 2: Kartın ortası susar

**Dosyalar:**
- Değiştir: `queen-editor/frontend/src/features/photo_generation/Gallery.jsx` (bekleyen ve çalışan
  hâller)
- Test: `queen-editor/frontend/src/features/photo_generation/Gallery.test.jsx:124-148`

- [ ] **Adım 1: Var olan üç testi hapın diline çevir (kırmızı test)**

```jsx
  it("draws a failed frame once, red, with its own way back", () => {
    const onRetry = vi.fn();
    renderGallery({ frames: MIXED, current: null, onRetry });

    // Once: not a red tile and a dashed one at the same time.
    expect(screen.getAllByText("foto kuyrukta")).toHaveLength(2);
    fireEvent.click(screen.getByText("Tekrar dene"));

    expect(onRetry).toHaveBeenCalledWith("2_a.png");
  });

  it("turns the frame the worker is holding into a spinner without moving it", () => {
    renderGallery({ frames: MIXED, current: "3_a.png" });

    // Four of the five are not photos; only the one the worker holds leaves the waiting pill.
    expect(screen.getAllByText("foto kuyrukta")).toHaveLength(1);
    expect(tileOf("3_a.png").textContent).toContain("4");
  });

  it("does not claim the gallery is empty when only waiting frames are in it", () => {
    renderGallery({ frames: [{ file: "0_a.png", status: "pending" }] });

    expect(screen.queryByText("henüz fotoğraf yok")).toBeNull();
    expect(screen.getByText("foto kuyrukta")).toBeTruthy();
  });
```

ve iki yeni test:

```jsx
  it("leaves the middle of a waiting card wordless -- the dashed border says it", () => {
    renderGallery({ frames: MIXED, current: "3_a.png" });

    expect(screen.queryByText("bekliyor")).toBeNull();
  });

  it("leaves the rendering card to the spinner alone", () => {
    renderGallery({ frames: MIXED, current: "3_a.png" });

    expect(screen.queryByText("Çalışıyor")).toBeNull();
    expect(tileOf("3_a.png").querySelector(".wf-spinner")).toBeTruthy();
  });
```

- [ ] **Adım 2: Koş, kırmızıyı gör**

Koş: `npm test --prefix queen-editor/frontend -- --run`
Beklenen: "bekliyor" ve "Çalışıyor" hâlâ ekranda olduğu için iki yeni test FAIL; `getAllByText`
çevrilen testler PASS (hap Görev 1'de geldi).

- [ ] **Adım 3: İki yazıyı da kaldır**

`Gallery.jsx` — çalışan hâl kendi tutucumuza geçer:

```jsx
import { Rendering, StatusPill } from "./frame_status.jsx";
```

```jsx
                    ) : state === "running" ? (
                      <Rendering style={{ aspectRatio: "1/1" }} />
```

bekleyen hâlin ortası boşalır:

```jsx
                    ) : (
                      /* Nothing in the middle: the dashed border already says there are no pixels,
                         and the corner's pill says what the frame is waiting for. */
                      <div className="wf-img" style={{ aspectRatio: "1/1", borderStyle: "dashed",
                                                       opacity: 0.35 }} />
                    )}
```

`ImgPH` kullanılmıyorsa kit import'undan düşer.

- [ ] **Adım 4: Koş, yeşili gör**

Koş: `npm test --prefix queen-editor/frontend -- --run`

---

### Görev 3: Detayın alanı da susar

**Dosyalar:**
- Değiştir: `queen-editor/frontend/src/features/photo_generation/PhotoDetail.jsx:7`, `:167-168`
- Test: `queen-editor/frontend/src/features/photo_generation/PhotoDetail.test.jsx:226-232`

- [ ] **Adım 1: Testi çevir (kırmızı test)**

```jsx
  it("spins instead of showing a photo, and lets nothing be pressed", async () => {
    await open("2_a.png", { frames: MIXED, status: RUNNING });

    expect(document.querySelector(".wf-spinner")).toBeTruthy();
    expect(screen.queryByText("Çalışıyor")).toBeNull();
    expect(screen.queryByText("henüz üretilmedi")).toBeNull();
    expect(screen.getByText("Kuyruktan çıkar").disabled).toBe(true);
  });
```

- [ ] **Adım 2: Koş, kırmızıyı gör**

Koş: `npm test --prefix queen-editor/frontend -- --run`
Beklenen: FAIL — "Çalışıyor" hâlâ orada.

- [ ] **Adım 3: Aynı tutucuyu kullan**

`PhotoDetail.jsx`:

```jsx
import { Btn, Hand, Icon, Mono, Note } from "../../vendor/kit.jsx";
import { Rendering } from "./frame_status.jsx";
```

```jsx
            ) : state === "running" ? (
              <Rendering style={HOLDER} />
```

- [ ] **Adım 4: Koş, yeşili gör**

Koş: `npm test --prefix queen-editor/frontend -- --run`

---

### Görev 4: Hap halkanın köşesinden çekilir

**Dosyalar:**
- Değiştir: `queen-editor/frontend/src/shared/app.css`

- [ ] **Adım 1: Kuralı yaz**

`app.css`'in sonuna:

```css
/* The state pill and the select ring want the same corner. The ring wins it whenever it is on
   screen -- under the pointer while browsing, and always while selection mode is open -- so the
   pill drops to the corner below instead of sitting under it. */
.qe-tile:hover .qe-pill,
.qe-tile--selecting .qe-pill {
  top: auto;
  bottom: 6px;
}
```

Test yok: imleç hâli JS'in bilmediği bir şey ve halkanın kendi görünürlüğü de aynı sebeple
test edilmiyor (bkz. `.qe-check`).

---

### Görev 5: Kapanış

- [ ] **Adım 1: İki takımı da koş**

Koş: `npm test --prefix queen-editor/frontend -- --run` → 14 dosya PASS
Koş: `python -m pytest queen-editor -q` → 371 PASS

- [ ] **Adım 2: Derle**

Koş: `npm run build --prefix queen-editor/frontend`

- [ ] **Adım 3: Tek commit**

```bash
git add -A
git commit -F - <<'MSG'
feat(queen-editor): a frame says its state in the corner, not across its middle

The only written state a card had sat in the middle of it, right where the
photo is about to appear -- so the card had to say "bekliyor" and then unsay
it. The middle is now left to the dashed border and the spinner, and the state
moves to a pill in the corner, where it can be read without being in the way.

The pill is one mould for every layer: it says "<layer> <state>", and the video
and audio rows are already written next to the photo one. What Blok 5-6 adds
here is a call, not a component.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
MSG
```

## Öz denetim

**1. Spec kapsaması:** Karar 1 (sözlük) → Görev 1; karar 2 (vendor) ve 4 (detay) → Görev 2-3;
karar 3 (tek dosya) → Görev 1'in `frame_status.jsx`'i; karar 5 (imleç) → Görev 4; karar 6
(`pointerEvents`) → Görev 1'in `PILL` stili. Kabul kriterinin altı maddesinden beşi testte, biri
(imleçle kayma) CSS'te ve gerekçesi spec'te.

**2. Yer tutucu taraması:** Yok.

**3. Tür tutarlılığı:** `StatusPill` ve `Rendering` adları üç görevde de aynı; `data-pill` ve
`qe-pill` Görev 1'de doğup Görev 4'te kullanılıyor; `layer="photo"` anahtarı `LAYER_WORD`'ün
anahtarıyla birebir.
