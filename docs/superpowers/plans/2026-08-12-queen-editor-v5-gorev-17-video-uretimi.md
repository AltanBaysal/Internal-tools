# Queen Editor v5 · Görev 17 — Motor videoyu üretir · Uygulama planı

> **Uygulayıcıya:** her adım önce kırmızı test, sonra en küçük kod. Tasarım:
> [Görev 17 spec](../specs/2026-08-12-queen-editor-v5-gorev-17-video-uretimi-design.md).

**Hedef:** sırası gelen video işi ComfyUI'nin video grafiğiyle üretilsin, çıkan mp4 karenin video
katmanı olarak `P0_0_V1_0.mp4` adıyla yazılsın.

**Mimari:** taşımaya iki yetenek eklenir (görsel yükleme, uzantıyla çıktı seçme); grafik bilgisi
yeni bir data sınıfında (`ComfyVideoGenerator`); motor katmanın adını `layer_file` ile sorar ve
video işine karenin foto baytlarını verir.

**Yığın:** Python (pytest).

## Genel kısıtlar

- Kod, yorum, test adı ve commit **İngilizce**; kullanıcıya görünen metin **Türkçe**.
- Hata mesajı sunucunun/dosyanın kendi cevabını basar, sebep uydurmaz.
- Katman kuralı: `presentation → domain ← data → services`.
- Test komutları (birebir):
  - `python -m pytest queen-editor -q`
  - `npm test --prefix queen-editor/frontend -- --run`

---

## Görev 1 — Taşıma: görsel yükleme ve uzantıyla çıktı

**Dosyalar:**
- Değişecek: `queen-editor/backend/services/comfy/client.py`
- Test: `queen-editor/backend/tests/test_comfy_client.py`

**Arayüz:**
- Üretir: `ComfyClient.upload_image(name, data) -> str` ·
  `ComfyClient.fetch_output(history_entry, extensions=None) -> bytes`

- [ ] **Adım 1 — kırmızı testler:** önce `FakeHttp.post`'u yükleme çağrısını da alacak hâle getir:

```python
    def post(self, url, json=None, timeout=None, files=None, data=None):
        self.posted = (url, json)
        self.post_calls.append({"url": url, "json": json, "files": files, "data": data})
        return self._post
```

(`__init__`'e `self.post_calls = []` ekle; `self.posted` duruyor, eski testler onu okuyor.)

```python
def test_upload_image_sends_the_file_and_returns_the_servers_name():
    http = FakeHttp(post=FakeResponse({"name": "P0_0.png"}))

    assert client_with(http).upload_image("P0_0.png", b"PNGDATA") == "P0_0.png"
    call = http.post_calls[0]
    assert call["url"] == "http://comfy:8188/upload/image"
    assert call["files"] == {"image": ("P0_0.png", b"PNGDATA")}
    # Overwrite: the same frame uploaded twice must not become P0_0 (1).png, or LoadImage would
    # point at the first upload for good.
    assert call["data"] == {"overwrite": "true"}


def test_upload_image_raises_with_the_servers_own_body():
    http = FakeHttp(post=FakeResponse(status_code=413))

    with pytest.raises(RuntimeError) as blew_up:
        client_with(http).upload_image("P0_0.png", b"PNGDATA")

    assert "413" in str(blew_up.value) and "raw body" in str(blew_up.value)


def test_fetch_output_finds_a_video_among_the_graphs_outputs():
    # A video graph publishes under "gifs" and may carry a preview image node as well.
    entry = {"outputs": {"55": {"images": [{"filename": "a.png", "type": "output"}]},
                         "81": {"gifs": [{"filename": "v.mp4", "subfolder": "", "type": "output"}]}}}
    http = FakeHttp(gets=[FakeResponse(content=b"MP4DATA")])

    assert client_with(http).fetch_output(entry, extensions=(".mp4",)) == b"MP4DATA"
    _url, params = http.get_calls[0]
    assert params["filename"] == "v.mp4"


def test_fetch_output_says_what_came_when_no_output_has_the_wanted_extension():
    entry = {"outputs": {"81": {"gifs": [{"filename": "v.webm", "type": "output"}]}}}

    with pytest.raises(RuntimeError) as blew_up:
        client_with(FakeHttp()).fetch_output(entry, extensions=(".mp4",))

    assert "v.webm" in str(blew_up.value)
```

- [ ] **Adım 2:** `python -m pytest queen-editor -q` → kırmızı.

- [ ] **Adım 3 — `client.py`:**

```python
    def upload_image(self, name, data):
        """Put an image in ComfyUI's input folder and return the name the server kept it under.

        The graph runs on the server's disk while the picture lives on Drive, so the bytes travel
        over HTTP. overwrite=true because the name is the frame's own: uploading the same frame
        again must replace it, not become "P0_0 (1).png" that LoadImage would never look at.
        """
        resp = self._http.post(f"{self.base}/upload/image",
                               files={"image": (name, data)},
                               data={"overwrite": "true"}, timeout=120)
        if resp.status_code >= 400:
            raise RuntimeError(f"POST /upload/image -> HTTP {resp.status_code}\n{resp.text}")
        return resp.json()["name"]
```

`fetch_output` uzantı süzgeciyle:

```python
    def fetch_output(self, history_entry, extensions=None):
        """Download THE produced file over /view and return its bytes.

        type=="output" drops temp previews (a preview node registers temp files). Exactly one real
        output is the contract: silently picking one of N would hide a graph whose batch size is
        not 1, so the raw outputs are printed and the render stops.

        `extensions` is how a caller says which medium it came for: a video graph publishes under
        "gifs" and may carry an image node as well, so the file is chosen by its own name rather
        than by which key it landed in. No extensions means the images the photo graph produces.
        """
        keys = ("gifs", "videos", "images") if extensions else ("images",)
        outputs = [item
                   for node_output in history_entry.get("outputs", {}).values()
                   for key in keys
                   for item in node_output.get(key, [])
                   if item.get("type", "output") == "output"
                   and (not extensions
                        or item.get("filename", "").lower().endswith(tuple(extensions)))]
        if len(outputs) != 1:
            raise RuntimeError(
                f"1 çıktı bekleniyordu, {len(outputs)} geldi — grafikte Batch Size 1 mi?\n"
                + json.dumps(history_entry.get("outputs", {}), indent=2, ensure_ascii=False))
        ...
```

> Var olan test "1 çıktı görseli bekleniyordu" metnini değil "Batch Size"ı arıyor; metni yukarıdaki
> gibi kısaltmak testi bozmaz.

- [ ] **Adım 4:** `python -m pytest queen-editor -q` → yeşil.

---

## Görev 2 — Depo: baytları okumak

**Dosyalar:**
- Değişecek: `queen-editor/backend/services/drive/storage.py`,
  `queen-editor/backend/features/photo_generation/data/photo_store.py`,
  `queen-editor/backend/features/photo_generation/domain/ports.py`
- Test: `queen-editor/backend/tests/test_photo_store.py`

- [ ] **Adım 1 — kırmızı test (`test_photo_store.py` sonuna):**

```python
def test_a_photos_bytes_can_be_read_back(tmp_path):
    store = DrivePhotoStore(DriveStorage(str(tmp_path)))
    store.save("düğün", "P0_0.png", b"PNGDATA")

    assert store.read("düğün", "P0_0.png") == b"PNGDATA"
```

> Dosyadaki mevcut testlerin `DrivePhotoStore`'u nasıl kurduğuna bak ve aynısını kullan.

- [ ] **Adım 2:** `python -m pytest queen-editor -q` → kırmızı.

- [ ] **Adım 3 — `storage.py`:**

```python
    def read_bytes(self, subdir, name):
        """Contents of root/subdir/name as bytes; None when it is not there."""
        path = os.path.join(self.root, subdir, name)
        if not os.path.isfile(path):
            return None
        with open(path, "rb") as f:
            return f.read()
```

`photo_store.py`:

```python
    def read(self, project, filename):
        """The photo's own bytes -- what a video producer hangs its render on."""
        return self._storage.read_bytes(project, filename)
```

`ports.py`'de `PhotoStore`'a:

```python
    def read(self, project: str, filename: str) -> bytes | None:
        """The file's bytes; None when it is not there."""
        ...
```

- [ ] **Adım 4:** `python -m pytest queen-editor -q` → yeşil.

---

## Görev 3 — Video üreticisi

**Dosyalar:**
- Yeni: `queen-editor/backend/features/photo_generation/data/comfy_video_generator.py`
- Test: `queen-editor/backend/tests/test_comfy_video_generator.py`

**Arayüz:**
- Üretir: `ComfyVideoGenerator(client, workflow_path, timeout).generate(prompt, negative, seed,
  model="", source=None) -> bytes`

- [ ] **Adım 1 — kırmızı testler:**

```python
import json

import pytest

from backend.features.photo_generation.data.comfy_video_generator import ComfyVideoGenerator

GRAPH = {
    "287": {"class_type": "LoadImage", "inputs": {"image": "example.png"}},
    "233:240": {"class_type": "PromptGenerator", "inputs": {"prompt": "", "seed": -1}},
    "210": {"class_type": "Seed", "inputs": {"seed": -1}},
}


class FakeClient:
    def __init__(self):
        self.uploaded = None
        self.submitted = None
        self.fetched = None

    def upload_image(self, name, data):
        self.uploaded = (name, data)
        return f"server-{name}"

    def submit(self, workflow):
        self.submitted = workflow
        return "p1"

    def wait(self, prompt_id, timeout):
        return {"outputs": "history"}

    def fetch_output(self, history_entry, extensions=None):
        self.fetched = (history_entry, extensions)
        return b"MP4DATA"


def graph_at(tmp_path, graph=None):
    path = tmp_path / "workflow_video_api.json"
    path.write_text(json.dumps(graph if graph is not None else GRAPH), encoding="utf-8")
    return str(path)


def generator(tmp_path, client, graph=None):
    return ComfyVideoGenerator(client, graph_at(tmp_path, graph), timeout=60)


def test_the_frames_photo_is_uploaded_and_the_graph_points_at_it(tmp_path):
    client = FakeClient()

    data = generator(tmp_path, client).generate("kadın dönüyor", "", 42,
                                                source=("P0_0.png", b"PNGDATA"))

    assert data == b"MP4DATA"
    assert client.uploaded == ("P0_0.png", b"PNGDATA")
    assert client.submitted["287"]["inputs"]["image"] == "server-P0_0.png"
    assert client.submitted["233:240"]["inputs"]["prompt"] == "kadın dönüyor"
    # Both seeds: the sampler's own and the prompt node's, so the same seed reproduces the video.
    assert client.submitted["210"]["inputs"]["seed"] == 42
    assert client.submitted["233:240"]["inputs"]["seed"] == 42
    # Only an mp4 counts as the render: a preview image node must not be mistaken for it.
    assert client.fetched == ({"outputs": "history"}, (".mp4",))


def test_a_video_without_a_photo_to_hang_on_says_so(tmp_path):
    with pytest.raises(RuntimeError) as blew_up:
        generator(tmp_path, FakeClient()).generate("prompt", "", 42)

    assert "foto" in str(blew_up.value).lower()


def test_a_missing_graph_names_the_file_it_wants(tmp_path):
    gen = ComfyVideoGenerator(FakeClient(), str(tmp_path / "yok.json"), timeout=60)

    with pytest.raises(RuntimeError) as blew_up:
        gen.generate("prompt", "", 42, source=("P0_0.png", b"PNG"))

    assert "yok.json" in str(blew_up.value)


def test_a_graph_exported_in_ui_format_says_which_export_to_use(tmp_path):
    gen = generator(tmp_path, FakeClient(), graph={"nodes": [], "links": []})

    with pytest.raises(RuntimeError) as blew_up:
        gen.generate("prompt", "", 42, source=("P0_0.png", b"PNG"))

    assert "Export (API)" in str(blew_up.value)


def test_a_graph_whose_nodes_moved_names_the_missing_one(tmp_path):
    gen = generator(tmp_path, FakeClient(), graph={k: v for k, v in GRAPH.items() if k != "210"})

    with pytest.raises(RuntimeError) as blew_up:
        gen.generate("prompt", "", 42, source=("P0_0.png", b"PNG"))

    assert "210" in str(blew_up.value)


def test_a_seed_the_job_never_carried_leaves_the_graphs_own(tmp_path):
    # A video job plans no seed (Görev 14): the graph's own randomisation stands.
    client = FakeClient()

    generator(tmp_path, client).generate("prompt", "", None, source=("P0_0.png", b"PNG"))

    assert client.submitted["210"]["inputs"]["seed"] == -1
```

- [ ] **Adım 2:** `python -m pytest queen-editor -q` → ImportError.

- [ ] **Adım 3 — `comfy_video_generator.py`:**

```python
"""PhotoGenerator over ComfyUI for VIDEO -- the only place that knows the video graph.

Node ids come from our own export (queen-editor/workflow_video_api.json); they are inherited
knowledge from collab-toolbox's photo_to_video notebook, which drives the same WAN 2.2 I2V graph:
  "287"     LoadImage        -> the frame's photo
  "233:240" PromptGenerator  -> the video prompt (and its own seed)
  "210"     Seed (rgthree)   -> the sampler's noise seed

A new export can renumber these; then this file changes and nothing else does. Duration is not
patched at all: how long a video is, is the graph's own setting (madde 28).
"""
import json

IMAGE_NODE = "287"
PROMPT_NODE = "233:240"
SEED_NODE = "210"

# What counts as the render. A video graph often carries a preview image node too, so the file is
# chosen by its own extension rather than by which output key it landed in.
VIDEO_EXTENSIONS = (".mp4",)


class ComfyVideoGenerator:
    def __init__(self, client, workflow_path, timeout):
        self._client = client
        self._workflow_path = workflow_path
        self._timeout = timeout

    def generate(self, prompt, negative, seed, model="", source=None):
        """`source` is the frame's photo as (name, bytes) -- an I2V render hangs on a picture.

        `negative` and `model` are the port's, not this graph's: the negative and the checkpoint
        are baked into the export, and a video job carries neither.
        """
        if not source:
            raise RuntimeError("Video için kaynak foto verilmedi")
        workflow = self._load()
        name, data = source
        workflow[IMAGE_NODE]["inputs"]["image"] = self._client.upload_image(name, data)
        workflow[PROMPT_NODE]["inputs"]["prompt"] = prompt
        if seed is not None:
            # Both seeds: the sampler's noise and PromptGenerator's own, so the same seed
            # reproduces the video even when the prompt carries wildcard syntax. A job with no seed
            # leaves the graph's own value alone.
            workflow[SEED_NODE]["inputs"]["seed"] = seed
            workflow[PROMPT_NODE]["inputs"]["seed"] = seed

        prompt_id = self._client.submit(workflow)
        history = self._client.wait(prompt_id, self._timeout)
        return self._client.fetch_output(history, extensions=VIDEO_EXTENSIONS)

    def _load(self):
        """Fresh copy per render -- patching is never written back to the shipped file."""
        try:
            with open(self._workflow_path, encoding="utf-8") as f:
                workflow = json.load(f)
        except FileNotFoundError:
            raise RuntimeError(
                f"Video grafiği yok: {self._workflow_path} — ComfyUI'de "
                "'Workflow → Export (API)' ile kaydet ve repoya commit'le") from None
        if "nodes" in workflow:
            raise RuntimeError("workflow_video_api.json UI formatında — ComfyUI'de "
                               "'Workflow → Export (API)' ile kaydet")
        for node_id in (IMAGE_NODE, PROMPT_NODE, SEED_NODE):
            if node_id not in workflow:
                raise RuntimeError(f"Video grafiğinde {node_id} node yok — graf değişmiş, "
                                   "node id'lerini güncelle")
        return workflow
```

- [ ] **Adım 4:** `python -m pytest queen-editor -q` → yeşil.

---

## Görev 4 — Katmanın adı ve motorun kaynağı

**Dosyalar:**
- Değişecek: `queen-editor/backend/features/photo_generation/domain/photo_name.py`,
  `queen-editor/backend/features/photo_generation/domain/run_loop.py`
- Test: `queen-editor/backend/tests/test_photo_name.py`,
  `queen-editor/backend/tests/test_photo_usecases.py`

**Arayüz:**
- Üretir: `photo_name.layer_file(kind, frame) -> str`

- [ ] **Adım 1 — kırmızı testler (`test_photo_name.py`):**

```python
def test_a_layers_file_is_named_by_what_it_is():
    assert layer_file("photo", "P11_3") == "P11_3.png"
    # The first (and only) video of a frame: round 1, variant 0 -- a second video is a new frame.
    assert layer_file("video", "P11_3") == "P11_3_V1_0.mp4"
```

ve (`test_photo_usecases.py`, Görev 16'nın video testlerinin yanına):

```python
def test_a_video_is_written_under_the_layers_own_name():
    store, record, plan_store = video_job_project(prompt="kırmızı elbiseli kadın")
    generator = FakeGenerator()

    resume_batch(sync_runner(), store, record, plan_store, {layers.VIDEO: generator},
                 lambda: "t", "düğün", writers={layers.VIDEO: FakeWriter()})

    assert [name for name, _data in store.saved] == ["0_a_V1_0.mp4"]
    video = [row for row in record.rows if row.get("layer") == "video"][0]
    assert video["file"] == "0_a_V1_0.mp4"


def test_the_video_producer_is_handed_the_frames_own_photo():
    store, record, plan_store = video_job_project(prompt="kırmızı elbiseli kadın")
    store.files["0_a.png"] = b"PNGDATA"
    generator = FakeGenerator()

    resume_batch(sync_runner(), store, record, plan_store, {layers.VIDEO: generator},
                 lambda: "t", "düğün", writers={layers.VIDEO: FakeWriter()})

    assert generator.sources == [("0_a.png", b"PNGDATA")]
```

`FakeStore`'a okuma yeteneği ekle (var olan `saved` listesi duruyor):

```python
class FakeStore:
    def __init__(self, projects=("düğün",), next_no=0):
        ...
        self.files = {}                   # what read() answers with, by name

    def save(self, project, filename, data):
        self.saved.append((filename, data))
        self.files[filename] = data
        return filename

    def read(self, project, filename):
        return self.files.get(filename)
```

`FakeGenerator.generate`'e kaynağı kaydettir:

```python
    def __init__(self, fail_on=(), installed=("nova.safetensors",)):
        ...
        self.sources = []

    def generate(self, prompt, negative, seed, model="", source=None):
        self.calls.append((prompt, negative, seed, model))
        self.sources.append(source)
        ...
```

> `FailsTwice` ve `StopsAfter` gibi öteki sahte üreticilere de `source=None` parametresi gerekiyor;
> testler kırmızıya dönünce hangileri olduğunu tam takım söyler.

- [ ] **Adım 2:** `python -m pytest queen-editor -q` → kırmızı.

- [ ] **Adım 3 — `photo_name.py`:**

```python
from backend.features.photo_generation.domain import layers
```

> Döngü kontrolü: `layers.py` hiçbir şey import etmiyor, bu yüzden bu import güvenli.

```python
# The first video of a frame. A frame has at most one, and a second one is a new frame (madde 25),
# so the pair is constant until "yeniden üret" starts new rounds (madde 98).
FIRST_ROUND, FIRST_VARIANT = 1, 0


def layer_file(kind, frame):
    """The file name one produced layer takes.

    Photo and video are named from the frame's own identity. Audio grows the VIDEO's name rather
    than the frame's, so it joins here when the audio producer does.
    """
    if kind == layers.VIDEO:
        return video_file(frame, FIRST_ROUND, FIRST_VARIANT)
    return photo_file(frame)
```

- [ ] **Adım 4 — `run_loop.py`:** `photo_file` yerine katmanın adı ve video işine kaynak.

Import: `from ...photo_name import layer_file, photo_file` (rapor satırları `photo_file`'ı
kullanmaya devam ediyor).

```python
            fid = current["id"]
            # The layer's own name: what gets saved, and what a failure's line points at. The
            # gallery still marks its tiles by the frame's photo name (see the report below) --
            # that is the screen's identifier, not the layer's.
            name = layer_file(kind, fid)
```

`producer.generate` çağrısına kaynak:

```python
                data = producer.generate(prompt, current["negative"], current["seed"],
                                         current["model"],
                                         source=_source_for(kind, store, slots, project, fid))
```

Yardımcı, `_prompts_of`'un yanına:

```python
def _source_for(kind, store, slots, project, fid):
    """The picture a layer is made from, as (name, bytes) -- None for a layer that needs none.

    A video hangs on the frame's photo; a photo is made from its prompt alone. Read at the job's
    turn rather than kept in memory: the file is on Drive and the run may have started hours ago.
    `slots` is the turn's own snapshot, so nothing is asked of the record twice.
    """
    if kind == layers.PHOTO:
        return None
    photo = slots.get(fid, {}).get(layers.PHOTO)
    if not photo:
        return None
    return (photo["file"], store.read(project, photo["file"]))
```

> `layers`'ı run_loop'a import et (`from ... domain import layers, policy, queue`).

- [ ] **Adım 5:** `python -m pytest queen-editor -q` → yeşil.

---

## Görev 5 — Bağlama: config ve main

**Dosyalar:**
- Değişecek: `queen-editor/backend/config.py`, `queen-editor/backend/main.py`

- [ ] **Adım 1 — `config.py`:**

```python
# The video graph ships in the repo the way the photo one does -- our own export, never
# collab-toolbox's file.
VIDEO_WORKFLOW_PATH = os.path.join(os.path.dirname(_BACKEND_DIR), "workflow_video_api.json")
VIDEO_TIMEOUT = 30 * 60    # seconds for one video; an A100 makes 5s in minutes, so this is a stall guard
```

- [ ] **Adım 2 — `main.py`:**

```python
from backend.features.photo_generation.data.comfy_video_generator import ComfyVideoGenerator
```

```python
_video_generator = ComfyVideoGenerator(_comfy_client, config.VIDEO_WORKFLOW_PATH,
                                       config.VIDEO_TIMEOUT)
_producers = {layers.PHOTO: _photo_generator, layers.VIDEO: _video_generator}
```

> Yorumu güncelle: artık "video ve ses üreticileri gelince" değil, "ses üreticisi gelince".

- [ ] **Adım 3:** `python -m pytest queen-editor -q` → yeşil.

---

## Görev 6 — Tam takım ve commit

- [ ] **Adım 1:** `python -m pytest queen-editor -q`
- [ ] **Adım 2:** `npm test --prefix queen-editor/frontend -- --run`
- [ ] **Adım 3:** commit:

```
feat(queen-editor): the engine makes the video a frame is waiting for
```

- [ ] **Adım 4:** kullanıcıya söyle: `queen-editor/workflow_video_api.json` repoda yok; ComfyUI'de
WAN 2.2 I2V grafiğini **Export (API)** ile kaydedip commit'lemeden gerçek video üretilemez.
