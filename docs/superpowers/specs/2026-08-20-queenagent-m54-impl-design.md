# Madde 54 · Tur 2 (uygulama) — Tasarım

**Madde:** [v4 yol haritası Madde 54](../plans/2026-08-20-queenagent-v4-colab-roadmap.md)
**Turun kırmızısı:** [Tur 1 tasarımı](2026-08-20-queenagent-m54-test-design.md) —
`test_dist_is_committed.py`, iki test.
**Bu belgenin konusu:** kuralın kendisi. Testler onu zaten tarif etti; burada **nerede** ve **neden
orada** yazıldığı var.

---

## Kural nerede yaşamalı

Kökteki [.gitignore](../../../.gitignore) `dist/` diyor, ve bunu PyInstaller artıkları için diyor —
depodaki her `dist` klasörünü kastediyor. İstisna oraya yazılmaz: kök dosya araçları tanımaz, ve
tanımaya başlarsa her yeni araç onu büyütür.

İstisna **aracın kendi dosyasında** durur. queen-editor bunu zaten böyle yapıyor
([queen-editor/.gitignore](../../../queen-editor/.gitignore)): `!frontend/dist/`, ve sebebi satırın
yanında. queen-agent'ın dosyası bugün tam tersini söylüyor — `frontend/dist/` diyerek kökün kuralını
**pekiştiriyor**, ve yanında "unlike queen-editor, nothing here ships pre-built" yazıyor. Çevrilecek
olan o satır ve o cümle.

Sonuç: iki araç, iki dosya, aynı desen. Kural nerede geçerliyse orada yazılı.

## Neden dizinin kendisi yeniden dahil ediliyor

`!frontend/dist/` **dizini** yeniden dahil ediyor, içindeki dosyaları değil. Sebebi git'in kendi
davranışı: yok sayılan bir dizine hiç girilmez, yani içindeki dosyalar hakkında yazılmış bir kural
**hiç okunmaz**. Dizin geri alınınca git içine girer, ve `dist/` kuralı yalnız `dist` adlı dizinleri
eşlediği için içerideki `index.html` ve `assets/` kendiliğinden serbest kalır.

## Ne commit'leniyor

Üç dosya: `index.html` ve `assets/` altındaki iki bundle. Derleme sökme sırasında silinmişti, Tur
1'de sayfanın okunabilmesi için yeniden üretildi; şimdi commit'leniyor.

## Bunun doğurduğu kural

Bundan sonra bir frontend değişikliği, `dist` **aynı commit'te** yeniden derlenip eklenmeden bitmiş
sayılmaz. Bunu belge olarak söyleyecek yer Madde 53 (FOUNDATION Karar 3); tutacak yer Tur 1'in iki
testi. Bu maddede yalnız gerçek kuruluyor, cümle bir sonrakinde yazılıyor — belgenin bir commit
boyunca yalan söylememesi için.

## Bilerek yapılmayan

- Kök `.gitignore` değişmiyor.
- queen-editor'ün `dist`'ine dokunulmuyor; orada kural zaten yürüyor.
- `.gitattributes` eklenmiyor. Bundle'lar depoya LF ile giriyor ve Colab'a LF olarak varıyor;
  Windows'taki çalışma kopyasının CRLF olması ne servisi ne testi etkiliyor.
