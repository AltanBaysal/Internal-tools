# Madde 231 · Galeride Shift ile aralık, Ctrl ile tek tek seçim — test turunun tasarımı

**Tarih:** 17 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

## Kullanıcıdan gereken

Hiçbir şey. Kullanıcı 17 Eylül'de Ctrl'ün de gelmesini istedi. Teknik kararları kullanıcı bıraktı.

## Bugün ne oluyor

[`Gallery.jsx`](../../../queen-editor/frontend/src/features/photo_generation/Gallery.jsx)'de seçim,
kimliklerin basılma sırasıyla tutulduğu bir liste. Bir kart üç yoldan seçiliyor: halkaya basmak
*(`onCheck`)*, seçim açıkken kartın kendisine basmak *(kartın `onClick`'i)*, ve seçim yokken hiçbir
yol yok, çünkü kartın bağlantısı detay sayfasını açıyor. Hiçbiri tuşa bakmıyor.

## Ne olacak

Windows'un dosya seçimi gibi, üç kuralla:

1. **Shift + tık, çapadan tıklanan karta kadar olan her kartı seçime ekler.** Aralık galerinin
   **ekrandaki sırasıyla** sayılıyor, basılma sırasıyla değil. Yukarıdan aşağı da aşağıdan yukarı da
   aynı. Seçimde zaten olanlar **kalıyor**: aralık ekleniyor, seçimin yerine geçmiyor, çünkü
   kullanıcının seçtiği bir kartı sessizce düşürmek bir kayıp olurdu.
2. **Ctrl + tık, kartı seçime ekler ya da çıkarır.** Mac'teki karşılığı ⌘ de aynı işi yapıyor.
3. **Çapa, Shift'siz basılan son kart.** Shift + tık çapayı taşımıyor, böylece aynı çapadan farklı
   bir uca uzatılabiliyor.

**Seçim yokken** Shift ya da Ctrl ile bir karta basmak detay sayfasını **açmıyor**, seçimi o kartla
başlatıyor. Seçim yokken çapa da yok: eski bir seçimden kalan çapa yeni bir aralık başlatmıyor.

**Worker'ın tuttuğu kare** aralığın içinde kalsa da seçilmiyor, bugün de seçilemediği için.

Tuşsuz tık bugünkü gibi: seçim yokken detayı açıyor, seçim varken kartı ekleyip çıkarıyor.

## Çivilenecek olgular

| # | Ne diyor | Bugün |
|---|---|---|
| 1 | Shift + tık yukarıdan aşağı aralığı seçiyor | **kırmızı** |
| 2 | Shift + tık aşağıdan yukarı aralığı seçiyor | **kırmızı** |
| 3 | Aralık son tuşsuz basılan karttan başlıyor, ve daha önce seçilen kalıyor | **kırmızı** |
| 4 | Worker'ın tuttuğu kare aralıkta seçilmiyor | **kırmızı** |
| 5 | Seçim yokken Shift + tık detayı açmıyor, seçimi o kartla başlatıyor | **kırmızı** |
| 6 | Ctrl + tık detayı açmadan kartı ekliyor, ikinci kez çıkarıyor | **kırmızı** |
| 7 | Seçim çubuğundaki sayı aralığı sayıyor | **kırmızı** |

## Bu turda değişen

Yalnız testler: `Gallery.test.jsx`.
