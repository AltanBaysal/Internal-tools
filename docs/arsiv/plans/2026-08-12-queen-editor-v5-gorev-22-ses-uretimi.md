# Queen Editor v5 · Görev 22 — Motor sesi üretir ve videoya bindirir · Uygulama planı

> Tasarım: [Görev 22 spec](../specs/2026-08-12-queen-editor-v5-gorev-22-ses-uretimi-design.md).
> Önce kırmızı test, sonra en küçük kod.

**Hedef:** ses işi ComfyUI'nin ses grafiğiyle üretilsin, çıkan wav videonun adını büyüten adla
yazılsın, galeride ikinci rozet doğsun.

## Genel kısıtlar

- Kod/yorum/test **İngilizce**, arayüz metni **Türkçe**.
- Test komutları (birebir): `python -m pytest queen-editor -q` ·
  `npm test --prefix queen-editor/frontend -- --run` · `npm run build --prefix queen-editor/frontend`

---

## Görev 1 — İstemci sesi de bulur

**Dosyalar:** `services/comfy/client.py`, test: `tests/test_comfy_client.py`

- [ ] **Adım 1 — kırmızı test:**

```python
def test_fetch_output_finds_a_sound_wherever_the_node_published_it():
    # ComfyUI publishes sound under its own key; the extension is what picks the file.
    entry = {"outputs": {"90": {"audio": [{"filename": "s.wav", "subfolder": "",
                                           "type": "output"}]}}}
    http = FakeHttp(gets=[FakeResponse(content=b"WAVDATA")])

    assert client_with(http).fetch_output(entry, extensions=(".wav",)) == b"WAVDATA"
```

- [ ] **Adım 2:** kırmızı.

- [ ] **Adım 3 — `fetch_output`:** uzantı verildiğinde çıktı sözlüğünün her listesine bakılır.

```python
        outputs = []
        for node_output in history_entry.get("outputs", {}).values():
            # With an extension to go by, every list the node published is worth looking at: which
            # key a medium lands under is the node's own business (images, gifs, audio, videos).
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
```

- [ ] **Adım 4:** yeşil.

---

## Görev 2 — Ses üreticisi

**Dosyalar:** yeni `data/comfy_audio_generator.py`, test: yeni
`tests/test_comfy_audio_generator.py`

- [ ] **Adım 1 — kırmızı testler:** `test_comfy_video_generator.py`'nin kalıbı, grafik:

```python
GRAPH = {
    "1": {"class_type": "VHS_LoadVideoPath", "inputs": {"video": "example.mp4"}},
    "2": {"class_type": "MMAudioSampler", "inputs": {"prompt": "", "seed": -1}},
}
```

testler: video yüklenir ve grafiğe yazılır · prompt yazılır · `.wav` istenir · kaynak yoksa
patlar · grafik yok/UI biçiminde/node eksik hâlleri.

- [ ] **Adım 2:** kırmızı.

- [ ] **Adım 3 — `comfy_audio_generator.py`:** `ComfyVideoGenerator`'ın ikizi; node kimlikleri
`VIDEO_NODE = "1"`, `PROMPT_NODE = "2"`, `AUDIO_EXTENSIONS = (".wav",)`; tohum yalnız node'da
varsa yazılır (`if seed is not None and "seed" in inputs`).

> Gerçek export gelince node kimlikleri değişecek; dosyanın başındaki tablo o gün güncellenir.

- [ ] **Adım 4:** yeşil.

---

## Görev 3 — Adı videonun adı büyütür

**Dosyalar:** `domain/photo_name.py`, `domain/run_loop.py`, testler: `test_photo_name.py`,
`test_photo_usecases.py`

- [ ] **Adım 1 — kırmızı testler:**

```python
def test_a_sounds_file_grows_the_videos_name():
    assert layer_file("audio", "P11_3", video="P11_3_V1_0.mp4") == "P11_3_V1_0_S1_0.wav"


def test_a_sound_with_no_video_falls_back_to_the_frames_own_name():
    # Should not happen -- sound is never in scope without a video -- but a name is still a name.
    assert layer_file("audio", "P11_3") == "P11_3_S1_0.wav"
```

ve motor:

```python
def test_a_sound_is_made_from_the_frames_video_and_written_beside_it():
    store, record, plan_store = video_job_project(prompt="kırmızı elbiseli kadın")
    record.append("düğün", {"file": "0_a_V1_0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done", "prompt": "kadın dönüyor"})
    store.files["0_a_V1_0.mp4"] = b"MP4DATA"
    plan_store.frames.append({"id": "0_a", "type": "audio", "number": 0, "variant": 0,
                              "prompt": "sessiz oda", "negative": "", "seed": None, "model": ""})
    generator = FakeGenerator()

    resume_batch(sync_runner(), store, record, plan_store,
                 {layers.VIDEO: FakeGenerator(), layers.AUDIO: generator},
                 lambda: "t", "düğün")

    assert generator.sources == [("0_a_V1_0.mp4", b"MP4DATA")]
    assert [name for name, _d in store.saved] == ["0_a_V1_0_S1_0.wav"]
```

- [ ] **Adım 2:** kırmızı.

- [ ] **Adım 3 — `photo_name.layer_file`:**

```python
def layer_file(kind, frame, video=None):
    """The file name one produced layer takes.

    Photo and video are named from the frame's own identity; audio grows the VIDEO's name, because
    a sound is mixed over one particular video and the name has to say which.
    """
    if kind == layers.VIDEO:
        return video_file(frame, FIRST_ROUND, FIRST_VARIANT)
    if kind == layers.AUDIO:
        stem = video.rsplit(".", 1)[0] if video else frame
        return audio_file(stem, FIRST_ROUND, FIRST_VARIANT)
    return photo_file(frame)
```

- [ ] **Adım 4 — `run_loop`:** hem ad hem kaynak karenin videosunu bilir.

```python
            held = slots.get(fid, {})
            video = held.get(layers.VIDEO, {}).get("file") if held else None
            name = layer_file(kind, fid, video=video)
```

`_source_for` katmanın altındakini verir:

```python
def _source_for(kind, store, slots, project, fid):
    """The file a layer is made from, as (name, bytes); None for a layer that needs none.

    A video hangs on the frame's photo and a sound is laid over its video, while a photo is made
    from its prompt alone. Read at the job's turn rather than kept in memory: the file is on Drive
    and the run may have started hours ago.
    """
    under = {layers.VIDEO: layers.PHOTO, layers.AUDIO: layers.VIDEO}.get(kind)
    if under is None:
        return None
    cell = slots.get(fid, {}).get(under)
    if not cell:
        return None
    return (cell["file"], store.read(project, cell["file"]))
```

- [ ] **Adım 5:** yeşil.

---

## Görev 4 — Bağlama

**Dosyalar:** `config.py`, `main.py`

```python
AUDIO_WORKFLOW_PATH = os.path.join(os.path.dirname(_BACKEND_DIR), "workflow_audio_api.json")
AUDIO_TIMEOUT = 15 * 60    # seconds for one sound; MMAudio is fast, so this is a stall guard
```

```python
_producers = {layers.PHOTO: _photo_generator, layers.VIDEO: _video_generator,
              layers.AUDIO: _audio_generator}
```

- [ ] `python -m pytest queen-editor -q` → yeşil.

---

## Görev 5 — Galeride ikinci rozet

**Dosyalar:** `Gallery.jsx`, test: `Gallery.test.jsx`

- [ ] **Adım 1 — kırmızı testler:**

```jsx
  it("marks a frame that has a sound as well", () => {
    renderGallery({ frames: [withVideo("P0_0.png", {
      layers: { photo: "P0_0.png", video: "P0_0_V1_0.mp4", audio: "P0_0_V1_0_S1_0.wav" } })] });

    expect(screen.getByText("video")).toBeTruthy();
    expect(screen.getByText("ses")).toBeTruthy();
    expect(document.querySelector("[data-glyph=sound]")).toBeTruthy();
  });

  it("does not call a failed sound something the frame owns", () => {
    renderGallery({ frames: [withVideo("P0_0.png", {
      layers: { photo: "P0_0.png", video: "P0_0_V1_0.mp4", audio: "P0_0_V1_0_S1_0.wav" },
      failed: ["audio"] })] });

    expect(screen.queryByText("ses")).toBeNull();
  });
```

- [ ] **Adım 2:** kırmızı.

- [ ] **Adım 3 — `Gallery.jsx`:** `owns` tek katmandan listeye döner.

```jsx
// What the frame owns, in layer order. A layer that blew up holds its slot but is not something
// the frame owns -- that is the pill's to say.
const OWNED = [{ layer: "video", word: "video", Glyph: PlayGlyph },
               { layer: "audio", word: "ses", Glyph: SoundGlyph }];
```

```jsx
          const owns = OWNED.filter(({ layer }) => (frame.layers || {})[layer]
            && !(frame.failed || []).includes(layer));
```

`Tile` içinde tek kutunun içinde ikisi yan yana çizilir.

- [ ] **Adım 4:** yeşil.

---

## Görev 6 — Tam takım, build, commit

- [ ] `python -m pytest queen-editor -q`
- [ ] `npm test --prefix queen-editor/frontend -- --run`
- [ ] `npm run build --prefix queen-editor/frontend`
- [ ] `dist/` ile tek commit:

```
feat(queen-editor): the engine lays a sound over the video it belongs to
```

- [ ] Kullanıcıya söyle: `workflow_audio_api.json` da repoda yok; video grafiğiyle birlikte
export edilip commit'lenmeli.
