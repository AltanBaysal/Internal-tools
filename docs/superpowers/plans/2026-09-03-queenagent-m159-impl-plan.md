# Madde 159 — uygulama turu planı

**Spec:** [m159 craft uygulama design](../specs/2026-09-03-queenagent-m159-craft-uygulama-design.md)

## 1. `tools.py` — `CRAFT` yazılır

`WRITING`'in üstüne. `WRITING` yeniden kurulur: kendi çerçevesi + `CRAFT`.

## 2. `tools.py` — şema kalkar

`SCHEMA` import'u, `read_prompt_structure_schema`'nın tanımı ve `run_tool`'daki dalı.

## 3. `tools.py` — dört açıklamaya `CRAFT` eklenir

`set_character`, `set_outfit`, `set_location`, `update_frame` — her birinin kendi cümlesinden sonra.

## 4. `schema.py` silinir

## 5. `modes.py`, `context_box.py`, `stream_answer.py`, `skills.py` temizlenir

`skills.py`'nin modül docstring'i de düzelir: *"şema schema.py'de yaşıyor ve bir araçla çekiliyor"*
artık yanlış.

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

`feat(m159): …` — mesajda çift tırnak yok.
