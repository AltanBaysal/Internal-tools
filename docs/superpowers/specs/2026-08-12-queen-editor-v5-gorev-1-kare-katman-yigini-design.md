# Queen Editor v5 · Görev 1 — Kare katman yığını olur

**Tarih:** 2026-08-12 · **Yol haritası:**
[v5 Görev 1](../plans/2026-08-12-queen-editor-v5-roadmap.md) · **Kapsadığı maddeler:** 103, 101 ·
**Katman:** yalnız arka uç

## Amaç

Kare, bir fotoğraf olmaktan çıkıp **bir katman yığınına** dönüyor: foto + en fazla bir video + en
fazla bir ses; ses videoya bağlı (madde 103). Yığının tek bir kuralı var ve tasarımın bütün üretim
davranışı ondan çıkıyor: **üret = ekle, sil = kaldır** — hiçbir üretim var olan bir katmanın üstüne
yazmaz.

Bunun kod tarafındaki asıl kazancı şu: bugün **kare ile dosya aynı şey.** Günlük satırları dosya
adıyla anahtarlanıyor, galeri sırası dosya adı tutuyor, "bu kareye ne oldu" sorusu "bu dosyaya ne
oldu" sorusuyla aynı soru. Tasarım v3 bu eşitliği iki yerden birden bozuyor: bir kare üç dosya
taşıyabiliyor (madde 103) ve iki kare **aynı dosyayı paylaşabiliyor** (madde 100, 102 — kopya
kareler fotoyu, ses varyantları videoyu paylaşıyor). Eşitlik burada çözülmezse Blok 5'teki her görev
onu yeniden çözmek zorunda kalır.

Görev 1 bu yüzden tek bir şeyi getiriyor: **karenin kendi kimliği ve katman yuvaları.** Üretimin
kendisi (Blok 5-6), adların yeni şeması (Görev 2) ve ekranın hiçbir parçası bu görevde yok.

## Kapsam

**İçinde:** günlüğün kare ve katman tanıması; katman yuvası kuralı (foto · video · ses); "üret =
ekle" kısıtının kayıt düzeyinde kurulması; kareyi silmenin bütün katmanları götürmesi; videoyu
silmenin sesi de götürmesi; paylaşılan dosyanın son sahibi gidene kadar diskte kalması; galeri
sırasının dosya adı yerine kare kimliği tutması.

**Dışında:** dosya adı şeması (Görev 2) — bu görev bugünkü `<sayı>_<harf>` adını aynen kullanır;
kuyruğun iş türü tanıması (Görev 3); video ve ses üretiminin kendisi (Blok 5-6); kopya karenin
doğması (Görev 15); katman silmenin arayüzü ve sekme başına yıkıcı eylem (Görev 26); her türlü
ekran dokunuşu.

---

## 1 · Kare ile dosya ayrılıyor

Bugün bir karenin kimliği, fotoğrafının dosya adı. Yarın bir foto dosyası birden çok kareye ait
olabileceği için bu kimlik yetmiyor.

**Karenin kimliği, doğduğu andaki adıdır ve bir daha hiç değişmez.** Bu görevde o ad bugünkü
plandan geliyor: planın verdiği `<sayı>_<harf>` çifti — yani `12_a`. Kareye sonradan video takılması
kimliğini değiştirmez; kimlik doğum anında verilir, katmanlar üstüne gelir.

**Neden değişmez bir kimlik.** Galeri sırası, detay sayfasının adresi ve seçim hep kareyi işaret
ediyor. Kimlik katman geldikçe büyüseydi (`12_a` → `12_a_video`), video üretilen her karede galeri
sırası ve açık duran her adres bozulurdu — kullanıcının düzenlediği sıra, ilke 1'e göre korunması
gereken emeğin ta kendisi.

**Dosya adı ile kimlik neden aynı şey değil:** kimlik kareyi, ad dosyayı gösterir. Bir foto dosyası
iki karede yaşayabilir; bir karenin üç dosyası olabilir. Görev 2 ad şemasını değiştirdiğinde
kimliğin biçimi de yeni doğan kareler için onunla değişir — ama var olan karelerin kimliği
dokunulmadan kalır, çünkü kimlik doğum anının kaydıdır.

---

## 2 · Günlük: satır artık kareyi ve katmanı söylüyor

Proje klasöründeki dosya sayısı değişmiyor. Günlük satırı iki alan kazanıyor:

| Alan | Anlamı |
|---|---|
| `frame` | Satırın hangi kareye ait olduğu — karenin kimliği |
| `layer` | Hangi yuva: `photo` · `video` · `audio` |

`status` sözlüğü aynen duruyor (`done` · `failed` · `removed` · `deleted` · `queued`); yalnız artık
**kareye değil, karenin bir katmanına** ait.

**Okuma kuralı değişiyor:** bugün "bir dosya adı hakkında en son yazılan satır geçerli". Artık
**bir (kare, katman) çifti hakkında en son yazılan satır geçerli.**

Gerekçe: dosya paylaşılabilir hâle geldiği an dosya başına katlamak yanlış cevap verir — A karesinin
fotosu silindiğinde aynı dosyayı kullanan B karesinin fotosu da silinmiş görünürdü. Kare kendi
katmanının sahibi; dosya ortak olabilir.

**Geriye uyum, migrasyon yok.** `frame` ve `layer` alanı olmayan eski satır tek türdür — foto —
çünkü bugün başka katman yok. Böyle bir satır okunurken `layer` = `photo`, `frame` = dosya adının
uzantısız hâli sayılır (`12_a.png` → `12_a`). Drive'daki mevcut projeler elle dokunulmadan çalışmaya
devam eder; bu, `status` alanı gelirken kullanılan uyumun aynısıdır.

---

## 3 · Yuva kuralı: dolu · boş

Bir karenin üç yuvası var ve her yuva iki hâlden birinde:

```
DOLU  = yuvanın son satırı  done | failed
BOŞ   = yuvanın hiç satırı yok  ·  ya da son satırı deleted | removed | queued
```

**Bu soru "kuyruk bu kareyi borçlu mu" sorusu DEĞİL.** İki ayrı soru, iki ayrı kural — karıştırmak
v4'te kapatılmış bir hatayı geri getirir:

| Soru | Kim sorar | Kural |
|---|---|---|
| **Yuva dolu mu** | üretim ("buraya yazabilir miyim") ve panel ("bu kare kapsamda mı") | yukarıdaki ikili |
| **Kuyruk borçlu mu** | işçi ("sırada ne var") | **değişmiyor:** hiç satırı yok, ya da son satırı `queued` |

Silinmiş bir foto yuvası **boştur** ama kuyruk onu borçlu **değildir** — silinen fotoğrafın karesi
kuyruğa geri dönmez (v4 Madde 1'de düzeltilen hata, kabul kriteri olarak duruyor). Boş yuva yalnız
şunu söyler: oraya yeni bir iş **istenebilir**. İşin kendiliğinden doğması diye bir şey yok; işi ya
panel ya Tekrar dene ekler.

Bu ikili, tasarımın üç ayrı davranışını tek kuraldan türetiyor:

**a) "Üret = ekle" kısıtı.** Dolu yuvaya üretim yazılamaz. Video üretimi videolu bir kareye
gelirse reddedilir — tasarımın "videolu kare kopyalanır" kuralının (madde 25) kayıt tarafındaki
karşılığı budur. Kopya karenin doğması Görev 15'in işi; buradaki iş, ezmenin **mümkün olmaması**.

Kısıtı bir **alan kuralı** taşıyor: "bu karenin bu yuvasına üretim yazılabilir mi" sorusunu
cevaplayan tek bir saf işlev. Üretim yolları onu çağırmadan katman yazamaz; bugünkü foto yolu da
buna bağlanır, böylece kural üç katmanda tek yerde durur.

**b) Hatalı katman dolu sayılır** *(kullanıcı kararı, 2026-08-12)*. Videosu hata almış kare
"videosu var ama bozuk" demektir; üretim panelinin kapsamına geri düşmez, panel onu atlar.
Düzeltmenin tek yolu karttaki ya da detaydaki **Tekrar dene**'dir. Böylece aynı kare için iki
üretim yolu açılmaz ve kullanıcı ikisini birden tetikleyip aynı kareye iki iş sokamaz.

**c) Silinen katman yuvayı boşaltır** *(kullanıcı kararı, 2026-08-12)*. Kullanıcı videoyu bilerek
silerse kare yeniden videosuz olur ve panel kapsamına döner; "tüm kareler" denirse videosu yeniden
üretilir. Uygulama hiçbir yerde "kullanıcı bunu bilerek sildi" diye bir işaret tutmaz — tutsaydı,
aynı gerçeğe ikinci bir yazıcı vermiş olurduk.

**Tekrar dene neyi değiştirir.** Bugünkü mekanizma aynen geçerli: `queued` satırı yuvayı boşaltır,
üretim de ancak boş yuvaya yazabildiği için kural tek yerde kalır. Yeni bir kavram gerekmiyor.

**Ses videoya bağlıdır.** Ses yuvası ancak video yuvası doluyken dolabilir. Videosuz kareye ses
üretilemez — tasarımın "videosuz kare ses kapsamına hiç girmez" kuralının (madde 31) kayıt
tarafındaki karşılığı.

---

## 4 · Silme: kare, katman ve paylaşılan dosya

Tasarım iki ayrı yıkıcı eylem tanıyor (madde 101, 80). İkisi de aynı iki adımdan geçiyor: **önce
dosya diskten kalkar, sonra günlüğe satır yazılır** — bugünkü sıranın aynısı, çünkü satır "bu artık
yok" demektir ve dosya dururken yazılamaz.

| Eylem | Hangi yuvalara satır yazılır | Hangi dosyalar silinir |
|---|---|---|
| **Kareyi sil** | Karenin dolu olan bütün yuvalarına `deleted` | O yuvaların dosyaları — paylaşılanlar hariç |
| **Videoyu sil** | Video ve (varsa) ses yuvasına `deleted` | Video ve ses dosyası — paylaşılanlar hariç |
| **Sesi sil** | Yalnız ses yuvasına `deleted` | Ses dosyası — paylaşılan değilse |

Videoyu silmek sesi de götürür, çünkü ses videoya bindirilidir ve altındaki video gidince
dayanaksız kalır (madde 80). Sesi silmek videoyu bırakır; video sessiz oynar.

**Paylaşılan dosya kuralı.** Bir dosya, **onu gösteren son canlı yuva da kapanana kadar** diskte
kalır (madde 101). Kopya kareler fotoyu, ses varyantları videoyu paylaştığı için bu kural
kaçınılmaz: A karesini silmek, aynı fotoyu kullanan B karesinin fotoğrafını götüremez.

Karar dosya başına ve satır yazılmadan **önce** veriliyor, böylece bugünkü sıra bozulmuyor: kapatılacak
yuvalar **hesaptan düşülerek** o dosyayı gösteren başka canlı yuva var mı diye bakılır; varsa dosya
yerinde bırakılır, yoksa silinir. Ancak bundan sonra kapanış satırları yazılır.

Sıra neden böyle: dosya silme patlarsa hiçbir şey değişmemiş olur ve hata bütün gerçektir. Satır
önce yazılsaydı, silme patladığında kayıt "yok" derken dosya diskte kalırdı.

**Kare silinmiş sayılır**, bütün yuvaları kapandığında — ayrıca bir "kare silindi" işareti
yazılmaz.

Bekleyen kareyle karışmaz, çünkü galeri sorusu "yuva boş mu" değil, bugünküyle aynı soru: **karenin
hiç satırı yok mu, yoksa kapanmış satırları mı var.** Hiç satırı olmayan kare bekliyordur ve
galeride durur; kapanmış satırları olan kare silinmiştir ve galeride durmaz. 3. bölümdeki "boş
yuva" ikisini de kapsar; bu ayrımı yapan kural odur, doluluk değil.

**Galeri yalnız foto yuvasına bakar.** Fotoyu tek başına silen bir eylem yok — foto taban katman,
onu silmek kareyi silmek demek. Dolayısıyla karenin galeride durup durmadığı bugünkü kuralın
aynısıyla cevaplanıyor, yalnız artık dosya yerine foto yuvası okunuyor: `done` ya da `failed` ise
durur, satırı hiç yoksa ya da `queued` ise bekleyen olarak durur, `deleted` ya da `removed` ise
durmaz. Video ve ses yuvaları bu kararın dışında; onlar karenin görünümünü değiştirir, varlığını
değil.

---

## 5 · Galeri sırası kare kimliği tutar

Sıra dosyası bugün dosya adları tutuyor. İki kare aynı foto dosyasını paylaşabildiği an bu liste
hangi kareyi kastettiğini söyleyemez hâle gelir; bu yüzden **kare kimliklerine** geçiyor.

**Geriye uyum:** `.png` ile biten eski girdi, uzantısı atılarak kare kimliği sayılır — 2. bölümdeki
uyumun aynısı. Kullanıcının düzenlediği sıra hiçbir projede kaybolmaz.

Sürüklemenin kendisi, sıranın üretim sırası olması ve bekleyen karenin sürüklenebilmesi bu görevde
değil — Görev 8'in işi. Burada yalnız listenin **neyi** tuttuğu değişiyor.

---

## 6 · Uç noktalar

Şekiller korunuyor; arayüz bu görevde hiç değişmediği için bugünkü alanlar aynen duruyor.

| Uç nokta | Değişen |
|---|---|
| `GET …/frames` | Her kare iki alan kazanır: `id` (kare kimliği) ve `layers` (dolu yuvalar ve dosyaları). `file` alanı **aynen kalır** ve foto dosyasını göstermeye devam eder — bugünkü arayüz onu okuyor |
| `POST …/photos/delete` | Yalnız foto dosyasını değil, karenin **bütün** katman dosyalarını götürür; paylaşılan dosyaya dokunmaz |
| Fotoğrafı sunan uç nokta | Değişmez — o bir **dosya** adresidir, kare adresi değil |

**Katman silmenin kendi uç noktası bu görevde açılmıyor.** Videoyu ve sesi tek tek silmek arayüzden
ancak Görev 26'da isteniyor; kuralı burada kuruluyor, uç noktası orada açılacak. Kural erken,
yüzeyi zamanında.

---

## 7 · Testler

Arka uç `pytest`, sahte port'larla — ComfyUI yok, Drive yok, dil modeli yok. **Full TDD:** her
davranış için önce kırmızı test, sonra onu geçiren en küçük kod.

**Kare ve katman okuma**
- `frame` ve `layer` alanı olmayan eski satır, foto katmanı olarak okunur; kimliği dosya adının
  uzantısız hâlidir.
- Aynı karenin iki farklı katmanı birbirinin durumunu etkilemez.
- Aynı **dosyayı** gösteren iki farklı karenin yuvaları birbirinden bağımsız kapanır.

**Yuva kuralı**
- Boş video yuvasına üretim yazılır.
- Dolu video yuvasına ikinci video yazılamaz.
- `failed` satırlı yuva **dolu** sayılır — üretim yazılamaz, kapsam dışıdır.
- `deleted` satırlı yuva **boş** sayılır — üretim yeniden yazılabilir.
- `queued` satırı yuvayı boşaltır (Tekrar dene yolu).
- Videosuz kareye ses yazılamaz.

**Yuva ile kuyruk borcu ayrı** *(v4'te kapatılan hatanın nöbetçisi)*
- Fotoğrafı silinen karenin foto yuvası boştur ama kuyruk onu **borçlu değildir** — kare yeniden
  üretilmez. v4'ün bu testi aynen korunur ve yeni kuralla birlikte de geçer.
- `failed` satırlı kare kendiliğinden yeniden denenmez.

**Silme**
- Kareyi silmek foto, video ve ses dosyalarının üçünü birden diskten kaldırır.
- Videoyu silmek üstündeki sesi de kaldırır; foto ve kare yerinde kalır.
- Sesi silmek videoyu ve fotoyu bırakır.
- Paylaşılan foto: iki kareden biri silinince dosya diskte kalır; ikincisi de silinince kalkar.
- Dosya silme patlarsa günlüğe kapanış satırı yazılmaz — kayıt ile disk ayrışmaz.
- Bütün yuvaları kapanan kare galeride görünmez.
- Hiç satırı olmayan kare (bekleyen) galeride görünür — silinmiş sayılmaz.
- Videosu silinmiş kare galeride durur — video yuvası karenin varlığını belirlemez.

**Sıra dosyası**
- Kare kimlikleriyle yazılır ve okunur.
- `.png` ile biten eski girdiler kimliğe çevrilerek okunur; kullanıcının sırası korunur.
- Silinen karenin kimliği sıradan düşer.

---

## 8 · Kabul kriteri

`pytest` yeşil ve şu iki cümle testlerle kanıtlanmış:

1. Videolu bir kareye ikinci video eklenemiyor — dolu yuvaya üretim yazılamıyor.
2. Silinen bir karenin hiçbir katman dosyası geride kalmıyor; paylaşılan dosya ise son sahibi gidene
   kadar yerinde duruyor.

Arayüz bu görevde hiç değişmiyor, dolayısıyla ekranda görülecek bir şey yok. Katman yığınının
kullanıcıya görünmesi Blok 5 ile başlıyor.

## 9 · Sonraki görevlere bırakılanlar

Bu görevin bilerek açık bıraktığı ve nerede kapanacağı:

| Bırakılan | Nerede kapanır |
|---|---|
| Kimliğin ve dosya adının yeni şeması (`P11_3`, `P11_3_V1_0`) | Görev 2 |
| Eski adlı dosyaların yeni şemayla birlikte yaşaması | Görev 2 |
| Kuyruğun iş türü tanıması (foto · video · ses) | Görev 3 |
| Kopya karenin doğması ve paylaşılan dosyayı göstermesi | Görev 15 |
| Katman silmenin uç noktası ve arayüzü | Görev 26 |
| Arayüzün `file` yerine `id` okumaya geçmesi | Görev 7-8 |
