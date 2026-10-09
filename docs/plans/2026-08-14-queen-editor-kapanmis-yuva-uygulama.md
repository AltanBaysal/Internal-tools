# Kapanmış yuva: İMPLEMENTASYON döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `92bf10b`'deki dört kırmızı testi yeşile çevirmek.

**Architecture:** Tek dosya, tek dal: iş eklenmeden önce kapanmış yuva açılır.

**Tech Stack:** Python, pytest.

**Tasarım:** [implementasyon spec'i](../specs/2026-08-14-queen-editor-kapanmis-yuva-uygulama-design.md)

## Global Constraints

- **Testler değişmiyor.** `92bf10b`'deki altı test sözleşme.
- Yorum ve docstring **İngilizce**.
- Commit mesajında **çift tırnak yok**.
- Komut: `python -m pytest queen-editor/backend/tests -q`

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `.../photo_generation/domain/usecases/queue_layer.py` | katman işini kuyruğa koymak | kapanmış yuva açılır |

---

### Task 1: Kapanmış yuva, iş eklenmeden açılır

**Files:**
- Modify: `queen-editor/backend/features/photo_generation/domain/usecases/queue_layer.py`

- [ ] **Step 1: `queue` içe aktarılır**

```python
from backend.features.photo_generation.domain import layers, queue
```

- [ ] **Step 2: Yuvaların anlık hâli okunur**

`taken = known_ids(...)` satırının altına:

```python
    # What the log last said about each slot. Read once: the only cells consulted below belong to
    # frames that already exist, and the rows written during the loop are about other slots.
    slots = record.slots(project)
```

- [ ] **Step 3: Kaynak karenin yuvası açılır**

```python
        if kind not in held:
            jobs.append(_job(kind, fid, number, variant))
            owed -= 1
```

şununla değişir:

```python
        if kind not in held:
            settled = slots.get(fid, {}).get(kind)
            if settled:
                # Free is not the same as never written about: emptying the queue writes removed and
                # deleting a layer writes deleted, and both close the job for good. queued is the one
                # line that reopens it -- the same line Tekrar dene writes, with the slot's own file
                # name -- and without it the job appended below lands in a plan the queue cannot see
                # it in. Reported 2026-08-14: after emptying the queue, sound could never be queued
                # again.
                record.mark(project, fid, kind, settled["file"], queue.QUEUED, now())
            jobs.append(_job(kind, fid, number, variant))
            owed -= 1
```

- [ ] **Step 4: Takım**

Run: `python -m pytest queen-editor/backend/tests -q`
Expected: 603 geçen, 0 düşen.

---

### Task 2: Commit

- [ ] **Step 1: Commit**

```bash
git add queen-editor/backend docs/superpowers
git commit -F - <<'EOF'
feat(queen-editor): let a settled slot be asked for again

The four tests from the previous commit go green.

A job is known by its frame and its layer, and a slot that has been written
about is settled for good -- queued is the only status that reopens one.
Emptying the queue writes removed on every waiting job, so asking for that
layer again appended a job the queue could not see: the run started, found
nothing, and reported the previous batch total. The user could not queue sound
again after emptying the queue, and no amount of asking would have helped.

Queueing a layer now writes the reopening line first, with the slot own file
name, exactly as Tekrar dene does. Loosening what counts as owed would have
been shorter and wrong: a job pulled out of the queue would come back on its
own, and emptying the queue would empty nothing. What reopens a job is being
asked for again, and the log says so.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** açan satır → Step 3. Eksik yok.

**Kontrol edilen dal:** `kind not in held` yalnız dolu olmayan yuvalar için doğru, yani `DONE` ve
`FAILED` bu dala hiç girmiyor ve kopya kare yolu değişmeden duruyor — iki bekçi testi bunu tutuyor.

**Kontrol edilen sıra:** `slots` döngüden **önce** okunuyor. Döngü içinde yazılan satırlar ya
başka bir karenin yuvasına (`record.mark`) ya da yeni doğan kopyalara (`carry_layers`) ait,
dolayısıyla anlık görüntü bayatlamıyor.

**Kontrol edilen alternatif:** `queue.is_open`'a `REMOVED` eklemek daha kısa olurdu ama "Kuyruğu
boşalt"ı anlamsızlaştırırdı — çıkarılan iş kimse istemeden geri gelirdi.