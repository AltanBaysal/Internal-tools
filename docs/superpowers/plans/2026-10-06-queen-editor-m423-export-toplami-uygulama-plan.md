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
git add docs/superpowers/specs/2026-10-06-queen-editor-m423-export-toplami-uygulama-design.md docs/superpowers/plans/2026-10-06-queen-editor-m423-export-toplami-uygulama-plan.md queen-editor/backend/features/photo_generation/data/photo_record.py queen-editor/backend/features/photo_generation/domain/ports.py queen-editor/backend/features/photo_generation/domain/usecases/list_frames.py queen-editor/backend/features/photo_generation/domain/copy_frame.py queen-editor/backend/features/photo_generation/domain/usecases/export_summary.py queen-editor/backend/features/photo_generation/data/comfy_h3_video_generator.py queen-editor/backend/main.py
git commit -m 'feat(queen-editor): 423 -- the export total is each video own length added up' -m 'The line length rides the fold, the card (lengths) and a copy frame, and the summary adds them; a video whose line says none counts at the graph length, as before. Screen unchanged. Four lines green.' -m 'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>'
```
