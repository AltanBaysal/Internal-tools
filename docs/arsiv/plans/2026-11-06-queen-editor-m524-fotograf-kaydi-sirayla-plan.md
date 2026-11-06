# Madde 524 · Fotoğraf kaydına satırlar sırayla yazılır — plan

**Madde:** [v11 yol haritası](../arsiv/roadmaps/2026-10-24-queen-editor-v11-roadmap.md#v11-23), 524 · v11-23 ·
**Spec:** [2026-11-06-queen-editor-m524-fotograf-kaydi-sirayla-design.md](../specs/2026-11-06-queen-editor-m524-fotograf-kaydi-sirayla-design.md)

Önce test, eski kodda kırmızı; sonra kod (yeşil). Ekrana dokunulmaz, `dist` derlenmez.

## 1. Test — `backend/tests/test_photo_record.py`

- `InPieces(Storage)`: gerçek depo; ilk eklemesi dosyaya iki parça halinde ulaşır (`cut` bayttan
  bölünür) ve arada ikinci yazmayı `Meanwhile.now` ile (523'ün `test_written_at_once.py`'sinden)
  içeri alır. Sonraki eklemeler olduğu gibi.
- `test_two_lines_written_at_once_stand_whole_in_the_order_they_were_written`, `cut` 0 (ilk bayttan
  önce: sıra) ve satırın içi (bölünme). Dosyanın satırları birinci ve ikinci girdinin JSON'u,
  bu sırayla.

## 2. Kod

- `features/photo_generation/data/photo_record.py`: `threading` içeri; `__init__`'te
  `self._appending = threading.Lock()` ve nedeni; `append` satırı kilidin dışında kurar, içinde
  `append_line`'a verir. Modül docstring'inde 513'ün sıraya dayandığı cümleye kilidin bunu tuttuğu
  eklenir.

## 3. BACKLOG

- `queen-editor/BACKLOG.md`: *"Fotoğraf kaydına aynı anda iki satır yazılabilir"* silinir.

## 4. Suite

- `python -m pytest queen-editor -q`.
