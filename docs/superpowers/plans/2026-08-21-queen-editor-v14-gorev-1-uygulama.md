# v14 Görev 1 — Motorun bitiş karesi alabilmesi: UYGULAMA döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Test döngüsünün kırmızı bıraktığı yirmi testi yeşile döndürmek: video üreticisi iki grafik
tutsun, bitiş karesi verildiğinde ikincisini yüklesin, üç üretici de `end` argümanını alsın, ve yeni
grafiğin okuduğu model hem üreticiler grubunda hem defterin indirdiği listede olsun.

**Architecture:** Karar tek yerde: `ComfyVideoGenerator.generate`, bir bitiş karesi verilip
verilmediğine bakıp iki grafikten birini yüklüyor. "Üretim modu" kelimesi bu katmana hiç inmiyor —
loop ile bağlı arasındaki fark yalnız hangi fotoğrafın geldiği, ve onu kuyruk biliyor. `_load` artık
yolu ve beklenen node'ları argüman alıyor, böylece iki grafik tek yükleyiciyi paylaşıyor ve hata
cümlesindeki dosya adı yolun kendisinden çıkıyor.

**Tech Stack:** Python 3, Flask, ComfyUI HTTP API, Jupyter (Colab).

**Spec:** [uygulama turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-1-bitis-karesi-uygulama-design.md)

## Global Constraints

- **Test dosyaları bu döngüde değişmiyor.** Kırmızı commit'lenen yirmi test neyi tarif ediyorsa kod
  odur; bir testi düzeltmek gerekiyorsa bu, kararın yanlış olduğunun işaretidir ve önce konuşulur.
- Yorumlar ve docstring'ler **İngilizce**; kullanıcıya görünen metin (hata cümleleri, defterin
  markdown'ı ve çıktısı) **Türkçe**.
- **Yorum NEDEN'i söyler ve yalnız bugün doğru olanı.** `# OLD:` / `# NEW:` izi yok.
- **Hata mesajında sebep uydurulmaz** — dosya adı yoldan okunur, elle yazılmaz.
- Commit mesajında **çift tırnak yok**, ve **amend yok**.
- Komut: dört satır, birebir, boru yok.
- `dist/` **derlenmiyor** — bu döngüde ön yüz kaynağı değişmiyor.
- Commit **yeşil gider**.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `backend/config.py` | yolların tek yeri | 1 sabit eklenir |
| `data/comfy_video_generator.py` | iki grafiği bilen tek yer | kurucu, `generate`, `_load`, `seconds` |
| `domain/ports.py` | kuyruğun üreticiyle sözleşmesi | imzaya `end` |
| `data/comfy_photo_generator.py` | foto üreticisi | imzaya `end`, yok sayılır |
| `data/mmaudio_generator.py` | ses üreticisi | imzaya `end`, yok sayılır |
| `features/producers/domain/model_groups.py` | "kurulu mu" yargısının listesi | 1 satır eklenir |
| `backend/main.py` | bileşim kökü | ikinci yol geçilir |
| `app.ipynb` | modelleri indiren yer | klasör, satır, denetim, tahmin |

---

### Task 1: Yolun tanımı

**Files:**
- Modify: `queen-editor/backend/config.py`

**Interfaces:**
- Produces: `config.VIDEO_FIRST_LAST_WORKFLOW_PATH` — Task 5 ve `test_workflow_asset.py` buna
  dayanıyor.

- [ ] **Step 1: Sabiti ekle**

`VIDEO_WORKFLOW_PATH`'in hemen altına:

```python
# The second video graph: a video that ends on a chosen picture. Its own pipeline rather than the
# one above with a node swapped, so it ships beside it and standard production is untouched.
VIDEO_FIRST_LAST_WORKFLOW_PATH = os.path.join(os.path.dirname(_BACKEND_DIR),
                                              "workflow_video_first_last_api.json")
```

- [ ] **Step 2: Takımı koştur**

Run: `python -m pytest queen-editor -q`
Expected: `test_workflow_asset.py`'ın üç testinden **ikisi yeşile döner**
(`..._is_api_format_with_the_nodes_we_patch` ve `..._agree_on_how_long_a_render_runs`). Üçüncüsü —
model nöbeti — hâlâ kırmızı: `clip_vision_h.safetensors` grupta yok. Öbür on yedi kırmızı yerinde.

---

### Task 2: Portun sözleşmesi ve iki sessiz üretici

**Files:**
- Modify: `queen-editor/backend/features/photo_generation/domain/ports.py`
- Modify: `queen-editor/backend/features/photo_generation/data/comfy_photo_generator.py`
- Modify: `queen-editor/backend/features/photo_generation/data/mmaudio_generator.py`

**Interfaces:**
- Produces: `generate(prompt, negative, seed, model="", source=None, end=None) -> bytes` — üç
  üreticinin de imzası. Task 3 aynı imzayı taşıyor, `run_loop` 2. maddede bunu çağıracak.

- [ ] **Step 1: Portu genişlet**

`ports.py`:

```python
class PhotoGenerator(Protocol):
    def generate(self, prompt: str, negative: str, seed: int, model: str = "",
                 source: tuple | None = None, end: tuple | None = None) -> bytes:
```

ve docstring'e `source`'un paragrafından sonra:

```
        `end` is the picture the layer arrives at, same shape. Only a video has one; a photo and a
        sound take the argument and ignore it, for the same reason `source` is taken by all three.
```

- [ ] **Step 2: Foto üreticisi argümanı alsın**

`comfy_photo_generator.py`:

```python
    def generate(self, prompt, negative, seed, model="", source=None, end=None):
        """`source` and `end` are nobody's business here: a picture is made from its words alone and
        arrives nowhere. Both are taken because the queue has one call shape for every producer --
        see ports.PhotoGenerator.
        """
```

- [ ] **Step 3: Ses üreticisi argümanı alsın**

`mmaudio_generator.py`:

```python
    def generate(self, prompt, negative, seed, model="", source=None, end=None):
        """`source` is the frame's video as (name, bytes); the answer is its sound as bytes.

        `end` is a video's business alone -- a sound is laid over the whole of one and arrives
        nowhere. Taken and ignored, because the queue has one call shape for every producer.
```

(docstring'in kalanı olduğu gibi kalır.)

- [ ] **Step 4: Takımı koştur**

Run: `python -m pytest queen-editor -q`
Expected: `test_producer_contract.py`'daki
`test_a_producer_with_no_end_frame_takes_the_argument_anyway` **yeşile döner**. Aynı dosyanın öbür
iki testi hâlâ kırmızı: `producers_over` video üreticisini dört argümanla kuruyor.

---

### Task 3: İki grafiği bilen üretici

**Files:**
- Modify: `queen-editor/backend/features/photo_generation/data/comfy_video_generator.py`

**Interfaces:**
- Consumes: Task 2'nin imzası.
- Produces: `ComfyVideoGenerator(client, workflow_path, first_last_path, timeout)`; modül sabitleri
  `STANDARD_NODES`, `FIRST_LAST_START_NODE`, `FIRST_LAST_END_NODE`, `FIRST_LAST_PROMPT_NODE`,
  `FIRST_LAST_SEED_NODE`, `FIRST_LAST_NODES`. Task 6 kurucuyu bu sırayla çağırıyor.

- [ ] **Step 1: Modül docstring'ini iki grafiğe göre yaz**

Baştaki docstring, ikinci grafiğin node künyesini ve neden iki grafik olduğunu taşır:

```python
"""The video producer over ComfyUI -- the only place that knows what the video graphs look like.

Two graphs, because a video that ends on a picture is a different pipeline rather than the same one
with a node swapped: the FIRST2LASTFRAME hat carries its own checkpoints, its own CLIP vision and
its own sampling. Moving standard production onto it would change how every video already made
would look, so both ship and the job decides which one runs.

Node ids come from our own exports. workflow_video_api.json (WAN 2.2 I2V, inherited knowledge from
collab-toolbox's photo_to_video notebook):
  "287"     LoadImage        -> the frame's photo
  "233:240" PromptGenerator  -> the video prompt (and its own seed)
  "210"     Seed (rgthree)   -> the sampler's noise seed
  "178"     PrimitiveFloat   -> how many seconds one render runs

workflow_video_first_last_api.json (the arbuzai workflow's FIRST2LASTFRAME group):
  "338"     LoadImage        -> the frame the video starts on
  "342"     LoadImage        -> the frame it ends on
  "333:291" PromptGenerator  -> the video prompt (and its own seed)
  "327"     Seed (rgthree)   -> the sampler's noise seed

A new export can renumber these; then this file changes and nothing else does. The duration is read
rather than patched: the graph is where it is set (design v3, madde 28), and this file is the only
one that knows where in the graph that is -- so anybody who needs the number asks instead of
keeping a copy. It is read from the standard graph alone, because one number is quoted for every
video whatever graph made it; that the two graphs agree is held by test_workflow_asset.
"""
import json
import os
```

- [ ] **Step 2: Node kümelerini tanımla**

Var olan dört sabitin altına:

```python
STANDARD_NODES = (IMAGE_NODE, PROMPT_NODE, SEED_NODE, DURATION_NODE)

FIRST_LAST_START_NODE = "338"
FIRST_LAST_END_NODE = "342"
FIRST_LAST_PROMPT_NODE = "333:291"
FIRST_LAST_SEED_NODE = "327"
FIRST_LAST_NODES = (FIRST_LAST_START_NODE, FIRST_LAST_END_NODE, FIRST_LAST_PROMPT_NODE,
                    FIRST_LAST_SEED_NODE)
```

`FIRST_LAST_NODES` süre node'unu saymıyor: süre yalnız standart grafikten okunuyor, bu grafikten
istenen bir şey değil.

- [ ] **Step 3: Kurucuya ikinci yolu ver**

```python
    def __init__(self, client, workflow_path, first_last_path, timeout):
        self._client = client
        self._workflow_path = workflow_path
        self._first_last_path = first_last_path
        self._timeout = timeout
```

- [ ] **Step 4: generate'i yaz**

```python
    def generate(self, prompt, negative, seed, model="", source=None, end=None):
        """`source` is the frame's photo as (name, bytes) -- an I2V render hangs on a picture.

        `end` is the picture the video arrives at, same shape, and giving one is the whole of the
        decision made here: with an ending frame the render runs on the first-last graph, without
        one it runs exactly as it always has. Which frame that picture belongs to -- the frame's own
        for a loop, the next one's for a linked video -- is the queue's answer, so the word "mode"
        never reaches this layer.

        `negative` and `model` belong to the port rather than to these graphs: both are baked into
        the exports, and a video job carries neither.
        """
        if not source:
            # The ending frame is where the video arrives, not what it is built on.
            raise RuntimeError("Video için kaynak foto verilmedi")
        if end:
            workflow = self._load(self._first_last_path, FIRST_LAST_NODES)
            image_node, prompt_node, seed_node = (FIRST_LAST_START_NODE, FIRST_LAST_PROMPT_NODE,
                                                  FIRST_LAST_SEED_NODE)
        else:
            workflow = self._load(self._workflow_path, STANDARD_NODES)
            image_node, prompt_node, seed_node = IMAGE_NODE, PROMPT_NODE, SEED_NODE

        workflow[image_node]["inputs"]["image"] = self._client.upload_image(*source)
        if end:
            # Uploaded after the first one and never before it: an ending frame is a picture the
            # server has to hold, exactly like the photo the video hangs on.
            workflow[FIRST_LAST_END_NODE]["inputs"]["image"] = self._client.upload_image(*end)
        workflow[prompt_node]["inputs"]["prompt"] = prompt
        if seed is not None:
            # Both seeds: the sampler's noise and PromptGenerator's own, so the same seed
            # reproduces the video even when the prompt carries wildcard syntax. A job with no seed
            # leaves the graph's own value where it is.
            workflow[seed_node]["inputs"]["seed"] = seed
            workflow[prompt_node]["inputs"]["seed"] = seed

        prompt_id = self._client.submit(workflow)
        history = self._client.wait(prompt_id, self._timeout)
        return self._client.fetch_output(history, VIDEO_EXTENSIONS)
```

Kaynak denetimi grafik seçiminin **önünde**: bitiş karesi verilip kaynak verilmediğinde çıkan
cümle bugünküyle aynı kalıyor.

- [ ] **Step 5: seconds ve _load'u yaz**

```python
    def seconds(self):
        """How long one render runs, as the graph has it. Float on purpose: the field is one, and
        rounding it here would be a second version of the truth as surely as a copy would be."""
        return float(self._load(self._workflow_path, STANDARD_NODES)[DURATION_NODE]["inputs"][
            "value"])

    def _load(self, path, required):
        """Fresh copy per render -- patching is never written back to the shipped file."""
        try:
            with open(path, encoding="utf-8") as f:
                workflow = json.load(f)
        except FileNotFoundError:
            raise RuntimeError(
                f"Video grafiği yok: {path} — ComfyUI'de "
                "'Workflow → Export (API)' ile kaydet ve repoya commit'le") from None
        # The file's own name, not a written one: two graphs share this loader and a hardcoded name
        # would send whoever reads the error to the wrong file.
        name = os.path.basename(path)
        if "nodes" in workflow:
            raise RuntimeError(f"{name} UI formatında — ComfyUI'de "
                               "'Workflow → Export (API)' ile kaydet")
        for node_id in required:
            if node_id not in workflow:
                raise RuntimeError(f"{name} grafiğinde {node_id} node yok — graf değişmiş, "
                                   "node id'lerini güncelle")
        return workflow
```

- [ ] **Step 6: Takımı koştur**

Run: `python -m pytest queen-editor -q`
Expected: `test_comfy_video_generator.py`'ın on beşi de yeşil, `test_producer_contract.py`'ın üçü
de yeşil. Tek kırmızı kaldı: `test_every_model_the_first_last_graph_loads_is_in_the_video_group`.

---

### Task 4: Grubun listesi

**Files:**
- Modify: `queen-editor/backend/features/producers/domain/model_groups.py`

**Interfaces:**
- Produces: `GROUPS["video"]` içinde `{"folder": "clip_vision", "name": "clip_vision_h.safetensors"}`
  — Task 5 defterde aynı adı indiriyor, ve `test_notebook_installs_the_producer_groups.py` ikisini
  karşılaştırıyor.

- [ ] **Step 1: Satırı ekle**

`GROUPS["video"]` listesinin sonuna:

```python
        # Only the first-last graph reads this one, and only through its CLIPVisionLoader. It is in
        # the video group all the same: one producer, and a producer is installed or it is not.
        {"folder": "clip_vision", "name": "clip_vision_h.safetensors"},
```

- [ ] **Step 2: Takımı koştur**

Run: `python -m pytest queen-editor -q`
Expected: model nöbeti yeşile döner, **ama yeni bir kırmızı doğar**:
`test_notebook_installs_the_producer_groups.py` — grup artık defterin indirmediği bir dosya
sayıyor. Task 5 onu kapatıyor. Bu sıra bilerek: listeyi defterden önce büyütmek, "grup ne diyorsa
defter onu indirir" kuralını testin ağzından duyurmanın yolu.

---

### Task 5: Defterin indirdiği liste

**Files:**
- Modify: `queen-editor/app.ipynb`

**Interfaces:**
- Consumes: Task 4'ün grup satırı ve Task 1'in dosya adı.
- Produces: yok (defter kimsenin import ettiği bir şey değil).

- [ ] **Step 1: Hedef klasörü tanımla — hücre `f0df85b4`**

`TENC` satırının altına:

```python
CLIPV = f"{COMFY}/models/clip_vision"       # only the first-last video graph loads from here
```

ve `makedirs` döngüsünün listesine `CLIPV`, `TENC` ile `MMAU` arasına:

```python
for d in [CKPT, LORA, UPSC, BBOX, SAMS, DIFF, VAE, TENC, CLIPV, MMAU]:
```

- [ ] **Step 2: İndirme satırını ekle — aynı hücre**

`OPEN_VIDEO` listesinin sonuna:

```python
    # Read by the first-last graph alone, through its CLIPVisionLoader. Still part of the video
    # group: one producer, and a producer is installed or it is not.
    (f"{WAN21}/clip_vision/clip_vision_h.safetensors",
     CLIPV, "clip_vision_h.safetensors", "CLIP Vision H", None),
```

`WAN21` deposundan: dosya Wan 2.1'in paketinde duruyor, 2.2'ninkinde değil.

- [ ] **Step 3: Özet listesine klasörü ekle — aynı hücre**

`INSTALL_VIDEO` dalındaki `folders` satırına:

```python
    folders += [("diffusion_models", DIFF, "*.safetensors"), ("vae", VAE, "*.safetensors"),
                ("text_encoders", TENC, "*.safetensors"), ("clip_vision", CLIPV, "*.safetensors")]
```

- [ ] **Step 4: Disk tahminini büyüt — aynı hücre**

```python
SIZES = [(INSTALL_PHOTO, 8, "fotoğraf"), (INSTALL_VIDEO, 39, "video"), (INSTALL_AUDIO, 9, "ses")]
```

ve aynı hücredeki hata cümlesinin sonundaki `(video tek başına ~37 GiB)` → `~39 GiB`.

Sebebi: disk ölçümü bu sayıdan besleniyor. Eski sayı yeni dosyayı saymıyor, ve az tahmin diski
doldurup yarım dosya bırakıyor.

- [ ] **Step 5: Üç grafiğin denetimi — hücre `95ed9468`**

İki grafiği sayan denetim üçe çıkar:

```python
# All three graphs ship with the repo (our own copies) -- a forgotten commit shows up here rather
# than at the first render. Two of them are video: the standard one, and the one for a video that
# ends on a chosen picture. Sound has no graph: it runs in the app's own process.
for _name in ("workflow_api.json", "workflow_video_api.json",
              "workflow_video_first_last_api.json"):
    _path = os.path.join(CLONE_DIR, "queen-editor", _name)
    assert os.path.exists(_path), f"❌ Grafik yok: {_path} — {_name} commit'lenmiş mi?"
print("✓ Klon tamam (derlenmiş arayüz + üç grafik mevcut)")
```

- [ ] **Step 6: Okunan sayıları düzelt — üç yer daha**

Kullanıcının gözüyle gördüğü her `~37 GiB` `~39 GiB` olur:

- hücre `34c9ff58` (markdown): `Fotoğraf ~8 GiB · video ~39 GiB · ses ~9 GiB`
- hücre `8215086b` (CONFIG yorumu): `fotoğraf ~8 GiB · video ~39 GiB (T4'ün diski çoğu zaman
  yetmez, A100 iste) · ses ~9 GiB`, ve aynı hücredeki `xai_probe` docstring'inde `~39 GiB of video
  models`
- hücre `4d387058` (markdown başlık): `## Modeller — seçilen üreticiler, önce gated probe (~8 / ~39
  / ~9 GiB)`

- [ ] **Step 7: Takımı koştur**

Run: `python -m pytest queen-editor -q`
Expected: `test_notebook_installs_the_producer_groups.py` yeşile döner. Bu noktada
`backend/main.py` hâlâ eski kurucuyu çağırıyor ama onu hiçbir test tutmuyor — Task 6 onun için var.

---

### Task 6: Bileşim kökü

**Files:**
- Modify: `queen-editor/backend/main.py`

**Interfaces:**
- Consumes: Task 1'in sabiti ve Task 3'ün kurucusu.

- [ ] **Step 1: İkinci yolu geç**

```python
_video_generator = ComfyVideoGenerator(_comfy_client, config.VIDEO_WORKFLOW_PATH,
                                       config.VIDEO_FIRST_LAST_WORKFLOW_PATH,
                                       config.VIDEO_TIMEOUT)
```

Bunu bir test tutmuyor ve tutamaz: bileşim kökü gerçek ComfyUI'ye ve gerçek Drive'a bağlanıyor.
Atlanırsa takım yeşil kalır ve uygulama Colab'da ilk video işinde `TypeError` ile düşer — bu
adımın kendi başına bir madde olmasının sebebi bu.

- [ ] **Step 2: Dört komutu koştur**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Expected: dördü de yeşil, hiçbiri `skip`/`xfail` taşımıyor.

---

### Task 7: Yeşil commit

- [ ] **Step 1: Commit**

```bash
git add queen-editor docs/superpowers
git commit -F - <<'EOF'
feat(queen-editor): the engine can be given an ending frame

The video producer holds two graphs and picks by what it was handed: an ending picture
means the first-last graph, no ending picture means the graph that has always run. It
is never told a mode -- loop and linked differ only in which photo arrives -- so the
word stays in the domain where the choice is actually made.

_load takes the path and the nodes it wants, so both graphs share one loader and the
error names the file it actually read.

The first-last graph reads a CLIP vision model the I2V hat has no node for, so it joins
the video group and the notebook downloads it - one producer, and a producer is
installed or it is not. The video estimate moves 37 to 39 GiB with it, since the disk
check is fed from that number.

Four suites green.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** spec'in saydığı sekiz dosyanın sekizi de bir task'ta. `config.py` → Task 1;
`ports.py` + iki sessiz üretici → Task 2; `comfy_video_generator.py` → Task 3; `model_groups.py` →
Task 4; `app.ipynb` → Task 5; `main.py` → Task 6.

**Tip tutarlılığı:** `generate(prompt, negative, seed, model="", source=None, end=None)` dört yerde
de aynı: portta, üç üreticide. Kurucu `(client, workflow_path, first_last_path, timeout)` iki yerde
aynı: Task 3'te tanımlı, Task 6'da çağrılıyor — ve test döngüsündeki `generator` yardımcısıyla da
aynı sırada.

**Sıra neden böyle:** Task 4 (grup) Task 5'ten (defter) önce, çünkü grubu büyütmek defteri tutan
testi kırmızıya çeviriyor ve o kırmızı kuralın kendisini söylüyor. Tersi sırada defter, hiçbir
testin istemediği bir dosyayı indirir hâle gelirdi ve neden indirdiğini kimse soramazdı.

**Kontrol edilen tuzak:** `FIRST_LAST_NODES` süre node'unu içermiyor. İçerseydi
`test_a_first_last_graph_whose_nodes_moved_names_the_missing_one` yine geçerdi, ama üretici
grafikten hiç okumadığı bir node'u şart koşuyor olurdu — ve yeni bir export süreyi başka yere
taşıdığında bitiş kareli üretim, hiç kullanmadığı bir sayı yüzünden düşerdi.

**Kontrol edilen tuzak 2:** `if not source` kontrolü grafik seçiminin önünde duruyor. Sonra
gelseydi, bitiş karesi verilip kaynak verilmeyen çağrı önce ikinci grafiği açar ve dosya yoksa
"grafik yok" derdi — `test_an_end_frame_does_not_stand_in_for_the_photo`'nun beklediği "foto"
cümlesi yerine.

**Kontrol edilen tuzak 3:** Task 6'yı hiçbir test tutmuyor. Planda kendi task'ı olması ve bu
notun yazılması, atlanmasının tek engeli.
