# v14 Görev 1 — Motorun bitiş karesi alabilmesi: TEST döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Video üreticisinin bitiş karesi alabilmesini, iki grafikten doğru olanı seçmesini, her iki
kareyi de sunucuya yüklemesini ve yeni grafiğin depodaki hâlinin doğrulanmasını sınayan testleri
yazmak; takımı kırmızı commit'lemek.

**Architecture:** Üç var olan test dosyası genişliyor, yeni dosya yok. `test_workflow_asset.py`
depodaki JSON'a bakan nöbet — yeni grafiğin API formatında olduğunu, yamaladığımız node'ların yerinde
durduğunu ve yüklediği her modelin üreticiler listesinde adının geçtiğini sorar.
`test_comfy_video_generator.py` üreticinin kendi davranışı — sahte bir ComfyUI ve `tmp_path`'e
yazılmış iki sahte grafikle. `test_producer_contract.py` üç gerçek üreticinin kuyrukla tek çağrı
biçiminde konuştuğunu tutar.

**Tech Stack:** Python 3, pytest.

**Spec:** [test turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-1-bitis-karesi-testler-design.md)

## Global Constraints

- **Bu döngüde kod yazılmıyor.** `backend/` altındaki hiçbir kaynak dosyası değişmiyor — ne
  `config.py`, ne `comfy_video_generator.py`, ne `model_groups.py`. Yalnız `backend/tests/` altındaki
  üç dosya ve bu iki belge.
- Test adları, docstring'leri ve yorumları **İngilizce**; kullanıcıya görünen metin yok. Hata
  mesajlarındaki Türkçe parçalar (`"foto"`, `"Export (API)"`) üretilen metin değil, **var olan**
  hata metninin sınandığı parçalar.
- Commit mesajında **çift tırnak yok**, ve **amend yok**.
- Komut: `python -m pytest queen-editor -q` (dört satırın hepsi koşulur, hiçbiri boru ile
  kısaltılmaz).
- `dist/` **derlenmiyor** — ön yüz davranışı değişmedi.
- Commit **kırmızı gider**. `skip`/`xfail` yok.
- `queen-editor/workflow_video_first_last_api.json` zaten depoda (`e30e945`) — bu döngü onu
  yaratmıyor, yalnız ona bakıyor.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `backend/tests/test_workflow_asset.py` | depodaki grafiklerin nöbeti | 3 test eklenir |
| `backend/tests/test_comfy_video_generator.py` | üreticinin iki grafikle davranışı | sahte grafik + yardımcılar genişler, 6 test eklenir, 3 test güncellenir |
| `backend/tests/test_producer_contract.py` | üç gerçek üreticinin tek çağrı biçimi | 1 test eklenir, kurucu çağrısı genişler |

---

### Task 1: Yeni grafiğin nöbeti

**Files:**
- Modify: `queen-editor/backend/tests/test_workflow_asset.py`

**Interfaces:**
- Consumes: `config.VIDEO_FIRST_LAST_WORKFLOW_PATH` — **henüz yok**, implementasyon döngüsünde
  doğacak. Bu döngüde kırmızılığın kaynağı tam olarak bu.
- Produces: yok (test dosyası).

- [ ] **Step 1: İki grafik testini yaz**

`queen-editor/backend/tests/test_workflow_asset.py`, `test_video_workflow_is_api_format_with_the_nodes_we_patch`'in **hemen altına**:

```python
def test_the_first_last_video_workflow_is_api_format_with_the_nodes_we_patch():
    """The second video graph: the arbuzai workflow's FIRST2LASTFRAME group, exported as our own
    file. It carries two LoadImage nodes rather than one, and which of them is the ending frame is
    decided by the graph's wiring -- so both ids are asserted, and so is the node that reads them."""
    with open(config.VIDEO_FIRST_LAST_WORKFLOW_PATH, encoding="utf-8") as f:
        workflow = json.load(f)
    assert "nodes" not in workflow, "UI formatında export — 'Workflow → Export (API)' gerekiyor"
    assert workflow["338"]["class_type"] == "LoadImage"
    assert "image" in workflow["338"]["inputs"]
    assert workflow["342"]["class_type"] == "LoadImage"
    assert "image" in workflow["342"]["inputs"]
    # The two pictures are only an ending frame because this node reads them as one.
    assert workflow["343"]["class_type"] == "WanFirstLastFrameToVideo"
    assert workflow["343"]["inputs"]["start_image"][0] == "338"
    assert workflow["343"]["inputs"]["end_image"][0] == "342"
    assert workflow["333:291"]["class_type"] == "PromptGenerator"
    assert {"prompt", "seed"} <= set(workflow["333:291"]["inputs"])
    assert workflow["327"]["class_type"] == "Seed (rgthree)"
    assert "seed" in workflow["327"]["inputs"]


def test_both_video_graphs_agree_on_how_long_a_render_runs():
    """How long a video runs is read from one graph and quoted for every video, export estimate
    included. Two graphs disagreeing would make that number a lie for half the gallery."""
    with open(config.VIDEO_WORKFLOW_PATH, encoding="utf-8") as f:
        standard = json.load(f)
    with open(config.VIDEO_FIRST_LAST_WORKFLOW_PATH, encoding="utf-8") as f:
        first_last = json.load(f)

    assert standard["178"]["inputs"]["value"] == first_last["335"]["inputs"]["value"]
```

- [ ] **Step 2: Model nöbetini yaz**

Aynı dosyanın **sonuna**, `test_every_model_the_video_graph_loads_is_in_the_video_group`'un altına:

```python
def test_every_model_the_first_last_graph_loads_is_in_the_video_group():
    """The same guard for the second graph, and the reason it needs its own: FIRST2LASTFRAME reads a
    CLIP vision model that the I2V hat has no node for, so scanning only the first graph would leave
    the panel calling the video producer ready over a render that cannot start."""
    with open(config.VIDEO_FIRST_LAST_WORKFLOW_PATH, encoding="utf-8") as f:
        workflow = json.load(f)
    listed = {row["name"] for row in GROUPS["video"]}
    missing = sorted(_model_files(workflow) - listed)
    assert not missing, f"Graf bu dosyaları yüklüyor ama grup saymıyor: {missing}"
```

- [ ] **Step 3: Takımı koştur**

Run: `python -m pytest queen-editor -q`
Expected: 3 yeni test düşüyor, üçü de aynı sebeple:
`AttributeError: module 'backend.config' has no attribute 'VIDEO_FIRST_LAST_WORKFLOW_PATH'`.
Kalan her şey yeşil.

---

### Task 2: Üreticinin iki grafiği

**Files:**
- Modify: `queen-editor/backend/tests/test_comfy_video_generator.py`

**Interfaces:**
- Consumes: `ComfyVideoGenerator(client, workflow_path, first_last_path, timeout)` — **bugün üç
  argüman alıyor**, dördüncüsü implementasyon döngüsünde doğacak. `generate(...)` bir `end`
  argümanı alacak.
- Produces: `graphs_at(tmp_path, graph=None, first_last=None)` → `(standard_path, ends_path)`;
  `generator(tmp_path, client, graph=None, first_last=None, first_last_path=None)`. Task 3 bunları
  kullanmıyor, ama implementasyon döngüsü aynı isimlere dayanıyor.

- [ ] **Step 1: İkinci sahte grafiği tanımla**

`GRAPH` sözlüğünün hemen altına:

```python
# The second graph -- the arbuzai workflow's FIRST2LASTFRAME hat. Its duration deliberately differs
# from the standard graph's here, so a test can prove which of the two the length is read from.
FIRST_LAST_GRAPH = {
    "338": {"class_type": "LoadImage", "inputs": {"image": "example.png"}},
    "342": {"class_type": "LoadImage", "inputs": {"image": "example.png"}},
    "343": {"class_type": "WanFirstLastFrameToVideo",
            "inputs": {"start_image": ["338", 0], "end_image": ["342", 0]}},
    "333:291": {"class_type": "PromptGenerator", "inputs": {"prompt": "", "seed": -1}},
    "327": {"class_type": "Seed", "inputs": {"seed": -1}},
    "335": {"class_type": "PrimitiveFloat", "inputs": {"value": 9}},
}
```

- [ ] **Step 2: Sahte istemciyi iki yüklemeyi sayacak hâle getir**

`FakeClient` içinde `self.uploaded = None` → `self.uploads = []`, ve:

```python
    def upload_image(self, name, data):
        self.uploads.append((name, data))
        return f"server-{name}"
```

Sebep: bitiş karesi ikinci bir yükleme; tek alanlı bir sahte, ikincisinin birincinin üstüne
yazmasını gizlerdi.

- [ ] **Step 3: Yardımcıları iki grafiğe aç**

`graph_at` ve `generator` yerine:

```python
def graphs_at(tmp_path, graph=None, first_last=None):
    standard = tmp_path / "workflow_video_api.json"
    standard.write_text(json.dumps(graph if graph is not None else GRAPH), encoding="utf-8")
    ends = tmp_path / "workflow_video_first_last_api.json"
    ends.write_text(json.dumps(first_last if first_last is not None else FIRST_LAST_GRAPH),
                    encoding="utf-8")
    return str(standard), str(ends)


def generator(tmp_path, client, graph=None, first_last=None, first_last_path=None):
    standard, ends = graphs_at(tmp_path, graph, first_last)
    return ComfyVideoGenerator(client, standard, first_last_path or ends, timeout=60)
```

- [ ] **Step 4: Var olan üç testi yeni şekle getir**

`test_the_frames_photo_is_uploaded_and_the_graph_points_at_it` adını
`test_a_video_with_no_end_frame_is_rendered_by_the_standard_graph` yap, `client.uploaded == (...)`
yerine `client.uploads == [...]` koy ve iki satır ekle:

```python
def test_a_video_with_no_end_frame_is_rendered_by_the_standard_graph(tmp_path):
    client = FakeClient()

    data = generator(tmp_path, client).generate("kadın dönüyor", "", 42,
                                                source=("P0_0.png", b"PNGDATA"))

    assert data == b"MP4DATA"
    assert client.uploads == [("P0_0.png", b"PNGDATA")]
    assert client.submitted["287"]["inputs"]["image"] == "server-P0_0.png"
    assert client.submitted["233:240"]["inputs"]["prompt"] == "kadın dönüyor"
    # Both seeds: the sampler's noise and the prompt node's own, so one seed reproduces the video.
    assert client.submitted["210"]["inputs"]["seed"] == 42
    assert client.submitted["233:240"]["inputs"]["seed"] == 42
    # The graph that ends on a picture is not even opened.
    assert "343" not in client.submitted
    # Only an mp4 counts as the render: a preview image node must not be mistaken for it.
    assert client.fetched == ({"outputs": "history"}, (".mp4",))
```

`test_a_missing_graph_names_the_file_it_wants` kurucuyu elden çağırıyor, ikinci yolu alsın:

```python
def test_a_missing_graph_names_the_file_it_wants(tmp_path):
    _standard, ends = graphs_at(tmp_path)
    gen = ComfyVideoGenerator(FakeClient(), str(tmp_path / "yok.json"), ends, timeout=60)

    with pytest.raises(RuntimeError) as blew_up:
        gen.generate("prompt", "", 42, source=("P0_0.png", b"PNG"))

    assert "yok.json" in str(blew_up.value)
```

- [ ] **Step 5: Süre testini yaz**

`test_a_fractional_length_is_not_rounded_away`'in altına:

```python
def test_the_length_is_still_read_from_the_standard_graph(tmp_path):
    """One number is quoted for every video whatever graph made it, so it comes from one place. The
    two graphs are held to the same duration by test_workflow_asset, not by asking both here."""
    assert generator(tmp_path, FakeClient()).seconds() == 5
```

Sahte ikinci grafik 9 taşıyor, bu yüzden yanlış grafikten okuyan bir uygulama burada düşer.

- [ ] **Step 6: Bitiş kareli üretimin testlerini yaz**

`test_a_video_with_no_end_frame_is_rendered_by_the_standard_graph`'in altına:

```python
def test_a_video_with_an_end_frame_is_rendered_by_the_first_last_graph(tmp_path):
    """The producer is told an ending picture, never a mode: loop and linked differ only in which
    photo arrives here, and both are this one graph."""
    client = FakeClient()

    data = generator(tmp_path, client).generate("kadın dönüyor", "", 42,
                                                source=("P0_0.png", b"PNGDATA"),
                                                end=("P1_0.png", b"ENDDATA"))

    assert data == b"MP4DATA"
    assert client.submitted["338"]["inputs"]["image"] == "server-P0_0.png"
    assert client.submitted["342"]["inputs"]["image"] == "server-P1_0.png"
    assert client.submitted["333:291"]["inputs"]["prompt"] == "kadın dönüyor"
    assert client.submitted["327"]["inputs"]["seed"] == 42
    assert client.submitted["333:291"]["inputs"]["seed"] == 42
    # The standard graph's nodes are nowhere in what was sent.
    assert "287" not in client.submitted


def test_both_frames_reach_the_server_as_uploads(tmp_path):
    # An ending frame is a picture like the first one: ComfyUI renders what it has been given, so a
    # path or a name that never travelled would be a file the server cannot find.
    client = FakeClient()

    generator(tmp_path, client).generate("p", "", 42, source=("P0_0.png", b"PNGDATA"),
                                         end=("P1_0.png", b"ENDDATA"))

    assert client.uploads == [("P0_0.png", b"PNGDATA"), ("P1_0.png", b"ENDDATA")]


def test_an_end_frame_does_not_stand_in_for_the_photo(tmp_path):
    # A video is built on a picture; the ending frame is where it arrives, not what it is made of.
    with pytest.raises(RuntimeError) as blew_up:
        generator(tmp_path, FakeClient()).generate("p", "", 42, end=("P1_0.png", b"ENDDATA"))

    assert "foto" in str(blew_up.value).lower()
```

- [ ] **Step 7: Yeni grafiğin üç arıza testini yaz**

Her biri, standart grafiğin aynı adı taşıyan testinin hemen altına:

```python
def test_a_missing_first_last_graph_names_the_file_it_wants(tmp_path):
    gen = generator(tmp_path, FakeClient(), first_last_path=str(tmp_path / "sonyok.json"))

    with pytest.raises(RuntimeError) as blew_up:
        gen.generate("prompt", "", 42, source=("P0_0.png", b"PNG"), end=("P1_0.png", b"END"))

    assert "sonyok.json" in str(blew_up.value)
```

```python
def test_a_first_last_graph_exported_in_ui_format_says_which_export_to_use(tmp_path):
    gen = generator(tmp_path, FakeClient(), first_last={"nodes": [], "links": []})

    with pytest.raises(RuntimeError) as blew_up:
        gen.generate("prompt", "", 42, source=("P0_0.png", b"PNG"), end=("P1_0.png", b"END"))

    assert "Export (API)" in str(blew_up.value)
```

```python
def test_a_first_last_graph_whose_nodes_moved_names_the_missing_one(tmp_path):
    moved = {k: v for k, v in FIRST_LAST_GRAPH.items() if k != "342"}
    gen = generator(tmp_path, FakeClient(), first_last=moved)

    with pytest.raises(RuntimeError) as blew_up:
        gen.generate("prompt", "", 42, source=("P0_0.png", b"PNG"), end=("P1_0.png", b"END"))

    assert "342" in str(blew_up.value)
```

- [ ] **Step 8: Takımı koştur**

Run: `python -m pytest queen-editor -q`
Expected: kurucu dördüncü argümanı tanımadığı için `test_comfy_video_generator.py`'ın **tamamı**
düşüyor — `TypeError: ComfyVideoGenerator.__init__() got multiple values for argument 'timeout'`,
çünkü bugünkü üçüncü konumsal argüman `timeout`'un kendisi. Bu beklenen kırmızı: o dosyadaki her
test `generator` yardımcısından geçiyor. Task 1'in üç kırmızısı da yerinde duruyor.

**Not — testler nasıl çağrılır:** CLAUDE.md dört satırı **birebir** istiyor; tek dosyayı adıyla
koşturmak yok. Bir turun ortasında da tam takım koşulur, kırmızı içinde kırmızı ayırt edilir.

---

### Task 3: Kuyruğun tek çağrı biçimi

**Files:**
- Modify: `queen-editor/backend/tests/test_producer_contract.py`

**Interfaces:**
- Consumes: Task 2'nin kurucusuyla aynı imza; ayrıca `ComfyPhotoGenerator.generate` ve
  `MMAudioGenerator.generate` bir `end` argümanı alacak.
- Produces: yok.

- [ ] **Step 1: Yeni grafiğin yolunu tanıt**

Dosyanın başındaki yol sabitlerine:

```python
FIRST_LAST_GRAPH = os.path.join(ROOT, "workflow_video_first_last_api.json")
```

- [ ] **Step 2: Üretici kurulumunu genişlet**

```python
        layers.VIDEO: ComfyVideoGenerator(video_comfy, VIDEO_GRAPH, FIRST_LAST_GRAPH, timeout=60),
```

- [ ] **Step 3: Tek çağrı biçiminin testini yaz**

`producers_over`'ın hemen altına:

```python
def test_a_producer_with_no_end_frame_takes_the_argument_anyway(tmp_path):
    """The queue has one call shape, not three: whatever the loop hands a producer, every producer
    takes. A photo is made from its words and a sound from the video under it -- neither has an
    ending picture, and both are still handed the argument."""
    ffmpeg = Ffmpeg()

    photo = ComfyPhotoGenerator(PhotoComfy(), PHOTO_GRAPH, timeout=60).generate(
        "kraliçe tahtta", "blurry", 1, end=("P1_0.png", b"PNG"))
    sound = MMAudioGenerator(Sampler(), ffmpeg, tmp_dir=str(tmp_path)).generate(
        "dalga sesi", "", None, source=("P0_0_V1_0.mp4", b"MP4"), end=("P1_0.png", b"PNG"))

    assert photo == b"PNG"
    assert sound == b"RIFFwav"
```

- [ ] **Step 4: Bütün takımı koştur**

Run, dördü de birebir, boru yok:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Expected: `queen-editor` kırmızı; kalan üç takım yeşil. Kırmızının üç ayrı sebebi var ve üçü de bu
döngüde bilerek bırakıldı: `config`'de ikinci grafiğin yolu yok, `ComfyVideoGenerator` dördüncü
argümanı tanımıyor, üç üreticinin hiçbiri `end` almıyor.

---

### Task 4: Kırmızı commit

- [ ] **Step 1: Commit**

```bash
git add queen-editor/backend/tests docs/superpowers
git commit -F - <<'EOF'
test(queen-editor): v14 task 1 - the engine can be given an ending frame

Red on purpose: the video producer holds one graph and takes no ending frame, config
names no second graph, and the video group does not list the CLIP vision model. The
other three suites stay green.

The producer is never told a mode, only whether an ending picture came with the job:
given one it renders on the first-last graph, given none it renders exactly as today.
Loop and linked differ only in which photo arrives, so both are the same graph and the
word mode never reaches the data layer.

Two graphs ship side by side because FIRST2LASTFRAME is a pipeline of its own - own
checkpoints, own CLIP vision, own sampling - so moving standard production onto it
would change how every video already made would look. Their durations are held equal
by a test instead, since one number is quoted for every video whatever graph made it.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** spec'in on iki testinin on ikisi planda kodlu. 1-3 → Task 1; 4-11 → Task 2;
12 → Task 3. Spec'in "Bu turun sınırı" bölümü → Global Constraints'in ilk maddesi (`run_loop`,
kuyruk ve üretim modu bu döngüde hiç anılmıyor).

**Tip tutarlılığı:** `ComfyVideoGenerator(client, standard, ends, timeout)` üç yerde de aynı sırada:
`generator` yardımcısında, `test_a_missing_graph_names_the_file_it_wants`'ta ve
`producers_over`'da. `end=(ad, bayt)` üç üreticinin çağrısında da aynı şekilde.

**Kontrol edilen tuzak:** sahte ikinci grafiğin süresi 9, birincisininki 5. İkisi eşit yazılsaydı
`test_the_length_is_still_read_from_the_standard_graph` yanlış grafikten okuyan bir uygulamayla da
yeşil kalırdı — testin bütün değeri bu farkta.

**Kontrol edilen tuzak 2:** `FakeClient.uploaded` tek alandı. Liste yapılmadan bırakılsaydı ikinci
yükleme birincinin üstüne yazardı ve `test_both_frames_reach_the_server_as_uploads` bir yüklemeyi
hiç göremezdi.

**Kontrol edilen tuzak 3:** `test_an_end_frame_does_not_stand_in_for_the_photo` bugün de yeşil
doğabilir — `source` yokken üretici zaten hata veriyor. Değeri ileriye dönük: implementasyon
döngüsünde `end`'i gören bir dal yazılırken, o dalın kaynak kontrolünün önüne geçmemesini tutan
tek test bu.

**Kontrol edilen kapsam:** `test_workflow_asset.py`'ın üç yeni testi `config`'e bakıyor,
`test_comfy_video_generator.py` ise `tmp_path`'e yazdığı sahte grafiklere. İkisi ayrı sebeple
kırmızı, ve implementasyon döngüsünde ayrı ayrı yeşile dönüyorlar: biri yol sabitiyle, öteki
üreticinin kendisiyle.
