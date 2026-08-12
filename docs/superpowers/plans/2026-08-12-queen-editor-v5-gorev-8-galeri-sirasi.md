# Görev 8 — Galeri sırası ve sürükleme · Uygulama Planı

> **Çalıştıran ajan için:** GEREKLİ ALT BECERİ: superpowers:executing-plans.

**Amaç:** Galerinin sırası üretimin sırası olur — sıradaki iş, galerinin en altındaki açık iştir —
ve her kare sürüklenebilir hâle gelir.

**Mimari:** `queue.open_jobs` isteğe bağlı bir sıra listesi alır ve tür içinde ona göre dizer. Sıra
deposu `run_loop`'a anahtarlı bir parametre olarak taşınır; zincirdeki her halka onu geçirir. Ön
yüzde tutma kuralı ve ipucu kalkar.

**Yığın:** Flask (sync) + React 18 · pytest (sahte port'lar) · vitest + jsdom.

**Spec:** [Görev 8 tasarımı](../specs/2026-08-12-queen-editor-v5-gorev-8-galeri-sirasi-design.md)

## Global kısıtlar

- **Full TDD:** önce kırmızı test.
- Yeni parametrenin adı her halkada aynı: `order_store`, **anahtarlı ve varsayılanı `None`**.
  Verilmediğinde davranış bugünküyle birebir aynı olmalı.
- Dil ayrımı: yorum/docstring/test adı/commit **İngilizce**, kullanıcı metni **Türkçe**.
- **Yorum sürüklenmez:** `retry_frame`'in "renders in the plan's own order" cümlesi bu görevde
  yanlışa döner, düzeltilir.
- Test komutları: `npm test --prefix queen-editor/frontend -- --run` ·
  `python -m pytest queen-editor -q` · derleme `npm run build --prefix queen-editor/frontend`.
- **Tek commit**, görevin sonunda, `dist/` ile birlikte.

---

### Görev 1: Kuyruk galeriyi alttan yukarı okur

**Dosyalar:**
- Değiştir: `queen-editor/backend/features/photo_generation/domain/queue.py:50-64`
- Test: `queen-editor/backend/tests/test_queue.py`

**Arayüzler:**
- Üretir: `open_jobs(jobs, slots, order=())` — `order` sıra dosyasının kendi listesi (galeri sırası,
  en yeni önce). Verilmezse dizilim planın.

- [ ] **Adım 1: Testleri yaz (kırmızı test)**

`test_queue.py`'ye, dosyanın kendi yardımcılarıyla aynı biçimde:

```python
def test_a_type_is_done_in_the_gallery_s_own_order_read_from_the_bottom():
    # The gallery is newest-first, so its bottom is what gets produced first.
    jobs = [job("P0_0"), job("P1_0"), job("P2_0")]
    order = ["P1_0", "P0_0", "P2_0"]          # what the user dragged, top first

    owed = queue.open_jobs(jobs, {}, order)

    assert [j["id"] for j in owed] == ["P2_0", "P0_0", "P1_0"]


def test_a_job_the_order_file_never_heard_of_waits_at_the_end():
    jobs = [job("P0_0"), job("P1_0"), job("P2_0")]
    order = ["P1_0"]

    owed = queue.open_jobs(jobs, {}, order)

    # P1_0 is placed; the other two keep the plan's own sequence behind it.
    assert [j["id"] for j in owed] == ["P1_0", "P0_0", "P2_0"]


def test_without_an_order_the_plan_still_decides():
    jobs = [job("P0_0"), job("P1_0")]

    assert [j["id"] for j in queue.open_jobs(jobs, {})] == ["P0_0", "P1_0"]


def test_a_requeued_job_stays_behind_fresh_work_wherever_the_gallery_puts_it():
    jobs = [job("P0_0"), job("P1_0")]
    slots = {"P0_0": {"photo": {"status": queue.QUEUED, "file": "P0_0.png"}}}
    order = ["P1_0", "P0_0"]                  # P0_0 is at the bottom, so it would go first

    owed = queue.open_jobs(jobs, slots, order)

    assert [j["id"] for j in owed] == ["P1_0", "P0_0"]


def test_the_gallery_cannot_pull_a_video_ahead_of_the_photos():
    jobs = [job("P0_0"), {"id": "P0_0", "type": "video"}]
    order = ["P0_0"]

    owed = queue.open_jobs(jobs, {}, order)

    assert [queue.type_of(j) for j in owed] == ["photo", "video"]
```

`job(...)` ve `slots` biçimi için dosyanın var olan testlerine bak; yardımcı yoksa var olan
testlerdeki sözlük biçimini birebir kullan.

- [ ] **Adım 2: Koş, kırmızıyı gör**

Koş: `python -m pytest queen-editor -q`
Beklenen: `open_jobs()` üçüncü argümanı kabul etmediği için TypeError'lı FAIL'ler.

- [ ] **Adım 3: Sıralamayı yaz**

`queue.py`:

```python
def open_jobs(jobs, slots, order=()):
    """The jobs still owed, in the order the engine will do them.

    Type first, then where the frame sits in the gallery -- read from the bottom up, because the
    gallery is newest-first and the frame at its foot is the one produced first. `order` is the
    gallery's own stored sequence; a job it has never heard of waits at the end, and among
    themselves those keep the plan's order. No stored order at all means plan order, which is what
    an ungalleried project has always done.

    Inside a type, a job the user sent back with Tekrar dene waits behind everything that has never
    had a turn (design v2, G10); the gallery's order applies within each of those two tiers rather
    than across them.
    """
    # Rank by distance from the bottom of the gallery. Everything unplaced shares the last rank,
    # and sorted() is stable, so those keep the plan's own sequence.
    rank = {fid: index for index, fid in enumerate(reversed(list(order)))}
    unplaced = len(rank)

    def place(job):
        return rank.get(job["id"], unplaced)

    owed = []
    for kind in ORDER:
        same = [j for j in jobs if type_of(j) == kind]
        fresh = [j for j in same if _status(slots, j) is None]
        requeued = [j for j in same if _status(slots, j) == QUEUED]
        owed += sorted(fresh, key=place) + sorted(requeued, key=place)
    return owed
```

- [ ] **Adım 4: Koş, yeşili gör**

Koş: `python -m pytest queen-editor -q`

---

### Görev 2: Sıra deposu koşuya taşınır

**Dosyalar:**
- Değiştir: `queen-editor/backend/features/photo_generation/domain/run_loop.py:17-36`, `:45`
- Değiştir: `queen-editor/backend/features/photo_generation/domain/usecases/run_queue.py:15-23`
- Değiştir: `.../usecases/start_batch.py:73-90`, `.../usecases/resume_batch.py:16-22`,
  `.../usecases/retry_frame.py:1-25`
- Değiştir: `queen-editor/backend/main.py:72-89`
- Test: `queen-editor/backend/tests/test_photo_usecases.py`

**Arayüzler:**
- Tüketir: `open_jobs(jobs, slots, order)` (Görev 1).
- Üretir: `make_job(..., clock=…, log=None, order_store=None)` ·
  `run_queue(..., log=None, order_store=None)` · `start_batch(..., log=None, order_store=None)` ·
  `resume_batch(..., log=None, order_store=None)` · `retry_frame(..., log=None, order_store=None)`.

- [ ] **Adım 1: Uçtan uca testi yaz (kırmızı test)**

`test_photo_usecases.py`'ye — dosyanın kendi sahte port'larıyla; sıra deposu için okuma yeten
küçük bir sahte yeter:

```python
class FakeOrderStore:
    def __init__(self, order=()):
        self.order = list(order)

    def read(self, project):
        return list(self.order)

    def write(self, project, order):
        self.order = list(order)


def test_the_worker_starts_from_the_bottom_of_the_gallery():
    runner, store, record, plan = FakeRunner(), FakeStore(), FakeRecord(), FakePlanStore()
    order = FakeOrderStore(["P1_0", "P0_0"])   # the user dragged P0_0 to the foot
    plan.write("düğün", [{"id": "P0_0", "type": "photo", "prompt": "a", "negative": "",
                          "seed": 1, "model": ""},
                         {"id": "P1_0", "type": "photo", "prompt": "b", "negative": "",
                          "seed": 2, "model": ""}])

    resume_batch(runner, store, record, plan, {"photo": FakeGenerator()},
                 lambda: "2026-08-12T00:00:00+00:00", "düğün", order_store=order)

    assert [name for name, _data in store.saved] == ["P0_0.png", "P1_0.png"]
```

Sahte sınıfların adları ve kurucuları dosyanın kendi kalıbından alınır; `plan.write` yoksa o
dosyanın planı doldurma biçimi ne ise o kullanılır.

- [ ] **Adım 2: Koş, kırmızıyı gör**

Koş: `python -m pytest queen-editor -q`
Beklenen: `resume_batch()` `order_store` anahtarını tanımıyor.

- [ ] **Adım 3: Parametreyi zincire geçir**

`run_loop.py` — imza ve `snapshot`:

```python
def make_job(runner, store, record, plan_store, producers, now, project,
             clock=time.monotonic, log=None, order_store=None):
```

```python
    def snapshot():
        return (plan_store.read(project)["frames"], record.slots(project),
                order_store.read(project) if order_store else ())

    def summary(status, **extra):
        jobs, slots, _order = snapshot()
        return {"status": status, **queue.counts(jobs, slots), **extra}
```

döngüde:

```python
            jobs, slots, order = snapshot()
            owed = queue.open_jobs(jobs, slots, order)
```

`make_job`'ın docstring'ine tek cümle: sıra deposu verilmezse dizilim planın olur.

`run_queue.py`:

```python
def run_queue(runner, store, record, plan_store, producers, now, project, log=None,
              order_store=None):
```

```python
    job = make_job(runner, store, record, plan_store, producers, now, project, log=log,
                   order_store=order_store)
```

`start_batch.py`, `resume_batch.py`, `retry_frame.py` — her birinin imzasına `order_store=None`
eklenir ve `run_queue`'ya anahtarla geçirilir, örneğin:

```python
def resume_batch(runner, store, record, plan_store, producers, now, project, log=None,
                 order_store=None):
```

```python
    run_queue(runner, store, record, plan_store, producers, now, project, log,
              order_store=order_store)
```

`retry_frame.py`'nin başındaki docstring cümlesi düzelir:

```python
"""Put a frame back in line -- the one whose tile is red.

Retrying re-plans nothing: the frame is already in the plan with the prompt, negative and seed it
was submitted under, so putting it back in line is one line in the record. It renders where the
gallery puts it, behind the jobs that have never had a turn.
"""
```

- [ ] **Adım 4: Composition root'u bağla**

`main.py` — üç `partial`'a `order_store=_order_store` eklenir (`start_batch`, `resume_batch`,
`retry_frame`):

```python
    start_batch=partial(start_batch, _photo_runner, _photo_store, _photo_record, _plan_store,
                        _producers, lambda: random.randint(0, 2**31 - 1),
                        lambda: datetime.now(timezone.utc).isoformat(timespec="seconds"),
                        log=_timing, order_store=_order_store),
```

- [ ] **Adım 5: Koş, yeşili gör**

Koş: `python -m pytest queen-editor -q`

---

### Görev 3: Her kare sürüklenir

**Dosyalar:**
- Değiştir: `queen-editor/frontend/src/features/photo_generation/Gallery.jsx` — `HINT` sabiti,
  `hint` durumu, `press`, `Tile`'ın `hint` prop'u
- Test: `queen-editor/frontend/src/features/photo_generation/Gallery.test.jsx:414-432`

- [ ] **Adım 1: İki testi tersine çevir (kırmızı test)**

```jsx
  it("lifts a waiting frame too -- the order it is produced in is what the drag decides", () => {
    renderGallery({ frames: [{ file: "9_a.png", status: "pending" }, done("0_a.png")] });

    fireEvent.mouseDown(tileOf("9_a.png"));
    act(() => { vi.advanceTimersByTime(250); });

    expect(tileOf("9_a.png").draggable).toBe(true);
    expect(screen.queryByText("üretilince sıralanabilir")).toBeNull();
  });

  it("lifts a failed frame too", () => {
    renderGallery({ frames: [{ file: "9_a.png", status: "failed" }, done("0_a.png")] });

    fireEvent.mouseDown(tileOf("9_a.png"));
    act(() => { vi.advanceTimersByTime(250); });

    expect(tileOf("9_a.png").draggable).toBe(true);
  });

  it("lifts the frame the worker is holding, without asking it to stop", () => {
    renderGallery({ frames: [{ file: "9_a.png", status: "pending" }, done("0_a.png")],
                    current: "9_a.png" });

    fireEvent.mouseDown(tileOf("9_a.png"));
    act(() => { vi.advanceTimersByTime(250); });

    expect(tileOf("9_a.png").draggable).toBe(true);
  });
```

- [ ] **Adım 2: Koş, kırmızıyı gör**

Koş: `npm test --prefix queen-editor/frontend -- --run`
Beklenen: üç FAIL — kart kalkmıyor, ipucu çıkıyor.

- [ ] **Adım 3: Tutma kuralını ve ipucunu kaldır**

`Gallery.jsx`:

- `HINT` sabiti silinir.
- `const [hint, setHint] = useState(null);` silinir.
- `press` sadeleşir:

```jsx
  // Every card can be picked up, whatever became of it: the sequence a drag makes is the sequence
  // the queue produces in, so a frame with no pixels yet is exactly the one worth moving.
  function press(file) {
    clearTimeout(hold.current);
    hold.current = setTimeout(() => setArmed(file), HOLD_MS);
  }
```

- `release` yalnız `setArmed(null)` yapar.
- `onMouseDown={() => !selecting && press(frame.file)}`
- `Tile`'ın imzasından ve gövdesinden `hint` düşer.
- `<Tile ... hint={...}>` satırı kalkar.
- `draggable={armed === frame.file && !selecting}` — değişmez.
- `produced` değişkeni artık `press` için kullanılmıyor; başka kullanıcısı varsa kalır, yoksa
  düşer.
- `Tile`'ın üstündeki "Only a produced frame can be picked up" yorumu koda uydurulur.

- [ ] **Adım 4: Koş, yeşili gör**

Koş: `npm test --prefix queen-editor/frontend -- --run`

---

### Görev 4: Kapanış

**Dosyalar:**
- Değiştir: `queen-editor/CODE-STANDARD.md` — dosya tablosunun "gallery order" ve "run plan"
  satırları

- [ ] **Adım 1: Belgeyi koda uydur**

`CODE-STANDARD.md`'nin dört dosyalık tablosunda iki satır:

```markdown
| run plan | which frames this run was asked to produce, and with what | overwritten per run; the queue the worker reads |
| gallery order | in what order the frames stand -- which is both how the gallery shows them and the order they are produced in | rewritten on every drop |
```

- [ ] **Adım 2: İki takımı da koş**

Koş: `python -m pytest queen-editor -q`
Koş: `npm test --prefix queen-editor/frontend -- --run`

- [ ] **Adım 3: Derle**

Koş: `npm run build --prefix queen-editor/frontend`

- [ ] **Adım 4: Tek commit**

```bash
git add -A
git commit -F - <<'MSG'
feat(queen-editor): the order you drag is the order things get made

The gallery had an order and the queue had another. Dragging a tile moved the
badge, the export list and nothing else -- the engine went on taking the next
frame the plan happened to list, so the one thing a drag could not do was the
one thing worth doing with it.

Now there is one sequence. The queue reads the gallery's own file and works it
from the bottom up, because the gallery is newest-first and its foot is what
was made first. The plan keeps saying what was asked for and with what; it just
no longer claims to say in what order.

Two rules survive on purpose: the engine still finishes a type before starting
the next, and a frame sent back with Tekrar dene still waits behind work that
has never had a turn. The gallery's order applies inside those, not across them.

And every card can be picked up now -- a frame with no pixels yet is exactly
the one worth moving.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
MSG
```

## Öz denetim

**1. Spec kapsaması:** Karar 1-3 (alttan yukarı, tek dosya, bilinmeyen sona) → Görev 1; karar 4
(Tekrar dene katmanı) ve 5 (tür sırası) → Görev 1'in iki testi; karar 6 (anahtarlı bağımlılık) →
Görev 2; karar 7 (her kare sürüklenir) → Görev 3. Kabul kriterinin beş maddesinden dördü testte,
beşincisi (çalışan kare yarıda kesilmez) motorun var olan davranışı — Görev 3'ün üçüncü testi
kartın kalktığını, var olan motor testleri işin bittiğini söylüyor.

**2. Yer tutucu taraması:** Sahte sınıf adları ve `job(...)` yardımcısı test dosyalarının kendi
kalıbına bırakıldı; ikisi de o dosyalarda **var olan** biçimlerdir, uydurulacak bir şey yok.

**3. Tür tutarlılığı:** `order_store` adı beş imzada da aynı ve hepsinde anahtarlı; `open_jobs`'un
üçüncü parametresi `order` (liste), `order_store` değil — `run_loop` dönüşümü tek yerde yapıyor.
