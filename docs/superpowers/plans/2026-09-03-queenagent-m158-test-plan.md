# Madde 158 — test turu planı

**Spec:** [m158 düzeltme testler design](../specs/2026-09-03-queenagent-m158-duzeltme-testler-design.md)

Bu tur yalnız test yazar.

## 1. Fikstür

157'nin `CROWDED`'ı olduğu gibi kullanılır: 1. ve 3. kareler dolu, 2. kare yalnız sahne taşıyor.
Yani hem güncellenebilir bir kare hem de reddedilecek boş bir kare zaten orada — ikinci bir fikstür
yazmaya gerek yok.

## 2. Alan testleri

Spec'in 1–4'ü. Her biri güncellemeden sonra **dokunulmayan** alanları da okur; yoksa test
"değişti"yi çiviler ama "geri kalanı durdu"yu çivilemez, ve aracın sözü tam olarak ikincisi.

## 3. Ret testleri

Spec'in 5–9'u ve 11–12'si. Hepsinde dosyanın değişmediği ayrıca okunur.

## 4. Kabul testleri

Spec'in 10'u ve 13'ü.

## 5. Kayıt testleri

Spec'in 15–17'si. Roster 18'e çıkar, `test_modes.py`'nin `WRITES` listesine bir ad girer.

## 6. Koşulur ve kırmızı görülür

CLAUDE.md'nin dört satırı, **sırayla**:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: `queen-agent` kırmızı, diğer üç satır yeşil.

## 7. Kırmızı commit'lenir

`test(m158): …` — mesajda çift tırnak yok.
