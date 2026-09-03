# Madde 158 — uygulama turu planı

**Spec:** [m158 düzeltme uygulama design](../specs/2026-09-03-queenagent-m158-duzeltme-uygulama-design.md)

## 1. `_UPDATABLE` ve `WRITTEN` sabitleri

`_UPDATABLE = _FRAME_FIELDS + ("scene",)`.

Boş karenin ölçüsü tek bir yerden okunur: `_is_written(frame)` — `write_frame_prompt` da onu
çağırır, yoksa aynı kare iki araca göre iki hâlde olur.

## 2. `_the_frame` dışarı alınır

`remove_frame`'in numara çözme ve aralık kontrolü bir fonksiyona taşınır, ve `remove_frame` onu
çağırmaya başlar. Davranışı değişmiyor — 157'nin testleri bunun kanıtı.

## 3. `_update_frame` yazılır

Spec'in sırası: yabancı alan → numara → boş kare → verilen alan yok → `_unknown_names` → yaz.

## 4. `run_tool`'a bir dal, `TOOL_SPECS`'e bir tanım, `modes.py`'ye bir ad

## 5. Koşulur ve yeşil görülür

CLAUDE.md'nin dört satırı, **sırayla**:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: `queen-agent` yalnız notebook'un iki bilinen kırmızısıyla, diğer üçü tamamen yeşil.

## 6. Commit

`feat(m158): …` — mesajda çift tırnak yok.
