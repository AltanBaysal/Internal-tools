# Görev 2 — Dosya adları katman şemasına geçer · Uygulama planı

**Amaç:** Yeni doğan kareler `P{prompt}_{varyant}` kimliğiyle ve `P11_3.png` adıyla gelir; katman
dosyaları adı `_V1_0` / `_S1_0` ile büyütür. Eski adlı kareler dokunulmadan yan yana yaşar.

**Mimari:** Şema tek bir alan modülünde (`domain/photo_name.py`) yaşamayı sürdürür; kimlik artık
hesaplanmıyor, plan karesine yazılıyor. Ayrıştırma iki şemayı da okur.

**Spec:** [Görev 2](../specs/2026-08-12-queen-editor-v5-gorev-2-dosya-adi-semasi-design.md)

## Genel kısıtlar

- **Full TDD**, test komutu `python -m pytest queen-editor -q`.
- Dil ayrımı, bağımlılık yönü ve geriye uyum kuralları Görev 1 planındakiyle aynı.
- **Tek commit**, görev komple bitince.

## Dosya haritası

| Dosya | Değişen |
|---|---|
| `domain/photo_name.py` | Yeni şema, katman adları, iki şemalı ayrıştırma |
| `domain/usecases/start_batch.py` | Plan karesinin `id` ve `variant` taşıması |
| `domain/queue.py` · `run_loop.py` · `list_frames.py` · `retry_frame.py` · `cancel_generation.py` | Kimliği hesaplamak yerine kareden okumak |
| `domain/ports.py` · `data/photo_store.py` | `save` dosya adını alması |
| `tests/test_photo_name.py` · `test_photo_usecases.py` · `test_photo_record.py` · `test_photo_routes.py` | Beklentiler |

---

## Adım 1 — Şema testleri (kırmızı)

`tests/test_photo_name.py`'ye ekle:

```python
def test_a_new_frames_identity_carries_the_prompt_and_the_variant():
    assert frame_id(11, 3) == "P11_3"


def test_the_photo_file_is_the_identity_with_an_extension():
    assert photo_file("P11_3") == "P11_3.png"


def test_a_video_file_grows_the_identity_by_its_own_pair():
    assert video_file("P11_3", 1, 0) == "P11_3_V1_0.mp4"


def test_an_audio_file_grows_the_video_name():
    # Audio is mixed over one video, so its name says which one.
    assert audio_file("P11_3_V1_0", 1, 0) == "P11_3_V1_0_S1_0.wav"


def test_a_legacy_identity_keeps_its_letter():
    assert legacy_frame_id(11, "d") == "11_d"


def test_both_schemes_yield_the_same_number():
    assert number_of("P11_3.png") == 11
    assert number_of("11_d.png") == 11
    assert number_of("P11_3_V1_0.mp4") == 11
    assert number_of("P11_3_V1_0_S1_0.wav") == 11


def test_a_name_outside_both_schemes_has_no_number():
    assert number_of("notlar.txt") is None
    assert number_of("photos.jsonl") is None
    assert number_of("P.png") is None
    assert number_of("Px_3.png") is None
```

Koş → `ImportError`.

## Adım 2 — `photo_name.py`

```python
"""How a frame is identified, and how each of its layer files is named.

Identity and file name are not the same thing (see Görev 1): the identity says which frame, the name
says which file. A picture can belong to two frames and one frame can own three files.

The scheme says what a frame carries. A photo-only frame is P11_3; give it a video and the video
file is P11_3_V1_0.mp4; mix audio over that video and the audio file is P11_3_V1_0_S1_0.wav. Every
layer adds a pair -- round and variant -- and a layer that is not there is never written. The audio
name grows the video's rather than the frame's, because audio is mixed over one particular video.

Two schemes read, one writes. Frames born before this file said "P" are still on Drive under
<number>_<letter>; nothing is renamed (renaming is a bulk write over a user's finished work, and
photo URLs are handed out as permanent). So parsing accepts both and only new frames are named the
new way.
"""


def frame_id(number, variant):
    """A frame's identity: P + the prompt number + its photo variant.

    Variants count from zero, which is the design's "a=0, b=1" rule with the letters taken out.
    """
    return f"P{number}_{variant}"


def legacy_frame_id(number, letter):
    """The identity frames born before the P scheme carry."""
    return f"{number}_{letter}"


def photo_file(frame):
    """The name a frame's photo is stored under."""
    return f"{frame}.png"


def video_file(frame, round_no, variant):
    """The name a frame's video is stored under -- the identity plus this layer's pair."""
    return f"{frame}_V{round_no}_{variant}.mp4"


def audio_file(video, round_no, variant):
    """The name an audio layer is stored under -- the VIDEO's name plus this layer's pair.

    `video` is the video file's name without its extension: audio is mixed over one video, and the
    name has to say which.
    """
    return f"{video}_S{round_no}_{variant}.wav"


def frame_id_of(name):
    """A file or stored name -> the frame it belongs to; an identity comes back unchanged."""
    stem = name.rsplit(".", 1)[0] if "." in name else name
    # Layer pairs are suffixes on the identity, so the frame is what comes before the first one.
    for marker in ("_V", "_S"):
        cut = stem.find(marker)
        if cut != -1:
            stem = stem[:cut]
    return stem


def number_of(filename):
    """The prompt number a file's name claims; None when the name fits neither scheme.

    Both schemes claim numbers, because both name real files and a number may never be reused.
    """
    stem = frame_id_of(filename)
    if stem.startswith("P"):
        number, _, variant = stem[1:].partition("_")
        return int(number) if number.isdigit() and variant.isdigit() else None
    number, _, letter = stem.partition("_")
    if not number.isdigit() or len(letter) != 1 or not letter.isalpha():
        return None
    return int(number)
```

**Dikkat:** `file_name(number, letter)` kalkıyor; çağıranlar `photo_file(frame_id)`'a geçiyor.

Koş → şema testleri yeşil, çağıranlar kırmızı.

## Adım 3 — Plan karesi kimliğini taşır

`start_batch.plan_frames`:

```python
def plan_frames(start, prompts, negative, variants, new_seed, model=""):
    """[{"id", "number", "variant", "prompt", "negative", "seed", "model"}] in prompt-major order.

    Prompt-major means P0_0 P0_1 … P1_0. Number = prompt, variant = which of its variants.

    The identity is written down here rather than computed later, and that is the point: it is the
    one thing about a frame that must never change. A computed identity would have moved under every
    frame on Drive the moment the scheme changed, and the gallery order the user dragged into place
    points at exactly these strings.

    The negative and the model ride on the frame rather than on the plan: a live queue holds batches
    submitted under different settings, and a frame has to render with the ones it was submitted
    under.

    Seeds are drawn here, when the frames are planned, rather than when a frame renders: the plan is
    what a resumed run reads back, so a frame has to produce the image it was planned to produce.
    """
    return [{"id": frame_id(start + index, variant), "number": start + index, "variant": variant,
             "prompt": prompt, "negative": negative, "seed": new_seed(), "model": model}
            for index, prompt in enumerate(prompts)
            for variant in range(variants)]
```

`plan_store.read` geriye uyumu tamamlar — `id` yoksa eski kimlik yazılır:

```python
        for frame in data["frames"]:
            if not isinstance(frame, dict) or not isinstance(frame.get("number"), int):
                continue
            negative = frame.get("negative")
            model = frame.get("model")
            # A frame planned before models could be chosen carries none, and empty means "the
            # graph's own checkpoint" -- so those frames render exactly as they always did.
            # A frame planned before identities were written down gets the one it was born with.
            identity = frame.get("id")
            if not isinstance(identity, str):
                identity = legacy_frame_id(frame["number"], frame.get("letter", "a"))
            frames.append({**frame, "id": identity,
                           "negative": negative if isinstance(negative, str) else legacy,
                           "model": model if isinstance(model, str) else ""})
```

## Adım 4 — Çağıranlar kimliği kareden okur

Beş yerde aynı değişiklik: `frame_id(frame["number"], frame["letter"])` → `frame["id"]`,
`file_name(...)` → `photo_file(frame["id"])`.

- `queue._key(frame)` → `frame["id"]`
- `queue.counts` → `photo_file(f["id"])`
- `run_loop`: `fid = frame["id"]`, `name = photo_file(fid)`, `store.save(project, name, data)`
- `cancel_generation`, `retry_frame`, `list_frames`: aynı ikame

`PhotoStore.save` artık dosya adını alıyor (numara/harf değil), çünkü adı kuran yer artık şema
modülü:

```python
    def save(self, project, filename, data):
        """Persist the photo under the name the domain chose; returns that name."""
        self._storage.write_bytes(project, filename, data)
        return filename
```

`photo_store.next_number` aynen kalır — `number_of` iki şemayı da okuduğu için diskteki her iki tür
adı da sayar.

## Adım 5 — Testleri güncelle ve yeşile boya

- `test_photo_usecases.py`: `FakeStore.save(project, filename, data)`; **`FakePlanStore.read`
  gerçeğinin `id` geriye uyumunu taşır** (yoksa eski kareli testler kimliksiz kalır); `plan_frames`
  beklentileri `id`/`variant` taşır; kare kurucusu `frame(number, variant=0, ...)` olur ve `id`
  yazar; dosya adı beklentileri `P0_0.png` biçimine geçer.
- `start_batch`: varyant sınırı `LETTERS`'a değil kendi sabitine bakar (`MAX_VARIANTS = 26`);
  hata metni değişmez.
- `test_photo_record.py`: dokunulmaz (geriye uyum testleri eski adlarla kalmalı).
- `test_photo_routes.py`: üretilen dosya adı beklentileri `P0_0.png` biçimine geçer.
- **Yeni test — yan yana yaşama:**

```python
def test_old_and_new_frames_live_side_by_side():
    record, plan_store = FakeRecord(), FakePlanStore()
    # A project made before the scheme changed: its plan has no identities.
    plan_store.frames = [{"number": 11, "letter": "d", "prompt": "eski", "seed": 1}]
    record.append("düğün", {"file": "11_d.png", "status": "done"})
    order = FakeOrderStore(["11_d"])

    run_batch(sync_runner(), FakeStore(next_no=12), FakeGenerator(), text='["yeni"]', variants=1,
              record=record, plan_store=plan_store)
    frames = list_frames(record, FakeStore(), plan_store, order, "düğün")

    # The old frame keeps its name and its place; the new one is named the new way.
    assert [f["id"] for f in frames] == ["P12_0", "11_d"]
    assert [f["file"] for f in frames] == ["P12_0.png", "11_d.png"]
```

Koş → tam takım yeşil.

## Adım 6 — Commit

```bash
git add queen-editor/backend docs/superpowers
git commit -m 'feat(queen-editor): file names carry the layers a frame has'
```

## Kabul kriteri

- Yeni kare `P{prompt}_{varyant}.png` adıyla iniyor ve kimliği o.
- Eski adlı kareli projeye yeni kare eklenince ikisi yan yana duruyor, numara çakışmıyor, sıra
  bozulmuyor.
- `python -m pytest queen-editor -q` yeşil.
