# Queen Editor v5 · Görev 20 — Ses üret paneli · Uygulama planı

> Tasarım: [Görev 20 spec](../specs/2026-08-12-queen-editor-v5-gorev-20-ses-paneli-design.md).
> Her adım önce kırmızı test, sonra en küçük kod.

**Hedef:** video panelinin aynısı ses için de açılsın; ses işleri kuyruğa girsin; ses kopyası
kaynağın fotoğrafını **ve videosunu** paylaşsın.

**Mimari:** `queue_videos` → `queue_layer(kind)`; uç nokta `/layers/<kind>`; ön yüzde `VideoPanel`
→ `LayerPanel` (katmanın sözcükleri bir sözlükte).

## Genel kısıtlar

- Kod/yorum/test **İngilizce**, arayüz metni **Türkçe**.
- Katman sırası foto → video → ses; ses videonun üstüne biner.
- Test komutları (birebir): `python -m pytest queen-editor -q` ·
  `npm test --prefix queen-editor/frontend -- --run` · `npm run build --prefix queen-editor/frontend`

---

## Görev 1 — Kayıt katman prompt'larını söyler

**Dosyalar:** `data/photo_record.py`, `domain/ports.py`, `domain/run_loop.py`,
test: `tests/test_photo_record.py` (+ `tests/test_photo_usecases.py`'daki `FakeRecord`)

- [ ] **Adım 1 — kırmızı test (`test_photo_record.py`):**

```python
def test_prompts_are_folded_per_layer(tmp_path):
    record = record_at(tmp_path)
    record.append("düğün", {"file": "P0_0.png", "frame": "P0_0", "layer": "photo",
                            "status": "done", "prompt": "kırmızı elbise"})
    record.append("düğün", {"file": "P0_0_V1_0.mp4", "frame": "P0_0", "layer": "video",
                            "status": "done", "prompt": "kadın dönüyor"})

    assert record.prompts("düğün") == {"P0_0": {"photo": "kırmızı elbise",
                                                "video": "kadın dönüyor"}}
```

> `record_at` yardımcısı dosyada nasıl adlanıyorsa onu kullan.

- [ ] **Adım 2:** `python -m pytest queen-editor -q` → kırmızı.

- [ ] **Adım 3 — `DrivePhotoRecord`:**

```python
    def prompts(self, project):
        """{frame: {layer: prompt}} -- what each layer was made from; the latest line wins.

        Read by whoever needs a frame's own words: a copy frame carries them over, and the model
        that writes a video's or a sound's prompt starts from them.
        """
        folded = {}
        for row in self._rows(project):
            prompt = row.get("prompt")
            if isinstance(prompt, str):
                folded.setdefault(_frame_of(row), {})[_layer_of(row)] = prompt
        return folded
```

Aynısını `FakeRecord`'a da yaz (testlerin sahtesi kütüğü aynı şekilde katlıyor). `ports.py`'de
`PhotoRecord`'a bir satır ekle.

- [ ] **Adım 4 — `run_loop._prompts_of`** artık kaydın kendi cevabını okur:

```python
def _prompts_of(record, project, fid):
    """What the frame already says, layer by layer -- the material a prompt writer works from."""
    return record.prompts(project).get(fid, {})
```

> Görev 16'nın testleri yeşil kalmalı: `{"photo": "..."}` aynı sözlük.

- [ ] **Adım 5:** `python -m pytest queen-editor -q` → yeşil.

---

## Görev 2 — `queue_layer`

**Dosyalar:** `domain/usecases/queue_videos.py` → `queue_layer.py`, `presentation/routes.py`,
`main.py`, testler: `test_photo_usecases.py`, `test_photo_routes.py`

**Arayüz:** `queue_layer(runner, store, record, plan_store, order_store, producers, now, project,
kind, files=None, variants=1, log=None, writers=None) -> int` ·
`frames_in_scope(gallery, kind, files=None)` · `POST /api/projects/<project>/layers/<kind>`

- [ ] **Adım 1 — kırmızı testler:**

```python
def test_audio_skips_a_frame_that_has_no_video():
    # Sound is mixed over a video: a frame without one is never in its scope (madde 31).
    gallery = [{"id": "0_a", "file": "0_a.png", "status": "done", "layers": {}, "failed": []},
               {"id": "1_a", "file": "1_a.png", "status": "done",
                "layers": {"video": "1_a_V1_0.mp4"}, "failed": []}]

    assert [f["id"] for f in frames_in_scope(gallery, layers.AUDIO)] == ["1_a"]
    # Even by hand: there is nothing to lay the sound over.
    assert frames_in_scope(gallery, layers.AUDIO, ["0_a.png"]) == []


def test_audio_skips_a_video_that_blew_up():
    gallery = [{"id": "0_a", "file": "0_a.png", "status": "done",
                "layers": {"video": "0_a_V1_0.mp4"}, "failed": ["video"]}]

    assert frames_in_scope(gallery, layers.AUDIO) == []


def test_an_audio_job_is_planned_for_a_frame_with_a_video():
    store, record, plan_store = video_project((0, "a"))
    record.append("düğün", {"file": "0_a_V1_0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done", "prompt": "kadın dönüyor"})

    added = queue_layer(sync_runner(), store, record, plan_store, FakeOrderStore(),
                        {layers.PHOTO: FakeGenerator()}, lambda: "t", "düğün", layers.AUDIO)

    assert added == 1
    job = plan_store.appended[-1][0]
    assert (job["id"], job["type"]) == ("0_a", "audio")


def test_a_sound_copy_carries_the_photo_and_the_video():
    store, record, plan_store = video_project((0, "a"))
    record.append("düğün", {"file": "0_a_V1_0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done", "prompt": "kadın dönüyor"})

    queue_layer(sync_runner(), store, record, plan_store, FakeOrderStore(),
                {layers.PHOTO: FakeGenerator()}, lambda: "t", "düğün", layers.AUDIO, variants=2)

    copy = record.slots("düğün")["P0_1"]
    assert copy["photo"]["file"] == "0_a.png"
    assert copy["video"]["file"] == "0_a_V1_0.mp4"
    # And the words the source was made from come with them.
    assert record.prompts("düğün")["P0_1"] == {"photo": "p", "video": "kadın dönüyor"}


def test_a_video_copy_still_carries_only_the_photo():
    store, record, plan_store = video_project((0, "a"))

    queue_layer(sync_runner(), store, record, plan_store, FakeOrderStore(),
                {layers.PHOTO: FakeGenerator()}, lambda: "t", "düğün", layers.VIDEO, variants=2)

    assert list(record.slots("düğün")["P0_1"]) == ["photo"]
```

Yol testleri (`test_photo_routes.py`): mevcut `/videos` testlerini `/layers/video`'ya çevir ve ekle:

```python
def test_an_unknown_layer_is_not_a_place_to_queue_anything(tmp_path):
    client, _ = make_client(tmp_path)

    assert client.post("/api/projects/düğün/layers/foto", json={}).status_code == 404
```

- [ ] **Adım 2:** `python -m pytest queen-editor -q` → kırmızı.

- [ ] **Adım 3 — dosyayı `queue_layer.py` olarak yaz** (git mv gerekmez; yeni dosya + eskisini sil).
Kapsam:

```python
def frames_in_scope(gallery, kind, files=None):
    """The frames a `kind` job can be hung on, in gallery order.

    `files` is the gallery's own selection; None means every frame that does not have this layer
    yet. A frame that already has one is out of the None scope and inside a selection's: picking a
    frame by hand says "this one", and that is how a second video or a second sound is asked for --
    it becomes a copy frame rather than writing over what is there (madde 25).
    """
    chosen = None if files is None else set(files)
    scope = []
    for frame in gallery:
        if chosen is not None and frame["file"] not in chosen:
            continue
        # Only a produced photo can carry anything, and a name that claims no number cannot be
        # planned at all: the plan keeps a number per job and reads back only the jobs that have one.
        if frame["status"] != "done" or _family(frame)[0] is None:
            continue
        held, broken = frame.get("layers", {}), frame.get("failed", [])
        # Sound is mixed over a video, so a frame without one -- or whose video blew up -- is never
        # in its scope, however it was chosen (madde 31). The photo needs no check of its own: a
        # frame whose status is done has one.
        if kind == layers.AUDIO and (layers.VIDEO not in held or layers.VIDEO in broken):
            continue
        if chosen is None and kind in held:
            continue
        scope.append(frame)
    return scope
```

Kopya, üretilen katmanın altındaki her şeyi taşır:

```python
        for _ in range(owed):
            copy = next_id(taken, number)
            taken.add(copy)
            # A real frame, born holding everything below the layer being made: a video copy shares
            # the picture, a sound copy shares the picture and the video (madde 102). No flag and no
            # field -- the gallery draws it, deletes it and orders it by the rules it already has.
            for under in queue.ORDER[:queue.ORDER.index(kind)]:
                file = frame.get("layers", {}).get(under)
                if not file:
                    continue
                record.append(project, {"file": file, "frame": copy, "layer": under,
                                        "status": queue.DONE,
                                        "prompt": said.get(under, ""),
                                        "negative": frame.get("negative", ""),
                                        "seed": frame.get("seed"), "createdAt": now()})
            born.setdefault(fid, []).append(copy)
            jobs.append(_job(kind, copy, number, variant_of(copy)))
```

> `said = record.prompts(project).get(fid, {})` döngünün başında bir kez okunur; foto satırı için
> `frame["layers"]["photo"]` zaten var (kare üretilmiş).

`_video_job` → `_job(kind, fid, number, variant)`.

`queue_videos` adını kullanan her yeri (`routes.py`, `main.py`, testler) `queue_layer`'a çevir.

- [ ] **Adım 4 — `routes.py`:** yol katmanı taşır.

```python
    @bp.post("/api/projects/<project>/layers/<kind>")
    def post_layer(project, kind):
        if kind not in QUEUEABLE:
            # A photo is asked for with its own prompts, not by hanging a layer on a frame.
            return jsonify({"error": f"Böyle bir katman yok: {kind}"}), 404
        ...
            added = queue_layer(project, kind, files=files, variants=body.get("variants", 1))
```

`QUEUEABLE = (layers.VIDEO, layers.AUDIO)` dosyanın başında.

- [ ] **Adım 5:** `python -m pytest queen-editor -q` → yeşil.

---

## Görev 3 — `LayerPanel`

**Dosyalar:** `VideoPanel.jsx` → `LayerPanel.jsx`, `VideoPanel.test.jsx` → `LayerPanel.test.jsx`,
`SidePanel.jsx`, `glyphs.jsx`, `shared/api.js`, `useGeneration.js`

- [ ] **Adım 1 — kırmızı testler:** var olan video testleri `<LayerPanel layer="video" …/>` ile
koşar (metinler aynı), üstüne ses için:

```jsx
describe("LayerPanel — sound", () => {
  const FRAMES = [
    { id: "0_a", file: "0_a.png", status: "done", layers: {}, failed: [] },
    { id: "1_a", file: "1_a.png", status: "done", layers: { video: "1_a_V1_0.mp4" }, failed: [] },
  ];

  function renderSound(props) {
    return render(<LayerPanel layer="audio" frames={FRAMES} selected={[]} producer={null}
                              onQueue={() => Promise.resolve({ added: 1 })} onInstall={() => {}}
                              {...props} />);
  }

  it("counts only the frames that have a video and no sound", () => {
    renderSound();

    expect(screen.getByText("Videosu olup sesi olmayan kareler").closest("button").textContent)
      .toContain("1");
  });

  it("says what it would make, in its own words", () => {
    renderSound();

    expect(screen.getByText("MMAudio v2")).toBeTruthy();
    expect(screen.getByText("1 ses üretilecek — her kare kendi sesini alır.")).toBeTruthy();
  });

  it("says there is nothing to do in its own words", () => {
    renderSound({ frames: [FRAMES[0]] });

    expect(screen.getByText("Videosu olup sesi olmayan kare yok — üretilecek bir şey yok."))
      .toBeTruthy();
  });

  it("confirms in its own words", async () => {
    renderSound();

    await act(async () => { fireEvent.click(screen.getByText("Kuyruğa ekle")); });

    expect(screen.getByText("1 ses kuyruğa eklendi")).toBeTruthy();
  });
});
```

- [ ] **Adım 2:** `npm test --prefix queen-editor/frontend -- --run` → kırmızı.

- [ ] **Adım 3 — `LayerPanel.jsx`:** katmanın sözcükleri bir sözlükte.

```jsx
// What each layer calls itself. The panel is one component because the design asks for one
// ("video panelinin birebir aynısı"); only these words and the scope rule differ.
const WORDS = {
  video: {
    model: "WAN 2.2 I2V", missing: "Videosu olmayanlar", noun: "video",
    note: "Her video 5 saniye — bu sürümde sabit.",
    empty: "Tüm karelerin videosu var — üretilecek bir şey yok.",
    hint: "Video prompt'u otomatik: LLM her fotonun kendi prompt'undan yazar. Detayda okunur, düzenlenir.",
  },
  audio: {
    model: "MMAudio v2", missing: "Videosu olup sesi olmayan kareler", noun: "ses",
    note: "Ses videonun süresince üretilir.",
    empty: "Videosu olup sesi olmayan kare yok — üretilecek bir şey yok.",
    hint: "Ses prompt'u otomatik: LLM fotonun ve videonun prompt'undan yazar. Detayda okunur, düzenlenir.",
  },
};
```

Kapsam süzgeci sunucununkiyle aynı cümleyi kurar:

```jsx
/** The frames this layer can be hung on. The server decides the same way -- this is the panel's
 *  own count, not a second rule: sound needs a video under it, video needs only a photo. */
function eligible(frames, layer) {
  return (frames || []).filter((frame) => {
    if (frame.status !== "done") return false;
    const held = frame.layers || {};
    const broken = frame.failed || [];
    if (layer === "audio" && (!held.video || broken.includes("video"))) return false;
    return true;
  });
}
```

`missing` = `eligible(...)` içinden `!held[layer]` olanlar; `inSelection` = `eligible` ∩ seçim.

Buton ikonu: video için `VideoGlyph`, ses için yeni `SoundGlyph` (dalga).

- [ ] **Adım 4 — `glyphs.jsx`:** dalga ikonu.

```jsx
// A wave: what the design puts in front of the sound panel's button and on its rail icon.
export const SoundGlyph = ({ size }) => (
  <Glyph name="sound" size={size}>
    <path d="M1.8 7c.9-2.6 1.7-2.6 2.6 0s1.7 2.6 2.6 0 1.7-2.6 2.6 0 1.7 2.6 2.6 0"
          stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" />
  </Glyph>
);
```

- [ ] **Adım 5 — `SidePanel.jsx`:** şeride `{ id: "audio", title: "Ses üret" }` satırı, `GLYPH`'e
`audio: SoundGlyph`, ve iki panel de `LayerPanel`:

```jsx
        {(open === "video" || open === "audio") && (
          <LayerPanel layer={open} frames={frames} selected={selected}
                      producer={(producers?.producers || []).find((p) => p.id === open)}
                      onQueue={(files, variants) => onQueueLayer(open, files, variants)}
                      onInstall={producers?.install} />
        )}
```

- [ ] **Adım 6 — `api.js` ve `useGeneration.js`:** `queueVideos(project, files, variants)` →
`queueLayer(project, kind, files, variants)`; hook'ta `queueVideo` → `queueLayer(kind, files,
variants)`.

- [ ] **Adım 7:** `npm test --prefix queen-editor/frontend -- --run` → yeşil.

---

## Görev 4 — Tam takım, build, commit

- [ ] `python -m pytest queen-editor -q`
- [ ] `npm test --prefix queen-editor/frontend -- --run`
- [ ] `npm run build --prefix queen-editor/frontend`
- [ ] `dist/` ile tek commit:

```
feat(queen-editor): sound is asked for the way a video is
```
