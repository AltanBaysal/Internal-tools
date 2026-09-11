# Madde 210 — queen-editor'ün sürüm kaydı · uygulama turu

**Kaynak:** [yol haritasının Madde 210'u](../plans/2026-09-11-queen-editor-v5-roadmap.md) ·
**Test turu:** [spec](2026-09-11-queen-editor-m210-surum-kaydi-testler-design.md), kırmızısı
`e820c50`.

## Ne yazılacak

Dört kırmızı var ve üçü tek bir dosyanın yokluğundan: `queen-editor/SURUMLER.md`. Dördüncüsü
CLAUDE.md'nin bir cümlesi.

## Kayıt ne söyler

İki şey, ve ikisi de bugün hiçbir yerde yazmıyor:

**Güncel sürüm.** Tek satır, tek dal adı. Soruyu soran buraya bakar ve biter.

**Hangi belgenin hangi sürüme ait olduğu.** On dört yol haritası, beş sürüm. Kaydın değeri burada:
bir belgenin adındaki numara onun sürümü değil, ve bunu söyleyen tek yer bu dosya.

**Neyin yanlış gittiği de yazılır**, çünkü kayıt olmadan aynı soru aynı yanlış cevabı alır: koşan yol
haritasına madde ekleyecek yerde her koşuda yeni bir roadmap açılmış. Bir sürüm bir daldır ve o dalın
tek yol haritası olur.

## v2'nin dalı yazılmıyor, çünkü bilinmiyor

Test turu *"her yol haritası başlığında dalını söyler"* diye bir varsayım kodladı ve varsayım yanlış
çıktı: **v2 hiçbir yerinde dal adı taşımıyor**, ve doğrusu ölçülemiyor.

Ölçülen şu: belgeyi ekleyen commit `01344b0`, `feat/queen-editor-v1` dalının geçmişinde duruyor — ama
v1'e sonradan girmiş bir commit de orada durur, yani bu onun o dalda yazıldığını kanıtlamıyor. Üstüne
v2, v3'ün v1'i adlayarak açıldığı gün kapanmış; yani v1 iki koşuyu birden taşımış da olabilir, v2
başka bir yerde koşmuş da.

**Uydurulmuş bir dal adı yazılmayacak.** Kayıt *bilinmiyor* der ve ölçümü yanına koyar. Test de buna
göre düzelir: bir belge ya başlığında dalını söyler, ya da kayıt onu **açıkça bilinmiyor diye
işaretler**. Sessizlik hâlâ kırmızı — düzelen tek şey, dürüst bir bilinmeyenin geçebilmesi.

Bu, testin gevşetilmesi değil: yanlış olan iddia değil, iddianın dayandığı varsayımdı.

## Dosya adlarına dokunulmuyor

Ne bu turda ne sonra. Yazılmış spec'ler ve görev planları bu adlara atıf yapıyor; üstelik v5–v13'ün
dokuzu aynı dalda koştuğu için yeniden adlandırma dokuz dosyayı tek ada yığardı.

Eski koşuların metni de birleştirilmiyor: yüz elliden fazla madde okunmaz tek bir belgeye inerdi ve
gerçekten olmuş koşu sınırları silinirdi.

## Değişen dosyalar

| Dosya | Ne oluyor |
|---|---|
| `queen-editor/SURUMLER.md` | yeni: güncel sürüm, sürüm–belge tablosu, ve neyin yanlış gittiği |
| `CLAUDE.md` | *"highest `vN` current"* cümlesi düzelir — güncel sürüm en yüksek belge değil, en son dal |
| `test_version_record.py` | üçüncü iddia, kayıtta açıkça bilinmiyor işaretli belgeyi kabul eder |

**Eski on üç belgeye dokunulmuyor.** Onikisi dalını zaten başlığında söylüyor; on üçüncüsü v2, ve onun
cevabı kayıtta duruyor. Belgelere birer düzeltme satırı eklemek on üç dosyayı açıp aynı cümleyi
kopyalamak olurdu — bir kopya da bayatlayan şeydir.

## Nasıl görülür

```bash
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Dördü de yeşile döner, arka uçta 745 yeşil; ön yüz süiti hiç etkilenmez — bu madde ön yüze
dokunmuyor, `dist` derlenmiyor.

Adım adım dökümü [uygulama turunun planında](../plans/2026-09-11-queen-editor-m210-impl-plan.md).
