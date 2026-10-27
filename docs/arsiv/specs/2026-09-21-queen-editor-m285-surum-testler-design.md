# Madde 285 · Ekran V6 diyecek — test turunun tasarımı

**Tarih:** 21 Eylül 2026 · **Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md) ·
**Kurallar:** [FOUNDATION](../../../queen-editor/FOUNDATION.md) ·
[CODE-STANDARD](../../../queen-editor/CODE-STANDARD.md)

## Kullanıcıdan gereken

Hiçbir şey.

## Bugün ne var

`version.js` `VERSION = "V5"` diyor, ve dört ekran onu çiziyor. v6 gerçek davranış değiştirdi —
yatay birleşik çıktı, disclaimer, yeni adım adı, klasörler — ve kullanıcı başlıkta hâlâ **V5**
görüyor.

## Bu madde kırmızı veremez, ve sebebi bir kural

248'in kararı: **sayı elle yazılan bir karardır**, koşu açılınca değişir, ve `"V6"`yı bir teste
yazmak o kararı iki yere koymak olur. Mevcut test o yüzden yalnız **biçimi** tutuyor:
`/^V\d+$/`. Dört ekranın testleri de aynısını yapıyor — `/^Queen Editor V\d+$/`.

Yani sayıyı `V6` yapmak **hiçbir testi düşürmez**, ve düşürecek bir test yazmak 248'i çiğnemek
olur. **Bu tur bu yüzden kırmızı vermiyor**, ve bu `skip`/`xfail` ile gizlenmiyor — olduğu gibi
yazılıyor. Turların sırası korunuyor: test önce, kod sonra.

## Ama çivilenecek gerçek bir şey var

**Ekranın çizdiği sayı, `version.js`'in söylediği sayı olmalı.** Bugün bunu tutan hiçbir test yok:
dört ekran testi kendi başına bir kalıp soruyor, hiçbiri modülü okumuyor. Ekran bir gün elle
`"V5"` yazsa, ya da modül değişip ekran değişmese, **hiçbir test düşmez**.

Bu turda yazılan test o boşluğu kapatıyor: `VERSION` içe alınıyor, ve ekranda **tam o değer**
aranıyor. Bugün yeşil — ama ekranla modülün ayrılmasını bundan sonra o tutuyor, ve asıl kazanç bu:
sayı hâlâ tek yerde, ve tek yerde olduğu artık ölçülüyor.

## Çivilenen olgu

**Export ekranının başlığı `Queen Editor ${VERSION}` diyor**, modülden okunan değerle. Sabit bir
sayı hiçbir teste yazılmıyor.

## Beklenen sonuç

**Kırmızı yok, dört satır yeşil kalıyor.** Sayının değişmesi uygulama turunda, ve orada da yeşil
kalacak — çünkü test sayıyı değil **bağı** tutuyor.
