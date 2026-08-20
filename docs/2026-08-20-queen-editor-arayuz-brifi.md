# Queen Editor — Arayüz İşleri

**20 Ağustos 2026 · 6 madde**

Sıradaki işlerden arayüzü ilgilendirenler. Her maddede ne istediğimiz ve tasarımın hangi kararı
vermesi gerektiği yazıyor.

**Tasarımı olabildiğince basit tut.** Var olan düzeni koru, yeni parça eklemekten kaçın; bir sorun
mevcut bir yerde çözülebiliyorsa orada çözülsün.

---

## 3 · Video için loop ve sonrakine bağlama seçimi

En büyük tasarım işi. Videonun bitiş karesi seçilebilecek; iki mod var:

| Mod | Başlangıç | Bitiş |
|---|---|---|
| Loop | Kartın kendi fotoğrafı | Aynı fotoğraf — video başladığı yere döner |
| Sonrakine bağla | Kartın kendi fotoğrafı | Bir sonraki kartın fotoğrafı |

Örnek: sıradaki 10. kartta "sonrakine bağla" seçilirse video 10'dan başlar, 11'de biter.

**Karar verildi:**

- Seçim **kartın üstünde** yapılır. Her kart üç durumdan birinde: normal, loop, sonrakine bağla.
- Seçim üretimi başlatmaz — kart işaretlenir, üretim toplu üretime kadar bekler.
- Kart hangi modda olduğunu **ikonla** gösterir.
- "Sonrakine bağla" işaretli kartın sonrakisi yoksa **üretim engellenmez**: o kare kuyruğa girmez,
  diğerleri girer. Kullanıcı düzeltip tekrar basınca o da eklenir. Bu durum yalnız **dizinin son
  kartında** olabilir — sonrakisi olmayan tek kart o.
- Panel bunu tek satırla söyler ve durum sürdüğü sürece orada durur.
- Kartın üstünde kalıcı bir uyarı durumu yok. Sorun üretim anında, panelde konuşulur.

Not: yukarıdaki sorun yalnız **sonrakine bağla** modunda çıkıyor. Loop kendi fotoğrafına bağlandığı
için kart nereye taşınırsa taşınsın bozulmuyor. Aynı kontrolün iki modu ama yalnız biri kırılgan.

**Karar sende:**

- Üç durum kartta nasıl seçilir ve hangi ikonlarla gösterilir? Kart küçük, ikonlar resmin üstüne
  biniyor.
- Bir kartın loop mu, bağlı mı olduğu galeriye bakınca okunabilmeli — nasıl?

## 4.1 · Her sekme yalnız kendi katmanını göstersin

Kare detayında üç sekme var: Foto, Video, Ses. Katmanlar üst üste biniyor — fotoğraf en altta, video
onun üstünde, ses en üstte. Sayfa bugün "açık sekmenin altındakileri de göster" diye kurulmuş:

| Açık sekme | Bugün sağ sütunda görünen | Olması gereken |
|---|---|---|
| Foto | Yalnız fotoğraf | Aynı — zaten doğru |
| Video | Fotoğraf **+** video | Yalnız video |
| Ses | Fotoğraf **+** video **+** ses | Yalnız ses |

Bu bilerek yapılmıştı ("bu katman neyden yapıldı" görünsün diye), kararı geri alıyoruz.

**Karar verildi:** video seçiliyse video detayları görünür, ses seçiliyse ses detayları, foto
seçiliyse foto detayları.

- **Kalacak:** kaçıncı kare olduğu · **kartın kendi adı** · açık sekmenin kendi prompt kutusu
- **Gidecek:** katman başına açılan dosya adı satırlarının **hepsi** — açık olanınki de dahil ·
  alttaki katmanların prompt kutuları

Yani sekmede görünen tek ad kartın adı; katmanların dosya adları hiç yazmıyor. Video sekmesi için
somut hâli:

```
bugün                            olması gereken

Sıra          3 / 12             Sıra          3 / 12
Foto          kare_03.png        <kartın adı>
Video         kare_03.mp4
                                 Prompt   [video'nun prompt'u]
Prompt   [video'nun prompt'u]
Foto prompt   [salt okunur]
```

Video prompt'u çoğu zaman boş — onu yapay zekâ yazıyor, üretim sırası gelene kadar boş duruyor. Bu
durumda prompt kutusu boş görünsün, yeter; ayrı bir boş sayfa tasarımı istemiyoruz. Bu maddede
senden karar beklemiyoruz.

## 4.2 · Foto / Video / Ses sekmeleri ayrılsın

Şu an bitişikler, tek bir parça gibi okunuyorlar. Bu da bilerek yapılmıştı ("üç ayrı hap değil, üç
durumu olan tek denetim"), kararı geri alıyoruz.

**İstediğimiz:** aralarına boşluk girsin, üç ayrı sekme gibi dursunlar.

Açık olan sekme rengiyle belli olsun — ek bir işaret istemiyoruz. Bu maddede senden karar
beklemiyoruz, boşluğun ölçüsü sende.

## 4.3 · Video paneli yanlış sebebi söylüyor

Üretilecek bir şey kalmadığında panel hep aynı cümleyi basıyor: *"Tüm karelerin videosu var —
üretilecek bir şey yok."* Oysa iş kalmamasının birden çok sebebi var ve panel hangisi olduğuna
bakmıyor. Fotoğrafı henüz üretilmemiş kareler seçtiğinde de bunu diyor — o karelerin videosu yok,
daha fotoğrafı bile yok.

**Karar verildi.** Bugünkü gibi **tek bir mesaj** kalsın, ama duruma göre değişsin:

| Durum | Mesaj |
|---|---|
| Üretilmiş karelerin hepsinde zaten video var | Tüm karelerin videosu var. |
| Hiç üretilmiş kare yok | Henüz üretilmiş kare yok. |
| Seçilen karelerin fotoğrafı üretilmemiş | Seçili karelerin fotoğrafı henüz üretilmedi. |
| Varyant sayısı boş | Varyant sayısı girilmedi. |

Aynı desen ses paneli için de geçerli. Mesaj her zaman tek satır; bu maddede senden karar
beklemiyoruz.

## 5 · Toplu kart taşıma

Kareler çoğu zaman birbirinin devamı, bir dizi oluşturuyorlar. O diziyi başka bir yere almak
gerektiğinde kartlar tek tek taşınıyor ve sıra karışıyor.

**İstediğimiz:** birden fazla kart seçilip sürüklendiğinde hepsi birlikte taşınsın, kendi
aralarındaki sıra bozulmadan. Çoklu seçim zaten var, tek kart sürükleme de çalışıyor.

**Karar verildi — yeni bir öğe eklenmiyor:**

- Seçili kartların hepsi aynı anda "sürükleniyor" görünümüne geçer. Bugün tek kart sürüklenirken ne
  oluyorsa, seçimin tamamına uygulanır. Neyin gittiği kaynakta görünür; sayı rozeti ya da yığın
  görüntüsü gerekmiyor.
- Bırakılacak yuvanın göstergesi değişmez — kartlar bitişik bir blok olarak ineceği için bugünkü
  gösterge yeterli.
- Sürüklenirken imlecin altında görünen görüntüye dokunulmaz; tarayıcının varsayılanı kalır.

Kural olarak: seçili bir kart sürüklenirse seçimin tamamı gider, seçili olmayan bir kart
sürüklenirse yalnız o gider ve seçim bozulmaz.

Seçim dağınıksa — örneğin 3, 7 ve 9. kartlar — taşındıklarında **yan yana gelirler**, kendi
aralarındaki sıra korunarak. Aralarında kalan kartlar boşluğu kapatır.

Bu maddede senden karar beklemiyoruz.

## 1.1 · Galeride kart bekleme durumu

Galeri yavaş yükleniyor; asıl çözüm geliştirme tarafında (karolar için küçük önizleme). Senden
istediğimiz tek şey bekleme hâli.

**Karar sende:** kart, resmi gelene kadar ne gösterecek — boş çerçeve, yer tutucu, bulanık önizleme?
Galeri kaydırılırken bu durumun sık görüneceğini hesaba kat.

---

## Bu listede olmayanlar

Sıradaki işlerin hepsi arayüz değil; bunlara bakmana gerek yok:

- **Video kalitesi** — üretim ayarları ve videonun prompt'u. Ekranda karşılığı yok.
- **Üretme hızı** — üretimin kendi süresi.
- **Varyant varsayılanı** — bir prompt'tan kaç kare üretileceğinin varsayılanı 4'ten 2'ye inecek. Tek
  bir sayı.
- **Kart kopyalama** — ertelendi, sırası gelince tasarıma dönecek.
