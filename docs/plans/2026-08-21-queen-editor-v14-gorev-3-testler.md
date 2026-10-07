# v14 Görev 3 — Video ve sesin tohumunun kayda geçmesi: TEST döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eksik tohumu motorun seçmesini, seçtiği sayının hem üreticiye hem kayda gitmesini, bir işin
üç denemesinin tek tohum paylaşmasını ve ses üreticisinin artık tohum icat etmemesini sınayan sekiz
testi yazmak; takımı kırmızı commit'lemek.

**Architecture:** Bir yeni test dosyası (`test_seed.py` — saf fonksiyon), motorun tohum davranışı
`test_photo_usecases.py`'de sahtelerle, ve `test_mmaudio_generator.py`'de sorumluluğun devri:
icat eden iki test gidiyor, icat etmediğini söyleyen bir test geliyor.

**Tech Stack:** Python 3, pytest.

**Spec:** [test turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-3-tohum-testler-design.md)

## Global Constraints

- **Bu döngüde kod yazılmıyor.** `backend/features/` altındaki hiçbir dosya değişmiyor; `seed.py`
  bu turda doğmuyor.
- **Silinen testler bu turun işi.** `test_a_job_with_no_seed_still_reaches_the_model_with_one` ve
  `test_two_seedless_jobs_do_not_get_the_same_seed` bir sorumluluğu sınıyor ve o sorumluluk bu
  maddede yer değiştiriyor. Kalmaları, kaldırılan bir davranışı zorunlu tutmak olurdu.
- Test adları, docstring'leri ve yorumları **İngilizce**.
- Commit mesajında **çift tırnak yok**, ve **amend yok**.
- Komut: dört satır, birebir, boru yok.
- `dist/` **derlenmiyor**.
- Commit **kırmızı gider**.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `backend/tests/test_seed.py` | tohumun aralığı ve değişkenliği | yaratılır |
| `backend/tests/test_photo_usecases.py` | motorun tohum davranışı | 5 test eklenir |
| `backend/tests/test_mmaudio_generator.py` | ses üreticisinin tohum icat etmemesi | 2 test silinir, 1 eklenir |

---

### Task 1: Tohumun kendisi

**Files:**
- Create: `queen-editor/backend/tests/test_seed.py`

**Interfaces:**
- Consumes: `backend.features.photo_generation.domain.seed` — **henüz yok**.

- [ ] **Step 1: Dosyayı yaz**

```python
"""The number a job is rendered with, when the job carries none.

One range for every seed in the app: a photo job is planned in it, and a layer job is given one out
of it when its turn comes. A seed is a seed wherever it was born, and three copies of the same
range in three files is how they stop being the same range.
"""
from backend.features.photo_generation.domain import seed


def test_a_seed_is_inside_the_range_a_photo_job_is_planned_in():
    for _ in range(50):
        number = seed.random_seed()
        assert 0 <= number <= seed.MAX


def test_two_seeds_are_not_the_same_number():
    """Not a claim about randomness -- a generator that answered 7 every time would pass every other
    test in this run and make every variant of a frame identical."""
    assert len({seed.random_seed() for _ in range(20)}) > 1
```

- [ ] **Step 2: Takımı koştur**

Run: `python -m pytest queen-editor -q`
Expected: dosya toplanamıyor — `ImportError: cannot import name 'seed'`.

---

### Task 2: Motorun seçtiği tohum

**Files:**
- Modify: `queen-editor/backend/tests/test_photo_usecases.py`

**Interfaces:**
- Consumes: `make_job(..., new_seed=...)` — **parametre henüz yok**; `FakeGenerator.calls`
  (üçüncü alan tohum) ve `FakeRecord.rows`.

- [ ] **Step 1: Tek katman işi koşturan yardımcıyı yaz**

`render_one_video`'nun altına:

```python
def render_seedless(new_seed, jobs=1):
    """`jobs` seedless video jobs on their own frames, run to completion.

    Video rather than sound because a video job is the one that plans no seed and has a producer a
    test can hold; what the loop does about a missing seed is the same whatever the layer is.
    """
    store, record = FakeStore(), FakeRecord()
    plan_store = FakePlanStore(frames=[frame(number) for number in range(jobs)])
    planned = []
    for number in range(jobs):
        fid = f"{number}_a"
        record.append("düğün", {"file": f"{fid}.png", "frame": fid, "layer": "photo",
                                "status": "done"})
        store.files[f"{fid}.png"] = b"PNG"
        planned.append({"id": fid, "type": "video", "number": number, "variant": 0,
                        "prompt": "p", "negative": "", "seed": None, "model": ""})
    plan_store.append("düğün", planned)
    generator = FakeGenerator()
    make_job(sync_runner(), store, record, plan_store, {layers.VIDEO: generator},
             lambda: "t", "düğün", new_seed=new_seed)()
    return generator, record


def video_seeds(record):
    """The seed written on every produced video row, in the order the rows were written."""
    return [row["seed"] for row in record.rows
            if row.get("layer") == "video" and row.get("status") == "done"]
```

- [ ] **Step 2: Beş testi yaz**

```python
def test_a_seedless_job_is_produced_with_a_seed_the_engine_chose():
    """A layer job is planned without one (queue_layer), and until now that None travelled all the
    way into the render: the sound engine invented a number of its own and the video graph kept its
    -1, which rgthree only randomises in the browser widget."""
    generator, _record = render_seedless(lambda: 777)

    assert [call[2] for call in generator.calls] == [777]


def test_the_seed_a_job_was_produced_with_is_written_down():
    """The whole madde in one line: the number that rendered the layer is the number on its row, so
    the row can be produced again."""
    generator, record = render_seedless(lambda: 777)

    assert video_seeds(record) == [call[2] for call in generator.calls]


def test_a_job_that_carried_its_own_seed_keeps_it():
    # A photo job is planned with a seed of its own. Choosing a second one for it would quietly
    # produce a different picture from the one the plan describes.
    store, generator = FakeStore(), FakeGenerator()
    record = FakeRecord()
    run_batch(sync_runner(), store, generator, text='["a"]', variants=1, record=record)

    assert [call[2] for call in generator.calls] == [42]


def test_two_seedless_jobs_get_seeds_of_their_own():
    """Two variants of one frame must not come out identical: asking for a second would buy
    nothing."""
    seeds = iter([777, 888])
    generator, _record = render_seedless(lambda: next(seeds), jobs=2)

    assert sorted(call[2] for call in generator.calls) == [777, 888]
```

Üç denemenin tek tohum paylaştığını görmek için üreticinin **düşmesi** gerekiyor: başarılı bir
üretici tek çağrı yapar ve "bir tohum" iddiası hiçbir şey söylemez. `FakeGenerator(fail_on=["p"])`
üç deneme yaptırıp sonunda kareyi kırmızıya çeviriyor, ama üç çağrı kaydedilmiş oluyor.

```python
def test_the_three_attempts_of_one_job_share_one_seed():
    """Otherwise "produce this row again with its seed" would name a number only the last attempt
    used, and the two earlier renders would be unreproducible."""
    seeds = iter([1, 2, 3])
    store, record = FakeStore(), FakeRecord()
    plan_store = FakePlanStore(frames=[frame(0)])
    record.append("düğün", {"file": "0_a.png", "frame": "0_a", "layer": "photo", "status": "done"})
    store.files["0_a.png"] = b"PNG"
    plan_store.append("düğün", [{"id": "0_a", "type": "video", "number": 0, "variant": 0,
                                 "prompt": "p", "negative": "", "seed": None, "model": ""}])
    # Fails every time, so the job spends all three of its attempts and three calls are recorded.
    generator = FakeGenerator(fail_on=["p"])

    make_job(sync_runner(), store, record, plan_store, {layers.VIDEO: generator},
             lambda: "t", "düğün", new_seed=lambda: next(seeds))()

    assert len(generator.calls) == 3
    assert len({call[2] for call in generator.calls}) == 1
```

- [ ] **Step 3: Takımı koştur**

Run: `python -m pytest queen-editor -q`
Expected: `test_photo_usecases.py`'ın beş yeni testi `TypeError: make_job() got an unexpected
keyword argument 'new_seed'` ile düşüyor. Task 1'in toplama hatası duruyor.

---

### Task 3: Ses üreticisinin bıraktığı iş

**Files:**
- Modify: `queen-editor/backend/tests/test_mmaudio_generator.py`

**Interfaces:**
- Consumes: `MMAudioGenerator(sampler, ffmpeg, tmp_dir=None)` — `new_seed` **kalkıyor**.

- [ ] **Step 1: Portun dört kullanıcısını ele al**

`make_with_port` yardımcısı siliniyor. Ona dayanan dört test:

| Test | Ne oluyor | Neden |
|---|---|---|
| `test_a_job_with_no_seed_still_reaches_the_model_with_one` | siliniyor | "eksik tohumu ses üreticisi icat eder" davranışını sınıyor, ve o davranış motora taşınıyor |
| `test_two_seedless_jobs_do_not_get_the_same_seed` | siliniyor | aynı sebep; iki işin ayrı tohum almasını artık motorun testi tutuyor |
| `test_a_job_that_carries_its_own_seed_keeps_it` | siliniyor | tek iddiası "port sorulmamalı"ydı; port kalkınca yerine geçen testin içinde eriyor |
| `test_every_piece_of_one_sound_shares_its_seed` | **kalıyor**, gerçek bir tohumla yeniden yazılıyor | söylediği şey portla ilgili değil: bir ses tek tohumla üretilir, kaç parçaya bölünürse bölünsün |

Silinen bir davranışı zorunlu tutan test kalırsa, bir sonraki gelen onu geri koymak zorunda kalır.

- [ ] **Step 2: Yerine geleni yaz**

Silinenlerin yerine:

```python
def test_the_sound_engine_invents_no_seed_of_its_own(tmp_path):
    """The seed arrives with the job now: the loop picks one before the render, because the number
    also has to be written on the produced layer's row and a seed chosen in here could never reach
    it. Two places choosing a seed is two different answers to one question."""
    sampler = FakeSampler()

    make(tmp_path, sampler).generate("waves", "", 4242, source=SOURCE)

    assert sampler.calls[0]["seed"] == 4242
    # The port is gone, not merely unused: a constructor that still took one would let a caller put
    # the second answer back.
    with pytest.raises(TypeError):
        MMAudioGenerator(sampler, FakeFfmpeg(), tmp_dir=str(tmp_path), new_seed=lambda: 1)


def test_every_piece_of_one_sound_shares_its_seed(tmp_path):
    """A long video is cut into pieces but what comes out is one sound: a seed per piece would
    change its character halfway through."""
    sampler = FakeSampler()

    make(tmp_path, sampler, FakeFfmpeg(seconds=24.0)).generate("waves", "", 4242, source=SOURCE)

    assert [call["seed"] for call in sampler.calls] == [4242, 4242, 4242]
```

- [ ] **Step 3: Dört komutu koştur**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Expected: `queen-editor` kırmızı — `test_seed.py` toplanamıyor, beş motor testi `new_seed`
argümanını tanımayan `make_job` yüzünden düşüyor, ve `test_the_sound_engine_invents_no_seed_of_its_own`
`TypeError` beklerken kurucu argümanı hâlâ kabul ettiği için düşüyor. Kalan üç takım yeşil.

---

### Task 4: Kırmızı commit

- [ ] **Step 1: Commit**

```bash
git add queen-editor/backend/tests docs/superpowers
git commit -F - <<'EOF'
test(queen-editor): v14 task 3 - the seed a job was produced with is written down

Red on purpose: there is no seed module, make_job takes no new_seed, and MMAudio still
carries a seed port of its own. The other three suites stay green.

The roadmap asked for producers to return the seed they used. That cannot be done for
video: a seedless video job leaves the graph -1 in place, and rgthree only randomises
that in the browser widget, so the only number the producer could honestly return is
-1. The domain picks the seed instead, before the render, and hands the same number to
the producer and to the record. It closes the -1 bug on the way.

Two MMAudio tests go with this commit. They asked the sound engine to invent a seed
when the job carried none, and that responsibility moves to the loop; keeping them
would hold a removed behaviour in place. What replaces them says the engine invents
nothing and that the port is gone rather than merely unused.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** spec'in sekiz testinin sekizi planda kodlu. 1-2 → Task 1; 3-7 → Task 2;
8 → Task 3. Spec'in 4. ve 5. kararları (`MMAudioGenerator` kurucusu, `main.py`'nin lambda'ları)
implementasyon turunun işi; testleri Task 3'ün `pytest.raises(TypeError)`'ı taşıyor.

**Tip tutarlılığı:** `make_job(..., new_seed=callable)` Task 2'nin iki yerinde aynı.
`FakeGenerator.calls` bir dörtlü ve tohum üçüncü sırada (`call[2]`) — dosyanın var olan
kullanımıyla aynı.

**Kontrol edilen tuzak:** `test_the_three_attempts_of_one_job_share_one_seed` düşen bir üreticiyle
koşuyor. Başarılı bir üreticiyle tek çağrı olurdu ve test "bir tohum" derken aslında hiçbir şey
söylemezdi — üç deneme yapılmadan üç denemenin aynı tohumu paylaştığı görülemez.

**Kontrol edilen tuzak 2:** `test_two_seedless_jobs_get_seeds_of_their_own` iki **ayrı karede** iki
video işi kuruyor. Aynı karede iki video işi kurmak işe yaramazdı: ikincisinin slotu dolu olur ve
kuyruk onu hiç çalıştırmazdı.

**Kontrol edilen tuzak 3:** `test_a_job_that_carried_its_own_seed_keeps_it` foto akışından geçiyor
(`run_batch`), çünkü tohumunu taşıyan tek iş türü o. Katman işiyle yazılsaydı sınadığı şey
kurgunun kendisi olurdu.
