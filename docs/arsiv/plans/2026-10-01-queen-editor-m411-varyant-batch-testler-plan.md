# Madde 411 — Varyantlar tek işte, test turunun planı

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*. **Commit yok** — madde
> çıktıyı değiştirdiği için her şey çalışma ağacında kalır, kullanıcı Changes'te okur.

**Hedef:** Bir prompt'un fotoğraf varyantlarının ComfyUI'ye tek batch olarak gittiğini — tek seed,
kendi adıyla ve kendi satırıyla inen her varyant, payına düşen süre, bütünüyle yeniden denenen ve
durdurulunca bütünüyle giden batch, tutmayan kartta ve tek varyantta bugünkü yol — ve ekranın
batch'in her karesini üretiliyor gösterdiğini anlatan testler.

**Yaklaşım:** Döngü sahte üreticilerle koşar: batch yapabilen yeni sahte `FakeGenerator`'ın üstüne
`fits_batch` ve `generate_batch` taşır, bugünkü sahteler batch yapamaz. İstemci ve üretici kendi
sahteleriyle, sözleşme testi gerçek üretici ve gönderilen grafikle. Ekran vitest + jsdom, sahte saat.

**Araçlar:** pytest (`parametrize`), vitest, Testing Library.

**Spec:** [m411 test turu](../specs/2026-10-01-queen-editor-m411-varyant-batch-testler-design.md)

## Her yere geçerli kurallar

- Test adları ve docstring'ler **İngilizce**; kullanıcının gördüğü metin Türkçe.
- Testler dört satırla koşulur; `skip` / `xfail` / `.skip` / `.todo` yok. Bu turda kaynak kod
  değişmiyor.
- Hiçbir test gerçek bir ComfyUI'ye, GPU'ya, Drive'a ya da saate dokunmaz.

**Arayüz — uygulama turunun vereceği:**
- Fotoğraf üreticisi: `fits_batch(count) -> bool`,
  `generate_batch(prompt, negative, seed, count, model="", lora="") -> list[bytes]`. Batch
  yapamayan üretici bu ikisini taşımaz.
- `ComfyClient.fetch_outputs(history_entry, count, extensions=None) -> list[bytes]`,
  `ComfyClient.vram_total() -> int`.
- `ComfyPhotoGenerator`: Batch Size node'u `"23"`.
- Durum: `batch` — `current` ile aynı işte üretilen öteki karelerin kimlikleri; turun ilk raporunda
  `None`.
- `useGeneration` `batch` döndürür (dizi); `Gallery` `batch` prop'u alır; `PhotoDetail` onu
  `useGeneration`'dan okur.

---

## Görev 1: `backend/tests/test_variant_batch.py` — yeni

**Dosya:** Oluştur: `queen-editor/backend/tests/test_variant_batch.py`

- [ ] **Adım 1: Dosyanın tamamı.** Sahteler `test_photo_usecases`'ten — `test_export.py`'nin yaptığı
  gibi.

```python
"""A prompt's variants made in one ComfyUI job (madde 411).

The queue's own fakes come from test_photo_usecases. None of them can make a batch, which is why
every test there still walks the one-by-one path; the producer added here can.
"""
from backend.features.photo_generation.domain import layers
from backend.features.photo_generation.domain.run_loop import make_job
from backend.features.photo_generation.domain.usecases.regenerate import regenerate
from backend.features.photo_generation.domain.usecases.resume_batch import resume_batch
from backend.features.photo_generation.domain.usecases.retry_failed import retry_failed
from backend.features.photo_generation.domain.usecases.retry_frame import retry_frame
from backend.features.photo_generation.domain.usecases.start_batch import plan_frames, start_batch
from backend.tests.test_photo_usecases import (
    Clock,
    FakeGenerator,
    FakeOrderStore,
    FakePlanStore,
    FakeRecord,
    FakeStore,
    FrameFault,
    rows_of,
    sync_runner,
    video_project,
    watched,
)

NOW = "2026-10-01T10:00:00+00:00"


class BatchGenerator(FakeGenerator):
    """A photo producer that can make a prompt's variants in one job, on a card that holds `fits`.

    `fail_on` names the prompts whose batch blows up as the frame's fault. `clock` and `seconds` say
    how long a batch works. `stop` is a runner the first batch asks to stop before it falls, the way
    Durdur interrupts ComfyUI mid-render.
    """

    def __init__(self, fits=26, fail_on=(), clock=None, seconds=0.0, stop=None):
        super().__init__(fail_on)
        self.fits, self.clock, self.seconds, self.stop = fits, clock, seconds, stop
        self.asked = []
        self.batches = []

    def fits_batch(self, count):
        self.asked.append(count)
        return count <= self.fits

    def generate_batch(self, prompt, negative, seed, count, model="", lora=""):
        self.batches.append((prompt, negative, seed, count, model, lora))
        if self.clock is not None:
            self.clock.passes(self.seconds)
        if self.stop is not None:
            runner, self.stop = self.stop, None
            runner.request_stop()
            raise RuntimeError("Processing interrupted")
        if prompt in self.fail_on:
            raise FrameFault(f"node 41: {prompt}")
        return [f"{prompt}{index}".encode() for index in range(count)]


def submit(generator, text='["a", "b"]', variants=2, seeds=(11, 22, 33, 44), runner=None,
           store=None, record=None, plan_store=None, order_store=None):
    """Kuyruğa ekle, the way the panel sends it, with these seeds drawn in turn."""
    drawn = iter(seeds)
    return start_batch(runner or sync_runner(), store or FakeStore(), record or FakeRecord(),
                       plan_store or FakePlanStore(), {layers.PHOTO: generator},
                       lambda: next(drawn), lambda: NOW, "düğün", text, "neg", variants,
                       order_store=order_store)


def one_prompt(count, seed=11):
    """A plan holding one prompt's `count` variants, the way plan_frames writes them."""
    return FakePlanStore(frames=plan_frames(0, [{"prompt": "a"}], "neg", count, lambda: seed))


def test_a_prompts_variants_go_to_the_producer_as_one_batch():
    generator = BatchGenerator()

    submit(generator)

    # One graph per prompt, carrying the seed its first variant was planned with.
    assert generator.batches == [("a", "neg", 11, 2, "", ""), ("b", "neg", 33, 2, "", "")]
    assert generator.calls == []


def test_each_variant_lands_under_its_own_name_with_its_own_picture():
    store = FakeStore()

    submit(BatchGenerator(), store=store)

    assert store.saved == [("P0_0.png", b"a0"), ("P0_1.png", b"a1"),
                           ("P1_0.png", b"b0"), ("P1_1.png", b"b1")]


class NotingStore(FakeStore):
    """Drive, writing each file it is handed into a log shared with the record."""

    def __init__(self, said):
        super().__init__()
        self.said = said

    def save(self, project, filename, data):
        self.said.append(f"file {filename}")
        return super().save(project, filename, data)


class NotingRecord(FakeRecord):
    """The record, writing each row it is handed into a log shared with Drive."""

    def __init__(self, said):
        super().__init__()
        self.said = said

    def append(self, project, entry):
        self.said.append(f"row {entry['file']}")
        super().append(project, entry)


def test_each_row_is_written_only_after_its_own_file():
    """A frame is done exactly when its row exists (CODE-STANDARD, Separation of concerns): a batch
    that dies between two files must leave no row naming a picture that is not there."""
    said = []

    submit(BatchGenerator(), text='["a"]', store=NotingStore(said), record=NotingRecord(said))

    assert said == ["file P0_0.png", "row P0_0.png", "file P0_1.png", "row P0_1.png"]


def test_every_variants_row_names_the_seed_its_batch_was_made_with():
    """The batch's variants come from one seed (madde 411, decision 1): the row says the number the
    render was handed, even though it does not make that one picture again on its own."""
    record = FakeRecord()

    submit(BatchGenerator(), record=record)

    assert [(row["frame"], row["seed"]) for row in rows_of(record, "photo")] == [
        ("P0_0", 11), ("P0_1", 11), ("P1_0", 33), ("P1_1", 33)]


def test_each_variants_time_is_its_share_of_the_batch():
    """Decision 3: a picture's time stays comparable with one made alone."""
    clock, record = Clock(), FakeRecord()

    make_job(sync_runner(), FakeStore(), record, one_prompt(4),
             {layers.PHOTO: BatchGenerator(clock=clock, seconds=80.0)}, lambda: NOW, "düğün",
             clock=clock)()

    assert [row["renderSeconds"] for row in rows_of(record, "photo")] == [20.0] * 4


def test_a_prompt_with_one_variant_is_made_as_it_always_was():
    generator = BatchGenerator()

    submit(generator, text='["a"]', variants=1)

    assert generator.calls == [("a", "neg", 11, "")]
    assert generator.batches == [] and generator.asked == []


def test_a_card_that_cannot_hold_the_batch_makes_the_variants_one_by_one():
    generator = BatchGenerator(fits=1)

    submit(generator, text='["a"]', variants=4)

    # Each with its own seed, the way every variant was made before madde 411.
    assert generator.calls == [("a", "neg", 11, ""), ("a", "neg", 22, ""),
                               ("a", "neg", 33, ""), ("a", "neg", 44, "")]
    assert generator.batches == []


def test_a_prompt_the_card_cannot_hold_is_not_batched_once_enough_of_it_is_made():
    """Decision 4 is about the prompt's batch: a card that cannot hold it makes every variant alone,
    not two alone and the rest together once what is left happens to fit."""
    generator = BatchGenerator(fits=2)

    submit(generator, text='["a"]', variants=3, seeds=(11, 22, 33))

    assert len(generator.calls) == 3 and generator.batches == []
    assert generator.asked and set(generator.asked) == {3}


def test_a_failing_batch_is_tried_again_whole_and_then_every_variant_turns_red():
    generator, record = BatchGenerator(fail_on=["a"]), FakeRecord()

    submit(generator, record=record)

    # Decision 2: the variants are tried again together -- three times, as one job (madde 8).
    assert generator.batches == [("a", "neg", 11, 2, "", "")] * 3 + [("b", "neg", 33, 2, "", "")]
    slots = record.slots("düğün")
    assert {fid: slots[fid]["photo"]["status"] for fid in ("P0_0", "P0_1", "P1_0", "P1_1")} == {
        "P0_0": "failed", "P0_1": "failed", "P1_0": "done", "P1_1": "done"}
    assert slots["P0_1"]["photo"]["error"] == "node 41: a — 3 kez denendi"


def test_a_stopped_batch_leaves_nothing_and_is_made_whole_on_resume():
    """Decision 2: a stop mid-batch loses the whole batch -- and nothing else, because nothing of it
    was written: every variant is still owed."""
    runner, store, record, plan_store = sync_runner(), FakeStore(), FakeRecord(), FakePlanStore()
    generator = BatchGenerator(stop=runner)

    submit(generator, text='["a"]', runner=runner, store=store, record=record,
           plan_store=plan_store)

    assert runner.status()["status"] == "paused"
    assert store.saved == [] and rows_of(record, "photo") == []

    resume_batch(runner, store, record, plan_store, {layers.PHOTO: generator}, lambda: NOW,
                 "düğün")

    assert generator.batches == [("a", "neg", 11, 2, "", "")] * 2
    assert [name for name, _data in store.saved] == ["P0_0.png", "P0_1.png"]


def failed_pair():
    """A prompt's two variants, both red: their batch fell three times."""
    record, seeds = FakeRecord(), iter([11, 22])
    plan_store = FakePlanStore(frames=plan_frames(0, [{"prompt": "a"}], "neg", 2,
                                                  lambda: next(seeds)))
    for fid in ("P0_0", "P0_1"):
        record.mark("düğün", fid, layers.PHOTO, f"{fid}.png", "failed", NOW,
                    error="node 41: a — 3 kez denendi")
    return record, plan_store


def test_a_variant_sent_back_with_tekrar_dene_is_made_alone():
    record, plan_store = failed_pair()
    generator = BatchGenerator()

    retry_frame(sync_runner(), FakeStore(), record, plan_store, {layers.PHOTO: generator},
                lambda: NOW, "düğün", "P0_1")

    # Its own planned seed, as before madde 411.
    assert generator.calls == [("a", "neg", 22, "")]
    assert generator.batches == []


def test_variants_sent_back_all_at_once_are_made_one_by_one():
    record, plan_store = failed_pair()
    generator = BatchGenerator()

    retry_failed(sync_runner(), FakeStore(), record, plan_store, {layers.PHOTO: generator},
                 lambda: NOW, "düğün")

    assert generator.calls == [("a", "neg", 11, ""), ("a", "neg", 22, "")]
    assert generator.batches == []


def test_a_regenerated_frame_is_made_alone():
    store, record, plan_store = video_project((0, "a"))
    generator = BatchGenerator()

    regenerate(sync_runner(), store, record, plan_store, FakeOrderStore(),
               {layers.PHOTO: generator}, lambda: 7, lambda: NOW, "düğün", "0_a", layers.PHOTO,
               "p")

    assert generator.calls == [("p", "", 7, "")]
    assert generator.batches == []


def test_a_variant_dragged_elsewhere_is_made_where_it_stands_alone():
    """The gallery's order is the order work is done in: a batch is never gathered from further
    down the queue."""
    generator = BatchGenerator()
    # Newest first, as the gallery stores it -- so made from the foot up: P0_0, P1_0, P1_1, P0_1.
    order = FakeOrderStore(["P0_1", "P1_1", "P1_0", "P0_0"])

    submit(generator, order_store=order)

    assert generator.calls == [("a", "neg", 11, ""), ("a", "neg", 22, "")]
    assert generator.batches == [("b", "neg", 33, 2, "", "")]


def test_video_jobs_are_never_batched():
    """Photo only: a frame's videos each start from a picture of their own."""
    store, record = FakeStore(), FakeRecord()
    plan_store = FakePlanStore(frames=[
        {"id": fid, "type": "video", "number": 0, "variant": variant,
         "prompt": "kamera yaklaşır", "negative": "", "seed": None, "model": ""}
        for variant, fid in enumerate(("P0_0", "P0_1"))])
    for fid in ("P0_0", "P0_1"):
        record.append("düğün", {"file": f"{fid}.png", "frame": fid, "layer": "photo",
                                "status": "done"})
        store.files[f"{fid}.png"] = b"PNG"
    generator = BatchGenerator()

    make_job(sync_runner(), store, record, plan_store, {layers.VIDEO: generator}, lambda: NOW,
             "düğün", new_seed=lambda: 5)()

    assert len(generator.calls) == 2
    assert generator.batches == [] and generator.asked == []


class Peeks(BatchGenerator):
    """Notes the status as the runner holds it while each batch is being made."""

    def __init__(self, runner):
        super().__init__()
        self.runner, self.seen = runner, []

    def generate_batch(self, *args, **kwargs):
        self.seen.append(self.runner.status())
        return super().generate_batch(*args, **kwargs)


def test_the_status_names_every_frame_its_batch_is_making():
    """The gallery draws every one of them as being made, each with the live time (madde 408)."""
    runner, reports = watched()
    generator = Peeks(runner)

    submit(generator, variants=3, seeds=(1, 2, 3, 4, 5, 6), runner=runner)

    seen = generator.seen[0]
    assert seen["current"]["id"] == "P0_0"
    assert seen["batch"] == ["P0_1", "P0_2"]
    assert seen["startedAt"] == NOW
    assert seen["pending"] == ["P1_0.png", "P1_1.png", "P1_2.png"]
    # Cleared at the top of every turn, the way the start is: nothing is being made yet.
    assert reports[0]["batch"] is None


def test_the_timing_line_names_the_batchs_files_together():
    clock, lines = Clock(), []

    make_job(sync_runner(), FakeStore(), FakeRecord(), one_prompt(2),
             {layers.PHOTO: BatchGenerator(clock=clock, seconds=80.0)}, lambda: NOW, "düğün",
             clock=clock, log=lines.append)()

    assert lines == ["⏱ P0_0.png, P0_1.png · render 80.0 sn · drive 0.0 sn"]
```

## Görev 2: `backend/tests/test_comfy_client.py`

**Dosya:** Değiştir: `queen-editor/backend/tests/test_comfy_client.py`

- [ ] **Adım 1: Dosyanın sonuna dört test.**

```python
# --- Madde 411: a prompt's variants in one batch -------------------------------------------------

def test_fetch_outputs_downloads_every_output_in_order():
    # SaveImage lists a batch's files in batch order; the comparer's previews are temp files under
    # keys of their own (rgthree's image_comparer.py).
    entry = {"outputs": {
        "50": {"images": [{"filename": "ComfyUI_00001_.png", "subfolder": "", "type": "output"},
                          {"filename": "ComfyUI_00002_.png", "subfolder": "", "type": "output"},
                          {"filename": "ComfyUI_00003_.png", "subfolder": "", "type": "output"}]},
        "57": {"a_images": [{"filename": "rgthree.compare._temp_00001_.png", "type": "temp"}],
               "b_images": [{"filename": "rgthree.compare._temp_00002_.png", "type": "temp"}]}}}
    http = FakeHttp(gets=[FakeResponse(content=b"ONE"), FakeResponse(content=b"TWO"),
                          FakeResponse(content=b"THREE")])

    assert client_with(http).fetch_outputs(entry, 3) == [b"ONE", b"TWO", b"THREE"]
    assert [params["filename"] for _url, params in http.get_calls] == [
        "ComfyUI_00001_.png", "ComfyUI_00002_.png", "ComfyUI_00003_.png"]


def test_fetch_outputs_stops_when_the_count_is_not_what_was_asked():
    entry = {"outputs": {"50": {"images": [{"filename": "a.png", "type": "output"},
                                           {"filename": "b.png", "type": "output"}]}}}

    with pytest.raises(RuntimeError) as exc:
        client_with(FakeHttp()).fetch_outputs(entry, 3)

    assert "3 çıktı bekleniyordu, 2 geldi" in str(exc.value)
    assert "b.png" in str(exc.value)


# What ComfyUI's /system_stats answers on Colab's T4 (server.py, system_stats).
STATS = {"system": {"os": "linux"},
         "devices": [{"name": "cuda:0 Tesla T4 : cudaMallocAsync", "type": "cuda", "index": 0,
                      "vram_total": 15828320256, "vram_free": 15512174592,
                      "torch_vram_total": 0, "torch_vram_free": 0}]}


def test_vram_total_is_the_card_comfyui_renders_on():
    http = FakeHttp(gets=[FakeResponse(STATS)])

    assert client_with(http).vram_total() == 15828320256
    assert http.get_calls[0][0] == "http://comfy:8188/system_stats"


def test_asking_about_the_card_names_an_unreachable_server_too(tmp_path):
    client = client_with(FakeHttp(refuse=True), log_path=_comfy_log(tmp_path))

    with pytest.raises(Exception) as exc:
        client.vram_total()

    assert str(exc.value).splitlines()[0] == "ComfyUI'ye bağlanılamadı — http://comfy:8188"
```

## Görev 3: `backend/tests/test_comfy_photo_generator.py`

**Dosya:** Değiştir: `queen-editor/backend/tests/test_comfy_photo_generator.py`

- [ ] **Adım 1: `FakeClient` batch'i ve kartı bilir.**

```python
class FakeClient:
    def __init__(self, vram=0):
        self.submitted = None
        self.waited = None
        self.fetched = None
        # What /system_stats says the card holds, in bytes (madde 411).
        self.vram = vram

    ...

    def fetch_outputs(self, history, count):
        self.fetched = count
        return [f"PNG{index}".encode() for index in range(count)]

    def vram_total(self):
        return self.vram
```

- [ ] **Adım 2: Varsayılan grafiğe Batch Size node'u** — `write_graph`'ın sözlüğüne, `"4"`'ün
  arkasına:

```python
        "23": {"inputs": {"value": 1}, "class_type": "easy int", "_meta": {"title": "Batch Size"}},
```

- [ ] **Adım 3: Dosyanın sonuna altı test** *(sonuncusu beş durumla parametreli)*.

```python
# --- Madde 411: a prompt's variants in one batch -------------------------------------------------

def test_a_batch_writes_its_count_into_the_batch_size_node(tmp_path):
    client, generator = generator_at(tmp_path)

    assert generator.generate_batch("kraliçe tahtta", "blurry", 12345, 4) == [
        b"PNG0", b"PNG1", b"PNG2", b"PNG3"]

    assert client.submitted["23"]["inputs"]["value"] == 4
    assert client.fetched == 4
    # Everything else is the single render's: the same words, the same negative, one seed.
    assert client.submitted["3"]["inputs"]["populated_text"] == "kraliçe tahtta"
    assert client.submitted["4"]["inputs"]["populated_text"] == "blurry"
    assert client.submitted["40"]["inputs"]["seed"] == 12345
    # The stall guard is a photo's: four pictures in one job get four of them.
    assert client.waited == ("p1", 240)


def test_a_batch_carries_the_model_and_the_lora_like_a_single_render(tmp_path):
    client, generator = generator_at(tmp_path)

    generator.generate_batch("kraliçe tahtta", "", 1, 2, "nova3dcg", "slime")

    assert client.submitted["45"]["inputs"]["ckpt_name"] == "nova3DCGXL_ilV90.safetensors"
    assert lora_slots(client.submitted["27"]["inputs"]) == SLIME
    assert client.submitted["3"]["inputs"]["populated_text"] == \
        "translucent penetration, kraliçe tahtta"


def test_a_single_render_leaves_the_batch_size_as_the_export_ships_it(tmp_path):
    client, generator = generator_at(tmp_path)

    generator.generate("kraliçe", "", 1)

    assert client.submitted["23"]["inputs"]["value"] == 1


def test_a_batch_does_not_mutate_the_file_on_disk(tmp_path):
    path = write_graph(tmp_path)

    ComfyPhotoGenerator(FakeClient(), path, timeout=60).generate_batch("yeni", "", 1, 3)

    with open(path, encoding="utf-8") as f:
        assert json.load(f)["23"]["inputs"]["value"] == 1


def test_a_batch_on_a_graph_with_no_batch_size_node_says_which_node_is_missing(tmp_path):
    """A re-export can renumber the graph. Asked for only when a batch needs it: a single render
    never touches the node."""
    graph = {
        "3": {"inputs": {"wildcard_text": "", "populated_text": ""}},
        "4": {"inputs": {"wildcard_text": "", "populated_text": ""}},
        "40": {"inputs": {"seed": -1}},
        "45": {"inputs": {"ckpt_name": "export.safetensors"}},
    }
    _client, generator = generator_at(tmp_path, graph)

    with pytest.raises(RuntimeError) as exc:
        generator.generate_batch("kraliçe", "", 1, 2)

    assert "23" in str(exc.value)


# The cards' total memory as PyTorch reports it on Colab: "GPU 0 has a total capacity of ...".
T4 = round(14.74 * 1024 ** 3)
A100 = round(39.56 * 1024 ** 3)
SMALL = 8 * 1024 ** 3


@pytest.mark.parametrize("vram, count, fits", [
    (T4, 4, True), (T4, 7, True), (T4, 8, False), (A100, 26, True), (SMALL, 2, False),
], ids=["t4-4", "t4-7", "t4-8", "a100-26", "8gib-2"])
def test_the_card_is_weighed_by_comfyuis_own_memory_rules(tmp_path, vram, count, fits):
    """Decision 4: a card whose memory is not enough for the batch makes the variants one by one.
    The numbers behind the line are ComfyUI's own -- see comfy_photo_generator.py."""
    generator = ComfyPhotoGenerator(FakeClient(vram=vram), write_graph(tmp_path), timeout=60)

    assert generator.fits_batch(count) is fits
```

## Görev 4: `backend/tests/test_producer_contract.py`

**Dosya:** Değiştir: `queen-editor/backend/tests/test_producer_contract.py`

- [ ] **Adım 1: Dosyanın sonuna bir sahte, bir plan, bir test.**

```python
class BatchComfy(PhotoComfy):
    """The photo graph's server on an A100: it holds the batch, and answers with as many pictures
    as the graph asked for."""

    def __init__(self):
        self.graphs = []

    def submit(self, workflow):
        self.graphs.append(workflow)
        return "p1"

    def vram_total(self):
        return round(39.56 * 1024 ** 3)

    def fetch_outputs(self, history, count):
        return [f"PNG{index}".encode() for index in range(count)]


# One prompt's two variants, the way plan_frames writes them.
VARIANTS = [{"id": f"P0_{variant}", "type": "photo", "number": 0, "variant": variant,
             "prompt": "kraliçe tahtta", "negative": "blurry", "seed": 1, "model": "", "lora": ""}
            for variant in range(2)]


def test_a_prompts_variants_go_through_the_real_photo_producer_as_one_batch():
    """Madde 411 on the shipped graph: the node the count is written into is the one its latent
    reads the batch size from, so ComfyUI really makes both pictures in one job."""
    store, comfy = Store(), BatchComfy()

    make_job(Runner(), store, Record(), Plan(VARIANTS),
             {layers.PHOTO: ComfyPhotoGenerator(comfy, PHOTO_GRAPH, timeout=60)},
             lambda: "2026-10-01T00:00:00+00:00", "düğün")()

    assert len(comfy.graphs) == 1
    graph = comfy.graphs[0]
    assert graph["23"]["inputs"]["value"] == 2
    assert graph["25"]["class_type"] == "EmptyLatentImage"
    assert graph["25"]["inputs"]["batch_size"] == ["23", 0]
    assert store.saved == ["P0_0.png", "P0_1.png"]
```

## Görev 5: Ekran testleri

**Dosyalar:** Değiştir: `queen-editor/frontend/src/features/photo_generation/useGeneration.test.jsx`,
`Gallery.test.jsx`, `PhotoDetail.test.jsx`, `ProjectScreen.test.jsx`

- [ ] **Adım 1: `useGeneration.test.jsx`** — `describe("useGeneration", …)` içine, "says no start for
  another project's run"ın arkasına:

```jsx
  it("names the frames made in one batch with the one it is on (madde 411)", async () => {
    getStatus.mockResolvedValue({ ...RUNNING, current: { id: "P0_0", type: "photo" },
                                  batch: ["P0_1", "P0_2"] });
    listFrames.mockResolvedValue([]);

    const { result } = renderHook(() => useGeneration("düğün"));
    await settle();

    expect(result.current.batch).toEqual(["P0_1", "P0_2"]);
  });

  it("names no batch for another project's run", async () => {
    getStatus.mockResolvedValue({ ...RUNNING, project: "komşu", current: { id: "P0_0" },
                                  batch: ["P0_1"] });
    listFrames.mockResolvedValue([]);

    const { result } = renderHook(() => useGeneration("düğün"));
    await settle();

    expect(result.current.batch).toEqual([]);
  });

  it("does not count the frames a batch is making as waiting", async () => {
    getStatus.mockResolvedValue({ ...RUNNING, current: { id: "P0_0" }, batch: ["P0_1", "P0_2"] });
    listFrames.mockResolvedValue(["P0_0", "P0_1", "P0_2", "P0_3"].map((id) => (
      { id, file: `${id}.png`, status: "pending", owed: ["photo"], failed: [] })));

    const { result } = renderHook(() => useGeneration("düğün"));
    await settle();

    expect(result.current.queue).toEqual([{ layer: "photo", owed: 1 }]);
  });
```

- [ ] **Adım 2: `Gallery.test.jsx`** — dosyanın sonuna:

```jsx
describe("Gallery — a prompt's variants made in one batch (madde 411)", () => {
  const AGO_46 = "2026-10-01T09:59:14+00:00";
  const pillOf = (name) => tileOf(name).querySelector("[data-pill]");
  const VARIANTS = [pending("P0_3.png"), pending("P0_2.png"), pending("P0_1.png"),
                    pending("P0_0.png")];

  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-10-01T10:00:00Z"));
  });
  afterEach(() => vi.useRealTimers());

  it("says every tile of the batch is being made, with the batch's live time", () => {
    renderGallery({ frames: VARIANTS, current: "P0_0", batch: ["P0_1", "P0_2", "P0_3"],
                    currentLayer: "photo", running: true, startedAt: AGO_46 });

    ["P0_0.png", "P0_1.png", "P0_2.png", "P0_3.png"].forEach((name) => {
      expect(pillOf(name).textContent).toBe("foto üretiliyor0:46");
    });
  });

  it("offers no ring on a tile the batch is making", () => {
    renderGallery({ frames: [pending("P1_0.png"), ...VARIANTS], current: "P0_0",
                    batch: ["P0_1"], currentLayer: "photo", running: true });

    expect(checkOf("P0_1.png")).toBeNull();
    expect(checkOf("P1_0.png")).not.toBeNull();
  });
});
```

- [ ] **Adım 3: `PhotoDetail.test.jsx`** — dosyanın sonuna:

```jsx
describe("PhotoDetail — a frame its batch is making (madde 411)", () => {
  const AGO_46 = "2026-10-01T09:59:14+00:00";
  const timeShown = () => document.querySelector("[data-time]");

  beforeEach(() => { vi.setSystemTime(new Date("2026-10-01T10:00:00Z")); });

  it("counts the batch's time live on every frame it is making", async () => {
    await open("P0_1", {
      frames: [waiting("P0_1.png", "kırmızı elbise"), waiting("P0_0.png", "kırmızı elbise")],
      status: { status: "running", project: "düğün", current: { id: "P0_0", type: "photo" },
                batch: ["P0_1"], startedAt: AGO_46 },
    });

    expect(timeShown().textContent).toBe("0:46");
    expect(timeShown().style.color).toBe("var(--accent)");
  });
});
```

- [ ] **Adım 4: `ProjectScreen.test.jsx`** — dosyanın sonuna:

```jsx
describe("ProjectScreen — the tiles of a batch show its time (madde 411)", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-10-01T10:00:00Z"));
  });
  afterEach(() => vi.useRealTimers());

  it("hands the gallery the frames made in one batch with the one it is on", async () => {
    listFrames.mockResolvedValue(["P0_1", "P0_0"].map((id) => (
      { id, file: `${id}.png`, status: "pending", layers: {}, owed: ["photo"], failed: [] })));
    getStatus.mockResolvedValue({ status: "running", project: "süre",
                                  current: { id: "P0_0", type: "photo" }, batch: ["P0_1"],
                                  startedAt: "2026-10-01T09:59:14+00:00" });
    renderScreen("süre");
    await act(async () => { await vi.advanceTimersByTimeAsync(0); });

    expect(document.getElementById("tile-P0_1").querySelector("[data-pill]").textContent)
      .toContain("0:46");
  });
});
```

## Görev 6: Koşu — kırmızı, commit yok

- [ ] **Adım 1: Dört satırı koş**, paralel, yazıldığı gibi:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: `queen-editor` pytest'inde kırmızı — `test_variant_batch.py`'nin 1, 2, 4, 5, 8, 9, 10, 14,
16, 17'si; `test_comfy_client.py`'nin dört yenisi; `test_comfy_photo_generator.py`'nin 22 (ikisi),
24, 25'i ve beş durumun beşi; sözleşme testi — 24. Yeşil — `test_variant_batch.py`'nin 3, 6, 7, 11,
12, 13, 15'i (bugünü kilitliyorlar) ve 23. `queen-editor` vitest'inde yedi yeni test kırmızı. Öteki
her şey yeşil; öteki iki satır yeşil.

**Koşuldu:** `24 failed, 1265 passed` · vitest `7 failed | 787 passed (794)` · queen-agent
`989 passed` · queen-agent vitest `838 passed (838)`.

- [ ] **Adım 2: Commit yok.** Testler, spec ve bu plan çalışma ağacında kalır.
