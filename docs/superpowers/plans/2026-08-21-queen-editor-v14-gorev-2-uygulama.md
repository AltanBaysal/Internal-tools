# v14 Görev 2 — Kuyruk işinin üretim modunu taşıması: UYGULAMA döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Test döngüsünün kırmızı bıraktığı on beş testi yeşile döndürmek: üç modun adı doğsun,
kuyruk modu plan satırına yazsın, bağlı modda hedefi kuyruk anında çözsün, ve motor modu okuyup
üreticiye bitiş karesini versin.

**Architecture:** Bir yeni domain modülü ve iki var olan domain dosyasının genişlemesi. Yazan taraf
`queue_layer`, okuyan taraf `run_loop`; ikisi arasındaki sözleşme plan satırının iki anahtarı
(`mode`, `linkedTo`). Üretici hiçbir şey öğrenmiyor — ona hâlâ yalnız bir resim gidiyor ya da
gitmiyor.

**Tech Stack:** Python 3.

**Spec:** [uygulama turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-2-uretim-modu-uygulama-design.md)

## Global Constraints

- **Test dosyaları bu döngüde değişmiyor.** Kırmızı commit'lenen on beş test neyi tarif ediyorsa
  kod odur. **İki istisna çıktı ve ikisi de burada yazılı** — hiçbiri bir iddiayı değiştirmiyor:
  - Test turu `test_photo_routes.py`'nin sahtelerini genişletmeyi atlamıştı (`FakeGenerator`,
    `StopsAfter` ve üç satır içi sahte). Motor `end=` göndermeye başlayınca yirmi iki uç testi
    `TypeError` ile düştü. İmzalar burada genişledi.
  - `test_a_linked_video_whose_target_lost_its_photo_turns_that_frame_red`'in kurulumu iki kareli
    bir galeri kuruyordu ama ikinci karenin fotoğrafını yazmıyordu; o karenin foto işi borçlu
    kalıyor ve koşu, bu testte olmayan bir foto üreticisini bekleyerek duruyordu — video işine hiç
    gelinmiyordu. Galeri tek kareye indirildi, ki silinmiş bir hedefin bıraktığı hâl zaten odur.
    İddia (o karo kırmızıya döner) değişmedi.
- Yorumlar ve docstring'ler **İngilizce**; hata cümleleri **Türkçe** (kullanıcı okuyor).
- **Yorum NEDEN'i söyler ve yalnız bugün doğru olanı.**
- **Katman kuralı:** `production_mode.py` domain'de ve hiçbir şey import etmiyor. `run_loop` ile
  `queue_layer` ondan okuyor; ters yön yok.
- Commit mesajında **çift tırnak yok**, ve **amend yok**.
- Komut: dört satır, birebir, boru yok.
- `dist/` **derlenmiyor**.
- Commit **yeşil gider**.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `domain/production_mode.py` | üç modun kimliği ve okunması | yaratılır |
| `domain/usecases/queue_layer.py` | modu plan satırına yazan yer | `InvalidMode`, `mode`, iki yardımcı |
| `domain/run_loop.py` | modu okuyup bitiş karesini seçen yer | `MissingEndFrame`, `_end_for` |

---

### Task 1: Üç modun adı

**Files:**
- Create: `queen-editor/backend/features/photo_generation/domain/production_mode.py`

**Interfaces:**
- Produces: `STANDARD`, `LOOP`, `LINKED`, `ALL`, `of(job) -> str`. Task 2 ve Task 3 bunlara
  dayanıyor.

- [ ] **Step 1: Modülü yaz**

```python
"""How a video job says where it ends.

Three identities and nothing else. What the user reads in Turkish is the frontend's business
(production_modes.js): a name and its label pulled apart on purpose, so renaming one on screen never
touches what is written in a plan file that has to keep reading back for months.

Only a video has a mode. A photo is made from its words and a sound is laid over the whole of a
video -- neither arrives anywhere, so neither is asked.
"""
STANDARD = "standard"
LOOP = "loop"
LINKED = "linked"

# What the queue validates against. A mode missing from here could never be asked for.
ALL = (STANDARD, LOOP, LINKED)


def of(job):
    """The mode a planned job carries, as the engine should read it.

    Anything the list does not know reads as the plain one, and so does a job with no mode at all:
    every video planned before this madde carries none, and each has to go on rendering exactly as
    it does today. The queue refuses an unknown mode at the door, so by the time a job is being
    rendered the plain reading is the only honest one left.
    """
    mode = job.get("mode")
    return mode if mode in ALL else STANDARD
```

- [ ] **Step 2: Takımı koştur**

Run: `python -m pytest queen-editor -q`
Expected: `test_production_mode.py`'ın dördü de yeşil. `test_photo_usecases.py` hâlâ toplanamıyor —
`InvalidMode` yok.

---

### Task 2: Kuyruğun yazdığı mod

**Files:**
- Modify: `queen-editor/backend/features/photo_generation/domain/usecases/queue_layer.py`

**Interfaces:**
- Consumes: Task 1'in modülü; `queue.DONE`; `list_frames`'in galeri sırası.
- Produces: `InvalidMode`; `queue_layer(..., mode=production_mode.STANDARD)`. 4. madde uç noktadan
  bu parametreyi çağıracak.

- [ ] **Step 1: Import'u ve istisnayı ekle**

```python
from backend.features.photo_generation.domain import layers, production_mode, queue
```

ve `InvalidScope`'un altına:

```python
class InvalidMode(Exception):
    """A production mode nobody knows, or one given to a layer that ends nowhere."""
```

- [ ] **Step 2: Plan satırının işaretini ekle**

`_job`'a `mark` parametresi:

```python
def _job(kind, fid, number, variant, mark=()):
    """The plan line for one layer.

    The prompt is empty on purpose: a language model writes it when the job's turn comes, and a box
    the user was never shown must not pretend to hold their words.

    `mark` is what the production mode adds -- nothing at all for a layer that ends nowhere.
    """
    return {"id": fid, "type": kind, "number": number, "variant": variant,
            "prompt": "", "negative": "", "seed": None, "model": "", **dict(mark)}
```

- [ ] **Step 3: İki yardımcıyı yaz**

`_job`'un altına:

```python
def _frame_after(gallery, fid):
    """The frame a linked video ends on: the one that comes after it in the film.

    The film's sequence, not the gallery's reading order. The gallery is newest-first and the export
    stitches it reversed (export_summary.exportable) -- the foot of the gallery is the film's first
    frame -- so the frame that plays next is the one ABOVE, at index - 1. Linking downwards would
    make every chain run against the film it is part of.

    None where there is nothing to end on: the last frame of the film -- the top of the gallery --
    has no next, and a next whose photo never landed is the same emptiness seen from closer up.
    """
    for index, frame in enumerate(gallery):
        if frame["id"] != fid:
            continue
        after = gallery[index - 1] if index > 0 else None
        return after["id"] if after and after["status"] == queue.DONE else None
    return None


def _mark(kind, mode, gallery, fid):
    """What the mode writes into this frame's plan line, or None when it takes no job at all.

    Resolved as the job is queued rather than as it is rendered: the user can drag the gallery while
    the queue runs, and a target read hours later would not be the one they were looking at when
    they pressed the button.
    """
    if kind != layers.VIDEO:
        return {}
    if mode != production_mode.LINKED:
        return {"mode": mode}
    target = _frame_after(gallery, fid)
    if target is None:
        # The brief's decision: production is not blocked, this one frame stays out and the rest go
        # in. Fixing the selection and pressing again is all it takes.
        return None
    return {"mode": mode, "linkedTo": target}
```

`None` ile `{}` ayrı şeyler: biri "yazacak bir şey yok", öteki "bu kare kuyruğa hiç girmesin".

- [ ] **Step 4: İmzayı ve doğrulamaları yaz**

```python
def queue_layer(runner, store, record, plan_store, order_store, producers, now, project, kind,
                files=None, variants=1, log=None, writers=None,
                mode=production_mode.STANDARD):
    """Returns how many jobs of this kind the queue took."""
    if files is not None and (not isinstance(files, list)
                              or any(not isinstance(name, str) for name in files)):
        raise InvalidScope("Seçim listesi metin dizisi olmalı.")
    if mode not in production_mode.ALL:
        raise InvalidMode(f"Üretim modu şunlardan biri olmalı: {', '.join(production_mode.ALL)}.")
    if mode != production_mode.STANDARD and kind != layers.VIDEO:
        # Only a video ends on a picture. Ignoring the argument would hide the caller's mistake
        # behind a sound that came out fine.
        raise InvalidMode("Üretim modu yalnız video işine verilebilir.")
```

(kalan doğrulamalar olduğu gibi kalır.)

- [ ] **Step 5: Döngüyü işareti kullanacak hâle getir**

```python
    for frame in reversed(scope):
        fid = frame["id"]
        mark = _mark(kind, mode, gallery, fid)
        if mark is None:
            continue
        number, variant = family(frame)
```

ve iki `_job` çağrısı `mark`'ı taşır:

```python
            jobs.append(_job(kind, fid, number, variant, mark))
```

```python
            jobs.append(_job(kind, copy, number, variant_of(copy), mark))
```

- [ ] **Step 6: Boş batch'i erken kapat**

`if born:` satırının **üstüne**:

```python
    if not jobs:
        # Every frame in scope was dropped for want of something to end on. Nothing owed and nothing
        # started, exactly as an empty scope already is.
        return 0
```

Bu satır olmadan `test_a_linked_batch_with_nowhere_to_end_takes_nothing` boş bir listeyi plana
ekler ve koşuyu başlatırdı: cevap yine 0 olurdu, ama sebebi "iş yok" değil "boş iş listesi
gönderildi" olurdu.

- [ ] **Step 7: Takımı koştur**

Run: `python -m pytest queen-editor -q`
Expected: `test_photo_usecases.py` artık toplanıyor. Kuyruğun yedi testi yeşil, motorun dördü
kırmızı: üretici hâlâ `end` almıyor, dolayısıyla `generator.ends` her işte `[None]`.

---

### Task 3: Motorun okuduğu mod

**Files:**
- Modify: `queen-editor/backend/features/photo_generation/domain/run_loop.py`

**Interfaces:**
- Consumes: Task 1'in modülü, Task 2'nin yazdığı `mode`/`linkedTo` anahtarları, `policy.is_frame_fault`.
- Produces: `MissingEndFrame` — dışarıdan kimse yakalamıyor; `policy` onu şekline bakarak tanıyor.

- [ ] **Step 1: Import'u ve istisnayı ekle**

```python
from backend.features.photo_generation.domain import layers, policy, production_mode, queue
```

ve `UNDER` sözlüğünün üstüne:

```python
class MissingEndFrame(RuntimeError):
    """A linked video's target frame has no photo to end on.

    frame_level, so policy treats it the way it treats a graph that blew up: this one tile turns red
    and the queue goes on. The alternative -- quietly rendering a plain video instead -- would hand
    the user something other than what they asked for and say nothing about it.
    """

    frame_level = True
```

- [ ] **Step 2: Bitiş karesini seçen fonksiyonu yaz**

`_source_for`'un altına:

```python
def _end_for(job, store, slots, project, fid, source):
    """The picture this job's video arrives at, as (name, bytes); None when it arrives nowhere.

    Read at the job's turn like the source is, and for the same reason: the file is on Drive and the
    run may have started hours ago.

    A loop ends on the frame's own picture -- the very file it is being made from -- so `source` is
    handed back rather than read a second time.
    """
    mode = production_mode.of(job)
    if mode == production_mode.STANDARD:
        return None
    if mode == production_mode.LOOP:
        return source
    target = job.get("linkedTo")
    cell = slots.get(target, {}).get(layers.PHOTO) if target else None
    if not cell:
        # Deleted between the press and the render. Named in the message, because "the frame it was
        # told to end on" is the one thing the user cannot work out from the tile.
        raise MissingEndFrame(f"Bağlanacak karenin fotoğrafı yok: {target or '?'}")
    return (cell["file"], store.read(project, cell["file"]))
```

- [ ] **Step 3: Üreticiye bitiş karesini ver**

`producer.generate` çağrısı:

```python
                under = _source_for(kind, store, slots, project, fid)
                data = producer.generate(prompt, current["negative"], current["seed"],
                                         current["model"], source=under,
                                         end=_end_for(current, store, slots, project, fid, under))
```

`under` bir değişkende duruyor çünkü loop modunda bitiş karesi kaynağın **kendisi**: iki kez
okumak, aynı dosyayı Drive'dan iki kez indirmek olurdu.

Çağrı `try` bloğunun içinde kalıyor — `MissingEndFrame` bir render arızası gibi ele alınıyor,
ve üç deneme ile kare-arızası kuralı ona da olduğu gibi uygulanıyor.

- [ ] **Step 4: Dört komutu koştur**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Expected: dördü de yeşil.

---

### Task 4: Yeşil commit

- [ ] **Step 1: Yol haritasını işaretle**

`docs/superpowers/plans/2026-08-20-queen-editor-v14-roadmap.md`: 2. maddenin **İş** hücresi ✅ ile
başlar, başlıktaki sayaç `1/31` → `2/31`.

- [ ] **Step 2: Commit**

```bash
git add queen-editor docs/superpowers
git commit -F - <<'EOF'
feat(queen-editor): the queue carries a video job production mode

The mode is written when the job is queued, and so is the frame a linked video ends on.
The queue runs for hours and the gallery can be dragged while it does, so a target read
at render time would not be the one the user was looking at when they pressed.

The next frame is the gallery own next, the same reading the detail page forward arrow
already does. A frame with nothing to end on stays out of the batch and the rest go in;
if every frame in scope goes that way the answer is zero, which is what an empty scope
already answers.

The loop reads the mode and picks the ending picture: none for a plain video, the
frame own photo for a loop, the linked frame photo for a linked one. A linked target
whose photo is gone raises a frame level failure, so that one tile turns red and the
queue goes on -- rendering a plain video instead would hand the user something else and
say nothing about it.

The producer still learns nothing: it is handed a picture or it is not.

Four suites green.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** spec'in saydığı üç dosyanın üçü de bir task'ta. `production_mode.py` → Task 1;
`queue_layer.py` → Task 2; `run_loop.py` → Task 3.

**Tip tutarlılığı:** `production_mode.of(job)` iki yerden çağrılıyor ve ikisinde de bir plan satırı
alıyor. Plan satırının anahtarları `mode` ve `linkedTo` — Task 2 yazıyor, Task 3 okuyor, ikisinde de
aynı yazımla. `_mark` üç dönüş şekli taşıyor (`{}`, `{"mode": ...}`, `None`) ve döngü üçünü de ayrı
ele alıyor.

**Kontrol edilen tuzak:** `_end_for` `source`'u argüman alıyor, kendi okumuyor. Kendi okusaydı loop
modunda aynı dosya Drive'dan iki kez inerdi — bir video için iki indirme, kırk video için kırk.

**Kontrol edilen tuzak 2:** `producer.generate` çağrısı `try` bloğunun içinde ve `_end_for` de
öyle. Dışarı alınsaydı `MissingEndFrame` üç denemeye ve kare-arızası kuralına hiç uğramaz, koşuyu
ilk seferde bir istisna ile keserdi.

**Kontrol edilen tuzak 3:** `if not jobs: return 0` `plan_store.append`'in önünde ama `order_store.
write`'ın da önünde. Sonra gelseydi, hedefsiz kaldığı için hiç iş almayan bir batch yine de galeri
sırasını yeniden yazardı.

**Kontrol edilen sıra:** `_frame_after` `queue.DONE` ile karşılaştırıyor, `"done"` ile değil.
Galerinin durum kelimesi tek yerde tanımlı ve buradaki bir kopya, o kelime değiştiği gün sessizce
yanlış cevap verirdi.

**Turun içinde düzeltilen karar:** ilk yazımda `_frame_after` `index + 1`'e bakıyordu, çünkü spec
"sonraki"yi detay sayfasının ileri okuna dayandırmıştı. Kırmızı testler onu yakaladı: o ok galeriyi
aşağı, yani **filmin tersine** yürüyor. Filmin sırasını söyleyen yer `export_summary.exportable` ve
o galeriyi ters birleştiriyor — galerinin dibi filmin başı. Doğrusu `index - 1`. Spec'in 4. kararı
buna göre düzeltildi.

Bu, iki turun neden ayrı olduğunun kendisi: karar önce testte yazıldığı için, kodu yazarken yapılan
yön hatası testin kendisini yeniden yorumlamadan görülebildi.
