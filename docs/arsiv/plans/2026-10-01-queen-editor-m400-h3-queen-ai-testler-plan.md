# Madde 400 — H3 prompt'unu Queen AI yazar, test turunun planı

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*.

**Hedef:** Spec'in yirmi dokuz testi ve H3'ün, Loop'un değişen testleri — yeni testler kırmızı.

**Mimari:** Yeni servis `services/deepseek/client.py` *(test 1–9)*; yazarın portu fotoğrafı
(`source`) ve senaryoyu (`scene`) alır *(10–18, 19–22)*; main.py H3 oturumunda H3 yazarını DeepSeek'e
bağlar *(23–26)*; defter anahtarı okur ve geçirir *(27–29)*.

**Spec:** [m400 test turu](../specs/2026-10-01-queen-editor-m400-h3-queen-ai-testler-design.md)

## Her yere geçerli kurallar

- Test adı ve yorum **İngilizce**; defter testlerinin assert cümleleri Türkçe. Kaynak kod değişmiyor.
- Henüz olmayan modül ve isim kullanıldığı yerde içe aktarılıyor: pytest toplama hatasında bütün
  oturumu durdurur.
- Metinlerin tamamı testte tutulmaz; anlamlı cümleleri tutulur.

---

## Görev 1: `queen-editor/backend/tests/test_deepseek_client.py` — yeni dosya

```python
"""The DeepSeek transport (madde 400): an instruction, words and pictures in, the answer's text out.

The client is imported where it is used rather than at the top: a module that is not there yet
would fail collection, and pytest stops the whole session on a collection error.
"""
import base64

import pytest

URL = "https://api.deepseek.com/chat/completions"
PHOTO = ("P0_0.png", b"PNGDATA")


def _module():
    from backend.services.deepseek import client
    return client


class FakeResponse:
    def __init__(self, payload=None, status_code=200, text=""):
        self._payload = payload
        self.status_code = status_code
        self.text = text or ""

    def json(self):
        if self._payload is None:
            raise ValueError("no json")
        return self._payload


class FakeHttp:
    """Records the one request the client makes and answers with what the test set up."""

    def __init__(self, response):
        self.response = response
        self.calls = []

    def post(self, url, headers=None, json=None, timeout=None):
        self.calls.append({"url": url, "headers": headers, "body": json, "timeout": timeout})
        return self.response


def answering(text):
    return FakeResponse({"choices": [{"message": {"content": text}}]})


def client(http, api_key="k-1"):
    return _module().DeepSeekClient(api_key, "deepseek-flash", URL, http=http, timeout=120)


def picture(media_type, data):
    """The part a picture travels as: a data URL, since the file is on this machine and nowhere a
    link could point at."""
    return {"type": "image_url",
            "image_url": {"url": f"data:{media_type};base64,{base64.b64encode(data).decode()}"}}


def test_the_request_carries_the_model_the_instruction_the_picture_and_the_words():
    http = FakeHttp(answering(" integrated_multimodal_description: [Shot 1] she turns "))

    answer = client(http).complete("talimat", "Scenario: kraliçe dönüyor", [PHOTO])

    assert answer == "integrated_multimodal_description: [Shot 1] she turns"
    call = http.calls[0]
    assert call["url"] == URL
    assert call["headers"]["Authorization"] == "Bearer k-1"
    assert call["timeout"] == 120
    # The picture rides in the user message alone: DeepSeek answers 400 to one in the system message.
    assert call["body"] == {
        "model": "deepseek-flash",
        "messages": [{"role": "system", "content": "talimat"},
                     {"role": "user", "content": [
                         picture("image/png", b"PNGDATA"),
                         {"type": "text", "text": "Scenario: kraliçe dönüyor"}]}],
    }


def test_the_picture_s_type_is_read_off_its_name():
    http = FakeHttp(answering("x"))

    client(http).complete("talimat", "söz", [("kare.jpg", b"JPGDATA")])

    assert http.calls[0]["body"]["messages"][1]["content"][0] == picture("image/jpeg", b"JPGDATA")


def test_with_no_words_the_user_message_holds_the_picture_alone():
    http = FakeHttp(answering("x"))

    client(http).complete("talimat", "", [PHOTO])

    assert http.calls[0]["body"]["messages"][1]["content"] == [picture("image/png", b"PNGDATA")]


def test_an_http_error_is_raised_with_the_servers_own_body():
    http = FakeHttp(FakeResponse(status_code=401, text='{"error": "invalid key"}'))

    with pytest.raises(RuntimeError) as blew_up:
        client(http).complete("talimat", "", [PHOTO])

    assert "401" in str(blew_up.value)
    assert '{"error": "invalid key"}' in str(blew_up.value)


def test_an_answer_that_is_not_the_expected_shape_shows_what_came():
    http = FakeHttp(FakeResponse({"choices": []}, text='{"choices": []}'))

    with pytest.raises(RuntimeError) as blew_up:
        client(http).complete("talimat", "", [PHOTO])

    assert '{"choices": []}' in str(blew_up.value)


def test_an_empty_answer_is_a_failure_rather_than_an_empty_prompt():
    http = FakeHttp(answering("   "))

    with pytest.raises(RuntimeError):
        client(http).complete("talimat", "", [PHOTO])


def test_without_a_key_it_says_so_before_it_asks_anything():
    http = FakeHttp(answering("x"))

    with pytest.raises(_module().NotConfigured) as refused:
        client(http, api_key="").complete("talimat", "", [PHOTO])

    assert http.calls == []
    assert "DEEPSEEK_API_KEY" in str(refused.value) and "Colab Secrets" in str(refused.value)


def test_the_key_reaches_the_header_without_the_whitespace_around_it():
    """A key pasted into Colab's secret store can carry a trailing newline, and the header is
    built here."""
    http = FakeHttp(answering("x"))

    client(http, api_key="\n k-1 \n").complete("talimat", "", [PHOTO])

    assert http.calls[0]["headers"]["Authorization"] == "Bearer k-1"


def test_a_key_that_is_only_whitespace_counts_as_no_key():
    http = FakeHttp(answering("x"))

    with pytest.raises(_module().NotConfigured):
        client(http, api_key="   ").complete("talimat", "", [PHOTO])

    assert http.calls == []
```

## Görev 2: `queen-editor/backend/tests/test_video_prompt_writer.py`

`FakeClient`'ın altına:

```python
# Madde 400: Queen AI is shown the frame's photo and reads its scenario.
PHOTO = ("P0_0.png", b"PNGDATA")
THRONE = "Kraliçe tahtında oturuyor; salon boş ve karanlık."


class FakeVisionClient:
    """DeepSeek, without one: records each ask as (instruction, words, pictures)."""

    def __init__(self, answer="integrated_multimodal_description: [Shot 1] she turns"):
        self.answer = answer
        self.calls = []

    def complete(self, system, text="", images=()):
        self.calls.append((system, text, list(images)))
        return self.answer
```

`test_the_h3_writer_converts_the_photo_prompt_with_its_own_instruction`'ın yerine:

```python
def test_the_h3_writer_shows_queen_ai_the_photo_and_the_scenario():
    """The model sees the picture the tags drew, so the tags themselves are not sent."""
    instruction, writer = _h3()
    client = FakeVisionClient()

    written = writer(client).write({"photo": "score_9_up, 1girl, queen"}, "standard",
                                   source=PHOTO, scene=THRONE)

    assert written == "integrated_multimodal_description: [Shot 1] she turns"
    assert client.calls == [(instruction, f"Scenario: {THRONE}", [PHOTO])]


def test_a_frame_with_no_scenario_sends_the_photo_alone():
    """The H3 text says what to do then: a small, natural motion for the picture."""
    instruction, writer = _h3()
    client = FakeVisionClient()

    writer(client).write({"photo": "score_9_up, 1girl, queen"}, "standard", source=PHOTO,
                         scene="")

    assert client.calls == [(instruction, "", [PHOTO])]
```

`test_the_h3_instruction_says_the_photo_is_the_first_frame`'in cümlesi:
`"The photo is the first frame of the video."`

`test_the_h3_instruction_never_asks_for_dynv2`'nin gövdesi:

```python
    _instruction, writer = _h3()
    client = FakeVisionClient()

    for mode in ("standard", "loop", "linked"):
        writer(client).write({"photo": "kırmızı elbiseli kadın"}, mode, source=PHOTO,
                             scene=THRONE)

    for sent, _words, _pictures in client.calls:
        assert "dynv2" not in sent, f"Talimat hâlâ dynv2 istiyor:\n{sent}"
```

Üç bölüm testinin altına:

```python
def test_the_h3_text_asks_for_no_speech_where_the_scenario_has_none():
    """The user's words (v8-3, 29 Eylül): "özellikle konuşma belirtilmediyse senayoda o framede
    konuşma eklnemesin". H3 has no negative, so the prompt itself says there is none."""
    instruction, _writer = _h3()

    assert "write no speech at all" in instruction
    assert '"No one speaks."' in instruction


def test_the_h3_text_calls_the_photo_picture_1_and_leaves_the_first_line_to_the_code():
    """The producer opens the prompt with the line saying where each picture sits
    (comfy_h3_video_generator), and that line calls the photo Picture 1."""
    instruction, _writer = _h3()

    assert "call the photo Picture 1" in instruction
    assert "Never write the line." in instruction


def test_the_h3_text_says_what_to_do_without_a_scenario():
    instruction, _writer = _h3()

    assert "If no scenario is given, write a small, natural motion for Picture 1." in instruction
```

`test_a_loop_video_is_asked_for_a_motion_that_returns` ve
`test_a_plain_video_is_asked_for_nothing_extra`'nın gövdeleri, ve yanlarına bağlı kare:

```python
    instruction, writer = _h3()
    client = FakeVisionClient()

    writer(client).write({"photo": "kırmızı elbiseli kadın"}, "loop", source=PHOTO, scene="")

    assert client.calls[0][0] == instruction + _loop_rule()
```

```python
    instruction, writer = _h3()
    client = FakeVisionClient()

    writer(client).write({"photo": "kırmızı elbiseli kadın"}, "standard", source=PHOTO,
                         scene="")

    assert client.calls[0][0] == instruction


def test_a_linked_video_gets_the_h3_text_alone_for_now():
    """Madde 402 adds what a linked video is asked for, with the next frame's photo; until then it
    is asked what a plain one is."""
    instruction, writer = _h3()
    client = FakeVisionClient()

    writer(client).write({"photo": "kırmızı elbiseli kadın"}, "linked", source=PHOTO, scene="")

    assert client.calls[0][0] == instruction
```

Loop metninin testleri:

```python
def test_the_loop_rule_says_what_it_wants_and_what_it_refuses():
    # The whole of the fix is in these words: a motion that comes back, not one that comes to rest.
    rule = _loop_rule()

    assert "loop" in rule.lower() and "comes back to the first pose" in rule
    assert "shows as a stop each time the video starts again" in rule
```

`test_the_loop_rule_asks_for_one_speed_to_the_end`'in son satırı:
`assert "same speed" in rule and "slows down" in rule`. Altına:

```python
def test_the_loop_rule_holds_the_camera_still():
    """Madde 400: the last frame is the first photo again, so a camera that moved would have to
    come back too -- and its return would show at the seam."""
    rule = _loop_rule()

    assert "The last frame is the first photo again" in rule
    assert "The camera holds a static shot." in rule
```

Dosyanın sonuna:

```python
def test_wan_is_asked_as_before_whatever_else_it_is_handed():
    """The loop hands every writer the frame's photo and scenario -- one call shape -- and grok,
    which reads no picture, is asked exactly what it was asked before. 404 moves WAN."""
    client = FakeClient()

    VideoPromptWriter(client).write({"photo": "kırmızı elbiseli kadın"}, "standard",
                                    source=PHOTO, scene=THRONE)

    assert client.calls == [(VIDEO_INSTRUCTION, "kırmızı elbiseli kadın")]


def test_the_sound_is_asked_as_before_whatever_else_it_is_handed():
    client = FakeClient(answer="fabric rustling")

    AudioPromptWriter(client).write({"photo": "kırmızı elbiseli kadın", "video": "kadın dönüyor"},
                                    "standard", source=("P0_0_V1_0.mp4", b"MP4"), scene=THRONE)

    assert client.calls == [
        (AUDIO_INSTRUCTION, "Scene: kırmızı elbiseli kadın\nMotion: kadın dönüyor")]
```

## Görev 3: `queen-editor/backend/tests/test_photo_usecases.py`

`FakeWriter`:

```python
    def __init__(self, answer="kadın başını yavaşça çeviriyor", blows_up=None):
        self.answer = answer
        self.blows_up = blows_up
        self.calls = []
        self.modes = []
        # What the writer is shown besides the words (madde 400): the file the layer is made from,
        # and the frame's scenario. Apart for the reason the modes are.
        self.sources = []
        self.scenes = []

    def write(self, prompts, mode="standard", source=None, scene=""):
        self.calls.append(prompts)
        # Kept apart from the words: which mode a job is in is a different question, and one list
        # holding both could not answer either (madde 307).
        self.modes.append(mode)
        self.sources.append(source)
        self.scenes.append(scene)
        if self.blows_up:
            raise self.blows_up
        return self.answer
```

`test_a_model_that_will_not_answer_stops_the_run`'ın altına:

```python
# Madde 400: Queen AI writes H3's prompt looking at the photo and reading the frame's scenario.
THRONE = "Kraliçe tahtında oturuyor; salon boş ve karanlık."
GARDEN = "Kraliçe gece bahçede yürüyor, fenerler yanıyor."


def test_the_writer_sees_the_photo_the_video_is_made_from():
    store, record, plan_store = video_job_project(prompt="kırmızı elbiseli kadın")
    store.files["0_a.png"] = b"PNGDATA"
    writer = FakeWriter()

    resume_batch(sync_runner(), store, record, plan_store, {layers.VIDEO: FakeGenerator()},
                 lambda: "t", "düğün", writers={layers.VIDEO: writer})

    assert writer.sources == [("0_a.png", b"PNGDATA")]


def test_the_writer_is_handed_the_frame_s_scene_by_its_prompt_s_number():
    """397 wrote the scene on the photo lines the list opened, and the gallery finds it by the
    prompt's number. The writer is handed that same one, and never another prompt's."""
    store, record = FakeStore(), FakeRecord()
    plan_store = FakePlanStore(frames=[
        {**frame(0, prompt="taht"), "scene": THRONE},
        {**frame(1, prompt="bahçe"), "scene": GARDEN},
        {"id": "1_a", "type": "video", "number": 1, "variant": 0, "prompt": "",
         "negative": "", "seed": None, "model": ""},
    ])
    for number, prompt in ((0, "taht"), (1, "bahçe")):
        record.append("düğün", {"file": f"{number}_a.png", "frame": f"{number}_a",
                                "layer": "photo", "status": "done", "prompt": prompt})
    writer = FakeWriter()

    resume_batch(sync_runner(), store, record, plan_store, {layers.VIDEO: FakeGenerator()},
                 lambda: "t", "düğün", writers={layers.VIDEO: writer})

    assert writer.scenes == [GARDEN]


def test_a_twin_is_handed_its_source_s_scene():
    """A twin holds its source's picture, so the scene is that picture's -- found by the number,
    never copied onto the twin's own line."""
    store, record = FakeStore(), FakeRecord()
    plan_store = FakePlanStore(frames=[
        {"id": "P0_0", "type": "photo", "number": 0, "variant": 0, "prompt": "taht",
         "scene": THRONE, "negative": "", "seed": 1, "model": ""},
        {"id": "C1_P0_0", "type": "video", "number": 0, "variant": 0, "prompt": "",
         "negative": "", "seed": None, "model": ""},
    ])
    for fid in ("P0_0", "C1_P0_0"):
        record.append("düğün", {"file": "P0_0.png", "frame": fid, "layer": "photo",
                                "status": "done", "prompt": "taht"})
    writer = FakeWriter()

    resume_batch(sync_runner(), store, record, plan_store, {layers.VIDEO: FakeGenerator()},
                 lambda: "t", "düğün", writers={layers.VIDEO: writer})

    assert writer.scenes == [THRONE]


def test_a_frame_from_the_flat_list_is_handed_no_scene():
    store, record, plan_store = video_job_project(prompt="kırmızı elbiseli kadın")
    writer = FakeWriter()

    resume_batch(sync_runner(), store, record, plan_store, {layers.VIDEO: FakeGenerator()},
                 lambda: "t", "düğün", writers={layers.VIDEO: writer})

    assert writer.scenes == [""]
```

## Görev 4: `queen-editor/backend/tests/test_composition_root.py`

İçe aktarmalara `from backend.features.photo_generation.domain import layers`; dosyanın sonuna:

```python
PHOTO = ("P0_0.png", b"PNG")


def _refusal(main, kind):
    """What the session's writer for `kind` says with no key -- the sentence of the model it would
    have asked. No request leaves: a missing key is refused before one is built."""
    with pytest.raises(RuntimeError) as refused:
        main._writers[kind].write({"photo": "kırmızı elbiseli kadın", "video": "kadın dönüyor"},
                                  "standard", source=PHOTO, scene="")
    return str(refused.value)


def test_an_h3_session_s_video_prompt_is_queen_ai_s(import_main, monkeypatch):
    """Madde 400: DeepSeek writes H3's prompt, looking at the photo."""
    monkeypatch.setenv("QE_DEEPSEEK_API_KEY", "")
    main = import_main("h3")

    assert "DEEPSEEK_API_KEY" in _refusal(main, layers.VIDEO)


def test_a_wan_session_s_video_prompt_is_still_grok_s(import_main, monkeypatch):
    """404 moves WAN to Queen AI; until then grok writes it, as today."""
    monkeypatch.setenv("QE_XAI_API_KEY", "")
    main = import_main("")

    assert "XAI_API_KEY" in _refusal(main, layers.VIDEO)


def test_an_h3_session_s_sound_prompt_is_still_grok_s(import_main, monkeypatch):
    monkeypatch.setenv("QE_XAI_API_KEY", "")
    main = import_main("h3")

    assert "XAI_API_KEY" in _refusal(main, layers.AUDIO)


def test_the_deepseek_key_comes_from_the_environment(import_main, monkeypatch):
    """The notebook hands it over as QE_DEEPSEEK_API_KEY, the way every setting of this app
    travels. The model and its address are DeepSeek's own, the ones QueenAgent speaks to."""
    monkeypatch.setenv("QE_DEEPSEEK_API_KEY", "ds-1")
    import_main("h3")

    assert config.DEEPSEEK_API_KEY == "ds-1"
    assert config.DEEPSEEK_MODEL == "deepseek-flash"
    assert config.DEEPSEEK_URL == "https://api.deepseek.com/chat/completions"
```

`monkeypatch` `import_main`'den sonra istendiği için önce o sökülür: ortam eski hâline döner, sonra
`import_main` config'i yeniden okur.

## Görev 5: `queen-editor/backend/tests/test_notebook_installs_the_producer_groups.py`

`test_the_key_is_trimmed_where_it_is_read`'in altına:

```python
def test_the_deepseek_key_is_read_from_secrets_and_trimmed():
    """Madde 400: Queen AI writes H3's prompt. The secret is QueenAgent's own name, so the owner
    keeps one secret for both tools -- trimmed where it is pasted, like the xAI key."""
    assert 'DEEPSEEK_API_KEY = (userdata.get("DEEPSEEK_API_KEY") or "").strip()' in _source(), \
        "DeepSeek anahtarı Secrets'tan kırpılarak okunmuyor"


def test_the_deepseek_key_travels_to_the_app():
    assert '"QE_DEEPSEEK_API_KEY": DEEPSEEK_API_KEY' in _cell("# === Start Flask"), \
        "Defter DeepSeek anahtarını uygulamaya geçirmiyor"


def test_the_setup_names_the_deepseek_secret():
    """Colab hands a secret only to the notebooks it was opened to, so the person setting up has to
    know its name."""
    assert "DEEPSEEK_API_KEY" in _cell("🔑 Secrets"), \
        "Kurulum anlatımı DeepSeek secret'ını saymıyor"
```

## Görev 6: Koşu ve kırmızı commit

- [ ] Dört satır paralel, yazıldığı gibi *(CLAUDE.md, Commands)*.
- [ ] Beklenen: `queen-editor` pytest'inde kırmızı — Görev 1'in dokuzu *(modül yok)*; Görev 2'nin yeni
      ve değişen H3 testleri *(`source` bilinmeyen argüman, eski metin)*, Loop'un üç testi *(eski
      metin)*, WAN'ın ve sesin iki testi *(bilinmeyen argüman)*; Görev 3'ün ilk üçü *(yazar fotoğrafı
      ve senaryoyu almıyor)* — dördüncüsü bekçi, yeşil; Görev 4'ün dördü; Görev 5'in üçü. Üç bölüm
      testi, `test_wan_asks_for_the_same_returning_motion` ve bütün eski döngü testleri yeşil.
      Öteki üç satır yeşil.
- [ ] Spec, plan ve beş test dosyası tek commit'te: `test(queen-editor): Madde 400 red -- …`.
