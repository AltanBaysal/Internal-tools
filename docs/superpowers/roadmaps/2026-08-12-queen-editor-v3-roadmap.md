# Queen Editor — Yol Haritası v3 (KAPANDI)

**Koşu dalı:** `feat/queen-editor-v3` · **Tarih:** 2026-08-12 – 2026-08-14 · **Durum:** kapandı
**Öncesi:** [v2](2026-08-08-queen-editor-v2-roadmap.md) · **Sonrası:**
[v4](2026-08-20-queen-editor-v4-roadmap.md)

> **Sekiz koşu, tek belge.** Bu sürüm sekiz koşu taşıdı ve her koşu kendi yol haritasını açmıştı —
> o zamanki adlarıyla *"v5"*'ten *"v13"*'e *(v10 hiç yazılmadı)*. 11 Eylül 2026'da birleştirildiler:
> bir sürüm bir daldır ve o dalın tek yol haritası olur, yani o sekiz belge ayrı sürüm değildi.
> Metinleri olduğu gibi aşağıda; değişen tek şey başlık seviyeleri ve birbirlerine giden
> bağlantıların bölüm adına dönmesi.
>
> **Madde numaraları kaymadı, ve bölümüne aittir.** Her koşu görevlerini 1'den saymıştı, yani aynı
> numara bu dosyada sekiz kez geçiyor. Bir maddeye *"v3 · koşu 3 · görev 7"* diye gidilir; yazılmış
> spec'ler de belgenin o günkü adıyla atıf yapıyor, ve o ad her bölümün başlığında duruyor.

---

# Koşu 1 — 12 Ağustos *(o zamanki adıyla "yol haritası v5")*

**Tarih:** 2026-08-12 · **Koşu dalı:** `feat/queen-editor-v3` ·
**Durum:** 33 görevin 33'ü yazıldı ve commit edildi (`a878d59`'a kadar); **kullanıcının elle Colab
turu bekliyor** — aşağıdaki *Koşunun sonu* bölümü.
**Yerini aldığı koşu:** [v2 yol haritası](2026-08-08-queen-editor-v2-roadmap.md)
— Madde 1-11 bitti ve push edildi; Madde 12 (Colab turu) yalnız yüzeysel koşuldu, o borç bu koşuya
devrolmaz — bu koşunun kendi doğrulaması kendi işini kapsar.
**Kaynak:** [tasarım v3 farkları](../research/2026-08-11-queen-editor-tasarim-v3-farklari.md) —
108 madde + içine işlenmiş 14 kullanıcı kararı. Görevlerin altındaki **Maddeler** satırı oradaki
numaralardır; bulgunun içeriği orada, kararların gerekçesi de orada.

> **İsim çakışması.** Tasarım projesindeki **"Basit v3"**, repodaki bu **v5 yol haritasına**
> karşılık gelir. Belge boyunca ikisi tam adıyla anılır: **tasarım v3** ve **roadmap v5**.

**Kapsam sınırı:**

- **queen-tools zinciri emekli olur** *(kullanıcı kararı, 2026-08-12)*: uygulama video, ses ve
  export'u kendi yaptığında `collab-toolbox/queen-tools/` zincirinin girdisi kalmıyor. Bu koşuda
  zincire görev yok; defterler repoda durur, bakım almaz.
- **Tasarımın kendi kapsam dışıları dışarıda kalır:** yeniden adlandırma · AI agent panelinin içi
  ("sonraki sürümde tasarlanacak") · video süresi seçimi (süre bu sürümde sabit) · üretici kaldırma
  ve boyut gösterimi.
- **13 öksüz davranış iş üretmez** — "hepsi kalıyor" kararı gereği (sondaki *Korunanlar* bölümü).
- **Üç madde kararla işsiz kapandı:** 4 ve 5 (bugünkü davranış doğru sayıldı), 66 (istenmeyen şey
  bugün de yok). Kapsama tablosunda ayrıca görünürler.

İlke v4'tekiyle aynı: her görev çıktı odaklı (**ne çalışır** + **nasıl görülür**) ve bir öncekinin
üstüne birikir; hiçbir görev, zemini sonradan değişecek bir şeyin üstüne kurulmaz.

---

## Nasıl çalışacağız

Her görev aynı dört adımdan geçer, görev bitmeden sonrakine geçilmez:

1. **Spec** — görevin tasarım dokümanı (`docs/superpowers/specs/`). Fark belgesindeki maddeler
   burada davranışa açılır; görevin açık soruları burada karara bağlanır. Bittiğinde görevin
   altına **Spec** satırı eklenir.
2. **Plan** — uygulama planı (`docs/superpowers/plans/`), TDD adımlarıyla.
3. **Full TDD** — **hiçbir üretim kodu satırı, önce kırmızı bir test yokken yazılmaz.** Plan
   adımları böyle kesilir: önce başarısız test, sonra onu geçiren en küçük kod. Arka uç `pytest`
   (sahte port'larla; ComfyUI yok, Drive yok, dil modeli yok), ön yüz `npm test` (vitest + jsdom;
   ağ ve saat sahte, gerçek saniye beklenmez).
4. **Kapanış** — `pytest` ve `npm test` yeşil; ön yüze dokunulduysa `npm run build` koşulur ve
   üretilen `dist/` **aynı commit'te** gider. Görev biter bitmez commit + push edilir — Colab
   repoyu klonladığı için push edilmemiş iş orada görünmez.

Bir görevin **"Nasıl görülür"** satırı o görevin kabul kriteridir; testler o satırı kanıtlar.
Colab doğrulama turları bu belgede planlanmadı — ne zaman ve nasıl koşulacağı koşu sırasında
kararlaştırılır.

## Kod kuralları — FOUNDATION ve CODE-STANDARD bağlayıcıdır

Her görevin spec'i, planı ve kodu iki belgeye tabidir; çelişkide onlar kazanır:
ilkeler ve yığın kararları **[FOUNDATION.md](../../../queen-editor/FOUNDATION.md)**, katmanlar ve
yapı **[CODE-STANDARD.md](../../../queen-editor/CODE-STANDARD.md)**. Kurallar burada tekrar
yazılmaz; bu koşuda en çok işe karışacak olanlar:

- **Kullanıcının emeği kutsaldır** (ilke 1 — çakışmada hepsini yener). Tasarım v3'ün "üret = ekle,
  sil = kaldır" kuralı bu ilkenin ekrana inmiş hâlidir: hiçbir üretim var olan katmanı ezmez,
  yıkıcı her eylem açık ve onaylıdır, yarım iş yeniden başlatmadan sonra kaldığı yerden sürer.
- **Gerçek diskte durur** (ilke 2). Katmanlar, kuyruk, kurulum durumu — önemli olan her şey dosyada
  yaşar, uygulama açılışta kendini dosyalardan kurar. Yeni kayıt gerektiğinde CODE-STANDARD'ın
  **"bir dosya bir soru"** kuralı işler: bir dosya başka dosyanın cevabını bayrak olarak
  tekrarlamaz.
- **Kural arka uçta, ön yüz görüntüdür.** Kapsam hesabı, kopya karenin doğumu, adlandırma, tür
  sırası, export uygunluğu — hepsi arka uçta karar bulur; tarayıcı durumu çizer ve girdi toplar.
- **Bağımlılık yönü:** `presentation → domain ← data → services`; yasaklar istisnasız
  (`feature ↛ feature`, `service ↛ feature`, `service ↛ service`), somut bağlama yalnız
  composition root'ta. Video, ses, üreticiler ve export kendi feature'ları olarak açılır.
- **Yeniden üretilebilirlik** (ilke 4): her birim spec'inden tek başına yeniden yazılabilecek kadar
  küçük kalır; bağlamda rahat tutulamayan dosya bölünür.
- **`vendor/` elle düzenlenmez** — tasarım v3'ün dosyaları birebir gelir; uygulamaya uymayan şey
  `shared/` tarafında düzeltilir.
- **Dil ayrımı:** yorum, docstring, test adı, commit mesajı İngilizce; kullanıcının gördüğü her
  metin Türkçe.

## Bu belge detay tutmaz

Her görevin altında **kapsadığı madde numaraları** yazılı. Maddenin ne dediği fark belgesindedir;
nasıl yapılacağı görevin kendi spec'i ve planındadır. Yol haritası yalnız **hangi işin hangi
sırayla ve neyle birlikte yapılacağını** söyler.

`düzeltilecek` maddeler ayrı görev değildir — her biri, o ekranı zaten elden geçiren görevin kabul
kriterine katılır; böylece hiçbir ekran iki turda elden geçmez. **Zayıf sinyal kuralı:** 1/3
damgalı maddeler de görevlerine girer; spec yazılırken fark gerçek çıkmazsa madde "iş çıkmadı"
diye kapanır ve bu, görevin spec'ine not düşülür.

## Çekirdek: kare bir katman yığınıdır

Tasarım v3 tek karardan doğuyor: **kare artık yalnız fotoğraf değil** — foto + en çok bir video +
en çok bir ses; ses videoya bindirilidir. Üç sonucu her bloğa sızar:

1. **Hiçbir üretim var olanı ezmez** — "üret = ekle, sil = kaldır"; varyant istemek kareyi
   kopyalamaktır.
2. **Kuyruk kare değil iş tutar** — her işin türü vardır, motor türleri sırayla bitirir: önce
   fotolar, sonra videolar, sonra sesler.
3. **Dosya adı katmanları taşır** — ad; prompt'u, varyantı ve katman turlarını söyler.

Bu üçü zemin bloğunun işidir; geri kalan her şey üstüne oturur.

---

## Blok 1 · Zemin: kare ve iş

Ekranda az şey değişir; her şey buna basar.

### Görev 1 — Kare katman yığını olur

- **Ne çalışır:** kare kaydı foto + en çok bir video + en çok bir ses taşır; ses videoya bağlıdır.
  "Üret = ekle, sil = kaldır" kayıt düzeyinde kuraldır: hiçbir üretim var olan katmanın üstüne
  yazamaz. Kareyi silmek bütün katman dosyalarını birlikte götürür; videoyu silmek üstündeki sesi
  de götürür, kareyi bırakır.
- **Nasıl görülür:** `pytest` yeşil ve iki cümle kanıtlı — videolu kareye ikinci video eklenemiyor;
  silinen karenin hiçbir katman dosyası geride kalmıyor.
- **Yok:** ekran dokunuşu; video/ses üretiminin kendisi (Blok 5-6); katman silmenin arayüzü
  (Görev 26).
- **Maddeler:** 103, 101

### Görev 2 — Dosya adları katman şemasına geçer

- **Ne çalışır:** yeni üretilen her dosya yeni ad düzenini kullanır — ad; karenin prompt numarasını,
  varyantını ve katman turlarını taşır (fark belgesi 97'deki örnekler birebir). Var olan projelerin
  eski adlı dosyalarının akıbeti spec'te karara bağlanır.
- **Nasıl görülür:** yeni kare üretildiğinde dosyası yeni adla iner; ad, fark belgesindeki örnek
  kalıbıyla birebir.
- **Yok:** tur ve varyant artırma kuralları (kopya ve yeniden üretimle gelirler — Görev 15, 25).
- **Maddeler:** 97

### Görev 3 — Kuyruk kare değil iş tutar

- **Ne çalışır:** kuyruktaki her kaydın türü olur — foto, video, ses; motor işleri tür sırasıyla
  bitirir: önce bütün fotolar, sonra videolar, sonra sesler. Bugün tek tür olduğundan davranış
  dışarıdan değişmez; düzen değişir.
- **Nasıl görülür:** testler — karışık türde işler atıldığında bitirilme sırası tür sırasıdır;
  foto işleri bitmeden videoya geçilmez.
- **Yok:** kuyruk panelinin görünümü (Görev 9-10); video ve ses işinin gerçekten üretilmesi.
- **Maddeler:** 33, 36

### Görev 4 — Motor kuralları: duraklatma ve deneme

- **Ne çalışır:** Duraklat çalışan işi keser ve yarım işi kuyruğa iade eder — sayı 7'den 8'e çıkar
  *(karar 44)*; bekleyen sayısı çalışan işi hiç saymaz. Bir kare, **aynı iş üç deneme** başarısız
  olunca kırmızıya döner *(karar 45)* — üç deneme kuralı yalnız cevapsız kalınan durumla sınırlı
  olmaktan çıkar.
- **Nasıl görülür:** üretim sürerken sayı çalışanı dışlıyor; duraklatınca bir artıyor; tek
  başarısız cevap kareyi kırmızıya döndürmüyor, üçüncüsü döndürüyor.
- **Yok:** kuyruk panelinin yeni kartları (Görev 9-10).
- **Maddeler:** 44, 45

## Blok 2 · Foto tarafı zemine taşınır

Bugünkü ekranlar yeni zeminin diliyle konuşur hâle gelir.

### Görev 5 — Panel yeni adını alır

- **Ne çalışır:** panel başlığı **"Fotoğraf üret"**, ana buton **"Kuyruğa ekle"**; boş galeri
  cümlesi yeni buton adını söyler; panelin şerit ikonu tasarımdaki fotoğraf ikonuna döner.
- **Nasıl görülür:** üç metin ve ikon tasarım v3 ile birebir.
- **Maddeler:** 13, 14, 61, 9

### Görev 6 — Panel geri bildirimleri ayrışır

- **Ne çalışır:** format hatası kendi iki metniyle anlatılır ve "Kuyruğa eklenemedi" ile bir daha
  karışmaz; "Kuyruğa eklenemedi — tekrar dene" satırı ne yapılacağını söyler ve butonun altında
  ortalanır; yeşil onay kartı iki parçalı biçimine geçer ve **10 saniye** kalır *(karar 17)*;
  model listesi okunamayınca hata, kuyruk panelindeki hata kalıbına girer.
- **Nasıl görülür:** bozuk listeyle butona basınca çıkan iki satır da format hatasını anlatıyor,
  "Kuyruğa eklenemedi" çıkmıyor; başarılı eklemede kart 10 saniye duruyor.
- **Maddeler:** 15, 16, 17, 18

### Görev 7 — Galeri kartının durum dili

- **Ne çalışır:** kart ortasındaki "bekliyor" ve "Çalışıyor" yazıları kalkar; sol üstte tek
  kalıpta **katman + durum hapı** doğar; rozet düzeni üç düzleme ayrılır — sol üst durum, sağ alt
  sahiplik, seçim halkası. Bu görevde yalnız foto hapları vardır; video/ses hapları kendi
  bloklarında aynı kalıba eklenir.
- **Nasıl görülür:** dört hâl (bekleyen · çalışan · üretilmiş · hatalı) tasarımın kart diliyle
  çiziliyor, ortada yazı kalmıyor.
- **Yok:** video/ses sahiplik rozetleri (Görev 18, 22).
- **Maddeler:** 54, 55, 56, 57

### Görev 8 — Galeri sırası ve sürükleme

- **Ne çalışır:** galeri sırası üretim sırasıdır — kareyi sürüklemek kuyruğun sırasını da
  değiştirir; bekleyen ve çalışan kareler de sürüklenir.
- **Nasıl görülür:** bekleyen kareyi öne çek → önce o üretilir.
- **Maddeler:** 59, 60

## Blok 3 · Kuyruk paneli türlü yapıya geçer

Tek türle (foto) kurulur; video gelince ikinci kart kendiliğinden doğar.

### Görev 9 — Tür kartları ve panel düzeni

- **Ne çalışır:** kuyruk paneli tür başına kart çizer (bugün foto olduğundan tek kart görünür);
  sözcük "kare"den **"iş"e** döner; kart sırası üretim sırasıdır; panel başlığı **"Kuyruk"**;
  "Kuyruğu boşalt" panelin en dibine iner; büyük sayı vurgu rengine döner.
- **Nasıl görülür:** foto işleri akarken panel yeni dilde; kart düzeni ikinci türü hazır bekliyor.
- **Maddeler:** 34, 35, 36, 40, 41, 46

### Görev 10 — Bitiş, hata ve bilgi kartları

- **Ne çalışır:** bitiş tek satırdan iki ayrı karta çıkar — tamamlanma yeşil, durma kırmızı;
  hata satırındaki "galeride göster" yerine **"Hepsini tekrar dene"** gelir; durum kartı hâline
  göre renk alır; boş kuyruk kartı yeni panel adlarını söyler; açılışta kuyruğun kendiliğinden
  sürdüğünü söyleyen satır belirir.
- **Nasıl görülür:** hatalı biten koşuda iki kart ayrı ayrı; "Hepsini tekrar dene" hatalıları
  kuyruğun sonuna alıyor.
- **Maddeler:** 37, 38, 39, 42, 43

## Blok 4 · Üreticiler ve kurulum

Video üretebilmenin ön şartı: video üreticisi kurulabilmeli.

### Görev 11 — Şerit yeni düzeni + Üreticiler paneli

- **Ne çalışır:** şerit kart zeminine ve yeni seçili işaretine geçer; en alta **Üreticiler** ikonu
  ve paneli gelir — üç üretici satırı, kurulu olan "✓ kurulu", olmayan "Kur"
  *(karar 48: wireframe kaynak)*.
- **Nasıl görülür:** şerit tasarımın geometrisiyle; Üreticiler panelinde üç satır doğru durumu
  gösteriyor.
- **Yok:** kurulumun kendisi (Görev 12); video ve ses ikonları (panelleriyle gelir — Görev 14, 20).
- **Maddeler:** 8, 48 · madde 7'nin ilk adımı

### Görev 12 — Kurulum akışı

- **Ne çalışır:** üretici kurulu değilken ilgili üretim panelinin üstünde kurulum kartı durur ve
  kart varken "Kuyruğa ekle" pasiftir; **iki Kur farklıdır** *(karar 50)* — Üreticiler'deki onay
  sorar, panel içindeki sormaz; kurulum arkada sürer, ilerlemesi görünür, iptali ve bitiş onayı
  vardır; buton metni yalın **"Kur"**.
- **Nasıl görülür:** kurulumsuz üreticiyle panel açılınca kart + pasif buton; kur → ilerleme →
  kart kaybolur.
- **Maddeler:** 49, 50, 51, 52

### Görev 13 — Üretici eksikken kuyruk bekler

- **Ne çalışır:** sırası gelen işin üreticisi kurulu değilse iş atılmaz — kuyruk bekler ve bunu
  söyler; üretici kurulunca kaldığı yerden sürer.
- **Nasıl görülür:** üreticisiz video işi kuyruğa girer, atılmaz; kurulum bitince üretilir.
- **Maddeler:** 53

## Blok 5 · Video üretimi

### Görev 14 — Video üret paneli

- **Ne çalışır:** şeride video ikonu ve **"Video üret"** paneli gelir: kapsam radyosu (galeride
  seçim varsa "seçili kareler" işaretli açılır), varyant sayısı, sabit süre bilgisi; ekleme ara
  hâli, boş kapsam cümlesi ("Tüm karelerin videosu var — üretilecek bir şey yok") ve yeşil onay
  kartı panelin kendi hâlleridir.
- **Nasıl görülür:** panelden video işleri kuyruğa giriyor; kapsam boşken buton pasif ve cümle
  doğru.
- **Yok:** işlerin gerçekten üretilmesi (Görev 17); prompt'un yazılması (Görev 16).
- **Maddeler:** 23, 24, 28, 29 · madde 7'nin ikinci adımı

### Görev 15 — Kapsam ve kopya kare kuralları

- **Ne çalışır:** videosuz kareye video takılır, videolu kare **kopyalanır** — varyantın fazlası
  kopya kare doğurur, hiçbir kare ezilmez; seçimdeki bekleyen ve çalışan kareler atlanır; kopya
  kareler foto dosyasını paylaşır; varyant, üstündeki türev katmanları taşımaz.
- **Nasıl görülür:** videolu kareye ikinci video istenince galeriye kopya kare girer, kaynağa
  dokunulmaz; adlar fark belgesindeki varyant kalıbıyla.
- **Maddeler:** 25, 26, 100, 102

### Görev 16 — Video prompt'unu dil modeli yazar

- **Ne çalışır:** video prompt'u kullanıcıya sorulmaz — işin sırası gelince bir dil modeli foto
  prompt'undan yazar ve kareye kaydedilir; hangi dil modelinin kullanılacağı bu görevin spec'inde
  karara bağlanır.
- **Nasıl görülür:** üretilen video işinin karesinde kayıtlı bir video prompt'u var; detay
  açılınca görünecek (Görev 23).
- **Maddeler:** 27

### Görev 17 — Motor videoyu üretir

- **Ne çalışır:** sırası gelen video işi video üreticisiyle üretilir, çıkan video kareye katman
  olarak bağlanır ve dosyası katman şemasıyla yazılır; süre sabittir; foto işleri bitmeden video
  işine geçilmez (Görev 3'ün sırası). Üreticinin hangi altyapıyla koşacağı spec'te karara
  bağlanır.
- **Nasıl görülür:** videosuz kareye video iste → kare "video kuyrukta" → sırası gelince kare
  videolu olur, foto aynen durur.
- **Maddeler:** 23'ün üretim yarısı, 28

### Görev 18 — Galeride video

- **Ne çalışır:** videolu karenin sağ altında video sahiplik rozeti; kuyruktaki kopya kare
  galeride kaynağın fotoğrafıyla ve canlı "video kuyrukta" hapıyla durur.
- **Nasıl görülür:** üretim akarken kopya karenin hâli hap diliyle okunuyor; bitince rozet doğuyor.
- **Maddeler:** 58'in video yarısı

### Görev 19 — Katman hatası davranışı

- **Ne çalışır:** video (ve ileride ses) katmanı hata alınca **Tekrar dene** karta imleç gelince
  çıkar (fotosu duran kartın üstü kapanmaz); katman hatasında Tekrar dene **yeni kare açmaz** —
  eksik katmanı karenin kendisine üretir ("üret = ekle"nin tek istisnası); basınca buton kuyruğa
  girdiğini söyler.
- **Nasıl görülür:** video hatası olan karede imleçle buton; basınca iş kuyruğa girer, kopya
  doğmaz.
- **Maddeler:** 67, 68, 69

## Blok 6 · Ses üretimi

Video kalıbının üstüne ince katman: panel, kapsam, bindirme.

### Görev 20 — Ses üret paneli

- **Ne çalışır:** şeride ses ikonu ve **"Ses üret"** paneli gelir; kapsam kuralı videodan bir adım
  dar — **videosuz kare ses kapsamına hiç girmez**; boş kapsam cümlesi kendi diliyle ("Videosu
  olup sesi olmayan kare yok — üretilecek bir şey yok").
- **Nasıl görülür:** videosuz projede panel boş kapsamı söylüyor; videolu karelere ses işleri
  kuyruğa giriyor.
- **Maddeler:** 30, 31 · madde 7'nin son adımı

### Görev 21 — Ses prompt'unu dil modeli yazar

- **Ne çalışır:** ses prompt'u kullanıcıya sorulmaz — işin sırası gelince dil modeli **foto ve
  video prompt'undan** yazar ve kareye kaydedilir; video tarafında kurulan kalıbın (Görev 16)
  sese uyarlanmasıdır.
- **Nasıl görülür:** üretilen ses işinin karesinde kayıtlı bir ses prompt'u var; detay açılınca
  görünecek (Görev 23).
- **Maddeler:** 32

### Görev 22 — Motor sesi üretir ve videoya bindirir

- **Ne çalışır:** sırası gelen ses işi ses üreticisiyle üretilir ve videoya **bindirilir** —
  videolu kare artık sesli oynar; dosya katman şemasıyla yazılır; galeride ses sahiplik rozeti
  video rozetinin yanında doğar. Üreticinin altyapısı bu görevin spec'inde karara bağlanır.
- **Nasıl görülür:** sesli karenin videosu sesiyle oynuyor; sağ altta iki rozet yan yana.
- **Maddeler:** 30'un üretim yarısı, 58'in ses yarısı

## Blok 7 · Detay sayfası katmanlaşır

### Görev 23 — Sekme şeridi ve katman sütunu

- **Ne çalışır:** detaya **Foto | Video | Ses** sekme şeridi gelir — kare hangi katmanı taşıyorsa
  o sekmeler açılır; sağ sütun katman katman genişler (her katmanın kendi prompt'u ve bilgisi);
  bekleyen/çalışan karenin görsel alanı tasarımın diline geçer.
- **Nasıl görülür:** üç katmanlı karede üç sekme; katmansızda yalnız Foto.
- **Yok:** oynatma (Görev 24); düzenleme (Görev 25).
- **Maddeler:** 73, 75, 82

### Görev 24 — Oynatma

- **Ne çalışır:** video sekmesinde video, ses sekmesinde ses detayda oynar.
- **Nasıl görülür:** sekmeler arasında geçince ilgili katman oynatılabiliyor.
- **Maddeler:** 74

### Görev 25 — Prompt düzenleme ve Yeniden üret

- **Ne çalışır:** detaydaki prompt kutuları düzenlenebilir olur (kaydetme yok — düzenleme
  geçicidir); **"Yeniden üret — yeni kare"** butonu gelir *(karar 77: v2'nin "kapsam dışı" kararı
  bilinçli geri alındı)* — var olan kare ezilmez, sonuç yanına yeni kare olarak girer; buton her
  durumda vurguludur; yeniden üretim ad içinde tur numarasını artırır, yeni karenin numarası
  prompt'un değişip değişmediğine bakar.
- **Nasıl görülür:** prompt'u değiştir → Yeniden üret → kaynak durur, yeni kare kuyruğa girer,
  adlar kurala uyar.
- **Maddeler:** 76, 77, 78, 98, 99

### Görev 26 — Sekme başına tek yıkıcı eylem

- **Ne çalışır:** her sekmede tek yıkıcı buton — Video'da "Videoyu sil — kare kalır" (üstündeki
  ses de gider), Ses'te "Sesi sil — video kalır", kareyi tümden silmek yalnız Foto'da; detaydaki
  Sil butonu yıkıcı eylem standardına girer (arka plan sapması burada kapanır).
- **Nasıl görülür:** üç sekmenin butonları ve onay metinleri tasarımla birebir; katman silinince
  kare galeride durur.
- **Maddeler:** 80, 83

### Görev 27 — Hata ve kopya kare detayı

- **Ne çalışır:** hatalı katmanın detayında hatanın sebebi ve **Tekrar dene** durur; kuyruktaki
  kopya kare detayda kaynağın fotoğrafı + canlı "kuyrukta" rozeti + boş prompt kutusuyla görünür,
  "Kuyruktan çıkar" onay sormadan kaldırır.
- **Nasıl görülür:** hatalı kareyi aç → sebep okunuyor, tekrar denenebiliyor; kopya kareyi aç →
  hâli anlaşılıyor.
- **Maddeler:** 79, 81

## Blok 8 · Export ekranı

JSON export ölür; yerine kendi ekranı olan, video yazan Export gelir.

### Görev 28 — Ekran iskeleti

- **Ne çalışır:** app bar'daki Export artık dosya indirmez, **dördüncü ekranı** açar: özet kartı
  (kaç video, toplam süre), yan yana iki eşit buton — "Birleşik videoyu export et" ve "Ayrı
  ayrı export et"; ekranın kendisi onay adımıdır, ayrıca pencere çıkmaz; hiç video yoksa ekran
  yönlendirmeye döner.
- **Nasıl görülür:** videolu projede Export ekranı özetle açılıyor; videosuzda yönlendirme.
- **Yok:** export'un gerçekten koşması (Görev 30); uyarı ve pasiflik kuralları (Görev 29).
- **Maddeler:** 85, 86, 87, 88, 95

### Görev 29 — Uyarılar ve pasiflik

- **Ne çalışır:** koşul oluştukça özet kartında kırmızı satırlar doğar (sesi olmayan videolar,
  diziye girmeyecek kareler, kuyrukta bekleyen videolar); **üretim akarken export engellidir,
  kuyruk duraklatılınca serbest kalır** *(karar 90)*; butonların pasiflik kuralları işler.
- **Nasıl görülür:** kuyruk akarken butonlar pasif + sebep satırı; duraklat → serbest.
- **Maddeler:** 89, 90, 91

### Görev 30 — Export koşusu

- **Ne çalışır:** export Drive'da tarih adlı klasöre yazar; koşarken ilerleme butonun yerinde
  okunur; hata olursa koşu baştan başlatılır; export sürerken ekrandan çıkmak (onaylı) export'u
  iptal eder. Birleşik videonun nasıl birleştirileceği spec'te karara bağlanır.
- **Nasıl görülür:** export bit → Drive'da tarihli klasörde dosyalar; çıkışta onay + iptal.
- **Maddeler:** 92, 93, 94, 96

## Blok 9 · Dil ve cila

Metin ve görünüm genellemeleri — bütün ekranlar yerine oturunca tek geçişte.

### Görev 31 — "Kare" dili genele

- **Ne çalışır:** arayüz metinlerinde içerik birimi **"kare"** olur; üç silme onayı yeni
  metinlerine geçer — tekil/çoğul silme katman sayar, yalnız-bekleyen alt satırı üretilmiş
  kareleri korur, **karışık seçimde alt satır hiç yazılmaz** *(karar 64)*; seçim barındaki buton
  her senaryoda **"Sil"**.
- **Nasıl görülür:** üç seçim türünün onayları fark belgesindeki metinlerle birebir; "fotoğraf"
  sözcüğü içerik birimi olarak kalmıyor.
- **Maddeler:** 104, 62, 63, 64, 65

### Görev 32 — Proje ekranı ve silme davranışı

- **Ne çalışır:** proje silme onayı kare dilini konuşur ve üretimin akıbetini söyler; silmek
  çalışan üretimi **gerçekten durdurur** ve kuyruğu atar; kartın silme butonu çerçevesiz kırmızı
  çöp ikonu olur; projeden çıkış onayı kalkar, yerine üretim sürerken görünen bilgi balonu gelir.
- **Nasıl görülür:** üretim akarken projeyi sil → üretim durur, hata düşmez; çıkışta onay yok,
  balon var.
- **Maddeler:** 1, 2, 3, 10

### Görev 33 — Pencere ve yerleşim cilası

- **Ne çalışır:** onay pencerelerinin genişliği metnine göre değişir; uygulama açılışta yatayda
  taşmaz — varsayılan ekran cihaz ekranına tam oturur *(madde 107, elle bulgu)*; seçim barı en
  dibe yapışmaz, içeriğin üstünde yüzer *(madde 108, elle bulgu)*.
- **Nasıl görülür:** açılışta yatay kaydırma çubuğu yok; seçimde bar alt kenardan boşluklu.
- **Maddeler:** 105, 107, 108

---

## Sıra özeti

| Blok | Görevler | Görülür kazanım |
|---|---|---|
| 1 · Zemin | 1-4 | Kare katman taşır, kuyruk türlü iş tutar, motor kuralları oturur |
| 2 · Foto taşıma | 5-8 | Bugünkü ekranlar yeni adlar ve yeni durum diliyle |
| 3 · Kuyruk paneli | 9-10 | Tür kartları, iki bitiş kartı, "Hepsini tekrar dene" |
| 4 · Üreticiler | 11-13 | Kurulum uygulamanın içinde; kuyruk üreticisizken beklemeyi bilir |
| 5 · Video | 14-19 | Panelden videolu kareler; kopya kare; hata davranışı |
| 6 · Ses | 20-22 | Videolar seslenir; ikinci rozet |
| 7 · Detay | 23-27 | Sekmeli, oynatan, düzenleten, yeniden üreten detay |
| 8 · Export | 28-30 | JSON ölür; ekranlı, video yazan Export |
| 9 · Dil ve cila | 31-33 | "Kare" dili, proje silme davranışı, yerleşim düzeltmeleri |

## Neden bu sıra

- **Zemin önce (1-4):** 92 işin neredeyse hepsi "kare = katman yığını" kararına basıyor; zemin en
  son değişirse üstüne kurulan her şey iki kez yapılır. Motor kuralları (4) da zemindedir — export
  duraklatma serbestliği (Görev 29) ve kuyruk kartları (9-10) bu davranışın üstüne oturur.
- **Foto taşıma zeminden hemen sonra (5-8):** ekranlar yeni dile geçmeden kuyruk paneli ve yeni
  paneller eklenirse, eski dil ile yeni dil aynı ekranda yaşar ve her metne iki kez dokunulur.
- **Kuyruk paneli üreticilerden ve videodan önce (9-10):** tür kartı düzeni tek türle kurulur;
  video geldiğinde ikinci kart kod değil veri olarak doğar — ekleme olur, sökme olmaz.
- **Üreticiler videodan önce (11-13):** video üretebilmenin ön şartı video üreticisinin
  kurulabilmesi; kurulum akışı da en az bir üretim paneli varken (foto) kurulup denenebilir.
- **Video sesten önce (14-19):** ses videoya bindirilidir — videosuz ses kapsamı boştur (madde 31).
  Ses bloğu (20-22) video kalıbını miras alır, o yüzden incedir.
- **Detay katmanlardan sonra (23-27):** sekmeler ancak katmanlar gerçekten varken anlamlı;
  Yeniden üret (25), adlandırma kurallarını (2) ve kopya kalıbını (15) kullanır.
- **Export sona yakın (28-30):** videosuz export yönlendirme ekranından ibaret; gerçek işi ancak
  video ve ses varken görünür. Engelleme kuralı Görev 4'ün duraklatma davranışına basar.
- **Dil ve cila en sonda (31-33):** metin genellemeleri bütün ekranlar yerine oturunca tek geçişte
  yapılır; erken yapılırsa her yeni panelde aynı karar yeniden verilir.

Blok içi bağımlılıklar görev sırasının kendisidir: 15, 14'ün panelini; 17, 16'nın prompt'unu; 22,
21'in prompt'unu; 25, 23'ün sekmelerini varsayar. 19 ile 20 arasında sıra ilişkisi yoktur; bloklar
içinde bağımsız görevler istenirse öne çekilebilir — kapsama tablosu değişmez.

## Kapsama tablosu

Fark belgesindeki 108 maddenin her biri ya bir görevde ya da gerekçeli bir "iş yok" satırında.

| Alan | Maddeler | Görev |
|---|---|---|
| Projeler | 1, 2, 3, 10 | 32 |
| Projeler | ~~4~~, ~~5~~ | **iş yok** — karar: bugünkü davranış doğru |
| Projeler | 6 | korunur |
| Şerit | 7 | 11, 14, 20'ye yayılır — her ikon paneliyle gelir |
| Şerit | 8 | 11 |
| Şerit | 9 | 5 |
| Proje ekranı | 11, 12 | korunur |
| Fotoğraf üret | 13, 14 | 5 |
| Fotoğraf üret | 15, 16, 17, 18 | 6 |
| Fotoğraf üret | 19, 20, 21, 22 | korunur |
| Video üret | 23 | 14, 17 |
| Video üret | 24, 28, 29 | 14 |
| Video üret | 25, 26 | 15 |
| Video üret | 27 | 16 |
| Ses üret | 30 | 20, 22 |
| Ses üret | 31 | 20 |
| Ses üret | 32 | 21 |
| Kuyruk | 33 | 3 |
| Kuyruk | 36 | 3, 9 |
| Kuyruk | 34, 35, 40, 41, 46 | 9 |
| Kuyruk | 37, 38, 39, 42, 43 | 10 |
| Kuyruk | 44, 45 | 4 |
| Kuyruk | 47 | korunur |
| Üreticiler | 48 | 11 |
| Üreticiler | 49, 50, 51, 52 | 12 |
| Üreticiler | 53 | 13 |
| Galeri | 54, 55, 56, 57 | 7 |
| Galeri | 58 | 18 (video), 22 (ses) |
| Galeri | 59, 60 | 8 |
| Galeri | 61 | 5 |
| Galeri | 62, 63, 64, 65 | 31 |
| Galeri | ~~66~~ | **iş yok** — karar: alt bardan üretim zaten yok, ses de eklenmeyecek |
| Galeri | 67, 68, 69 | 19 |
| Galeri | 70, 71, 72 | korunur |
| Detay | 73, 75, 82 | 23 |
| Detay | 74 | 24 |
| Detay | 76, 77, 78 | 25 |
| Detay | 80, 83 | 26 |
| Detay | 79, 81 | 27 |
| Detay | 84 | korunur |
| Export | 85, 86, 87, 88, 95 | 28 |
| Export | 89, 90, 91 | 29 |
| Export | 92, 93, 94, 96 | 30 |
| Adlandırma | 97 | 2 |
| Adlandırma | 98, 99 | 25 |
| Adlandırma | 100, 102 | 15 |
| Adlandırma | 101, 103 | 1 |
| Genel | 104 | 31 |
| Genel | 105 | 33 |
| Genel | 106 | korunur |
| Elle bulgular | 107, 108 | 33 |

**Korunanlar.** Fark belgesinin 13 öksüz davranışı (6, 11, 12, 19, 20, 21, 22, 47, 70, 71, 72,
84, 106) *"on üçü de kalıyor"* kararıyla iş üretmez: yükleme ve hata hâlleri, tek üretim kilidi,
bağlantı kartı, "Tümünü seç"in ikinci basışı, sıra kaydedilememesi, "Fotoğraf bulunamadı" ekranı,
pencere klavye davranışı, model alanı ara hâlleri, prompt örneği, gönderim öncesi kayıt. Bir
görevin planı bunlardan biriyle çakışırsa kararı orada verir — v4'te bağlantı kartı metninin yeni
sayaç diline çevrilmesi gibi.

## Açık sorular

Tasarım düzeyinde açık soru kalmadı — beş çelişki ve yedi suskunluk fark belgesinde kullanıcı
kararıyla kapandı (kararlar maddelerin altında). Spec'lere kalan **teknik seçimler** şunlar; hiçbiri
bu belgede verilmez:

| Seçim | Nerede karara bağlanır |
|---|---|
| Video/ses prompt'unu yazacak dil modeli | Görev 16 (ses için 21) spec'i |
| Video ve ses üreticilerinin altyapısı ve kurulum biçimi | Görev 12 ve 17 (ses için 22) spec'leri |
| Eski adlı dosyaların yeni şemayla birlikte yaşaması | Görev 2 spec'i |
| Birleşik videonun birleştirilme yolu | Görev 30 spec'i |
| Kuyruk kartlarında canlı noktanın davranışı (tasarım suskun) | Görev 9 spec'i |

## Koşunun sonu

**33 görevin 33'ü bitti.** Her görev kendi spec'i, kendi planı ve kendi commit'iyle;
`feat/queen-editor-v3` dalında, son commit `a878d59`. Takım durumu: **550 arka uç · 295 ön yüz
testi geçiyor**, `dist/` her ön yüz commit'inde yeniden üretildi.

**Elle doğrulamadan önce yapılacaklar** — ikisi de kullanıcının:

| Ne | Neden |
|---|---|
| `queen-editor/workflow_video_api.json` ve `workflow_audio_api.json` repoya konmalı | ComfyUI → **Export (API)** ile dışa aktarılır; ikisi de repoda yok, onlarsız video ve ses üretilemez |
| `queen-editor/app.ipynb` içindeki `BRANCH` `feat/queen-editor-v3` yapılmalı | Defter dalı klonluyor; bugün hâlâ `feat/queen-editor-v2` yazıyor |

**Colab turunda özellikle bakılacaklar** — bu koşuda testle kapatılamayan üç yer:

- **Yatay taşma** *(madde 107)*: jsdom yerleşim hesaplamıyor, düzeltme ancak gerçek pencerede
  görülür.
- **Seçim barının yüzmesi** *(madde 108)*: 28 piksel bir tercih, ölçülmüş bir sabit değil.
- **Export'un ffmpeg'i** *(Görev 30)*: Colab'da kurulu gelir; yerel çalıştırmada yoksa export
  ffmpeg'in kendi cümlesiyle durur.

---

# Koşu 2 — 13 Ağustos *(o zamanki adıyla "yol haritası v6")*

**Tarih:** 2026-08-13 · **Koşu dalı:** `feat/queen-editor-v3` ·
**Durum:** 6 görevin 6'sı yazıldı ve commit edildi (`5839783`'e kadar); **kullanıcının elle Colab
turu bekliyor** — aşağıdaki *Koşunun sonu*.
**Yerini aldığı koşu:** yok — bu, **Koşu 1**'in kapanışında kullanıcıya kalan iki üretim dosyasının
yerine geçen küçük bir koşu.
**Kaynak:** kullanıcı kararı (2026-08-13) — fark belgesi yok, bulgu koşunun kendisinden çıktı.

## Neden bu koşu var

Koşu 1 bitti ama uygulama iki üretim dosyası olmadan çalışamıyor: `workflow_video_api.json` ve
`workflow_audio_api.json`. İkisini de "kullanıcı ComfyUI'den Export (API) ile çıkarsın" diye
bıraktık. İkisi de yanlış çıktı:

- **Video grafiği zaten repoda.** `collab-toolbox/video_generator/wan22-arbuzai/workflow_api.json`
  API formatında ve `comfy_video_generator.py`'nin beklediği üç node'un üçünü de taşıyor (287,
  210, 233:240) — `photo_to_video.ipynb` bu grafiğin Drive kopyasını okuyor, aslı burada. Dışa
  aktarılacak bir şey yok, kopyalanacak bir dosya var.
- **Ses için ComfyUI grafı hiç kurulmamış.** `mmaudio_generate.ipynb` ComfyUI kullanmıyor: MMAudio
  reposunu klonlayıp **süreç içinde** çalıştırıyor, NSFW fine-tune ağırlıklarla. queen-editor'ün
  ses üreticisi ise olmayan bir ComfyUI grafiğine (`VHS_LoadVideoPath` + `MMAudioSampler`) yazıldı.

**Kullanıcı kararı (2026-08-13):** ses için ComfyUI grafı kurulmayacak. *"Şu an mmaudio için ne
kullanıyorsak birebir aynısı."* Yani queen-editor de MMAudio'yu süreç içinde çalıştıracak.

## Kapsam sınırı

- **Ses dışındaki motor değişmiyor.** Foto ve video ComfyUI'de kalır; değişen yalnız ses.
- **Defterin toplu iş mantığı taşınmaz.** `mmaudio_generate.ipynb`'in Drive tarama, batch, atlama
  ve mp4'e mux etme kısmı queen-editor'ün işi değil — queen-editor kuyruğu kendisi yönetiyor ve
  sesi ayrı bir `.wav` olarak saklıyor (video ile birleştirme export'un işi, Koşu 1'in Görev 30'u).
  Taşınan şey **ses üretiminin kendisi**: model yükleme, chunk'lama, `generate` çağrısı,
  parametreler.
- **Prompt yazımı değişmez.** Ses prompt'unu bugün olduğu gibi Grok yazıyor (`xai_prompt_writer`);
  defterdeki elle yazılmış `ACTION_PROMPTS` listesi taşınmaz. Defterin **negative prompt'u** ise
  taşınır: o bir model ayarı, kullanıcı metni değil.
- **Foto grafiği değişmez.**

## Bozulan yazılı karar

**FOUNDATION madde 6** bugün *"ComfyUI is the generation engine"* diyor. Ses artık süreç içinde
çalışacağı için bu madde daralıyor: ComfyUI **foto ve video**nun motoru; ses, uygulamanın kendi
sürecinde koşan ikinci bir motor. Maddenin yeniden yazılması Görev 6'nın işi — gerekçesiyle
birlikte, çünkü "neden iki motor" sorusunu ilk soran kişi o dosyaya bakacak.

## Nasıl çalışacağız

Koşu 1'deki dört adımın aynısı, görev bitmeden sonrakine geçilmez:

1. **Spec** — `docs/superpowers/specs/`, görevin kararları burada verilir.
2. **Plan** — `docs/superpowers/plans/`, TDD adımlarıyla.
3. **Full TDD** — hiçbir üretim kodu satırı, önce kırmızı bir test yokken yazılmaz.
4. **Commit** — görev başına bir commit; ön yüz değiştiyse `dist/` aynı commit'te.

Komutlar her seferinde birebir aynı: `python -m pytest queen-editor -q`,
`npm test --prefix queen-editor/frontend -- --run`, `npm run build --prefix queen-editor/frontend`.

## Blok 1 · Video grafiği

### Görev 1 — Video grafiği repoya girer

- **Ne çalışır:** `queen-editor/workflow_video_api.json` repoda durur; video üreticisi onu açar,
  üç node'unu bulur ve yamalar. Dosya `collab-toolbox`'tan **kopyalanır** — çalışma anında oradan
  okunmaz (CODE-STANDARD'ın bağımsızlık kuralı).
- **Nasıl görülür:** üreticiyi gerçek dosyayla besleyen bir test, üç node'un varlığını ve API
  formatını doğrular; "graf yok" hatası artık çıkmaz. Testin yeri belli: `test_workflow_asset.py`
  foto grafiği için aynısını zaten yapıyor, video onun ikizi olarak yanına yazılır.

### Görev 2 — Model listesi grafiğin istediğini söyler

- **Ne çalışır:** `model_groups.py`'deki video grubu, grafiğin gerçekten adını verdiği dosyalarla
  örtüşür. Bugün örtüşmüyor: graf `SmoothMix_Animations_XXX_High/Low` da istiyor, grup yalnız
  `SmoothMix_I2V_v2_High/Low` sayıyor. Üretici paneli eksik modeli "kurulu" diye gösteriyor.
- **Nasıl görülür:** shipped grafiği okuyup adı geçen her model dosyasının grupta bulunduğunu
  doğrulayan bir test; panel eksik dosyayı eksik olarak söyler.
- **Karar bekliyor:** grafın dört checkpoint'i de gerekli mi, yoksa ikisi devre dışı bir dalda mı
  — Görev 2 spec'inde grafın kendisine bakılarak verilir.

## Blok 2 · Ses motoru süreç içine taşınır

### Görev 3 — MMAudio üreticisi

- **Ne çalışır:** yeni bir veri katmanı adaptörü, ses üreticisi portunu ComfyUI yerine MMAudio ile
  karşılar: video dosyasını alır, sesini `.wav` olarak döndürür. Defterin ayarları birebir —
  `large_44k` mimarisi + NSFW fine-tune ağırlık, `NUM_STEPS=40`, `CFG_STRENGTH=5.5`,
  `INFERENCE_MODE="euler"`, negative prompt `"music, speech, voices, singing, talking, vocals"`,
  ve 10 saniyeyi aşan videoda 8 saniye hedefli chunk + 100 ms crossfade.
- **Nasıl görülür:** sahte bir mmaudio modülüyle koşan testler — üretici doğru parametreleri
  geçirir, seed'i kullanır, uzun videoyu parçalar, kısa videoyu parçalamaz, çıkan dosya `.wav`.
- **Üç uygulama gerçeği**, plan yazılırken sürpriz olmasın diye burada:
  - **`torch` ve `mmaudio` import'u tembel olmalı.** Test makinesinde ikisi de yok; modül
    yüklenirken import edilirse tüm takım çöker. İçeri girme noktası enjekte edilir, tıpkı
    diğer adaptörlerin istemcisi gibi.
  - **Port bayt veriyor, MMAudio dosya istiyor.** Üretici portu videoyu `(ad, bayt)` olarak
    veriyor; ffmpeg ve `load_video` yol istiyor. Adaptör baytı geçici bir dosyaya yazar ve
    işi bitince siler.
  - **Seed defterden taşınmaz.** Defter dosya adından seed türetiyor çünkü kuyruğu yok;
    queen-editor her işe zaten kendi seed'ini veriyor, o kullanılır.
- **Karar bekliyor:** modelin ne zaman yükleneceği ve bellekte kalıp kalmayacağı (ComfyUI da aynı
  GPU'da); chunk'lamanın bu sürümde ölü kod olup olmadığı (video süresi sabit ~5 sn); işin kendi
  negative prompt'u boş değilse defterin sabiti mi yoksa işinki mi kazanır.

### Görev 4 — Ses üreticisinin kurulumu

- **Ne çalışır:** üretici paneli sesin gerçekten neye ihtiyacı olduğunu sayar: NSFW ağırlık dosyası
  ve MMAudio'nun kendi temel ağırlıkları. Bugünkü `mmaudio_large_44k_v2.pth` satırı ComfyUI
  node'una aitti ve karşılığı yok.
- **Nasıl görülür:** ses üreticisi kurulu değilken panel eksik dosyayı adıyla söyler; kurulunca
  kuyruk ses işini alır.

### Görev 5 — Bağlama ve eski kodun kaldırılması

- **Ne çalışır:** `main.py` ses üreticisi olarak yeni adaptörü bağlar; `ComfyAudioGenerator` ve
  `AUDIO_WORKFLOW_PATH` silinir. Kuyruk, katman ve export tarafında hiçbir şey değişmez — port
  aynı port.
- **Nasıl görülür:** tam takım yeşil; `workflow_audio_api.json` adı repoda hiçbir yerde geçmez.

### Görev 6 — Defter ve belgeler

- **Ne çalışır:** `app.ipynb`'in kurulum hücresi MMAudio reposunu kurar (klonla + `pip install -e .`)
  ve ağırlıkları hazırlar; `BRANCH` `feat/queen-editor-v3` olur. FOUNDATION madde 6 iki motoru
  anlatacak biçimde yeniden yazılır, CODE-STANDARD'ın miras tablosuna MMAudio satırı eklenir.
- **Nasıl görülür:** defter baştan sona koşunca ses üretimi çalışır; belgelerde ComfyUI'ın tek
  motor olduğunu söyleyen cümle kalmaz.

## Kapsam tablosu

| Bulgu | Görev |
|---|---|
| Video grafiği repoda yok | 1 |
| Model listesi grafiğe uymuyor | 2 |
| Ses ComfyUI grafiği yok, olmayacak da | 3 |
| Ses üreticisinin model listesi yanlış | 4 |
| Eski ses adaptörü ve config girdisi | 5 |
| Defter kurulumu ve dal adı | 6 |
| FOUNDATION madde 6 daralıyor | 6 |

## Açık sorular

Hiçbiri bu belgede verilmez; her biri kendi görevinin spec'inde karara bağlanır:

| Seçim | Nerede |
|---|---|
| Grafın dört checkpoint'inin hepsi gerekli mi | Görev 2 |
| MMAudio modeli ne zaman yüklenir, bellekte kalır mı (ComfyUI ile aynı GPU) | Görev 3 |
| Chunk'lama bu sürümde taşınsın mı (video süresi sabit ~5 sn) | Görev 3 |
| Negative prompt: defterin sabiti mi, işin kendi alanı mı | Görev 3 |
| NSFW ağırlığı uygulama mı indirir, defter mi | Görev 4 |

## Koşunun sonu

**6 görevin 6'sı bitti**, her biri kendi spec'i ve commit'iyle. Arka uç takımı **573 test**
geçiyor; ön yüz bu koşuda hiç değişmedi.

Koşu sırasında çıkan, roadmap'te olmayan üç bulgu — üçü de kapatıldı:

| Bulgu | Nerede kapandı |
|---|---|
| VAE, grafiğin istediğinden başka adla listeleniyordu | Görev 2 |
| Video grafiğinin 11 custom node'u defterde hiç kurulmuyordu | Görev 6 *(karar 2'de ayrıca yazıldı)* |
| `ffmpeg` defterde kurulmuyordu — export ve ses kesme onu çağırıyor | Görev 6 |

**Colab turunda bakılacaklar:**

- **Ses gerçekten üretiyor mu** — MMAudio süreç içinde ilk kez koşacak; ağırlık panelden inecek.
- **GPU sığıyor mu** — ComfyUI'ın WAN'ı ile MMAudio aynı kartta *(Görev 3 karar 4: A100'de sığar,
  ölçülmedi)*.
- **Video ilk kez uçtan uca** — graf, node'lar ve modeller bu koşuda ilk kez bir arada.
- Koşu 1'in kendi listesi: yatay taşma, seçim barının boşluğu, export'un ffmpeg'i.

**Kalan tek elle iş:** push. Defter repoyu klonluyor, dolayısıyla Colab turu push'tan sonra
anlamlı.

---

# Koşu 3 — 13 Ağustos *(o zamanki adıyla "yol haritası v7")*

**Tarih:** 2026-08-13 · **Koşu dalı:** `feat/queen-editor-v3` ·
**Durum:** 12 görevin 12'si yazıldı ve commit edildi (`55b0fc2`'ye kadar); **push ve kullanıcının
elle Colab turu bekliyor** — aşağıdaki *Koşunun sonu*.
**Koşudan çıkan, kapatılmayan iki şey:** galeri karolarının tam boy PNG çekmesi (önizleme üretmek
kendi tasarımını ister, Görev 8) ve başarısız karede hover'la inen karartma (tasarım kararı,
Görev 10). İkisi de EKSIKLER'de, kullanıcının kararını bekliyor.
**Yerini aldığı koşu:** yok — **Koşu 2** kapandıktan sonra açılan yeni koşu.
**Kaynak:** `queen-editor/EKSIKLER.md` — kullanıcının elle UI turunda bulduğu 10 madde ve koşu
sırasında çıkan 2 madde.

## Neden bu koşu var

Koşu 2 bitti, uygulama Colab'da ilk kez elden geçirildi ve **üretim hiç çalışmadı**. Turdan çıkan
liste üç kümede toplanıyor: çalışmayan üretim, defterin üstlendiği kurulum işi, ve kullanıcıyı
bekleten/yanıltan arayüz. Bu koşu o listeyi kapatır.

## Kapsam sınırı

- **Yeni yetenek yok.** Bu koşu yalnız bulunan eksikleri kapatır; hiçbir görev yeni bir ekran,
  yeni bir üretim türü veya yeni bir dosya türü getirmez.
- **Motorlar değişmiyor.** Foto ve video ComfyUI'de, ses süreç içinde kalır
  ([FOUNDATION madde 6](../../../queen-editor/FOUNDATION.md)).
- **Ön yüz aptal kalır.** Hiçbir görevin **kuralı** tarayıcıya yazılmaz: süre bilgisi de, "kurulu
  mu" cevabı da, bir işin ne kadar sürdüğü de sunucunundur — tarayıcı yalnız çizer
  ([FOUNDATION madde 4](../../../queen-editor/FOUNDATION.md)). Bir görev ön yüzde çözülebiliyor
  gibi duruyorsa, önce sunucuda karşılığı var mı diye bakılır. Ayrım şurada: elindekini ekranda
  tutmak çizim işidir ve ön yüzde kalır; o şeyin **ne kadar sürede geldiği** sunucunun işidir.
- **Katman kuralları aynen geçerli.** `presentation → domain ← data → services`, `feature ↛
  feature`, somut bağlama yalnız `backend/main.py`
  ([CODE-STANDARD](../../../queen-editor/CODE-STANDARD.md)).

## Bozulan yazılı karar

Blok 2 bugün yazılı olan bir kararı iptal ediyor: **CODE-STANDARD'ın bağımsızlık tablosu**, model
indirme/doğrulama makinesinin `app.ipynb`'e birebir kopyalandığını söylüyor, ve `model_groups`
foto üreticisinin "defterin kurduğu" üretici olduğunu yazıyor. Bundan sonra **defter hiçbir model
indirmez**; kurulum uygulamanın kurulum ekranının işidir, defterin işi kod ve kütüphane kurmaktır.
Bu iki belgenin (FOUNDATION + CODE-STANDARD) güncellenmesi **Görev 4'ün işidir** — gerekçesiyle
birlikte, çünkü "modeller neden defterden inmiyor" sorusunu ilk soran kişi oraya bakacak.

## Nasıl çalışacağız

Koşu 1 ve 2'deki dört adımın aynısı; görev bitmeden sonrakine geçilmez:

1. **Spec** — `docs/superpowers/specs/`, görevin kararları burada verilir.
2. **Plan** — `docs/superpowers/plans/`, TDD adımlarıyla.
3. **Full TDD** — hiçbir üretim kodu satırı, önce kırmızı bir test yokken yazılmaz.
4. **Commit** — görev başına bir commit; ön yüz değiştiyse `dist/` aynı commit'te.

Komutlar her seferinde birebir aynı: `python -m pytest queen-editor -q`,
`npm test --prefix queen-editor/frontend -- --run`, `npm run build --prefix queen-editor/frontend`.

## Bağımlılık haritası

- **Blok 1 herkesin önkoşulu:** üretim çalışmadan hiçbir madde elle doğrulanamaz.
- **Blok 2 kendi içinde zincir:** 2 → 3 → 4 → 5.
- **Blok 3'te 7, 6'ya bağlı.** 8 en sona bırakıldı: 6 ve 7 bittikten sonra geriye kalan gerçek
  maliyet ölçülebilir olur.
- **Blok 4 serbest:** dört görev birbirinden bağımsız, sıra tercih meselesi.

## Blok 1 · Uygulama çalışsın

### Görev 1 · Üretim sözleşmesi tek olsun

**Bulgu:** Fotoğraf üretimi hiç çalışmıyor — aynı kare üç kez denenip üretim duruyor. Ses üreticisi
de kuyruğun beklediğinden başka bir şey döndürüyor; ilk ses işinde düşer.

**Ne olacak:** Üç üretici de (foto, video, ses) kuyruğun beklediği tek sözleşmeyi karşılar, ve o
sözleşme yazılı olduğu yerde de doğru yazar. Kuyruğu üç üreticiyle birlikte baştan sona koşan bir
test gelir — bugün böyle bir test olmadığı için takım yeşilken uygulama çalışmıyordu.

**Bağımlılık:** Yok. Diğer on bir görevin önkoşulu.

**Bitti sayılır:** Foto, video ve ses işleri kuyrukta uçtan uca geçiyor; sözleşmeyi bozan bir
üretici eklendiğinde test kırmızı veriyor.

## Blok 2 · Kurulum uygulamanın işi

### Görev 2 · Civitai anahtarı uygulamaya geçsin

**Bulgu:** Uygulama anahtar isteyen bir kaynaktan indiremiyor. Civitai'de duran modeller bu yüzden
"uygulamadan inmez" diye işaretli ve defterin işi.

**Kullanıcı kararı (2026-08-13):** Anahtar Colab Secret'ta durur, defter onu uygulamaya geçirir,
indirmeyi uygulama yapar. Kullanıcıdan fazladan bir adım istenmez; anahtar hiçbir yere yazılmaz ve
hiçbir yerde basılmaz.

**Ne olacak:** Kurulum ekranı Civitai'deki video modellerini kendi indirir.

**Bağımlılık:** Görev 1 — kurulumun doğru olduğu ancak çalışan bir üretimle görülebilir.

**Bitti sayılır:** Video üreticisi "kurulu değil" durumundan tek tıkla kuruluyor, defter hiçbir
video modeline dokunmuyor.

### Görev 3 · Foto modelleri kurulum listesine girsin

**Bulgu:** Foto üreticisinin kurulum listesi boş. Uygulama "foto kurulu mu" sorusuna cevap veremiyor
ve kuramıyor.

**Ne olacak:** Foto modelleri de diğer üreticiler gibi listede yerini alır ve kurulum ekranından
kurulur.

**Bağımlılık:** Görev 2 — bu modeller anahtar olmadan inmiyor.

**Bitti sayılır:** Kurulum ekranı üç üreticiyi de aynı dille gösteriyor; hiçbiri "bunu defter
kurar" demiyor.

### Görev 4 · Defter model indirmeyi bıraksın

**Bulgu:** Defter hâlâ foto modellerini ve ses modelini indiriyor.

**Ne olacak:** Defterin model indirme işi tamamen kalkar; defter yalnız kod ve kütüphane kurar,
uygulama modelleri kurulmamış halde açılır ve kullanıcı kurulum ekranından kurar. Bu görev
**FOUNDATION ve CODE-STANDARD'ı da günceller** — yukarıdaki *Bozulan yazılı karar*.

**Bağımlılık:** Görev 2 ve 3 — önce uygulama indirebilir olmalı, yoksa defterin de indirmediği bir
ara durum kalır.

**Bitti sayılır:** Temiz bir Colab turunda uygulama açılıyor, hiçbir model inmemiş oluyor, üçü de
ekrandan kuruluyor; iki belge de yeni durumu anlatıyor.

### Görev 5 · Kurulum ekranı doğruyu söylesin

**Bulgu:** Kur'a basınca anında geri bildirim yok, tepki gecikmeli geliyor — arada ne olduğu belli
değil. Kurulum kartındaki ilerleme çubuğu da gerçek indirmeyle uyuşmuyor.

**Ne olacak:** Tıklar tıklamaz durum görünür. Uydurma çubuk kalkar; yerine ne indiğini söyleyen
dürüst bir satır kalır.

**Bağımlılık:** Görev 2–4 — kurulumun nihai davranışına karşı bir kez yazılsın, iki kez değil.

**Bitti sayılır:** Kur'a basan kullanıcı bir daha basmak zorunda kalmıyor; ekranda gördüğü hiçbir
şey gerçekten sapmıyor.

## Blok 3 · Bekleme hissi

Üç görev büyük ihtimalle **tek bir kökü** paylaşıyor: galerinin listesini almak pahalı, ve o liste
her ekran değişiminde yeniden isteniyor. Görev 6'nın spec'i bunu ölçtüğünde kök gerçekten oradaysa
Görev 8 kendiliğinden küçülür — o zaman 8, kalan farkı kapatan görev olur, ayrı bir iş değil.

### Görev 6 · Ekran değişince galeri sıfırdan yüklenmesin

**Bulgu:** Detaya girip galeriye dönünce yükleme baştan başlıyor; detayda da bekleniyor.

**Ne olacak:** Ekranlar arasında gidip gelmek elde olanı çöpe atmaz — bu bir çizim kararıdır ve ön
yüzde kalır. Listenin **maliyeti** ise sunucunun işi ve bu görevin spec'inde ölçülür; ölçüm
Görev 8'in ne olduğunu da belirler.

**Bağımlılık:** Blok 1.

**Bitti sayılır:** Detay ↔ galeri geçişi beklemesiz.

### Görev 7 · Kuyruğa eklenen kare anında görünsün

**Bulgu:** "Eklendi" yazıyor ama kare bir dakika kadar ekrana düşmüyor; insan bir daha basıyor.

**Ne olacak:** Kuyruğa giren kare, girdiği anda listede olur.

**Bağımlılık:** Görev 6 — aynı liste yolunu kullanıyor, önce o yol düzelmeli.

**Bitti sayılır:** Ekle'ye basınca kare hemen görünüyor; ikinci basış refleksi kalmıyor.

### Görev 8 · Açılışta galeri hızlı dolsun

**Bulgu:** Uygulama açılışında fotoğraflar çok yavaş yükleniyor.

**Ne olacak:** İlk dolum kullanıcıyı bekletmez. Neyin pahalı olduğu 6 ve 7'den sonra ölçülür ve
maliyet nerede ise orada azaltılır — kararın yeri yine sunucu.

**Bağımlılık:** Görev 6 ve 7.

**Bitti sayılır:** Proje açılışı, dolu bir galeride bile bekleme hissi vermiyor.

## Blok 4 · Arayüz

Dördü birbirinden bağımsız; sıra serbest.

### Görev 9 · Yan barda açık ikona basınca panel kapansın

**Bulgu:** Açık panelin ikonuna tekrar basmak hiçbir şey yapmıyor.

**Ne olacak:** Aynı ikona basınca panel komple kapanır ve tuval genişler — kod editörlerindeki gibi.

**Bitti sayılır:** İkon aç/kapa gibi çalışıyor; kapalıyken tuval genişlemiş oluyor.

### Görev 10 · Kare hover'da yerinden oynamasın

**Bulgu:** Karenin üstüne gelince kart garip biçimde ortalanıyor.

**Ne olacak:** Kare üstüne gelindiğinde yerinde kalır.

**Bitti sayılır:** Galeride fare gezdirmek hiçbir kareyi kaydırmıyor.

### Görev 11 · Durum yazısı okunur olsun

**Bulgu:** "foto kuyrukta" yazısı çok soluk, okunmuyor.

**Ne olacak:** Durum etiketi okunacak kadar açık olur — üç durumun üçünde de aynı ölçüyle.

**Bitti sayılır:** Etiket normal bakışta okunuyor.

### Görev 12 · Video süresi tek yerden gelsin

**Bulgu:** Video süresi iki yerde yazılı: grafikte ve export'un kendi sabitinde. Bugün tutuyorlar;
grafik değişirse export yanlış süre gösterir.

**Ne olacak:** Süre tek bir kaynaktan okunur, ikinci kopya kalkar.

**Bitti sayılır:** Grafikteki süre değiştiğinde export'un söylediği süre kendiliğinden takip ediyor.

## Koşunun sonu

Son görev commit edildikten sonra:

1. **Push** — defter repoyu klonluyor, bu yüzden Colab turu ancak push'tan sonra mümkün
   ([FOUNDATION madde 1](../../../queen-editor/FOUNDATION.md)).
2. **Kullanıcının elle Colab turu** — temiz makine, hiçbir model kurulu değil: kurulum ekranından
   üçünü kur, bir kare üret, videosunu ve sesini yap, export al.
3. **CLAUDE.md** queen-editor bölümü bu koşuyu göstersin, önceki koşu kapandı olarak işaretlensin.
4. **EKSIKLER.md** kapanan maddelerden temizlenir — bir sonraki tur temiz listeyle başlar.

---

# Koşu 4 — 13 Ağustos *(o zamanki adıyla "yol haritası v8")*

**Tarih:** 2026-08-13 · **Koşu dalı:** `feat/queen-editor-v3` · **Durum:** 3/3 bitti, push ve Colab turu bekliyor.
**Öncesi:** **Koşu 3** — 12 görev kapandı.
**Kaynak:** kullanıcı kararı (2026-08-13), Koşu 3'ün Colab turundan çıktı.

## Neden bu koşu var

Koşu 3 defterin **model** indirmesini kaldırdı, ama defter hâlâ MMAudio kütüphanesini klonlayıp
kuruyor. Kullanıcı Colab'da o satırları görünce sordu ve kararını verdi: **bu kurulum da defterde
olmasın, gerektiğinde yapılsın.** Yani ses motorunun kütüphanesi, ses üreticisi kurulurken kurulur.

Bir de Koşu 3'te eklenen "Modeller — burada inmez" hücresi kalkıyor: olmayan bir şeyi anlatan bir
hücre, defterde yer tutmaktan başka iş görmüyor.

## Kararlar (kullanıcı, 2026-08-13)

1. **Kütüphaneyi Üreticiler panelindeki "Kur" kurar.** İlk ses işinin kendi kurması elendi: kimse
   düğmeye basmadığı için kurulum üretimin ortasında olur, ve o sırada ekran ilerlemiyormuş gibi
   görünür. Ses için kural artık foto ve videoyla aynı: kurmadan iş başlamaz.
2. **Kurulumdan sonra uygulama kütüphaneyi canlı kullanmayı dener.** Olmazsa panel açıkça
   "uygulamayı yeniden başlat" der (Colab'da Flask hücresini tekrar çalıştırmak). Her kurulumdan
   sonra koşulsuz yeniden başlatma istemek elendi — çoğu turda gerekmiyor.
3. **Defterin adı "Queen Editor — Colab kurulumu".** Bölüm numarası yok; defterin işi kurmak ve
   sunucuyu açmak, üretim uygulamanın içinde.

## Kapsam sınırı

- **ComfyUI ve custom node'lar defterde kalır.** Onlar isteğe bağlı değil: ComfyUI ayağa kalkmadan
  uygulama foto da video da üretemez, ve node'lar ComfyUI'nin başlangıç şartı. MMAudio'yu ayıran
  şey, yalnız ses işi geldiğinde gerekmesi.
- **Yeni bir yetenek yok.** Kurulumun yeri değişiyor, davranışı değil.

## Kullanıcıya söylenen risk

Kütüphane kurulumu uygulamanın içine girince, kurulum hatası artık defterin fail-loud hücresinde
değil, bir isteğin içinde patlar. Kullanıcı bunu bilerek istedi; karşılığında defter yalnız
uygulamanın **koşması** için gerekli olanı kuruyor, ses motorunu kullanmayan bir tur onu hiç
kurmuyor.

## Görevler

### Görev 1 · Ses motoru gerektiğinde kurulsun

**Bulgu:** Defter MMAudio'yu her Run all'da klonlayıp `pip install -e` ediyor — sesi hiç
kullanmayan bir tur bile.

**Ne olacak:** Ses üreticisinin kurulumu kütüphaneyi de kapsar. Panelden "Kur"a basınca önce
kütüphane, sonra ağırlıklar gelir; ekran hangisinde olduğunu söyler. "Kurulu mu" sorusunun cevabı
da kütüphaneyi sayar — ağırlık dosyası yerinde ama kütüphane yoksa ses üreticisi kurulu değildir.
Kurulum bitince uygulama kütüphaneyi canlı kullanmayı dener; göremezse panel yeniden başlatmayı
ister.

**Bağımlılık:** Yok.

**Testler ne diyecek:**
- Ses kurulumu kütüphaneyi ağırlıklardan **önce** yapar; kütüphane zaten varsa tekrar kurulmaz.
- Kurulum sırası ekrana yansır: kütüphane adımındayken panel onu söyler, dosya adımındayken dosyayı.
- Kütüphane yoksa ses üreticisi "kurulu" görünmez; ağırlık dosyası dursa bile.
- Kütüphane kurulumu hata verirse ağırlıklara geçilmez ve hata panelde kendi sözleriyle görünür.
- Kurulumdan sonra kütüphane hâlâ görünmüyorsa panel yeniden başlatmayı isteyen cümleyi taşır.
- Foto ve video üreticilerinin kurulumu bugünkü davranışını aynen sürdürür.

**Test edilmeyen tek parça:** `git`/`pip` komutunu gerçekten çalıştıran sınıf — ComfyUI istemcisi
ve ffmpeg dışa aktarıcısı gibi dış dünya. Sahtesi yalnız sahteyi test ederdi
([CODE-STANDARD](../../../queen-editor/CODE-STANDARD.md)); kararlar onun üstündeki katmanda.

**Bitti sayılır:** Temiz makinede defter MMAudio'ya hiç dokunmuyor; ses üreticisi panelden tek
tıkla kuruluyor ve bir ses işi baştan sona geçiyor.

### Görev 2 · Defterden ses hücreleri ve model notu kalksın

**Bulgu:** Defterde MMAudio kurulum hücresi, onun markdown başlığı ve "Modeller — burada inmez"
notu duruyor.

**Ne olacak:** Üçü de silinir. Defterde kalan kurulum ComfyUI, custom node'lar ve ffmpeg —
uygulamanın koşması için gerekli olanlar.

**Bağımlılık:** Görev 1 — önce uygulama kurabilir olmalı, yoksa hiç kimsenin kurmadığı bir ara
durum kalır.

**Testler ne diyecek:** Defterde `MMAudio` geçen tek satır yok. Bu, Koşu 3'ün "model indirmeyi defter
yapmaz" testinin yanına aynı biçimde yazılır — bir daha eklenirse test söyler.

**Bitti sayılır:** Defteri Run all ile koşan biri ses motoruna dair hiçbir kurulum görmüyor.

### Görev 3 · Defterin ve README'nin adı bugünü anlatsın

**Bulgu:** Defterin başlığı *"Queen Editor — Tek foto (Bölüm 4)"*. Ne "tek foto" ne "Bölüm 4"
doğru: uygulama üç katman üretiyor, dizi export ediyor, üreticilerini kendi kuruyor. README aynı
eskimeyi taşıyor ("two-screen web UI", "Part 1…4").

**Ne olacak:** Başlık **"Queen Editor — Colab kurulumu"** olur; giriş paragrafı ve README uygulamanın
bugün ne olduğunu söyler; bölüm numaraları kalkar — kapanmış roadmap'lerin sırası zaten `docs/`
altında.

**Bağımlılık:** Görev 2 (aynı metinlere dokunuyor).

**Testler ne diyecek:** Buranın testi yok; değişen şey metin, ve bir başlığın doğru olup olmadığını
test değil okuyan anlar. Görev 1 ve 2'nin testleri koşuyor olacak.

**Bitti sayılır:** Defteri ilk kez açan biri ne yaptığını başlıktan doğru anlıyor.

## Nasıl çalışacağız

Koşu 3'ün aynısı: görev başına **spec → plan → full TDD → tek commit**. Test önce yazılır, kırmızı
görülür, sonra kod. Ön yüz değişirse `dist/` aynı commit'te. Komutlar:
`python -m pytest queen-editor -q`, `npm test --prefix queen-editor/frontend -- --run`,
`npm run build --prefix queen-editor/frontend`.

## Koşunun sonu

Push, sonra temiz bir Colab turu: Run all → Üreticiler'den üçünü kur → foto, video, ses üret →
export.

---

# Koşu 5 — 13 Ağustos *(o zamanki adıyla "yol haritası v9")*

**Tarih:** 2026-08-13 · **Koşu dalı:** `feat/queen-editor-v3` · **Durum:** 2/2 bitti, push ve Colab turu bekliyor.
**Öncesi:** **Koşu 4** — 3 görev kapandı, Colab turunda kurulum çalışmadı.

## Neden bu koşu var

Colab turunda üç üreticinin üçü de kurulamadı: foto ve video Civitai'nin yönlendirmesinde **403**,
ses ise kurulup süreçte görünmedi. Kullanıcı kararını verdi: **kurulum uygulamadan çıkacak,
Colab'da yapılacak** — `collab-toolbox`'ta yıllardır çalışan yöntemle.

Bu, Koşu 3 ve 4'ün yönünü tersine çeviriyor. Sebebi de yazılı olsun: uygulamanın indiricisi
kanıtlanmış hücrenin bildiği bir şeyi bilmiyordu ve öğrenmesi yeni iş demekti; kullanıcı o işi
yapmak yerine çalışan yöntemi kullanmayı seçti.

## Kapsam sınırı

- **Şimdilik yalnız fotoğraf.** Video ve ses modelleri bu koşuda kurulmuyor; sıraları gelince.
- **Panel kalıyor, ama sadece söylüyor.** Neyin kurulu olduğunu göstermeye devam eder; kurulu
  olmayan için "Colab'dan kur" der. Uygulama artık hiçbir şey indirmiyor.

## Görevler

### Görev 1 · Kurulum uygulamadan kalksın

**Ne olacak:** İndirme, kurulum, iptal — hepsi backend'den ve arayüzden silinir. Geriye tek soru
kalır: "bu üretici kurulu mu?" Panel onu cevaplamaya devam eder, ama artık bir şey yapamaz;
kurulu olmayan satır kullanıcıyı Colab defterine yollar.

**Bağımlılık:** Yok.

**Bitti sayılır:** Uygulamada indirme yapan tek satır kod yok; panel üç üreticinin durumunu doğru
gösteriyor ve kurulmamış olan için ne yapılacağını söylüyor.

### Görev 2 · Fotoğraf modelleri defterde kurulsun

**Ne olacak:** Defter fotoğraf grubunun beş dosyasını kurar — `collab-toolbox`'taki çalışan
hücrenin yöntemiyle, birebir. Ağır indirmeden önce kapılı erişim yoklanır, her dosya indikten
sonra doğrulanır, bozuk dosya silinmez. Kurulum **Flask'tan önce** gelir: uygulama açıldığında
her şey yerinde olsun, panel de doğru cevabı bir kez okusun.

**Bağımlılık:** Görev 1 — önce uygulamadaki ikinci yol kalkmalı, yoksa yine iki kurulum yolu olur.

**Bitti sayılır:** Temiz makinede Run all sonunda fotoğraf üreticisi kurulu görünüyor ve bir foto
üretiliyor.

## Sonraki koşuya kalanlar

Video ve ses modellerinin defterde kurulması. Kullanıcı önce fotoğrafın uçtan uca çalıştığını
görmek istiyor.

## Nasıl çalışacağız

Görev başına spec → plan → TDD → tek commit. Ön yüz değişirse `dist/` aynı commit'te.

---

# Koşu 6 — 13 Ağustos *(o zamanki adıyla "yol haritası v11")*

**Tarih:** 2026-08-13 · **Koşu dalı:** `feat/queen-editor-v3` · **Durum:** 6/6 — bitti, Colab turu bekliyor
**Öncesi:** [Colab kurulum seçimi](../plans/2026-08-13-queen-editor-colab-kurulum-secimi.md) ve
[v10 Görev 1](../plans/2026-08-13-queen-editor-v10-gorev-1-uretim-kendi-baslamasin.md) — ikisi de kapandı,
Colab turu sürüyor. *(Bu ikisi arada kalan işlerdi; "v10" diye bir yol haritası hiç yazılmadı.)*

## Neden bu koşu var

Kullanıcı Colab'da üretim denedi. Video prompt'u yazılamadı — xAI anahtarı reddedildi — ve üretim
durdu. Bu arada üç arayüz hatası daha çıktı: video panelinde seçili kare sayısı artmıyor, üretim
durduğu hâlde kareler kuyrukta görünüyor, seçim kalkınca kareler üstündeki halkalar kalıyor. Listede
bekleyen iki küçük madde de var.

Kullanıcı asıl soruyu sordu: **"testler zayıf mı kalıyor, çünkü sürekli hata buluyorum?"** Bakıldı,
cevap kısmen evet. 584 backend + 307 frontend testi var ama bulunan hataların hepsi aynı yerde:
**dikişlerde.** Her test bir parçayı, ona elle verdiğim girdilerle sınıyor; parçaların birbirine
bağlandığı yeri hiçbiri sınamıyor. Video panelinin sayısı "gelen listeyi doğru sayıyor mu" diye test
edilmiş, "doğru liste geliyor mu" diye değil.

Onun için bu koşunun çalışma biçimi değişiyor (aşağıda).

## Nasıl çalışacağız

**Her görev iki döngü.** Önce yalnız testler: spec → plan → testleri yaz → commit. O commit takımı
**kırmızı bırakır** ve mesajı hangi testlerin neden düştüğünü söyler. Sonra implementasyon: spec →
plan → kodu yaz → commit; takım yeşile döner.

Sebebi: testi kodla aynı nefeste yazınca test kodun zihin modelini miras alıyor ve aynı körlüğü
taşıyor. Araya commit sınırı koymak testi davranıştan yazmaya zorluyor — ortada henüz implementasyon
yok ki ondan kopya çekilsin. Yan faydası, implementasyon spec'inin kırmızı bir takıma karşı
yazılması: "bitti" bir kanaat değil, ölçülen bir şey oluyor.

**İstisna yok** — iki satırlık bir silme de iki döngü. Ön yüz değişen her görevde `dist/`
implementasyon commit'ine girer. Kullanıcı en sonda toplu Colab testi yapar; koşu boyunca durulmaz.

## Kapsam sınırı

- **Kurulum maddelerine dokunulmuyor.** Listede duran foto 403, video 403 ve ses maddelerini bu koşu
  kapatmıyor — onları kullanıcının Colab testi kapatacak.
- **"Claude" başlığındaki iki karar dışarıda:** galeri karolarına küçük önizleme ve başarısız karede
  hover karartması. İkisi de kendi tasarımını ister, koşuyu uzatırlar.

## Görevler

### Görev 1 · xAI anahtarı indirmeden önce yoklanır

**Ne olacak:** Defter, dışarıya bakan her şeyi ağır işten önce yokluyor — GitHub token'ı, Civitai
çerezi, disk, GPU — ama xAI anahtarını yoklamıyor. Bu yüzden anahtarın ölü olduğu ancak kurulum,
foto üretimi ve kuyruğa video atıldıktan sonra öğreniliyor. Anahtar da ilk saniyede yoklanacak:
xAI reddederse kendi cevabı basılacak, video kurulacaksa koşu duracak, kurulmayacaksa uyarıp
geçecek. Yapıştırırken sona yapışan boşluk da temizlenecek — bugünkü hatanın olası sebeplerinden
biri o.

**Bağımlılık:** Yok.

**Bitti sayılır:** Geçersiz anahtarla açılan bir koşu, hiçbir şey inmeden, xAI'ın kendi cümlesiyle
duruyor. Anahtarsız foto koşusu eskisi gibi çalışıyor.

### Görev 2 · Video panelinde seçili kare sayısı görünür

**Ne olacak:** Galeride kare seçilince video paneli sayıyı görmüyor. Düzeltilecek. Bu görev aynı
zamanda koşunun test zeminini kuruyor: ekranı gerçek gibi kurup kullanıcı gibi kullanan testler —
kare seç, sayıyı oku. Sonraki iki görev bu zemine yaslanıyor.

**Bağımlılık:** Yok, ama 3 ve 4 buna bağlı.

**Bitti sayılır:** Galeriden kare seçmek video panelindeki sayıyı değiştiriyor, ve bunu ekranı
uçtan uca kuran bir test söylüyor.

### Görev 3 · Duran üretim kuyrukta görünmez

**Ne olacak:** Hata üretimi durdurduğu hâlde kareler hâlâ "video kuyrukta" diyor. Duran bir kuyruk
kuyrukta görünmeyecek. Hatanın arayüzde mi sunucuda mı olduğu kendi spec'inde çıkacak — test
davranışı yazacağı için ikisinde de aynı test geçerli.

**Bağımlılık:** Görev 2'nin zemini.

**Bitti sayılır:** Üretim durdurulduktan sonra hiçbir kare kuyrukta bekliyormuş gibi görünmüyor.

### Görev 4 · Seçim kalkınca ✓ halkaları da kalkar

**Ne olacak:** Kareler seçilip sonra seçim kaldırılınca alttaki çubuk kayboluyor ama karelerin
üstündeki halkalar duruyor; seçim sürüyor mu bitti mi anlaşılmıyor. Seçim biterse halkalar da
bitecek.

**Bağımlılık:** Görev 2'nin zemini. Görev 5'ten önce olmalı: halka önce doğru davransın, sonra
adres değiştirsin.

**Bitti sayılır:** Seçim kalktığı anda karelerde seçimden eser kalmıyor.

### Görev 5 · Kare köşeleri yeniden dağıtılır

**Ne olacak:** Durum yazısı ("foto kuyrukta") tasarımın dediği yere, sol üste geçecek. ✓ seçim
halkası sağ üste taşınacak; halka belirdiğinde sıra numarası kaybolacak — seçim yaparken bakılan şey
resim, numara değil. Böylece hiçbir şey fare gelince yerinden oynamıyor.

**Bağımlılık:** Görev 4.

**Bitti sayılır:** Yazı sol üstte, halka sağ üstte, halka görünürken numara görünmüyor ve kartın
içinde fare gelince yer değiştiren hiçbir şey yok.

### Görev 6 · LLM açıklamaları iki panelden de kalkar

**Ne olacak:** Video ve ses panellerinin altındaki "prompt'u otomatik: LLM yazar" açıklaması
kalkacak. İkisi birden — iki panel tek bileşen ve tasarım birebir aynı olmalarını istiyor, birini
bırakmak onları görünür şekilde ayırırdı.

**Bağımlılık:** Yok.

**Bitti sayılır:** İki panelin de altında açıklama yok.

## Sonraki koşuya kalanlar

Galeri karolarının küçük önizlemeleri ve başarısız karede hover karartması — ikisi de tasarım kararı
bekliyor. Bir de kullanıcının Colab turundan çıkacak yeni maddeler.

---

# Koşu 7 — 14 Ağustos *(o zamanki adıyla "yol haritası v12")*

**Tarih:** 2026-08-14 · **Koşu dalı:** `feat/queen-editor-v3` · **Durum:** 2/2 — bitti, Colab turu bekliyor
**Öncesi:** **Koşu 6** — kapandı. Bu koşu onun Colab turundan çıktı.

## Neden bu koşu var

Kullanıcı Koşu 6'yı Colab'da çalıştırdı. Tur onun düzeltmelerini ekrana getirdi ve iki yeni şey
çıkardı.

**Ses hiç üretilemiyor.** Kuyruk bir ses işini tohumsuz planlıyor — ses işinin kendi tohumu yok,
çünkü kullanıcıya sorulan bir şey değil. Fotoğraf işleri bu duruma hiç düşmüyor (her fotoğrafın
kendi tohumu var), video tohumsuzluğu kaldırıyor, ses kaldırmıyor: ilk karede patlıyor —
*"manual_seed expected a long, but got NoneType"*. Aynı kare üç kez denendikten sonra üretim
duruyor. Yani ses üreticisi kurulu olsa bile bugün tek bir ses çıkmıyor.

**Kareler sürüklenip sıralanamıyor.** Koşu 6 galerinin sürükleme kodunun tek satırına dokunmadı —
yani bu kırılma ya ondan eski, ya da galerinin dışında bir yerde. Nerede olduğu görevin kendi
spec'inde çıkacak.

İkisi de yine **dikişte**. Ses için: tohumun plandan üreticiye giden yolunu uçtan uca izleyen bir
test yok, her parça kendi girdisiyle ayrı ayrı sınanmış. Sürükleme için: testler sürüklemenin
başladığını varsayıp devamını sınıyor — *başlayıp başlamadığını* soran bir test yok. Bulunan her
hatanın aynı yerden çıkması tesadüf değil, o yüzden çalışma biçimi Koşu 6'dakiyle aynı kalıyor.

## Nasıl çalışacağız

**Her görev iki döngü.** Önce yalnız testler: spec → plan → testleri yaz → commit. O commit takımı
**kırmızı bırakır** ve mesajı hangi testlerin neden düştüğünü söyler. Sonra implementasyon: spec →
plan → kodu yaz → commit; takım yeşile döner.

Sebebi: testi kodla aynı nefeste yazınca test kodun zihin modelini miras alıyor ve aynı körlüğü
taşıyor. Araya commit sınırı koymak testi davranıştan yazmaya zorluyor.

**İstisna yok.** Ön yüz değişen her görevde `dist/` implementasyon commit'ine girer. Kullanıcı en
sonda toplu Colab testi yapar; koşu boyunca durulmaz.

## Kapsam sınırı

- **Karar bekleyen iki tasarım işi dışarıda:** galeri karolarına küçük önizleme, başarısız karede
  hover karartması. İkisi de kendi tasarımını ister.
- **Bu koşu sesin patlamamasını sağlar, kulağa nasıl geldiğini değil.** Üretilen sesin kalitesi ve
  üreticinin gerçekten kurulu olduğu ancak bir Colab turuyla görülür.

## Görevler

### Görev 1 · Tohumsuz bir iş üretimi durdurmuyor

**Ne olacak:** Ses işleri tohumsuz planlanıyor ve ses üreticisi tohumsuz bir işi kaldıramıyor —
ilk karede patlayıp bütün kuyruğu durduruyor. Tohumsuz bir iş artık üretimi durdurmayacak; ses
işinin tohumu nereden gelecek — hiç gelmeyecek mi, plan mı verecek, üretici mi seçecek — görevin
kendi spec'inde kararlaşacak. Tohumun plandan üreticiye gidişi üç katman için de uçtan uca
sınanacak; bugün eksik olan tam olarak o yol.

**Bağımlılık:** Yok.

**Bitti sayılır:** Kuyruğa atılan bir ses işi baştan sona geçiyor, ve tohumsuz bir iş hiçbir
katmanda üretimi durdurmuyor.

### Görev 2 · Kareler yeniden sürüklenebiliyor

**Ne olacak:** Galeride kare sürükleyip sıra değiştirmek çalışmıyor. Çalışır hâle gelecek. Kırığın
tarayıcının sürüklemeyi hiç başlatmamasından mı, yoksa bırakılan sıranın kaydedilmemesinden mi
geldiği görevin kendi spec'inde çıkacak — test davranışı yazacağı için ikisinde de aynı test
geçerli.

**Bağımlılık:** Yok.

**Bitti sayılır:** Bir kare sürüklenip başka bir karenin yerine bırakıldığında yeni sırada kalıyor,
sayfa yenilendiğinde de orada duruyor.

## Sonraki koşuya kalanlar

Galeri karolarının küçük önizlemeleri ve başarısız karede hover karartması — ikisi de tasarım kararı
bekliyor. Bir de bu koşuyu kapatacak Colab turundan çıkacak yeni maddeler.

---

# Koşu 8 — 14 Ağustos *(o zamanki adıyla "yol haritası v13")*

**Tarih:** 2026-08-14 · **Koşu dalı:** `feat/queen-editor-v3` · **Durum:** 2/2 — bitti, Colab turu bekliyor
**Öncesi:** **Koşu 7** — kapandı. Bu koşu onun Colab turundan çıktı.

## Neden bu koşu var

Kullanıcı Koşu 7'yi Colab'da çalıştırdı. Galeri açıkken uygulama şunu bastı:

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
çalışma biçimi Koşu 7'dekiyle aynı kalıyor.

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

- **Küçük önizleme hâlâ dışarıda.** Koşu 7'den beri tasarım kararı bekliyor ve beklemeye devam
  ediyor. Bu koşu onu ikame etmiyor: tavan **kırılmayı** durdurur, önizleme **hızı** getirir. İkisi
  rakip değil, sıradaki iki ayrı iş.
- **Başarısız karede hover karartması** da Koşu 7'den devrolan tasarım işi olarak dışarıda.
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

Galeri karolarının küçük önizlemeleri ve başarısız karede hover karartması — ikisi de Koşu 7'den
devrediyor ve tasarım kararı bekliyor. Bir de bu koşuyu kapatacak Colab turundan çıkacak yeni
maddeler; çekişmenin gerçek mekanizması, tavan yetmezse, ilk sıradaki olur.
