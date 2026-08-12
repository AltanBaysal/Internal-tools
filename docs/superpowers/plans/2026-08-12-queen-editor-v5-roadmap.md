# Queen Editor — Yol Haritası v5

**Tarih:** 2026-08-12 · **Koşu dalı:** `feat/queen-editor-v3` ·
**Durum:** 33 görevin 33'ü yazıldı ve commit edildi (`a878d59`'a kadar); **kullanıcının elle Colab
turu bekliyor** — aşağıdaki *Koşunun sonu* bölümü.
**Yerini aldığı doküman:** [2026-08-08-queen-editor-v4-roadmap.md](2026-08-08-queen-editor-v4-roadmap.md)
— Madde 1-11 bitti ve push edildi; Madde 12 (Colab turu) yalnız yüzeysel koşuldu, o borç bu koşuya
devrolmaz — v5'in kendi doğrulaması kendi işini kapsar.
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
