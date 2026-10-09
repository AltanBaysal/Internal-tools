# Madde 423 — Export'un toplamı her videonun kendi uzunluğundan, uygulama turunun planı

> **Koşum:** bu oturumda, satır satır, 423'ün worktree'sinde. Kod yazılır, dört satır koşulur,
> suite yeşile döner, ve kod commit'lenir.

**Hedef:** Videonun satırındaki uzunluğu katlanıştan karta, karttan kopyaya ve özete taşımak; özetin
toplamı her videonun kendi uzunluğu olsun, satırı söylemeyeninki grafiğin uzunluğu.

**Yaklaşım:** Galeri kartından geçen yol — `renderSeconds`'ın yolu: `slots` → `card` → `CARRIED` →
`export_summary`. Yeni dosya, yeni parametre ya da yeni bağlantı yok.

**Araçlar:** Python, pytest.

**Spec:** [m423 uygulama turu](../specs/2026-10-06-queen-editor-m423-export-toplami-uygulama-design.md),
[m423 test turu](../specs/2026-10-06-queen-editor-m423-export-toplami-testler-design.md)

## Her yere geçerli kurallar

- Kod, yorum ve belge İngilizce; yorum *neden*i ve yalnız bugün doğru olanı söyler.
- Testlere dokunulmaz; testlerin anlattığından fazlası yazılmaz. `dist` değişmez.
- Kırmızı suite `477bdcdb`: `test_export_total.py`'de 7 kırmızı.

---

## Görev 1: Katlanış uzunluğu taşır

**Dosyalar:** Değiştir: `queen-editor/backend/features/photo_generation/data/photo_record.py`
(`slots`), `queen-editor/backend/features/photo_generation/domain/ports.py` (`PhotoRecord.slots`'un
belgesi)

- [ ] **Adım 1:** `slots`'ta `renderSeconds`'ın bloğunun altına:

```python
            if isinstance(row.get("seconds"), (int, float)):
                # Only an H3 video made since madde 422 says how long it runs; the export counts any
                # other at its graph's own length (madde 423).
                cell["seconds"] = row["seconds"]
```

- [ ] **Adım 2:** `slots`'un belgesi: anahtar listesine `[, "seconds"]`; *"A produced layer's line
  says how many seconds the model worked on it."*'in ardına *"A video made at a chosen length says
  how long it runs."*; *"None of the four"* → *"None of the five"*.
- [ ] **Adım 3:** `ports.py`'de `PhotoRecord.slots`'un belgesi: anahtar listesine `[, "seconds"]`,
  ve satır: *`"seconds"` only on a video made at a chosen length (madde 422): how long it runs.*

## Görev 2: Kart ve kopya uzunluğu taşır

**Dosyalar:** Değiştir: `queen-editor/backend/features/photo_generation/domain/usecases/list_frames.py`
(`_per_layer`'ın belgesi, `card`), `queen-editor/backend/features/photo_generation/domain/copy_frame.py`
(`CARRIED`)

- [ ] **Adım 1:** `card`'da `renderSeconds`'ın altına:

```python
                # How long each layer runs, where its line says (madde 423): a video made at a
                # chosen length. Not "seconds" -- renderSeconds beside it is another length.
                "lengths": _per_layer(cells, "seconds"),
```

- [ ] **Adım 2:** `_per_layer`'ın belgesi: *"which mode made it, which picture it arrived at, and
  how long the model worked on it"* → *"which mode made it, which picture it arrived at, how long
  the model worked on it, and how long it runs"*.
- [ ] **Adım 3:** `CARRIED`:

```python
# What a carried layer keeps about how it was made: the frame's own map, and the field the row
# takes. One file, two frames holding it -- without these the twin's tile would read video while the
# original reads loop, its detail page could not say where the video arrived, it would show no
# production time where the original shows one, and the export would count one video at two lengths.
CARRIED = (("modes", "mode"), ("endsOn", "endsOn"), ("renderSeconds", "renderSeconds"),
           ("lengths", "seconds"))
```

## Görev 3: Özet her videonun uzunluğunu toplar

**Dosyalar:** Değiştir:
`queen-editor/backend/features/photo_generation/domain/usecases/export_summary.py`,
`queen-editor/backend/features/photo_generation/data/comfy_h3_video_generator.py` (`seconds()`'ın
belgesi), `queen-editor/backend/main.py` (özetin bağlantısındaki yorum)

- [ ] **Adım 1:** Modül belgesinin üçüncü paragrafı:

```python
The length is not measured: each video runs as long as it was made. An H3 video made since madde 422
says it on its line; any other -- every video before 422, and every WAN video -- ran as long as its
graph says (madde 423). Measuring each file would cost a process per video every time the screen
asks, for a number already written down.
```

- [ ] **Adım 2:** `export_summary`'nin belgesi ve toplamı:

```python
def export_summary(record, store, plan_store, order_store, seconds, project):
    """`seconds()` answers how long a video made at its graph's own length runs.

    Asked rather than known: the length is the video graph's own setting, and a copy of the number
    here would go on being quoted after the graph moved. It is this session's graph, and a line does
    not say which model made its video -- so a video another session's model made at its own graph's
    length is counted at this one's.
    """
    # Raises ProjectMissing when there is no such project.
    frames = list_frames(record, store, plan_store, order_store, project)
    videos = exportable(frames)
    graph = seconds()
    # A video whose sound blew up is silent too: what is not there cannot be laid over it.
    silent = [frame for frame in videos
              if not frame.get("layers", {}).get(layers.AUDIO)
              or layers.AUDIO in frame.get("failed", [])]
    return {"videos": len(videos),
            "seconds": sum(frame["lengths"].get(layers.VIDEO, graph) for frame in videos),
            "silent": len(silent),
            ...
```

  (`withoutVideo` ve `folder` aynen.)
- [ ] **Adım 3:** `ComfyH3VideoGenerator.seconds()`'ın belgesi: *"The export summary quotes it for
  every video"* → *"The export summary counts every video whose line says no length at it"*.
- [ ] **Adım 4:** `main.py`, `export_summary=`'nin üstündeki yorum:

```python
    # How long a video made at its graph's own length runs is that graph's setting, so the producer
    # that owns the graph answers it; a video made at a chosen length says its own on its line
    # (madde 423).
```

## Görev 4: Dört satır, yeşil, commit

- [ ] **Adım 1:** Dört satır, yazıldığı gibi, paralel. Beklenen: hepsi yeşil — `queen-editor`'ün
  pytest'inde 1501 geçti.
- [ ] **Adım 2:**

```powershell
git add docs/specs/2026-10-06-queen-editor-m423-export-toplami-uygulama-design.md docs/plans/2026-10-06-queen-editor-m423-export-toplami-uygulama-plan.md queen-editor/backend/features/photo_generation/data/photo_record.py queen-editor/backend/features/photo_generation/domain/ports.py queen-editor/backend/features/photo_generation/domain/usecases/list_frames.py queen-editor/backend/features/photo_generation/domain/copy_frame.py queen-editor/backend/features/photo_generation/domain/usecases/export_summary.py queen-editor/backend/features/photo_generation/data/comfy_h3_video_generator.py queen-editor/backend/main.py
git commit -m 'feat(queen-editor): 423 -- the export total is each video own length added up' -m 'The line length rides the fold, the card (lengths) and a copy frame, and the summary adds them; a video whose line says none counts at the graph length, as before. Screen unchanged. Four lines green.' -m 'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>'
```

---

# İnceleme turu — satır üretilen videonun uzunluğunu söyler

**Hedef:** Video satırı işin uzunluğunu değil, üreticinin yaptığı videonun uzunluğunu söylesin.
**Yaklaşım:** Üreticilerin bugünkü `seconds()`'ı `seconds(asked=None)` olur; döngünün `_made_with`'i
video satırına onun cevabını yazar. Kırmızı suite `2ea4ebed`: 4 kırmızı.
**Kural:** `run_loop.py`'de yalnız `_made_with` ve çağrıldığı yer değişir — koşu dalı 429'la aynı
dosyanın başka yerlerine dokundu, birleştirmeyi koordinatör yapar.

## Görev 5: Port ve üreticiler

**Dosyalar:** Değiştir: `queen-editor/backend/features/photo_generation/domain/ports.py`,
`queen-editor/backend/features/photo_generation/data/comfy_h3_video_generator.py`,
`queen-editor/backend/features/photo_generation/data/comfy_video_generator.py`

- [ ] **Adım 1:** `ports.py`, `BatchPhotoGenerator`'ın altına:

```python
class VideoGenerator(PhotoGenerator, Protocol):
    """A video producer: it also says how long the videos it makes run (madde 423). The loop asks it
    of the video producer alone, and writes the answer on the video's row."""

    def seconds(self, asked: int | None = None) -> float:
        """How long a video asked to run `asked` seconds comes out. H3 makes what it is asked; WAN
        makes its graph's own whatever it is asked ("h3e özel"). None -- a job that asked for no
        length -- is the graph's own, which is also what the export summary counts a row that says
        no length at."""
        ...
```

- [ ] **Adım 2:** `PhotoGenerator.generate`'in `seconds` paragrafının sonuna: *"How long the video
  then runs is the producer's to say (VideoGenerator.seconds)."* `PhotoRecord.slots`'un belgesindeki
  satır: *`"seconds"` on a video produced since madde 423 (an H3 one since 422): how long it runs.*
- [ ] **Adım 3:** H3:

```python
    def seconds(self, asked=None):
        """How long a video asked to run `asked` seconds comes out: what it is asked, since that is
        what the Director is told (madde 422); asked none, the graph's own, as the I2VA graph's
        Director has it. The loop writes the answer on the video's row (madde 423), and the export
        summary counts a row that says no length at the graph's own. That the two graphs agree is
        held by test_workflow_asset."""
        if asked is not None:
            return asked
        standard = self._load(self._workflow_path)
        return float(standard[DIRECTOR_NODE]["inputs"]["duration"])
```

- [ ] **Adım 4:** WAN:

```python
    def seconds(self, asked=None):
        """How long a render runs, as the graph has it -- whatever it is asked: only H3's length is
        chosen ("h3e özel"), so a job an H3 session queued at a length comes out here at the graph's
        (madde 423). Float on purpose: the field is one, and rounding it here would be a second
        version of the truth as surely as a copy would be."""
        standard = self._load(self._workflow_path, STANDARD_NODES)
        return float(standard[DURATION_NODE]["inputs"]["value"])
```

## Görev 6: Döngü üreticinin cevabını yazar

**Dosyalar:** Değiştir: `queen-editor/backend/features/photo_generation/domain/run_loop.py`
(`_made_with` ve çağrıldığı yer)

- [ ] **Adım 1:** `_made_with`:

```python
def _made_with(job, end, kind, producer):
    """What the produced row says about how it was made, beyond its words and its seed.

    The mode, the name of the picture the video arrived at, and how long a video runs -- each only
    when there is one.

    Which jobs carry a mode is the queue's rule (queue_layer puts the field on video jobs alone) and
    it is not written a second time here, where the two could drift apart. A photo row saying
    standard would be a field that means nothing on nearly every line it appears on.

    The ending picture is named by the file the render was actually handed, not by the target's
    identity. The detail page prints that name, and an identity resolved later can resolve to
    nothing: the frame a video ends on can be deleted while the video stays.

    A video's length is its producer's answer, not the job's: the job carries the length it was
    queued with, and the model that makes it may not make that length -- an H3 session's job made in
    a later WAN session comes out at WAN's own (madde 423). The export adds these up.
    """
    made = {"mode": production_mode.of(job)} if job.get("mode") else {}
    if end:
        made["endsOn"] = end[0]
    if kind == layers.VIDEO:
        made["seconds"] = producer.seconds(job.get("seconds"))
    return made
```

- [ ] **Adım 2:** Çağrı: `**_made_with(current, ending)` → `**_made_with(current, ending, kind,
  producer)`.

## Görev 7: Belgeler bugünü söyler

**Dosyalar:** Değiştir: `data/photo_record.py`, `domain/usecases/list_frames.py`,
`domain/usecases/export_summary.py` (`queen-editor/backend/features/photo_generation/` altında),
`queen-editor/backend/main.py`

- [ ] **Adım 1:** `photo_record.slots`: belgede *"A video made at a chosen length says how long it
  runs."* → *"A produced video's line says how long it runs, since madde 423."*; yorum:

```python
                # How long a video runs, as its producer said (madde 423); a line written before
                # says nothing, and the export counts it at its graph's own length.
```

- [ ] **Adım 2:** `list_frames`'in `lengths` yorumu:

```python
                # How long each layer runs, where its line says: a video produced since madde 423.
                # Not "seconds" -- renderSeconds beside it is another length.
```

- [ ] **Adım 3:** `export_summary` modül belgesinin üçüncü paragrafı:

```python
The length is not measured: each video's line says how long it runs -- its producer's answer for
the video it made (madde 423). A line written before that says nothing, and its video ran as long
as its graph says. Measuring each file would cost a process and a Drive read per video, every time
the screen asks.
```

  ve fonksiyonun belgesi:

```python
    """`seconds()` answers how long a video made at its graph's own length runs -- what a line that
    says no length is counted at.

    Asked rather than known: the length is the video graph's own setting, and a copy of the number
    here would go on being quoted after the graph moved. It is this session's graph, and such a
    line -- written before madde 423 -- does not say which model made its video, so one another
    session's model made is counted at this one's.
    """
```

- [ ] **Adım 4:** `main.py`, `export_summary=`'nin üstündeki yorum:

```python
    # How long a video runs is on its line, its producer's answer (madde 423). A line written before
    # says nothing, and its video ran as long as the graph says -- so the producer that owns the
    # graph answers for it.
```

## Görev 8: Dört satır, yeşil, commit

- [ ] **Adım 1:** Dört satır, paralel. Beklenen: hepsi yeşil — `queen-editor`'ün pytest'inde 1507
  geçti.
- [ ] **Adım 2:**

```powershell
git add docs/specs/2026-10-06-queen-editor-m423-export-toplami-uygulama-design.md docs/plans/2026-10-06-queen-editor-m423-export-toplami-uygulama-plan.md queen-editor/backend/features/photo_generation/domain/ports.py queen-editor/backend/features/photo_generation/data/comfy_h3_video_generator.py queen-editor/backend/features/photo_generation/data/comfy_video_generator.py queen-editor/backend/features/photo_generation/domain/run_loop.py queen-editor/backend/features/photo_generation/data/photo_record.py queen-editor/backend/features/photo_generation/domain/usecases/list_frames.py queen-editor/backend/features/photo_generation/domain/usecases/export_summary.py queen-editor/backend/main.py
git commit -m 'feat(queen-editor): 423 -- a video row says how long the made video runs' -m 'Video producers answer seconds(asked): H3 the length asked or its graph 4, WAN its graph 5 whatever it is asked. The loop writes that answer on every produced video row instead of the job length, so a job queued for H3 and made by WAN says 5, and every new WAN row carries its length. The export keeps the graph fallback only for rows written before. Four lines green.' -m 'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>'
```
