# Madde 121 — Action sızıntıları kural defterine girer · Tur 1 (testler) tasarımı

**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) Madde 121.
**Gözlenen** *(28 Ağustos, beşinci deneme)*: beş sızıntı ve hiçbirini defter yakalamıyor —
action'da hareket, action'da kamera sözü, action'da rol adı, action'da `or`, giyene göre
adlandırılmış ve ikilenmiş outfit girdileri.

## Kural

Deftere beş girdi *(10-14)*. 119 olguyu öğretti; defter, dosya yazılmadan önce *"buna karşı
kontrol et"* denilen sayılabilir liste — 108→118 gösterdi ki olgu ve çit birlikte gerekiyor.

1. **10** — action'da hareket/zaman sözü; poz yazılır.
2. **11** — action'da kamera sözü; kadraj kendi alanının.
3. **12** — action'da rol-akrabalık adı; kamera ilişki görmez, kimin karede olduğunu characters
   haritası söylüyor.
4. **13** — herhangi bir değerde `or`; model tek resim çizer, yazı-tura atamaz.
5. **14** — giyene göre adlandırılmış outfit, ve iki giyen için aynı metni taşıyan iki girdi;
   giysi adlandırır, bir giysi bir girdidir.

## Test — `test_schema.py`, beş yeni

| Test | Aradığı |
|---|---|
| hareket | `10.` ve `frozen instant` |
| kamera sözü | `11.` ve `full body view` |
| rol adı | `12.` ve `stepson` |
| or | `13.` ve `any value` |
| giyen adı | `14.` ve `named after its wearer` |

Dikkat: defterde `style` kelimesi geçemez *(mevcut süpürme)* ve `shot` yalnız `medium shot`
olarak durabilir — girdiler ikisini de içermiyor.

## Beklenen kırmızı

`test_schema.py` 5. Defter çifti bilinen kırmızı.

## Bilerek yapılmayanlar

- **`schema.py` açılmaz** — tur 2.
- **Şemanın düzyazısı değişmez** — 119 yazdı; bu tur yalnız defter.
- **`dist` derlenmez.**
