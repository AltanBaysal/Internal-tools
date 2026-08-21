# v14 · Görev 13 — Seçim barının görünümü · **test turu**

**Kaynak:** yol haritası 13. madde · Fark 82, 83, 84.

Bar iki şey kazanıyor: öğeleri daha sık duruyor ve hiçbir düğme yazısı iki satıra düşmüyor; seçimde
bekleyen kare varsa katman silme düğmeleri hiç çizilmiyor.

## Fark 84 bu maddede yapılmıyor — sorusu sorulacak

Fark 84 barın alt kenardan **20px** yukarıda durmasını istiyor; bugün 28. Bu, kayıtta göründüğü gibi
bir "sapma" değil, **verilmiş bir karar**:

- v3'te **madde 108 kullanıcının kendi bulgusuydu**: *"bar en dibe yapışık, yüzer olmalı"*.
- v5'in 33. görev spec'i o bulguya cevap verirken şunu yazdı: *"Seçim barı alt kenardan 28 piksel
  yukarıda yüzer (madde 108). **Bugün 20**; kartın gölgesiyle birlikte bu, ekranın dibine yapışmış
  gibi okunuyor."*
- Aynı koşunun yol haritası da not düştü: *"28 piksel bir tercih, ölçülmüş bir sabit değil."*

Yani 20, kullanıcının bizzat "yapışık" dediği değer. v4 fark listesinin karar bölümü `değişecek`
maddelerin karar beklemediğini söylüyor ama istisnasını da yazıyor: *"orada 'sapma' sanılan şey
aslında sonradan verilmiş bir karardı"* — 84 tam olarak o istisna, ve fark listesi 28'i madde 108'e
bağlamadığı için onu o tabloya koymamış.

**Bu turda bar 28'de kalıyor** ve soru kullanıcıya açık metinle soruluyor. Yön güvenli olan yön:
kullanıcının kendi kararını bozmadan bırakmak, tersi bir tuşla geri alınabilir.

## Verilen kararlar

### 1 · Bekleyen kare varsa katman düğmeleri yok

Bugünkü kural (12. madde) "o katmanı taşıyan en az bir kare varsa çiz" idi. Üstüne bir koşul daha
biniyor: **seçimde üretilmemiş tek bir kare bile varsa ikisi de çizilmiyor.**

Gerekçe: bu iki düğmenin aldığı şey tamamlanmış bir yığın; kuyruk hâlâ o kareye yazıyorsa seçim
onların işi değil. Yalnız bekleyen karelerden oluşan seçimde bar her seçimde bulunan üç düğmeye
iniyor — `Tümünü seç · Sil · Vazgeç` (Fark 82).

Kopyala bu kuralı **almıyor**: Fark 79 karışık seçimde onun durmasını istiyor.

### 2 · Boşluk ve tek satır

Öğeler arası boşluk **14 → 10** (Fark 83).

"Bar sarmaz" iki cümle: öğelerin ikinci satıra düşmemesi ve buton yazılarının iki satıra
düşmemesi. Birincisi bugün de doğru — `display: flex` sarmayı zaten kapalı getiriyor, ve kod
yazmayan bir kural yazmıyoruz. İkincisi barın `white-space: nowrap` kazanmasıyla oluyor; bu aynı
zamanda düğmelerin kendi metinlerinin altına sıkışmasını da engelliyor, çünkü esnek bir öğe
`min-content` genişliğinin altına inmiyor.

Barın gerçekten tek satıra sığdığı **jsdom'da ölçülemez** — yerleşim hesaplanmıyor. Ölçülebilen
şey kuralın kendisi; sığma, kullanıcının Colab turunda görülecek.

### 3 · Kaç düğme

Yol haritası "beş düğme" diyor; bar bugün altı taşıyor — `Tümünü seç · Kopyala · Sil · Videoları
sil · Sesleri sil · Vazgeç`. Cümle 11. madde Kopyala'yı getirmeden önce yazılmış. Kastı duruyor:
hepsi tek satırda.

## Yazılacak testler

### `Gallery.test.jsx` — 4

| # | Ne diyor |
|---|---|
| 1 | Seçimde üretilmemiş bir kare varsa katman düğmeleri hiç çizilmiyor |
| 2 | Yalnız bekleyen seçiminde barda üç düğme kalıyor |
| 3 | Öğeler arası boşluk 10 |
| 4 | Düğme yazıları tek satırda kalıyor |

**Toplam 4 test.** 2 numara **doğuştan yeşil**: bekleyen karelerden oluşan bir seçimde Kopyala 11.
maddenin kuralıyla, katman düğmeleri de 12. maddenin kuralıyla zaten doğmuyor. Kırmızıya zorlamak
kaynağı bozmak olurdu; nöbeti yeni kural geldikten sonra tutuyor — o zaman aynı üç düğmeyi *başka
bir sebeple* koruyor.

## Kapsam dışı

- Barın konumu (Fark 84) — yukarıda anlatıldı, sorusu sorulacak.
- Kopyala'nın kuralı değişmiyor.

## Bitti sayılır

Dört komut da koşuyor; queen-editor frontend'de 3 kırmızı duruyor. Testler kırmızı commit ediliyor.
