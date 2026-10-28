# Madde 400 — H3 prompt'unu Queen AI yazar, uygulama turunun planı

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*.

**Hedef:** Test turunun kırmızı testleri yeşil; bugünkü testler yeşil kalıyor.

**Mimari:** Yeni servis `services/deepseek/`; yazar portu `source` ve `scene` alıyor; senaryo kuralı
`domain/scene.py`'de tek yerde; main.py H3 yazarını DeepSeek'e bağlıyor; defter anahtarı geçiriyor.

**Spec:** [m400 uygulama turu](../specs/2026-10-01-queen-editor-m400-h3-queen-ai-uygulama-design.md) ·
[test turu](../specs/2026-10-01-queen-editor-m400-h3-queen-ai-testler-design.md)

## Her yere geçerli kurallar

- Kod ve yorum İngilizce; çalışırken görünen cümleler Türkçe. Yorum NEDEN'i ve bugün doğru olanı
  söyler; satırlar 100 karakteri geçmez — metinlerin kendisi hariç: onlar olduğu gibi.
- İki metin `D:\Github\Internal-tools\tmp\queen-editor-prompts.md`'den kelimesi kelimesine; testler
  değişmez.
- Defter JSON metni olarak düzenlenir; hücrelerde yorum yok.

---

## Görev 1: Taşıyıcı

**Yeni:** `queen-editor/backend/services/deepseek/__init__.py` *(boş, `xai/`'ınki gibi)* ve
`queen-editor/backend/services/deepseek/client.py`:

```python
"""DeepSeek chat transport -- an instruction, words and pictures in, the answer's text back.

Knows nothing about video, prompts or frames: what to ask is the caller's business (see
features/photo_generation/data/xai_prompt_writer.py). `http` is injected so tests need no network.
"""
import base64
import mimetypes

import requests


class NotConfigured(RuntimeError):
    """No API key on this machine (message is user-facing)."""


def _picture(name, data):
    """One picture as a message part: a data URL, because the file is on this machine and no link
    could point at it. Its type is read off its name."""
    media_type = mimetypes.guess_type(name)[0]
    return {"type": "image_url",
            "image_url": {"url": f"data:{media_type};base64,{base64.b64encode(data).decode()}"}}


class DeepSeekClient:
    def __init__(self, api_key, model, url, http=requests, timeout=120):
        # Trimmed here because this is what builds the header: a key pasted with a trailing
        # newline would otherwise travel as `Bearer sk-...\n`. It also turns a key of nothing but
        # spaces into no key at all, so the sentence written for a missing key is the one the user
        # gets.
        self._api_key = (api_key or "").strip()
        self._model = model
        self._url = url
        self._http = http
        self._timeout = timeout

    def complete(self, system, text="", images=()):
        """One system message + one user message of pictures and words -> the answer's text.

        `images` is [(name, bytes)]. They ride in the user message alone: DeepSeek answers 400 to a
        picture in the system message. No words means no text part at all, rather than an empty one.
        """
        if not self._api_key:
            raise NotConfigured(
                "DEEPSEEK_API_KEY yok — Colab Secrets'a ekle ve notebook erişimini aç")
        said = [_picture(name, data) for name, data in images]
        if text:
            said.append({"type": "text", "text": text})
        response = self._http.post(
            self._url,
            headers={"Authorization": f"Bearer {self._api_key}",
                     "Content-Type": "application/json"},
            json={"model": self._model,
                  "messages": [{"role": "system", "content": system},
                               {"role": "user", "content": said}]},
            timeout=self._timeout,
        )
        if response.status_code >= 400:
            # The server's own body, never a guessed cause: a refusal can be the picture, the model
            # name, the key or the balance, and only the body knows which.
            raise RuntimeError(f"DeepSeek HTTP {response.status_code}\n{response.text}")
        try:
            answer = response.json()["choices"][0]["message"]["content"].strip()
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"DeepSeek cevabı beklenen biçimde değil ({type(exc).__name__})\n"
                               f"{response.text}") from None
        if not answer:
            raise RuntimeError(f"DeepSeek boş cevap döndü:\n{response.text}")
        return answer
```

## Görev 2: Ayar — `queen-editor/backend/config.py`, xAI bloğunun altına

```python

# Queen AI: the model that writes H3's video prompt looking at the frame's photo (madde 400). The key
# comes from Colab Secrets through the notebook, under the name QueenAgent's notebook reads too;
# without one the app still starts, and only an H3 video job's turn stops the run with the client's
# own sentence.
DEEPSEEK_API_KEY = os.environ.get("QE_DEEPSEEK_API_KEY", "")
# Not read from the environment, unlike xAI's two: those travel so the notebook's key probe asks
# exactly what the app asks, and nothing probes DeepSeek.
DEEPSEEK_MODEL = "deepseek-flash"
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_TIMEOUT = 120     # seconds per request; one prompt is a short answer
```

## Görev 3: Port — `domain/ports.py`, `PromptWriter`

```python
class PromptWriter(Protocol):
    def write(self, prompts: dict, mode: str, source: tuple | None = None,
              scene: str = "") -> str:
        """The prompt a job of this type should be produced with.

        `prompts` is what the frame already says: {"photo": …} today, plus the video's own when
        audio joins. Raising is a failure like any other -- the loop's three attempts and its
        frame-fault rule apply to it unchanged.

        `mode` is how the job is being produced (domain/production_mode.py). A loop video has to be
        asked for a motion that returns (madde 307); a sound takes the argument and ignores it, the
        way every producer takes `references`.

        `source` is the file the layer is made from as (name, bytes) -- the one its producer is
        handed -- and `scene` is the frame's scenario, empty for a frame that has none. H3's writer
        shows the model both (madde 400); the others take them and ignore them, for the same one
        call shape.
        """
        ...
```

## Görev 4: Senaryo — yeni `domain/scene.py`, ve `list_frames`

```python
"""A frame's scenario: what QueenAgent's list says happens in the prompt's frames (madde 397).

Found by the prompt's number rather than written on each frame. Every card holding the prompt's
picture carries that number -- a video's variant, a twin, a card whose photo was deleted
(photo_name._parts) -- so one scene answers for the family without being copied onto each of them.
Two readers ask: the gallery, which shows it, and the queue, which hands it to the prompt writer
(madde 400).
"""
from backend.features.photo_generation.domain.photo_name import number_of


def by_number(planned):
    """{prompt number: scene}, read off the plan lines that carry one."""
    return {frame["number"]: frame["scene"] for frame in planned if frame.get("scene")}


def of(found, fid):
    """The frame's scene out of by_number's answer; empty for a frame that has none."""
    return found.get(number_of(fid), "")
```

`list_frames.py`: içe aktarma `from backend.features.photo_generation.domain import layers, queue,
scene` ve `from backend.features.photo_generation.domain.photo_name import photo_file`
*(`number_of` başka yerde kullanılmıyor)*. Sözlüğün dört satırlık yorumu ve kendisi:

```python
    # What each prompt's frames were written from (madde 397): one scene per prompt, found by its
    # number (domain/scene.py).
    scenes = scene.by_number(planned)
```

Kartta: `"scene": scene.of(scenes, fid),`.

## Görev 5: Döngü — `domain/run_loop.py`

İçe aktarma: `layers, policy, production_mode, queue, scene, seed`. `try`'ın başı:

```python
            try:
                # Held in a variable because it is asked for more than once: the writer is shown the
                # file the layer is made from, the producer makes the layer from it, and a loop ends
                # on it too. Reading it again would be the same download from Drive.
                under = _source_for(kind, store, slots, project, fid)
                writer = (writers or {}).get(kind)
                if writer and not current["prompt"] and written is None:
                    # (bugünkü yorum aynen)
                    words = _prompts_of(record, project, fid)
                    # Nothing to convert: asking would buy an invented prompt. I2V sees the picture
                    # itself, so producing with an empty prompt is a real answer here.
                    if any(words.values()):
                        # The mode goes with the words: a loop video has to be asked for a motion
                        # that returns, and the frame's own prompts cannot say that (madde 307). The
                        # picture and the scenario go too: H3's writer looks at the one and reads the
                        # other (madde 400).
                        written = writer.write(words, production_mode.of(current), source=under,
                                               scene=scene.of(scene.by_number(jobs), fid))
                prompt = current["prompt"] or written or ""
```

Eski `under = _source_for(...)` satırı ve üstündeki iki satırlık yorum silinir; `pool` ve `ending`
olduğu gibi.

## Görev 6: Yazarlar — `data/xai_prompt_writer.py`

- Modülün docstring'inin son paragrafı:

```
Two transports, one per model: H3's writer talks to Queen AI -- DeepSeek, services/deepseek/ -- and
shows it the frame's photo (madde 400); WAN's and the sound's talk to xAI, services/xai/. This file
only decides what to say.
```

- `H3_VIDEO_INSTRUCTION`: "H3 (400)" bölümü, `"""` + satır sonu + metin + satır sonu + `"""`. Yorumu:

```python
# Written for MiniMax H3 (madde 243), whose prompt is sectioned and whose sound comes out of the same
# pass as the picture -- so the soundscape is this writer's too. Queen AI reads it with the frame's
# photo in front of it and the frame's scenario beside it (madde 400). Claude wrote the words on
# 2026-10-01 and the user reads them afterwards (v8 roadmap). The line saying which picture sits
# where is not asked for: the producer writes it, because it is the graph's fact rather than the
# scene's. dynv2, the word that wakes the Motion Booster lora, is not asked for either: the user adds
# it by hand to the prompts that want it (madde 331), and the producer moves it in front (246).
```

- `LOOP_RULE`: "Loop" bölümü, aynı biçimde. Yorumu bugünkü dört paragraf *(ilk cümlede "One text for
  both")* ve sonuna:

```python
#
# The camera holds still (madde 400): the last frame is the first photo again, so a camera that
# moved would have to travel back, and the return would show at the seam.
```

- `VideoPromptWriter.write(self, prompts, mode=production_mode.STANDARD, source=None, scene="")`,
  docstring'ine: "`source` and `scene` are taken and ignored: grok is asked the photo's words alone,
  and the queue has one call shape for every writer."
- `H3VideoPromptWriter`:

```python
    def write(self, prompts, mode=production_mode.STANDARD, source=None, scene=""):
        """Queen AI is shown the photo the video starts from and reads the frame's scenario
        (madde 400). The photo's own words are not sent: the model sees the picture they drew.

        A linked video is asked what a plain one is -- asked() adds words for a loop alone.
        """
        return self._client.complete(asked(H3_VIDEO_INSTRUCTION, mode),
                                     f"Scenario: {scene}" if scene else "", [source])
```

- `AudioPromptWriter.write(self, prompts, mode=production_mode.STANDARD, source=None, scene="")`;
  docstring'in ikinci paragrafı: "`mode` is a video's business -- a sound is laid over the whole of
  one however it was made. It is taken and ignored, like `source` and `scene`, because the queue has
  one call shape for every writer."

## Görev 7: Kompozisyon kökü — `backend/main.py`

```python
from backend.services.deepseek.client import DeepSeekClient
```

```python
# grok writes WAN's video prompt and every sound's.
_xai = XaiClient(config.XAI_API_KEY, config.XAI_MODEL, config.XAI_URL, timeout=config.XAI_TIMEOUT)
# One video model per session (madde 243): the notebook installs WAN or H3, never both, and says
# which. Each comes with the writer that knows its prompt; H3's is Queen AI, which looks at the
# photo (madde 400).
if config.VIDEO_MODEL == "h3":
    _video_generator = ComfyH3VideoGenerator(_comfy_client, config.H3_VIDEO_WORKFLOW_PATH,
                                             config.H3_VIDEO_FIRST_LAST_WORKFLOW_PATH,
                                             config.VIDEO_TIMEOUT)
    _video_writer = H3VideoPromptWriter(DeepSeekClient(config.DEEPSEEK_API_KEY,
                                                       config.DEEPSEEK_MODEL, config.DEEPSEEK_URL,
                                                       timeout=config.DEEPSEEK_TIMEOUT))
else:
    _video_generator = ComfyVideoGenerator(_comfy_client, config.VIDEO_WORKFLOW_PATH,
                                           config.VIDEO_FIRST_LAST_WORKFLOW_PATH,
                                           config.VIDEO_TIMEOUT)
    _video_writer = VideoPromptWriter(_xai)
```

Aşağıda: `# Who writes a job's prompt when it carries none. Photo has no writer: its prompt is the
user's own.` ve `_writers = {layers.VIDEO: _video_writer, layers.AUDIO: AudioPromptWriter(_xai)}`.

## Görev 8: Defter ve README

`queeneditor.ipynb`, JSON metni:
- Anlatım: `video için \`XAI_API_KEY\` (video prompt'unu yazan dil modeli).` →
  `H3 için \`DEEPSEEK_API_KEY\` (H3 prompt'unu yazan Queen AI — QueenAgent'ınkiyle aynı secret); WAN ve
  ses için \`XAI_API_KEY\` (onların prompt'unu yazan dil modeli).`
- CONFIG, `XAI_API_KEY`'in `try`'ının altına:
  `try:\n    DEEPSEEK_API_KEY = (userdata.get("DEEPSEEK_API_KEY") or "").strip()\nexcept Exception:\n    DEEPSEEK_API_KEY = ""\n\n`
- Flask: `"QE_XAI_API_KEY": XAI_API_KEY or "",` satırının altına
  `"QE_DEEPSEEK_API_KEY": DEEPSEEK_API_KEY,`.

`README.md`'nin Secrets tablosu:

```
| `DEEPSEEK_API_KEY` | H3 only: an H3 video's prompt is written by DeepSeek, which is shown the frame's photo. The same secret QueenAgent's notebook reads — open its notebook access for this notebook too. Without it photos still render and an H3 video job stops with the client's own sentence. |
| `XAI_API_KEY` | A WAN video's prompt and every sound's prompt are written by xAI when the job's turn comes. Without it photos still render and such a job stops with the client's own sentence. |
```

## Görev 9: Koşu, doğrulama, commit

- [ ] Dört satır paralel, yazıldığı gibi. Beklenen: hepsi yeşil.
- [ ] İki metin dosyayla karşılaştırılır: `tmp/queen-editor-prompts.md`'nin 5–34. ve 38–41. satırları,
      `xai_prompt_writer.py`'deki iki üç tırnağın içiyle `diff`'te fark yok.
- [ ] Spec, plan ve kod tek commit'te: `feat(queen-editor): 400 -- …`. Dist yok: ekran değişmedi.
