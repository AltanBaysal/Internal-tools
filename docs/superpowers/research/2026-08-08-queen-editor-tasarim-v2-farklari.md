# Queen Editor — Tasarım v2 Farkları

**Tarih:** 2026-08-08 · **Yöntem:**
[fark çıkarma tasarımı](../specs/2026-08-08-queen-editor-tasarim-v2-fark-cikarma-design.md) ·
[uygulama planı](../plans/2026-08-08-queen-editor-tasarim-v2-fark-cikarma.md)

> **İsim çakışması — okumadan önce.** Tasarım projesindeki **"Basit v2"** sürümü, repodaki
> **v3 yol haritasına** karşılık gelir; repodaki spec numaralarıyla aynı şey değildir. Tasarımın
> kendi handoff belgesi de bunu not düşüyor. Bu belgede ikisi hep tam adıyla anılır: **tasarım v2**
> ve **roadmap v3**. Yalın "v2" hiçbir yerde kullanılmaz.

**Bu belge karar vermez.** Farkı ve çelişkiyi işaretler; hangisinin kazanacağına karar vermek
okuyanın işidir.

Farklar üç bağımsız yolla çıkarıldı; üçü de birbirini görmeden çalıştı:

| Yol | Neye demirledi | Ne göremezdi |
|---|---|---|
| **1 · Anlatı** | Tasarımın yazılı kararları | Yazıya geçmemiş her şey |
| **2 · Tasarım kaynağı** | v2 ekranlarının kendisi (anlatıyı hiç okumadı) | Kararların gerekçesi |
| **3 · Ters yön** | Bugünkü uygulama → tasarımda ara | Bugün tutamağı olmayan yenilikler |

Her satırın yanında kaç yolun gördüğü yazıyor: **3/3 kesin · 2/3 güçlü · 1/3 elle doğrulandı.**

---

## 1 · Özet

Tasarım v2 tek bir karardan doğuyor: **üretim, "başlat / bitir"li tek seferlik bir iş olmaktan çıkıp
sürekli açık bir kuyruk oluyor.** Bunun üç büyük sonucu var. Birincisi, sağ panel üçe bölünüyor —
form, kuyruk ve (şimdilik boş) agent paneli — ve form artık **hiç kilitlenmiyor**: kuyruk akarken
sonraki parti yazılıp eklenebiliyor. İkincisi, ilerleme dili değişiyor: payda kalkıyor, geriye tek
dürüst sayı kalıyor — **kaç kare bekliyor**. Üçüncüsü, galeri tek bir diziye dönüyor; bekleyen,
çalışan ve üretilmiş kareler aynı numaralandırmayı paylaşıyor ve **numara yönü tersine dönüyor** —
en yeni en üstte, 1 en altta, export ise alttan yukarı okunuyor.

Bunların yanında iki uygulama geneli karar var: **yıkıcı eylem butonu** her yerde aynı görünüyor
(dolgusuz kırmızı + çöp ikonu, dolu kırmızı hiçbir yerde yok) ve **silme onayının dili** seçimin
içeriğine göre üçe ayrılıyor — bekleyen kareye "fotoğraf silinsin mi?" demek yanlış olurdu.

---

## 2 · Doğrulama tablosu

`●` gördü · `—` görmedi · `✎` yalnız bu yol gördü, kaynağa dönülüp elle doğrulandı

### Panel

| # | Fark | Tür | Y1 | Y2 | Y3 | Damga |
|---|---|---|---|---|---|---|
| P1 | Panel üçe ayrılıyor, sağına ikon şeridi geliyor | görsel | ● | ● | ● | 3/3 |
| P2 | Her panelin üstünde küçük başlık | görsel | — | — | ✎ | 1/3 |
| P3 | İlerleme/bitiş/hata bilgisi formdan kuyruk paneline taşınıyor | davranış | ● | ● | ● | 3/3 |
| P4 | **Üret** → **Üretime ekle**; iş başlatmak yerine kuyruğa ekliyor | davranış | ● | ● | ● | 3/3 |
| P5 | Panel hiç kilitlenmiyor | davranış | ● | ● | ● | 3/3 |
| P6 | **Ekleniyor…** ara durumu — alanlar açık kalıyor | davranış | ● | ● | ● | 3/3 |
| P7 | Yeşil "kuyruğa eklendi" kartı, kendiliğinden kayboluyor | davranış | ● | ● | ● | 3/3 |
| P8 | Eklenemezse tek satır "Kuyruğa eklenemedi" | davranış | ● | ● | ● | 3/3 |
| P9 | prompt × varyant hesabı kalkıyor | görsel | ● | ● | ● | 3/3 |
| P10 | Format hatası tek satıra iniyor, detay verilmiyor | davranış | ● | ● | ● | 3/3 |
| P11 | Format hatası akan kuyruğu etkilemiyor | davranış | — | ● | ● | 2/3 |
| P12 | Model açılır listesi geliyor | davranış | ● | ● | ● | 3/3 |
| P13 | Varyant 1–8'e iniyor, hata durumu kalkıyor | davranış | ● | — | ● | 2/3 |
| P14 | **Durdur** → **Duraklat** + "Duraklatılıyor…" ara durumu | davranış | ● | ● | ● | 3/3 |
| P15 | Duraklatınca çalışan karenin akıbeti | davranış | ● | ● | ● | **çelişki** |
| P16 | Sayaç paydayı bırakıyor → "N kare bekliyor" | görsel | ● | ● | ● | 3/3 |
| P17 | İlerleme çubuğu ve yüzde kalkıyor | görsel | ● | ● | ● | 3/3 |
| P18 | "şimdi: …" satırı kalkıyor | görsel | ● | ● | ● | 3/3 |
| P19 | Canlı yanıp sönen durum noktası geliyor | görsel | ● | ● | ● | 3/3 |
| P20 | **İptal et** → **Kuyruğu boşalt** + onay penceresi | davranış | ● | ● | ● | 3/3 |
| P21 | Kuyruğu boşalt durmuş kuyrukta da görünüyor | davranış | ● | ● | ● | 3/3 |
| P22 | Boşalttıktan sonra "Kuyruk boş"a dönüyor, yeşil kart çıkmıyor | davranış | — | — | ✎ | 1/3 |
| P23 | Bitiş kartı "N kare üretildi" + hatalı aynı cümlede | davranış | ● | ● | ● | 3/3 |
| P24 | "Kuyruk boş" diye ayrı bir hâl geliyor | davranış | ● | ● | ● | 3/3 |
| P25 | Hatalı kare satırı tıklanabilir: "galeride göster" | davranış | ● | ● | ● | 3/3 |
| P26 | Durma kuralı: "3 ardışık başarısız kare" mi, "3 deneme" mi | davranış | ● | ● | ● | **çelişki** |
| P27 | Kalan kare sayısı 26 puntoya büyüyor | görsel | — | ✎ | — | 1/3 |
| P28 | Sağ sütun 320 → 368 piksele çıkıyor | görsel | — | ✎ | — | 1/3 |
| P29 | AI agent paneli açılıyor (içi boş) | görsel | ● | ● | ● | 3/3 |

### Galeri

| # | Fark | Tür | Y1 | Y2 | Y3 | Damga |
|---|---|---|---|---|---|---|
| G1 | Numara yönü tersine dönüyor — en yeni en üstte, 1 en altta | davranış | ● | ● | ● | 3/3 |
| G2 | Bekleyen ve çalışan karede de rozet (soluk tonda) | görsel | ● | ● | ● | 3/3 |
| G3 | Dört kova tek diziye iniyor; kare yerinde fotoğrafa dönüşüyor | davranış | ● | ● | ● | 3/3 |
| G4 | Çalışan kare bekleyenlerin **altına** iniyor | görsel | — | ● | ● | 2/3 |
| G5 | Hatalı karenin ızgaradaki yeri | görsel | ● | ● | — | **çelişki** |
| G6 | Bekleyen kareler de seçilebiliyor; çalışanda daire hiç yok | davranış | ● | ● | ● | 3/3 |
| G7 | Bekleyen karta basılı tutunca "üretilince sıralanabilir" ipucu | davranış | ● | ● | ● | 3/3 |
| G8 | Silme onayı seçimin içeriğine göre üç metne bölünüyor | davranış | ● | ● | ● | 3/3 |
| G9 | Boş galeri metni yeni butonun adını anıyor | görsel | ● | ● | ● | 3/3 |
| G10 | **Tekrar dene** akan kuyruğu kesmiyor, kareyi sonuna alıyor | davranış | ● | — | ● | 2/3 |
| G11 | Sürükleme "basılı tut" eşiğiyle başlıyor | davranış | — | ✎ | — | 1/3 |
| G12 | Sayfa yenilenince kırmızı kareler kayboluyor | davranış | ✎ | — | — | 1/3 |

### Foto detay

| # | Fark | Tür | Y1 | Y2 | Y3 | Damga |
|---|---|---|---|---|---|---|
| F1 | Detay üç hâli de açıyor: üretilmiş · bekleyen · çalışan | davranış | ● | ● | ● | 3/3 |
| F2 | Negatif kutusu geliyor, prompt ile alanı eşit paylaşıyor | görsel | ● | ● | ● | 3/3 |
| F3 | Sıra sayacı ve oklar bekleyen + çalışan kareleri de sayıyor | davranış | ● | ● | ● | 3/3 |
| F4 | Bekleyende buton **Kuyruktan çıkar**, onay sormuyor | davranış | ● | ● | ● | 3/3 |
| F5 | Bekleyende "Dosya adı (planlanan)", soluk tonda | görsel | — | ● | ● | 2/3 |

### Projeler ve genel

| # | Fark | Tür | Y1 | Y2 | Y3 | Damga |
|---|---|---|---|---|---|---|
| N1 | Yıkıcı eylem standardı — dolu kırmızı buton hiçbir yerde yok | görsel | ● | ● | ● | 3/3 |
| N2 | Export sırası tersine dönüyor — en alttaki kare listenin ilki | davranış | ● | ● | ● | 3/3 |
| N3 | 8'den çok projede kaydırma çubuğu + solma perdesi | görsel | — | ✎ | — | 1/3 |
| N4 | Proje kartının silme butonu yıkıcı eylem standardına uymuyor | görsel | ● | — | — | **çelişki** |
| N5 | App bar'ın tonu | görsel | — | — | ● | **çelişki** |

---

## 3 · Davranış farkları — ekran ekran

### Panel · Üretime ekle

**Üret → Üretime ekle.** *Bugün:* Üret'e basınca o partinin kareleri planlanır ve hemen üretime
girer; üretim sürerken buton ekrandan kalkar, ikinci parti gönderilemez, gönderilirse "Zaten bir
üretim sürüyor" cevabı gelir. *Tasarım v2'de:* butona basınca prompt × varyant kadar kare kuyruğun
sonuna eklenir, kuyruk boş değilse üretim kendiliğinden akar, ayrı bir başlatma yoktur ve buton hiç
kaybolmaz.

**Panel kilidi kalkıyor.** *Bugün:* üretim başlar başlamaz prompt listesi, negatif ve varyant
kutuları soluklaşıp tıklanamaz olur. *Tasarım v2'de:* panel hiç kilitlenmez — kuyruk akarken sonraki
parti yazılıp eklenebilir.

**Ekleniyor… ara durumu.** *Bugün:* butona basıldığı an yazı "Başlatılıyor…" olur, buton pasifleşir
ve aynı anda üç giriş kutusu da kapanır; dönen bir gösterge yoktur. *Tasarım v2'de:* yalnız buton
kısa süre pasifleşip yanında dönen gösterge çıkar, alanlar açık kalır, sadece iki kez basılamaz.

**Ekleme onayı.** *Bugün:* bir partinin kabul edildiğine dair ayrı bir onay yoktur; onay, ilerleme
kartının belirmesidir. *Tasarım v2'de:* butonun altında yeşil kart "✓ 48 kare kuyruğa eklendi" der
ve birkaç saniye sonra kendiliğinden kaybolur; eklenemezse aynı yerde tek satır "Kuyruğa eklenemedi"
çıkar.

**Format hatası.** *Bugün:* liste okunamayınca kutu kırmızı çerçevelenir ve altında beklenen biçimi,
örnek listeyi ve ham teknik hatayı içeren uzun bir metin belirir. *Tasarım v2'de:* kutu kırmızı
çerçevelenir ve tek satır "Format hatası — liste okunamadı" yazar; satır ve konum verilmez. Ayrıca
akan kuyruk bundan hiç etkilenmez — bugün böyle bir durum oluşamıyor, çünkü üretim sürerken kutular
kilitli.

**Model seçimi.** *Bugün:* panelde model alanı yoktur, üretim tek sabit kurulumla koşar.
*Tasarım v2'de:* prompt listesinin üstünde model açılır listesi durur; model listesi yüklenemezse
bu ayrı bir ekran değildir, kuyruk panelindeki ölümcül hata kartıyla aynı kalıba girer.

**Varyant.** *Bugün:* kutu 1–26 arasını kabul eder; boş bırakılıp gönderilirse üretim başlamaz, kutu
kırmızıya döner ve hata yazısı çıkar. *Tasarım v2'de:* alan 1–8 kabul eder, dışına çıkan değer
yazılamaz, boşaltılırsa kendiliğinden 1'e döner ve hiçbir hata durumu doğmaz.

### Panel · Kuyruğu takip et

**Durum bilgisinin yeri.** *Bugün:* ilerleme, duraklama, durma, tamamlanma ve yarım kalma kartlarının
hepsi formun hemen altındadır. *Tasarım v2'de:* formun altında hiçbir durum kartı kalmaz; kullanıcı
durumu görmek için ikon şeridinden kuyruk paneline geçer.

**Durdur → Duraklat.** *Bugün:* buton *Durdur* der, basılınca *Durduruluyor…* olur; kart bu sırada
değişmez. *Tasarım v2'de:* buton *Duraklat* olur; basınca kartın başlığı "Duraklatılıyor…"a döner ve
noktası hâlâ canlıdır, ardından "Duraklatıldı"ya geçilir.

**Sayaç dili.** *Bugün:* kart "17 / 48" biçiminde bölmeli sayaç gösterir; duraklayınca da durunca da
tamamlanma oranı yazılır. *Tasarım v2'de:* payda kalkar, geriye tek büyük sayı ve yanında "kare
bekliyor" kalır. Gerekçe yazılı: kuyruğa ekledikçe toplam büyüdüğü için paydalı sayaç her eklemede
geriye sıçrar.

**Kuyruğu boşalt.** *Bugün:* yalnız duraklatılmış hâlde soluk, ikonsuz bir *İptal et* butonu vardır
ve basılınca hiçbir şey sorulmadan kalan kuyruk atılır. *Tasarım v2'de:* aynı yerde çöp ikonlu,
dolgusuz kırmızı *Kuyruğu boşalt* durur ve onay sorar — "Bekleyen 8 kare üretilmeden kuyruktan çıkar.
Üretilmiş fotoğraflar galeride kalır." Dosya silinmediği için "geri alınamaz" denmez. Buton
duraklatılmış **ve durmuş** kuyrukta görünür; akarken hiç yoktur, önce duraklatmak gerekir.

**Boşaltmadan sonra.** *Bugün:* kalan iş atılınca panel boşta hâline döner ve sayım önizlemesi
belirir. *Tasarım v2'de:* panel "Kuyruk boş" kartına döner; yeşil "tamamlandı" kartı **gösterilmez**
— o kart yalnız doğal bitişin onayıdır.

**Bitiş kartı.** *Bugün:* yeşil kart "48 / 48 üretildi — tamamlandı" der ve hatalı kare olsa bile bu
cümle değişmez; hatalı sayısı üretim bitince ekrandan kaybolur. *Tasarım v2'de:* kart "20 kare
üretildi" der, hatalı varsa aynı cümlenin içinde kırmızıyla söyler.

**Hatalı kareye gitmek.** *Bugün:* ilerleme kartındaki "2 fotoğraf üretilemedi — diğerleri devam
ediyor" satırı sadece bilgidir, tıklanamaz. *Tasarım v2'de:* satır altı çizili ve tıklanabilirdir:
"3 kare üretilemedi — galeride göster".

**Kuyruk boş hâli.** *Bugün:* yapılacak iş kalmadığında "kuyruk" diye bir kavram ekranda hiç
görünmez. *Tasarım v2'de:* kuyruk panelinde soluk noktalı "Kuyruk boş" kartı ve altında "Üretime
ekle panelinden kare gönder." yazar; hiçbir buton yoktur.

### Galeri

**Numara yönü tersine dönüyor.** *Bugün:* rozet galerideki konumu yukarıdan sayar — en üstteki (en
yeni) fotoğraf 1'dir; yeni kare geldiğinde altındaki her şeyin numarası bir kayar.
*Tasarım v2'de:* numara üretim sırasıdır, yeni kare en büyük numarayı alır ve en üstte durur; aşağı
indikçe numara küçülür, en alttaki 1'dir ve yeni kare eklendiğinde alttakilerin numarası hiç
değişmez.

**Kovalar tek diziye iniyor.** *Bugün:* galeri dört kovaya bölünür — önce çalışan kare, sonra
kırmızı hatalı kareler, sonra kesikli bekleyenler, sonra fotoğraflar. Bir kare üretilince bekleyen
öbekten çıkıp fotoğraf bloğunun başına iner, yani yer değiştirir ve etrafındakiler kayar.
*Tasarım v2'de:* her kare kendi sırasında durur ve üretilince **aynı yerde** fotoğrafa dönüşür; sıra
hiç oynamaz.

**Bekleyen kare seçilebilir oluyor.** *Bugün:* seçim halkası yalnız üretilmiş fotoğraflarda belirir;
bekleyen kare seçilemez, kuyruktan çıkarılamaz. *Tasarım v2'de:* seçim modu tektir — bekleyen ve
üretilmiş kareler birlikte seçilir, halka ikisinde de aynı görünür, farkı kartın kesikli görünümü
söyler. Çalışan karede halka **hiç yoktur** (pasif bir halka "neden seçemiyorum?" sorusu doğurur) ve
"Tümünü seç" onu atlar. Alt bardaki sayı tektir, türlere bölünmez.

**Silme onayı üçe ayrılıyor.** *Bugün:* her onay "N fotoğraf silinsin mi? · Bu işlem geri alınamaz."
der. *Tasarım v2'de:* yalnız bekleyen seçiliyse "N kare kuyruktan çıkarılsın mı? · Bu kareler
üretilmeyecek. Galerideki fotoğraflara dokunulmaz." denir, buton *Çıkar* olur ve "geri alınamaz"
hiç geçmez — dosya silinmiyor, aynı prompt yeniden eklenebilir. Karışık seçimde cümle iki parçalı
kurulur: "2 fotoğraf silinsin, 2 bekleyen kare kuyruktan çıkarılsın mı?"

**Sürükleme ipucu.** *Bugün:* bekleyen karta basılı tutulunca hiçbir şey olmaz; kullanıcı neden
sürükleyemediğini öğrenemez. *Tasarım v2'de:* kart kalkmaz ama yerinde "üretilince sıralanabilir"
ipucu belirir; sürükleme kare üretilir üretilmez açılır.

**Tekrar dene.** *Bugün:* kırmızı karedeki buton yalnız boşta iken çalışır; üretim sürerken
basılırsa istek geri çevrilir. *Tasarım v2'de:* akan kuyruk kesilmez, tekrar denenen kare kuyruğun
sonuna girer ve sıradaki işlerin önüne geçmez.

### Foto detay

**Üç hâl, tek iskelet.** *Bugün:* detay sayfası yalnız üretilmiş fotoğrafı tanır; bekleyen ya da
çalışan bir karenin adresine gidilirse "Fotoğraf bulunamadı" kartı çıkar. *Tasarım v2'de:* üçü de
aynı sayfayı kullanır — bekleyende kesikli "bekliyor / henüz üretilmedi" alanı, çalışanda dönen
gösterge belirir ve çalışan kare üretimi bitince sayfa yeniden yüklenmeden fotoğrafa döner.

**Butonun adı hâle göre değişiyor.** *Bugün:* altta tek buton vardır — *Sil* — ve onay penceresi
açar. *Tasarım v2'de:* bekleyende buton *Kuyruktan çıkar* olur ve onay sormaz (dosya silinmiyor),
sonraki kare açılır; çalışan karede buton pasiftir.

**Sayaç ve oklar tüm diziyi geziyor.** *Bugün:* "7 / 48" sayacı yalnız var olan fotoğrafları sayar;
oklar ve klavye yalnız onların arasında gezer. *Tasarım v2'de:* rozet dizisi = sıra sayacı = ok
sırası; oklar bekleyen ve çalışan kareler dahil tüm galeri sırasında gezer. Uçlarda pasifleşme ve
sarmama kuralı aynı kalır.

### Genel

**Export sırası tersine dönüyor.** *Bugün:* indirilen dosya galeriyi yukarıdan aşağı okur; ilk satır
en üstteki (en yeni) karedir. *Tasarım v2'de:* sıra numaraya göre artandır — galerinin **en
altındaki** kare listenin ilki ve videonun ilk karesidir. Dosyaya yalnız üretilmiş fotoğraflar girer.

---

## 4 · Görsel dil farkları

**İkon şeridi.** *Bugün:* sağdaki 320 piksellik panel tek bir yüzeydir, içine girip çıkılacak bir
yer ve panelin kendi adı yoktur. *Tasarım v2'de:* panelin sağına 48 piksellik dikey ikon şeridi
gelir; aktif ikon mor renge döner ve sağında 2 piksellik mor çizgi belirir, her panelin üstünde
küçük büyük harfli bir başlık durur. Sağ sütunun toplam genişliği 368 piksele çıkar.

**Ana butonun yüzü.** *Bugün:* mor buton parıltı ikonuyla "Üret" der. *Tasarım v2'de:* artı ikonuyla
"Üretime ekle" der; basılınca dönen halkayla "Ekleniyor…" olur.

**Kuyruk kartının tipografisi.** *Bugün:* durum kartındaki sayı 13 punto, mor renkte ve bölmeli
("12 / 48"). *Tasarım v2'de:* kalan kare sayısı 26 punto tek bir rakamdır, yanında 13 punto normal
yazıyla "kare bekliyor" durur; sayı normalde en açık yazı renginde, üretim durunca kırmızıdır.

**Canlı nokta.** *Bugün:* motorun çalıştığını yalnız ilerleme çubuğunun dolması anlatır.
*Tasarım v2'de:* durum başlığının solunda 7 piksellik yuvarlak nokta durur — akarken mor ve yaklaşık
1,2 saniyelik döngüyle sönüp yanar, duraklatılırken hâlâ atar, duraklatılınca sabitlenip soluk griye
döner, durunca kırmızı, bitince yeşil, kuyruk boşken en soluk gri olur.

**İlerleme çubuğu ve "şimdi:" satırı kalkıyor.** *Bugün:* kartta 5 piksellik mor dolan çubuk ve o an
işlenen prompt'un tek satırlık özeti vardır. *Tasarım v2'de:* ikisi de yoktur; kartta yalnız durum
başlığı ve kalan kare sayısı kalır.

**Bekleyen ve çalışan karede rozet.** *Bugün:* sıra rozeti yalnız gerçek fotoğraflardadır; kesikli
"bekliyor" karesi ve dönen göstergeli kare rozetsizdir. *Tasarım v2'de:* üçünde de rozet vardır,
üretilmişlerle aynı dizinin devamıdır, sadece daha soluk zemin ve daha soluk yazı tonundadır.

**Çalışan karenin yeri.** *Bugün:* dönen göstergeli kare ızgaranın en başına, bütün bekleyenlerin de
üstüne konur. *Tasarım v2'de:* bekleyenler en üstte durur, çalışan kare onların altında, üretilmişlerin
hemen üstünde yer alır — numara dizisi kesintisiz iner.

**Yıkıcı eylem standardı.** *Bugün:* onay penceresindeki son buton dolu kırmızı zeminli, beyaz yazılı
ve ikonsuzdur; galerideki ve karttaki silme butonları ise dolgusuz kırmızı çerçevelidir — yani iki
ayrı dil bir arada. *Tasarım v2'de:* dolu kırmızı buton hiçbir yerde kullanılmaz; onay penceresinin
son butonu da dolgusuz kırmızı çerçeve + kırmızı metin + solunda çöp ikonudur. Kapsamı: fotoğraf
silme (seçim modu ve detay), proje silme, kuyruğu boşaltma ve bunların onay pencereleri.

**Uzun proje listesi.** *Bugün:* proje sayısı artınca sayfa doğal olarak kayar, listenin devam
ettiğine dair görsel bir işaret yoktur. *Tasarım v2'de:* sekizden çok proje olunca ızgaranın sağında
koyu gri yuvarlatılmış ince bir kaydırma çubuğu ve altta yaklaşık 70 piksellik, sayfa zeminine
karışan bir solma perdesi belirir.

**Boş galeri metni.** *Bugün:* "Prompt'ları yaz, **Üret'e** bas — fotoğraflar burada belirecek."
*Tasarım v2'de:* "Prompt'ları yaz, **Üretime ekle**'ye bas — fotoğraflar burada belirecek."

**Bekleyende dosya adı.** *Bugün:* detayda etiket her zaman "Dosya adı"dır, değer tam parlaklıkta
yazılır. *Tasarım v2'de:* bekleyen karede etiket "Dosya adı (planlanan)" olur ve değer soluk tonda
yazılır.

---

## 5 · Roadmap v3 ile çelişkiler

Roadmap v3, tasarım tamamlanmadan **önce** yazıldı ve Madde 1 zaten "tasarım kaynak, repo
uygulayıcı" diyor. Aşağıdakiler karara bağlanmayı bekliyor — bu belge hangisinin kazanacağını
söylemez.

| Konu | Roadmap v3 ne diyor | Tasarım v2 ne diyor |
|---|---|---|
| **Buton adı** | "**Sıraya ekle**" | "**Üretime ekle**" |
| **Duraklat / Devam / İptal** | "Durdur / Devam et / İptal et — **Yok**"; "kuyruktan çıkarmanın tek yolu bekleyen kartı silmek" | Kuyruk panelinde **Duraklat**, **Devam et**, **Kaldığı yerden devam et** ve **Kuyruğu boşalt** var |
| **Seed alanı** | Bekleyen kart detayı: "prompt, negatif, **seed**" | "**Seed alanı yoktur** — üretilmiş fotoğrafta da yok, tutarlılık için hiçbirinde" |
| **Sıra yönü** | "kareler kuyruğun sonuna eklenir… beşi de galerinin **sonunda** kart olarak durur" | Numaralandırma **tersine döndü**: yeni kare en büyük numarayı alır, galerinin **en üstünde** durur |
| **Silinen numaranın akıbeti** | "silinen bekleyenin numarası **boşta kalır**, geri kullanılmaz" | "**Silme sonrası yeniden numaralanır** — delik kalmaz; 20 kareden 5 silinince kalanlar 1-15 olur" |
| **Elle devam** | "Kaldığı yerden devam et kartı **yalnızca ölümcül hatadan sonra** kalır" | Duraklatılmış kuyruk da elle **Devam et** ister |
| **Üretim süresi** (Madde 8) | Süre "fotoğrafın kaydında, oradan da foto detay sayfasında" görünecek | Detayın sağ sütununda süre alanı **yok**: yalnız Sıra, Dosya adı, Prompt, Negatif |
| **Üç panelli şerit** | Hiç geçmiyor — roadmap tek panel varsayıyor | Panel üçe ayrılıyor, üçüncüsü boş **AI agent** paneli |

**Roadmap'in açık sorusu karara bağlanmış.** Roadmap "bitiş kartı kalsın mı, yoksa sessizce mi
bitsin?" diye soruyordu. Tasarım v2 cevap veriyor: kart **kalır** ("Kuyruk tamamlandı", yeşil) ama
kuyruk elle boşaltıldığında **gösterilmez** — o kart yalnız doğal bitişin onayıdır.

---

## 6 · Öksüz davranışlar

Bugün uygulamada var, tasarım v2'de karşılığı yok. Bilerek mi kaldırıldı yoksa tasarım mı atladı —
belge karar vermiyor.

| Davranış | Kaç yol | Not |
|---|---|---|
| Başka projede üretim sürerken buton pasifleşiyor ve "Üretim sürüyor: X — bitmesini bekle." yazıyor | 3/3 | Tasarım projeler arası tek işçi kısıtından hiç söz etmiyor |
| Bağlantı koptuğunda ilerleme soluklaşıyor + "Sunucuya ulaşılamıyor — son bilinen: 17/48" kartı | 3/3 | Dayandığı ilerleme çubuğu tasarım v2'de zaten kaldırılmış |
| "Tümünü seç" ikinci kez basılınca tüm seçimi bırakıyor | 3/3 | Tasarım yalnız butonun varlığını ve çalışan kareyi atladığını yazıyor |
| Sürükleme sonrası sıra kaydedilemezse "Sıra kaydedilemedi" + sunucunun sırasına dönüş | 2/3 | Tasarım sıralamayı yalnız başarılı hâliyle anlatıyor |
| Proje ayarları yüklenemedi kartı ve proje açılırken bekleme hâli | 2/3 | Tasarım paneli hep dolu varsayıyor |
| Prompt kutusundaki soluk örnek liste (yer tutucu) | 1/3 ✎ | Tasarımın boş liste ekranında kutu tamamen boş |
| Projeler listesi yüklenirken dönen gösterge, yüklenemezse hata kartı | 2/3 | Tasarım yalnız dolu ve boş listeyi çiziyor |
| Galerinin ilk yükleme göstergesi | 1/3 ✎ | "Henüz fotoğraf yok" yalnız gerçekten boş olduğu bilinince yazılıyor |
| Detayda "Fotoğraf bulunamadı" kartı | 1/3 ✎ | Tasarım detayın yalnız üç hâlini tanıyor |
| Üretime basınca panelin önce kaydedilmesi; kayıt başarısızsa üretimin hiç başlamaması | 2/3 | Tasarım saklamayı söylüyor ama gönderime bağlanıp bağlanmadığını söylemiyor |

---

## 7 · Tasarım sadakati denetimi

**Bu bölüm tasarım v2 farkı değildir.** Buradaki maddeler, uygulamanın **bugün zaten** tasarımdan
saptığı yerlerdir — tasarım v2'ye geçilmese bile geçerliler. Ayrı durmalarının sebebi şu: "bugün
yanlış" ile "v2'de değişecek" farklı iki iddiadır; tek listede birleşirlerse hangisinin tasarımcı
kararı, hangisinin uygulama hatası olduğu okunamaz hâle gelir.

| Sapma | Bugün | Tasarım ne diyordu | Kaç yol |
|---|---|---|---|
| **Model alanı hiç yok** | Panel doğrudan prompt listesiyle başlıyor | Model açılır listesi **v1'den beri** panelin ilk alanı | 3/3 |
| **Format hatası fazlasını söylüyor** | Beklenen biçim, örnek liste ve ham teknik hata basılıyor | "Hata detayı verilmez, satır/konum gösterilmez" — **v1 kuralı** | 3/3 |
| **Aynı hatalı kare iki kez çiziliyor** | Bitmiş koşuda kare hem kırmızı hem kesikli "bekliyor" olarak görünüyor | Hatalı kare tek bir kırmızı karedir | 2/3 |
| **Yarım kalan koşunun kartı başka konuşuyor** | "Üretim yarım kaldı — 17/48 tamamlandı", sebep yazmıyor | "Üretim durdu · 7/48 tamamlandı — üretilenler kaydedildi"; sayfa kapansa da metin aynı | 2/3 |
| **Üretim sürerken Tekrar dene çalışmıyor** | İstek "Zaten bir üretim sürüyor" diye geri çevriliyor | Tekil hata üretimi durdurmaz; buton o sırada da basılabilir olmalı | 2/3 |
| **Duraklatılmış/durmuş hâlde panel kilitli kalmıyor** | Kilit yalnız üretim akarken; duraklayınca kutular serbest | "(duraklatılmış/durmuş hallerde de kilitli)" | 1/3 ✎ |
| **Hatalı kareyle biten koşu yeşil kartı göstermiyor** | Kırmızı "Üretim yarım kaldı" + Kaldığı yerden devam et çıkıyor | Kısmi bitişte ayrı tasarım yok — yeşil bildirim yine gelir, hatalı kareler kırmızı kalır | 1/3 ✎ |
| **Seçim çubuğu 0 seçiliyken de duruyor** | Mod açıldıktan sonra tüm seçim kalksa bile çubuk "0 seçili" diyor | Çubuk "en az bir kare seçiliyken" görünür | 1/3 ✎ |
| **Seçim çubuğu yüzmüyor** | Çubuk kaydırılan içeriğe yapışık; ancak en aşağı kaydırınca görünüyor | Galerinin altında ortada **yüzen** şerit; liste sonuna ekstra boşluk bırakılır | 1/3 ✎ |
| **Varyant üst sınırı uydurulmuş** | En fazla 26 kabul ediliyor | v1: "üst sınır yok" · tasarım v2: "1–8" — bugünkü 26 ikisine de uymuyor | 1/3 ✎ |
| **Boş proje adında uyarı çıkmıyor** | Kutu boşken buton pasif, hiçbir uyarı yazılmıyor | "Geçersiz karakter **veya boş ad** girildiğinde aynı yerde uyarı çıkar" | 1/3 ✎ |
| **Yeni proje uyarısı yazarken değil, basınca çıkıyor** | Uyarı ancak gönderdikten sonra beliriyor | Uyarı girildiğinde çıkar ve uyarı varken buton pasif kalır | 2/3 |
| **Sıralama basılı tutma eşiği olmadan başlıyor** | Basıp hafifçe kaydırınca sürükleme hemen başlıyor | "Basılı tut + sürükle" | 1/3 ✎ |
| **Sayfa yenilenince kırmızı kareler kayboluyor** | Hatalı kareler yalnız o oturumun hafızasında | Hatalı kareler galeride kırmızı kalır ve tek tek tekrar denenir | 1/3 ✎ |

---

## 8 · Çelişkiler

Bunlar uygulama ile tasarım arasında değil, **tasarımın kendi içinde** ya da yollar arasında.
Tek yolla çalışılsaydı hiçbiri görünmezdi.

### 8.1 · Duraklatınca çalışan kare ne oluyor? *(tasarım kendi içinde çelişiyor)*

- Bir yerde: *"Duraklat'a basınca çalışan kare **yarıda kesilmez**: biter, sonra durur."*
- Başka yerde: *"Duraklayınca **yarım kalan kare** kuyruğa geri döner (7 → 8)."*

İkisi aynı kareyi farklı anlatıyor: biri kare tamamlanıyor diyor, diğeri yarım kalıp kuyruğa
düşüyor diyor. Bugünkü uygulama ikincisine yakın — render anında kesiliyor, kesilen kare
başarısızlık sayılmıyor ve numarasını koruyor.

### 8.2 · Hatalı kare galeride nerede duruyor? *(iki artboard aynı şeyi söylemiyor)*

Üretim sürerken çizilen ekranda hatalı kare **kendi sırasında**, üretilmişlerin arasında kırmızı
duruyor. Bitmiş galeri çiziminde ise hatalı kareler **en üstte blok hâlinde**. Bugünkü uygulama
ikincisini yapıyor.

### 8.3 · "3 deneme" neyi sayıyor?

Tasarım *"ölümcül hatada otomatik 3 deneme yapılır"* ve *"3 kez denendi"* diyor. Bugünkü uygulama
*"üst üste 3 başarısız kare"* sayıyor — yani biri **aynı işin** üç kez denenmesini, diğeri **üç ayrı
karenin** peş peşe patlamasını anlatıyor. Aynı sayı, farklı kural.

### 8.4 · Proje kartının silme butonu kendi standardına uymuyor

Tasarımın uygulama geneli kuralı: yıkıcı eylem = dolgusuz buton + kırmızı çerçeve + kırmızı metin +
çöp ikonu, ve proje silme bu kuralın **örnekleri arasında sayılmış**. Ama tasarımın kendi proje
kartı çiziminde buton çerçevesiz, yazısız, yalnız kırmızı çöp ikonundan ibaret.

### 8.5 · App bar'ın tonu

Tasarımın bir cümlesi *"gövdeden daha **koyu** bir şeritle ayrılır"* diyor; başka bir cümlesi
*"gövde en koyu, app bar ve kartlar bir ton **açık**"* diyor. Çizilmiş ekranlar ve bugünkü uygulama
ikincisini kullanıyor.

### 8.6 · Uzun proje listesi kayar mı, kendi içinde mi kayar?

Yazılı anlatı *"ızgaranın kendi içinde ayrı bir kaydırma alanı yok"* diyor; ekran çizimi ise sekiz
projeden sonra ızgaranın sağına kaydırma çubuğu ve alta solma perdesi koyuyor.

---

## 9 · Zayıf sinyaller ve doğrulanamayanlar

Tek yolun gördüğü her madde kaynağa dönülüp elle doğrulandı. **Doğrulanamayan madde çıkmadı** —
2. bölümdeki `✎` işaretlilerin hepsi kaynakta karşılığını buldu ve ana listeye girdi.

Buna karşılık, çakıştırma **üç bulguyu düzeltti** — bir yolun kör noktasından geçmiş, başka bir yol
tarafından yakalanmışlar:

| Düzeltilen | Ne olmuştu |
|---|---|
| **Seçim modunda Esc kısayolu** | Yol 1 bunu "öksüz" saydı (yazılı anlatıda yok). Ekran çiziminde tasarımcı notu açıkça "Esc veya Vazgeç çıkar" diyor — tasarımda **var**. Yol 1 wireframe'i okumadığı için göremezdi. |
| **Sürükleme sırasındaki görüntü** | Yol 1 "tasarım söylemiyor" dedi. Ekranda çizili: sürüklenen kare eğilip büyüyor, hedef konumda kesikli mor yuva beliriyor. Yine yazılı anlatıda yok, ekranda var. |
| **Detaydan tekil silmede onay** | Yol 2 "tasarım söylemiyor" dedi. Yazılı anlatı söylüyor: "Altta Sil — aynı onay penceresini kullanır." Yol 2 anlatıyı bilerek okumadığı için göremezdi. |

Bu üç düzeltme, yöntemin kendi sağlamasıdır: iki yol tasarımın **yazısını** göremediği için, bir yol
da tasarımın **ekranını** göremediği için kaçırdı. Üçü birleşince açık kapanıyor.

---

## 10 · Tasarımın cevaplamadıkları

Bunlar fark değil, tasarım v2'de karar verilmemiş noktalar.

- **AI agent paneli boş.** Üçüncü ikon açılıyor, ortasında "Agent buradan çalışacak." yazıyor;
  içeriği bilinçli olarak sonraki sürüme bırakılmış.
- **Model listesi açılınca ne göreceği** yazılmamış — yalnız kapalı hâli ve seçili değer çizilmiş.
- **Projeler arası tek işçi kısıtı** hiç geçmiyor: iki projenin kuyruğu aynı anda akabilir mi,
  tasarım söylemiyor.
- **Modal pencerelerin klavye ve dış tıklama davranışı** çizilmemiş (Esc, Enter, karartılmış zemine
  tıklama). Yalnız seçim modunun ve detay sayfasının Esc ile kapandığı yazılı.
- **Formun kalıcılığı:** prompt/negatif/varyant projeyle saklanıyor ama kaydın gönderime bağlanıp
  bağlanmadığı ve proje yeniden açıldığında kutuların dolu mu geleceği söylenmemiş.
- **"Tümünü seç"in ikinci basışı** tanımlı değil.
- **Durum tazeleme sıklığı** için bir karar yok.
- **Sıralama ya da silme yazılamazsa** ne olacağı çizilmemiş.
