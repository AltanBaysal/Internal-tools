# Madde 156 — uygulama turu planı

**Spec:** [m156 sayım uygulama design](../specs/2026-09-03-queenagent-m156-sayim-uygulama-design.md)

Kırmızı commit'lendi. Bu tur onu yeşile çevirir.

## 1. `build_prompts.py` — `_kind` eklenir

`_identity`'nin hemen altına, aynı boyda: harita şeklindeki girdinin `kind`'ı, düz metnin hiçbir
şeyi.

## 2. `_counted` eklenir

`COUNTED = ("boy", "girl")` sabiti `BREAK`'in yanına, kodun okuduğu diğer sabitlerin arasına — sıra
bir karar, ve kararın yeri modülün başı.

```python
def _counted(people, characters):
    """How many of each kind stand in this frame, in the tags an image model counts with."""
```

`Counter` `collections`'tan gelir; import dosyanın başına.

## 3. `build_prompts`'ın döngüsünde sıra düzelir

`in_frame` `lead`'in önüne alınır, ve `lead`'in ikinci elemanı
`frame.get("people") or _counted(in_frame, characters)` olur.

## 4. Üç yorum bugüne çekilir

- döngünün içindeki *"the count is placed, never worked out"*
- `build_character_prompts`'ın *"a frame's own field"*
- `_identity`'nin gelecek zamanlı *"for the count code works out"*

## 5. `schema.py` kısaltılır

- `people` paragrafı gider.
- Örnekteki iki `"people"` satırı gider — ilk karede satır başı, ikinci karede satırın tamamı; JSON
  hâlâ geçerli okunmalı.
- `RULEBOOK`'tan 6. kural gider, yerine 3'ünki gibi numaranın neden boş bırakıldığını söyleyen bir
  yorum.

## 6. Koşulur ve yeşil görülür

CLAUDE.md'nin dört satırı, **sırayla**:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: `queen-agent` yalnız notebook'un iki bilinen kırmızısıyla, diğer üçü tamamen yeşil.

## 7. Commit

`feat(m156): …` — mesajda çift tırnak yok.
