# v14 Görev 2 — Kuyruk işinin üretim modunu taşıması: TEST döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Üç modun adını, kuyruğa modla iş eklenmesini, bağlı modda hedefin kuyruk anında
çözülmesini, planın modu kaybetmemesini ve motorun modu okuyup bitiş karesini seçmesini sınayan on
beş testi yazmak; takımı kırmızı commit'lemek.

**Architecture:** Bir yeni test dosyası ve iki var olan dosyanın genişlemesi. `test_production_mode.py`
üç modun okunmasını sınar — saf fonksiyon, hiçbir bağımlılığı yok. `test_plan_store.py` gerçek
depoya yazıp okur. `test_photo_usecases.py` kuyruğu ve motoru sahtelerle koşturur; motorun ne
gönderdiğini görebilmek için `FakeGenerator` aldığı bitiş karelerini kaydeder.

**Tech Stack:** Python 3, pytest.

**Spec:** [test turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-2-uretim-modu-testler-design.md)

## Global Constraints

- **Bu döngüde kod yazılmıyor.** `backend/features/` altındaki hiçbir dosya değişmiyor —
  `production_mode.py` bu turda **doğmuyor bile**; testleri onun yokluğuna çarpıyor.
- **Sahte imzaların genişlemesi kod yazmak değildir.** `test_photo_usecases.py`'daki her sahte
  üreticiye `end=None` eklenir. Eklenmezse implementasyon turunda çıkacak kırmızı `TypeError` olur
  ve maddenin sorduğu şey hakkında hiçbir şey söylemez.
- Test adları, docstring'leri ve yorumları **İngilizce**.
- Commit mesajında **çift tırnak yok**, ve **amend yok**.
- Komut: dört satır, birebir, boru yok. Tek dosyayı adıyla koşturmak yok.
- `dist/` **derlenmiyor**.
- Commit **kırmızı gider**. `skip`/`xfail` yok.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `backend/tests/test_production_mode.py` | üç modun okunması | yaratılır |
| `backend/tests/test_plan_store.py` | planın modu kaybetmemesi | 1 test eklenir |
| `backend/tests/test_photo_usecases.py` | kuyruk ve motor | sahteler genişler, 11 test eklenir |

---

### Task 1: Modların adı

**Files:**
- Create: `queen-editor/backend/tests/test_production_mode.py`

**Interfaces:**
- Consumes: `backend.features.photo_generation.domain.production_mode` — **henüz yok**. Modülün
  yokluğu bu dosyanın kırmızılığının tamamı.
- Produces: yok.

- [ ] **Step 1: Dosyayı yaz**

`queen-editor/backend/tests/test_production_mode.py`:

```python
"""How a video job says where it ends.

The three names live in the domain because the queue writes them, the engine reads them and the
screen only labels them. What the user sees in Turkish is the frontend's business; nothing here
knows those words.
"""
from backend.features.photo_generation.domain import production_mode


def test_a_job_that_names_a_mode_has_that_mode():
    assert production_mode.of({"mode": production_mode.STANDARD}) == production_mode.STANDARD
    assert production_mode.of({"mode": production_mode.LOOP}) == production_mode.LOOP
    assert production_mode.of({"mode": production_mode.LINKED}) == production_mode.LINKED


def test_a_job_that_names_no_mode_is_a_plain_one():
    """Every video job planned before this madde carries no mode, and each of them has to go on
    rendering exactly as it does today. Standard is not a tolerance here, it is the right answer."""
    assert production_mode.of({"type": "video"}) == production_mode.STANDARD


def test_a_mode_nobody_knows_is_read_as_the_plain_one():
    """A hand-edited plan or a newer client is not a reason to stop a run: the queue refuses an
    unknown mode at the door (queue_layer), and by the time a job is being rendered the only honest
    reading left is the plain one."""
    assert production_mode.of({"mode": "kelebek"}) == production_mode.STANDARD


def test_the_three_modes_are_the_whole_list():
    # ALL is what the queue validates against; a mode missing from it could never be asked for.
    assert production_mode.ALL == (production_mode.STANDARD, production_mode.LOOP,
                                   production_mode.LINKED)
```

- [ ] **Step 2: Takımı koştur**

Run: `python -m pytest queen-editor -q`
Expected: dosya toplanamıyor — `ImportError: cannot import name 'production_mode'`. Dört test de
koşmuyor bile; modülün yokluğu bu turun kırmızısının kendisi.

---

### Task 2: Planın hafızası

**Files:**
- Modify: `queen-editor/backend/tests/test_plan_store.py`

**Interfaces:**
- Consumes: `DrivePlanStore.append` / `read` (bugünkü hâlleriyle).
- Produces: yok.

- [ ] **Step 1: Gidiş-dönüş testini yaz**

Dosyanın `test_append_then_read_round_trips`'in altına:

```python
def test_the_plan_keeps_a_jobs_production_mode(tmp_path):
    """The mode is written when the job is queued and read when its turn comes, which can be hours
    later and a process restart apart. Nothing else stands between those two moments, so a read
    that dropped the key would leave every video plain with no sign of why."""
    store = store_at(tmp_path)
    store.append("düğün", [
        {"id": "P0_0", "type": "video", "number": 0, "variant": 0, "prompt": "", "negative": "",
         "seed": None, "model": "", "mode": "linked", "linkedTo": "P1_0"}])

    job = store.read("düğün")["frames"][0]

    assert job["mode"] == "linked"
    assert job["linkedTo"] == "P1_0"
```

- [ ] **Step 2: Takımı koştur**

Run: `python -m pytest queen-editor -q`
Expected: Task 1'in toplama hatası hâlâ koşuyu durduruyor, yani bu test bu adımda **hiç
koşmuyor**. Doğruluğu implementasyon turunun ilk yeşilinde görülecek — ve orada **yeşil doğacak**:
`read` satırı `{**frame}` ile kuruluyor, yani anahtarlar zaten sağ çıkıyor. İşi kırmızı olmak değil;
modun motora ulaşması bu gidiş-dönüşe bağlı ve okumayı bir gün sıkılaştıran biri bunu farkında
olmadan kırabilir.

---

### Task 3: Sahtelerin genişlemesi

**Files:**
- Modify: `queen-editor/backend/tests/test_photo_usecases.py`

**Interfaces:**
- Produces: `FakeGenerator.ends` — Task 5'in üç testi bu listeyi okuyor.

- [ ] **Step 1: FakeGenerator bitiş karelerini kaydetsin**

```python
class FakeGenerator:
    """Records what each frame asked for; `fail_on` names the prompts whose render fails."""

    def __init__(self, fail_on=(), installed=("nova.safetensors",)):
        self.calls = []
        self.sources = []
        # Kept apart from sources: what a layer is made from and where it arrives are two different
        # questions, and one list holding both could not answer either.
        self.ends = []
        self.models_called = 0
        self.fail_on = list(fail_on)
        self.installed = list(installed)

    def models(self):
        self.models_called += 1
        return list(self.installed)

    def generate(self, prompt, negative, seed, model="", source=None, end=None):
        self.calls.append((prompt, negative, seed, model))
        self.sources.append(source)
        self.ends.append(end)
        if prompt in self.fail_on:
            raise FrameFault(f"node 41: {prompt}")
        return b"PNG"
```

- [ ] **Step 2: Dosyadaki her satır içi sahteyi genişlet**

Dosya boyunca yerel sınıfların taşıdığı imza:

```python
    def generate(self, prompt, negative, seed, model="", source=None):
```

hepsi şu olur:

```python
    def generate(self, prompt, negative, seed, model="", source=None, end=None):
```

Toplu değiştirme yapılır — dosyada bu imzadan yirmiye yakın var ve hepsi aynı sebeple genişliyor.

- [ ] **Step 3: Takımı koştur**

Run: `python -m pytest queen-editor -q`
Expected: Task 1'in toplama hatası dışında hiçbir şey değişmedi. Genişleyen imzalar bugün kimsenin
göndermediği bir argümanı kabul ediyor, o kadar.

---

### Task 4: Kuyruğun modu

**Files:**
- Modify: `queen-editor/backend/tests/test_photo_usecases.py`

**Interfaces:**
- Consumes: `queue_layer(..., mode=...)` ve `InvalidMode` — **ikisi de yok**; kırmızılık bundan.
- Produces: `linked_project(*frames)` yardımcısı — Task 5 de kullanıyor.

- [ ] **Step 1: Testleri yaz**

`video_project`'in altına, `pytest.raises` için dosyanın zaten `import pytest` taşıdığı doğrulanır:

```python
def queue_video(store, record, plan_store, mode, order=(), files=None):
    """Queue a video job the way the panel would, and hand back the plan lines it wrote."""
    added = queue_layer(sync_runner(), store, record, plan_store, FakeOrderStore(order),
                        {layers.PHOTO: FakeGenerator()}, lambda: "t", "düğün", layers.VIDEO,
                        files=files, mode=mode)
    return added, (plan_store.appended[-1] if plan_store.appended else [])


def test_a_video_job_carries_the_mode_it_was_queued_with():
    store, record, plan_store = video_project((0, "a"), (1, "a"))

    _added, jobs = queue_video(store, record, plan_store, production_mode.LOOP)

    # The mode is on the job, not on the batch: the queue holds work from several presses at once,
    # and a batch-level answer would be read by whichever job happened to be next.
    assert [job["mode"] for job in jobs] == ["loop", "loop"]


def test_a_linked_video_job_names_the_frame_it_ends_on():
    """Resolved as the job is queued rather than as it is rendered: the queue runs for hours and the
    gallery can be dragged while it does, so a target read later would not be the one the user was
    looking at when they pressed the button."""
    store, record, plan_store = video_project((0, "a"), (1, "a"))

    _added, jobs = queue_video(store, record, plan_store, production_mode.LINKED)

    # The gallery is newest-first, so 1_a is above 0_a and the frame after 0_a is 1_a.
    by_id = {job["id"]: job for job in jobs}
    assert by_id["0_a"]["linkedTo"] == "1_a"


def test_the_last_frame_takes_no_linked_job_but_the_rest_do():
    """The frame at the top of the gallery has no next one. Production is not blocked over it: that
    one frame stays out and the rest go in, and fixing the selection is one press away."""
    store, record, plan_store = video_project((0, "a"), (1, "a"))

    added, jobs = queue_video(store, record, plan_store, production_mode.LINKED)

    assert added == 1
    assert [job["id"] for job in jobs] == ["0_a"]


def test_a_linked_batch_with_nowhere_to_end_takes_nothing():
    store, record, plan_store = video_project((0, "a"))

    added, _jobs = queue_video(store, record, plan_store, production_mode.LINKED)

    # Nothing owed and nothing started -- exactly what an empty scope already answers.
    assert added == 0
    assert plan_store.appended == []


def test_a_sound_job_carries_no_mode_at_all():
    """A sound is laid over the whole of a video and arrives nowhere. Writing "standard" on its line
    would be a field claiming an answer to a question the layer never asks."""
    store, record = FakeStore(), FakeRecord()
    plan_store = FakePlanStore(frames=[frame(0)])
    record.append("düğün", {"file": "0_a.png", "frame": "0_a", "layer": "photo", "status": "done"})
    record.append("düğün", {"file": "0_a_V1_0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done"})

    queue_layer(sync_runner(), store, record, plan_store, FakeOrderStore(),
                {layers.PHOTO: FakeGenerator()}, lambda: "t", "düğün", layers.AUDIO)

    assert "mode" not in plan_store.appended[-1][0]


def test_a_mode_nobody_knows_is_refused():
    store, record, plan_store = video_project((0, "a"))

    with pytest.raises(InvalidMode):
        queue_video(store, record, plan_store, "kelebek")


def test_a_sound_cannot_be_asked_to_end_anywhere():
    # Only a video ends on a picture. Ignoring the argument would hide the caller's mistake behind
    # a sound that came out fine.
    store, record, plan_store = video_project((0, "a"))

    with pytest.raises(InvalidMode):
        queue_layer(sync_runner(), store, record, plan_store, FakeOrderStore(),
                    {layers.PHOTO: FakeGenerator()}, lambda: "t", "düğün", layers.AUDIO,
                    mode=production_mode.LOOP)
```

- [ ] **Step 2: İki import ekle**

Dosyanın başındaki import öbeğine:

```python
from backend.features.photo_generation.domain import production_mode
```

ve `queue_layer`'ın geldiği satıra `InvalidMode`:

```python
from backend.features.photo_generation.domain.usecases.queue_layer import InvalidMode, queue_layer
```

(Var olan import satırının tam hâli okunup üstüne yazılır; bu dosya `queue_layer`'ı zaten
çağırıyor.)

- [ ] **Step 3: Takımı koştur**

Run: `python -m pytest queen-editor -q`
Expected: `test_photo_usecases.py` toplama sırasında tümüyle düşüyor —
`ImportError: cannot import name 'production_mode'` ve `InvalidMode`. Bu beklenen: iki isim de
implementasyon turunda doğuyor.

---

### Task 5: Motorun bitiş karesi

**Files:**
- Modify: `queen-editor/backend/tests/test_photo_usecases.py`

**Interfaces:**
- Consumes: `make_job` (bugünkü imzasıyla) ve `FakeGenerator.ends`.

- [ ] **Step 1: Motoru modla koşturan yardımcıyı yaz**

Task 4'ün testlerinin altına:

```python
def render_one_video(mode, linked_to=None, gallery=((0, "a"), (1, "a")), photos=("0_a", "1_a")):
    """One video job, planned by hand with the mode already on it, run to completion.

    Planned by hand rather than through queue_layer: what is under test here is the engine reading
    a mode, and going through the queue would make one test answer for two rules at once.
    """
    store, record = FakeStore(), FakeRecord()
    plan_store = FakePlanStore(frames=[frame(number) for number, _letter in gallery])
    for fid in photos:
        record.append("düğün", {"file": f"{fid}.png", "frame": fid, "layer": "photo",
                                "status": "done"})
        store.files[f"{fid}.png"] = f"{fid} bytes".encode()
    job = {"id": "0_a", "type": "video", "number": 0, "variant": 0, "prompt": "p", "negative": "",
           "seed": None, "model": "", "mode": mode}
    if linked_to is not None:
        job["linkedTo"] = linked_to
    plan_store.append("düğün", [job])
    generator = FakeGenerator()
    make_job(sync_runner(), store, record, plan_store, {layers.VIDEO: generator},
             lambda: "t", "düğün")()
    return generator, record


def test_a_plain_video_is_produced_with_no_ending_frame():
    generator, _record = render_one_video(production_mode.STANDARD)

    assert generator.ends == [None]


def test_a_loop_video_ends_on_its_own_picture():
    """A loop is a video that arrives where it started, so the ending picture is the frame's own --
    the very file it is being made from."""
    generator, _record = render_one_video(production_mode.LOOP)

    assert generator.ends == [("0_a.png", b"0_a bytes")]
    assert generator.sources == [("0_a.png", b"0_a bytes")]


def test_a_linked_video_ends_on_the_next_frames_picture():
    generator, _record = render_one_video(production_mode.LINKED, linked_to="1_a")

    assert generator.sources == [("0_a.png", b"0_a bytes")]
    assert generator.ends == [("1_a.png", b"1_a bytes")]


def test_a_linked_video_whose_target_lost_its_photo_turns_that_frame_red():
    """The frame it was told to end on is gone -- deleted between the press and the render. One
    frame's trouble, so the tile turns red and the queue goes on; falling back to a plain video
    would hand the user something other than what they asked for and say nothing about it."""
    generator, record = render_one_video(production_mode.LINKED, linked_to="1_a",
                                         photos=("0_a",))

    assert generator.ends == []          # nothing was ever rendered for this job
    video = record.slots("düğün")["0_a"]["video"]
    assert video["status"] == queue.FAILED
```

- [ ] **Step 2: Dört komutu koştur**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Expected: `queen-editor` kırmızı, kalan üç takım yeşil.

Kırmızının biçimi **toplama hatası**, tek tek düşen testler değil: `production_mode` modülü ve
`InvalidMode` yok, dolayısıyla `test_production_mode.py`, `test_photo_usecases.py` ve ondan import
eden `test_export.py` hiç toplanamıyor ve pytest üçünü de saymadan duruyor:

```
!!!!!!!!!!!!!!!!!!! Interrupted: 3 errors during collection !!!!!!!!!!!!!!!!!!!
```

**Bunun bedeli var ve bilerek ödeniyor:** bu commit'te queen-editor'ın kalan ~615 testi hiç
koşmuyor, yani "başka bir şey kırılmadı" bu commit'e bakarak görülemiyor. Bir öncekinde (1. maddenin
yeşil commit'i) hepsi koştu ve yeşildi, bir sonrakinde yine koşacak. Alternatifi, modülü iskelet
olarak bu turda doğurmaktı; o da test turunda kaynak dosyası yazmak olurdu ve bu turun tek kuralı
tam olarak onu yasaklıyor.

---

### Task 6: Kırmızı commit

- [ ] **Step 1: Commit**

```bash
git add queen-editor/backend/tests docs/superpowers
git commit -F - <<'EOF'
test(queen-editor): v14 task 2 - the queue carries a video job production mode

Red on purpose: there is no production_mode module, queue_layer knows no mode argument
and no InvalidMode, and the loop hands its producer no ending frame. The other three
suites stay green.

The mode is written when the job is queued, and so is the frame a linked video ends on:
the queue runs for hours and the gallery can be dragged while it does, so a target read
at render time would not be the one the user was looking at.

The next frame is the gallery's own next -- the same reading the detail page's forward
arrow already does. A frame with nothing to end on stays out of the batch and the rest
go in; production is not blocked over one frame at the top of the gallery.

The fake producers grew an end argument in this cycle. Widening a fake is not writing
the code: without it the implementation cycle's red would be a TypeError, which says
nothing about what this madde asks.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** spec'in on beş testinin on beşi planda kodlu, artı `ALL`'ın listesini tutan bir
tane daha (Task 1 Step 1) — spec'in 1. kararı `ALL`'dan söz ediyor ve kuyruğun doğrulaması ona
bakıyor. 1-3 → Task 1; 4 → Task 2; 5-11 → Task 4; 12-15 → Task 5.

**Tip tutarlılığı:** `production_mode.STANDARD/LOOP/LINKED/ALL/of` her yerde aynı adlarla.
`queue_layer(..., mode=...)` Task 4'ün iki yerinde aynı. Plan satırındaki anahtarlar `mode` ve
`linkedTo` — Task 2, Task 4 ve Task 5'te aynı yazımla.

**Kontrol edilen tuzak:** `test_the_last_frame_takes_no_linked_job_but_the_rest_do` iki kareli bir
galeride koşuyor. Tek kareyle koşsaydı "son kare düşer" ile "hiçbir şey girmez" aynı testte
karışırdı; ikisi ayrı test, çünkü ikisi ayrı karar.

**Kontrol edilen tuzak 2:** `render_one_video` işi elle planlıyor, `queue_layer`'dan geçirmiyor. Aksi
hâlde motorun modu okuması ile kuyruğun modu yazması tek testte birleşir ve biri bozulduğunda
hangisi olduğu anlaşılmazdı.

**Kontrol edilen tuzak 3:** `test_a_linked_video_whose_target_lost_its_photo_turns_that_frame_red`
`generator.ends == []` diyor. "Kırmızı oldu" tek başına yeterli değil: üreticiye yanlış bir resimle
gidilip sonra kırmızıya dönülse de karo kızarırdı, ve o hâlde kullanıcı istemediği bir videoyu
üretmek için GPU zamanı harcamış olurdu.

**Kontrol edilen kapsam:** `test_plan_store.py`'ın yeni testi yeşil doğuyor ve bu planda açıkça
yazıyor. Kırmızı olmayan bir testi kırmızı sanıp "neden geçti" diye kovalamak, bu döngünün en kolay
kaybedilen yarım saati.

**Kabul edilen zayıflık:** kırmızı, toplama seviyesinde. Bu commit'te queen-editor'ın kalan testleri
hiç koşmuyor, dolayısıyla bu turun düzenlemelerinin başka bir şeyi kırıp kırmadığı buradan
görülemiyor. Görüldüğü yer bir sonraki commit; ve arada duran tek değişiklik yirmi sahte imzanın
`end=None` alması, ki hiçbiri davranış taşımıyor.
