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

Kare detayında üç sekme var: Foto, Video, Ses. Sayfa bugün açık sekmenin altındaki katmanları da
gösteriyor — video sekmesinde fotoğrafın dosya adı ve prompt'u da yazıyor, ses sekmesinde ikisi
birden. Bu bilerek yapılmıştı ("bu katman neyden yapıldı" görünsün diye), kararı geri alıyoruz.

**Karar verildi.** Üçü de aynı, sade düzen:

- Üstte **kartın adı ve sırası**
- Altında **yalnız o sekmenin prompt'u** — Foto'da foto prompt'u, Video'da video prompt'u, Ses'te ses
  prompt'u

Başka prompt yok, katmanların dosya adları hiç yazmıyor. Bu Foto sekmesini de değiştiriyor: orada da
bugün bir dosya adı satırı var, o da gidiyor.

Düğmeler bugünkü gibi kalıyor.

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

## 7 · Kart kopyalama

Kullanıcı bir kartı kendi eliyle kopyalayabilsin. Kopya birebir ikiz olur — fotoğraf, video, ses
hepsi gelir, üretilecek bir şeyi kalmaz.

**Uygulamada zaten yerleşik olan kurallar** (tasarımın bunlara uyması yeter, değiştirmesi
gerekmiyor):

- Kopya, kaynağın hemen üstüne yerleşir
- Kopya kaynağın dosyalarını paylaşır — iki kart, diskte tek resim
- İkizlerden birini silmek öbürünü bozmaz

**Bugün galeride nasıl iş yapılıyor:** kartlar seçiliyor, sonra galerinin çubuğundaki düğmeyle
siliniyor. Kartın kendi üstünde eylem düğmesi yok — yalnız seçim işareti var, bir de bozuk katmanda
beliren "Tekrar dene".

**Karar sende:** kopyalama nereden yapılacak ve nasıl davranacak. Tasarımı da davranışı da sen
kur — tek kart mı kopyalanır, seçili olanların hepsi mi; düğme nerede durur; kopya oluştuğunda
kullanıcı bunu nasıl görür.

---

## Bu listede olmayanlar

Sıradaki işlerin hepsi arayüz değil; bunlara bakmana gerek yok:

- **Galeri hızı** — karolar için küçük önizleme üretilecek. Kartın bekleme hâli zaten var, tasarım
  gerekmiyor.
- **Video kalitesi** — üretim ayarları ve videonun prompt'u. Ekranda karşılığı yok.
- **Üretme hızı** — üretimin kendi süresi.
- **Varyant varsayılanı** — bir prompt'tan kaç kare üretileceğinin varsayılanı 4'ten 2'ye inecek. Tek
  bir sayı.
