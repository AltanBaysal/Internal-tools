# Queen Editor v5 · Görev 21 — Ses prompt'unu dil modeli yazar · Uygulama planı

> Tasarım: [Görev 21 spec](../specs/2026-08-12-queen-editor-v5-gorev-21-ses-prompt-design.md).
> Önce kırmızı test, sonra en küçük kod.

**Hedef:** ses işinin prompt'u, karenin foto ve video prompt'undan dil modeli tarafından yazılsın.

**Mimari:** Görev 16'nın yazıcı portu ve motoru olduğu gibi duruyor; eklenecek olan ikinci bir
yazıcı sınıfı ve onun talimatı.

## Genel kısıtlar

- Kod/yorum/test **İngilizce**; talimat metni İngilizce (modele yazılır, ekrana değil).
- Test komutları (birebir): `python -m pytest queen-editor -q` ·
  `npm test --prefix queen-editor/frontend -- --run`

---

## Görev 1 — Ses yazıcısı

**Dosyalar:** `data/xai_prompt_writer.py`, test: `tests/test_video_prompt_writer.py`

- [ ] **Adım 1 — kırmızı testler (aynı test dosyasına, ses için ikinci bir describe):**

```python
def test_the_sound_is_written_from_both_prompts():
    client = FakeClient(answer="fabric rustling, footsteps on stone")

    written = AudioPromptWriter(client).write({"photo": "kırmızı elbiseli kadın",
                                              "video": "kadın başını çeviriyor"})

    assert written == "fabric rustling, footsteps on stone"
    instruction, said = client.calls[0]
    assert instruction == AUDIO_INSTRUCTION
    # Both, labelled: the model has to know which is the scene and which is the motion.
    assert "kırmızı elbiseli kadın" in said and "kadın başını çeviriyor" in said
    assert said.index("kırmızı elbiseli kadın") < said.index("kadın başını çeviriyor")


def test_a_frame_with_no_video_prompt_still_sends_what_it_has():
    client = FakeClient()

    AudioPromptWriter(client).write({"photo": "kırmızı elbiseli kadın"})

    assert "kırmızı elbiseli kadın" in client.calls[0][1]


def test_the_sound_instruction_asks_for_the_scenes_own_sounds():
    assert "no music" in AUDIO_INSTRUCTION
    assert "no speech" in AUDIO_INSTRUCTION
```

- [ ] **Adım 2:** `python -m pytest queen-editor -q` → ImportError.

- [ ] **Adım 3 — `xai_prompt_writer.py`:** var olan `INSTRUCTION` sabiti `VIDEO_INSTRUCTION` olur
(geriye dönük kullanan tek yer kendi testi), yanına ses talimatı ve sınıfı:

```python
# Ours, not inherited: collab-toolbox asks the user for the sound prompt, so there was no
# instruction to bring over. Written for MMAudio, which reads a short comma-separated list of what
# should be heard.
AUDIO_INSTRUCTION = """
You write the audio prompt for MMAudio, which adds sound to a short silent video clip.

You are given the prompt the still image was generated from (the scene) and the prompt the motion
was generated from (what happens). Write what would be heard.

Follow these rules:

Name the sounds themselves, as a short comma-separated list -- fabric rustling, distant traffic,
water lapping.
Stay with what the scene and the motion imply; invent no event that is not in them.
No music: the scene's own sounds are what is wanted, not a soundtrack.
No speech, no singing, no voice-over: the lips in the video would not match.
Keep it to one line, no more than about fifteen words.

Output only the audio prompt itself, as plain text. No list markers, no quotes, no explanations.
"""


class AudioPromptWriter:
    def __init__(self, client):
        self._client = client

    def write(self, prompts):
        """Sound is made from the whole frame: the scene is in the photo's prompt and what happens
        is in the video's, so both go in one message, each under its own label."""
        said = [f"Scene: {prompts.get('photo', '')}"]
        video = prompts.get("video")
        if video:
            said.append(f"Motion: {video}")
        return self._client.complete(AUDIO_INSTRUCTION, "\n".join(said))
```

`VideoPromptWriter` `VIDEO_INSTRUCTION`'ı kullanır; testteki `INSTRUCTION` adını da güncelle.

- [ ] **Adım 4:** `python -m pytest queen-editor -q` → yeşil.

---

## Görev 2 — Bağlama ve motor testi

**Dosyalar:** `main.py`, test: `tests/test_photo_usecases.py`

- [ ] **Adım 1 — kırmızı test:**

```python
def test_a_sound_job_is_written_from_the_frames_two_prompts():
    store, record, plan_store = video_job_project(prompt="kırmızı elbiseli kadın")
    record.append("düğün", {"file": "0_a_V1_0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done", "prompt": "kadın başını çeviriyor"})
    plan_store.frames.append({"id": "0_a", "type": "audio", "number": 0, "variant": 0,
                              "prompt": "", "negative": "", "seed": None, "model": ""})
    writer = FakeWriter(answer="fabric rustling")

    resume_batch(sync_runner(), store, record, plan_store,
                 {layers.VIDEO: FakeGenerator(), layers.AUDIO: FakeGenerator()},
                 lambda: "t", "düğün", writers={layers.AUDIO: writer})

    assert writer.calls == [{"photo": "kırmızı elbiseli kadın", "video": "kadın başını çeviriyor"}]
```

> `video_job_project` planda bir video işi de bırakıyor; onun da üreticisi verildiği için sıra
> videodan sese geçer.

- [ ] **Adım 2:** `python -m pytest queen-editor -q` → kırmızı ya da yeşil olabilir; kırmızıysa
sebebini oku (motor katman haritasını zaten kullanıyor).

- [ ] **Adım 3 — `main.py`:** `_writers` haritasına ses satırı:

```python
_writers = {layers.VIDEO: VideoPromptWriter(_xai), layers.AUDIO: AudioPromptWriter(_xai)}
```

- [ ] **Adım 4:** `python -m pytest queen-editor -q` → yeşil.

---

## Görev 3 — Tam takım ve commit

- [ ] `python -m pytest queen-editor -q`
- [ ] `npm test --prefix queen-editor/frontend -- --run`
- [ ] commit (ön yüz değişmedi):

```
feat(queen-editor): a sound prompt is written from the whole frame
```
