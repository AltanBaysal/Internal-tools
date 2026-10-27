# Madde 411 — Varyantlar tek işte, uygulama turunun planı

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*. **Commit yok**, `dist`
> kurulmaz — çalışma ağacında kalır, kullanıcı Changes'te okur.

**Hedef:** Test turunun kırmızı testlerini kodla yeşile çevirmek — testlerin anlattığı kadar, fazlası
değil.

**Yaklaşım:** İstemci çok çıktıyı indirir ve kartın belleğini okur; fotoğraf üreticisi batch yapar ve
kartı tartar; saf bir domain kuralı hangi işlerin birlikte üretileceğini söyler; döngü, üreticisi
batch yapabiliyor ve kart tutuyorsa onları tek işte ister. Ekran batch'in karelerini üretiliyor
gösterir.

**Spec:** [m411 uygulama turu](../specs/2026-10-01-queen-editor-m411-varyant-batch-uygulama-design.md)
· [m411 test turu](../specs/2026-10-01-queen-editor-m411-varyant-batch-testler-design.md)

## Her yere geçerli kurallar

- Kod, yorum, docstring İngilizce; kullanıcının gördüğü metin Türkçe. Yorum neden'i söyler.
- FOUNDATION 1–2: her satır kendi dosyasından sonra; durdurulan batch hiçbir şey yazmaz.
- CODE-STANDARD: servis özellik bilmez (node id yok, prompt yok); domain saf; dosya şeması `data/`'da.
- Testlere dokunulmaz — test turunun 22. testindeki bekleme sınırı düzeltmesi dışında (spec'te).

---

## Görev 1: `services/comfy/client.py`

**Dosya:** Değiştir: `queen-editor/backend/services/comfy/client.py`

**Üretir:** `fetch_outputs(history_entry, count, extensions=None) -> list[bytes]`,
`vram_total() -> int`; `fetch_output` aynı.

- [ ] **Adım 1: Modül belgesi** — ilk satır:

```python
"""ComfyUI transport -- submit a graph, wait for it, pull the files it produced, say how much memory
the card it renders on has.
```

- [ ] **Adım 2: `fetch_output` `fetch_outputs`'a dayanır; indirme `_view`'da.**

```python
    def fetch_output(self, history_entry, extensions=None):
        """Download THE produced file over /view and return its bytes.

        Exactly one real output is the contract: silently picking one of N would hide a graph whose
        batch size is not 1, so the raw outputs are printed and the render stops.

        `extensions` is how a caller says which medium it came for: a video graph often carries an
        image node as well, so the file is chosen by its own name rather than by which key it
        landed in -- which key that is (images, gifs, videos, audio) is the node's own business.
        No extensions means the images a photo graph makes.
        """
        return self.fetch_outputs(history_entry, 1, extensions)[0]

    def fetch_outputs(self, history_entry, count, extensions=None):
        """Download the `count` produced files over /view, in the order the graph listed them -- a
        batch's pictures in the batch's order (madde 411).

        type=="output" drops temp previews (a preview node registers temp files). Any other number
        of real outputs stops the render with the raw outputs printed: taking what came would hand
        a frame a picture that is not its own, or none.
        """
        outputs = []
        for node_output in history_entry.get("outputs", {}).values():
            groups = node_output.values() if extensions else [node_output.get("images", [])]
            for group in groups:
                if not isinstance(group, list):
                    continue
                for item in group:
                    if not isinstance(item, dict) or item.get("type", "output") != "output":
                        continue
                    if extensions and not item.get("filename", "").lower().endswith(
                            tuple(extensions)):
                        continue
                    outputs.append(item)
        came = json.dumps(history_entry.get("outputs", {}), indent=2, ensure_ascii=False)
        if not outputs:
            wanted = ", ".join(extensions) if extensions else "görsel"
            raise RuntimeError(f"{wanted} çıktısı gelmedi — gelenler:\n{came}")
        if len(outputs) != count:
            raise RuntimeError(f"{count} çıktı bekleniyordu, {len(outputs)} geldi — grafikte "
                               f"Batch Size {count} mi?\n{came}")
        return [self._view(item) for item in outputs]

    def _view(self, item):
        """One produced file's bytes."""
        resp = self._send("get", f"{self.base}/view", timeout=300, params={
            "filename": item["filename"],
            "subfolder": item.get("subfolder", ""),
            "type": "output",
        })
        resp.raise_for_status()
        return resp.content

    def vram_total(self):
        """The memory of the card ComfyUI renders on, in bytes, as /system_stats reports it -- it
        lists that device first. What decides whether a prompt's variants fit in one batch
        (madde 411)."""
        resp = self._send("get", f"{self.base}/system_stats", timeout=30)
        resp.raise_for_status()
        return resp.json()["devices"][0]["vram_total"]
```

## Görev 2: `data/comfy_photo_generator.py`

**Dosya:** Değiştir: `queen-editor/backend/features/photo_generation/data/comfy_photo_generator.py`

**Tüketir:** Görev 1'in `fetch_outputs`, `vram_total`. **Üretir:**
`generate_batch(prompt, negative, seed, count, model="", lora="") -> list[bytes]`,
`fits_batch(count) -> bool`, `BATCH_NODE = "23"`.

- [ ] **Adım 1: Modül belgesi ve sabitler.**

```python
"""PhotoGenerator over ComfyUI -- the only place that knows what the graph looks like.

Node ids come from our own export (queen-editor/workflow_api.json):
  "3"  ImpactWildcardProcessor, _meta.title "POSITIVE"
  "4"  ImpactWildcardProcessor, _meta.title "NEGATIVE"
  "23" easy int "Batch Size" -> EmptyLatentImage's batch_size: how many pictures one job makes
  "27" Power Lora Loader (rgthree) -> which loras are switched on, and how strongly
  "40" Seed (rgthree) -> KSampler, FaceDetailer and both wildcard processors read it
  "45" CheckpointLoaderSimple -> which model renders the frame

A new export can renumber these; then this file changes and nothing else does.
"""
import json

from backend.features.photo_generation.domain import catalog

PROMPT_NODE = "3"
NEGATIVE_NODE = "4"
BATCH_NODE = "23"
LORA_NODE = "27"
SEED_NODE = "40"
MODEL_NODE = "45"

# What one batch of this graph asks of the card, by ComfyUI's own memory rules (madde 411) -- the
# card is weighed the way ComfyUI weighs it, not by a number of ours.
# The weights: SDXL's UNet, 2.6 billion parameters (the SDXL paper) at two bytes each in fp16.
WEIGHT_BYTES = 2.6e9 * 2
# What ComfyUI keeps back whatever the batch: minimum_inference_memory(), 0.8 GiB, plus the 400 MiB
# EXTRA_RESERVED_VRAM it holds on Linux (comfy/model_management.py).
RESERVED_BYTES = 0.8 * 1024 ** 3 + 400 * 1024 ** 2
# One picture's share of sampling: memory_required() -- latent area x 2 bytes x 0.01 x SDXL's
# memory_usage_factor 0.8, in MiB (comfy/model_base.py, supported_models.py) -- for this graph's
# 1024 x 1536, a 128 x 192 latent, doubled by cfg (sampler_helpers.py), and 1.5 times that, which
# _calc_cond_batch wants free before it runs cond and uncond together (samplers.py). A new size in
# nodes "1" and "11" changes this line.
PICTURE_BYTES = 1.5 * 2 * (128 * 192) * 2 * 0.01 * 0.8 * 1024 ** 2
```

- [ ] **Adım 2: `generate` grafiği `_graph`'tan alır; `generate_batch`, `fits_batch`.**

```python
    def generate(self, prompt, negative, seed, model="", lora="", source=None, end=None,
                 references=()):
        """`source` and `end` are nobody's business here: a picture is made from its words alone and
        arrives nowhere. Both are taken because the queue has one call shape for every producer --
        see ports.PhotoGenerator.
        """
        workflow = self._graph(prompt, negative, seed, model, lora)
        prompt_id = self._client.submit(workflow)
        history = self._client.wait(prompt_id, self._timeout)
        return self._client.fetch_output(history)

    def generate_batch(self, prompt, negative, seed, count, model="", lora=""):
        """`count` pictures of one prompt in one ComfyUI job, their noise drawn from one seed
        (madde 411), in the batch's order. The count goes into the graph's own Batch Size node,
        the one its latent reads.

        The stall guard is a photo's, so a batch gets one per picture: seven on a T4 take as long
        as seven made one by one, and a single photo's guard would call that a stall.
        """
        workflow = self._graph(prompt, negative, seed, model, lora)
        if BATCH_NODE not in workflow:
            raise RuntimeError(f"Workflow'da {BATCH_NODE} node yok — grafik yeniden export edilmiş "
                               "olabilir, Batch Size node'unun id'sini güncelle")
        workflow[BATCH_NODE]["inputs"]["value"] = count
        prompt_id = self._client.submit(workflow)
        history = self._client.wait(prompt_id, self._timeout * count)
        return self._client.fetch_outputs(history, count)

    def fits_batch(self, count):
        """Whether the card ComfyUI renders on holds `count` pictures of this graph in one batch."""
        needed = WEIGHT_BYTES + RESERVED_BYTES + count * PICTURE_BYTES
        return self._client.vram_total() >= needed

    def _graph(self, prompt, negative, seed, model, lora):
        """The shipped graph with this picture's words, seed, model and lora written in."""
        workflow = self._load()
        model, lora = catalog.LEGACY.get(model, (model, lora))
        chosen = self._model(model)
        extra = self._lora(lora)
        ... (bugünkü generate'in gövdesi, submit'e kadar, aynen)
        return workflow
```

## Görev 3: Domain — `variant_batch.py`, `run_loop.py`, `ports.py`

**Dosyalar:** Oluştur: `queen-editor/backend/features/photo_generation/domain/variant_batch.py`.
Değiştir: `run_loop.py`, `ports.py`.

**Üretir:** `variant_batch.together(owed, slots) -> list`, `variant_batch.asked(jobs, head) -> int`;
durumda `batch`.

- [ ] **Adım 1: `variant_batch.py`.**

```python
"""Which of the owed photos one render makes together (madde 411).

A prompt's variants are planned as frames of their own -- P3_0, P3_1, ... -- that share everything a
picture is made from and differ only in their seed. ComfyUI makes them as one batch from one seed,
so the variants standing together at the head of the queue go to it as one job.
"""
from backend.features.photo_generation.domain import layers, queue

# What a picture is made from beside its seed: variants that agree on all of it render alike.
MADE_FROM = ("prompt", "negative", "model", "lora")


def _variant_of(job, head):
    """Whether `job` is a photo of the prompt `head` was planned from."""
    return (queue.type_of(job) == layers.PHOTO and job.get("number") == head.get("number")
            and all(job.get(key) == head.get(key) for key in MADE_FROM))


def _fresh(job, slots):
    """Never had a turn: nothing was ever written about its picture. A photo sent back with Tekrar
    dene has its line, and is made alone with its own seed, the way it always was."""
    return layers.PHOTO not in slots.get(job["id"], {})


def together(owed, slots):
    """The head of the queue and the variants of its prompt standing right behind it.

    Right behind it, never gathered from further down: the gallery's order is the order work is done
    in, so a variant dragged elsewhere is made where it stands. Only a photo: a video's variants each
    start from a picture of their own.
    """
    head = owed[0]
    if not (_variant_of(head, head) and _fresh(head, slots)):
        return [head]
    group = [head]
    for job in owed[1:]:
        if not (_variant_of(job, head) and _fresh(job, slots)):
            break
        group.append(job)
    return group


def asked(jobs, head):
    """How many variants the plan asked of `head`'s prompt: the batch a card has to hold."""
    return len({job["id"] for job in jobs if _variant_of(job, head)})
```

- [ ] **Adım 2: `run_loop.py` — içe aktarma, iki yardımcı.** `variant_batch` domain içe aktarmasına
  eklenir; `_made_with`'in altına:

```python
def _made_together(owed, jobs, slots, producer):
    """The jobs this turn's render makes: the head of the queue, and the variants of its prompt that
    go with it in one batch (madde 411).

    Together only when the producer can make a batch at all -- a photo's can, a video's and a
    sound's cannot -- and the card holds every variant the prompt was asked for. Asked with that
    count rather than with what is left of it: a prompt too big for the card is made one by one to
    its end, as before, not one by one until the rest happens to fit.
    """
    group = variant_batch.together(owed, slots)
    if len(group) > 1 and hasattr(producer, "fits_batch") \
            and producer.fits_batch(variant_batch.asked(jobs, group[0])):
        return group
    return group[:1]


def _files(name, together):
    """Each made job's file, in order: the head's own name, then the other pictures of its batch."""
    return [name] + [photo_file(other["id"]) for other in together[1:]]
```

- [ ] **Adım 3: Turun ilk raporu `batch`'i temizler; `try`'dan önce `together`.**

```python
            progress = {**queue.counts(jobs, slots),
                        "current": None if writing else current,
                        "pending": [photo_file(j["id"])
                                    for j in (owed if writing else owed[1:])],
                        "startedAt": None, "batch": None}
            runner.report(progress)
            # What this turn makes: the job in hand alone, unless its prompt's variants go with it.
            together = [current]
            try:
```

- [ ] **Adım 4: Üretim dalı.**

```python
                    together = _made_together(owed, jobs, slots, producer)
                    # ... (madde 405/408 yorumu aynen) ...
                    runner.report({**progress, "startedAt": now(),
                                   "batch": [other["id"] for other in together[1:]],
                                   "pending": [photo_file(j["id"])
                                               for j in owed[len(together):]]})
                    started = clock()
                    if len(together) > 1:
                        made = producer.generate_batch(prompt, current["negative"], chosen,
                                                       len(together), current["model"],
                                                       current.get("lora", ""))
                    else:
                        made = [producer.generate(prompt, current["negative"], chosen,
                                                  current["model"], current.get("lora", ""),
                                                  source=under, end=ending, references=pool)]
```

- [ ] **Adım 5: Karenin hatası batch'in her işini kırmızı yapar.**

```python
                    with named.steady() as project:
                        for failed, file in zip(together, _files(name, together)):
                            record.mark(project, failed["id"], kind, file, queue.FAILED, now(),
                                        error=policy.frame_reason(exc, attempts))
```

- [ ] **Adım 6: İniş — her iş önce dosya, sonra satır; süre payı; video `made[0]`; zaman satırı.**

```python
            rendered = clock()
            # A batch's seconds shared out, so a picture's time reads like one made alone
            # (madde 411); a job made alone keeps all of its own.
            seconds = round((rendered - started) / len(together), 1)
            files = []
            with named.steady() as project:
                for landed, file, data in zip(together, _files(name, together), made):
                    filename = store.save(project, file, data)
                    files.append(filename)
                    # Only after the file exists: the line is what "this layer is here" means.
                    record.append(project, {"file": filename, "frame": landed["id"], "layer": kind,
                                            "status": queue.DONE,
                                            "prompt": prompt, "negative": current["negative"],
                                            "seed": chosen, "createdAt": now(),
                                            "renderSeconds": seconds,
                                            **_made_with(current, ending)})
                # ... (madde 296 bloğu aynen; _first_frame(stills, made[0], log) -- a video is
                # always made alone) ...
            if log:
                log(f"⏱ {', '.join(files)} · render {rendered - started:.1f} sn"
                    f" · drive {clock() - rendered:.1f} sn")
```

- [ ] **Adım 7: `ports.py`** — `PhotoGenerator`'ın altına:

```python
class BatchPhotoGenerator(PhotoGenerator, Protocol):
    """A photo producer that can also make a prompt's variants in one job (madde 411). The loop asks
    for these only of a producer that has them -- a video's and a sound's do not -- and makes the
    variants one by one otherwise."""

    def fits_batch(self, count: int) -> bool:
        """Whether the card holds `count` pictures of one prompt in one batch."""
        ...

    def generate_batch(self, prompt: str, negative: str, seed: int, count: int, model: str = "",
                       lora: str = "") -> list:
        """`count` pictures of one prompt from one seed, as bytes, in the batch's order."""
        ...
```

## Görev 4: Ekran

**Dosyalar:** Değiştir: `useGeneration.js`, `Gallery.jsx`, `PhotoDetail.jsx`, `ProjectScreen.jsx`
(`queen-editor/frontend/src/features/photo_generation/`).

- [ ] **Adım 1: `useGeneration.js`.**

```js
  const startedAt = current ? job.startedAt || null : null;
  // The other frames made in the same render, when a prompt's variants go to ComfyUI as one batch
  // (madde 411): each of them is being made as much as `current` is. The worker names none between
  // two renders.
  const batch = current ? job.batch || [] : [];
  ...
    (frame.owed || []).forEach((layer) => {
      if ((frame.id === current || batch.includes(frame.id)) && layer === currentLayer) return;
      owedByKind[layer] += 1;
    });
  ...
  return { job: told, known, frames, error, errorField, stopping, queue, failures,
           current, currentLayer, startedAt, batch,
           ... };
```

- [ ] **Adım 2: `Gallery.jsx`** — prop `batch = []`; `selecting`'in altına:

```js
  // Every frame the worker is making: the one it holds and the rest of its batch (madde 411). None
  // of them can be chosen, and each draws the live time.
  const making = (fid) => fid === current || batch.includes(fid);
```

`press`'in shift dizisi `.filter((id) => !making(id))`, `selectable` `frames.filter((frame) =>
!making(frame.id))`, kutucuk `const rendering = making(frame.id) ? (currentLayer || "photo") : null;`.

- [ ] **Adım 3: `PhotoDetail.jsx`** — hook'tan `batch`;
  `const running = frame && (frame.id === current || batch.includes(frame.id)) ? (currentLayer ||
  "photo") : null;` — yorum: "the worker is holding on THIS frame, alone or in its batch".

- [ ] **Adım 4: `ProjectScreen.jsx`** — hook'tan `batch`; `<Gallery … current={current} batch={batch}`.

## Görev 5: `CODE-STANDARD.md`

- [ ] **Adım 1:** Tablo: `photo ("3", "4", "23", "40", "45")`. Servisler: `comfy/` (… submit a graph,
  wait for it, fetch the files it produced, read the card's memory; no node id, …).

## Görev 6: Koşu — yeşil, commit yok

- [ ] **Adım 1: Dört satır**, paralel, yazıldığı gibi. Beklenen: dördü de yeşil.
  **Koşuldu:** queen-editor `1289 passed` · vitest `794 passed (794)` · queen-agent `989 passed` ·
  queen-agent vitest `838 passed (838)`.
- [ ] **Adım 2:** FOUNDATION, CODE-STANDARD ve *Bitti sayılır*'a karşı fark okunur. Commit yok,
  `dist` yok.
