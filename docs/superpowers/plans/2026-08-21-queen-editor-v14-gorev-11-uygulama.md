# v14 Görev 11 — Kart kopyalama: UYGULAMA döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Test döngüsünün bıraktığı 29 testi yeşile döndürmek: kopya adlansın, ikiz doğsun, rota ve
bar onu kullanıcının eline versin.

**Architecture:** Aşağıdan yukarı dört tur — ad, iş, rota, ekran. Her turdan sonra takım koşuyor,
çünkü python takımı ancak ilk iki turdan sonra **toplanabiliyor** ve testlerin gerçek sebeplerini
ilk kez orada görüyoruz.

**Tech Stack:** Python 3 + Flask, React 18 + vite.

**Spec:** [uygulama turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-11-kart-kopyalama-uygulama-design.md)

## Global Constraints

- **Test dosyaları bu döngüde değişmiyor — bir ölçüm düzeltmesi dışında.** Bardaki sırayı okuyan
  test düğmelerin `textContent`'ini karşılaştırıyordu; `Sil` çöp ikonuyla geldiği için metni
  `" Sil"` ve karşılaştırma bugünkü DOM hakkında yanlıştı. Doğrusu kaynağı değiştirmek değil —
  ikonu sökmek çalışan bir düğmeyi kötü bir iddiaya uydurmak olurdu — okumayı kırpmak. Testin
  ölçtüğü şey, yani sıra, aynen duruyor.
- Yorumlar ve kod **İngilizce**; ekran metni ve hata cümleleri **Türkçe**.
- Commit mesajında **çift tırnak yok**, ve **amend yok**.
- Komut: dört satır, birebir, boru yok.
- **`dist` bu commit'te derleniyor.**
- Commit **yeşil gider**.
- Hata sınıfı: `InvalidFrames`, `usecases/copy_frames.py` içinde, mesajı
  `Kopyalanacak kare listesi metin dizisi olmalı.` — rota onu 400 ile veriyor.
- Kopya öneki `C`, indeks **1'den** başlıyor.
- **Kuyruk çalıştırılmıyor, plan satırı yazılmıyor.** İkizin üretilecek bir şeyi yok.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `backend/features/photo_generation/domain/photo_name.py` | adın yazılması ve okunması | `COPY`, `copy_id`, `copy_parts`, `_parts` |
| `backend/features/photo_generation/domain/copy_frame.py` | ikizin adı ve katmanları | `next_copy_id`, `carry_all`, ortak iç işlev |
| `backend/features/photo_generation/domain/usecases/copy_frames.py` | işin kendisi | **yeni** |
| `backend/features/photo_generation/presentation/routes.py` | rota | `frames/copy` |
| `backend/main.py` | bağlama | `copy_frames=` |
| `frontend/src/shared/api.js` | çağrı | `copyFrames` |
| `frontend/src/features/photo_generation/useGeneration.js` | kancanın geçişi | `copyPhotos` |
| `frontend/src/features/photo_generation/ProjectScreen.jsx` | bağlanma | `onCopy` |
| `frontend/src/features/photo_generation/Gallery.jsx` | düğme ve kısayol | üç değişiklik |
| `frontend/dist/` | not defterinin okuduğu çıktı | derlenir |

---

### Task 1: Kopyanın adı

**Files:**
- Modify: `queen-editor/backend/features/photo_generation/domain/photo_name.py`
- Modify: `queen-editor/backend/features/photo_generation/domain/copy_frame.py`

**Interfaces:**
- Produces: `copy_id(base, index) -> str`, `copy_parts(name) -> (int|None, str)`,
  `next_copy_id(ids, source) -> str`. Task 2 üçünü de okuyor.

- [ ] **Step 1: Öneki yaz ve okut**

`photo_name.py`, `legacy_frame_id`'nin hemen altına:

```python
# A twin's identity is its source's with this in front: C1_P11_1 was copied from P11_1. At the
# front rather than the back, because a suffix reads as another layer round -- _V1_0 and _S1_0 are
# exactly that (madde 78).
COPY = "C"


def copy_id(base, index):
    """The identity the `index`th twin of `base` takes."""
    return f"{COPY}{index}_{base}"


def copy_parts(name):
    """(which copy, the identity it was copied from); a name with no prefix is its own base.

    One prefix, never nested: a copy of a copy is another copy of the same base, so the head is
    read off once and what is left is the base itself.
    """
    head, sep, rest = name.partition("_")
    if sep and head.startswith(COPY) and head[1:].isdigit() and rest:
        return int(head[1:]), rest
    return None, name
```

`_parts`'ın ilk satırı:

```python
    # The prefix comes off first: a twin holds its source's picture, so it belongs to the family of
    # the prompt that made that picture. Left on, the name fits neither scheme and the frame would
    # have no number at all.
    stem = copy_parts(frame_id_of(name))[1]
```

- [ ] **Step 2: İkizin adını ver**

`copy_frame.py`, `next_id`'nin hemen altına:

```python
def next_copy_id(ids, source):
    """The identity a twin of `source` takes; `ids` is every identity the project has used.

    One past the highest copy index that base has ever carried, never a gap -- next_id's rule, for
    next_id's reason: the name of a deleted twin stays claimed. Counted against the base rather than
    the source, so copying a copy gives C2_P11_1 rather than a nested name.
    """
    base = copy_parts(source)[1]
    used = [copy_parts(fid)[0] for fid in ids if copy_parts(fid)[1] == base]
    used = [index for index in used if index is not None]
    return copy_id(base, max(used) + 1 if used else 1)
```

İçe aktarma satırı `copy_id, copy_parts, frame_id, number_of, variant_of` oluyor.

- [ ] **Step 3: Takımı koştur**

Run: `python -m pytest queen-editor -q`
Expected: `test_photo_name.py` artık toplanıyor ve dört yeni testi yeşil; öbür üç dosya hâlâ
`copy_frames` modülünü bulamıyor.

---

### Task 2: İşin kendisi

**Files:**
- Modify: `queen-editor/backend/features/photo_generation/domain/copy_frame.py`
- Create: `queen-editor/backend/features/photo_generation/domain/usecases/copy_frames.py`

**Interfaces:**
- Consumes: Task 1'in `next_copy_id`'si.
- Produces: `copy_frames(record, store, plan_store, order_store, now, project, frames)` →
  `{"copies": [...]}`, ve `InvalidFrames`. Task 3 ikisini de okuyor.

- [ ] **Step 1: Taşımayı ikiye ayır**

`copy_frame.py`'nin sonundaki `carry_layers`, ortak bir iç işlevin iki çağrısına dönüşüyor:

```python
def _carry(record, project, copy, frame, slots, now):
    """Write the new frame's rows for `slots`, pointing at the source's own files.

    The rows are the source's: one picture, two frames holding it (madde 102).
    """
    words = frame.get("prompts", {})
    failed = frame.get("failed", [])
    for under in slots:
        file = frame.get("layers", {}).get(under)
        # A layer that blew up still names a file in the frame's map, but that file is not on disk:
        # a done row about it on the new frame would say it is.
        if not file or under in failed:
            continue
        made = {field: frame.get(source, {})[under]
                for source, field in CARRIED if frame.get(source, {}).get(under)}
        record.append(project, {"file": file, "frame": copy, "layer": under,
                                "status": queue.DONE, "prompt": words.get(under, ""),
                                "negative": frame.get("negative", ""),
                                "seed": frame.get("seed"), "createdAt": now(), **made})


def carry_layers(record, project, copy, frame, kind, now):
    """Give the new frame everything below the layer that is about to be made.

    A video copy shares the picture, a sound copy shares the picture and the video (madde 102).
    """
    _carry(record, project, copy, frame, queue.ORDER[:queue.ORDER.index(kind)], now)


def carry_all(record, project, copy, frame, now):
    """Give the new frame every layer its source holds -- a twin with nothing left to produce."""
    _carry(record, project, copy, frame, queue.ORDER, now)
```

- [ ] **Step 2: Kullanım durumunu yaz**

`usecases/copy_frames.py`:

```python
"""Twin the frames the user picked -- everything they hold, beside them.

Not a new idea: a copy frame is what a video variant past the first already is (copy_frame). What
is new is that the user asks for it, and that the twin takes EVERY layer rather than the ones under
the job about to run -- an exact twin has nothing left to produce.

So nothing is planned and nothing is queued. The twin's rows are the whole of it, and it reaches the
gallery the way any photo the plan does not know about does (list_frames). Its rows point at the
source's own files: one picture on disk, two frames holding it, and the last of them to be deleted
is what unlinks it (layers.files_to_unlink).

An identity the gallery does not know is skipped rather than refused, and so is a frame that has not
been produced yet: the first can be deleted in another tab while this selection sits open, and the
second owns no layer to twin. Refusing the whole press over either would leave the rest undone.
"""
from backend.features.photo_generation.domain import queue
from backend.features.photo_generation.domain.copy_frame import (
    carry_all,
    known_ids,
    next_copy_id,
    placed,
)
from backend.features.photo_generation.domain.usecases.list_frames import list_frames


class InvalidFrames(Exception):
    """The body was not a list of frame identities."""


def copy_frames(record, store, plan_store, order_store, now, project, frames):
    if not isinstance(frames, list) or any(not isinstance(fid, str) for fid in frames):
        raise InvalidFrames("Kopyalanacak kare listesi metin dizisi olmalı.")
    # Raises ProjectMissing when there is no such project.
    gallery = list_frames(record, store, plan_store, order_store, project)
    by_id = {frame["id"]: frame for frame in gallery}

    # Every name the project has ever used, growing as the twins are born: two copies of one source
    # in a single press must not be handed the same name.
    ids = known_ids(record, plan_store, project)
    born, copies = {}, []
    for fid in frames:
        frame = by_id.get(fid)
        if frame is None or frame["status"] != queue.DONE:
            continue
        twin = next_copy_id(ids, fid)
        ids.add(twin)
        carry_all(record, project, twin, frame, now)
        born.setdefault(fid, []).append(twin)
        copies.append(twin)

    if copies:
        # Written once at the end rather than per twin: it is a single small document, and one write
        # is one chance to be interrupted instead of N.
        order_store.write(project, placed([frame["id"] for frame in gallery], born))
    return {"copies": copies}
```

- [ ] **Step 3: Takımı koştur**

Run: `python -m pytest queen-editor -q`
Expected: `test_photo_usecases.py` ve `test_export.py` toplanıyor, on dört yeni test yeşil.
`test_photo_routes.py` hâlâ `copy_frames` anahtarını tanımayan blueprint yüzünden kırmızı.

---

### Task 3: Rota

**Files:**
- Modify: `queen-editor/backend/features/photo_generation/presentation/routes.py`
- Modify: `queen-editor/backend/main.py`

**Interfaces:**
- Consumes: Task 2'nin `copy_frames`'i ve `InvalidFrames`'i.

- [ ] **Step 1: Blueprint'e al**

`routes.py` içe aktarmalarına, `queue_layer` satırının üstüne:

```python
from backend.features.photo_generation.domain.usecases.copy_frames import InvalidFrames
```

`make_photo_generation_blueprint`'in imzasında `remove_frames`'in yanına `copy_frames` ekleniyor.

- [ ] **Step 2: Rotayı yaz**

Silme rotasının hemen altına:

```python
    # Beside the delete above, and the same shape: a list of identities in the body, because a copy
    # frame shares its source's picture and a file name would not say which of the two was asked
    # for.
    @bp.post("/api/projects/<project>/frames/copy")
    def copy(project):
        body = request.get_json(silent=True) or {}
        try:
            answer = copy_frames(project, body.get("frames"))
        except InvalidFrames as exc:
            return jsonify({"error": str(exc)}), 400
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404
        # The gallery comes back with the twins: the screen would ask for exactly this in a second
        # round-trip, and until it lands the copies it was just told about are nowhere.
        return jsonify({**answer, "frames": list_frames(project)})
```

- [ ] **Step 3: main.py'de bağla**

İçe aktarmalara `from backend.features.photo_generation.domain.usecases.copy_frames import
copy_frames`, ve `remove_frames=partial(...)`'ın hemen altına:

```python
    copy_frames=partial(copy_frames, _photo_record, _photo_store, _plan_store, _order_store,
                        lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")),
```

- [ ] **Step 4: Takımı koştur**

Run: `python -m pytest queen-editor -q`
Expected: python takımının tamamı yeşil.

---

### Task 4: Ekran

**Files:**
- Modify: `queen-editor/frontend/src/shared/api.js`
- Modify: `queen-editor/frontend/src/features/photo_generation/useGeneration.js`
- Modify: `queen-editor/frontend/src/features/photo_generation/ProjectScreen.jsx`
- Modify: `queen-editor/frontend/src/features/photo_generation/Gallery.jsx`

**Interfaces:**
- Produces: Gallery'nin `onCopy(frames) -> Promise<string[]|null>` prop'u.

- [ ] **Step 1: Çağrıyı yaz**

`api.js`, `removeFrames`'in hemen altına:

```js
// The twins of the frames named, born beside them. Identities again, the same as the delete call,
// and the answer carries both their names and the gallery they landed in.
export async function copyFrames(project, frames) {
  return request(`/api/projects/${encodeURIComponent(project)}/frames/copy`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ frames }),
  });
}
```

- [ ] **Step 2: Kancadan geçir**

`useGeneration.js` içe aktarmasına `copyFrames,` (alfabetik olarak `cancelGeneration`'dan sonra), ve
`removePhotos`'un hemen üstüne:

```js
  // Twins of the frames named. Nothing is produced, so nothing starts running -- the answer carries
  // the gallery they landed in, which is one round-trip instead of two. Resolves with the twins'
  // own names so the screen can move the selection onto them, or null when it was refused.
  const copyPhotos = useCallback((frames) => (
    copyFrames(project, frames)
      .then((body) => {
        if (!alive.current) return null;
        if (body?.frames) setFrames(body.frames);
        return body?.copies || [];
      })
      .catch((err) => {
        if (alive.current) setError(failureText(err));
        return null;
      })
  ), [project]);
```

Döndürülen nesneye `copyPhotos` ekleniyor.

- [ ] **Step 3: Galeriye bağla**

`ProjectScreen.jsx`: `removePhotos`'un yanına `copyPhotos`, ve `<Gallery … onDelete={removePhotos}`
satırına `onCopy={copyPhotos}`.

- [ ] **Step 4: Seçimin üretilmiş yarısını yukarı taşı**

`Gallery.jsx`: bugün `selectable`'ın altında duran `byId` / `chosenPhotos` / `chosenQueued` üçlüsü
`handleDelete`'in hemen altına, **erken dönüşlerin üstüne** çıkıyor:

```jsx
  // Who is in the selection, split by what they are: only a produced frame owns layers to twin or
  // files to delete. Worked out above the empty gallery's own answers, because the shortcut below
  // is listened for from up here -- and a list that is not there yet holds nobody.
  const byId = new Map((frames || []).map((frame) => [frame.id, frame]));
  const chosenPhotos = selected.filter((fid) => byId.get(fid)?.status === "done");
  const chosenQueued = selected.filter((fid) => byId.get(fid)?.status !== "done");

  function handleCopy() {
    // Only the produced ones multiply: a pending frame has no layer to twin (Fark 79).
    if (!chosenPhotos.length) return;
    onCopy(chosenPhotos).then((copies) => {
      // The selection moving onto the twins is how the copy is noticed -- there is no notification
      // of its own. A refused request answers with nothing and the selection stays where it was.
      if (copies?.length) setSelected(copies);
    });
  }
```

Aşağıdaki üç `const` satırı siliniyor; `selectable` yerinde kalıyor.

- [ ] **Step 5: Kısayolu ekle**

Escape'i dinleyen etki:

```jsx
  useEffect(() => {
    if (!selecting) return undefined;
    const onKey = (e) => {
      // The window owns the keyboard while it is up: both of these belong to the gallery behind it.
      if (confirming) return;
      if (e.key === "Escape") closeSelection();
      if (e.key.toLowerCase() === "d" && e.ctrlKey) {
        // The browser's own bookmark shortcut, taken: over a selection Ctrl + D means duplicate,
        // and a bookmark window is never what was meant.
        e.preventDefault();
        handleCopy();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  });
```

- [ ] **Step 6: Düğmeyi koy**

Bardaki `Tümünü seç` ile `Sil` arasına:

```jsx
            {/* Only while the selection holds something produced: a bar over nothing but pending
                frames offers no copy at all, because there is nothing to twin (Fark 79). Frameless,
                like the button beside it -- the destructive one is the only outlined one here. */}
            {chosenPhotos.length > 0 && (
              <Btn sm ghost onClick={handleCopy}>Kopyala</Btn>
            )}
```

- [ ] **Step 7: Bar sırasını okuyan satırı kırp**

`Gallery.test.jsx`, "puts Kopyala in the bar" testinde:

```jsx
    // Trimmed: Sil carries its trash glyph, so its text starts with a space. What is being read
    // here is the order of the words, not the spacing around them.
    const words = [...bar.querySelectorAll("button")].map((one) => one.textContent.trim());
```

- [ ] **Step 8: Dört komutu koştur**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Expected: dördü de yeşil — 384 / 474 / 686 / 423.

---

### Task 5: Derlenmiş çıktı ve yeşil commit

- [ ] **Step 1: Derle**

Run: `npm run build --prefix queen-editor/frontend`

- [ ] **Step 2: Yol haritasını işaretle**

11. maddenin **İş** hücresi ✅ ile başlar, sayaç `10/31` → `11/31`.

- [ ] **Step 3: Commit**

```bash
git add queen-editor docs/superpowers
git commit -F - <<'EOF'
feat(queen-editor): a card can be copied, and the copy is an exact twin

Kopyala stands in the selection bar, to the left of Sil, and Ctrl + D does the same thing.
The shortcut is taken from the browser, which owns it for bookmarks; the confirm window
keeps the keyboard while it is up.

The twin carries every layer its source really holds, with the words each was made from,
the mode the video was made in and the picture it arrived at. Its rows point at the
source's own files, so there is one picture on disk and two frames holding it -- and
deleting one twin leaves the other whole, because a file another frame still holds is
never unlinked.

Nothing is planned and nothing is queued: an exact twin has nothing left to produce, so
the queue never hears of it and it reaches the gallery from the record alone.

Its name is its source's with a prefix in front -- P11_1 copied is C1_P11_1 -- because a
suffix would read as another layer round. The prefix never nests: copying the copy gives
C2_P11_1, counted against the base, never reusing the name of a deleted twin. Number and
variant are read through it, so a twin still belongs to the family of the prompt that made
the picture it is holding.

It lands directly above its source and the selection moves onto it. That is how the copy
is noticed; there is no notification of its own. A selection of nothing but pending frames
draws no button at all, and a mixed one copies only the frames that have been produced.

A layer that blew up is not carried: it names a file that is not on disk. The rule lives
in the one place a carried row is written, so the variant copies get it too.

dist built in this commit.

Four suites green.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** spec'in beş parçası sırayla Task 1, Task 2, Task 2, Task 3, Task 4.

**Tip tutarlılığı:** `copy_parts` her yerde `(int|None, str)`; `copy_frames` `{"copies": [...]}`,
rota bunun üstüne `frames` ekliyor. `onCopy` bir söz veriyor ve adları ya da `null` döndürüyor —
`handleCopy` ikisini de karşılıyor.

**Kontrol edilen tuzak:** `_parts` öneki soyduğu için `number_of("C1_0_a_V1_0.mp4")` da doğru
çalışıyor: `frame_id_of` önce katman çiftini kesiyor, sonra önek ayrılıyor.

**Kontrol edilen tuzak 2:** `known_ids` yeni bir küme veriyor, dolayısıyla `ids.add(twin)` kimsenin
verisini bozmuyor — ve bir istekte aynı kaynaktan iki ikiz istenirse ikincisi `C2_` oluyor.

**Kontrol edilen tuzak 3:** `chosenPhotos` erken dönüşlerin üstüne çıkarken `frames` null olabiliyor;
`(frames || [])` bunun için. Boş listede `chosenPhotos` boş kalıyor ve `handleCopy` hiçbir şey
yapmıyor.

**Kontrol edilen tuzak 4:** `confirming` kontrolü artık dinleyicinin başında. Escape'in bugünkü
davranışı birebir aynı — bugün de `!confirming` ile korunuyordu.

**Kontrol edilen tuzak 5:** `e.key.toLowerCase()` — CapsLock açıkken tarayıcı `"D"` gönderiyor ve
kısayol ölmüş, yer imi penceresi açılmış olurdu.

**Kontrol edilen tuzak 6:** ikon taşıyan bir düğmenin `textContent`'i ikonla metin arasındaki
boşlukla başlıyor. Bar sırasını okuyan test bunu kırpmak zorunda; kaynağı ona uydurmak, çalışan bir
düğmeyi yanlış bir iddia için bozmak olurdu.

**Değişmeyen:** `carry_layers`'ın çağıranları. `queue_layer` ve `regenerate` aynı imzayı çağırıyor,
ve kopya kare testleri genellemenin onları bozmadığının nöbeti.
