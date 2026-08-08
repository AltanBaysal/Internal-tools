# Madde 9 — Projeler ekranı

**Tarih:** 2026-08-09 · **Branch:** `feat/queen-editor-v2` · **Yol haritası:**
[v4, Madde 9](../plans/2026-08-08-queen-editor-v4-roadmap.md) ·
**Kaynak:** [tasarım v2 farkları](../research/2026-08-08-queen-editor-tasarim-v2-farklari.md),
**N3**, **N4** ve iki ad uyarısı sapması

---

## 1 · Bugünkü hâl ve sorun

Projeler ekranı bu turda hiçbir maddenin uğramadığı tek ekran. Kalan üç iş:

- **Uyarı basınca çıkıyor, yazarken değil.** Geçersiz bir ad yazılır, Oluştur'a basılır, istek
  sunucuya gider ve ancak dönen cevapla uyarı belirir.
- **Boş adda hiçbir uyarı yok.** Kutu boşken buton pasif ve sebep yazmıyor — kullanıcı butonun neden
  ölü olduğunu tahmin etmek zorunda.
- **Kart silme butonu yıkıcı eylem standardının dışında** duruyor: çerçevesiz, yalnız kırmızı ikon.

## 2 · Karar özeti

| Kod | Karar |
|---|---|
| sapma | Uyarı **yazarken** çıkar; uyarı varken **Oluştur pasif** kalır |
| sapma | **Boş ad** da uyarı yazdırır — ama kutuya hiç dokunulmadan değil |
| **N4** | Kart silme butonu **kırmızı çerçeve + kırmızı çöp ikonu** olur, yazısız *(kullanıcı kararı, 2026-08-09)* |
| **N3** | Uzun listede ızgara kendi içinde kaymaz, **sayfa kayar** — yapılacak iş yok *(kullanıcı kararı, 2026-08-09)* |

## 3 · Ad uyarısı canlı olur — kural yine tek sahipte

Tasarım: *"Geçersiz karakter veya boş ad girildiğinde aynı yerde uyarı çıkar"* ve *"uyarı varken
buton pasif kalır."*

Buradaki tuzak, kuralı ön yüze kopyalamak: bugün ad kuralları arka uçta tek bir yerde duruyor
(`name_rules`) ve o dosyanın kendi yorumu *"the frontend prints them verbatim and keeps no copy of
the rules"* diyor. Yazarken uyarı vermek için kuralın kopyası ön yüze taşınırsa aynı kural iki
sahipli olur ve ikisi zamanla ayrışır.

**Çözüm: kuralı taşımak yerine soruyu sormak.** Sunucuya "bu ad olur mu?" diye soran, hiçbir şey
değiştirmeyen bir uç nokta açılır; cevabı ya `null` ya da **sunucunun kendi Türkçe cümlesi** olur.
Modal yazarken bunu sorar, dönen cümleyi olduğu gibi basar.

- İstek **yazma durunca** gider (kısa bir gecikmeyle), her tuşta değil.
- Cevaplar sırasız dönebilir; yalnız **o an kutuda yazan** ada ait cevap ekrana çıkar.
- Uç nokta **saf**: yalnız ad kurallarına bakar, diske dokunmaz. "Bu ad zaten kullanılıyor" bir
  kural değil bir çakışmadır ve yerini korur — Oluştur'a basınca çıkar. Tasarım da yazarken böyle
  bir uyarı istemiyor.
- Sunucuya ulaşılamıyorsa uyarı **çıkmaz**: bir önizleme yüzünden kullanıcının yolu kesilmez.
  Gerçek karar zaten Oluştur'a basınca sunucuda veriliyor ve orada hata olarak görünür.

**Kutuya dokunulmadan uyarı yok.** Modal açılır açılmaz "Proje adı boş olamaz." yazmak, hiçbir şey
yapmamış birini azarlamak olur. Tasarımın kelimesi de bu: uyarı **girildiğinde** çıkar. Yani kutuya
bir kez yazıldıktan sonra boşaltılırsa uyarı çıkar; hiç yazılmadıysa çıkmaz. Buton her iki hâlde de
pasiftir — biri sebebini söyler, diğeri söyleyecek bir şey olmadığı için susar.

## 4 · Kart silme butonu

**Kırmızı çerçeve + kırmızı çöp ikonu, yazısız.** Tasarım kendi içinde çelişiyordu: uygulama geneli
kuralı çerçeveli ve yazılı buton istiyor ve proje silmeyi örnekleri arasında sayıyor, ama kendi kart
çiziminde buton çerçevesiz ve yazısız (fark belgesi 8.4). Kullanıcı ortadaki hâli seçti: kuralın
rengi ve çerçevesi korunur, 4:3 kartın köşesine yazı sıkıştırılmaz.

Kuralın asıl koruduğu şey zaten duruyor ve değişmiyor: **dolu kırmızı buton hiçbir yerde yok**, ve
asıl yıkıcı adım olan onay penceresi standardın tam hâlini taşıyor.

## 5 · Uzun proje listesi

**Sayfa kayar; ızgaranın kendi kaydırma alanı yoktur.** Yazılı anlatı bunu söylüyordu, ekran çizimi
ise ızgaranın sağına kaydırma çubuğu ve alta solma perdesi koyuyordu (fark belgesi 8.7). Kullanıcı
yazılı anlatıyı seçti.

Bugünkü uygulama zaten böyle çalışıyor, dolayısıyla **bu maddede yapılacak iş yok**. Kayıt olsun diye
yazıldı: bir dahaki karşılaştırmada N3 "atlanmış" sanılmasın.

## 6 · Değişmeyenler

- Boş liste ekranı, yükleme göstergesi ve "Projeler yüklenemedi" kartı.
- Proje silme onay penceresi ve metinleri.
- Kartın kendisi bir buton: tıklanınca proje açılır, çöp ikonu ayrı bir buton olduğu için tıklama
  projeyi açmaz.
- Enter ile oluşturma, Esc ile kapatma, istek uçarken modalın kapanmaması.
- **"Bu ad zaten kullanılıyor"** yalnız Oluştur'a basınca çıkar.

## 7 · Yok

- Ad kurallarının ön yüze kopyalanması.
- Yazarken çakışma (aynı ad) denetimi.
- Izgara içi kaydırma, solma perdesi, sanallaştırma.
- Kartın yeniden adlandırılması, kapak görseli, foto sayısı (kapsam dışı).

## 8 · Kabul kriterleri (testler bunları kanıtlar)

**Arka uç**

1. Ad denetimi uç noktası geçerli ad için boş cevap verir.
2. Geçersiz karakter ve boş ad için **`name_rules`'un kendi cümlesini** döndürür — ayrı bir metin
   yazılmaz.
3. Uç nokta hiçbir şey oluşturmaz: çağrıldıktan sonra proje listesi değişmez.

**Ön yüz**

4. Modal açıldığında uyarı yoktur ve Oluştur pasiftir.
5. Geçersiz bir ad yazılınca uyarı sunucunun cümlesiyle çıkar ve Oluştur pasifleşir — hiçbir
   oluşturma isteği gönderilmez.
6. Ad düzeltilince uyarı kalkar ve Oluştur aktifleşir.
7. Yazılıp sonra boşaltılınca uyarı çıkar.
8. Denetim isteği her tuşta değil, yazma durunca gider.
9. Denetim isteği düşerse uyarı çıkmaz ve buton kilitlenmez.
10. Kart silme butonu kırmızı çerçevelidir.

## 9 · Kendi eleştirim

- **En kolay yol yanlış yoldu.** Ön yüze küçük bir regex koymak bu maddenin tamamını beş satırda
  bitirirdi — ve `name_rules.py`'nin kendi yorumunun yalanladığı bir kopya bırakırdı. Uç nokta
  pahalı görünüyor ama kuralı tek sahipte tutuyor; 3. bölüm gerekçesiyle yazılı.
- **"Girildiğinde" kelimesi kolayca atlanır.** Modal açılır açılmaz boş kutuya uyarı basmak
  tasarımın cümlesine *uyar gibi* durur ama kullanıcıyı hiç yapmadığı bir şeyle suçlar.
  "Dokunulmuş kutu" ayrımı bu yüzden var.
- **Ağ hatası uyarıya dönüşmemeli.** Denetim bir önizlemedir; sunucuya ulaşılamadığında kullanıcının
  önünü kesmesi, olmayan bir kuralı varmış gibi göstermek olur. Sessizce geçilir.
- **N3'te "iş yok" da bir karardır.** Yazmadan geçilseydi bir sonraki karşılaştırma bunu atlanmış
  bir fark sanırdı; 5. bölüm bunun için duruyor.
- **Sırasız cevap.** Hızlı yazarken eski bir cevabın yeni metnin üstüne uyarı basması gerçek bir
  hata olurdu; cevap, o an kutuda yazana ait değilse atılıyor.
