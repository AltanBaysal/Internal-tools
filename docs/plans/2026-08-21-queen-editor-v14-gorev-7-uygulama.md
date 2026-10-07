# v14 Görev 7 — Galeride loop rozeti: UYGULAMA döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Test döngüsünün kırmızı bıraktığı dokuz testi yeşile döndürmek: üretilen videonun modu
satıra yazılsın, hücreye katlansın, kareye `modes` olarak çıksın, kopyayla gitsin ve karoda "video"
yerine "loop" okunsun.

**Architecture:** Dört halka, dört ayrı dosya, her biri bir öncekinin çıktısını okuyor. Beşincisi
ön yüzde: kelime değiştirme, `owned`'ın süzgecinden sonra.

**Tech Stack:** Python 3.13, React 18, vite.

**Spec:** [uygulama turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-7-loop-rozeti-uygulama-design.md)

## Global Constraints

- **Test dosyaları bu döngüde değişmiyor.**
- Yorumlar **İngilizce**; ekran metni **Türkçe**.
- Commit mesajında **çift tırnak yok**, ve **amend yok**.
- Komut: dört satır, birebir, boru yok.
- **`dist` bu commit'te derleniyor.**
- Commit **yeşil gider**.
- **Eski satırlar okunmaya devam ediyor.** Drive'daki kayıtlarda `mode` yok; hiçbir halka onu zorunlu
  saymıyor.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `backend/features/photo_generation/domain/run_loop.py` | modu satıra yazmak | `_mode_of` + `append` |
| `backend/features/photo_generation/data/photo_record.py` | satırı hücreye katlamak | `slots` |
| `backend/features/photo_generation/domain/usecases/list_frames.py` | kareye `modes` vermek | `_modes` + iki `append` |
| `backend/features/photo_generation/domain/copy_frame.py` | kopyaya modu götürmek | `carry_layers` |
| `frontend/src/features/photo_generation/layer_words.js` | karonun kelimesi | `owned` |
| `frontend/dist/` | not defterinin okuduğu çıktı | derlenir |

---

### Task 1: Mod satıra yazılıyor

**Files:**
- Modify: `queen-editor/backend/features/photo_generation/domain/run_loop.py`

**Interfaces:**
- Produces: üretilen katmanın satırında isteğe bağlı `"mode"` alanı. Task 2 onu okuyor.

- [ ] **Step 1: `_mode_of`'u yaz**

`_end_for`'un altına:

```python
def _mode_of(job):
    """The mode to write on the produced layer's row -- nothing for a job that names none.

    The same reading the render used (_end_for), so the row says what the video actually is.

    Which jobs have a mode is the queue's rule -- queue_layer puts the field on video jobs alone --
    and it is not written a second time here, where the two could drift apart. A photo row saying
    standard would be a field that means nothing on nearly every line it appears on.
    """
    return {"mode": production_mode.of(job)} if job.get("mode") else {}
```

- [ ] **Step 2: Satıra ekle**

```python
            record.append(project, {"file": filename, "frame": fid, "layer": kind,
                                    "status": queue.DONE,
                                    "prompt": prompt, "negative": current["negative"],
                                    "seed": chosen, "createdAt": now(), **_mode_of(current)})
```

- [ ] **Step 3: Takımı koştur**

Run: `python -m pytest queen-editor -q`
Expected: dört kırmızı kalır. `test_a_loop_video_says_on_its_row_that_it_is_one` ve
`test_a_plain_video_says_so_on_its_row_as_well` yeşile döner.

---

### Task 2: Mod hücreye katlanıyor

**Files:**
- Modify: `queen-editor/backend/features/photo_generation/data/photo_record.py`

**Interfaces:**
- Consumes: Task 1'in satırı.
- Produces: `slots()` hücresinde isteğe bağlı `"mode"`. Task 3 ve Task 4 onu okuyor.

- [ ] **Step 1: `slots`'a ekle**

```python
        folded = {}
        for row in self._rows(project):
            cell = {"status": _status_of(row), "file": row["file"]}
            if isinstance(row.get("error"), str):
                cell["error"] = row["error"]
            if isinstance(row.get("mode"), str):
                # Only a produced video's line names one, and the lines already on Drive name none
                # -- so the key is there only when the line had it.
                cell["mode"] = row["mode"]
            folded.setdefault(_frame_of(row), {})[_layer_of(row)] = cell
        return folded
```

Sınıfın belgesindeki `slots` özeti de bir alan kazanıyor:

```python
        """{frame: {slot: {"status", "file"[, "error"][, "mode"]}}} -- the latest line per (frame,
        slot) wins.

        A failure line also carries why: the renderer's own sentence, which the detail page prints
        under the red frame. A produced video's line carries the mode it was made in. Neither is on
        every line, so neither key is always there.
        """
```

- [ ] **Step 2: Takımı koştur**

Run: `python -m pytest queen-editor -q`
Expected: üç kırmızı kalır. `test_a_line_that_names_a_mode_carries_it_into_the_slot` yeşile döner.

---

### Task 3: Kare `modes` alıyor

**Files:**
- Modify: `queen-editor/backend/features/photo_generation/domain/usecases/list_frames.py`

**Interfaces:**
- Consumes: Task 2'nin hücresi.
- Produces: karede `"modes": {layer: mode}`. Task 4 ve ön yüz onu okuyor.

- [ ] **Step 1: `_modes`'u yaz**

`_reasons`'ın altına:

```python
def _modes(cells):
    """{layer: the mode it was made in} -- only the layers whose line named one.

    Video is the only layer with a mode today. Written as a map rather than a field named for the
    video, because the tile's loop badge and the detail page's information row ask the same
    question, and a name would have to change the day a second layer gains one.
    """
    return {slot: cell["mode"] for slot, cell in cells.items() if cell.get("mode")}
```

- [ ] **Step 2: İki `append`'e ekle**

Planlı kareler:

```python
        frames.append({**frame, "id": fid,
                       "file": photo["file"] if photo else photo_file(fid),
                       "layers": _taken_files(cells),
                       "owed": owed.get(fid, []), "failed": _failed_layers(cells),
                       "errors": _reasons(cells), "modes": _modes(cells),
                       "prompts": _words(said.get(fid, {}), frame.get("prompt")),
                       "status": status if status in SHOWN else "pending"})
```

Planın tanımadığı fotoğraflar:

```python
            frames.append({**row, "id": fid, "layers": _taken_files(cells),
                           "owed": owed.get(fid, []), "failed": _failed_layers(cells),
                           "errors": _reasons(cells), "modes": _modes(cells),
                           "prompts": _words(said.get(fid, {}), row.get("prompt")),
                           "status": queue.DONE})
```

İkisine birden: bir kare hangi koldan geldiğine göre farklı alanlar taşısaydı, ön yüz hangi kolun
konuştuğunu bilmek zorunda kalırdı.

- [ ] **Step 3: Takımı koştur**

Run: `python -m pytest queen-editor -q`
Expected: bir kırmızı kalır — `test_a_sound_copy_carries_the_videos_mode_too`.

---

### Task 4: Kopya modu götürüyor

**Files:**
- Modify: `queen-editor/backend/features/photo_generation/domain/copy_frame.py`

**Interfaces:**
- Consumes: Task 3'ün `modes` haritası, karenin üstünden.

- [ ] **Step 1: `carry_layers`'a ekle**

```python
def carry_layers(record, project, copy, frame, kind, now):
    """Give the new frame everything below the layer that is about to be made.

    A video copy shares the picture, a sound copy shares the picture and the video (madde 102). The
    rows point at the source's own files: one picture, two frames holding it.
    """
    words = frame.get("prompts", {})
    modes = frame.get("modes", {})
    for under in queue.ORDER[:queue.ORDER.index(kind)]:
        file = frame.get("layers", {}).get(under)
        if not file:
            continue
        mode = modes.get(under)
        record.append(project, {"file": file, "frame": copy, "layer": under,
                                "status": queue.DONE, "prompt": words.get(under, ""),
                                "negative": frame.get("negative", ""),
                                "seed": frame.get("seed"), "createdAt": now(),
                                # One file, two frames holding it: without this the twin's tile
                                # would read video while the original reads loop.
                                **({"mode": mode} if mode else {})})
```

- [ ] **Step 2: Takımı koştur**

Run: `python -m pytest queen-editor -q`
Expected: 650 yeşil.

---

### Task 5: Karonun kelimesi

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/layer_words.js`

**Interfaces:**
- Consumes: Task 3'ün `frame.modes`, ve `production_modes.js`'in `LOOP`'u.

- [ ] **Step 1: `owned`'ı genişlet**

```js
import { LOOP } from "./production_modes.js";
```

ve `owned`'ın yerine:

```js
// What a loop video wears instead of the plain word. Lower case unlike the panel's own label: that
// one is a row in a list of choices, this one is a word laid on a picture beside video and ses.
const LOOP_WORD = "loop";

/** Which of OWNED this frame really has. A layer that blew up holds its slot but is not owned --
 *  that one is the status pill's to name.
 *
 *  A loop video takes the word rather than standing beside it: one row per layer, so the two can
 *  never be read together. Swapped after the filter, so a loop video that blew up says nothing at
 *  all. */
export function owned(frame) {
  return OWNED
    .filter(({ layer }) => (frame.layers || {})[layer] && !(frame.failed || []).includes(layer))
    .map((row) => (row.layer === "video" && (frame.modes || {}).video === LOOP
      ? { ...row, word: LOOP_WORD } : row));
}
```

Yeni bir nesne (`{ ...row, word }`), `OWNED`'ın satırının üstüne yazmak değil: `OWNED` modül
seviyesinde ve paylaşılan bir sabit, üstüne yazmak bir sonraki karenin kelimesini de değiştirirdi.

- [ ] **Step 2: Dört komutu koştur**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Expected: dördü de yeşil.

---

### Task 6: Derlenmiş çıktı ve yeşil commit

- [ ] **Step 1: Derle**

Run: `npm run build --prefix queen-editor/frontend`

- [ ] **Step 2: Yol haritasını işaretle**

7. maddenin **İş** hücresi ✅ ile başlar, sayaç `6/31` → `7/31`.

- [ ] **Step 3: Commit**

```bash
git add queen-editor docs/superpowers
git commit -F - <<'EOF'
feat(queen-editor): a finished loop video says so on its tile

The mode used to reach the render and stop there. Now it rides the whole way: the loop
writes it on the produced layer's row, the record folds it into the slot, the gallery
hands out modes per layer, and the tile reads loop where it read video.

Only a job that names a mode writes one. Which jobs those are is the queue's rule --
video jobs alone -- and repeating it in the engine would let the two disagree. Lines
already on Drive name none, and every link treats that as the answer rather than a gap.

The frame's field is a map keyed by layer, the shape errors already has. A field named
for the video would need renaming the day a second layer gains a mode, and the detail
page is about to ask the same question of the same frame.

A sound copy carries its source's video row, so it carries the mode with it: one file,
two frames holding it, and two answers about it would be one too many.

The word replaces rather than joins, after the failed-layer filter -- so a loop video
that blew up still says nothing, and the pill speaks for that tile alone.

dist built in this commit.

Four suites green.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** spec'in beş parçası sırayla Task 1–5. Kararlar 7 ve 8 (silme onayı ve bağlı modun
rozetsizliği) hiçbir dosyaya dokunmuyor — ikisi de "değişmeyen" kararlar.

**Tip tutarlılığı:** `mode` her halkada dize; `modes` her yerde `{layer: mode}`. `_modes` ile
`_reasons` aynı imzayı (`cells`) ve aynı süzme kuralını taşıyor.

**Kontrol edilen tuzak:** `owned` içindeki `.map` yeni nesne üretiyor. `row.word = LOOP_WORD`
yazılsaydı `OWNED`'ın kendi satırı değişir ve o modül seviyesinde paylaşıldığı için sonraki her kare
"loop" derdi — testler tek kareli olduğu için de yakalanmazdı.

**Kontrol edilen tuzak 2:** `.map` `.filter`'dan sonra. Önce gelseydi patlamış bir loop videosu
kelimesini değiştirir, sonra süzgeç onu atardı — sonuç aynı olurdu, ama sıra ters yazıldığında
okuyan kişi hangisinin nöbetçi olduğunu anlayamazdı. 13. test bu sıranın nöbeti.

**Kontrol edilen tuzak 3:** `_mode_of` `job.get("mode")` diye soruyor, `"mode" in job` diye değil.
Boş dize taşıyan bir iş — bugün mümkün değil, çünkü `queue_layer` doğruluyor — satıra boş bir alan
yazmıyor.

**Kontrol edilen tuzak 4:** `carry_layers`'daki mod, karenin `modes`'undan okunuyor, kayıttan
yeniden değil. `carry_layers` zaten `layers` ve `prompts`'u kareden okuyor; üçüncü bir kaynak,
kopyanın neye benzediğini üç ayrı yere sorardı.

**Kontrol edilen sınır:** `regenerate` yeniden ürettiği videoya mod yazmıyor, dolayısıyla yeniden
üretilen bir loop videosu rozetini kaybediyor. 9. maddenin işi — orada yeniden üret formuna mod
seçicisi geliyor ve varsayılanı bu videonun modu.