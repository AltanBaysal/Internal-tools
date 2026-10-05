# Madde 416 — DeepSeek'in kara kutusu, uygulama turunun planı

> **Koşum:** bu oturumda, satır satır, madde 416'nın kendi dalında. Testlere dokunulmaz.

**Hedef:** Test turunun kırmızı testlerini kodla yeşile çevirmek — testlerin anlattığı kadar, fazlası
değil.

**Yaklaşım:** İstemcinin üstünde ayrı bir kutu en çok beş deneme yapar ve bir `Answer` döner;
yazarlar kutuyu sorar ve başarısız cevabı metniyle fırlatır; `main.py` istemciyi kutuya sarar.

**Spec:** [m416 uygulama turu](../specs/2026-10-06-queen-editor-m416-kara-kutu-uygulama-design.md)
· [m416 test turu](../specs/2026-10-06-queen-editor-m416-kara-kutu-testler-design.md)

## Her yere geçerli kurallar

- Kod, yorum, docstring İngilizce; kullanıcının gördüğü metin Türkçe. Yorum neden'i söyler.
- CODE-STANDARD: kutu bir servis, hiçbir özelliği bilmez; yazar (`data/`) servisi kullanır; somut
  sınıflar yalnız `main.py`'de birleşir.
- Hata metni servisin kendi sözü; sebep uydurulmaz.
- `main.py`'de yalnız DeepSeek'in kurulduğu satırlar; dosyanın sonu 417'nin.

---

## Görev 1: `services/deepseek/box.py` — yeni; `client.py`'nin belgesi

**Dosyalar:** Oluştur: `queen-editor/backend/services/deepseek/box.py`. Değiştir:
`queen-editor/backend/services/deepseek/client.py` (modül belgesi).

**Üretir:** `TRIES = 5`; `Answer(text: str, failed: bool = False)`;
`Box(client).ask(system, text="", images=()) -> Answer`.

- [ ] **Adım 1: `box.py`'nin tamamı.**

```python
"""The black box every request to Queen AI goes through (madde 416).

The caller asks once and always gets an Answer back, never an exception. A request that came back
with an HTTP error, a malformed or an empty answer, or no answer at all is sent again as it was, up
to five tries in all; when every try failed, the Answer is the last error's own text, marked as a
failure. It never raises because a caller that loops -- an agent -- must not be broken by the
service (v9-3): what to do with the failure is the caller's call.

What one try is lives in client.py; this file decides how many there are and what comes back.
"""
from dataclasses import dataclass

TRIES = 5


@dataclass(frozen=True)
class Answer:
    """The model's text, or -- when `failed` -- why the box gave up, in the service's own words."""

    text: str
    failed: bool = False


class Box:
    def __init__(self, client):
        self._client = client

    def ask(self, system, text="", images=()):
        """The client's question, asked until it is answered or five tries have failed.

        Every failure is tried again, a missing key included: the client refuses that one before
        anything is sent, so its tries cost nothing, and one rule is simpler than a list of the
        exceptions worth a second try.
        """
        for _ in range(TRIES):
            try:
                return Answer(self._client.complete(system, text, images))
            except Exception as exc:
                said = str(exc)
        return Answer(said, failed=True)
```

- [ ] **Adım 2: `client.py`'nin modül belgesi.**

```python
"""DeepSeek chat transport -- an instruction, words and pictures in, the answer's text back.

One request, and a failure raised in the server's own words; sending it again is box.py's. Knows
nothing about video, prompts or frames: what to ask is the caller's business (see
features/photo_generation/data/prompt_writer.py). `http` is injected so tests need no network.
"""
```

## Görev 2: `data/prompt_writer.py`

**Dosya:** Değiştir: `queen-editor/backend/features/photo_generation/data/prompt_writer.py`

**Tüketir:** Görev 1'in `Box.ask` ve `Answer.text` / `Answer.failed`.

- [ ] **Adım 1: Modül belgesinin ikinci paragrafı.**

```python
"""What the language model is asked when a job needs a prompt nobody typed.

Every writer asks Queen AI -- DeepSeek -- through the box in services/deepseek/box.py, which sends a
failed request again (madde 416). A video's writer is shown the frame's photo and reads its scenario
(madde 400, 404), and H3's is shown the next frame's photo too for a linked video (402); the sound's
writer reads the video's prompt alone (404). Each prompt is its own ask. This file only decides what
to say.
"""
```

- [ ] **Adım 2: `_prompt`** — `_scenario`'nun altına:

```python
def _prompt(answer):
    """The box's answer as the prompt. A failure is raised instead, in the box's own words, so it
    takes the path every failed ask takes -- the run loop's three attempts, then the error line --
    and is never written on the card (madde 416)."""
    if answer.failed:
        raise RuntimeError(answer.text)
    return answer.text
```

- [ ] **Adım 3: Üç yazar kutuyu sorar.**

```python
class VideoPromptWriter:
    def __init__(self, queen_ai):
        self._queen_ai = queen_ai

    def write(...):
        ...
        return _prompt(self._queen_ai.ask(asked(VIDEO_INSTRUCTION, mode) + SYSTEM_PROMPT_SUFFIX,
                                          _scenario(scene), [source]))


class H3VideoPromptWriter:
    def __init__(self, queen_ai):
        self._queen_ai = queen_ai

    def write(...):
        ...
        return _prompt(self._queen_ai.ask(instruction + SYSTEM_PROMPT_SUFFIX, _scenario(scene),
                                          pictures))


class AudioPromptWriter:
    def __init__(self, queen_ai):
        self._queen_ai = queen_ai

    def write(...):
        ...
        return _prompt(self._queen_ai.ask(AUDIO_INSTRUCTION + SYSTEM_PROMPT_SUFFIX,
                                          f"Video prompt: {prompts.get('video', '')}"))
```

Docstring'ler ve `write`'ların geri kalanı aynen.

## Görev 3: `main.py` — DeepSeek'in kurulduğu satırlar

**Dosya:** Değiştir: `queen-editor/backend/main.py:91` ve `:106-109`

- [ ] **Adım 1: İçe aktarma** — `from backend.services.deepseek.client import DeepSeekClient`'in
  üstüne, servislerin alfabe sırasıyla: `from backend.services.deepseek.box import Box`.

- [ ] **Adım 2: Kurulum.**

```python
# Queen AI writes every prompt nobody typed (madde 400, 404): a video's looking at the frame's
# photo, a sound's from its video's prompt. Every ask goes through the box, which sends a failed
# request again (madde 416).
_queen_ai = Box(DeepSeekClient(config.DEEPSEEK_API_KEY, config.DEEPSEEK_MODEL,
                               config.DEEPSEEK_URL, timeout=config.DEEPSEEK_TIMEOUT))
```

## Görev 4: Koşu — yeşil, commit

- [ ] **Adım 1: Dört satır**, paralel, yazıldığı gibi:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: iki pytest satırı yeşil. İki vitest satırı bu çalışma ağacında başlayamaz — `node_modules`
yok; bu madde ekrana dokunmuyor.

**Koşuldu:** queen-editor `1305 passed` · queen-agent `989 passed` · iki vitest satırı:
`'vitest' is not recognized`.

- [ ] **Adım 2:** Fark FOUNDATION, CODE-STANDARD ve *Bitti sayılır*'a karşı okunur.

- [ ] **Adım 3: Commit** — kod, uygulama spec'i ve bu plan:

```powershell
git add queen-editor/backend/services/deepseek/box.py queen-editor/backend/services/deepseek/client.py queen-editor/backend/features/photo_generation/data/prompt_writer.py queen-editor/backend/main.py docs/superpowers/specs/2026-10-06-queen-editor-m416-kara-kutu-uygulama-design.md docs/superpowers/plans/2026-10-06-queen-editor-m416-kara-kutu-uygulama-plan.md
git commit -m @'
feat(queen-editor): 416 -- every Queen AI request goes through a box in services/deepseek: it sends a failed request again, five tries at most, and then returns the last error's own text marked as a failure instead of raising; the prompt writers raise that text into the run loop's own three attempts, so a failing run stops as today after fifteen requests with the box's text on the error line

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
