# Madde 429 — Kuyruğun sayacı her işi bir kez sayar, test turunun planı

> **Koşum:** bu oturumda, satır satır. Adımlar `- [ ]` ile işaretlenir. Bu turda kaynak kod
> değişmiyor; testler kırmızı commit'lenir.

**Hedef:** Planda iki satırı olan bir işin kuyruğun sayılarında bir kez sayıldığını söyleyen testler —
bugün kırmızı, ve kırmızı oldukları yer sebebi kanıtlıyor: sayılar planın satır sayısı.

**Yaklaşım:** Kural `queue.counts`'un kendisinde, dosyanın `job` ve `slots` yardımcılarıyla.
Kullanıcının iki yolu — madde 211'in düşür ve yeniden iste'si, 422'nin yeni uzunlukla Tekrar dene'si
— gerçek use case'lerle ve sahte portlarla; sayılar koşu bitince `runner.status()`'tan.

**Araçlar:** pytest.

**Spec:** [m429 test turu](../specs/2026-10-06-queen-editor-m429-kuyruk-sayaci-testler-design.md)

## Her yere geçerli kurallar

- Test adları, docstring'ler ve yorumlar **İngilizce**.
- Testler yalnız CLAUDE.md'nin dört satırıyla, olduğu gibi, paralel koşulur; `skip` / `xfail` yok.
- Yalnız `queen-editor/backend/tests/test_frame_queue.py` değişir — dalga 6'nın öteki maddelerinin
  dosyalarına dokunulmaz.

**Arayüz — uygulama turunun vereceği:** yok. `queue.counts(jobs, slots)` bugünkü imzasıyla ve bugünkü
dört anahtarla; değişen yalnız aynı işin satırlarını kaç kez saydığı.

---

## Görev 1: `backend/tests/test_frame_queue.py`

**Dosya:** Değiştir: `queen-editor/backend/tests/test_frame_queue.py`

**Kullandıkları:** `test_photo_usecases`'tan `FakeGenerator`, `ask_again`, `drop_the_video`,
`frame_with_a_photo`, `idle_runner`, `sync_runner`; `test_video_length`'ten `at`, `red_videos`;
`retry_frame`. Hepsi bugünkü imzalarıyla.

- [ ] **Adım 1: içe aktarmalar.** Dosyanın başı:

```python
"""The queue rule: the plan minus the jobs that already settled, type by type."""
from backend.features.photo_generation.domain import layers, production_mode, queue
from backend.features.photo_generation.domain.photo_name import frame_id
from backend.features.photo_generation.domain.usecases.retry_frame import retry_frame
from backend.tests.test_photo_usecases import (
    FakeGenerator,
    ask_again,
    drop_the_video,
    frame_with_a_photo,
    idle_runner,
    sync_runner,
)
from backend.tests.test_video_length import at, red_videos
```

- [ ] **Adım 2: dosyanın sonuna, `test_counts_are_read_from_the_slots`'un ardına.**

```python
# --- Each job counted once (madde 429) -----------------------------------------------------------

def test_a_job_planned_twice_is_counted_once():
    """Madde 429: a layer dropped and asked for again (madde 211), or a red video sent back at a new
    length (422), leaves two plan lines for one job. The engine makes it once, from its latest line,
    and the numbers count it once too. A frame's photo and its video stay two jobs."""
    jobs = [job(0), job(0, layers.VIDEO), job(0, layers.VIDEO)]
    taken = slots(photo_P0_0="done", video_P0_0="done")

    assert queue.counts(jobs, taken) == {"total": 2, "done": 2, "failed": 0, "failures": []}


def test_a_failed_job_planned_twice_is_one_failure():
    jobs = [job(0), job(0, layers.VIDEO), job(0, layers.VIDEO)]
    taken = slots(photo_P0_0="done", video_P0_0="failed")

    assert queue.counts(jobs, taken) == {"total": 2, "done": 1, "failed": 1,
                                         "failures": ["P0_0.png"]}


def numbers(runner):
    """What the queue panel is told once the run is through."""
    state = runner.status()
    return {key: state[key] for key in ("total", "done", "failed", "failures")}


def test_a_video_dropped_and_asked_for_again_is_counted_once():
    """Madde 211's steps: a video asked for, dropped while still owed, and a loop asked for in its
    place. The plan keeps the dropped one's line beside the new one."""
    store, record, plan_store = frame_with_a_photo()
    ask_again(store, record, plan_store, layers.VIDEO, FakeGenerator(), runner=idle_runner())
    drop_the_video(store, record, plan_store)
    runner = sync_runner()

    ask_again(store, record, plan_store, layers.VIDEO, FakeGenerator(),
              mode=production_mode.LOOP, runner=runner)

    assert numbers(runner) == {"total": 2, "done": 2, "failed": 0, "failures": []}


def test_a_red_video_sent_back_at_a_new_length_is_counted_once():
    """Madde 422: Tekrar dene writes a red video's line again at the project's length now."""
    store, record, plan_store = red_videos(0, seconds=4)
    runner = sync_runner()

    retry_frame(runner, store, record, plan_store, {layers.VIDEO: FakeGenerator()},
                lambda: "t", "düğün", "0_a", length=at(12))

    assert numbers(runner) == {"total": 2, "done": 2, "failed": 0, "failures": []}


def test_a_red_video_that_fails_again_at_a_new_length_is_one_failure():
    store, record, plan_store = red_videos(0, seconds=4)
    runner = sync_runner()

    retry_frame(runner, store, record, plan_store,
                {layers.VIDEO: FakeGenerator(fail_on=["kadın dönüyor"])},
                lambda: "t", "düğün", "0_a", length=at(12))

    assert numbers(runner) == {"total": 2, "done": 1, "failed": 1, "failures": ["0_a.png"]}
```

## Görev 2: Koş, kırmızıyı oku, commit'le

- [ ] **Adım 1: dört satır, paralel, olduğu gibi.**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: `queen-editor` pytest'inde **tam beş** kırmızı — yeni beş test, hepsi aynı yerden:
sayılar planın satır sayısı (`total` 3; bitmişse `done` 3, kırmızıysa `failed` 2 ve karenin dosyası
`failures`'ta iki kez). Öteki üç satır yeşil. **Kırmızı başka bir yerden geliyorsa sebep
kanıtlanmamıştır:** commit yok, madde *"bulamadım"* diye döner.

- [ ] **Adım 2: commit** — spec, plan ve test dosyası.

```powershell
git add docs/specs/2026-10-06-queen-editor-m429-kuyruk-sayaci-testler-design.md docs/plans/2026-10-06-queen-editor-m429-kuyruk-sayaci-testler-plan.md queen-editor/backend/tests/test_frame_queue.py
git commit -m @'
test(queen-editor): Madde 429 red -- a job with two plan lines is counted once in total, done, failed and failures, after a layer dropped and asked for again and after Tekrar dene at a new H3 length

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
