# Queen Editor v5 · Görev 11 — Şerit yeni düzeni + Üreticiler paneli · Tasarım

**Tarih:** 2026-08-12 · **Dal:** `feat/queen-editor-v3` ·
**Yol haritası:** [roadmap v5](../plans/2026-08-12-queen-editor-v5-roadmap.md) — Blok 4, Görev 11 ·
**Kaynak maddeler:** [tasarım v3 farkları](../research/2026-08-11-queen-editor-tasarim-v3-farklari.md)
8, 48 · madde 7'nin ilk adımı · **Tür:** arka uç + ön yüz.

## Blok 4'ün zemini — kullanıcı kararı (2026-08-12)

Yol haritası "üreticilerin altyapısı ve kurulum biçimi"ni Görev 12'ye bırakmıştı. Karar alındı ve
bütün blok buna oturur:

- **Kurulum = model grubu indirmek.** Bir üretici, bir ComfyUI grafiği ve o grafiğin ihtiyaç duyduğu
  model dosyalarıdır. "Kur", o dosyaları çalışma zamanındaki ComfyUI klasörüne indirir; "kurulu mu"
  sorusunun cevabı dosyaların yerinde olup olmadığıdır. Foto üreticisi bugün zaten böyle kurulu —
  defterin setup hücreleri onun model grubunu indiriyor.
- **Motorlar:** video **WAN 2.2 I2V**, ses **MMAudio** — ikisi de `collab-toolbox`'ta çalışır hâlde.
  Miras alınan şey **bilgi**: grafik ve model adları kendi dosyalarımıza kopyalanır, o klasöre
  çalışma zamanı bağımlılığı kurulmaz (CODE-STANDARD'ın bağımsızlık kuralı).

Bu görev kararın yalnız **görünen** yarısını yapar: hangi üreticinin kurulu olduğunu söyler.
İndirmenin kendisi Görev 12'dir.

## Neden

Şeritte üç ikon var ve hepsi tek projenin foto işine bakıyor. Video ve ses üreticileri geldiğinde
kullanıcının cevaplaması gereken yeni bir soru doğuyor: **hangi motor bu makinede kurulu?** Bugün bu
sorunun sorulacağı bir yer yok — panel de yok, cevap da yok.

Bu görev o yeri açıyor: şeridin en altına **Üreticiler** paneli gelir ve üç üreticiyi durumlarıyla
sayar. Aynı geçişte şerit tasarımın kendi geometrisine oturur, çünkü altıncı ikon eklenirken hücre
düzeni de değişiyor.

## Ne olacak

**Şerit** (madde 8): kendi kart zemini olur; hücreler şeridin tam genişliğini kaplar (48×46); seçili
hücrenin sağ kenarı boydan boya 2 piksel vurgu rengi olur, seçili olmayanlar aynı kalınlıkta saydam
çizgi taşır — böylece ikonlar seçimle kaymaz. En alta, boşlukla ayrılmış **Üreticiler** ikonu gelir.

**Üreticiler paneli** (madde 48): başlığın altında *"Her üretici kendi model grubunu kurar.
Kullanmadığın kurulmaz."* ve üç çerçeveli satır — **Fotoğraf üreticisi · Video üreticisi · Ses
üreticisi**. Kurulu olan satır yeşil **"✓ kurulu"**, olmayan tam genişlikte mor **"Kur"** taşır. Bu
sürümde kaldırma yok, boyut yazılmıyor.

## Kararlar

### 1. "Kurulu mu" sorusunu üreticinin kendisi cevaplar

Kurulum model dosyası indirmek olduğuna göre kurulu olmak da o dosyaların yerinde olması demek — ve
bunu bilen tek yer, o grafiği koşturan üreticinin kendisi. Bu yüzden üretici port'una tek bir soru
eklenir: **kurulu musun.**

Foto üreticisi bu soruyu bugün de cevaplayabiliyor: motor kendisine hangi model dosyalarının
listelendiğini söylüyor, ve liste boş değilse grubu inmiş demektir. Video ve ses için henüz bir
üretici nesnesi yok — **nesnesi olmayan üretici kurulu değildir**, ki motorun bugünkü kuralının
aynısıdır ("bu iş türü için üretici yok").

Ayrı bir "kuruldu" işaret dosyası **açılmaz**: gerçek diskte durur (ilke 2), ve dosyaların yanına
"bu dosyalar var" diye ikinci bir kayıt koymak, bir dosyanın başka dosyanın cevabını bayrak olarak
tekrarlaması olurdu.

### 2. Üreticiler kendi feature'ıdır, foto'nun içi değil

Panel üç üreticiden söz ediyor; ikisi foto üretimiyle hiç ilgili değil. Arka uçta bu yüzden kendi
feature'ı olur (`backend/features/producers/`) ve **hiçbir feature'ı import etmez**: elindeki tek
şey "kurulu musun" diye sorulabilen bir port'tur; hangi somut sınıfın geldiğine composition root
karar verir. CODE-STANDARD'ın `feature ↛ feature` yasağı böylece kırılmadan kalır.

Ön yüzde de panel kendi klasörüne girer (`features/producers/`). Şerit onu **bileşen olarak**
import eder. Şerit bugün foto ekranının içinde duruyor ama aslında uygulamanın kendi çerçevesi —
Blok 5-6'da video ve ses panelleri de ona bağlanınca dört feature'a birden hizmet edecek, ve
**taşınma anı orasıdır**. Bugün taşımak, sebebi henüz doğmamış bir düzenleme olurdu.

### 3. Cevap alınamazsa panel sustuğunu söyler

Üreticiye "kurulu musun" diye sorulur ve motor cevap vermeyebilir (tünel kopuk, ComfyUI ayakta
değil). O zaman "kurulu değil" demek **yalan** olur ve kullanıcıyı gereksiz bir indirmeye çağırır.

Bunun yerine soru cevapsız kalınca panel, model listesinin okunamamasında kullandığı kalıbın aynısını
gösterir: kırmızı çerçeveli hata kartı + sunucunun kendi cümlesi. Satırlar hiç çizilmez — üç satırın
ikisi doğru biri yanlış olacağına, hiçbiri yazılmaz.

### 4. Bu görevde "Kur" pasiftir

Butonun kendisi tasarımın satırının parçası, ama basınca ne olacağı (onay penceresi, indirme,
ilerleme, iptal) **Görev 12'nin** işi. Bu görevde buton çizilir ve **pasif** durur; Görev 12 onu
açar. Basılabilir ama hiçbir şey yapmayan bir buton çizmek, kullanıcıya yalan söylemek olurdu.

## Nasıl görülür

1. Şeridin kendi kart zemini var; seçili ikonun sağ kenarı boydan boya mor, seçili olmayanlarda
   ikonlar aynı yerde duruyor (kayma yok).
2. Şeridin en altında, ötekilerden boşlukla ayrılmış Üreticiler ikonu var.
3. Panel açılınca üç satır: Fotoğraf üreticisi "✓ kurulu", Video ve Ses üreticisi pasif "Kur".
4. ComfyUI ayakta değilken panel satır çizmez; kırmızı hata kartı + sunucunun cümlesi gösterir.

## Testler

**Arka uç:**

| Konu | Test |
|---|---|
| Liste | üç üretici üretim sırasında ve kendi adlarıyla listelenir |
| Kurulu | üreticisi olan ve "kuruluyum" diyen satır `installed: true` döner |
| Kurulu değil | üreticisi olmayan tür `installed: false` döner |
| Cevapsız | üretici soruya patlarsa uç 502 ve sunucunun cümlesi döner |
| Foto | foto üreticisi motorun listesi doluyken kurulu, boşken değil |

**Ön yüz:**

| Konu | Test |
|---|---|
| Satırlar | üç satır adlarıyla çizilir, kurulu olan "✓ kurulu" der |
| Kur | kurulu olmayan satırda pasif "Kur" butonu var |
| Hata | durum okunamayınca satır yok, hata kartı var |
| Şerit | Üreticiler ikonu şeritte en sonda ve kendi paneli açılıyor |

## Kapsam dışı

- **Kurulumun kendisi** (49-52) — **Görev 12**: iki Kur butonunun farkı, onay penceresi, ilerleme,
  iptal, üretim panelindeki kurulum kartı.
- **Kuyruğun üretici eksikken beklemesi** (53) — **Görev 13**.
- **Üreticiler ikonunun kurulum sürerken yanıp sönen mor noktası** (madde 7'nin son cümlesi) —
  kurulum kavramıyla birlikte **Görev 12**.
- **Video ve ses panelleri** (madde 7'nin kalanı) — Görev 14 ve 20.

## Riskler

- **"Kurulu" ölçütü foto için model listesinin dolu olması.** Kullanıcının seçtiği modeli değil,
  *herhangi bir* modeli arar; grubun eksik inmesi hâlinde "kurulu" der. Kesin ölçüt (hangi
  dosyaların aranacağı) Görev 12'de, indirilecek grup tanımlanırken netleşir ve bu satır oraya
  bağlanır.
- **Şeridin geometrisi** tasarımın piksel değerleriyle veriliyor ama ekranda doğrulanması Colab
  turuna kalıyor; testler yalnız ikonun varlığını ve panelin açılmasını kanıtlar.
