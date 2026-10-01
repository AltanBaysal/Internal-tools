# Madde 404 — WAN'ın ve sesin prompt'unu Queen AI yazar, uygulama turunun planı

> **Koşum:** bu oturumda, satır satır.

**Hedef:** Test turunun kırmızı on beş testini yeşile çevirmek, başka hiçbir şey.

**Mimari:** İki metin değişir, WAN yazarı H3'ünki gibi sorar, ses yazarı yalnız videonun prompt'unu
gönderir *(Görev 1)*; döngünün `_unwritten`'ı sesi videonun prompt'una bağlar *(Görev 2)*; `main.py` üç
yazarı tek Queen AI istemcisine bağlar, README'nin iki Secrets satırı düzelir *(Görev 3)*.

**Spec:** [m404 uygulama turu](../specs/2026-10-01-queen-editor-m404-wan-ve-ses-queen-ai-uygulama-design.md)

## Her yere geçerli kurallar

- Kod ve yorum İngilizce; README İngilizce, kendi dilinde. Yorum NEDEN'i ve şimdi doğru olanı söyler.
- Metinler `D:\Github\Internal-tools\tmp\queen-editor-prompts.md`'den kelimesi kelimesine; yalnız
  okunur. `H3_VIDEO_INSTRUCTION`, `LOOP_RULE`, `LINKED_RULE` değişmez.
- `run_loop.py`'de `_unwritten` ve yeni `_has_words` dışında satır değişmez *(405 aynı dosyada)*.
- dist yok; ekran değişmiyor.

---

## Görev 1: `queen-editor/backend/features/photo_generation/data/xai_prompt_writer.py`

- Modül docstring'i: hangi yazarın hangi taşıyıcıyla konuştuğu — üçü de Queen AI.
- `VIDEO_INSTRUCTION` = "WAN (404)" bölümü; üstündeki yorum: Queen AI fotoğrafı görüp senaryoyu
  okuyarak yazar, ses girmez — sesin kendi prompt'u var.
- `AUDIO_INSTRUCTION` = "Ses — MMAudio (404)" bölümü; yorum: yalnız videonun prompt'undan.
- Yeni yardımcı ve yazarlar:

```python
def _scenario(scene):
    """How both video writers say the frame's scenario: labelled, and nothing at all when there is
    none -- the texts say what to do then."""
    return f"Scenario: {scene}" if scene else ""


class VideoPromptWriter:
    def write(self, prompts, mode=production_mode.STANDARD, source=None, end=None, scene=""):
        return self._client.complete(asked(VIDEO_INSTRUCTION, mode), _scenario(scene), [source])


class AudioPromptWriter:
    def write(self, prompts, mode=production_mode.STANDARD, source=None, end=None, scene=""):
        return self._client.complete(AUDIO_INSTRUCTION, f"Video prompt: {prompts.get('video', '')}")
```

`H3VideoPromptWriter` senaryoyu `_scenario(scene)` ile söyler; başka değişiklik yok.

## Görev 2: `queen-editor/backend/features/photo_generation/domain/run_loop.py`

```python
def _has_words(kind, said):
    """Whether the frame says anything this job's prompt can be written from. A sound is written
    from its video's prompt alone (madde 404), so the photo's words give it nothing; a video is
    written from whatever the frame says."""
    return bool(said.get(layers.VIDEO)) if kind == layers.AUDIO else any(said.values())
```

`_unwritten`'ın son koşulu `_has_words(queue.type_of(job), said.get(job["id"], {}))` olur; docstring'i
sesin videonun prompt'unu beklediğini söyler.

## Görev 3: `queen-editor/backend/main.py` ve `queen-editor/README.md`

```python
# Queen AI writes every prompt nobody typed (madde 400, 404): a video's looking at the frame's photo,
# a sound's from its video's prompt.
_queen_ai = DeepSeekClient(config.DEEPSEEK_API_KEY, config.DEEPSEEK_MODEL, config.DEEPSEEK_URL,
                           timeout=config.DEEPSEEK_TIMEOUT)
```

H3 dalı `H3VideoPromptWriter(_queen_ai)`, WAN dalı `VideoPromptWriter(_queen_ai)`;
`_writers = {layers.VIDEO: _video_writer, layers.AUDIO: AudioPromptWriter(_queen_ai)}`. `_xai` ve
`XaiClient` içe aktarması silinir.

README Secrets: `DEEPSEEK_API_KEY` ve `XAI_API_KEY` satırları spec'in parça 4'ünün söylediğini söyler.

## Görev 4: Doğrulama ve commit

- [ ] İki metin dosyadakiyle karakteri karakterine aynı: `tmp/queen-editor-prompts.md`'nin iki
  bölümünü ve kodu Read ile satır satır karşılaştır.
- [ ] Dört satır, paralel, yazıldığı gibi; hepsi yeşil.
- [ ] Commit: `feat(queen-editor): 404 -- …`
