# Queen Editor — Yol Haritası v13

**Tarih:** 2026-08-14 · **Koşu dalı:** `feat/queen-editor-v3` · **Durum:** 0/2
**Öncesi:** [v12](2026-08-14-queen-editor-v12-roadmap.md) — kapandı. Bu koşu onun Colab turundan
çıktı.

## Neden bu koşu var

Kullanıcı v12'yi Colab'da çalıştırdı. Galeri açıkken uygulama şunu bastı:

```
Sunucuya ulaşılamadı — bağlantıyı kontrol et.
Zaman aşımı (10 sn)
```

Mesajın kendisi doğru: `request()` on saniye cevap vermeyen isteği kesiyor ve kestiğini söylüyor.
Tur, arkasındaki iki ayrı eksiği çıkardı.

**Galeri kendi sunucusunu boğuyor.** `/api/frames` fotoğraflara hiç bakmıyor — proje klasöründeki üç
metin dosyasını okuyor, ve `photos.jsonl` damgasıyla önbellekte tutuluyor. Yani yavaşlığın kaynağı
isteğin kendi işi değil. Kaynak, galerinin karoları: her karo tünelden geçen ayrı bir istek ve
**aynı anda kaçının uçtuğunu sınırlayan hiçbir şey yok**. Poll'un isteği onların arasında sırasını
bekliyor ve on saniyelik kesme devreye giriyor.

Çekişmenin hangisi olduğu — bağlantı slotlarının dolması mı, tam boy fotoğrafların bandı doldurması
mı — **ölçülmedi**, çünkü bu koşu yazılırken Colab kapalıydı. Tünel HTTP/2 konuşuyorsa slot sınırı
hiç devrede değildir; bant doygunluğu ise aynı sonucu tek başına verir. İkisinin de sebebi aynı
şeydir (aynı anda uçan çok sayıda büyük istek) ve ikisi de aynı tavanla çözülür, o yüzden koşu
ölçümü beklemeden ilerliyor. Tavandan sonra hata sürerse ilk iş ölçmek olur.

**Bir hata ayıklanamıyor.** Ekranda "hangi istek cevapsız kaldı" ve "tünel gerçekte ne döndürdü"
yazmıyor, çünkü `request()` düz bir metin fırlatıyor ve yol boyunca kanıt düşüyor: JSON olmayan
gövde `null`'a çevriliyor (Cloudflare'ın hata sayfası ve kodu buharlaşıyor), gövdede `error` varsa
HTTP kodu hiç görünmüyor, metot ve yol ise hiçbir yere yazılmıyor. Kopyala düğmesi zaten var —
kopyalayacak kanıt yok.

İkisi de yine **dikişte**. Kuyruk için: hiçbir test "aynı anda kaç resim uçuyor" diye sormuyor,
çünkü bugüne kadar bunu sınırlayan bir şey yoktu — sorulacak bir davranış yoktu. Hata için: her
katmanın kendi testi var ve geçiyor, ama kanıt katmanların **arasında** kayboluyor; `api.js`'in
bildiğini panel hiç görmüyor. Bulunan her hatanın aynı yerden çıkması tesadüf değil, o yüzden
çalışma biçimi v12'deki gibi kalıyor.

## Nasıl çalışacağız

**Her görev iki döngü.** Önce yalnız testler: spec → plan → testleri yaz → commit. O commit takımı
**kırmızı bırakır** ve mesajı hangi testlerin neden düştüğünü söyler. Sonra implementasyon: spec →
plan → kodu yaz → commit; takım yeşile döner.

Sebebi: testi kodla aynı nefeste yazınca test kodun zihin modelini miras alıyor ve aynı körlüğü
taşıyor. Araya commit sınırı koymak testi davranıştan yazmaya zorluyor.

**Yeni bir modül getiren görevde iskelet test döngüsüne girer.** Modül hiç yokken test dosyası
import'ta patlar; kırmızıdır ama hiçbir `expect` değerlendirilmez, dolayısıyla testin doğru şeyi
sorup sormadığı görünmez. Bunun yerine test döngüsü modülü **yalnız imzalarıyla** açar — dönüş tipi
doğru, içi boş, içinde tek bir kural, sayı veya koşul yok. Böylece her test koşar ve **iddiasından**
düşer. Kural ("önce mantık yazılmaz") sağlam kalır: miras alınacak bir zihin modeli yoktur, yalnız
isimler vardır.

**İstisna yok.** Ön yüz değişen her görevde `dist/` implementasyon commit'ine girer. Kullanıcı en
sonda toplu Colab testi yapar; koşu boyunca durulmaz.

## Kapsam sınırı

- **Küçük önizleme hâlâ dışarıda.** v12'den beri tasarım kararı bekliyor ve beklemeye devam ediyor.
  Bu koşu onu ikame etmiyor: tavan **kırılmayı** durdurur, önizleme **hızı** getirir. İkisi rakip
  değil, sıradaki iki ayrı iş.
- **Başarısız karede hover karartması** da v12'den devrolan tasarım işi olarak dışarıda.
- **Çekişmenin hangi mekanizma olduğu ölçülmüyor.** Yukarıda yazılı; koşu tavanla ilerliyor.
- **On saniyelik kesme değeri değişmiyor.** Sayı sorunun kendisi değil, sorunun görünme biçimi.

## Görevler

### Görev 1 · Galeri resimleri sunucuyu aç bırakıyor

**Ne olacak:** Galeri karolarının resimleri bir eşzamanlılık kuyruğundan geçecek — aynı anda en
fazla ikisi uçacak, gerisi sırada bekleyecek. Karo görüş alanına yaklaşınca sıraya girecek, slot
almadan uzaklaşırsa sıradan düşecek; yani bugünkü `loading="lazy"` davranışı korunuyor, üstüne bir
tavan konuyor. Kuyruğun kendisi DOM bilmeyen saf bir modül olacak, çünkü işin bütün kuralları orada
ve orası tarayıcısız sınanabiliyor.

**Bağımlılık:** Yok.

**Bitti sayılır:** Galeride aynı anda en fazla iki karo resmi uçuyor, kaydırılan yer önce iniyor, ve
üretim sürerken poll zaman aşımına düşmüyor. Son yargı Colab turunun.

### Görev 2 · Bir hata kendi kanıtını taşıyor

**Ne olacak:** Bir istek başarısız olduğunda hangi istek olduğu, sunucunun HTTP kodu ve gövdenin ham
metni hatanın üstünde taşınacak; kopyala düğmesi bunları verecek. Ekranda görünen cümle
değişmeyecek — zenginleşen şey kopyalanan kanıt. Bugün kanıtın nerede düştüğü belli: JSON olmayan
gövde, gövdesi olan hatanın HTTP kodu, ve hiç yazılmayan metot/yol.

**Bağımlılık:** Yok. Görev 1'den sonra yapılıyor çünkü asıl kırığı o düzeltiyor; teknik bir bağı
yok.

**Bitti sayılır:** Ölü bir tünelden dönen hata kartında Kopyala'ya basınca panoya hangi isteğin
atıldığı, dönen HTTP kodu ve ham gövde geliyor; hiçbiri uydurulmuş bir sebep içermiyor.

## Sonraki koşuya kalanlar

Galeri karolarının küçük önizlemeleri ve başarısız karede hover karartması — ikisi de v12'den
devrediyor ve tasarım kararı bekliyor. Bir de bu koşuyu kapatacak Colab turundan çıkacak yeni
maddeler; çekişmenin gerçek mekanizması, tavan yetmezse, ilk sıradaki olur.
