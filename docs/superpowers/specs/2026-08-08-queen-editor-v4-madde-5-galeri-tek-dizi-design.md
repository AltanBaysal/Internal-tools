# Queen Editor v4 · Madde 5 — Galeri tek dizi olur

**Tarih:** 2026-08-08 · **Yol haritası:**
[v4 Madde 5](../plans/2026-08-08-queen-editor-v4-roadmap.md) · **Kapsadığı kodlar:** G1-G5, N2 ·
**sapma:** aynı hatalı karenin iki kez çizilmesi · **Katman:** arka uç + ön yüz

## Amaç

Galeri dört kovaya bölünmüş olmaktan çıkıp **tek bir diziye** iniyor. Kullanıcının kararı
(2026-08-08) istisnasız: **her kare her zaman kendi sırasında durur** — çalışan, bekleyen, hatalı ya
da üretilmiş. Karenin durumu yalnız görünümünü değiştirir, yerini değil.

## 1 · Tek dizi nereden geliyor

Bugün ekran iki kaynağı birleştiriyor: fotoğrafların listesi (`/photos`) ve kuyruğun kalanı
(`/queue`). İkisi "bu kare nerede duruyor" sorusuna ayrı ayrı cevap veriyor, ekran da onları dört
öbeğe diziyor. Tek dizi için tek cevap gerekiyor.

**`/api/projects/<proje>/frames`** geliyor ve ikisinin yerini alıyor. Cevabı, galerinin görüneceği
sırayla, yukarıdan aşağı:

```
[{ "file": "23_a.png", "status": "done",    "prompt": …, "negative": …, "seed": … },
 { "file": "22_a.png", "status": "pending", "prompt": …, "negative": …, "seed": … },
 { "file": "21_a.png", "status": "failed",  … }]
```

- **Küme:** plandaki her kare + kayıttaki her fotoğraf (eski projelerin planı yalnız son partiyi
  tutuyor, o yüzden birleşim).
- **Elenenler:** `removed` ve `deleted` — galeride yerleri yok.
- **`running` yoktur.** Çalışan kare diskte durum taşımaz; ekran onu koşan işçiden öğrenip `pending`
  görünen kareyi dönen göstergeye çevirir.
- **Sıra:** saklanan galeri sırası (sürükle-bırakın yazdığı), tanımadığı kareler en üste. Yeni kare
  en üstte belirir ve altındakilerin yeri hiç değişmez.

`/queue` kalkıyor. İki uç noktanın aynı soruya cevap vermesi, standardın "bir dosya başkasının
cevabını tekrarlamaz" kuralının uç nokta hâliydi.

## 2 · Numara yönü tersine dönüyor

Rozet **dizideki konumdur, alttan sayılır**: en alttaki 1, en üstteki N. Yeni kare en büyük numarayı
alır ve en üstte durur; altındakilerin numarası değişmez. Silme sonrası kalanlar yeniden numaralanır
— delik kalmaz, çünkü numara dosya adı değil, güncel sıradır.

Rozet artık **bekleyen ve çalışan karelerde de** var; üretilmişlerle aynı dizinin devamı, sadece
daha soluk tonda.

## 3 · Export sırası tersine dönüyor

Dosyaya **yalnız üretilmiş fotoğraflar** girer ve sıra galerinin **tersidir**: en alttaki kare
listenin ilki, yani videonun ilk karesi.

## 4 · Kareler nasıl görünüyor

| Durum | Görünüm | Sürüklenir | Rozet |
|---|---|---|---|
| Üretilmiş | fotoğraf | evet | tam parlaklıkta |
| Bekleyen | kesikli kutu, "bekliyor" | hayır | soluk |
| Çalışan | dönen gösterge | hayır | soluk |
| Hatalı | kırmızı çerçeve, uyarı ikonu, **Tekrar dene** | hayır | soluk |

**Aynı hatalı kare bir kez çizilir.** Bugün bitmiş bir koşuda hatalı kare hem kırmızı hem kesikli
"bekliyor" olarak iki yerde beliriyordu; tek dizide bir karenin tek durumu var.

## 5 · Sürükleme

Yalnız üretilmiş kareler kaldırılabilir; bırakma hedefi dizideki herhangi bir konumdur. Sıra
kaydedilirken listenin tamamı gönderilir — bekleyenler dahil, çünkü sıra artık onları da kapsıyor.

Sunucudaki sıra doğrulaması buna göre genişler: kabul edilen adlar kümesi "kayıttaki fotoğraflar"
değil, "galeride görünen kareler" olur.

## 6 · Testler

**Arka uç**
- `/frames` planı ve kaydı birleştirip saklanan sıraya diziyor; `removed`/`deleted` kareler yok.
- Tanınmayan kare en üste geliyor, altındakilerin sırası değişmiyor.
- Export galerinin tersini veriyor ve yalnız üretilmişleri içeriyor.
- Sıra kaydı bekleyen kare adlarını da kabul ediyor, tanımadığını düşürüyor.

**Ön yüz**
- Dört durum tek ızgarada, her biri kendi sırasında.
- Rozet alttan sayıyor: en alttaki 1.
- Çalışan kare dönen gösterge, bekleyen kesikli, hatalı kırmızı — ve hatalı kare **bir kez**.
- Bekleyen kare sürüklenemiyor, üretilmiş sürüklenebiliyor.
- Bir kare üretilince yerinde fotoğrafa dönüşüyor, komşuları oynamıyor.

## 7 · Geçiş dönemi — bilerek bırakılan iki şey

**Detay sayfası bekleyen kareyi tanımıyor.** Galeri artık tek dizi olduğu için detay sayfasının
okları da o diziyi geziyor — tasarımın istediği bu (F3). Ama bekleyen bir kareye gelindiğinde sayfa
hâlâ fotoğraf çizmeye çalışıyor. Detayın üç hâli **Madde 7**'nin işi; şimdi yamamak aynı sayfayı iki
kez elden geçirmek olurdu. Galeriden tıklayarak oraya gidilemiyor (yalnız üretilmiş kare bağlantı
taşıyor), yani yol yalnız oklardan geçiyor.

**Seçim yalnız üretilmiş karelerde.** Tasarım bekleyen karelerin de seçilmesini istiyor (G6), ama o
**Madde 6**'nın işi. Bu maddede seçim halkası yalnız fotoğraflarda; "Tümünü seç" de yalnız onları
alıyor.

## 8 · Kabul kriteri

`pytest` ve `npm test` yeşil, `npm run build` koşuldu, `dist/` aynı commit'te.

1. Kuyruk akarken galeri hiç oynamıyor; tek değişen bir karenin kutudan fotoğrafa dönmesi.
2. En alttaki karenin rozeti 1; yeni kare en üstte, en büyük numarayla.
3. Export listesi galerinin tersi ve yalnız üretilmiş fotoğrafları içeriyor.
