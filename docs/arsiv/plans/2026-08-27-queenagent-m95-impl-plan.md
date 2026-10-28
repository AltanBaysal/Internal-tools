# Madde 95 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-27-queenagent-m95-prompt-sirasi-uygulama-design.md](../specs/2026-08-27-queenagent-m95-prompt-sirasi-uygulama-design.md)
**Tur 1:** dokuz kırmızı commit'lendi *(`397cb77`)*. Bu turda test yazılmaz.
**Komut:** `python -m pytest queen-agent -q`

---

## Tek dosya, iki değişiklik

`queen-agent/backend/features/workspace/domain/build_prompts.py`

## 1 · Karakter bloğu kendi yardımcısına çıkıyor

Dosyanın sonuna, `_worn` ile `_looked_up` arasına:

```python
def _block(people, characters, outfits, number, misses):
    """One character then what they wear, name after name.

    Its own function because the frame is built in two halves and this shape appears in both: the
    one in front and everyone left behind them. The neighbour rule -- an identity and its outfits
    touching -- is what tells an image model whose clothes are whose, and it is written once.
    """
    parts = []
    for name, worn in people:
        parts.append(_looked_up(name, characters, "characters", number, misses))
        parts.extend(_looked_up(outfit, outfits, "outfits", number, misses) for outfit in worn)
    return parts
```

## 2 · Döngü ikiye bölünüyor

Bugünkü gövde:

```python
    misses, built = [], []
    for number, frame in enumerate(frames, start=1):
        # The order is fixed here rather than in the file: a structure that could reorder itself
        # would answer "why did this frame come out different" with "it varies".
        parts = [structure.get("quality", "")]
        # One character at a time, identity then what they wear: the only thing telling an image
        # model whose clothes are whose is that the two sit next to each other.
        for name, worn in _worn(frame.get("characters")):
            parts.append(_looked_up(name, characters, "characters", number, misses))
            for outfit in worn:
                parts.append(_looked_up(outfit, outfits, "outfits", number, misses))
        place = frame.get("location") or ""
        if place:
            parts.append(_looked_up(place, locations, "locations", number, misses))
        parts.append(frame.get("action", ""))
        parts.append(frame.get("camera", ""))
        built.append(_tags(parts))
```

Yerine:

```python
    misses, built = [], []
    for number, frame in enumerate(frames, start=1):
        # The order is fixed here rather than in the file: a structure that could reorder itself
        # would answer "why did this frame come out different" with "it varies". It also keeps two
        # descriptions apart -- whoever leads opens the prompt, everyone else closes it, and the
        # place, the action and the camera sit in between so the two do not bleed together.
        #
        # The count is placed, never worked out: the code knows who entered the frame but not what
        # they are, and no field says so.
        parts = [structure.get("quality", ""), frame.get("people", "")]
        # Whoever the frame wrote first leads it. No field names them -- the order already carries
        # it, and a second place saying the same thing is a place that can disagree.
        in_frame = _worn(frame.get("characters"))
        parts.extend(_block(in_frame[:1], characters, outfits, number, misses))
        place = frame.get("location") or ""
        if place:
            parts.append(_looked_up(place, locations, "locations", number, misses))
        parts.append(frame.get("action", ""))
        parts.append(frame.get("camera", ""))
        parts.extend(_block(in_frame[1:], characters, outfits, number, misses))
        built.append(_tags(parts))
```

`_worn` bir liste döndürdüğü için `[:1]` ile `[1:]` her iki biçimde de çalışıyor — harita da, eski
düz liste de. Kimsesi olmayan karede ikisi de boş, ve hiçbir şey eklenmiyor.

## 3 · Koş

```
python -m pytest queen-agent -q
```

Beklenen: `test_build_prompts.py`'nin tamamı yeşil — dokuz kırmızı dönüyor, var olan yirmi sekiz
test yerinde kalıyor. **İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.

## 4 · Commit

```
feat(queen-agent): the frame opens with whoever leads it
```

Spec, plan ve kod tek commit'te. `dist` yok: ön yüz değişmiyor.
