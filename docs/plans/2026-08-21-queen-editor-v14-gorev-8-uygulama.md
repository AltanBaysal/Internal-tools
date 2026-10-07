# v14 Görev 8 — Detayda Üretim modu bilgi satırı: UYGULAMA döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Test döngüsünün kırmızı bıraktığı sekiz testi yeşile döndürmek: videonun vardığı fotoğraf
kayda geçsin, kareye çıksın, ve detayın video sekmesinde "Üretim modu" satırı doğsun.

**Architecture:** 7. maddenin zinciri, bu kez ikinci bir alan için — ve zincir ikiye çıktığı yerde
tekrar yerine ortak bir yardımcı. Ön yüzde bir etiket arayıcı ve bir `Field`.

**Tech Stack:** Python 3.13, React 18, vite.

**Spec:** [uygulama turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-8-mod-bilgi-satiri-uygulama-design.md)

## Global Constraints

- **Test dosyaları bu döngüde değişmiyor.**
- Yorumlar **İngilizce**; ekran metni **Türkçe**.
- Commit mesajında **çift tırnak yok**, ve **amend yok**.
- Komut: dört satır, birebir, boru yok.
- **`dist` bu commit'te derleniyor.**
- Commit **yeşil gider**.
- **Eski satırlar okunmaya devam ediyor.** Drive'daki kayıtlarda ne `mode` ne `endsOn` var.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `backend/features/photo_generation/domain/run_loop.py` | satırın nasıl yapıldığı | `_mode_of` → `_made_with` |
| `backend/features/photo_generation/data/photo_record.py` | hücreye katlamak | `slots` |
| `backend/features/photo_generation/domain/usecases/list_frames.py` | kareye vermek | `_per_layer` + iki `append` |
| `backend/features/photo_generation/domain/copy_frame.py` | kopyaya götürmek | `carry_layers` |
| `frontend/src/features/photo_generation/production_modes.js` | modun adı | `labelOf` |
| `frontend/src/features/photo_generation/PhotoDetail.jsx` | satırın kendisi | `Field` |
| `frontend/dist/` | not defterinin okuduğu çıktı | derlenir |

---

### Task 1: Vardığı yer satıra yazılıyor

**Files:**
- Modify: `queen-editor/backend/features/photo_generation/domain/run_loop.py`

**Interfaces:**
- Produces: üretilen katmanın satırında isteğe bağlı `"endsOn"`. Task 2 onu okuyor.

- [ ] **Step 1: `_mode_of`'u `_made_with` yap**

```python
def _made_with(job, end):
    """What the produced row says about how it was made, beyond its words and its seed.

    The mode, and the name of the picture the video arrived at -- each only when there is one.

    Which jobs carry a mode is the queue's rule (queue_layer puts the field on video jobs alone) and
    it is not written a second time here, where the two could drift apart. A photo row saying
    standard would be a field that means nothing on nearly every line it appears on.

    The ending picture is named by the file the render was actually handed, not by the target's
    identity. The detail page prints that name, and an identity resolved later can resolve to
    nothing: the frame a video ends on can be deleted while the video stays.
    """
    made = {"mode": production_mode.of(job)} if job.get("mode") else {}
    if end:
        made["endsOn"] = end[0]
    return made
```

- [ ] **Step 2: `end`'i bir değişkende tut**

```python
                under = _source_for(kind, store, slots, project, fid)
                # Held because the row names it too: the picture the video arrives at is what the
                # detail page prints for a linked one.
                ending = _end_for(current, store, slots, project, fid, under)
                data = producer.generate(prompt, current["negative"], chosen,
                                         current["model"], source=under, end=ending)
```

`under`'ın üstündeki bugünkü yorum (`Held in a variable because a loop ends on the very file it is
made from…`) yerinde kalıyor — o başka bir sebep ve hâlâ doğru.

- [ ] **Step 3: `append`'i çevir**

```python
            record.append(project, {"file": filename, "frame": fid, "layer": kind,
                                    "status": queue.DONE,
                                    "prompt": prompt, "negative": current["negative"],
                                    "seed": chosen, "createdAt": now(),
                                    **_made_with(current, ending)})
```

- [ ] **Step 4: Takımı koştur**

Run: `python -m pytest queen-editor -q`
Expected: üç kırmızı kalır. `test_a_linked_video_names_the_picture_it_ended_on` ve
`test_a_loop_video_names_its_own_picture` yeşile döner.

---

### Task 2: Kayıt ve galeri cevabı

**Files:**
- Modify: `queen-editor/backend/features/photo_generation/data/photo_record.py`
- Modify: `queen-editor/backend/features/photo_generation/domain/usecases/list_frames.py`

**Interfaces:**
- Consumes: Task 1'in satırı.
- Produces: hücrede `endsOn`, karede `"endsOn": {layer: file}`. Task 3 ve ön yüz okuyor.

- [ ] **Step 1: Hücreye katla**

```python
            if isinstance(row.get("mode"), str):
                # Only a produced video's line names one, and the lines already on Drive name none
                # -- so the key is there only when the line had it.
                cell["mode"] = row["mode"]
            if isinstance(row.get("endsOn"), str):
                cell["endsOn"] = row["endsOn"]
```

Ve `slots`'un özeti:

```python
        """{frame: {slot: {"status", "file"[, "error"][, "mode"][, "endsOn"]}}} -- the latest line
        per (frame, slot) wins.

        A failure line also carries why: the renderer's own sentence, which the detail page prints
        under the red frame. A produced video's line carries the mode it was made in, and the
        picture it arrived at when it arrived at one. None of the three is on every line, so none
        of those keys is always there.
        """
```

- [ ] **Step 2: `_modes`'u `_per_layer` üstüne oturt**

`list_frames.py` içinde, `_modes`'un yerine:

```python
def _per_layer(cells, field):
    """{layer: the field's value} -- only the layers whose line carried it.

    Both of this shape's users answer the same kind of question about one layer at a time: which
    mode made it, and which picture it arrived at. Written as maps rather than fields named for the
    video, because both would have to be renamed the day a second layer gains a mode.
    """
    return {slot: cell[field] for slot, cell in cells.items() if cell.get(field)}
```

- [ ] **Step 3: İki `append`'i çevir**

Planlı kareler:

```python
                       "errors": _reasons(cells), "modes": _per_layer(cells, "mode"),
                       "endsOn": _per_layer(cells, "endsOn"),
```

Planın tanımadığı fotoğraflar:

```python
                           "errors": _reasons(cells), "modes": _per_layer(cells, "mode"),
                           "endsOn": _per_layer(cells, "endsOn"),
```

- [ ] **Step 4: Takımı koştur**

Run: `python -m pytest queen-editor -q`
Expected: bir kırmızı kalır — `test_a_sound_copy_carries_where_the_video_ended_too`.

---

### Task 3: Kopya iki alanı da götürüyor

**Files:**
- Modify: `queen-editor/backend/features/photo_generation/domain/copy_frame.py`

**Interfaces:**
- Consumes: Task 2'nin `modes` ve `endsOn` haritaları, karenin üstünden.

- [ ] **Step 1: Taşınan alanları bir listeye al**

```python
# What a carried layer keeps about how it was made: the frame's own map, and the field the row
# takes. One file, two frames holding it -- without these the twin's tile would read video while
# the original reads loop, and its detail page could not say where the video arrived.
CARRIED = (("modes", "mode"), ("endsOn", "endsOn"))


def carry_layers(record, project, copy, frame, kind, now):
    """Give the new frame everything below the layer that is about to be made.

    A video copy shares the picture, a sound copy shares the picture and the video (madde 102). The
    rows point at the source's own files: one picture, two frames holding it.
    """
    words = frame.get("prompts", {})
    for under in queue.ORDER[:queue.ORDER.index(kind)]:
        file = frame.get("layers", {}).get(under)
        if not file:
            continue
        made = {field: frame.get(source, {})[under]
                for source, field in CARRIED if frame.get(source, {}).get(under)}
        record.append(project, {"file": file, "frame": copy, "layer": under,
                                "status": queue.DONE, "prompt": words.get(under, ""),
                                "negative": frame.get("negative", ""),
                                "seed": frame.get("seed"), "createdAt": now(), **made})
```

- [ ] **Step 2: Takımı koştur**

Run: `python -m pytest queen-editor -q`
Expected: 653 yeşil.

---

### Task 4: Modun adı ve satırın kendisi

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/production_modes.js`
- Modify: `queen-editor/frontend/src/features/photo_generation/PhotoDetail.jsx`

**Interfaces:**
- Produces: `labelOf(mode) -> string`.
- Consumes: `frame.modes`, `frame.endsOn`.

- [ ] **Step 1: `labelOf`'u yaz**

`MODES`'un altına:

```js
/** The mode's own name, for the places that report a mode rather than offer one.
 *
 * The id itself is the fallback: a value this list does not know is corrupted data, and printing it
 * says more than an empty row would.
 */
export function labelOf(mode) {
  return (MODES.find((one) => one.id === mode) || {}).label || mode;
}
```

- [ ] **Step 2: Satırın değerini hesapla**

`PhotoDetail.jsx`'in import satırına:

```jsx
import { LINKED, labelOf } from "./production_modes.js";
```

ve `said` / `typed` hesabının yanına:

```jsx
  // How the open layer was made, when its line said so. Only a video has an answer today, and only
  // a produced one: a failed or deleted layer's latest line names no mode.
  const madeIn = (frame?.modes || {})[open];
  // Linked names the picture rather than the frame's number -- the sequence can be dragged, and a
  // number would then be a lie about a video nobody touched.
  const arrivesAt = (frame?.endsOn || {})[open];
```

- [ ] **Step 3: `Field`'i çiz**

Sıra ve dosya adlarının durduğu sarmalayan sıranın sonuna:

```jsx
              {open === "video" && madeIn && (
                /* Information, never a control: changing the mode is making the video again, and
                   that is the form further down (madde 94). */
                <Field label="Üretim modu"
                       value={madeIn === LINKED && arrivesAt
                         ? `${labelOf(madeIn)} → ${arrivesAt}`
                         : labelOf(madeIn)} />
              )}
```

- [ ] **Step 4: Dört komutu koştur**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Expected: dördü de yeşil.

---

### Task 5: Derlenmiş çıktı ve yeşil commit

- [ ] **Step 1: Derle**

Run: `npm run build --prefix queen-editor/frontend`

- [ ] **Step 2: Yol haritasını işaretle**

8. maddenin **İş** hücresi ✅ ile başlar, sayaç `7/31` → `8/31`.

- [ ] **Step 3: Commit**

```bash
git add queen-editor docs/superpowers
git commit -F - <<'EOF'
feat(queen-editor): the video tab says how this video was made

A row beside the sequence number and the file name, on the video tab alone: the mode
this video was produced in, and for a linked one the picture it arrived at. Nothing to
press -- changing the mode is making the video again, and that form is further down.

The ending picture is written on the row at render time, by the file the producer was
actually handed. Not the target's identity resolved later: the frame a video ends on can
be deleted while the video stays, and then a resolved name would resolve to nothing. The
design asks for the name over the number for a neighbouring reason -- the sequence can
be dragged and a number becomes a lie.

Whatever the render was given as an ending is what the row names, mode or no mode. A
loop's own picture is recorded too, which nothing reads yet; the alternative was
teaching the engine which modes end somewhere, and the modes already know.

The frame now answers two questions of the same shape, so they share one reader rather
than a second copy of it. The copy path carries both fields, from one list rather than
two lines that could fall out of step.

The mode's name comes from the same list the panel offers -- one place names the modes.
An id the list does not know prints itself: corrupted data says more than an empty row.

dist built in this commit.

Four suites green.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** spec'in altı parçası sırayla Task 1, 2, 2, 3, 4, 4.

**Tip tutarlılığı:** `_per_layer(cells, field)` iki çağrısında da aynı imza; `labelOf` her zaman
dize döndürüyor, dolayısıyla `Field`'in değeri hiç boş kalmıyor.

**Kontrol edilen tuzak:** `_reasons` `_per_layer`'a çevrilmedi. O yalnız **patlamış** katmanlara
bakıyor (`_failed_layers`), ötekiler alanın kendi varlığına — aynı görünen iki kuralı tek fonksiyona
sıkıştırmak, birinin süzgecini öbürüne bulaştırırdı.

**Kontrol edilen tuzak 2:** `CARRIED` çifti (`"modes"` → `"mode"`) tekil/çoğul farkını taşıyor:
karedeki harita çoğul, satırdaki alan tekil. Tek bir ada indirgemek, iki taraftan birini yeniden
adlandırmayı gerektirirdi.

**Kontrol edilen tuzak 3:** satır `madeIn` sorusuna bağlı, `open === "video"` tek başına değil.
Modu yazılmamış eski bir video boş bir satır doğurmuyor — 12. test bunun nöbeti.

**Kontrol edilen tuzak 4:** `arrivesAt` yalnız `LINKED`'de okunuyor. Loop'un satırında da bir ad
var (kendi resmi) ve onu yazmak "Loop → 0_a.png" gibi, hiçbir şey eklemeyen bir tekrar olurdu.

**Kontrol edilen tuzak 5:** `ending` `try` bloğunun içinde hesaplanıyor, bugün olduğu gibi.
Dışarı alınsaydı `MissingEndFrame` yakalanmaz ve bir karenin derdi bütün koşuyu durdururdu.
