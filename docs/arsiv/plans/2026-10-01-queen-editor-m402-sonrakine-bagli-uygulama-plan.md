# Madde 402 — Sonrakine bağlı karede geçiş yumuşar, uygulama turunun planı

> **Koşum:** bu oturumda, satır satır.

**Hedef:** Test turunun kırmızı dokuz testini yeşile çevirmek.

**Mimari:** Port `end`'i alır; döngü vardığı resmi yazardan önce bir kez okur ve yazara da verir; H3
yazarı bağlı videoda iki resmi gösterir ve `LINKED_RULE`'u ekler.

**Spec:** [m402 uygulama turu](../specs/2026-10-01-queen-editor-m402-sonrakine-bagli-uygulama-design.md)

## Her yere geçerli kurallar

- Kod ve yorum İngilizce; yorum NEDEN'i ve yalnız bugün doğru olanı söyler.
- `LINKED_RULE` `D:\Github\Internal-tools\tmp\queen-editor-prompts.md`'nin "Sonrakine bağlı kare (402 —
  H3'e eklenir)" bölümü, kelimesi kelimesine — `…` karakteri dahil.
- Testlere dokunulmaz.

---

## Görev 1: Port — `queen-editor/backend/features/photo_generation/domain/ports.py`

```python
class PromptWriter(Protocol):
    def write(self, prompts: dict, mode: str, source: tuple | None = None,
              end: tuple | None = None, scene: str = "") -> str:
```

Docstring'e: `end` videonun vardığı resim, üreticinin aldığı `end`'in kendisi, yoksa None; H3'ün yazarı
bağlı videoda onu da gösterir (madde 402), ötekiler alır ve yok sayar.

## Görev 2: Yazarlar — `queen-editor/backend/features/photo_generation/data/xai_prompt_writer.py`

`LOOP_RULE`'un altına, yorumuyla:

```python
# What a linked video's prompt has to ask for, appended to H3's instruction alone (madde 402). The
# model is shown the next frame's photo and asked for the way there in detail: a video written only
# from where it starts reaches the next frame like a seam, and a transition written out is what the
# video model follows. The text names Picture 2 and WAN's writer is shown no picture, so it is H3's.
LINKED_RULE = """
This video ends on the photo of the next frame. …(dosyadaki bölüm, kelimesi kelimesine)…
"""
```

`H3VideoPromptWriter.write`:

```python
    def write(self, prompts, mode=production_mode.STANDARD, source=None, end=None, scene=""):
        instruction, pictures = asked(H3_VIDEO_INSTRUCTION, mode), [source]
        if mode == production_mode.LINKED:
            instruction, pictures = instruction + LINKED_RULE, [source, end]
        return self._client.complete(instruction, f"Scenario: {scene}" if scene else "", pictures)
```

`VideoPromptWriter.write` ve `AudioPromptWriter.write` imzaya `end=None` alır, gövdeleri aynı;
docstring'leri `end`'i de yok saydıklarını söyler. Modülün docstring'i H3 yazarının bağlı videoda
sonraki karenin fotoğrafını da gösterdiğini söyler.

## Görev 3: Döngü — `queen-editor/backend/features/photo_generation/domain/run_loop.py`

`under`'ın altına:

```python
                under = _source_for(kind, store, slots, project, fid)
                ending = _end_for(current, store, slots, project, fid, under)
```

Yazarın çağrısı:

```python
                        written = writer.write(words, production_mode.of(current), source=under,
                                               end=ending,
                                               scene=scene.of(scene.by_number(jobs), fid))
```

Üreticinin önündeki eski `ending = _end_for(…)` satırı ve yorumu kalkar; `under` ve `ending`'in
üstündeki yorumlar ikisinin de yazara ve üreticiye gittiğini, `ending`'in yazardan önce bulunduğu için
kaybolmuş bir hedefin istek harcatmadığını söyler.

## Görev 4: Koşu ve commit

- [ ] Dört satır paralel, yazıldığı gibi.
- [ ] Beklenen: dördü de yeşil.
- [ ] `LINKED_RULE` dosyadaki bölümle karşılaştırılır.
- [ ] Spec, plan ve üç kaynak dosya tek commit'te: `feat(queen-editor): 402 -- …`.
