# Madde 232 · Kare değişince sahnede eski karenin dosyası kalmayacak — test turunun tasarımı

**Tarih:** 17 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

## Kullanıcıdan gereken

Hiçbir şey. Kullanıcı 17 Eylül'de verdi: fotoğraf **gecikerek** geliyor ama o arada yanlış kare
görünüyor, video ve seste de aynısı var, ve çözümün **kökten ve basit** olması isteniyor.

## Bugün ne oluyor

Oklar sayfayı yeniden kurmuyor, altındaki kareyi değiştiriyor *(`PhotoDetail.jsx`)*. Sahnedeki öğeler
kareye bağlı değil:

- **Fotoğraf:** aynı `<img>` kalıyor, yalnız `src`'si değişiyor. Tarayıcı yenisi gelene kadar eskisini
  çizmeye devam ediyor.
- **Video ve ses:** `LayerPlayer` aynı kalıyor. İçindeki `<video>` ve `<audio>` yalnız adres
  değiştiriyor, ve dalga formu eski sesin tepelerini yenisi okunana kadar tutuyor.

Aynı kökün bir izi zaten kodda: eski karenin ret kartı, basışları ve yazıları bir `useEffect`'te
**elle** temizleniyor. O temizlik state için doğru yer, çünkü açık sekme bilerek korunuyor *(madde 38)*.
Medya ise state değil, DOM. Onu elle temizlemek yerine React'e yeni bir öğe kurdurmak gerekiyor.

## Ne olacak

**Sahnedeki medya karenin kimliğine ve açık sekmeye bağlı bir `key` taşıyor.** Kare değişince eski
`<img>`, `<video>` ve `<audio>` DOM'dan çıkıyor ve yenileri kuruluyor. Önceki kareden hiçbir piksel
ya da ses kalamıyor.

**Yeni öğe gelene kadar sahne ne olduğunu söylüyor.** Dosya yüklenene kadar **`yükleniyor…`**
yazıyor, uygulamanın model kutusunda kullandığı kelimeyle. Dosya gelirse kelime kalkıyor. Gelmezse
sahne **`Dosya yüklenemedi`** diyor, altında hangi adresin gelmediği `RawOutput` kutusunda duruyor ve
*Kopyala* ile alınabiliyor. Tarayıcı bir medya hatasına sebep cümlesi vermiyor, bu yüzden yazılan
yalnız bilinen: adres.

**Bu durum üç medya için tek yerde tutuluyor**, ayrı ayrı değil.

## Çivilenecek olgular

| # | Ne diyor | Bugün |
|---|---|---|
| 1 | Kare değişince eski `<img>` DOM'dan çıkıyor | **kırmızı** |
| 2 | Yeni fotoğraf yüklenene kadar sahne `yükleniyor…` diyor, yüklenince kelime kalkıyor | **kırmızı** |
| 3 | Fotoğraf gelmezse sahne `Dosya yüklenemedi` diyor ve adresi gösteriyor | **kırmızı** |
| 4 | Video sekmesinde kare değişince eski `<video>` DOM'dan çıkıyor | **kırmızı** |
| 5 | Ses sekmesinde kare değişince eski `<audio>` DOM'dan çıkıyor | **kırmızı** |
| 6 | Video yüklenene kadar `yükleniyor…`, yüklenince kelime kalkıyor | **kırmızı** |
| 7 | Video gelmezse `Dosya yüklenemedi` ve adresi | **kırmızı** |

Açık sekmenin korunması zaten çivili *("keeps the open tab when the next frame has that layer too")*,
ve bu turda dokunulmuyor.

## Bu turda değişen

Yalnız testler: `PhotoDetail.test.jsx`.
