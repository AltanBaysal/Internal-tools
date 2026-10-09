# v14 Görev 12 — Toplu katman silme: UYGULAMA döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Test döngüsünün bıraktığı 18 testi yeşile döndürmek: gövde kuralı ortak eve, `remove_layer`
çoğula, bara iki düğme ve iki pencere.

**Architecture:** Aşağıdan yukarı üç tur — ortak kural, iş, ekran. Python takımı ancak ilk turdan
sonra **toplanabiliyor**, testlerin gerçek sebeplerini ilk kez orada görüyoruz.

**Tech Stack:** Python 3 + Flask, React 18 + vite.

**Spec:** [uygulama turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-12-toplu-katman-silme-uygulama-design.md)

## Global Constraints

- **Test dosyaları bu döngüde değişmiyor — bir ölçüm düzeltmesi dışında.** Pencereyi iptal eden
  test `getByText("Vazgeç")` diyordu; pencere açıkken ekranda iki tane var — barınki ve
  pencereninki — ve testin bastığı pencerenin olanı. `getAllByText(…).at(-1)` oluyor, `Sil`
  için zaten kullanılan deyimin aynısı. Kaynak doğru; ölçüm hangi düğme olduğunu söyleyemiyordu.
- Yorumlar ve kod **İngilizce**; ekran metni ve hata cümleleri **Türkçe**.
- Commit mesajında **çift tırnak yok**, ve **amend yok**.
- Komut: dört satır, birebir, boru yok.
- **`dist` bu commit'te derleniyor.**
- Commit **yeşil gider**.
- Hata cümleleri: `Silinecek kare listesi metin dizisi olmalı.` ·
  `Kopyalanacak kare listesi metin dizisi olmalı.` · `Katmanı silinecek kare listesi metin dizisi
  olmalı.`
- Ekran cümleleri birebir: `9 karenin videosu silinsin mi?` · `9 karenin sesi silinsin mi?` ·
  `Kareler ve fotoğrafları kalır. Videoya bindirilen sesler de gider.` ·
  `Kareler, fotoğrafları ve videoları kalır.` ·
  `Seçili 12 kareden videosu olmayan 3 kare atlanır. `
- **Detay sayfasının kendi pencereleri değişmiyor** — yalnız çağrısı listeye dönüyor.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `backend/features/photo_generation/domain/frame_list.py` | kimlik listesinin kuralı | **yeni** |
| `…/domain/usecases/remove_frames.py` | silme | `checked` |
| `…/domain/usecases/copy_frames.py` | kopyalama | `checked` |
| `…/domain/usecases/remove_layer.py` | katman silme | çoğul imza, tek geçiş |
| `…/presentation/routes.py` | rotalar | gövde, 400 |
| `frontend/src/shared/api.js` | çağrı | liste |
| `…/photo_generation/useGeneration.js` | kanca | imza |
| `…/photo_generation/PhotoDetail.jsx` | tek kare | `[frame.id]` |
| `…/photo_generation/ProjectScreen.jsx` | bağlanma | `onRemoveLayer` |
| `…/photo_generation/layer_words.js` | sözler | `LAYER_ACTIONS`, `layerConfirm` |
| `…/photo_generation/Gallery.jsx` | bar ve pencereler | dört değişiklik |
| `frontend/dist/` | not defterinin okuduğu çıktı | derlenir |

---

### Task 1: Gövde kuralı ortak eve

**Files:**
- Create: `queen-editor/backend/features/photo_generation/domain/frame_list.py`
- Modify: `…/domain/usecases/remove_frames.py`
- Modify: `…/domain/usecases/copy_frames.py`
- Modify: `…/presentation/routes.py`

**Interfaces:**
- Produces: `InvalidFrames`, `checked(frames, what) -> list`. Task 2 ikisini de okuyor.

- [ ] **Step 1: Modülü yaz**

```python
"""The list of frame identities a request carries, and the one rule it has to keep.

Three calls take one: deleting frames, copying them, and taking a layer off them. The rule is the
same for all three and the sentence differs only in what was being asked for, so both live here --
a second copy would drift the moment one of them was reworded.
"""


class InvalidFrames(Exception):
    """The body was not a list of frame identities (the message is user-facing)."""


def checked(frames, what):
    """`frames` back when it is a list of identities; InvalidFrames naming the ask otherwise."""
    if not isinstance(frames, list) or any(not isinstance(fid, str) for fid in frames):
        raise InvalidFrames(f"{what} kare listesi metin dizisi olmalı.")
    return frames
```

- [ ] **Step 2: İki kullanım durumunu ona bağla**

`remove_frames.py`: `InvalidFiles` sınıfı siliniyor, denetim satırı
`checked(frames, "Silinecek")` oluyor, içe aktarma listesine `frame_list` giriyor.

`copy_frames.py`: aynısı, `checked(frames, "Kopyalanacak")`.

- [ ] **Step 3: Rotayı düzelt**

`routes.py`: `copy_frames`'ten gelen `InvalidFrames` ve `remove_frames`'ten gelen `InvalidFiles` içe
aktarmaları yerine tek satır:

```python
from backend.features.photo_generation.domain.frame_list import InvalidFrames
```

Silme rotasındaki `except InvalidFiles` → `except InvalidFrames`.

- [ ] **Step 4: Takımı koştur**

Run: `python -m pytest queen-editor -q`
Expected: dosyalar toplanıyor; `remove_layer`'ı çağıran testler kırmızı — imza henüz tekil.

---

### Task 2: Katman silme çoğullaşıyor

**Files:**
- Modify: `queen-editor/backend/features/photo_generation/domain/usecases/remove_layer.py`
- Modify: `queen-editor/backend/features/photo_generation/presentation/routes.py`

**Interfaces:**
- Consumes: Task 1'in `checked`'i.
- Produces: `remove_layer(record, store, plan_store, order_store, now, project, frames, kind)` →
  `{"deleted": [...]}`.

- [ ] **Step 1: Başlığı ve gövdeyi yaz**

Modülün docstring'i iki paragraf kazanıyor (tekil→çoğul, ve neden tek geçiş), `FrameMissing` içe
aktarması gidiyor, `frame_list.checked` geliyor. Gövde:

```python
def remove_layer(record, store, plan_store, order_store, now, project, frames, kind):
    """Returns what really left the disk: {"deleted": [file names]}.

    Frames are named by their identities rather than by files: a copy frame shares its source's
    picture (madde 102), so one file name can belong to two frames and only one of them is losing
    its video.
    """
    checked(frames, "Katmanı silinecek")
    # Raises ProjectMissing when there is no such project.
    gallery = {frame["id"]: frame
               for frame in list_frames(record, store, plan_store, order_store, project)}
    slots = record.slots(project)
    over = queue.ORDER[queue.ORDER.index(kind):]      # the layer itself and everything above it

    # The whole press is decided first: which slots close, and which jobs above them never get to be
    # made. Deciding it frame by frame would answer a shared file wrong -- the second frame would
    # still see the first one holding it.
    closing, dropping = set(), []
    for fid in frames:
        frame = gallery.get(fid)
        if frame is None:
            continue
        cells = slots.get(fid, {})
        closing |= {(fid, slot) for slot in over
                    if layers.is_taken((cells.get(slot) or {}).get("status"))}
        # A job the queue still owes above the closed layer would go looking for a video that is no
        # longer there. The name written down is the one it would have taken.
        dropping += [(fid, slot, layer_file(slot, fid, (cells.get(layers.VIDEO) or {}).get("file")))
                     for slot in over if slot in frame.get("owed", [])]

    deleted = sorted(layers.files_to_unlink(slots, closing))
    for name in deleted:
        store.delete(project, name)
    for fid, slot in sorted(closing):
        record.mark(project, fid, slot, slots[fid][slot]["file"], queue.DELETED, now())
    for fid, slot, name in dropping:
        record.mark(project, fid, slot, name, queue.REMOVED, now())
    return {"deleted": deleted}
```

- [ ] **Step 2: Rotayı çoğullaştır**

```python
        try:
            # What really left the disk goes back: a layer the frame did not carry costs nothing and
            # is not an error, and neither is a name the gallery no longer knows.
            return jsonify(remove_layer(project, body.get("frames"), kind))
        except InvalidFrames as exc:
            return jsonify({"error": str(exc)}), 400
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404
        except OSError as exc:
            # The operating system's own words -- never guess the cause.
            return jsonify({"error": str(exc)}), 500
```

- [ ] **Step 3: Takımı koştur**

Run: `python -m pytest queen-editor -q`
Expected: python takımının tamamı yeşil.

---

### Task 3: Sözler

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/layer_words.js`

**Interfaces:**
- Produces: `LAYER_ACTIONS`, `layerConfirm(layer, held, selected) -> {title, body, width}`. Task 4
  ikisini de okuyor.

- [ ] **Step 1: İki şeyi ekle**

Dosyanın sonuna:

```js
// What the bar's two layer buttons say, and what each one's window promises. Here beside the
// counting sentence for the reason that one is here: the tile's badges and every window that names
// a layer have to be using one set of words.
export const LAYER_ACTIONS = [
  { layer: "video", label: "Videoları sil", noun: "videosu",
    stays: "Kareler ve fotoğrafları kalır. Videoya bindirilen sesler de gider." },
  { layer: "audio", label: "Sesleri sil", noun: "sesi",
    stays: "Kareler, fotoğrafları ve videoları kalır." },
];

/**
 * One of those windows: how many frames really lose the layer, and what survives.
 * `held` is how many of the selection carry it, `selected` is the whole selection.
 *
 * The skipped frames get a sentence of their own and it comes first, because it is what explains
 * the number in the title. Written as a count of frames rather than of the number itself: Turkish
 * hangs a suffix on a number that changes with its last digit, and a table for that would be more
 * machinery than one sentence is worth.
 *
 * The width travels with the words (madde 105): the skip sentence makes the window a size wider.
 */
export function layerConfirm(layer, held, selected) {
  const { noun, stays } = LAYER_ACTIONS.find((one) => one.layer === layer);
  const skipped = selected - held;
  return {
    title: `${held} karenin ${noun} silinsin mi?`,
    body: skipped
      ? `Seçili ${selected} kareden ${noun} olmayan ${skipped} kare atlanır. ${stays}`
      : stays,
    width: skipped ? 420 : 400,
  };
}
```

---

### Task 4: Ekran

**Files:**
- Modify: `queen-editor/frontend/src/shared/api.js`
- Modify: `…/photo_generation/useGeneration.js`
- Modify: `…/photo_generation/PhotoDetail.jsx`
- Modify: `…/photo_generation/ProjectScreen.jsx`
- Modify: `…/photo_generation/Gallery.jsx`

**Interfaces:**
- Consumes: Task 3'ün ikisi.
- Produces: Gallery'nin `onRemoveLayer(frames, kind)` prop'u.

- [ ] **Step 1: Çağrıyı listeye al**

`api.js`:

```js
// One call for one frame and for many, the same as deleting frames: the bar takes a layer off a
// whole selection and the detail page takes it off one.
export async function removeLayer(project, frames, kind) {
  return request(`/api/projects/${encodeURIComponent(project)}/layers/${kind}/delete`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ frames }),
  });
}
```

`useGeneration.js`: `const removeLayer = useCallback((frames, kind) => (deleteLayer(project, frames,
kind)…`, ve yorumun ilk cümlesi `One layer off the frames named.` oluyor.

`PhotoDetail.jsx`: `removeLayer([frame.id], layer)`.

`ProjectScreen.jsx`: kancadan `removeLayer` alınıyor ve `<Gallery … onRemoveLayer={removeLayer}`.

- [ ] **Step 2: Kırmızı biçimi sabite çıkar**

`Gallery.jsx`, `BAR`'ın hemen altına:

```jsx
// Red text, red border, no fill -- the app-wide destructive standard (madde 83). Three of the bar's
// buttons wear it now.
const DANGER = { color: "var(--danger)", borderColor: "var(--danger)", background: "none" };
// Which window is open, or none. A name rather than a flag: there are three of them now -- the
// frames' own and one per layer -- and only one can be up at a time.
const FRAMES = "frames";
```

- [ ] **Step 3: Pencereyi isimlendir**

`useState(false)` → `useState(null)`; `setConfirming(true)` → `setConfirming(FRAMES)`;
`handleDelete` ve pencerelerin `onCancel`'ı `setConfirming(null)` diyor.

- [ ] **Step 4: Kim taşıyor**

`handleCopy`'nin hemen altına:

```jsx
  // Which of the selection really carries a layer, in the gallery's own words: a layer that blew up
  // holds its slot but is not one the frame owns, and the tile shows no badge for it either. One
  // answer for three questions -- whether the button is drawn, what its window counts, and what the
  // request carries.
  const holding = (layer) => selected.filter(
    (fid) => owned(byId.get(fid) || {}).some((row) => row.layer === layer));

  function handleRemoveLayer() {
    const layer = confirming;
    setDeleting(true);
    onRemoveLayer(holding(layer), layer).then(() => {
      setDeleting(false);
      setConfirming(null);
      closeSelection();
    });
  }
```

- [ ] **Step 5: İki düğme**

Bardaki `Sil`in hemen altına:

```jsx
            {/* One per layer, to the right of Sil and dressed like it. Drawn only while something
                selected carries that layer: a window asking about no frames at all is not a
                window (Fark 80). */}
            {LAYER_ACTIONS.map(({ layer, label }) => holding(layer).length > 0 && (
              <Btn key={layer} sm onClick={() => setConfirming(layer)} style={DANGER}>
                <Icon.Trash /> {label}
              </Btn>
            ))}
```

- [ ] **Step 6: İki pencere**

```jsx
      {confirming === FRAMES && (
        <ConfirmModal title={confirm.title} body={confirm.body} confirmLabel={confirm.label}
                      width={confirm.width}
                      busyLabel="Siliniyor…" danger busy={deleting}
                      onCancel={() => setConfirming(null)} onConfirm={handleDelete} />
      )}

      {confirming && confirming !== FRAMES && (
        /* The layer's own window: what goes, what stays, and who is being skipped. Its words and
           its width both come from the module the tile badges come from. */
        <ConfirmModal {...layerConfirm(confirming, holding(confirming).length, selected.length)}
                      confirmLabel="Sil" busyLabel="Siliniyor…" danger busy={deleting}
                      onCancel={() => setConfirming(null)} onConfirm={handleRemoveLayer} />
      )}
```

İçe aktarma: `import { LAYER_ACTIONS, layerConfirm, lostLayers, owned } from "./layer_words.js";`

- [ ] **Step 7: Dört komutu koştur**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Expected: dördü de yeşil — 384 / 474 / 694 / 434.

---

### Task 5: Derlenmiş çıktı ve yeşil commit

- [ ] **Step 1: Derle**

Run: `npm run build --prefix queen-editor/frontend`

- [ ] **Step 2: Yol haritasını işaretle**

12. maddenin **İş** hücresi ✅ ile başlar, sayaç `11/31` → `12/31`.

- [ ] **Step 3: Commit**

```bash
git add queen-editor docs/superpowers
git commit -F - <<'EOF'
feat(queen-editor): a layer can be taken off a whole selection

Videolari sil and Sesleri sil stand to the right of Sil, dressed like it. Each is drawn
only while something in the selection carries that layer, and its window counts only those
frames -- when the rest of the selection does not carry it, a sentence says how many are
being skipped, first, because it is what explains the number in the title.

Which frames carry a layer is one answer read three times: whether the button is drawn,
what the window counts, and what the request sends. It is the gallery's own answer, so a
layer that blew up is not one the frame carries -- the tile shows no badge for it either.

remove_layer now takes a list of identities. One use case for one frame and for many, the
way deleting frames already works; the detail page sends a list of one. The whole press is
decided before a line is written, which is what makes a file two frames share come off the
disk when both of them let go in the same press.

An identity the gallery no longer knows is skipped rather than refused.

The body check had reached three callers, so it moved into one: frame_list holds the rule
and the exception, and each caller names its own verb in the message. remove_frames loses
InvalidFiles, a name that was already stale -- the body says frames.

The gallery's confirm state is a name now rather than a flag: there are three windows and
only one can be up.

dist built in this commit.

Four suites green.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** spec'in dört parçası sırayla Task 1, Task 2, Task 3, Task 4.

**Tip tutarlılığı:** `remove_layer` her yerde `(…, project, frames, kind)` ve `{"deleted": [...]}`;
`onRemoveLayer(frames, kind)` kancanın imzasıyla aynı sırada; `layerConfirm` `ConfirmModal`'ın üç
prop'unu birebir veriyor, o yüzden yayılarak geçiyor.

**Kontrol edilen tuzak:** `byId.get(fid)` seçili kare listeden düşmüşse `undefined`; `|| {}` olmadan
`owned` patlıyor.

**Kontrol edilen tuzak 2:** `dropping` dosya adını **döngü içinde** hesaplıyor, çünkü ses adı o
karenin videosunun adından türüyor — sonradan hesaplansa video satırı kapanmış olurdu.

**Kontrol edilen tuzak 3:** `checked` her şeyden önce çağrılıyor, yani olmayan projede bile gövde
hatası gövde hatası kalıyor — kopyalamada verilen kararın aynısı.

**Kontrol edilen tuzak 4:** `confirming` artık dize; `if (confirming) return` koruması `null` yanlış
değer olduğu için aynen çalışıyor, ve `confirming === FRAMES` karşılaştırması `"video"` ile
karışmıyor.

**Değişmeyen:** detay sayfasının iki penceresi ve sözleri. Yalnız çağrısı listeye dönüyor, ve o
sayfanın testleri bunun nöbeti.
