# Madde 402 — Sonrakine bağlı karede geçiş yumuşar, test turunun planı

> **Koşum:** bu oturumda, satır satır.

**Hedef:** Spec'in yedi testi ve değişen ses testi — yeni testler kırmızı.

**Mimari:** Yazarın portu videonun vardığı resmi (`end`) de alır; H3 yazarı bağlı videoda iki resmi
gösterir ve bağlı metni ekler *(test 1–5)*; döngü vardığı resmi yazardan önce bulur ve yazara da verir
*(6–7)*.

**Spec:** [m402 test turu](../specs/2026-10-01-queen-editor-m402-sonrakine-bagli-testler-design.md)

## Her yere geçerli kurallar

- Test adı ve yorum **İngilizce**. Kaynak kod değişmiyor.
- Henüz olmayan isim (`LINKED_RULE`) kullanıldığı yerde içe aktarılıyor: pytest toplama hatasında
  bütün oturumu durdurur.
- Bağlı metnin tamamı testte tutulmaz; anlamlı cümleleri tutulur.

---

## Görev 1: `queen-editor/backend/tests/test_video_prompt_writer.py`

`THRONE`'un altına:

```python
# Madde 402: a linked video's writer sees the photo the video ends on too.
NEXT = ("P1_0.png", b"NEXTDATA")
```

`test_a_linked_video_gets_the_h3_text_alone_for_now`'ın yerine:

```python
def _linked_rule():
    from backend.features.photo_generation.data import xai_prompt_writer
    return xai_prompt_writer.LINKED_RULE


def test_a_linked_video_shows_queen_ai_both_pictures_in_order():
    """Madde 402: the video ends on the next frame's photo, so the model is shown where it has to
    arrive -- this frame's photo first, as Picture 1, then the next one's, as Picture 2."""
    instruction, writer = _h3()
    client = FakeVisionClient()

    writer(client).write({"photo": "kırmızı elbiseli kadın"}, "linked", source=PHOTO, end=NEXT,
                         scene=THRONE)

    assert client.calls == [(instruction + _linked_rule(), f"Scenario: {THRONE}", [PHOTO, NEXT])]


def test_the_linked_text_calls_the_next_photo_picture_2_and_ends_on_it():
    rule = _linked_rule()

    assert "call the second photo Picture 2" in rule
    assert "Picture 2 is the last frame of the video." in rule


def test_the_linked_text_asks_for_the_changes_in_detail():
    """The user's words (v8-3, 29 Eylül): today a linked video joins "uc uca eklem gibi", and a
    transition written in detail is what the video model follows."""
    rule = _linked_rule()

    assert "Write the changes in detail, so the video flows into Picture 2 and never jumps." in rule
    assert "Never describe the two photos again." in rule


def test_a_loop_video_shows_its_picture_once():
    """A loop ends on its own photo -- the one already shown -- so it is not sent a second time, and
    nothing of the linked text reaches it."""
    instruction, writer = _h3()
    client = FakeVisionClient()

    writer(client).write({"photo": "kırmızı elbiseli kadın"}, "loop", source=PHOTO, end=PHOTO,
                         scene="")

    assert client.calls == [(instruction + _loop_rule(), "", [PHOTO])]
```

`test_wan_is_asked_as_before_whatever_else_it_is_handed`'ın altına:

```python
def test_wan_never_hears_of_picture_2():
    """The linked text names Picture 2, and WAN's writer is shown no picture at all: the text is
    H3's alone. 404 moves WAN."""
    client = FakeClient()

    VideoPromptWriter(client).write({"photo": "kırmızı elbiseli kadın"}, "linked", source=PHOTO,
                                    end=NEXT, scene=THRONE)

    assert client.calls == [(VIDEO_INSTRUCTION, "kırmızı elbiseli kadın")]
```

`test_the_sound_is_asked_as_before_whatever_else_it_is_handed`'ın çağrısı `end=NEXT`'i de alır:

```python
    AudioPromptWriter(client).write({"photo": "kırmızı elbiseli kadın", "video": "kadın dönüyor"},
                                    "standard", source=("P0_0_V1_0.mp4", b"MP4"), end=NEXT,
                                    scene=THRONE)
```

## Görev 2: `queen-editor/backend/tests/test_photo_usecases.py`

`FakeWriter`:

```python
    def __init__(self, answer="kadın başını yavaşça çeviriyor", blows_up=None):
        self.answer = answer
        self.blows_up = blows_up
        self.calls = []
        self.modes = []
        # What the writer is shown besides the words: the file the layer is made from and the
        # frame's scenario (madde 400), and the picture a video arrives at (402). Apart for the
        # reason the modes are.
        self.sources = []
        self.ends = []
        self.scenes = []

    def write(self, prompts, mode="standard", source=None, end=None, scene=""):
        self.calls.append(prompts)
        # Kept apart from the words: which mode a job is in is a different question, and one list
        # holding both could not answer either (madde 307).
        self.modes.append(mode)
        self.sources.append(source)
        self.ends.append(end)
        self.scenes.append(scene)
        if self.blows_up:
            raise self.blows_up
        return self.answer
```

`test_a_linked_video_whose_target_lost_its_photo_turns_that_frame_red`'ın altına:

```python
def write_one_video(mode, linked_to=None, numbers=(0, 1)):
    """render_one_video with a writer to ask: the job carries no prompt and the photos have words,
    so the writer is asked. Returns (writer, generator, record)."""
    store, record = FakeStore(), FakeRecord()
    plan_store = FakePlanStore(frames=[frame(number) for number in numbers])
    for number in numbers:
        fid = f"{number}_a"
        record.append("düğün", {"file": f"{fid}.png", "frame": fid, "layer": "photo",
                                "status": "done", "prompt": "kırmızı elbiseli kadın"})
        store.files[f"{fid}.png"] = f"{fid} bytes".encode()
    job = {"id": "0_a", "type": "video", "number": 0, "variant": 0, "prompt": "", "negative": "",
           "seed": None, "model": "", "mode": mode}
    if linked_to is not None:
        job["linkedTo"] = linked_to
    plan_store.append("düğün", [job])
    writer, generator = FakeWriter(), FakeGenerator()
    make_job(sync_runner(), store, record, plan_store, {layers.VIDEO: generator},
             lambda: "t", "düğün", writers={layers.VIDEO: writer})()
    return writer, generator, record


@pytest.mark.parametrize("mode, linked_to, arrives_at", [
    (production_mode.STANDARD, None, None),
    (production_mode.LOOP, None, ("0_a.png", b"0_a bytes")),
    (production_mode.LINKED, "1_a", ("1_a.png", b"1_a bytes")),
])
def test_the_writer_is_handed_the_picture_the_video_arrives_at(mode, linked_to, arrives_at):
    """Madde 402: a linked video's prompt is written seeing the next frame's photo -- the very one
    the producer ends on, read once for both."""
    writer, generator, _record = write_one_video(mode, linked_to)

    assert writer.ends == [arrives_at]
    assert generator.ends == [arrives_at]


def test_a_linked_video_with_nowhere_to_end_asks_the_writer_nothing():
    """The frame it was told to end on lost its photo, so the video cannot be made and no prompt is
    bought for it. The tile turns red as it always has."""
    writer, _generator, record = write_one_video(production_mode.LINKED, "1_a", numbers=(0,))

    assert writer.calls == []
    assert record.slots("düğün")["0_a"]["video"]["status"] == queue.FAILED
```

## Görev 3: Koşu ve kırmızı commit

- [ ] Dört satır paralel, yazıldığı gibi *(CLAUDE.md, Commands)*.
- [ ] Beklenen: `queen-editor` pytest'inde kırmızı — Görev 1'in beşi ve değişen ses testi *(`end`
      bilinmeyen argüman; `LINKED_RULE` yok)*; Görev 2'de parametreli testin loop ve bağlı hâlleri
      *(yazar `end` almıyor — sahte yazarın varsayılanı `None`)* ve kayıp fotoğraf testi *(yazar
      resimden önce soruluyor)*. Parametreli testin standart hâli yeşil *(bekçi)*. Bütün eski testler
      yeşil. Öteki üç satır yeşil.
- [ ] Spec, plan ve iki test dosyası tek commit'te: `test(queen-editor): Madde 402 red -- …`.
