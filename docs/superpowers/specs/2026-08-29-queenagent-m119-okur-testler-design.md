# Madde 119 — Şema okurunu söyler · Tur 1 (testler) tasarımı

**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) Madde 119.
**Gözlenen** *(28 Ağustos, beşinci deneme)*: yapı dosyasında hareket yönetmenliği — `head moving
back and forth`, `riding with hips moving` — çünkü modelin okuduğu hiçbir metin promptların kime
gittiğini söylemiyor: SDXL/etiket bilgisi (K9) yalnız modelin görmediği belgelerde, karenin tek
bir donmuş fotoğraf olduğu hiçbir yerde.

## Kural

Şemanın en başına bir olgu paragrafı, kamera paragrafına bir kapatma cümlesi:

1. Her prompt SDXL ailesinden bir görüntü modeline gider; model etiket okur, cümle değil; bir
   prompt tek bir durağan resim üretir — donmuş bir an. Zamanla görünen hiçbir şey resme ulaşmaz:
   hareket yok, ses yok, önce-sonra yok. Bir hareket, içinden geçtiği **poz** olarak yazılır
   *(yasak tek başına kareyi boşaltırdı — 115'in "cause"u nasıl görünene çevrildiyse)*.
2. Kameranın iki yarısı da paragraftaki listelerden gelir — `from side profile` bir tag değil,
   `from side` öyle.

## Test — `test_schema.py`, dört yeni

| Test | Aradığı |
|---|---|
| şema okurunu adlandırır | `SDXL-family` ve `tags, never sentences` |
| kare tek donmuş an | `one single still picture`, `frozen instant`, `no motion` |
| hareket poza çevrilir | `the pose it passes through` |
| kamera listeden | `come from the lists` |

Mevcut süpürmeler korunur: olgu paragrafı `{` içermez *(artikel süpürmesi örnek bölgesini ilk
`{`'den bulur)*, `shot` kelimesi geçmez.

## Beklenen kırmızı

`test_schema.py` 4. Defter çifti dal yaşadıkça bilinen kırmızı, bu maddenin değil.

## Bilerek yapılmayanlar

- **`schema.py` açılmaz** — tur 2.
- **Skill metinleri ellenmez** — bağlam 120'nin, defter girdileri 121'in işi.
- **`dist` derlenmez.**
