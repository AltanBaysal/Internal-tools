# Madde 429 — Kuyruğun sayacı her işi bir kez sayar, uygulama turunun planı

> **Koşum:** bu oturumda, satır satır. Adımlar `- [ ]` ile işaretlenir. Testler test turunda
> commit'lendi; bu tur yalnız onların söylediği kodu yazar.

**Hedef:** `queue.counts` her (kare, katman) işini bir kez saysın — motorun saydığı gibi.

**Yaklaşım:** Motorun kuralı `_latest_per_frame` satırları kare ve katman başına tutar; `counts`
saymadan önce planı ondan geçirir. `open_jobs` onu tip tip çağırdığı için orada bir şey değişmez.

**Araçlar:** Python, pytest.

**Spec:** [m429 uygulama turu](../specs/2026-10-06-queen-editor-m429-kuyruk-sayaci-uygulama-design.md)

## Her yere geçerli kurallar

- Kod ve yorumlar **İngilizce**; yorum nedenini söyler, yalnız bugün doğru olanı.
- Testler yalnız CLAUDE.md'nin dört satırıyla, olduğu gibi, paralel koşulur; `skip` / `xfail` yok.
- Yalnız `queen-editor/backend/features/photo_generation/domain/queue.py` değişir; testlere
  dokunulmaz.

**Arayüz:** `counts(jobs, slots)` → `{"total", "done", "failed", "failures"}`, bugünkü gibi.
`_latest_per_frame(jobs)` → satır listesi, plandaki sırasıyla; artık (kare, katman) başına bir satır.

---

## Görev 1: `domain/queue.py`

**Dosya:** Değiştir: `queen-editor/backend/features/photo_generation/domain/queue.py`

- [ ] **Adım 1: `_latest_per_frame` kare ve katman başına tutar.** Belgesinin ilk satırı ve sonuna bir
  paragraf; anahtar `(job["id"], type_of(job))`:

```python
def _latest_per_frame(jobs):
    """One line per frame and layer: the last one written for it, in the plan's own order.

    The status lives per (frame, layer) while the plan may hold several lines for that pair -- a
    layer asked for, dropped, and asked for again appends a line each time and the old ones stay.
    Reopening the cell reopens every one of them, so the frame was owed the same video twice and the
    engine made it from the oldest line: the job that had been dropped. Asking for loop gave back the
    standard video that was deleted (madde 211).

    The plan is not corrected -- it records what was asked for, and it was asked for three times.
    What is single here is the debt, because the status that settles it is single.

    Keyed by the layer as well as the frame: the counter reads the whole plan at once, where a
    frame's photo and its video are two jobs (madde 429).
    """
    latest = {}
    for job in jobs:
        latest[(job["id"], type_of(job))] = job
    # Rebuilt by walking the plan rather than the dict, so each surviving line keeps the place its
    # own line stands in and the gallery's order still decides ties.
    return [job for job in jobs if latest[(job["id"], type_of(job))] is job]
```

- [ ] **Adım 2: `counts` planı saymadan önce ondan geçirir.**

```python
def counts(jobs, slots):
    """The numbers the status endpoint publishes -- read from disk rather than from a run's memory,
    so they are still right after the server restarts.

    Each job once, however many lines the plan holds for it: the engine makes it once, from its
    latest line, and counting lines said one more for every layer asked for again (madde 429).

    Looked up by identity, published as file names: the screen marks its red tiles by file.
    """
    jobs = _latest_per_frame(jobs)
    failures = [photo_file(j["id"]) for j in jobs if _status(slots, j) == FAILED]
    return {"total": len(jobs),
            "done": sum(1 for j in jobs if _status(slots, j) == DONE),
            "failed": len(failures),
            "failures": failures}
```

## Görev 2: Koş, yeşili oku, commit'le

- [ ] **Adım 1: dört satır, paralel, olduğu gibi.**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: dört satır da yeşil; `queen-editor` pytest'inde test turunun beş kırmızısı yeşil.

- [ ] **Adım 2: commit** — spec, plan ve `queue.py`.

```powershell
git add docs/superpowers/specs/2026-10-06-queen-editor-m429-kuyruk-sayaci-uygulama-design.md docs/superpowers/plans/2026-10-06-queen-editor-m429-kuyruk-sayaci-uygulama-plan.md queen-editor/backend/features/photo_generation/domain/queue.py
git commit -m @'
fix(queen-editor): 429 -- the queue counts each job once: counts reads the plan through the engine's own latest line per frame and layer, so a layer dropped and asked for again, or a red video sent back at a new H3 length, no longer adds one to total, done, failed and failures

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
