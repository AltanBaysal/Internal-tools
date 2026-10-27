# Kapanmış yuva: TEST döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Kuyruktan çıkarılmış ya da silinmiş bir katmanın yeniden istenebildiğini sınayan testleri
yazmak, takımı kırmızı commit'lemek.

**Architecture:** Tek dosya, bir yardımcı ve beş test.

**Tech Stack:** pytest.

**Tasarım:** [test spec'i](../specs/2026-08-14-queen-editor-kapanmis-yuva-testler-design.md)

## Global Constraints

- **Bu döngüde üretim kodu değişmiyor.**
- Test adları ve docstring'ler **İngilizce**.
- Commit mesajında **çift tırnak yok**.
- Komut: `python -m pytest queen-editor/backend/tests -q`

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `queen-editor/backend/tests/test_photo_usecases.py` | kuyruk kullanım senaryoları | 1 yardımcı + 5 test |

---

### Task 1: Kapanmış yuvanın testleri

**Files:**
- Modify: `queen-editor/backend/tests/test_photo_usecases.py`

- [ ] **Step 1: Yardımcıyı ekle**

`test_a_layer_job_is_planned_with_no_seed_of_its_own`'ın hemen altına:

```python
def settled_slot_project(layer, status):
    """A frame with a photo and a video, and a `layer` slot whose last line settled it.

    This is what emptying the queue leaves behind: nothing was produced, but the slot has been
    written about, and a written slot is closed for good unless something reopens it.
    """
    store, record = FakeStore(), FakeRecord()
    plan_store = FakePlanStore(frames=[frame(0)])
    record.append("düğün", {"file": "0_a.png", "frame": "0_a", "layer": "photo", "status": "done"})
    record.append("düğün", {"file": "0_a_V1_0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done"})
    store.files["0_a.png"] = b"PNGDATA"
    store.files["0_a_V1_0.mp4"] = b"MP4DATA"
    record.mark("düğün", "0_a", layer, "0_a.png", status, "t")
    return store, record, plan_store


def ask_again(store, record, plan_store, layer, generator, files=None):
    return queue_layer(sync_runner(), store, record, plan_store, FakeOrderStore(),
                       {layer: generator}, lambda: "t", "düğün", layer, files=files)
```

- [ ] **Step 2: Beş testi ekle**

```python
def test_a_sound_pulled_out_of_the_queue_can_be_asked_for_again():
    """2026-08-14: the queue was emptied and sound could never be queued again. Emptying writes
    removed on the slot, a written slot is settled, and queue_layer appended a job nobody could
    see -- the run ended having found nothing and reported the previous batch's total."""
    store, record, plan_store = settled_slot_project(layers.AUDIO, queue.REMOVED)
    generator = FakeGenerator()

    added = ask_again(store, record, plan_store, layers.AUDIO, generator)

    assert added == 1
    # Not the plan's contents: whether the sound was actually made.
    assert len(generator.calls) == 1
    assert [name for name, _data in store.saved] == ["0_a_V1_0_S1_0.wav"]


def test_a_video_pulled_out_of_the_queue_can_be_asked_for_again():
    """The hole is not the sound layer's: every layer is closed by the same rule."""
    store, record, plan_store = settled_slot_project(layers.VIDEO, queue.REMOVED)
    generator = FakeGenerator()

    ask_again(store, record, plan_store, layers.VIDEO, generator)

    assert len(generator.calls) == 1


def test_a_deleted_layer_can_be_asked_for_again():
    """A deleted layer frees its slot without putting the frame back in line -- which is right, and
    is also why asking for it again has to do the putting back."""
    store, record, plan_store = settled_slot_project(layers.AUDIO, queue.DELETED)
    generator = FakeGenerator()

    ask_again(store, record, plan_store, layers.AUDIO, generator)

    assert len(generator.calls) == 1


def test_reopening_a_settled_slot_is_written_down():
    """queued is the one written status that reopens a job, so the reopening is a line in the log
    rather than an assumption. Without this the hole could be closed by loosening is_open instead,
    and the queue's single rule would live in two places."""
    store, record, plan_store = settled_slot_project(layers.AUDIO, queue.REMOVED)

    ask_again(store, record, plan_store, layers.AUDIO, FakeGenerator())

    said = [row["status"] for row in record.rows if row.get("layer") == "audio"]
    assert queue.QUEUED in said
    assert said.index(queue.QUEUED) > said.index(queue.REMOVED)


def test_a_failed_layer_stays_out_of_the_scope_nobody_picked():
    """A guard, not a hole: a failed slot counts as taken, so the frame leaves the panel's own
    scope and is rescued by Tekrar dene alone -- one frame never gets two ways to be produced at
    once. Reopening settled slots must not drag failed ones back in."""
    store, record, plan_store = settled_slot_project(layers.AUDIO, queue.FAILED)
    generator = FakeGenerator()

    added = ask_again(store, record, plan_store, layers.AUDIO, generator)

    assert added == 0
    assert generator.calls == []


def test_a_failed_layer_picked_by_hand_becomes_a_frame_of_its_own():
    """The other guard: picking the frame says these ones, and asking for a layer it already holds
    is asking for a second one -- which is born as a copy frame (madde 25), never written over the
    first. This path works today and must keep working."""
    store, record, plan_store = settled_slot_project(layers.AUDIO, queue.FAILED)
    generator = FakeGenerator()

    ask_again(store, record, plan_store, layers.AUDIO, generator, files=["0_a.png"])

    assert len(generator.calls) == 1
    # The new identity is the frame's, not the file's: a sound is named after the video it sits on,
    # and the copy carries its source's video -- so the name is no way to tell the two apart.
    made = [row for row in record.rows
            if row.get("layer") == "audio" and row.get("status") == "done"]
    assert len(made) == 1
    assert made[0]["frame"] != "0_a"
```

- [ ] **Step 3: Koş**

Run: `python -m pytest queen-editor/backend/tests/test_photo_usecases.py -q`
Expected: 4 düşen (ilk üçü ve `..._is_written_down`), iki bekçi geçiyor.

---

### Task 2: Takım ve kırmızı commit

- [ ] **Step 1: Tam takım**

Run: `python -m pytest queen-editor/backend/tests -q`
Expected: 4 düşen, 599 geçen.

- [ ] **Step 2: Commit**

```bash
git add queen-editor/backend/tests docs/superpowers
git commit -F - <<'EOF'
test(queen-editor): ask for a layer that was pulled out of the queue

Red on purpose -- the implementation cycle turns these green.

Emptying the queue writes removed on every waiting job's slot. A job is known
by its frame and its layer, and a written slot is settled for good: queued is
the only status that reopens one. queue_layer appends a job and never writes
that line, so after emptying the queue the same layer can never be asked for
again -- the job lands in the plan, the queue cannot see it, and the run ends
having found nothing.

Four failures. Three ask for a sound, a video and a deleted layer to be made
after their slot was settled, and none of them are made today. The fourth asks
that the reopening be a line in the log rather than an assumption, so the hole
cannot be closed by loosening what counts as owed and splitting the queue's
one rule across two places.

One stays green: a failed layer becomes a frame of its own. A failed slot
counts as taken, so asking again means asking for a second one, and that path
already works. It is here so the fix cannot quietly take it away.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** 1 → sound · 2 → video · 3 → deleted · 4 → written down · 5 → guard. Eksik yok.

**Kontrol edilen tuzak:** `settled_slot_project` plana **iş eklemiyor** — yalnız üretilmiş bir
fotoğraf ve video ile kapanmış bir yuva bırakıyor. Plana bekleyen bir iş konsaydı `queue_layer`
onu da koşturur ve üreticinin çağrılması yeni işi değil eskisini kanıtlardı.

**Kontrol edilen varsayım:** `FakePlanStore.read` kimliği kendisi dolduruyor (`frame(0)` → `0_a`),
yani plan satırının `id` taşımaması sorun değil.

**Bekçiyi yazarken düzeltilen iki varsayım.**

1. "Başarısız katman kopya kare doğurur" **seçim olmadan yanlış**: başarısız yuva dolu sayıldığı
   için kare varsayılan kapsamdan tümüyle çıkıyor ve hiçbir şey olmuyor. Bekçi ikiye ayrıldı —
   biri kapsam dışı kaldığını, öteki elle seçilince kopya doğduğunu söylüyor.
2. "Kopya kare farklı bir dosya adı üretir" **yanlış**: ses, üstüne bindiği **videodan** ad alıyor
   ve kopya kaynağının videosunu taşıyor, yani dosya adı ikisini ayırt etmiyor. İddia kaydın
   yazdığı kare kimliğine taşındı. Kimliğin nasıl üretildiği (`P0_1`) yine tahmin edilmiyor —
   yalnız kaynağınki **olmadığı** söyleniyor.
