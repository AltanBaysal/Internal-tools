# v14 Görev 22 — Detayın görsel hizalaması: UYGULAMA döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Test döngüsünün bıraktığı 3 + 26 kırmızıyı yeşile döndürmek.

**Architecture:** Altı dosya — iki motor tarafında, dördü ön yüzde.

**Tech Stack:** Python 3, Flask; React 18, vite.

**Spec:** [uygulama turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-22-detay-hizalamasi-uygulama-design.md)

## Global Constraints

- **Test dosyaları bu döngüde değişmiyor.**
- Yorumlar **İngilizce**; ekran metni **Türkçe**.
- Commit mesajında **çift tırnak yok**, ve **amend yok**.
- Komut: dört satır, birebir, boru yok.
- **`dist` bu commit'te derleniyor.**
- Commit **yeşil gider**.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `backend/.../usecases/regenerate.py` | yeniden üretme kuralı | `negative` parametresi |
| `backend/.../presentation/routes.py` | gövdenin çevirisi | `negative` okunur |
| `frontend/.../shared/api.js` + `useGeneration.js` | isteğin taşınması | `negative` eklenir |
| `frontend/.../photo_generation/glyphs.jsx` | ekranın ikonları | `PauseGlyph` |
| `frontend/.../photo_generation/frame_status.jsx` | durum çizimleri | `Making` |
| `frontend/.../photo_generation/LayerPlayer.jsx` | oynatıcı | çubuk içeri, düğme çerçeveli |
| `frontend/.../photo_generation/PhotoDetail.jsx` | detay sayfası | sahne, düğmeler, metinler, kutular |
| `frontend/dist/` | not defterinin okuduğu çıktı | derlenir |

---

### Task 1: Motor negatifi taşıyor

**Files:**
- Modify: `queen-editor/backend/features/photo_generation/domain/usecases/regenerate.py`
- Modify: `queen-editor/backend/features/photo_generation/presentation/routes.py`

**Interfaces:**
- Produces: `regenerate(..., prompt, negative="", ...)`.

- [ ] **Step 1: İmza**

```python
def regenerate(runner, store, record, plan_store, order_store, producers, new_seed, now,
               project, fid, kind, prompt, negative="", log=None, writers=None,
               mode=production_mode.STANDARD):
```

Docstring'e bir paragraf:

```
    `negative` is the box's own words, the same way `prompt` is (Fark 98). Only a photo carries one:
    the layers over it are made from what is under them, so whatever is passed for a video or a
    sound is dropped here rather than at the caller.
```

- [ ] **Step 2: Satır**

```python
        "negative": negative if kind == layers.PHOTO else "",
```

- [ ] **Step 3: Yol**

```python
        prompt = body.get("prompt")
        negative = body.get("negative")
        try:
            # The frame is named by its identity: a copy frame shares its source's picture, so a
            # file name would not say which of the two was asked for. A non-string prompt counts as
            # no words at all -- what goes down is exactly what the user was shown, and the negative
            # travels the same way.
            frame = regenerate(project, body.get("frame"), layer,
                               prompt if isinstance(prompt, str) else "",
                               negative if isinstance(negative, str) else "",
                               mode=body.get("mode", production_mode.STANDARD))
```

---

### Task 2: İstek negatifi taşıyor

**Files:**
- Modify: `queen-editor/frontend/src/shared/api.js`
- Modify: `queen-editor/frontend/src/features/photo_generation/useGeneration.js`

- [ ] **Step 1: `api.js`**

```js
export async function regenerateFrame(project, frame, layer, prompt, mode, negative) {
  return request(`/api/projects/${encodeURIComponent(project)}/regenerate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ frame, layer, prompt, mode, negative }),
  });
}
```

- [ ] **Step 2: `useGeneration.js`**

```js
  const regenerate = useCallback((frame, kind, prompt, mode, negative) => (
    regenerateFrame(project, frame, kind, prompt, mode, negative)
```

---

### Task 3: İki çizim

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/glyphs.jsx`
- Modify: `queen-editor/frontend/src/features/photo_generation/frame_status.jsx`

**Interfaces:**
- Produces: `PauseGlyph({ size })`, `Making({ layer })`.

- [ ] **Step 1: `glyphs.jsx` sonuna**

```jsx
// Two bars: what the round button over the video shows while the clip is running.
export const PauseGlyph = ({ size }) => (
  <Glyph name="pause" size={size}>
    <path d="M5 2.5v9M9 2.5v9" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
  </Glyph>
);
```

- [ ] **Step 2: `frame_status.jsx`'e, `Rendering`'in yanına**

```jsx
/** What the stage says while a layer is made over a picture that is already there.
 *
 * The picture stays under it (Fark 113): for the length of a render it is the one thing left to
 * look at, and swapping it for a spinner took that away. A photo being made has no picture to keep
 * -- that one still gets `Rendering`.
 */
export function Making({ layer }) {
  return (
    <span data-making className="wf-mono"
          style={{ position: "absolute", top: "50%", left: "50%",
                   transform: "translate(-50%,-50%)", zIndex: 1,
                   display: "flex", alignItems: "center", gap: 6,
                   background: "rgba(10,8,7,.72)", borderRadius: 4, padding: "8px 14px",
                   fontSize: 12, color: "var(--accent)" }}>
      <span aria-hidden="true" className="qe-dot qe-dot--alive"
            style={{ background: "currentColor", width: 6, height: 6 }} />
      {LAYER_WORD[layer]} üretiliyor…
    </span>
  );
}
```

---

### Task 4: Oynatıcı videonun içine giriyor

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/LayerPlayer.jsx`

**Interfaces:**
- Produces: `data-scene`, `data-track`.

- [ ] **Step 1: Sabitler**

```jsx
const SCENE = { position: "relative", width: "100%", maxWidth: "calc(100% - 120px)",
                aspectRatio: "16/9", background: "#000", borderRadius: "var(--r-sm)",
                overflow: "hidden" };
// Fark 116: an outline and a darker ground, so the button reads as a button over any frame the
// video happens to be paused on. Written in longhands -- the shorthand is not reliably read back.
const BUTTON = { position: "absolute", top: "50%", left: "50%", transform: "translate(-50%,-50%)",
                 width: 64, height: 64, borderRadius: "50%",
                 borderWidth: 1, borderStyle: "solid", borderColor: "rgba(255,255,255,.35)",
                 background: "rgba(10,8,7,.72)", color: "#fff", cursor: "pointer",
                 display: "flex", alignItems: "center", justifyContent: "center", zIndex: 2 };
// Fark 114/115: the clock, the line and the waveform live inside the picture now, a little above
// its bottom edge, so the player reads as one thing rather than two stacked.
const TRACK = { position: "absolute", left: 12, right: 12, bottom: 10, zIndex: 1,
                display: "flex", alignItems: "center", gap: 10 };
// White with a shadow rather than the panel's faint ink: what is under these is a picture now, and
// a tone chosen for a flat surface disappears over half of them.
const CLOCK = { color: "#fff", textShadow: "0 1px 3px rgba(0,0,0,.8)" };
const UNPLAYED = "rgba(255,255,255,.35)";
```

- [ ] **Step 2: Render**

```jsx
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", width: "100%" }}>
      <div data-scene style={SCENE}>
        {/* Loops by itself: the design asks for a five second clip that keeps going round. */}
        <video ref={video} src={videoUrl} loop playsInline
               onPlay={() => setPlaying(true)} onPause={() => setPlaying(false)}
               onTimeUpdate={onTime}
               onLoadedMetadata={() => setLength(video.current?.duration || 0)}
               style={{ width: "100%", height: "100%", objectFit: "contain", display: "block" }} />
        {audioUrl && <audio ref={audio} src={audioUrl} loop />}
        <button type="button" aria-label={playing ? "Duraklat" : "Oynat"} onClick={toggle}
                style={BUTTON}>
          {playing ? <PauseGlyph size={22} /> : <PlayGlyph size={22} />}
        </button>

        <div data-track style={TRACK}>
          <Mono size={11} style={CLOCK}>{clock(at)}</Mono>
          {audioUrl ? (
            <div style={{ flex: 1, display: "flex", alignItems: "center", gap: 2, height: 24 }}>
              {Array.from({ length: BARS }, (_, bar) => (
                <span key={bar} data-bar
                      style={{ flex: 1,
                               // A flat bar is what an unread waveform looks like: still a progress
                               // strip, still not a shape anybody invented.
                               height: `${20 + 80 * (peaks ? peaks[bar] : 0.2)}%`,
                               borderRadius: 1,
                               background: bar / BARS <= done ? "var(--accent)" : UNPLAYED }} />
              ))}
            </div>
          ) : (
            /* No box around it: over a picture the contrast is the picture. */
            <div style={{ flex: 1, height: 4, borderRadius: 2, overflow: "hidden",
                          background: "rgba(255,255,255,.25)" }}>
              <div data-progress style={{ width: `${done * 100}%`, height: "100%",
                                          background: "var(--accent)" }} />
            </div>
          )}
          <Mono size={11} style={CLOCK}>{clock(length)}</Mono>
        </div>
      </div>
    </div>
  );
```

`import { PauseGlyph, PlayGlyph } from "./glyphs.jsx";` ekleniyor; `STAGE` ve `ROW` gidiyor.

---

### Task 5: Sahne

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/PhotoDetail.jsx`

**Interfaces:**
- Produces: `data-stage`.

- [ ] **Step 1: Ölçüler**

```js
// Fark 103: the strip and the picture used to crowd the same band. The top opens and the strip
// drops a little closer to it; the other three sides stay where they were.
const STAGE = {
  flex: 1, display: "flex", alignItems: "center", justifyContent: "center",
  padding: "48px 24px 24px",
  position: "relative", background: "var(--bg)", minHeight: 0,
};
```

```js
const STRIP = { position: "absolute", top: 12, left: "50%", transform: "translateX(-50%)",
                display: "flex", gap: 8, zIndex: 2 };
```

`<div style={STAGE}>` üç yerde geçiyor (yükleniyor, bulunamadı, asıl sahne); `data-stage` yalnız
asıl sahneye giriyor — testin ölçtüğü o, ve öteki ikisinde şerit hiç yok.

- [ ] **Step 2: Resim tek kalıptan**

`HOLDER`'ın altına:

```js
// contain, not a fixed ratio: the server does not know the photo's shape and it is never cropped.
const PICTURE = { maxWidth: "100%", maxHeight: "100%", width: "auto", height: "auto",
                  objectFit: "contain", display: "block" };
// 120px is the arrow gutter -- the picture and anything laid over it keep clear of both ends.
const FRAMED = { position: "relative", display: "flex", maxWidth: "calc(100% - 120px)",
                 maxHeight: "100%" };
```

- [ ] **Step 3: Üç dal**

```jsx
            ) : openState === "running" ? (
              produced ? (
                /* Fark 113: the picture stays and a box over it says what is being made. */
                <div style={FRAMED}>
                  <img src={fileUrl(project, frame.file)} alt={frame.file} style={PICTURE} />
                  <Making layer={open} />
                </div>
              ) : (
                /* A photo being made has no picture to keep: this is the holder's own case. */
                <Rendering style={HOLDER} />
              )
            ) : openState === "failed" ? (
              /* Madde 79: red border, red ground, and the renderer's own sentence under the two
                 words -- the one place the reason is readable. The heading is the ordinary face
                 and the reason is machine output, which is what it looks like (Fark 106). */
              <div className="wf-img" style={{ ...HOLDER, borderColor: "var(--danger)",
                                               background: "var(--danger-bg)",
                                               backgroundImage: "none", padding: 24 }}>
                <span style={{ color: "var(--danger)" }}><Icon.Warn /></span>
                <Note size={13} style={{ color: "var(--danger)" }}>Bu kare üretilemedi</Note>
                {(frame.errors || {})[open] && (
                  <Mono size={11} style={{ color: "var(--ink-2)", textAlign: "center",
                                           lineHeight: 1.5 }}>
                    {frame.errors[open]}
                  </Mono>
                )}
              </div>
            ) : produced ? (
              /* The picture the frame holds -- its own, or its source's when this is a copy waiting
                 for the layer above it (madde 81). */
              <div style={FRAMED}>
                <img src={fileUrl(project, frame.file)} alt={frame.file} style={PICTURE} />
              </div>
            ) : (
              /* Madde 82: the holder keeps the frame's own shape and its two lines are drawn
                 faintly -- a frame with no pixels yet is not an error, only not here yet. The word
                 is the heading and the sentence under it steps back (Fark 105). */
              <div data-holder className="wf-img"
                   style={{ ...HOLDER, borderStyle: "dashed", opacity: 0.45 }}>
                <Mono size={14} style={{ color: "var(--ink-3)" }}>bekliyor</Mono>
                <Note size={10} style={{ color: "var(--ink-4)" }}>henüz üretilmedi</Note>
              </div>
            )}
```

- [ ] **Step 4: Köşe**

```jsx
            {sent.length > 0 ? (
              <Corner>
                {/* Fark 107/108: one press opens a frame of its own and the other puts this one
                    back in line, and the corner used to say the same thing about both. */}
                <Pill color="var(--accent)" alive>
                  {retried ? "kuyrukta — tekrar denenecek" : "yeniden üretilecek — kuyrukta"}
                </Pill>
              </Corner>
            ) : coming ? (
              <Corner>
                {/* Fark 112: the stage is full of the source's picture and nothing said so
                    (karar 37). */}
                {produced && !ownsItsPhoto && (
                  <Pill color="var(--ink-2)">kaynak foto · kopya kare</Pill>
                )}
                <StatusPill layer={coming} state={running ? "running" : "pending"} />
              </Corner>
            ) : null}
```

`import { Corner, Making, Pill, Rendering, StatusPill } from "./frame_status.jsx";`

---

### Task 6: Basış, düğmeler ve pencereler

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/PhotoDetail.jsx`

- [ ] **Step 1: `DESTRUCTIVE` gövdesi bir kalıp**

```js
const DESTRUCTIVE = {
  video: { label: "Videoyu sil — kare kalır", title: "Video silinsin mi?",
           // Named rather than described: a frame carries more than one video across its history
           // and the window should say which one is going (Fark 101).
           body: (file) => `${file} ve üzerindeki ses kalıcı olarak silinir — bu geri alınamaz. `
                           + "Kare ve fotoğrafı galeride kalır." },
  audio: { label: "Sesi sil — video kalır", title: "Ses silinsin mi?",
           body: (file) => `${file} kalıcı olarak silinir — bu geri alınamaz. Video ve kare kalır; `
                           + "video sessiz oynar." },
};
// Red is a warning about what a press costs, and a press that cannot happen costs nothing
// (Fark 111).
const DANGER = { color: "var(--danger)", borderColor: "var(--danger)", background: "none",
                 justifyContent: "center" };
const bin = (off) => (off ? { justifyContent: "center" } : DANGER);
```

- [ ] **Step 2: Basışın hatırası**

```js
  // The layers already sent off, and how. A regenerate lands on a frame of its own and a retry on
  // this one, so the page sees neither arrive -- the button has to remember the press itself, and
  // the corner has to say which press it was (Fark 108).
  const [sent, setSent] = useState([]);
```

```js
  const wasSent = (layer) => sent.some((one) => one.layer === layer);
  const retried = sent.some((one) => one.retry);
```

`handleRegenerate`: `setSent((layers) => [...layers, { layer, retry: false }]);`
`handleRetry`: `setSent((layers) => [...layers, { layer, retry: true }]);`
Üç okuma yeri `sent.includes(open)` → `wasSent(open)`.

- [ ] **Step 3: Onay penceresi neyi sorduğunu biliyor**

`const [confirming, setConfirming] = useState(false);` →

```js
  // Which window is open, not merely that one is: a failed layer's way out deletes the FRAME while
  // a layer tab is open, and deciding from the open tab would show it the layer's words.
  const [asking, setAsking] = useState(null);              // "frame" | "layer" | null
```

`confirming` geçen her yer `asking`'e dönüyor: klavye etkisi (`if (asking) return;`), sıfırlama
etkisi (`setAsking(null)`), `handleRemove` ve `handleRemoveLayer` (`setAsking(null)`).

Pencere:

```jsx
      {asking === "frame" ? (
        <ConfirmModal title="1 kare silinsin mi?"
                      // The selection bar's own language: one window, one way of counting
                      // (Fark 102).
                      body={lostLayers(frame ? [frame] : []) + "Bu işlem geri alınamaz."}
                      confirmLabel="Sil" busyLabel="Siliniyor…" danger busy={busy}
                      onCancel={() => setAsking(null)} onConfirm={handleRemove} />
      ) : asking === "layer" ? (
        // Wider than the frame's own window (madde 80): these two say what survives the deletion,
        // and that sentence does not fit 320.
        <ConfirmModal title={DESTRUCTIVE[open].title}
                      body={DESTRUCTIVE[open].body((frame.layers || {})[open])} width={400}
                      confirmLabel="Sil" busyLabel="Siliniyor…" danger busy={busy}
                      onCancel={() => setAsking(null)} onConfirm={handleRemoveLayer} />
      ) : null}
```

- [ ] **Step 4: Yıkıcı düğme dört duruma açılıyor**

```jsx
              {/* One way out per tab (madde 80), and what it says is what the press costs. The
                  last two take the frame rather than the layer: the queue removes frames and not
                  layers, so there is no press behind a button that would leave one (karar 38). */}
              {open === "photo" ? (
                <Btn sm disabled={busy || state === "running"}
                     onClick={ownsItsPhoto ? () => setAsking("frame") : handleRemove}
                     style={bin(busy || state === "running")}>
                  <Icon.Trash /> {ownsItsPhoto
                    ? "Sil"
                    : (awaited ? "Kuyruktan çıkar" : "Kareyi sil")}
                </Btn>
              ) : holds ? (
                <Btn sm disabled={busy} onClick={() => setAsking("layer")} style={bin(busy)}>
                  <Icon.Trash /> {DESTRUCTIVE[open].label}
                </Btn>
              ) : openState === "pending" ? (
                /* Fark 99: the button lived on the photo tab alone, which is not the tab the user
                   is on while they wait for what it shows. */
                <Btn sm disabled={busy} onClick={handleRemove} style={bin(busy)}>
                  <Icon.Trash /> Kuyruktan çıkar
                </Btn>
              ) : openState === "failed" ? (
                /* Fark 100: a copy with no video is pointless, so the way out stands beside the
                   way back. It asks first when a file would really leave the disk. */
                <Btn sm disabled={busy}
                     onClick={ownsItsPhoto ? () => setAsking("frame") : handleRemove}
                     style={bin(busy)}>
                  <Icon.Trash /> Kareyi sil
                </Btn>
              ) : null}
```

- [ ] **Step 5: İki düğme metni ve boyu**

```jsx
              {holds && (
                /* Accent whether the prompt was touched or not (madde 78): making the frame again
                   is what this page is for. Full size, because the button under it is the way out
                   and the two used to be drawn as if they weighed the same (Fark 110). */
                <Btn hl disabled={wasSent(open) || Boolean(noTarget)}
                     onClick={handleRegenerate} style={{ justifyContent: "center" }}>
                  {wasSent(open)
                    ? "Kuyruğa eklendi"
                    : <><Icon.Regen /> Yeniden üret — yeni kare</>}
                </Btn>
              )}
```

```jsx
              {openState === "failed" && (
                /* The way back from a red layer, on the page it is read (madde 79). Retrying makes
                   no new frame -- it is the one exception to "üret = ekle" -- and the button says
                   so itself rather than leaving it to be found out (Fark 109). */
                <Btn sm hl disabled={wasSent(open)} onClick={handleRetry}
                     style={{ justifyContent: "center" }}>
                  {wasSent(open) ? "Kuyruğa eklendi" : <><Icon.Regen /> Tekrar dene — bu kareye</>}
                </Btn>
              )}
```

---

### Task 7: Kutular

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/PhotoDetail.jsx`

- [ ] **Step 1: Monospace**

`TextBlock` içindeki `<Note size={12} …>` → `<Mono size={12} …>`.

`PromptBox`'ın `className="wf-stroke wf-note"` → `className="wf-stroke wf-mono"`.

Gerekçe yorumu `PromptBox`'ın üstüne:

```jsx
// The visual language says a prompt box is monospace wherever it stands, and the production panel
// already reads that way -- the same words used to come out in two faces on two screens (Fark 117).
```

- [ ] **Step 2: Negatifin kendi hesabı**

`changed`'ın altına:

```js
  // The negative is the user's too now (Fark 98). Its own comparison rather than the prompt's: they
  // are two boxes and either one of them can be the thing that changed.
  const saidNegative = frame?.negative ?? "";
  const typedNegative = words.negative ?? saidNegative;
  const negativeChanged = typedNegative.trim() !== saidNegative.trim();
```

- [ ] **Step 3: Kutu**

```jsx
              {/* The negative belongs to the photo alone: video and sound jobs carry none. */}
              {open === "photo" && (
                <PromptBox label={`${LAYER_LABEL.photo} negatif prompt'u`}
                           value={typedNegative} changed={negativeChanged}
                           height={NEGATIVE_HEIGHT}
                           onChange={(text) => setWords((kept) => ({ ...kept, negative: text }))} />
              )}
```

- [ ] **Step 4: Gönderim**

```jsx
    return regenerate(frame.id, layer, typed, layer === "video" ? picked : undefined,
                      layer === "photo" ? typedNegative : undefined)
```

Yorumu:

```jsx
    // undefined off the video tab: a body with no mode is what the server has always read, and a
    // mode on a sound would be refused outright. The negative travels the other way round -- only
    // a photo is made from one.
```

- [ ] **Step 5: Dört komutu koştur**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Expected: dördü de yeşil — 384 / 474 / 697 / 519.

---

### Task 8: Derlenmiş çıktı ve yeşil commit

- [ ] **Step 1: Derle**

Run: `npm run build --prefix queen-editor/frontend`

- [ ] **Step 2: Yol haritasını işaretle**

22. maddenin **İş** hücresi ✅ ile başlar, sayaç `21/31` → `22/31`. E bölümü kapanır.

- [ ] **Step 3: Commit**

```bash
git add queen-editor docs/superpowers
git commit -F - <<'EOF'
feat(queen-editor): the detail page comes into line

Sixteen differences, one page, and the closing of section E.

The stage opens from the top and the strip drops toward it, so the tabs and the picture stop
crowding the same band. A waiting frame's two lines take a step apart and a failed frame's
two trade faces -- the heading reads as a heading and the renderer's own sentence reads as
what it is. A layer being made keeps its picture, with a dark box over it saying what is
coming; a photo being made still gets the holder, because it has no picture to keep.

The page stops saying the same thing about two different presses. Making a frame again
opens a frame of its own and retrying puts this one back in line, and both the corner and
the button now say which happened. That needed the record of a press to carry what it was,
so the list holds the layer and the kind together instead of the layer alone.

The way out reaches every tab. A queued layer's tab carries the button that leaves the
queue, and a failed layer's carries the way out beside the way back. Both of them take the
frame -- the queue removes frames and not layers -- and both ask first when a file would
really leave the disk. That last part is why the confirm now knows which window it is
rather than reading it off the open tab: a failed video's way out deletes the frame while
the video tab is open.

The two buttons stop weighing the same, a disabled delete drops its red, and the confirms
name what they are about to take -- the layer by its file, the frame by counting it the way
the selection bar does.

The negative becomes the user's. That reached the engine: the regenerate route carried no
negative and the use case wrote the source frame's onto the new line, so an accent border
would have promised a frame that never differed. Only a photo carries one, and a layer over
it drops whatever it is handed.

Both prompt boxes read monospace now, which is what the visual language always said and
what the production panel already did.

The player's clock, line and waveform move inside the video, the line loses its box, the
bars nobody has reached turn translucent white, and the round button gains an outline and a
drawn glyph in place of a text character.

dist built in this commit.

Four suites green.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** spec'in yedi bölümü Task 1+2 (1), Task 5 (2), Task 6 Step 2 (3), Task 6
Step 3+4 (4), Task 6 Step 1+5 (5), Task 7 (6), Task 3+4 (7).

**Tip tutarlılığı:** `DESTRUCTIVE[…].body` artık fonksiyon ve tek çağıranı var. `sent` artık
nesne listesi ve üç okuma yeri de `wasSent`'ten geçiyor.

**Kontrol edilen tuzak:** `regenerate`'in yeni parametresi `prompt`'tan sonra ve `log`'dan önce
geliyor. Mevcut çağıranların hepsi `log` ve `writers`'ı **ada göre** veriyor, `mode` da öyle —
konumsal veren tek yer yok, yani araya girmek kimseyi kaydırmıyor.

**Kontrol edilen tuzak 2:** `bin(off)` çerçevesiz bırakmıyor, `justifyContent`'i koruyup rengi
bırakıyor. `Btn`'in kendi sınıfı çerçeveyi zaten çiziyor.

**Kontrol edilen tuzak 3:** `Making` yalnız `produced` iken doğuyor. `openState === "running"`
tek başına yetmez: fotoğrafın kendisi üretilirken de doğrudur ve orada gösterilecek dosya yok.

**Kontrol edilen tuzak 4:** kopya kare etiketi `coming` dalında; `sent.length > 0` dalında değil.
Kullanıcı yeniden üret'e bastıysa köşede söylenecek şey bu değil.

**Koşuda çıkan tuzak 5: kırmızı turda düzeltilecek testleri eksik saymışım.** Beş test bu turda
düşürüldü ve hiçbiri uygulamanın kusuru değildi:

- **Üçü çağrı imzası.** `regenerateFrame` altıncı bir argüman aldı ve üç test onu `toHaveBeenCalledWith`
  ile beşle karşılaştırıyordu. Video sekmesinde altıncı argüman `undefined` — bir video negatiften
  yapılmaz — ve üç test bunu yazıyor. Bir imzayı büyütmek onu birebir eşleyen her testi ilgilendirir;
  kırmızı tur bunu listelemeliydi.
- **İkisi negatif kutusu.** Kutu yazılabilir olunca `getByText(/bulanık/)` ile bulunamaz oldu, ve
  boş bir kutunun "—"si kalktı — "—" salt okunur bir kutunun gösterecek şeyi olmadığında dediği şey.
  Birincisi kuralı düzeltince kendiliğinden geçti (aşağıya bakınız); ikincisinin ölçüsü
  değiştirildi: kutu var ve boş.

**Koşuda çıkan tuzak 6: negatif prompt gibi davranıyor, her zaman yazılabilir değil.** İlk yazışımda
kutu foto sekmesinde koşulsuz yazılabilirdi. Farkın cümlesi *"negatif de prompt gibi düzenlenir"*, ve
prompt yalnız katman gerçekten oradayken düzenlenebiliyor — bir kareyi yeniden üretmek için önce bir
kare olması gerekiyor. Kural `holds`'a bağlandı.

**Koşuda çıkan tuzak 7: `Making` testinin açtığı sekme yanlıştı.** Test foto sekmesinde kutuyu
arıyordu; oysa foto sekmesinde üretilen bir şey yok, kutu katmanın kendi sekmesine ait. Aynı test
işin adını `layer` diye veriyordu, kuyruğun kendi alanı ise `type`. İkisi de testin kusuru, ikisi de
düzeltildi.

**Koşuda çıkan tuzak 8: kırmızı turda bir testin son satırını yenisinin içine almışım.**
`test_a_regenerate_mode_nobody_knows_is_refused`'un `assert resp.get_json()["error"]` satırı yeni
testin gövdesine düşmüştü. Kırmızı tur bunu yakalamadı çünkü yeni test zaten ondan önceki satırda
düşüyordu. Satır sahibine geri verildi.

**Değişmeyen:** sekme şeridinin kendisi, oklar, klavye, sağ sütunun düzeni, hata kartları.
