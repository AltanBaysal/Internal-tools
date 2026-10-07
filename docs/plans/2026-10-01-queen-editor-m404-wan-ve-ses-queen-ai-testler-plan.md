# Madde 404 — WAN'ın ve sesin prompt'unu Queen AI yazar, test turunun planı

> **Koşum:** bu oturumda, satır satır.

**Hedef:** Spec'in on dört testi — yeni ve değişen testler kırmızı.

**Mimari:** WAN yazarı Queen AI'a H3'ünki gibi fotoğrafı ve senaryoyu gösterir, ses yazarı yalnız
videonun prompt'unu gönderir *(test 1–10)*; döngü sesi yalnız videonun prompt'u varsa yazdırır
*(11–12)*; `main.py` WAN'ı ve sesi Queen AI'a bağlar *(13–14)*.

**Spec:** [m404 test turu](../specs/2026-10-01-queen-editor-m404-wan-ve-ses-queen-ai-testler-design.md)

## Her yere geçerli kurallar

- Test adı ve yorum **İngilizce**. Kaynak kod değişmiyor.
- Metinlerin tamamı testte tutulmaz; anlamlı cümleleri tutulur.
- Hiçbir test ağa çıkmaz: kablo testleri iki anahtarı da boşaltır, böylece kırmızı koşuda bile grok'a
  istek gitmez.

---

## Görev 1: `queen-editor/backend/tests/test_video_prompt_writer.py`

- Grok biçimli `FakeClient` sınıfı silinir; bütün yazarlar `FakeVisionClient` ile sorulur.
- Silinen testler: `test_the_photo_prompt_is_what_the_model_is_asked_to_convert`,
  `test_the_instruction_says_what_wan_needs_and_what_to_leave_out`,
  `test_the_sound_is_written_from_both_prompts`, `test_a_frame_with_no_video_prompt_still_sends_what_it_has`,
  `test_wan_is_asked_as_before_whatever_else_it_is_handed`,
  `test_the_sound_is_asked_as_before_whatever_else_it_is_handed`.

Dosyanın başına, `FakeVisionClient`'ın altına *(test 1–5, 8, 10)*:

```python
def test_the_wan_writer_shows_queen_ai_the_photo_and_the_scenario():
    """Madde 404: WAN's prompt is written the way H3's is -- the model sees the picture the tags
    drew, so the tags themselves are not sent."""
    client = FakeVisionClient(answer="she turns her head")

    written = VideoPromptWriter(client).write({"photo": "score_9_up, 1girl, queen"}, "standard",
                                              source=PHOTO, scene=THRONE)

    assert written == "she turns her head"
    assert client.calls == [(VIDEO_INSTRUCTION, f"Scenario: {THRONE}", [PHOTO])]


def test_a_wan_frame_with_no_scenario_sends_the_photo_alone():
    client = FakeVisionClient()

    VideoPromptWriter(client).write({"photo": "score_9_up, 1girl, queen"}, "standard",
                                    source=PHOTO, scene="")

    assert client.calls == [(VIDEO_INSTRUCTION, "", [PHOTO])]


def test_the_wan_text_asks_for_the_motion_alone_with_the_camera_still():
    assert "Never describe the photo again." in VIDEO_INSTRUCTION
    assert "Keep the camera static: no camera movement, no zoom, no pan." in VIDEO_INSTRUCTION


def test_the_wan_text_leaves_the_sound_out():
    """The user's words (1 Ekim): "wan değişsin sesi katma" -- WAN makes no sound, and the sound
    has a prompt of its own."""
    assert "Wan makes no sound." in VIDEO_INSTRUCTION
    assert "Write no sounds and no spoken words." in VIDEO_INSTRUCTION


def test_the_wan_text_says_what_to_do_without_a_scenario():
    assert ("If no scenario is given, write a small, natural motion for the photo."
            in VIDEO_INSTRUCTION)


def test_the_sound_is_written_from_the_video_s_prompt_alone():
    """The user's words (1 Ekim): "mmaudio da video promptundan alsın". No picture and none of the
    photo's words: the video's prompt already says what happens."""
    client = FakeVisionClient(answer="fabric rustling, footsteps on stone")

    written = AudioPromptWriter(client).write({"photo": "kırmızı elbiseli kadın",
                                              "video": "kadın başını çeviriyor"})

    assert written == "fabric rustling, footsteps on stone"
    assert client.calls == [(AUDIO_INSTRUCTION, "Video prompt: kadın başını çeviriyor", [])]


def test_the_sound_text_writes_from_the_video_prompt():
    assert "The video prompt says what happens in the video." in AUDIO_INSTRUCTION
    assert "Write only the sounds the video prompt implies." in AUDIO_INSTRUCTION
```

`test_wan_asks_for_the_same_returning_motion` *(test 6)*:

```python
def test_wan_asks_for_the_same_returning_motion():
    # Loop is a mode of both engines, so the rule belongs to both writers -- as one sentence.
    client = FakeVisionClient()

    VideoPromptWriter(client).write({"photo": "kırmızı elbiseli kadın"}, "loop", source=PHOTO,
                                    scene="")

    assert client.calls == [(VIDEO_INSTRUCTION + _loop_rule(), "", [PHOTO])]
```

`test_the_sound_writer_takes_the_mode_and_ignores_it` yalnız `FakeVisionClient(answer="fabric
rustling")`'e geçer.

`test_wan_never_hears_of_picture_2` *(test 7)* ve `test_the_sound_is_asked_as_before…`'in yerine
*(test 9)*:

```python
def test_wan_never_hears_of_picture_2():
    """The linked text names Picture 2 and is H3's alone: WAN is shown its own photo and nothing
    else, whatever the mode."""
    client = FakeVisionClient()

    VideoPromptWriter(client).write({"photo": "kırmızı elbiseli kadın"}, "linked", source=PHOTO,
                                    end=NEXT, scene=THRONE)

    assert client.calls == [(VIDEO_INSTRUCTION, f"Scenario: {THRONE}", [PHOTO])]


def test_the_sound_is_shown_no_picture_whatever_it_is_handed():
    """The loop hands every writer the same arguments; the sound's takes the video's prompt alone."""
    client = FakeVisionClient(answer="fabric rustling")

    AudioPromptWriter(client).write({"photo": "kırmızı elbiseli kadın", "video": "kadın dönüyor"},
                                    "standard", source=("P0_0_V1_0.mp4", b"MP4"), end=NEXT,
                                    scene=THRONE)

    assert client.calls == [(AUDIO_INSTRUCTION, "Video prompt: kadın dönüyor", [])]
```

## Görev 2: `queen-editor/backend/tests/test_photo_usecases.py`

`test_a_sound_job_is_written_from_the_frames_two_prompts` →
`test_a_sound_job_s_writer_is_handed_the_frame_s_words`, gövdesi aynı.

`test_a_model_that_will_not_answer_stops_the_run`'ın altına *(test 11–12)*:

```python
# Madde 404: a sound is written from its video's prompt alone.
def test_a_sound_whose_video_has_no_prompt_is_not_worth_an_ask():
    """The photo's words are not what a sound is written from, so they buy no ask: the sound is made
    with no prompt, like a frame with no words at all."""
    store, record, plan_store = video_job_project(prompt="kırmızı elbiseli kadın")
    record.append("düğün", {"file": "0_a_V1_0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done", "prompt": ""})
    store.files["0_a_V1_0.mp4"] = b"MP4DATA"
    plan_store.frames.append({"id": "0_a", "type": "audio", "number": 0, "variant": 0,
                              "prompt": "", "negative": "", "seed": None, "model": ""})
    sound, writer = FakeGenerator(), FakeWriter()

    resume_batch(sync_runner(), store, record, plan_store,
                 {layers.VIDEO: FakeGenerator(), layers.AUDIO: sound},
                 lambda: "t", "düğün", writers={layers.AUDIO: writer})

    assert writer.calls == []
    assert [call[0] for call in sound.calls] == [""]


def test_a_sound_is_written_once_its_video_s_own_prompt_is_on_the_card():
    """A video that carries the user's words has them in the record only once it is made, so the
    sound waits for them rather than being written from nothing."""
    store, record, plan_store = video_job_project(prompt="kırmızı elbiseli kadın",
                                                  job_prompt="elini kaldırıyor")
    plan_store.frames.append({"id": "0_a", "type": "audio", "number": 0, "variant": 0,
                              "prompt": "", "negative": "", "seed": None, "model": ""})
    sound, writer = FakeGenerator(), FakeWriter(answer="fabric rustling")

    resume_batch(sync_runner(), store, record, plan_store,
                 {layers.VIDEO: FakeGenerator(), layers.AUDIO: sound},
                 lambda: "t", "düğün", writers={layers.AUDIO: writer})

    assert writer.calls == [{"photo": "kırmızı elbiseli kadın", "video": "elini kaldırıyor"}]
    assert [call[0] for call in sound.calls] == ["fabric rustling"]
```

## Görev 3: `queen-editor/backend/tests/test_composition_root.py`

`test_a_wan_session_s_video_prompt_is_still_grok_s` ve `test_an_h3_session_s_sound_prompt_is_still_grok_s`'in
yerine *(test 13–14)*:

```python
def test_a_wan_session_s_video_prompt_is_queen_ai_s(import_main, monkeypatch):
    """Madde 404: DeepSeek writes WAN's prompt too. Both keys are empty, so the sentence names the
    model the writer asks -- and no request leaves either way."""
    monkeypatch.setenv("QE_DEEPSEEK_API_KEY", "")
    monkeypatch.setenv("QE_XAI_API_KEY", "")
    main = import_main("")

    assert "DEEPSEEK_API_KEY" in _refusal(main, layers.VIDEO)


@pytest.mark.parametrize("video_model", ["", "h3"])
def test_every_session_s_sound_prompt_is_queen_ai_s(import_main, monkeypatch, video_model):
    """Madde 404: the sound is written by Queen AI in a session of either video model."""
    monkeypatch.setenv("QE_DEEPSEEK_API_KEY", "")
    monkeypatch.setenv("QE_XAI_API_KEY", "")
    main = import_main(video_model)

    assert "DEEPSEEK_API_KEY" in _refusal(main, layers.AUDIO)
```

## Görev 4: Kırmızı koşu ve commit

- [ ] Dört satır, paralel, yazıldığı gibi.
- [ ] Beklenen: `queen-editor` pytest'inde spec'in 1–14'ü kırmızı *(3 ve 5–10'un bazıları eski metinde
  yok ya da çağrı biçimi eski)*; `test_the_sound_writer_takes_the_mode_and_ignores_it` ve
  `test_the_sound_instruction_asks_for_the_scenes_own_sounds` yeşil; ötekiler yeşil.
- [ ] Commit: `test(queen-editor): Madde 404 red -- …`
