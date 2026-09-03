# Madde 153 — Uygulama turu planı

**Kaynak:** [tasarım](../specs/2026-09-03-queenagent-m153-numara-uygulama-design.md) ·
**Tur:** uygulama *(yeşile götürür)*

Yalnız kod, hepsi `tools.py`'de. Hiçbir teste dokunulmuyor.

---

## 1. `_renumber(frames)`

- Listeyi sırayla geçer, her kareyi `{"frame": sıra, **kalanı}` diye **yerinde yeniden kurar**.
- Yerinde kurulması gerekiyor: üstüne yazmak numarayı günceller ama başa almaz, çünkü sözlükte
  anahtar ilk yazıldığı yerde durur.
- Ayrı bir fonksiyon, çünkü 155 ve 157 de buradan geçecek.

## 2. `_add_frames` — çağrı yeri

- `frames.append(...)` ile `file_store.write(...)` arasında.

## 3. `_add_frames` — cevap

- `Added frame {len(frames)} to {source}.`
- `outcome` değişmiyor: `1 frame`.

## 4. Koş ve yeşili gör

```
python -m pytest queen-agent -q
```

Defterin iki kırmızısı dışında hepsi yeşil olmalı. Diğer üç satır ardışık koşulur.

## 5. Yeşil commit'lenir

`feat(m153): …`
