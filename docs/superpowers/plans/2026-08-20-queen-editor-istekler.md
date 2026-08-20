# Queen Editor — İstekler

**Tarih:** 2026-08-20 · **Dal:** `feat/queen-editor-v4`

Sıradaki işlerin tek listesi. Kullanıcının bugün saydıkları, kendi sırasıyla; bekleyen eski maddeler
de bunların içine yerleşti.

Maddeler ne istendiğini ve neye bağlı olduğunu söylüyor; nasıl yapılacağı sırası gelince kendi
spec'inde çıkar. Bilerek ertelenmiş işlerin kalıcı kaydı [BACKLOG.md](../../../queen-editor/BACKLOG.md).

## Ham liste

1. UI hızı ciddi şekilde artırılır
2. Video modelinin gücü artırılacak
3. Video üretiminde loop ve bir sonraki kareye bağlama özelliği gelecek
4. Bulunan UI hataları düzeltilecek
5. Toplu card taşıma
6. Detaydan çıkınca yüklenmeme olmaması — sayfa neden, fotolar neden siliniyor
7. Duplicate card özelliği gelmeli *(erteleme kalktı)*
8. Default 2 yap
9. Üretme hızı *(sonradan eklendi, en sona)*

---

## 1 · UI hızı

İki ayrı şey; ilaçları da ayrı.

### 1.1 Galeride fotoğraflar ve videolar yavaş yükleniyor
Karolar yavaş doluyor, çünkü her karo dosyanın tam boyunu indiriyor.

**Öneri — küçük önizleme.** Karolar için küçük birer önizleme üretilsin; galeri tam boy dosya yerine
onları göstersin. Asıl hızı bu getirir.

Kararı gereken: önizleme ne zaman üretilecek (kare üretilirken mi, ilk bakışta mı) ve kare
değişince ne olacak.

**Yarısı yapıldı, görülmedi.** Aynı anda kaç karonun birden indirileceğine bir tavan kondu; bu dalda
duruyor ama Colab'da denenmedi. Tavan yığılmayı durdurur, indirilen veriyi küçültmez — o yüzden
önizleme yine de gerekiyor.

### 1.2 Detaydan dönünce ana sayfa state'ini kaybediyor
Bir kareyi açıp geri gelince galeri sıfırdan yükleniyor, fotoğraflar ekrandan kayboluyor. Dosyalar
Drive'da duruyor — kaybolan görüntü, veri değil. Olması gereken: geri dönünce sayfa bıraktığın yerde
dursun.

**Ham listedeki 6 bu maddedir** — aynı kök, tek iş.

## 2 · Video modelinin gücü

Model değişmiyor. Güç iki yerden aranacak.

### 2.1 LoRA denenecek
Videonun LoRA'ları değiştirilip denenecek.

**Bedeli:** LoRA seçimi bugün uygulamadan yapılamıyor, üretim tarifinin içinde sabit duruyor. Colab
yalnız yayınlanmış hâli gördüğü için **her deneme bir yayın** demek. Denemeyi ucuzlatmak — LoRA'yı
uygulamadan seçilebilir kılmak — kendi başına ayrı bir iş; bu maddeye dahil mi, karar gerekir.

### 2.2 Video prompt'u güçlenecek
Kullanıcı yazmazsa videonun prompt'unu yapay zekâ yazıyor. Ona verilen talimat güçlenecek.

**Kapsam:** şimdilik yalnız talimat. Yazan modeli değiştirmek bu maddede yok.

## 3 · Loop ve sonraki kareye bağlama

**İkisi tek özellik.** Video üretimi ilk ve son kareyi alabilir; fark yalnızca son karenin ne
olduğunda:

| Mod | İlk kare | Son kare |
|---|---|---|
| Loop | Kartın kendi fotoğrafı | Aynı fotoğraf — video başladığı yere döner |
| Sonrakine bağla | Kartın kendi fotoğrafı | Bir sonraki kartın fotoğrafı |

10. kartta *"sonrakine bağla"* seçilirse: başlangıç 10, bitiş 11.

**Bugün son kare verilemiyor** — üretim yalnız ilk kareyi alıyor. Asıl iş bu; iki mod onun üstüne
oturan seçim.

Loop için başka bir araçtan grafik devralınması düşünülüyordu; buna gerek kalmıyor, loop kendi
üretimimizin son karesi.

**Tasarımda çözülecek:** son kartta "sonrakine bağla" ne yapar; sonraki kartın fotoğrafı yoksa ne
olur; seçim kart başına mı, toplu mu.

## 4 · Bulunan UI hataları

Üçü de daha önce görülmüş, kararı verilmiş, sırası gelmemiş işler.

### 4.1 Detay sayfası yalnız kendi katmanını göstersin
Bugün açık sekmenin altındaki katmanlar da görünüyor — video sekmesinde fotoğrafın adı ve prompt'u da
yazıyor. Üçü de aynı, sade düzene inecek: üstte kartın adı ve sırası, altında yalnız o sekmenin
prompt'u. Başka prompt yok, katmanların dosya adları hiç yazmıyor — Foto sekmesindeki dosya adı
satırı da gidiyor. Düğmeler bugünkü gibi kalıyor.

Video prompt'u çoğu zaman boş olduğu için sekme boşalabilir; o durumda prompt kutusu boş görünsün,
ayrı bir boş sayfa tasarımı istenmiyor.

### 4.2 Foto / Video / Ses sekmeleri ayrılsın
Bugün bitişikler, tek bir parça gibi duruyorlar. Aralarına boşluk girecek.

**Tasarımda çözülecek:** ayrılınca hangi sekmenin açık olduğu yalnız renkten anlaşılacak; buna bir
kez daha bakmak gerekir.

### 4.3 Video paneli yanlış sebebi söylüyor
Seçilen karelerin henüz fotoğrafı yokken panel *"Tüm karelerin videosu var — üretilecek bir şey
yok"* diyor. Sebep o değil.

## 5 · Toplu kart taşıma

**Neden:** kareler çoğu zaman birbirinin devamı, bir dizi oluşturuyorlar. O diziyi başka bir yere
almak gerektiğinde kartlar tek tek taşınıyor ve sıra karışıyor.

**Ne olacak:** birden fazla kart seçilip sürüklendiğinde hepsi birlikte taşınacak, kendi aralarındaki
sıra bozulmadan. Çoklu seçim zaten var, tek kart sürükleme de çalışıyor; eksik olan seçimin
sürüklemeye katılması. Mekanik değişmiyor.

**Karar verildi:** dağınık seçim taşınınca kartlar yan yana gelir, kendi aralarındaki sıra korunur.
Seçili bir kart sürüklenirse seçimin tamamı gider; seçili olmayan sürüklenirse yalnız o gider. Ekrana
yeni bir öğe eklenmiyor — seçili kartların hepsi sürüklenen görünümüne geçer, yuva göstergesi aynı
kalır.

## 7 · Duplicate card

Kullanıcı bir kartı kendi eliyle kopyalayabilsin.

**Sıfırdan değil.** Uygulamada kopya kare kavramı zaten var: bir kareye birden fazla video varyantı
istendiğinde fazlalıklar kopya kare olarak doğuyor — kaynağın fotoğrafını paylaşıyorlar (diskte tek
resim), kaynağın hemen üstüne yerleşiyorlar, galeride normal kare gibi davranıyorlar. Adlandırma,
yerleşim ve kayıt kuralları hazır; eksik olan kullanıcının bunu isteyebileceği bir yol.

**Karar verildi:** kopya kartın **tamamını** alır — fotoğraf, video, ses. Birebir ikiz olur,
üretilecek bir şeyi kalmaz. Bugünkü kopya kareden farkı bu: o yalnız fotoğrafı paylaşıp videosunu
kendi üretiyor.

Dosya paylaşımının silme tarafı da çözülmüş: bir dosyayı başka bir kare hâlâ tutuyorsa dosya yerinde
kalıyor, yani ikizlerden birini silmek öbürünü bozmuyor.

**Tasarımda çözülecek:** kopyalama nereden yapılır ve nasıl davranır — tasarımcıya bırakıldı.

## 8 · Fotoğraf varyant varsayılanı 4 → 2

Üretim panelinde bir prompt'tan kaç kare üretileceğinin varsayılanı 4; 2 olacak. Katman panelindeki
varyant değişmiyor.

Listedeki en küçük iş.

## 9 · Üretme hızı

Sıranın en sonu. Üretim hızlansın; yol olarak hız LoRA'ları denenecek.

Kazanç fotoğraf tarafında görünüyor — video zaten hızlı koşacak şekilde ayarlı.

**Dikkat:** madde 2.1 videoyu güçlendirmek istiyor, bu madde hızlandırmak. İkisi aynı ayarları ters
yönlere çekiyor, birlikte bakılmalı.

## Colab turu

Bir madde tarayıcı olmadan yargılanamıyor: **1.1'in tavanı** — galeri açıkken çıkan zaman aşımı
kalktı mı. Bu dalda duruyor ama notebook yalnız yayınlanmış hâli klonladığı için tur, dal
yayınlanmadan atılamaz.

Turun sonucu sıralamayı değiştirir: tavan yetmediyse 1.1 öne geçer.
