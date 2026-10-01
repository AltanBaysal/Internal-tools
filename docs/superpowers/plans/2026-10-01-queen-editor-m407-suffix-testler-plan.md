# Madde 407 — Prompt'u yazan modelin system prompt'una suffix, test turu planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Hedef:** Queen AI'ın her yazarının system mesajının QueenAgent'ın suffix'iyle bittiğini, ve Queen
Editor'ün suffix'inin QueenAgent'ınkiyle birebir aynı olduğunu söyleyen testler, kırmızı.

**Mimari:** Queen Editor kendi kopyasını tutacak; testler gönderilen mesajın tamamını "yazarın metni +
modun kuralı + suffix" olarak sorar, ve kopyayı QueenAgent'ın `prompt.py`'sinden yüklenen değerle
karşılaştırır.

**Araçlar:** pytest, `importlib.util`.

**Spec:** [m407 test turu](../specs/2026-10-01-queen-editor-m407-suffix-testler-design.md)

## Genel kısıtlar

- Yalnız testler; kod dosyasına dokunulmaz. QueenAgent'ın hiçbir dosyasına dokunulmaz.
- Değişen tek dosya: `queen-editor/backend/tests/test_video_prompt_writer.py`.
- Kopyanın adı: `prompt_writer.SYSTEM_PROMPT_SUFFIX`.
- QueenAgent'ın dosyası: `queen-agent/backend/features/workspace/domain/prompt.py`, adı
  `SYSTEM_PROMPT_SUFFIX`.
- Test adları ve yorumlar İngilizce; assert mesajları Türkçe.
- Dört satır CLAUDE.md'deki gibi, paralel, borusuz, daraltılmadan.

---

### Görev 1: Yardımcılar

**Dosya:** Değiştir `queen-editor/backend/tests/test_video_prompt_writer.py:1-26`

- [ ] Dosyanın başı:

```python
import importlib.util
import os

from backend.features.photo_generation.data import prompt_writer
from backend.features.photo_generation.data.prompt_writer import (
    AUDIO_INSTRUCTION,
    VIDEO_INSTRUCTION,
    AudioPromptWriter,
    VideoPromptWriter,
)

TOOL = os.path.dirname(          # queen-editor
    os.path.dirname(             # backend
        os.path.dirname(os.path.abspath(__file__))))  # tests
QUEEN_AGENT_PROMPT = os.path.join(os.path.dirname(TOOL), "queen-agent", "backend", "features",
                                  "workspace", "domain", "prompt.py")
```

- [ ] `FakeVisionClient`'ın arkasına iki yardımcı:

```python
def _sent(instruction):
    """What a writer hands Queen AI as its system message: its own text, then the suffix (madde
    407)."""
    return instruction + prompt_writer.SYSTEM_PROMPT_SUFFIX


def _queen_agent_suffix():
    """QueenAgent's suffix, the value QueenAgent sends.

    Its module is loaded rather than parsed, so the value is read however the owner writes it. The
    module imports nothing, by its own rule, so loading it brings nothing else of QueenAgent's here.
    """
    spec = importlib.util.spec_from_file_location("queen_agent_prompt", QUEEN_AGENT_PROMPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.SYSTEM_PROMPT_SUFFIX
```

### Görev 2: Gönderilen mesajın tamamını soran on iki test

**Dosya:** Değiştir `queen-editor/backend/tests/test_video_prompt_writer.py`

Her birinde yalnız beklenen system mesajı `_sent(...)` ile sarılır:

- [ ] `test_the_wan_writer_shows_queen_ai_the_photo_and_the_scenario` →
  `assert client.calls == [(_sent(VIDEO_INSTRUCTION), f"Scenario: {THRONE}", [PHOTO])]`
- [ ] `test_a_wan_frame_with_no_scenario_sends_the_photo_alone` →
  `assert client.calls == [(_sent(VIDEO_INSTRUCTION), "", [PHOTO])]`
- [ ] `test_the_sound_is_written_from_the_video_s_prompt_alone` →
  `assert client.calls == [(_sent(AUDIO_INSTRUCTION), "Video prompt: kadın başını çeviriyor",`
  `[])]` (iki satıra bölünür)
- [ ] `test_the_h3_writer_shows_queen_ai_the_photo_and_the_scenario` →
  `assert client.calls == [(_sent(instruction), f"Scenario: {THRONE}", [PHOTO])]`
- [ ] `test_a_frame_with_no_scenario_sends_the_photo_alone` →
  `assert client.calls == [(_sent(instruction), "", [PHOTO])]`
- [ ] `test_a_loop_video_is_asked_for_a_motion_that_returns` →
  `assert client.calls[0][0] == _sent(instruction + _loop_rule())`
- [ ] `test_a_plain_video_is_asked_for_nothing_extra` → `assert client.calls[0][0] ==
  _sent(instruction)`, üstünde bir yorum satırı: `# The suffix rides on every mode (madde 407); a
  plain video adds no rule of its own.`
- [ ] `test_a_linked_video_shows_queen_ai_both_pictures_in_order` →
  `assert client.calls == [(_sent(instruction + _linked_rule()), f"Scenario: {THRONE}",`
  `[PHOTO, NEXT])]` (iki satıra bölünür)
- [ ] `test_a_loop_video_shows_its_picture_once` →
  `assert client.calls == [(_sent(instruction + _loop_rule()), "", [PHOTO])]`
- [ ] `test_wan_asks_for_the_same_returning_motion` →
  `assert client.calls == [(_sent(VIDEO_INSTRUCTION + _loop_rule()), "", [PHOTO])]`
- [ ] `test_wan_never_hears_of_picture_2` →
  `assert client.calls == [(_sent(VIDEO_INSTRUCTION), f"Scenario: {THRONE}", [PHOTO])]`
- [ ] `test_the_sound_is_shown_no_picture_whatever_it_is_handed` →
  `assert client.calls == [(_sent(AUDIO_INSTRUCTION), "Video prompt: kadın dönüyor", [])]`

### Görev 3: İki yeni test

**Dosya:** Değiştir `queen-editor/backend/tests/test_video_prompt_writer.py` — dosyanın sonuna.

- [ ] Ekle:

```python
def test_the_suffix_is_queen_agent_s_word_for_word():
    """Madde 407: the same text QueenAgent ends its system prompt with -- the user's "evet" (30
    Eylül). A copy, pinned: the owner rewrites QueenAgent's suffix by hand, and this goes red that
    day until the copy follows."""
    assert prompt_writer.SYSTEM_PROMPT_SUFFIX == _queen_agent_suffix(), (
        "Queen Editor'ün suffix'i QueenAgent'ınkiyle aynı değil: queen-agent/backend/features/"
        "workspace/domain/prompt.py'deki SYSTEM_PROMPT_SUFFIX, queen-editor/backend/features/"
        "photo_generation/data/prompt_writer.py'ye aynen kopyalanmalı"
    )


def test_every_writer_s_system_prompt_ends_with_queen_agent_s_suffix():
    """Madde 407, as its done-sentence says it: whichever prompt Queen AI writes -- H3, WAN or the
    sound -- and in whichever mode, the system prompt it is handed ends with QueenAgent's suffix.
    Asked of QueenAgent's text rather than the copy."""
    _instruction, h3 = _h3()
    client = FakeVisionClient()

    for writer in (VideoPromptWriter, h3, AudioPromptWriter):
        for mode in ("standard", "loop", "linked"):
            writer(client).write({"photo": "kırmızı elbiseli kadın", "video": "kadın dönüyor"},
                                 mode, source=PHOTO, end=NEXT, scene=THRONE)

    suffix = _queen_agent_suffix()
    for sent, _words, _pictures in client.calls:
        assert sent.endswith(suffix), f"System prompt suffix'le bitmiyor:\n{sent}"
```

### Görev 4: Kırmızıyı gör ve commit'le

- [ ] Dört satır, paralel:
  `python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend` ·
  `python -m pytest queen-editor -q` · `npm test --prefix queen-editor/frontend`
- [ ] Beklenen: queen-editor pytest'te on dört test kırmızı — `_sent` kullanan on iki ve pin testi
  `AttributeError` (`SYSTEM_PROMPT_SUFFIX` yok), son-ek testi `AssertionError`; dosya toplanıyor.
  Öteki üç satır yeşil.
- [ ] Commit: `test(queen-editor): Madde 407 red -- …`, spec ve plan ile. Mesajda çift tırnak yok;
  son satır `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
