# Queen Editor — Yol Haritası v4

**Tarih:** 2026-08-08 · **Branch:** `feat/queen-editor-v2` · **Durum:** **Madde 1-11 bitti ve push
edildi (2026-08-09); geriye yalnız Madde 12 — kullanıcının Colab turu — kaldı.** Kapanış anındaki
sayılar: arka uç **317** test, ön yüz **148** test, hepsi yeşil; `dist/` her maddede yeniden üretilip
aynı commit'te gitti. Maddelerin altındaki **Spec** satırları o maddenin kararlarının yazılı olduğu
yerdir.
**Yerini aldığı doküman:** [2026-08-08-queen-editor-v3-roadmap.md](2026-08-08-queen-editor-v3-roadmap.md)
— v3'ün Madde 1'i (tasarım) tamamlandı; Madde 2-6 tasarımdan **önce** yazıldığı için tasarımla sekiz
yerde çelişiyordu ve bu belgede yenilendi; Madde 7-9 aynen taşındı.
**Kaynak:** [tasarım v2 farkları](../research/2026-08-08-queen-editor-tasarim-v2-farklari.md) —
maddelerin içeriği oradaki bulgu kodlarıdır.

> **İsim çakışması.** Tasarım projesindeki **"Basit v2"**, repodaki bu **v4 yol haritasına** karşılık
> gelir. Belge boyunca ikisi tam adıyla anılır: **tasarım v2** ve **roadmap v4**.

**Kapsam sınırı (değişmedi):** video üretiminin kendisi kapsam dışı, sınır Export dosyası. Kapsam
dışı kalanlar: bağlantı çubuğu · foto sayısı / kapak · yeniden adlandırma · referans görsel ·
**Yeniden üret** (tasarımda var, yapılmayacak — fark belgesi 1. bölüm).

İlke aynı: her madde çıktı odaklı (**ne çalışır** + **nasıl görülür**) ve bir öncekinin üstüne
birikir. Değişen tek şey kapanma anı: bu koşuda maddeler **testleri yeşile boyayarak** kapanır,
Colab denemesi tek dalgada Madde 12'de yapılır (bkz. *Nasıl çalışacağız*).

---

## Nasıl çalışacağız

Her madde aynı dört adımdan geçer, madde bitmeden sonrakine geçilmez:

1. **Spec** — maddenin tasarım dokümanı (`docs/superpowers/specs/`). Fark belgesindeki kodlar burada
   davranışa açılır, maddenin açık soruları burada karara bağlanır.
2. **Plan** — uygulama planı (`docs/superpowers/plans/`), TDD adımlarıyla.
3. **TDD** — önce başarısız test, sonra kod. Arka uç `pytest` (sahte port'larla; ComfyUI yok, Drive
   yok), ön yüz `npm test` (vitest + jsdom; `fetch` ve saat sahte, gerçek saniye beklenmez).
4. **Kapanış** — `pytest` ve `npm test` yeşil; ön yüze dokunulduysa `npm run build` koşulur ve
   üretilen `dist/` **aynı commit'te** gider, yoksa Colab bayat arayüz sunar.

**Colab denemesi en sonda, toplu.** Kullanıcının zamanı sınırlı, o yüzden maddeler tek tek Colab'da
denenmez — hepsi Madde 12'de bir dalgada denenir. Bunun iki sonucu var:

- Bir maddenin "nasıl görülür" satırı, o maddenin **kabul kriteridir**, Colab'da yapılacak bir tur
  değil. Testler o satırı kanıtlamalı.
- Madde biter bitmez commit + push edilir; Colab repoyu klonladığı için push edilmemiş iş Colab'da
  görünmez ([FOUNDATION.md](../../../queen-editor/FOUNDATION.md), Karar 1). Bu koşuda commit için
  ayrıca kullanıcı onayı beklenmez.

## Kod kuralları

Kurallar burada tekrar yazılmaz, yerleri şunlar: ilkeler ve yığın kararları
[FOUNDATION.md](../../../queen-editor/FOUNDATION.md), katmanlar ve yapı
[CODE-STANDARD.md](../../../queen-editor/CODE-STANDARD.md). Bu koşuda en çok işe karışacak olanlar:

- **Bağımlılık yönü:** `presentation → domain ← data → services`. Yasaklar istisnasız:
  `feature ↛ feature`, `service ↛ feature`, `service ↛ service`. Somut sınıflar yalnız `main.py`'de
  bağlanır.
- **Kural arka uçta, ön yüz görüntüdür.** Tarayıcı durumu çizer ve girdi toplar; testin
  doğrulayacağı hiçbir kararı sahiplenmez. Yazarken gösterilen tahmin bir önizlemedir, kural değildir.
- **Gerçek diskte durur.** Süreç hafızası atılabilir; önemli olan her şey Drive'a dosya olarak yazılır
  ve uygulama yeniden başlayınca kendini o dosyalardan kurar. **Madde 1'i doğrudan ilgilendirir:** bir
  dosya başka bir dosyanın cevabını bayrak olarak tekrarlamaz — plan kare kare işaretlenmez, bir kare
  ancak foto kaydında satırı olduğunda bitmiştir. Hatalı kare de "dördüncü soruyu" cevaplıyorsa
  dördüncü dosyayı ister; spec'inde bu karar verilir.
- **Kullanıcının emeği kutsaldır.** Hiçbir senaryo bitmiş işi kaybetmez; yıkıcı her eylem açık ve
  onaylıdır. Yarım kalan iş yeniden başlatmadan sonra kaldığı yerden sürer.
- **Yeniden üretilebilirlik.** Her birim tek başına spec'inden yeniden yazılabilecek kadar basit ve
  sınırlı kalır; bağlamda rahat tutulamayacak kadar büyüyen dosya çok iş yapıyordur, bölünür.
- **`vendor/` elle düzenlenmez.** Tasarım projesinden birebir gelir; tek mekanik istisna dosyanın
  export satırıdır. Uygulamaya uymayan şey `shared/app.css`'te düzeltilir, `vendor/`'da değil.
- **Dil ayrımı:** yorum, docstring, **test adı** ve commit mesajı **İngilizce**; kullanıcının gördüğü
  arayüz metni **Türkçe**.

## Bu belge detay tutmaz

Her maddenin altında **kapsadığı bulgu kodları** yazılı. Kodun ne dediği fark belgesindedir; nasıl
yapılacağı maddenin kendi tasarım dokümanı ve planındadır. Yol haritası yalnız **hangi işin hangi
sırayla ve neyle birlikte yapılacağını** söyler.

Aynı kural sapmalar için de geçerli: fark belgesinin 7. bölümündeki "bugün zaten yanlış" maddeleri
ayrı bir madde değil — her biri **o ekranı zaten yeniden yapan maddenin** kabul kriteridir. Böylece
hiçbir ekran iki turda elden geçmez. Hangi sapmanın nereye gittiği maddelerin altında yazılı;
toplu görünüm için sondaki **kapsama tablosuna** bakılır.

## Çekirdek: kuyruk sürekli açık

Tasarım v2 tek bir karardan doğuyor: **üretim, "başlat / bitir"li tek seferlik bir iş olmaktan çıkıp
sürekli açık bir kuyruk oluyor.** v3 bu kararı zaten almıştı; tasarım onu ekranlara indirdi ve üç
yerde v3'ün varsaydığından farklı çıktı:

| v3 varsayıyordu | Tasarım v2 diyor ki |
|---|---|
| Tek panel | Panel üçe ayrılır, sağına ikon şeridi gelir |
| Duraklat / Devam / İptal **kalkar** | Kuyruk panelinde **kalır** — kuyruğu topluca durdurmanın yolu var |
| Yeni kare kuyruğun **sonunda**, galerinin altında | Yeni kare **en büyük numarayı** alır, galerinin **en üstünde** durur |

Bu üçünde tasarım kazanıyor: v3'ün kendi Madde 1'i "tasarım kaynak, repo uygulayıcı" diyor ve
tasarım v3'ten sonra yapıldı. Aynı gerekçeyle buton adı **Üretime ekle**, **seed alanı yok** ve
duraklatılmış kuyruk elle **Devam et** ister.

**Çelişki sanılan bir madde vardı, değilmiş.** v3 "silinen bekleyenin numarası boşta kalır" derken
*dosya numarasından* söz ediyor (`12_a.png` bir daha kullanılmaz); tasarım "silme sonrası yeniden
numaralanır, delik kalmaz" derken *galerideki rozetten*. İkisi ayrı numara, ikisi de doğru — rozet
bugün de dosya adından değil konumdan geliyor.

---

## Madde 1 — Kuyruk canlı olur (arka uç)

Zemin: kuyruk dondurulmuş liste olmaktan çıkar, üstüne yazılabilen bir sıra olur. Hatalı kare de
aynı turda kalıcı hâle gelir — kayıt bir kere açılsın diye.

- **Ne çalışır:** plana sonuna ekleme ve bekleyen kareyi çıkarma; döngü her turda plandan sıradaki
  bekleyeni alır; kuyruk boş değilse üretim kendiliğinden başlar, boşalınca kendiliğinden durur.
  Hatalı kare oturumun hafızasında değil, kuyrukla aynı yerde kalıcı olarak durur. Dosya numarası
  ayırma kuralı aynı — silinen bekleyenin dosya numarası geri kullanılmaz.
- **Nasıl görülür:** `pytest` yeşil ve üç cümle kanıtlanmış — üretim sürerken atılan ikinci parti
  kesinti olmadan arkaya diziliyor; sunucu yeniden başladıktan sonra da kuyruk uç noktası patlamış
  kareyi bildiriyor; silinen fotoğrafın karesi kuyruğa geri dönmüyor.
- **Yok:** arayüz dokunuşu — galeri Madde 5'te baştan yapılıyor, şimdi dokunmak onu iki kez elden
  geçirmek olur; kırmızı karenin ekranda kalıcılığı orada görünür hâle gelir. Ayrıca çalışan kareyi
  kesme kuralı (Madde 4) ve durma kuralı (Madde 8) burada değil.
- **Kodlar:** G12 · P4, P5 ve G3'ün zemini
- **Spec:** [Madde 1 — Canlı kuyruk](../specs/2026-08-08-queen-editor-v4-madde-1-canli-kuyruk-design.md)

## Madde 2 — Panel üçe ayrılır

Sağ sütunun iskeleti. İçlerini sonraki maddeler dolduruyor.

- **Ne çalışır:** panelin sağına dikey ikon şeridi gelir, üç panel arasında geçilir — form, kuyruk ve
  içi boş agent paneli; her panelin üstünde küçük başlık durur. Durum kartları formun altından kuyruk
  paneline **taşınır** — içerikleri Madde 4'te yeniden yazılacak, burada yalnız yer değiştirirler.
- **Nasıl görülür:** ikonlara basınca panel değişir, aktif ikon mor olur; ilerleme kartı artık formun
  altında değil kuyruk panelinde.
- **Yok:** kartların içeriğine dokunmak; agent panelinin içi (bilerek boş).
- **Kodlar:** P1, P2, P3, P28, P29

## Madde 3 — Üretime ekle formu

Form paneli tasarımın hâline geçer ve bir daha hiç kilitlenmez.

- **Ne çalışır:** **Üret** → **Üretime ekle**; üretim sürerken panel kilidi kalkar; "Ekleniyor…" ara
  durumu yalnız butonu tutar, alanlar açık kalır; yeşil "kuyruğa eklendi" kartı gelir ve kendiliğinden
  kaybolur; eklenemezse tek satır hata; prompt × varyant hesabı kalkar; format hatası tek satıra iner
  ve akan kuyruğu etkilemez; boş galeri metni yeni butonun adını anar.
- **Nasıl görülür:** üretim sürerken prompt yaz → Üretime ekle basılabilir; kareler kuyruğun sonunda
  belirir, çalışan kare kesilmez.
- **Yok:** model seçimi (Madde 10); kuyruk panelinin içeriği (Madde 4).
- **Kodlar:** P4-P11, P13, G9 · **sapma:** format hatasının fazlasını söylemesi
- **Korunur:** başka projede üretim sürerken butonun pasifleşmesi — tasarım bu kısıttan hiç söz
  etmiyor, kaldıran bir karar da yok.

## Madde 4 — Kuyruk paneli

Kuyruğun bütün hâlleri tek panelde.

- **Ne çalışır:** akıyor · duraklatılıyor · duraklatıldı · durdu · tamamlandı · boş. **Duraklat**,
  **Devam et** ve onay soran **Kuyruğu boşalt** burada. Sayaç paydayı bırakır ("N kare bekliyor"),
  ilerleme çubuğu ve "şimdi:" satırı kalkar, canlı nokta gelir, hatalı kare satırı tıklanınca galeriye
  götürür. Duraklat'a basınca çalışan kare kesilir ve kuyruğa geri döner (fark belgesi 8.1 kararı).
- **Nasıl görülür:** kuyruk akarken panelde tek büyük sayı; Duraklat → "Duraklatıldı"; Kuyruğu boşalt
  → onay → "Kuyruk boş", yeşil kart çıkmaz.
- **Yok:** hangi kuralla durulduğu ve hatanın kendisi (Madde 8).
- **Kodlar:** P14, P16-P25, P27 · **sapmalar:** yarım kalan koşunun kartının başka konuşması · hatalı
  kareyle biten koşuda yeşil kartın çıkmaması
- **Uyarlanır:** "Sunucuya ulaşılamıyor — son bilinen: 17/48" kartı bugün ilerleme çubuğuna
  dayanıyordu; çubuk kalktığı için metni yeni sayaç diline çevrilir.

## Madde 5 — Galeri tek dizi olur

Galerinin sırası kuralı: bir kare nereye konduysa orada kalır.

- **Ne çalışır:** dört kova (çalışan / hatalı / bekleyen / fotoğraf) kalkar; **her kare her zaman
  kendi sırasında durur** — durumu yalnız görünümünü değiştirir, yerini değil. Numara üretim
  sırasıdır: yeni kare en büyük numarayı alır ve en üstte durur, alttakilerin numarası hiç değişmez.
  Kare üretilince aynı yerde fotoğrafa dönüşür. Bekleyen ve çalışan karede de rozet (soluk tonda).
  Export sırası buna göre döner — en alttaki kare listenin ilki.
- **Nasıl görülür:** kuyruk akarken galeri hiç oynamaz; tek değişen, bir karenin kesikli kutudan
  fotoğrafa dönmesidir. Bir kare patlasın → kırmızı kare komşularının arasında kalır, öbeğe gitmez.
- **Yok:** seçim modu (Madde 6); detay sayfası (Madde 7).
- **Kodlar:** G1-G5, N2 · **sapma:** aynı hatalı karenin iki kez çizilmesi

## Madde 6 — Seçim modu ve yıkıcı eylem

Kuyruktan toplu çıkarmanın yolu ve uygulama geneli silme dili.

- **Ne çalışır:** bekleyen kareler de seçilebilir, üretilmişlerle aynı halkayı taşır; çalışan karede
  halka **hiç yoktur** ve "Tümünü seç" onu atlar; onay metni seçimin içeriğine göre değişir; seçim
  çubuğu galerinin altında yüzer ve seçim sıfırlanınca kaybolur; sürükleme basılı tut eşiğiyle başlar,
  bekleyen karta basılınca "üretilince sıralanabilir" ipucu çıkar. Yıkıcı eylem standardı uygulama
  geneline uygulanır — dolu kırmızı buton hiçbir yerde kalmaz.
- **Nasıl görülür:** bekleyen kareleri seç → "N kare kuyruktan çıkarılsın mı?" → çıkar, üretilmez,
  galerideki fotoğraflara dokunulmaz.
- **Kodlar:** G6, G7, G8, G11, N1 · **sapmalar:** seçim çubuğunun 0 seçiliyken durması · seçim
  çubuğunun yüzmemesi · sıralamanın basılı tutma eşiği olmadan başlaması
- **Spec:** [Madde 6 — Seçim modu](../specs/2026-08-08-queen-editor-v4-madde-6-secim-modu-design.md)

## Madde 7 — Bekleyen ve çalışan karenin detayı

Detay sayfası üç hâli de tanır.

- **Ne çalışır:** üretilmiş · bekleyen · çalışan; bekleyende kesikli "henüz üretilmedi" alanı,
  çalışanda dönen gösterge ve üretim bitince sayfa yenilenmeden fotoğrafa dönüş. Negatif kutusu gelir
  ve prompt ile alanı eşit paylaşır. Sıra sayacı ve oklar bekleyen + çalışan kareleri de gezer.
  Bekleyende buton **Kuyruktan çıkar** olur ve onay sormaz; çalışanda pasiftir. Bekleyende etiket
  "Dosya adı (planlanan)" olur.
- **Nasıl görülür:** bekleyen kareyi aç → prompt ve negatifini gör, kuyruktan çıkar; oklarla galeri
  sırası boyunca kesintisiz gez.
- **Yok:** seed alanı (tasarım hiçbir ekranda istemiyor); prompt düzenleme ve **Yeniden üret**
  (kapsam dışı).
- **Kodlar:** F1-F5
- **Spec:** [Madde 7 — Bekleyen kare detayı](../specs/2026-08-09-queen-editor-v4-madde-7-bekleyen-kare-detayi-design.md)

## Madde 8 — Durma kuralı ve hata

Ne zaman durulur, ne zaman devam edilir.

- **Ne çalışır:** ölümcül hatada **aynı iş otomatik 3 kez denenir**, olmazsa durulur; hata türüne göre
  ayrım yapılmaz. Tek karenin patlaması üretimi durdurmaz — kare kırmızı olur, sıradakiyle devam
  edilir. **Tekrar dene** akan kuyruğu kesmez, kareyi kuyruğun sonuna alır. Proje yeniden açıldığında
  kuyrukta iş varsa üretim kendiliğinden sürer; elle **Kaldığı yerden devam et** yalnız ölümcül
  hatadan ve duraklatmadan sonra istenir.
- **Nasıl görülür:** ComfyUI'ı öldür → üç deneme, sonra kırmızı "Üretim durdu" + sunucunun teknik
  satırı; düzelt → kuyruk kaldığı yerden akar. Bir kare patlasın → üretim sürer, kırmızı karede
  Tekrar dene basılabilir ve kare sonda yeniden üretilir.
- **Kodlar:** P26, G10 · **sapma:** üretim sürerken Tekrar dene'nin çalışmaması
- **Spec:** [Madde 8 — Durma kuralı](../specs/2026-08-09-queen-editor-v4-madde-8-durma-kurali-design.md)
  — "ölümcül"ün mekanik tanımı, denemeler arası beklemenin reddi ve proje açılınca otomatik devam
  orada karara bağlandı.

## Madde 9 — Projeler ekranı

Hiçbir maddenin uğramadığı tek ekran; sapmaları burada toplanıyor.

- **Ne çalışır:** geçersiz **veya boş** proje adında uyarı yazarken çıkar ve uyarı varken buton pasif
  kalır; sekizden çok projede ızgaranın sağında kaydırma çubuğu ve altta solma perdesi belirir; proje
  kartının silme butonu yıkıcı eylem standardına girer.
- **Nasıl görülür:** kutuyu boşalt → uyarı hemen çıkar, buton pasif; dokuzuncu projeyi ekle → liste
  kendi içinde kayar.
- **Kodlar:** N3, N4 · **sapmalar:** boş proje adında uyarı çıkmaması · uyarının yazarken değil
  basınca çıkması
- **Spec:** [Madde 9 — Projeler ekranı](../specs/2026-08-09-queen-editor-v4-madde-9-projeler-ekrani-design.md)
  — iki açık soru kullanıcı kararıyla kapandı: silme butonu **kırmızı çerçeveli çöp ikonu**, uzun
  listede **sayfa kayar** (ızgaranın kendi kaydırması yok, bu yüzden N3'te kod değişmedi).

## Madde 10 — Çoklu model

v3'ten devreden bağımsız en büyük iş; hiçbir madde buna bağımlı değil, istenirse öne çekilebilir.

- **Ne çalışır:** paneldeki model açılır listesi gerçek seçim yapar — birden fazla model kurulur,
  seçilen modelle üretilir, seçim projeyle kaydedilir. Model listesi yüklenemezse ayrı bir ekran
  değil, kuyruk panelindeki hata kalıbına girer.
- **Nasıl görülür:** modeli değiştir, üret → görünür şekilde farklı sonuç; projeyi yeniden aç →
  seçim durur.
- **Kodlar:** P12 · **sapma:** model alanının hiç olmaması
- **Spec:** [Madde 10 — Çoklu model](../specs/2026-08-09-queen-editor-v4-madde-10-coklu-model-design.md)
  — "hangi modeller kurulacak" sorusu uygulamadan çıktı: liste ComfyUI'ye sorulur, model eklemek
  notebook CONFIG'inde bir satırdır.

## Madde 11 — Üretim süresi ölçümü

v3'ten devreden küçük iş, bilerek sonda: hız kararlarının (T4 → L4 → A100, adım sayısı, FaceDetailer)
tahminle değil ölçümle verilmesi için.

- **Ne çalışır:** her kare için geçen süre ölçülür ve Colab hücre çıktısına satır satır basılır.
  Süre render'ın kendisini kapsar; Drive'a yazma ayrı sayılır ki "GPU ne kadar, boru hattı ne kadar"
  ayrımı görülebilsin.
- **Nasıl görülür:** üretim sürerken hücre her kare bittiğinde bir satır basar; GPU'yu değiştirip
  aynı grafı koşunca fark rakamla görünür.
- **Yok:** ortalama/özet paneli, grafik, GPU model tespiti.
- **Spec:** [Madde 11 — Üretim süresi](../specs/2026-08-09-queen-editor-v4-madde-11-uretim-suresi-design.md)
  — açık soru kapandı: süre **detay sayfasında görünmeyecek** (tasarımın yan sütununda süre alanı
  yok, seed alanının olmadığı gerekçenin aynısı).

## Madde 12 — Colab doğrulaması (toplu)

En sonda, tek dalgada.

- **Ne çalışır:** [doğrulama listesinden](2026-08-05-queen-editor-colab-dogrulama.md) devreden **G3**
  (üst üste hata → kırmızı "Üretim durdu" kartı + sunucunun teknik satırı — artık üç deneme kuralıyla),
  **G4** (tekil kare patlarsa kırmızı kare + Tekrar dene, üretim sürer), **H1-H2** (runtime ölünce
  bağlantı kartı, dönünce toparlanma); üstüne bu yol haritasının kendi listesi: çalışırken kuyruğa
  ekleme, galerinin hiç oynamaması, bekleyen kareyi seçip çıkarma, bekleyen kartın detayı, duraklat /
  devam / kuyruğu boşalt, hatalı karenin sayfa yenilendikten sonra da yerinde durması.
- **Nasıl görülür:** ComfyUI öldürülür → üç deneme sonra kart; runtime kapatılır → ~12 sn içinde
  bağlantı kartı; kuyruğa iş atılır, biri çıkarılır, sekme kapatılıp açılır → kuyruk kaldığı yerden
  akar ve galeri aynı sırada durur.
- **Yok:** v3'ün F2-F5 maddeleri yerine artık tasarımın duraklat/devam/boşalt akışı denenir.

**Deneme listesi (sırayla):**

| # | Ne yapılır | Beklenen |
|---|---|---|
| 1 | Proje aç, prompt yaz, **Üretime ekle** | Yeşil "N kare kuyruğa eklendi", kareler galerinin üstünde kesikli kutu olarak belirir |
| 2 | Üretim akarken **ikinci parti** at | Panel kilitlenmez, yeni kareler kuyruğun sonuna girer, çalışan kare kesilmez |
| 3 | Kuyruk akarken galeriye bak | Galeri hiç oynamaz; tek değişen, bir karenin kesikli kutudan fotoğrafa dönmesi |
| 4 | Bekleyen bir kareye tıkla | Detay açılır: kesikli "henüz üretilmedi", prompt + negatif, **Kuyruktan çıkar** (onay sormaz) |
| 5 | Çalışan kareyi detayda aç, bekle | Dönen gösterge fotoğrafa döner, **sayfa yenilenmeden** |
| 6 | Oklarla galeri boyunca gez | Sayaç rozetle aynı sayıyı yazar; `›` aşağı gider, uçlarda ok pasifleşir |
| 7 | Bekleyen kareleri seç → **Çıkar** | "N kare kuyruktan çıkarılsın mı?" — üretilmezler, fotoğraflara dokunulmaz |
| 8 | **Duraklat** → **Devam et** → **Kuyruğu boşalt** | Duraklat çalışan kareyi keser ve kare kuyruğa döner; boşalt onay ister, sonra "Kuyruk boş" |
| 9 | Modeli değiştir, üret *(ikinci model kuruluysa)* | Görünür şekilde farklı sonuç; projeyi kapatıp açınca seçim durur |
| 10 | ComfyUI'ı öldür (`pkill -f 'python main.py'`) | **Aynı kare** üç kez denenir, sonra kırmızı "Üretim durdu" + sunucunun teknik satırı; **kırmızı kare oluşmaz** |
| 11 | ComfyUI'ı geri başlat → **Kaldığı yerden devam et** | Kuyruk aynı kareden akar |
| 12 | Tek kare patlasın (bozuk prompt) | Üretim sürer, kare kırmızı kalır, **Tekrar dene** basılabilir ve kare **sonda** yeniden üretilir |
| 13 | Sayfayı yenile | Kırmızı kare yerinde durur, kuyruk kaldığı yerden akar |
| 14 | Colab runtime'ı kapat | ~12 sn içinde bağlantı kartı; runtime dönünce toparlanır |
| 15 | Sunucu hücresinin çıktısına bak | Her üretilen kare için `⏱ 3_a.png · render … sn · drive … sn` satırı |
| 16 | Projeler ekranında ad kutusuna geçersiz karakter yaz | Uyarı **yazarken** çıkar, **Oluştur** pasif kalır |

---

## Sıra özeti

| Madde | Görülür çıktı | Yeni kazanım |
|---|---|---|
| 1 · Kuyruk canlı olur | Çalışırken eklenen iş arkaya dizilir; hata sayfa yenilenince kalır | kuyruk ve hata kalıcı bir kayıt olur |
| 2 · Panel üçe ayrılır | İkon şeridi, üç panel | durum bilgisi formdan ayrılır |
| 3 · Üretime ekle formu | Üretim sürerken prompt eklenebilir | panel bir daha kilitlenmez |
| 4 · Kuyruk paneli | "N kare bekliyor" + duraklat / devam / boşalt | kuyruğun tek bir yönetim yeri |
| 5 · Galeri tek dizi olur | Galeri üretim akarken hiç oynamaz | kare nereye konduysa orada kalır |
| 6 · Seçim modu ve yıkıcı eylem | Bekleyen kareler toplu çıkarılır | tek silme dili, tek seçim modu |
| 7 · Bekleyen kare detayı | Kuyruktaki işin içi görünür | kuyruk incelenebilir hâle gelir |
| 8 · Durma kuralı ve hata | Bağlantı kesintisi kare harcamıyor | üç deneme aynı işe |
| 9 · Projeler ekranı | Boş adda uyarı, uzun listede kaydırma | son sapmalar kapanır |
| 10 · Çoklu model | Model seçimi | içerik çeşitliliği |
| 11 · Üretim süresi ölçümü | Colab log'unda saniye | hız kararları ölçümle verilir |
| 12 · Colab doğrulaması | Devreden G/H + kuyruğun kendi listesi | tek dalgada topluca kanıtlanır |

## Neden bu sıra

- **Arka uç önce (1):** kuyruk canlı olmadan "Üretime ekle" yalan olur — buton basılır ama iş arkaya
  dizilemez, bekleyen kare de sırasında yer ayıramaz. Hatalı karenin kalıcılığı da aynı kayda
  dokunduğu için buraya alındı; Madde 5'in "kare yerinde durur" iddiası ancak hata sayfa yenilenince
  kaybolmayınca kanıtlanabilir.
- **İskelet içerikten önce (2 → 3, 4):** form ve kuyruk paneli, Madde 2'nin açtığı panellerin içinde
  yaşıyor. Durum kartlarının taşınması ile yeniden yazılması bilerek ayrıldı: taşıma mekanik bir iş,
  ikisi birleşirse Madde 2 şişer.
- **Galeri panelden sonra (5):** Madde 5'in asıl iddiası "sıra hiç oynamaz" ve bu ancak **akan
  kuyruğa ikinci parti atarak** test edilir — o da Madde 3'ü gerektirir.
- **Seçim ve detay galeriden sonra (6, 7):** ikisi de galerinin tek diziye inmiş hâlini varsayıyor.
- **Hata sonda (8):** durma kuralının nerede duracağı, ancak kuyruk sürekli akar hâle geldikten sonra
  doğru kurulur.
- **Projeler ekranı bağımsız (9):** hiçbir madde oraya uğramıyor, sıranın herhangi bir yerine
  alınabilir.
- **Çoklu model ve süre sonda (10, 11):** bağımsızlar; süre ölçümü asıl işini doğrulama turunda
  yapar.
- **Doğrulama en sonda (12):** iki sebep. Kullanıcının Colab'da harcayacak sınırlı zamanı var, o
  yüzden tek dalga; ayrıca kuyruk davranışı yolun ortasında değiştiği için erken bir tur zaten iki
  kere yapılırdı.

## Kapsama tablosu

Fark belgesindeki her kod bir maddede karşılığını buluyor. Kapsam dışı ve karara bağlanmış olanlar
da burada — bir dahaki karşılaştırmada "atlanmış" sanılmasınlar.

| Kaynak | Kodlar | Madde |
|---|---|---|
| Panel | P1, P2, P3, P28, P29 | 2 |
| Panel | P4-P11, P13 | 3 |
| Panel | P12 | 10 |
| Panel | P14, P16-P25, P27 | 4 |
| Panel | P26 | 8 |
| Panel | ~~P15~~ | karara bağlandı — bugünkü davranış kalıyor, Madde 4'ün içinde |
| Galeri | G1-G5 | 5 |
| Galeri | G6, G7, G8, G11 | 6 |
| Galeri | G9 | 3 |
| Galeri | G10 | 8 |
| Galeri | G12 | 1 |
| Foto detay | F1-F5 | 7 |
| Foto detay | ~~F6-F10~~ | **kapsam dışı** — Yeniden üret yapılmayacak |
| Genel | N1 | 6 |
| Genel | N2 | 5 |
| Genel | N3, N4 | 9 |
| Genel | N5 | çelişki kapandı — çizim ve bugünkü uygulama aynı, yapılacak iş yok |
| Sapma (7. bölüm) | format hatası | 3 |
| Sapma | yarım kalan koşunun kartı · hatalı bitişte yeşil kart | 4 |
| Sapma | aynı hatalı karenin iki kez çizilmesi | 5 |
| Sapma | seçim çubuğu 0'da duruyor · çubuk yüzmüyor · sürükleme eşiği | 6 |
| Sapma | üretim sürerken Tekrar dene | 8 |
| Sapma | boş proje adı uyarısı · uyarının zamanlaması | 9 |
| Sapma | model alanı hiç yok | 10 |
| Sapma | duraklatılmış hâlde panel kilitli kalmıyor | düştü — panel artık hiç kilitlenmiyor (P5) |
| Sapma | ~~varyant üst sınırı~~ | kapandı — 26 doğru sayı |

**Öksüz davranışlar korunur.** Fark belgesinin 6. bölümündeki on davranış (projeler arası tek işçi
kısıtı, bağlantı kartı, "Tümünü seç"in ikinci basışı, sıra kaydedilemedi uyarısı, yükleme
göstergeleri, "Fotoğraf bulunamadı" kartı…) tasarımda karşılığı olmadığı için değil, tasarım onlardan
hiç söz etmediği için listelenmişti. Kaldıran bir karar yok; hepsi kalır. Bir maddenin planı bunlardan
biriyle çakışırsa kararı orada verir — Madde 4'ün bağlantı kartı metnini yeni sayaç diline çevirmesi
gibi.

## Açık sorular — hepsi kapandı

| Soru | Karar | Nerede |
|---|---|---|
| Varyant kutusunun davranışı (Madde 3) | Geçersiz değer kutuya **hiç girilemez**; boş bırakılan kutu odak kaybında **1'e döner**. Üst sınır 26. | Madde 3 |
| Proje kartının silme butonu (8.4) | **Kırmızı çerçeve + kırmızı çöp ikonu**, yazısız — *kullanıcı kararı* | Madde 9 |
| Uzun proje listesi (8.7) | **Sayfa kayar**, ızgaranın kendi kaydırma alanı yok — *kullanıcı kararı*; bugünkü davranış, kod değişmedi | Madde 9 |
| Üretim süresi detayda görünsün mü | **Hayır** — tasarımın yan sütununda süre alanı yok | Madde 11 |
| Hangi modeller kurulacak | Uygulamanın sorusu değil: liste ComfyUI'ye sorulur, kurulacaklar notebook CONFIG'inde | Madde 10 |

## Sıradaki adım

**Madde 12 — Colab doğrulaması, kullanıcı koşar.** Kod tarafı bitti: Madde 1-11 uygulandı, testler
yeşil, `dist/` güncel ve her şey `feat/queen-editor-v2` dalına push edildi. Notebook artık bu dalı
klonluyor (önce `feat/queen-editor-v1`'i klonluyordu, yani bir Colab turu eski kodu denerdi).

Denemeden önce **iki elle yapılacak iş** var:
- **İkinci bir model kur** ki model seçimi görünür şekilde denenebilsin: `app.ipynb`'nin model
  hücresindeki `CIVITAI_MODELS` (ya da `OPEN_MODELS`) listesine bir satır eklemek yeter. Tek modelle
  de her şey çalışır, yalnız "modeli değiştir → farklı sonuç" adımı denenemez.
- Colab **Secrets**'ta `GITHUB_TOKEN` ve `CIVITAI_COOKIE` güncel olmalı (cookie ~30 günde bir ölür).
