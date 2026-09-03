# Madde 152 — Uygulama turu planı

**Kaynak:** [tasarım](../specs/2026-09-03-queenagent-m152-parametre-uygulama-design.md) ·
**Tur:** uygulama *(yeşile götürür)*

Yalnız kod. Hiçbir teste dokunulmuyor.

---

## 1. `tools.py` — araç tanımı

- `frames` parametresi çıkıyor; `action`, `camera`, `characters`, `location` giriyor.
- `required`: `name`, `action`, `camera`.
- Açıklama yeniden yazılıyor: araç bir kare alıyor, alan alan. `people` hiçbir yerde geçmiyor.
- Tanınan alanların kümesi modül seviyesinde bir sabit — hem şema hem kod kontrolü aynı listeden
  okusun, iki kopya ilk değişiklikte ayrışır.

## 2. `tools.py` — `_add_frames`

Sırayla, hepsi yazmadan önce:

1. Dosya var mı *(bugünkü cevap)*
2. JSON okunuyor mu *(bugünkü cevap, parser'ın kendi cümlesi)*
3. `frames` listesi var mı *(bugünkü cevap)*
4. **Tanınmayan alan var mı** → ret, hangisi olduğunu ve nelerin tanındığını söyleyerek
5. **`action` ve `camera` var mı** → ret
6. **Adlar haritalarda var mı** → ret, `build_prompts`'ın sözlüğüyle: `lara is not in characters;
   known: aylin`
7. Kareyi kur ve yaz

- Cevap: `Added a frame to scene.json; it holds 3 now.`
- `outcome`: `1 frame`

## 3. `skills.py`

- *"in batches of five"* → *"one call per frame"*.
- Tek cümle; gruplamanın sebebi zaten aracın şeklinde.

## 4. Koş ve yeşili gör

```
python -m pytest queen-agent -q
```

707 olmalı. Diğer üç satır ardışık koşulur.

## 5. Yeşil commit'lenir

`feat(m152): …`
