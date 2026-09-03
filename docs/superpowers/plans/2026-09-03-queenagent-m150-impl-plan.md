# Madde 150 — Uygulama turu planı

**Kaynak:** [tasarım](../specs/2026-09-03-queenagent-m150-quality-uygulama-design.md) ·
**Tur:** uygulama *(yeşile götürür)*

Yalnız kod. Bu turda hiçbir teste dokunulmuyor — kırmızıda duran beş test ne istiyorsa o yazılıyor.

---

## 1. `build_prompts.py` — sabitin yorumu

- 12-13. satırdaki *"farklı bir zincir gerekiyorsa dosyaya `quality` yazılır ve bu kenara çekilir"*
  cümlesi siliniyor; kod ile çelişen yorum düzeltilir.
- Yerine: zincirin neden kodda olduğu *(Madde 110)* ve kapının neden kapandığı *(Madde 150)*.

## 2. `build_prompts.py` — iki ifade

- 51: `structure.get("quality") or DEFAULT_QUALITY` → `DEFAULT_QUALITY`
- 97: aynısı.
- Sonuç: `build_prompts` ve `build_character_prompts` dosyadan `quality` diye bir şey okumuyor.

## 3. `schema.py` — paragraf

- 81-83. satırlardaki kalite paragrafı siliniyor.

## 4. `schema.py` — kitapçığın 3. kuralı

- Kural siliniyor, **numaralar kaydırılmıyor**: liste 1, 2, 4, 5 … 14 diye gidiyor.
- Sebep tasarımda yazılı: numaralar anılıyor, ve düşen bir şeyin numarası tutuluyor *(Madde 142'nin
  emsali)*.

## 5. Koş ve yeşili gör

```
python -m pytest queen-agent -q
```

Beş kırmızı yeşile dönmüş, sayı 688 olmalı. Başka bir yerde kırmızı çıkarsa durulur.

Diğer üç satır da koşulur.

**Not:** dört satır aynı anda koşturulunca queen-agent frontend'i `test-setup.js`'te toptan düştü ve
tek başına koşunca 586 geçti — kaynak çekişmesinden gelen sahte bir kırmızı. Frontend'e bu maddede
dokunulmuyor; yine de tek başına bir kez koşulur.

## 6. Yeşil commit'lenir

`feat(m150): …`
