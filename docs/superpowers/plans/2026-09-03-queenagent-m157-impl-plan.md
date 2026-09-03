# Madde 157 — uygulama turu planı

**Spec:** [m157 silme uygulama design](../specs/2026-09-03-queenagent-m157-silme-uygulama-design.md)

## 1. `_naming` → `_frames_naming`

Numara listesi döndürür; numara listedeki sıradan gelir. `_set_entry`'nin çağrısı `len(...)` ile
sarılır.

## 2. `_STILL` tablosu ve `_remove_entry`

`_set_entry`'nin hemen ardına, aynı biçimde. Sıra: `_opened` → boş ad → olmayan ad → kullanılan ad →
sil.

## 3. `_a_number` ve `_remove_frame`

`_a_number` `bool`'u dışarıda bırakır. `_remove_frame` `_renumber`'ı çağırır ve cevabında kalan
sayıyı söyler.

## 4. `run_tool`'a dört dal

`set_location`'ın ardına, `add_scene`'in önüne.

## 5. `TOOL_SPECS`'e dört tanım

`set_location`'ın ardına.

## 6. `modes.py`'nin `EDIT` listesine dört ad

## 7. Koşulur ve yeşil görülür

CLAUDE.md'nin dört satırı, **sırayla**:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: `queen-agent` yalnız notebook'un iki bilinen kırmızısıyla, diğer üçü tamamen yeşil.

## 8. Commit

`feat(m157): …` — mesajda çift tırnak yok.
