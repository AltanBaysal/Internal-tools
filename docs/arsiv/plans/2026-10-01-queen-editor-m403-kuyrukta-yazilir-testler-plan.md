# Madde 403 — Prompt'lar kuyruğa eklenirken yazılıp karta eklenir, test turunun planı

> **Koşum:** bu oturumda, satır satır.

**Hedef:** Spec'in on iki testi ve sözü değişen iki sayfa testi — yeni testler kırmızı.

**Mimari:** Kayıt yazılmış prompt'u tutar (`prompt_written`, `written_prompts`) ve durum saymaz
*(test 1–5)*; döngü her turda önce borçlu işlerin prompt'unu yazar, sonra karttakiyle üretir *(6–11)*;
sayfa henüz yazılmamış prompt için yeni sözü söyler *(12 ve iki değişen test)*.

**Spec:** [m403 test turu](../specs/2026-10-01-queen-editor-m403-kuyrukta-yazilir-testler-design.md)

## Her yere geçerli kurallar

- Test adı ve yorum **İngilizce**. Kaynak kod değişmiyor.
- Yeni port adları (`prompt_written`, `written_prompts`) yalnız çağrıldıkları yerde geçer: toplama
  hatası olmaz, test kendi içinde kırmızıya döner.
- `FakeRecord` gerçeğinin katlayışını taklit eder — test kodudur, bu turda değişir.

---

## Görev 1: `queen-editor/backend/tests/test_photo_record.py`

Başa `import pytest`. Dosyanın sonuna:

```python
# Madde 403: a prompt written for a layer still owed is kept on the card until the layer is made.
def test_a_written_prompt_waits_for_the_layer_still_owed(tmp_path):
    record = record_at(tmp_path)

    record.prompt_written("düğün", "0_a", "video", "0_a_V1_0.mp4", "kadın dönüyor", "t")

    assert record.written_prompts("düğün") == {"0_a": {"video": "kadın dönüyor"}}


def test_the_frame_says_the_written_prompt_for_that_layer(tmp_path):
    """What the detail page shows and what the sound's writer reads: the frame's words, layer by
    layer -- a layer still owed says the words it will be made with."""
    record = record_at(tmp_path)
    record.append("düğün", {"file": "0_a.png", "frame": "0_a", "layer": "photo",
                            "status": "done", "prompt": "kırmızı elbise"})

    record.prompt_written("düğün", "0_a", "video", "0_a_V1_0.mp4", "kadın dönüyor", "t")

    assert record.prompts("düğün") == {"0_a": {"photo": "kırmızı elbise",
                                                "video": "kadın dönüyor"}}


def test_a_written_prompt_is_not_a_status_of_the_layer(tmp_path):
    """The layer is exactly as owed as it was. A job never written about stays one and a job put
    back in line stays put back -- the queue orders those two apart."""
    record = record_at(tmp_path)
    record.prompt_written("düğün", "0_a", "video", "0_a_V1_0.mp4", "kadın dönüyor", "t")
    record.mark("düğün", "1_a", "video", "1_a_V1_0.mp4", "queued", "t")
    record.prompt_written("düğün", "1_a", "video", "1_a_V1_0.mp4", "kadın eğiliyor", "t")

    assert record.slots("düğün") == {
        "1_a": {"video": {"status": "queued", "file": "1_a_V1_0.mp4"}}}


@pytest.mark.parametrize("status", ["done", "failed", "removed", "queued", "deleted"])
def test_the_next_line_about_the_layer_ends_its_written_prompt(tmp_path, status):
    """Landed, blew up, pulled out, put back in line, deleted: whatever happens next, the prompt
    was for the layer as it was queued. A layer queued again is written for again."""
    record = record_at(tmp_path)
    record.prompt_written("düğün", "0_a", "video", "0_a_V1_0.mp4", "kadın dönüyor", "t")

    record.mark("düğün", "0_a", "video", "0_a_V1_0.mp4", status, "t2")

    assert record.written_prompts("düğün") == {}


def test_a_written_prompt_is_about_its_own_layer_alone(tmp_path):
    record = record_at(tmp_path)
    record.prompt_written("düğün", "0_a", "video", "0_a_V1_0.mp4", "kadın dönüyor", "t")

    record.mark("düğün", "0_a", "photo", "0_a.png", "deleted", "t2")

    assert record.written_prompts("düğün") == {"0_a": {"video": "kadın dönüyor"}}
```

## Görev 2: `queen-editor/backend/tests/test_photo_usecases.py`

`FakeRecord`'a, `mark`'ın altına:

```python
    def prompt_written(self, project, frame, layer, file, prompt, at):
        self.rows.append({"frame": frame, "layer": layer, "file": file, "status": "written",
                          "prompt": prompt, "at": at})
```

`FakeRecord.slots`'un döngüsünün başına:

```python
            # A written prompt is not something that became of the layer (madde 403).
            if row.get("status") == "written":
                continue
```

`FakeRecord.prompts`'un altına:

```python
    def written_prompts(self, project):
        folded = {}
        for row in self.rows:
            slot = (self._frame_of(row), self._layer_of(row))
            if row.get("status") == "written":
                folded[slot] = row["prompt"]
            else:
                folded.pop(slot, None)
        answer = {}
        for (frame, layer), prompt in folded.items():
            answer.setdefault(frame, {})[layer] = prompt
        return answer
```

`test_a_frame_from_the_flat_list_is_handed_no_scene`'in altına:

```python
# Madde 403: a prompt is written as its layer is queued and put on the card; the producer uses it.
def test_a_queued_video_s_prompt_is_on_its_card_before_it_is_made():
    """Nobody can make the video in this session, so nothing is produced at all -- and the card
    already says what the video will be made with."""
    store, record = FakeStore(), FakeRecord()
    plan_store = FakePlanStore(frames=[frame(0, prompt="kırmızı elbiseli kadın")])
    record.append("düğün", {"file": "0_a.png", "frame": "0_a", "layer": "photo", "status": "done",
                            "prompt": "kırmızı elbiseli kadın"})
    runner = sync_runner()

    queue_layer(runner, store, record, plan_store, FakeOrderStore(),
                {layers.PHOTO: FakeGenerator()}, lambda: "t", "düğün", layers.VIDEO,
                writers={layers.VIDEO: FakeWriter()})

    assert runner.status()["status"] == "waiting"
    card = list_frames(record, store, plan_store, FakeOrderStore(), "düğün")[0]
    assert card["owed"] == ["video"]
    assert card["prompts"]["video"] == "kadın başını yavaşça çeviriyor"


def test_every_owed_prompt_is_written_before_anything_is_made():
    store, record = FakeStore(), FakeRecord()
    plan_store = FakePlanStore(frames=[frame(0), frame(1)])
    for number in (0, 1):
        record.append("düğün", {"file": f"{number}_a.png", "frame": f"{number}_a",
                                "layer": "photo", "status": "done",
                                "prompt": "kırmızı elbiseli kadın"})
    plan_store.append("düğün", [{"id": f"{number}_a", "type": "video", "number": number,
                                 "variant": 0, "prompt": "", "negative": "", "seed": None,
                                 "model": ""} for number in (0, 1)])
    writer, generator = FakeWriter(), FakeGenerator()
    asked_by_then = []
    original = generator.generate

    def spy(*args, **kwargs):
        asked_by_then.append(len(writer.calls))
        return original(*args, **kwargs)

    generator.generate = spy

    resume_batch(sync_runner(), store, record, plan_store, {layers.VIDEO: generator},
                 lambda: "t", "düğün", writers={layers.VIDEO: writer})

    assert asked_by_then == [2, 2]


def test_a_prompt_already_on_the_card_is_not_bought_again():
    """Written before the server went down: the run that picks the job up again makes the video
    with the card's own words and asks nobody."""
    store, record, plan_store = video_job_project(prompt="kırmızı elbiseli kadın")
    record.prompt_written("düğün", "0_a", "video", "0_a_V1_0.mp4", "elini kaldırıyor", "t")
    generator, writer = FakeGenerator(), FakeWriter()

    resume_batch(sync_runner(), store, record, plan_store, {layers.VIDEO: generator},
                 lambda: "t", "düğün", writers={layers.VIDEO: writer})

    assert writer.calls == []
    assert [call[0] for call in generator.calls] == ["elini kaldırıyor"]
    assert video_row(record)["prompt"] == "elini kaldırıyor"


def test_a_sound_is_written_seeing_the_video_s_written_prompt():
    """The sound's writer reads the video's prompt when there is one, and a written one is one."""
    store, record, plan_store = video_job_project(prompt="kırmızı elbiseli kadın")
    plan_store.frames.append({"id": "0_a", "type": "audio", "number": 0, "variant": 0,
                              "prompt": "", "negative": "", "seed": None, "model": ""})
    sound_writer = FakeWriter(answer="fabric rustling")

    resume_batch(sync_runner(), store, record, plan_store, {layers.PHOTO: FakeGenerator()},
                 lambda: "t", "düğün",
                 writers={layers.VIDEO: FakeWriter(answer="kadın başını çeviriyor"),
                          layers.AUDIO: sound_writer})

    assert sound_writer.calls == [{"photo": "kırmızı elbiseli kadın",
                                   "video": "kadın başını çeviriyor"}]


def test_a_layer_sent_back_with_tekrar_dene_is_written_for_again():
    """Put back in line is queued again: its prompt is written again, and the card shows the new
    one before it is made."""
    store, record, plan_store = video_job_project(prompt="kırmızı elbiseli kadın")
    record.prompt_written("düğün", "0_a", "video", "0_a_V1_0.mp4", "eski prompt", "t")
    record.mark("düğün", "0_a", "video", "0_a_V1_0.mp4", queue.FAILED, "t",
                error="node 41 — 3 kez denendi")
    generator, writer = FakeGenerator(), FakeWriter()

    retry_frame(sync_runner(), store, record, plan_store, {layers.VIDEO: generator},
                lambda: "t2", "düğün", "0_a", writers={layers.VIDEO: writer})

    assert len(writer.calls) == 1
    assert [call[0] for call in generator.calls] == ["kadın başını yavaşça çeviriyor"]


def test_while_prompts_are_written_no_frame_is_reported_as_being_made():
    """A prompt being written is not a layer being made: no tile says üretiliyor meanwhile."""
    store, record, plan_store = video_job_project(prompt="kırmızı elbiseli kadın")
    runner, writer = sync_runner(), FakeWriter()
    seen = []
    original = writer.write

    def spy(*args, **kwargs):
        seen.append(runner.status().get("current"))
        return original(*args, **kwargs)

    writer.write = spy

    resume_batch(runner, store, record, plan_store, {layers.VIDEO: FakeGenerator()},
                 lambda: "t", "düğün", writers={layers.VIDEO: writer})

    assert seen == [None]
```

## Görev 3: `queen-editor/frontend/src/features/photo_generation/PhotoDetail.test.jsx`

İki yerde `"Prompt yok — üretim sırası geldiğinde eklenecek."` →
`"Prompt yok — üretimden önce yazılacak."`.

*"a copy frame waiting in the queue"* bloğunun sonuna:

```jsx
  it("shows the prompt written for the layer it is waiting for", async () => {
    // Madde 403: the prompt is written as the layer is queued, so a waiting video already has its
    // words -- and the box shows them rather than a notice.
    await open("P0_1", { frames: [{ ...QUEUED_COPY,
      prompts: { photo: "kırmızı elbise", video: "kadın başını çeviriyor" } }] });

    fireEvent.click(tab("Video"));

    expect(screen.getByText("kadın başını çeviriyor")).toBeTruthy();
    expect(screen.queryByText("Prompt yok — üretimden önce yazılacak.")).toBeNull();
  });
```

## Görev 4: Koşu ve kırmızı commit

- [ ] Dört satır paralel, yazıldığı gibi *(CLAUDE.md, Commands)*.
- [ ] Beklenen: `queen-editor` pytest'inde Görev 1'in bütün testleri kırmızı *(`prompt_written` yok)*;
      Görev 2'de 6, 7, 8, 9 ve 11 kırmızı *(döngü bekleyen koşuda yazmıyor, üretimden hemen önce
      yazıyor, karttakini okumuyor, yazarken işi üretiliyor diye bildiriyor)*; 10 yeşil *(bekçi)*.
      Bütün eski testler yeşil. `queen-editor` vitest'inde değişen iki test kırmızı, yenisi yeşil.
      `queen-agent`'ın iki satırı yeşil.
- [ ] Spec, plan ve üç test dosyası tek commit'te: `test(queen-editor): Madde 403 red -- …`.
