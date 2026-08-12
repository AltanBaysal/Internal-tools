# Queen Editor v5 · Görev 12 — Kurulum akışı · Tasarım

**Tarih:** 2026-08-12 · **Dal:** `feat/queen-editor-v3` ·
**Yol haritası:** [roadmap v5](../plans/2026-08-12-queen-editor-v5-roadmap.md) — Blok 4, Görev 12 ·
**Kaynak maddeler:** [tasarım v3 farkları](../research/2026-08-11-queen-editor-tasarim-v3-farklari.md)
49, 50, 51, 52 · **Tür:** arka uç + ön yüz.

## Neden

Görev 11 soruyu sordu — hangi üretici kurulu — ama cevabı değiştirmenin bir yolu yok. "Kur" butonu
pasif duruyor. Bu görev onu açıyor: bir üreticinin model grubu **uygulamanın içinden** iniyor,
inerken ne kadar kaldığı görünüyor, vazgeçilebiliyor ve bitince ilgili panel kendiliğinden
kullanılabilir hâle geliyor.

## Ne olacak

| Yer | Davranış | Madde |
|---|---|---|
| Üreticiler panelindeki **Kur** | önce onay penceresi ("… kurulsun mu? · Kurulum uzun sürebilir. Üretimi engellemez, arkada sürer."), sonra kurulum | 50 |
| Üretim panelindeki kurulum kartı | üretici kurulu değilken başlığın altında mor çerçeveli kart: "… üreticisi kurulu değil." + tam genişlikte küçük mor **Kur**; kart dururken "Kuyruğa ekle" pasif | 49 |
| Panel içindeki **Kur** | onay **sormaz**, doğrudan başlatır | 50 |
| Kurulum sürerken | mor ilerleme çubuğu + canlı nokta + "kuruluyor… bitince bu kart kaybolur"; Üreticiler satırında ghost kırmızı **İptal** | 49, 51 |
| İptal | onay penceresi ("Kurulum iptal edilsin mi? · İnen kısım atılır, sonra baştan kurmak gerekir. Kuyruktaki video işleri atılmaz — kurulum yapılana kadar beklemede kalır."), sonra "kurulu değil"e döner | 51 |
| Buton metni | her yerde yalın **"Kur"** | 52 |
| Şeritteki Üreticiler ikonu | kurulum sürerken köşesinde yanıp sönen mor nokta | 7 |

## Kararlar

### 1. Kurulum, model grubunu ComfyUI'nin yanına indirmektir

Kullanıcı kararı: bir üretici, bir ComfyUI grafiği ve o grafiğin model grubudur; kurmak o dosyaları
çalışma zamanındaki ComfyUI klasörüne indirmektir. Üç şey buradan çıkar:

- **Grup veridir, kod değil.** Her üretici, ihtiyaç duyduğu dosyaları `{klasör, ad, adres}`
  üçlüleriyle sayar. Video için WAN 2.2 I2V, ses için MMAudio — bilgi `collab-toolbox`'tan miras
  alınır, o klasöre çalışma zamanı bağımlılığı kurulmaz.
- **"Kurulu mu" dosyaya bakar.** Görev 11'de foto için "motor bir model listeliyor mu" diye
  soruluyordu; artık ölçüt **grubun her dosyasının yerinde olması**. Ölçüt tek yerde tanımlanır ve
  üç üretici için de aynıdır.
- **Hedef klasör yapılandırmadır.** ComfyUI'nin kökü `QE_COMFY_ROOT` ile gelir; defterin CONFIG
  hücresi onu verir. Kod hiçbir yolu sabitlemez.

### 2. Kimlik doğrulaması isteyen dosya bu sürümde uygulamanın işi değil

Video grubunun bir parçası Civitai'den geliyor ve **token istiyor**; defter bunu bugün kullanıcıdan
alıyor. Uygulamaya bir token kutusu eklemek tasarımda karşılığı olmayan yeni bir ekran olurdu.

**Karar:** uygulama **açık adresten inebilen** dosyaları indirir. Token isteyen dosya grubun içinde
`notebook` işaretiyle durur; kurulum ona gelince, o dosyayı defterin kurduğunu söyleyen bir hatayla
durur ve kart sebebi yazar. Böylece hiçbir şey sessizce yarım kalmaz ve uygulama, yapamayacağı işi
yapıyormuş gibi görünmez.

### 3. Kurulum tek ve arka plandadır — üretimi durdurmaz

Makine tek: aynı anda **tek kurulum** koşar, ikinci istek reddedilir. Ama kurulum üretimi
engellemez; ikisi ayrı işler ve tasarımın onay metni de bunu söylüyor ("Üretimi engellemez, arkada
sürer").

Kurulumun durumu bellekte yaşar, diskte değil: ölen bir süreç "kuruluyor" bırakmamalı — koşan
üretimin `running` durumunda olduğu gibi. Yarım inen dosya da kalmaz; iptal ve çöküş aynı temizliği
yapar.

### 4. İlerleme bayt sayar, dosya değil

Kart bir çubuk çiziyor; çubuğun dürüst olması için ölçü **inen bayt / toplam bayt** olmalı. Dosya
sayısına bakan bir çubuk, 4 GB'lık dosyanın yanında 20 MB'lıkla aynı adımı atardı.

Toplam boyut indirmeden önce bilinmiyor olabilir (sunucu `Content-Length` vermeyebilir). O zaman
çubuk belirsiz hâline geçer — uydurulmuş bir yüzde yazılmaz.

### 5. İki Kur iki farklı sorunun cevabı

Madde 50'nin çelişkisi zaten çözülmüş: iki ayrı buton var. Sebebi de anlamlı — Üreticiler
panelindeki Kur, kullanıcının **kendi başlattığı** bir bakım işi ve uzun sürebileceği söylenmeli;
üretim panelindeki Kur ise kullanıcının zaten istediği şeyin (video üretmek) önündeki tek engel, ve
oraya bir onay koymak "istediğin şeyi istiyor musun" diye sormak olurdu.

### 6. Kurulum bitince panel kendiliğinden açılır

Kart "bitince bu kart kaybolur" diyor; yani ekran kurulumun bittiğini kendisi görmeli. Üretici
durumu, kurulum sürerken **yoklanır** (üretim durumunun yoklandığı gibi) ve bitince kart kaybolur,
"Kuyruğa ekle" serbest kalır. Kullanıcının sayfayı yenilemesi gerekmez.

## Nasıl görülür

1. Video paneli açılınca (Blok 5) üstünde "Video üreticisi kurulu değil." kartı ve "Kuyruğa ekle"
   pasif. Bugün aynı kart **foto panelinde**, foto üreticisi kurulu değilse görünür.
2. Panel içindeki Kur'a basınca soru sorulmaz, kart ilerleme çubuğuna döner.
3. Üreticiler panelindeki Kur'a basınca önce onay penceresi çıkar.
4. Kurulum sürerken Üreticiler satırında İptal var; basınca onay sorar, kabul edilirse inen kısım
   atılır ve satır "kurulu değil"e döner.
5. Kurulum bitince kart kaybolur, satır "✓ kurulu" olur, "Kuyruğa ekle" açılır.
6. Şeritteki Üreticiler ikonu kurulum sürerken yanıp sönen mor nokta taşır.

## Testler

**Arka uç:**

| Konu | Test |
|---|---|
| Grup | üreticinin grubu eksiksiz diskteyse kurulu, bir dosya eksikse değil |
| Kurulum | kurulum grubun eksik dosyalarını indirir, var olanı yeniden indirmez |
| İlerleme | durum inen/toplam baytı ve hangi dosyanın indiğini söyler |
| Tek koşu | kurulum sürerken ikinci istek reddedilir |
| İptal | iptal yarım dosyayı siler ve durum "kurulu değil"e döner |
| Token | token isteyen dosyaya gelince kurulum durur ve sebebi söyler |
| Üretim | kurulum sürerken üretim başlatılabilir (biri ötekini kilitlemez) |

**Ön yüz:**

| Konu | Test |
|---|---|
| Kart | üretici kurulu değilken panelin üstünde kart var ve "Kuyruğa ekle" pasif |
| Onay farkı | Üreticiler'deki Kur onay açar; paneldeki Kur açmaz |
| İlerleme | kurulum sürerken kart çubuk ve "kuruluyor…" gösterir |
| İptal | İptal onay açar; kabul edilince istek gider |
| Bitiş | kurulum bitince kart kaybolur ve buton serbest kalır |
| Nokta | kurulum sürerken şerit ikonunda canlı nokta var |

## Kapsam dışı

- **Kuyruğun üretici eksikken beklemesi** (53) — **Görev 13**.
- **Video ve ses panellerinin kendisi** — Görev 14 ve 20; bu görevin kurulum kartı foto panelinde
  kurulur ve oradan miras alınır.
- **Üretici kaldırma ve boyut gösterimi** — tasarımın kendi kapsam dışısı.
- **Custom node kurulumu** — grafiklerin ihtiyaç duyduğu ComfyUI eklentileri defterin işi olarak
  kalır; bu görev **model dosyalarını** indirir. Eklentiyi uygulamanın içinden kurmak, koşan
  ComfyUI'yi yeniden başlatmayı gerektirir ve tasarımda karşılığı yok.

## Riskler

- **Token'lı dosya** (karar 2) video kurulumunu uygulamanın içinden tamamlanamaz kılıyor. Kullanıcı
  bunu kartta okuyor; sessiz bir yarım kurulum yok. Gerçek çözüm (token kutusu) tasarımın bir
  sonraki sürümüne ait.
- **İndirme boyutları büyük** ve testler sahte indiriciyle koşuyor; gerçek davranış Colab turunda
  görülecek.
- **Custom node'ların dışarıda kalması** (kapsam dışı) video üretiminin Blok 5'te çalışması için
  defterin doğru eklentileri kurmuş olmasını şart koşar. Blok 5'in spec'i bunu yazacak.
