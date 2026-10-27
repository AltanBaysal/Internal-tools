# v12 Görev 1 — Tohumsuz iş: TEST döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tohumun plandan ses üreticisine giden yolunu sınayan testleri yazmak ve takımı kırmızı
commit'lemek.

**Architecture:** Üç test dosyası. Biri üreticinin tohum kurallarını yazıyor, biri sözleşmeyi
kuyruğun gerçek planına oturtuyor, biri kuyruğun ne yazdığını kilitliyor.

**Tech Stack:** pytest.

**Tasarım:** [test spec'i](../specs/2026-08-14-queen-editor-v12-gorev-1-testler-design.md)

## Global Constraints

- **Bu döngüde üretim kodu değişmiyor.** `backend/features/` altında tek satır bile.
- Test adları, docstring'ler ve yorumlar **İngilizce**.
- Commit mesajında **çift tırnak yok**.
- Komut: `python -m pytest queen-editor/backend/tests -q`
- Commit **kırmızı gider** ve mesajı hangi testin neden düştüğünü ayırarak söyler.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `queen-editor/backend/tests/test_mmaudio_generator.py` | ses üreticisinin kararları | 1 yardımcı + 4 test eklenir |
| `queen-editor/backend/tests/test_producer_contract.py` | kuyruk ↔ gerçek üreticiler | sahte sampler sıkılaşır, plan kuyruğunkine çevrilir |
| `queen-editor/backend/tests/test_photo_usecases.py` | kuyruğun yazdığı plan | 1 test eklenir |

---

### Task 1: Üreticinin dört tohum kuralı

**Files:**
- Modify: `queen-editor/backend/tests/test_mmaudio_generator.py`

- [ ] **Step 1: Portlu bir kurucu ekle**

`make()` fonksiyonunun hemen altına. `make()`'e dokunulmuyor — onu kullanan dokuz test bugünkü
gibi yeşil kalmalı, yoksa kırmızının anlamı kaybolur.

```python
def make_with_port(tmp_path, sampler, new_seed, ffmpeg=None):
    """The generator with a seed port. A sound job carries no seed of its own, so this is the
    only thing standing between the queue's None and torch's manual_seed."""
    return MMAudioGenerator(sampler, ffmpeg or FakeFfmpeg(), tmp_dir=str(tmp_path),
                            new_seed=new_seed)
```

- [ ] **Step 2: Tohumsuz iş modele bir tam sayıyla gidiyor**

Dosyanın sonuna:

```python
def test_a_job_with_no_seed_still_reaches_the_model_with_one(tmp_path):
    """Every sound job is planned without a seed, and torch's manual_seed takes a long or raises.
    Passing the None straight through is what stopped production on 2026-08-14."""
    sampler = FakeSampler()

    make_with_port(tmp_path, sampler, lambda: 11).generate("waves", "", None, source=SOURCE)

    assert sampler.calls[0]["seed"] == 11
```

- [ ] **Step 3: İki tohumsuz iş aynı tohumu almıyor**

```python
def test_two_seedless_jobs_do_not_get_the_same_seed(tmp_path):
    """Otherwise two sound variants of one video would be the same file, and asking for a second
    would buy nothing."""
    sampler = FakeSampler()
    seeds = iter([11, 22])
    generator = make_with_port(tmp_path, sampler, lambda: next(seeds))

    generator.generate("waves", "", None, source=SOURCE)
    generator.generate("waves", "", None, source=SOURCE)

    assert [call["seed"] for call in sampler.calls] == [11, 22]
```

- [ ] **Step 4: Bir sesin bütün parçaları aynı tohumu paylaşıyor**

```python
def test_every_piece_of_one_sound_shares_its_seed(tmp_path):
    """A long video is cut into pieces but what comes out is one sound: a seed per piece would
    change its character halfway through."""
    sampler = FakeSampler()
    seeds = iter([11, 22, 33, 44])

    make_with_port(tmp_path, sampler, lambda: next(seeds),
                   ffmpeg=FakeFfmpeg(seconds=24.0)).generate("waves", "", None, source=SOURCE)

    assert [call["seed"] for call in sampler.calls] == [11, 11, 11]
```

- [ ] **Step 5: İşin kendi tohumu varsa korunuyor**

```python
def test_a_job_that_carries_its_own_seed_keeps_it(tmp_path):
    """No job carries one today, but the port makes overwriting one possible for the first time."""
    def never():
        raise AssertionError("the job carried a seed; the port must not be asked")

    sampler = FakeSampler()

    make_with_port(tmp_path, sampler, never).generate("waves", "", 4242, source=SOURCE)

    assert sampler.calls[0]["seed"] == 4242
```

- [ ] **Step 6: Bu dosyayı koş**

Run: `python -m pytest queen-editor/backend/tests/test_mmaudio_generator.py -q`
Expected: 4 düşen, hepsi `TypeError: __init__() got an unexpected keyword argument 'new_seed'`;
eski 9 test yeşil.

---

### Task 2: Sözleşme kuyruğun gerçek planıyla koşuyor

**Files:**
- Modify: `queen-editor/backend/tests/test_producer_contract.py`

- [ ] **Step 1: Sahte sampler torch'un şartını taşısın**

`class Sampler` tümüyle şununla değişir:

```python
class Sampler:
    """Stands in for torch on the one point that decides this contract: manual_seed takes a long
    and raises on anything else. A fake that shrugs at the seed is exactly what let a seedless
    sound job reach Colab."""

    def render(self, video, prompt, negative, seed, duration):
        assert isinstance(seed, int), f"MMAudio needs an integer seed, got {seed!r}"
        return b"RIFFwav"
```

- [ ] **Step 2: Planı kuyruğun yazdığı plana çevir**

`FRAMES`'in üstündeki yorum ve iki tohum değişir:

```python
# One frame, all three layers -- so the run also proves the order: the video is made from the
# photo the same run produced, and the sound from that video.
# The seeds are the queue's own, not this file's invention: a photo job is planned with one and a
# layer job with none (queue_layer, locked by test_a_layer_job_is_planned_with_no_seed_of_its_own).
# Writing seeds in by hand here is what kept the sound producer's demand for one out of sight.
FRAMES = [
    {"id": "P0_0", "type": "photo", "number": 0, "variant": 0,
     "prompt": "kraliçe tahtta", "negative": "blurry", "seed": 1, "model": ""},
    {"id": "P0_0", "type": "video", "number": 0, "variant": 0,
     "prompt": "kamera yaklaşır", "negative": "", "seed": None, "model": ""},
    {"id": "P0_0", "type": "audio", "number": 0, "variant": 0,
     "prompt": "dalga sesi", "negative": "", "seed": None, "model": ""},
]
```

- [ ] **Step 3: Bu dosyayı koş**

Run: `python -m pytest queen-editor/backend/tests/test_producer_contract.py -q`
Expected: 1 düşen. `test_the_queue_runs_the_three_real_producers_end_to_end` `status == "done"`
beklerken `"error"` görür. `test_each_layer_is_made_from_the_one_below_it` **yeşil kalır** — o test
videonun ses üreticisine ulaştığını sınıyor, ulaşma da render'dan önce oluyor. Video tarafı da
düşmez: grafiğin kendi tohumunu bırakır.

---

### Task 3: Kuyruğun tohumsuz planladığı kilitleniyor

**Files:**
- Modify: `queen-editor/backend/tests/test_photo_usecases.py`

- [ ] **Step 1: `test_a_video_job_is_planned_for_every_frame_that_has_none`'ın hemen altına ekle**

```python
def test_a_layer_job_is_planned_with_no_seed_of_its_own():
    """Only a photo is made from a prompt and a seed; a layer is made from what is under it. The
    producer contract runs against this, so the two must not drift apart."""
    store, record, plan_store = video_project((0, "a"))

    queue_layer(sync_runner(), store, record, plan_store, FakeOrderStore(),
                {layers.PHOTO: FakeGenerator()}, lambda: "t", "düğün", layers.VIDEO)

    assert plan_store.appended[-1][0]["seed"] is None
```

- [ ] **Step 2: Bu testi koş**

Run: `python -m pytest queen-editor/backend/tests/test_photo_usecases.py -q`
Expected: hepsi yeşil — bu test bugünkü davranışı kilitliyor.

---

### Task 4: Takımı koş ve kırmızı commit'le

- [ ] **Step 1: Tam takım**

Run: `python -m pytest queen-editor/backend/tests -q`
Expected: 5 düşen (4 `TypeError`, 1 sözleşme), 592 geçen.

- [ ] **Step 2: Commit**

```bash
git add queen-editor/backend/tests docs/superpowers
git commit -F - <<'EOF'
test(queen-editor): follow the seed from the plan to the sound producer

Red on purpose -- the implementation cycle turns these green.

Five failures in two groups. The one in test_producer_contract.py is the real
one: the plan now carries what the queue actually writes, no seed on a layer
job, and the fake sampler now demands the integer torch demands. The run tries
the sound three times and stops with status error, the same shape as the Colab
run that found this.

The four in test_mmaudio_generator.py fail with TypeError instead. They hand
the generator a seed port it does not take yet, so they describe the interface
rather than reproduce the fault -- including the guard that a job carrying its
own seed keeps it, because only a port can prove it was never asked.

Green already: the queue plans a layer job with no seed. That locks today's
behaviour, so the None in the contract file is a fact rather than a claim.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** 1–4 → Task 1 · 5–6 → Task 2 · 7 → Task 3 · kırmızı commit → Task 4. Eksik yok.

**Kontrol edilen tuzak:** `make()` değiştirilmedi. Ona `new_seed` eklemek dosyadaki dokuz eski testi
de `TypeError`'a düşürürdü; o zaman kırmızı, hatayı değil kurucu imzasını anlatırdı.

**Kontrol edilen tuzak 2:** Sözleşme dosyasındaki sahte sampler `assert` atıyor, `raise` değil —
`run_loop` `Exception` yakalıyor ve `AssertionError` da odur, yani üç deneme kuralı gerçekten
işliyor ve koşu Colab'daki gibi `status: "error"` ile duruyor. Testin kırmızısı hatayı hem gösteriyor
hem şeklini koruyor.

**Kontrol edilen bağ:** Task 2'nin yorumu Task 3'ün test adını anıyor. İkisi aynı commit'te girdiği
için ad ilk andan itibaren doğru.
