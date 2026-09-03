# Madde 154 — Uygulama turu planı

**Kaynak:** [tasarım](../specs/2026-09-03-queenagent-m154-haritalar-uygulama-design.md) ·
**Tur:** uygulama *(yeşile götürür)*

Yalnız kod. Hiçbir teste dokunulmuyor.

---

## 1. `build_prompts.py` — iki şekil

- `_identity(entry)` — sözlükse `tags`, değilse kendisi.
- `_block` içinde ve `build_character_prompts` içinde çağrılıyor.
- `kind` prompta girmiyor.

## 2. `tools.py` — yardımcılar

- `KINDS = ("girl", "boy")` — 156 da buradan okuyacak.
- `structure_name(name)` — `safe_name`'den sonra, uzantıyı `.json` yapar.
- `_set_entry(...)` — üç aracın ortak gövdesi.

## 3. `tools.py` — dört araç tanımı

- `create_structure(file)`
- `set_character(file, name, kind, tags)`
- `set_outfit(file, name, tags)`
- `set_location(file, name, tags)`
- Açıklamalar kuralları taşıyor: karaktere kıyafet yazılmaz; bir kıyafet girdisi **tek kişiyi**
  giydirir ve giysiye göre adlandırılır.

## 4. `tools.py` — yönlendirme ve kart

- `run_tool` dört adı tanır.
- `WRITES_FILES`'a `create_structure` girer.

## 5. `modes.py`

- Dört ad `EDIT`'in listesine.

## 6. Koş ve yeşili gör

```
python -m pytest queen-agent -q
```

Defterin iki kırmızısı dışında hepsi yeşil. Diğer üç satır ardışık koşulur.

## 7. Yeşil commit'lenir

`feat(m154): …`
