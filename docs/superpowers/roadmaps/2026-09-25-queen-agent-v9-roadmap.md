# QueenAgent — Yol Haritası v9

**Tarih:** 2026-09-25 · **Koşu dalı:** `feat/queenagent-v9` · **Durum:** 35/48
**Öncesi:** [v8](2026-09-06-queen-agent-v8-roadmap.md) — kapandı ve `356d605` ile main'e alındı.
**Öteki araca dokunan madde:** 377 — queen-editor'ün roadmap bağlantılarını denetleyen testi.
**Kaynak:** v9-1 ve v9-2 kullanıcının 25 Eylül'deki sözlerinden doğdu. v9-3 ve v9-4
[BACKLOG.md](../../../queen-agent/BACKLOG.md)'den geliyor, backlog'un dört maddesi de v9-2'ye katıldı;
hepsini kullanıcı 28 Eylül'de getirdi. v9-6 kullanıcının 28 Eylül'deki sözlerinden doğdu. **v9-5 boş:**
sürüm maddesiydi, hizalanırken v9-2'ye katıldı *(kullanıcı, 28 Eylül)*, ve numarası kaymadı. v9-7
de kullanıcının 28 Eylül'deki sözlerinden doğdu; yazdığı listeyi queen-editor'ün
[v8-3](2026-09-25-queen-editor-v8-roadmap.md)'ü okur. v9-8 ve v9-9 da 28 Eylül'deki sözlerinden
doğdu. v9-10 ve v9-11 kullanıcının 29 Eylül'deki sözlerinden doğdu. **v9-7b 29 Eylül'de kalktı:** H3 prompt'unu
artık queen-editor yazıyor *(v9-7'nin kararları)*, ve numarası kaymadı. **v9-2 29 Eylül'de v9-2a – v9-2w
olarak bölündü**, tasarımcının `queen-agent-v3` dalından; v9-1d aynı gün oradan doğdu *(v9-2'nin
kararları)*. v9-12 aynı gün Claude'un önerisinden doğdu, ve kullanıcı kabul etti.

**Bu numarayla yazılan ilk belge koşulmadan kapandı** *(`81cf9d53`)*: maddeleri backlog'a döndü.
Playwright 28 Eylül'de v9-3 olarak geri geldi; ötekiler aynı gün backlog'dan da çıkarıldı
*(kullanıcı — "gerek kalmadı bunlara")*. DeepSeek'i OpenRouter'dan geçiren maddesi kullanıcı
istemediği için hiçbir yerde; dalı da 28 Eylül'de silindi, ve `feat/queenagent-v9` bu belge için
main'den yeniden açıldı *(kullanıcı — "Eski dal silinsin, yerelde ve GitHub'da")*.

**Maddeler parçalara bölündü, ve koşulacak sıra aşağıdaki dalgaların sırası** *(kullanıcı, 28 Eylül —
"küçük bir ai agentın kolay yapıilceği bölümediyse böl ve depdnecy yada işlerin alaksına göre
yeniden roadmp akışını sırala")*. Her parça tek başına yapılıp test ediliyor; hizalamada konuşulan
kararlar tablonun altında, maddenin kendi başlığında duruyor.

**29 Eylül'de parçalar paralel dalgalara dizildi** *(kullanıcı — "roadmpi olabildice küçük ve paralele
çalışabilir maddelr bölmeni sityorum nedeni şu her madde bir sub agetn taragından koşulacak sen ise
çıktılarını kontrol ediceksin ajanların")*. Bir dalganın parçaları aynı anda koşar, ve dalga öncekiler
birleşince başlar; her dalganın başında parçaların neyin üstüne kurulduğu yazılı. Aynı dalgadakiler
aynı yere dokunmaz — aynı dosyanın ayrı yerlerine dokunabilirler, ve birleştirmeyi Claude yapar.

- **v9-3 en başta, tek tek** *(kullanıcı — "en başa al şimdi")*: sonraki parçalar tarayıcıda kontrol
  edilir.
- **Dalga 1 – 6:** tasarımın parçaları, sunucunun onlara gereken işleri, ve v9-12.
- **Prompt'a dokunan parçalar dalgalardan sonra, tek tek** *(kullanıcı, 29 Eylül — "bu prompt relate
  değişsikleri en sona al abi ben görmek istiyorum çünkü değişikleri")*: v9-7a, v9-8a, v9-9, v9-11,
  v9-8b – v9-8f. Hepsi modele giden aynı metne yazıyor, o yüzden aynı anda koşamaz. v9-9 ve v9-11
  v9-8a'nın hemen arkasında: ikisi de Start a scenario'nun sahneleri yazan adımına dokunuyor, ve
  metnin kelime tavanı v9-8a'da yükseliyor.
- **v9-6 sona doğru** *(kullanıcı — "listenin en sonuna al bunu")*, **v9-10 en sonda** *(kullanıcı, 29
  Eylül — "bunu en son al beraber yaoarız")*.

**Koşu: her parçayı bir subagent koşar, Claude yönetir** *(kullanıcı, 29 Eylül — yukarıdaki söz, ve
"bir sıkıntı varsa senin çözemeyeceğin bana raise etmelisni")*.

- **Her parça bir Opus subagent'ı** *(kullanıcı — "opsu çünkü kodlama yapıyoruz o tasarım içindi")*,
  kendi worktree'sinde, dalın ucundan başlar. Adımları CLAUDE.md'deki gibi, superpowers skill'leriyle.
- **Kırmızı tur:** subagent test spec'ini, planı ve testleri yazar, dört test satırını kendisi koşar,
  yeni testlerin kırmızı olduğunu görür ve kendi dalında commit'ler. İşi bitip emin olunca Claude'a
  getirir, ve en son Claude bakar *(kullanıcı — "yok onlar koşsju n kendielr işi bitirdiğinde emin
  olup sana raise etsin sen en son kontreol et olur mu")*.
- **Yeşil tur:** aynı subagent implementasyonu yazar, suite'i yeşile getirir, ve olabildiğince kendisi
  kontrol eder — tasarımın belgeleri, FOUNDATION.md ve CODE-STANDARD.md, kendi değişikliği; sonra
  commit'ler. **Playwright subagent'ta değil** *(kullanıcı — "yine agent baksın olabidliğince
  playwrightı sanırım agentlar kullanırsa sıkınt oluyor ama diğer şeyler için düşün")*: tarayıcı tek,
  orada Claude bakar.
- **Claude en son bakar, ve yalnız çalışıyor mu diye değil:** kod FOUNDATION.md'ye ve
  CODE-STANDARD.md'ye uyuyor mu, ve sürdürülebilir mi *(kullanıcı — "bir ana agent olarak senin işin
  sadece yazılan kod çalışıyorm u bakmak değil aynı zamanda architetural 2 tane dokumanımız var onlar
  uygun yazılmış mı diye kontrol etmek ve bu kod usürdürüelbilir mi diye sormayıda içeriyor")*.
  Yanlışsa aynı subagent'a geri yazar; doğruysa birleştirir ve parçayı işaretler. Claude'un
  çözemediği kullanıcıya gelir.
- **v9-3 Claude'un, subagent'sız:** v9-3a'nın ayarı yazılınca kullanıcı Claude Code'u yeniden açar, ve
  subagent'lar ondan sonra başlar *(kullanıcı, 29 Eylül — "ilk taskı subagetn olmadan sen yap sonra
  baştan açıp kapatayım sonra subagetna geçeriz olur mu")*. v9-3b de Claude'un, çünkü tarayıcı
  Claude'da.

**Numaralar koşu açılırken verildi: 334–376**, 29 Eylül'de, tablonun sırasıyla; sayaçta en yüksek
numara Queen Editor v7'nin 333'üydü. Belge yazılırken maddeler `v9-N` diye kendi numaralarını
taşıyordu, ve metin parçaları hâlâ o adlarla anıyor; o yüzden tabloda ikisi yan yana duruyor.
**377 koşu sırasında çıktı**, aynı gün: 334'ün testleri koşarken queen-editor'ün süitinde koşudan önceki
bir kırmızı bulundu, ve kullanıcı onu subagent'lara verdi: Dalga 1'de koşar. **378 de aynı gün çıktı:**
334'ün tarayıcısı ilk açıldığında kullanıcı onun güvenli kullanılmasını istedi; Dalga 0'da 335'ten önce,
Claude yapar. **379 dalga 1'de çıktı:** 340'ın subagent'ı CODE-STANDARD'da koşudan önce de yanlış olan bir
cümle buldu; Dalga 2'de bir subagent'ın. **380 dalga 2'de çıktı:** 349 tarayıcıda denenirken hata kartı
yazma kutusunun altında yarım kaldı; Dalga 3'te bir subagent'ın. **381 dalga 3'te çıktı:** 356 tarayıcıda
denenirken panelin kenarını çekmek sayfanın yazısını seçti; Dalga 4'te bir subagent'ın.

**Queen Editor'ün v8-3'ü önce biter:** v9-7a'nın çıkardığı listeyi bugünkü kutu okuyamaz, o yüzden v9
main'e v8'den önce alınmaz.

**Kullanıcıdan gerekenler, koşudan önce:** v9-3a'nın ayarı yazılınca Claude Code'un yeniden açılması.
**Koşu sırasında:** 378'in ayarı yazılınca Claude Code'un bir kez daha yeniden açılması; v9-10'a gelince
koşu durur, ve madde kullanıcıyla birlikte yapılır.

---

### Dalga 0 — tek tek

| # | İş | Bitti sayılır |
|---|---|---|
| 334 · v9-3a | ✅ **Playwright MCP bu depoda ayarlanır.** queen-design'daki gibi: ayar depoda durur, sürüm sabittir, tarayıcı arka planda açılır; cihazda nasıl kurulu olduğu koşuda bulunur. **Kullanıcıdan gereken:** ayar yazılınca Claude Code'un yeniden açılması. *Kararları: v9-3.* | Claude Code yeniden açılınca bu depoda Playwright araçları görünüyor, ve Claude bir sayfayı açıp ekran görüntüsünü alabiliyor. |
| 378 | ✅ **Playwright MCP güvenli kullanılır.** Tarayıcı normal internete karışmaz: yalnız bu bilgisayarda çalışan araçları ve onların fontlarını — Google Fonts — açar. Kodu tarayıcının dışında, bilgisayarda çalıştıran araç yasak, ve Playwright'ın yazdıkları git'e girmez. Kurallar CLAUDE.md'de. queen-design'daki kurallardan öğrenilir. *(Kullanıcı, 29 Eylül — "mcp yi günveli bir şekilde kullanmamız lazım  bu nednele queen desingdan öğren bunu normal internete karışmaması lazı mynai bir araştır ona göre claude mdyi de güncelle"; fontlar olmadan ekranlar yedek fontla çıkacağı için Google Fonts'a — "izin verilsin".)* **Claude'un, subagent'sız:** tarayıcı Claude'da. **Kullanıcıdan gereken:** ayar yazılınca Claude Code'un yeniden açılması. | Claude Code yeniden açılınca tarayıcı bir internet adresini açamıyor, ama yerel QueenAgent'ı fontlarıyla açıyor; `browser_run_code_unsafe` çağrılamıyor; `git status` Playwright'ın dosyalarını göstermiyor. |
| 335 · v9-3b | ✅ **QueenAgent Playwright ile kontrol edilir.** Claude bu bilgisayarda yerel çalışan QueenAgent'ı açar ve kullanıcının yerine kullanır; gerçek AI çağrısı yapılabilir. Önünde bir engel çıkmazsa düzenleme yapılmadan kapanır. *Kararları: v9-3.* **29 Eylül'de sahte anahtarla koştu** *(kullanıcı — "abi dummy apı key kullan lütfen apı keye ihtiyacın yok")*: proje açıldı, *Start a scenario* seçildi, mesaj gitti, ve DeepSeek'in 401'i ekranda hata kartı olarak göründü. Düzenleme gerekmedi. | Claude yerel QueenAgent'ı Playwright ile açıp bir skill'i baştan sona çalıştırabiliyor ve sonucu ekranda görüyor. |

### Dalga 1 — v9-3'ten sonra, aynı anda

Hepsi bugünkü kodun üstüne kurulur.

| # | İş | Bitti sayılır |
|---|---|---|
| 336 · v9-4a | ✅ **Yalnız Queen Flash kalır**, DeepSeek'in bugünkü adıyla — `deepseek-flash`; Pro kalkar. *Kararları: v9-4.* | Cevaplar `deepseek-flash`'tan geliyor; *Queen Pro* hiçbir yerde seçilemiyor. |
| 337 · v9-1a | ✅ **Tavan ve gösterge yalnız sohbetin mesajlarını ölçer**, ve tavan 50.000 kalır. Açılan dosyalar kutusu da sayılmaz. *Kararları: v9-1.* | Gösterge yalnız sohbetin mesajlarını çiziyor: çok araç çağıran bir tur ya da büyük bir dosya açmak onu büyütmüyor. Sohbet, mesajları 50.000'e ulaşınca yeni tur almıyor. |
| 338 · v9-2a | ✅ **Üst çubuk.** Pencerenin üstünde, her ekranda aynı yerde ve aynı boyda bir çubuk. Solda `QueenAgent` ve sürümü tek satırda: sürüm adla aynı boyda ve aynı kalınlıkta, kalın değil. Bir proje açıkken ortada yalnız projenin adı. Sağda ekrandan çıkış düğmesi: sohbette `Exit project`, uygulamanın açılışına döner. Kenar çubuğundaki marka kalkar; katlama düğmesi v9-2w'ye kadar kenar çubuğunun başında kalır. Listede (6). *Kararları: v9-2; tasarım: 150, 159, 161, 166.* | Her ekranın üstünde çubuk: solda `QueenAgent` ile sürümü aynı boyda ve kalınlıkta, sohbette ortada projenin adı, sağda `Exit project`; basınca açılışa dönülüyor. Kenar çubuğunda marka yok. |
| 339 · v9-2b | ✅ **Proje sabitlenir ve arşivlenir — sunucu.** Bir proje sabitlenip bırakılabilir, arşive alınıp geri getirilebilir; proje listesi her projenin sabitli ve arşivde olup olmadığını söyler. Ekrana dokunmaz: menüsü v9-2q'da, arşivi v9-2t'de. **Mimari:** CODE-STANDARD'a göre `project.json` yalnız projenin adını ve ne zamandan beri olduğunu cevaplar; sabitlemek ve arşivlemek başka bir soru, ve başka bir anda yazılır. Spec bunu o kurala göre çözer, ve yeni bir dosya gelirse CODE-STANDARD'ın tablosu aynı parçada güncellenir. *Kararları: v9-2; tasarım: 135, 167.* | Sunucu bir projeyi sabitliyor, bırakıyor, arşive alıyor ve geri getiriyor; liste ikisini de söylüyor, ve uygulama yeniden açılınca kalıyor. |
| 340 · v9-2c | ✅ **Yüklenirken spinner, önce dosya listesinde.** Parlayan iskeletin yerine küçük bir dönen halka gelir. Başlık ve düğmeler yerinde durur, yalnız yüklenen kısmın yerinde spinner döner. Bu parça spinner'ı kurar ve dosya listesine koyar; sohbetin açılışı v9-2l'de, All projects ve ad sorma ekranı v9-2u'da. *Kararları: v9-2; tasarım: 173, 181.* | Dosya listesi yüklenirken spinner dönüyor; listede parlayan iskelet yok. |
| 341 · v9-2g | ✅ **Yanıp sönen kare kalkar.** Cevap gelirken yazının sonunda kare çizilmez; süren satırdaki `Pondering…` gibi kelimeler yeter. *Kararları: v9-2; tasarım: 156.* | Cevap gelirken yazının sonunda kare yok. |
| 342 · v9-2h | ✅ **Açık dosyanın başlığı.** Üst satırda solda çerçeveli bir `←`, sağda yazılı `Refresh` ve `Copy`; üçü aynı boyda. Dosyanın adı altında kendi satırında, kesilmeden, ve içerikten bir çizgiyle ayrı. Download kalkar. `Copy` basınca `Copied` ya da `Could not copy` der, sonra geri döner. `←` satırın ortasında durur *(tasarımın APP-BUGS.md'si, 48)*. *Kararları: v9-2; tasarım: 154, 155, 176, 186.* | Açık dosyada üst satırda `←` solda, `Refresh` ve `Copy` sağda, aynı boyda; ad altında tam; Download yok. |
| 343 · v9-2i | ✅ **Çemberin sözü, ve dolmanın önceden duyurusu.** Çemberin ipucu `This chat is N% full`. Sohbet dörtte beşe, 40.000'e gelince çemberin yanında `N% full` yazar. Ölçü v9-1a'nın: yalnız mesajlar. Listede (5). *Kararları: v9-1 ve v9-2; tasarım: 146, 182.* | Çemberin üstüne gelince `This chat is N% full`; %80'i geçmiş sohbette çemberin yanında `N% full` yazıyor. |
| 344 · v9-12 | ✅ **ChatScreen.jsx bölünür.** Mesajı çizen bileşenler kendi dosyalarına taşınır; ekran ve davranış değişmez. *(Claude önerdi, 29 Eylül — FOUNDATION'ın 4. ilkesi: "A file too big to hold comfortably in context is doing too much — split it"; v9'un dokuz parçası bu dosyaya dokunuyor. Kullanıcı — "Evet, v9-12 olarak eklensin".)* | Ekran önceki gibi, ve testler yeşil; ChatScreen.jsx'te ekranın kendisi kalıyor, mesajın parçaları kendi dosyalarında. |
| 377 | ✅ **Roadmap'lerin bağlantı testi internet adresini dosya saymaz.** queen-editor'ün `test_a_roadmap_can_still_reach_everything_it_links_to`'su bir roadmap'in `.md` ile biten her bağlantısını diskte arıyor. v9'un iki MiniMax rehberi internet adresi, ve süit 28 Eylül'den beri kırmızı *(`d9c2d6f5`)*. Test `https://` gibi bir adresi dosya saymaz; diskteki bağlantıları denetlemeye devam eder. **queen-editor'ün koduna dokunur.** *(Kullanıcı, 29 Eylül — Claude'un seçeneğini seçti: "Yeni madde 377 olarak açılır … Test, https:// gibi adresleri dosya saymaz. queen-editor'ün koduna dokunduğu için roadmap'in başında öteki araca dokunan madde olarak yazılır."; sonra: "abi şimdi yapmıyorsun açıyorsun ve bekliyorsun bunuda suba agetnlar yapıcak roadmpe ekle aç ve bekle yani".)* **Kırmızı turu yazıldı** *(`11029a5d`)*: iki kırmızı — yeni iddia ve eskisi. Yeşil turu bir subagent'ın. | queen-editor'ün arka uç süiti yeşil; bir roadmap'teki kırık bir yerel bağlantı yine kırmızı veriyor. |

### Dalga 2 — dalga 1 birleşince

v9-1b v9-1a'nın; v9-2j v9-2b'nin; v9-2d, v9-2e ve v9-2f v9-12'nin; v9-2m v9-2c'nin; v9-2w v9-2a'nın
üstüne kurulur.

| # | İş | Bitti sayılır |
|---|---|---|
| 345 · v9-1b | ✅ **Sohbet baştan kırpılabilir.** En eski mesajlar, sohbet 10.000'e inene kadar modele gitmez ama ekranda kalır; özet yok. Kırpmadan sonra çember, modele hâlâ gideni okur *(29 Eylül)*. *Kararları: v9-1.* | Kırpılmış bir sohbette modele yalnız son 10.000 gidiyor, bütün mesajlar ekranda duruyor, ve sohbet yeniden tur alıyor. Sohbetin ölçüsü yalnız modele gidenleri sayıyor. |
| 346 · v9-2j | ✅ **Projenin son kullanıldığı an, ve listenin sırası — sunucu.** Proje listesi her projenin en son ne zaman kullanıldığını söyler, ve önce sabitlenenler, sonra son kullanılanlar sırasıyla gelir. All projects satırda `2h ago` gibi yazar *(v9-2n)*. **Mimari:** an saklanmaz, sohbetlerden okunur — CODE-STANDARD'a göre hiçbir dosya ötekinin cevabını tekrarlamaz; sıra bir kural, o yüzden sunucunun *(FOUNDATION, Karar 4)*. *Kararları: v9-2; tasarım: 135, 167.* | Sunucunun proje listesi her projenin son kullanıldığı anı veriyor, sabitlenenler önde, sonra en son kullanılan; bir projede sohbet edilince o an yenileniyor. |
| 347 · v9-2d | ✅ **Sohbet başlığında yalnız sohbetin adı.** `← proje /` kalkar; projenin adı üst çubukta *(v9-2a)*. *Kararları: v9-2; tasarım: 152, 168.* | Sohbet açıkken başlıkta yalnız sohbetin adı var; `←` ve projenin adı yok. |
| 348 · v9-2e | ✅ **Mesajın altındaki notlar tek satırda.** Kullanıcının mesajının altında saat, sürüm okları ve ✎ aynı satırda, saat önde. Süren cevabın satırı da saatle başlar. Listede (4). *Kararları: v9-2; tasarım: 139.* | Düzenlenmiş bir sorunun altında saat, `‹ 1/2 ›` ve ✎ tek satırda; süren cevabın satırı saatle başlıyor. |
| 349 · v9-2f | ✅ **Sunucunun reddi de hata kartı.** Sunucu bir mesajı reddedince kırmızı satır yerine, cevap gelmeyince çıkan kahverengi kart çıkar: `Couldn't get a response.`, altında sunucunun kendi yazısı, ve `Try again`. *Kararları: v9-2; tasarım: 193.* | Reddedilen mesajda kahverengi kart, sunucunun yazısı ve `Try again` var; kırmızı ret satırı yok. |
| 350 · v9-2m | ✅ **Dosya listesinde yazılı Refresh, başlığın satırında.** `↻` yazılı `Refresh` olur, listenin kutusundan çıkıp `PROJECT FILES 5 ›` başlığının sağına geçer; kutu ilk dosyayla başlar. Panel katlanınca `Refresh` görünmez. *Kararları: v9-2; tasarım: 154, 175.* | Yan panelin başlık satırında solda `PROJECT FILES 5 ›`, sağda `Refresh`; kutunun ilk satırı ilk dosya. |
| 351 · v9-2w | ✅ **Kenar çubuğunu katlama.** Katlama düğmesi bir panel ikonu olur, ve kenar çubuğunun en altında, sağda durur. Katlanınca kenar çubuğu dar bir ikon sütununa iner: `+` yeni sohbet, ve en altta aynı panel ikonu; arama ikonu v9-2v'de gelir. `Ctrl + .` her yerde açıp kapar. *Kararları: v9-2; tasarım: 174, 187.* | Panel ikonu kenar çubuğunun sağ altında; basınca ya da `Ctrl + .` ile ikon sütunu kalıyor, yeniden basınca açılıyor. |
| 379 | ✅ **CODE-STANDARD'ın hareket paragrafı yalnız bugünü anlatır.** CODE-STANDARD.md, `shared/app.css`'in iki keyframe'in sahibi olduğunu, üçüncü bir animasyonun icat edilmediğini, ve fade olmayan tek hareketin rail'in genişliği olduğunu söylüyor. Bugün üçü de yanlış: `msg-spin` `workspace.css`'te duruyor ve canlı satırın, dosya listesinin ve 355'ten beri açılan sohbetin spinner'ını döndürüyor; 351'den beri kenar çubuğu da genişliğiyle katlanıyor. *(340'ın subagent'ı buldu, 29 Eylül.)* **Kod değişmez; paragraf bugünkü animasyonları, nerede durduklarını ve neyin hareket ettiğini söyler.** "Üçüncü animasyon icat edilmez" kuralı kalkar *(kullanıcı, 29 Eylül — "Kural kalksın, paragraf yalnız bugünkü durumu anlatsın.")*. Aynı parçada `workspace.css`'teki `.rail__head--still` yorumu düzelir: sınıfı artık dosya okunurken değil, dar ekranda katlanan panel kullanıyor *(350'nin subagent'ı buldu)*. | CODE-STANDARD'ın o paragrafı bugünkü animasyonları, nerede durduklarını ve neyin hareket ettiğini doğru söylüyor, ve bir yasak koymuyor; `.rail__head--still`'in yorumu sınıfın bugün nerede kullanıldığını söylüyor. |

### Dalga 3 — dalga 2 birleşince

v9-1c v9-1b'nin; v9-2n v9-2a, v9-2b ve v9-2j'nin; v9-2k v9-2e'nin; v9-2l v9-2c ile v9-2d'nin; v9-2o
v9-2m'nin üstüne kurulur.

| # | İş | Bitti sayılır |
|---|---|---|
| 352 · v9-1c | ✅ **Dolan sohbette *burada devam et*.** Sohbet dolar dolmaz, mesaj reddedilmeden, yazma kutusunun yerinde bir bildirim: `This chat is full.`, dolu çember, `New chat` ve `Continue here`. `Continue here` onay istemez ve geri alınmaz: v9-1b'nin kırpmasını yapar, ve sohbet yeniden mesaj alır. Kırpılmış sohbet yeniden dolunca bildirim yine çıkar *(29 Eylül)*. **Mimari:** sohbetin dolu olduğunu sunucu söyler, ekran hesaplamaz *(FOUNDATION, Karar 4)*. Listede (5). *Kararları: v9-1; tasarım: 140, 182.* | Dolu sohbette yazma kutusunun yerinde bildirim ve iki düğme; `New chat` yeni sohbet açıyor; `Continue here`'den sonra en eski mesajlar modele gitmiyor ama ekranda duruyor, ve sohbet yeniden mesaj alıyor. |
| 353 · v9-2n | ✅ **All projects ekranı.** Uygulama bu ekranla açılır, ve ekranda kenar çubuğu yok. Başlık `All projects` ve `+ New project`; altında önce sabitlenenler (`PINNED`), sonra son kullanılanlar (`RECENT`). Her satırda projenin adı, `N chats · N files` ve son kullanıldığı an. Satıra basınca projenin son sohbeti açılır, sohbeti yoksa boş sohbeti. Proje yoksa ekran `No projects yet.` der. Proje ekranı, "No projects yet" ekranı ve parlayan iskeletin son iki yeri kalkar. **Sohbet silme de kalkar**, tek yeri proje ekranıydı *(29 Eylül)*: sunucudaki silme ölü kod olur ve o da kalkar, ve CODE-STANDARD'daki çöp satırı düzelir. `+ New project` bugünkü gibi proje açar; ad sorma ekranı v9-2r'de. Listede (1)–(3). *Kararları: v9-2; tasarım: 135, 142, 165, 167, 170.* | Uygulama All projects ile açılıyor; sabitlenenler üstte, sonra son kullanılanlar; satıra basınca projenin son sohbeti açılıyor. Proje ekranı yok, ve `Exit project` buraya dönüyor. |
| 354 · v9-2k | ✅ **Cevabın altında cached ve missed.** Biten cevabın altında saat, önbellekten gelen token'lar yeşil `cached`, gelmeyenler kırmızı `missed`: `09:38 · 49.2k cached · 12.1k missed`. Modelin yazdığı token'lar gösterilmez. Sayısı olmayan eski cevapta yalnız saat kalır; süren cevapta tek sayı kalır. *(Backlog'dan — kullanıcı, 29 Eylül: "abi token gösteriyoruz ya her chatin altında 2 tane gösterlim bir yeşil bir kırmızı yeşil chached kırmızı missed cahced".)* *Kararları: v9-2; tasarım: 189, 192.* | Biten cevabın altında yeşil `cached` ve kırmızı `missed` var, `out` yok; eski cevapta yalnız saat. |
| 355 · v9-2l | ✅ **Sohbet açılırken açılmış gibi görünür.** Bir sohbet yüklenirken başlığı kenar çubuğundaki adıyla, yazma kutusu kapalı ve dosya paneli yerinde durur; mesajların yerinde, parlayan iskelet yerine v9-2c'nin spinner'ı döner. Tek başına duran `← back` kalkar. *Kararları: v9-2; tasarım: 194.* | Yüklenen sohbette başlık, kapalı yazma kutusu ve dosya paneli görünüyor, mesajların yerinde spinner dönüyor; `← back` yok. |
| 356 · v9-2o | ✅ **Açık dosya da çekilerek genişler.** Dosya açıkken de yan panelin sol kenarı çekilerek genişletilip daraltılır. Liste ile açık dosya tek genişlik: listeyi çektiğin kadar dosya açılır, dosyayı çektiğin kadar liste kalır. *Kararları: v9-2; tasarım: 158, 177.* | Dosya açıkken panelin kenarı çekilince genişliyor ya da daralıyor; dosya kapanınca liste o genişlikte, ve sonraki dosya o genişlikte açılıyor. |
| 380 | ✅ **Sohbetin sonuna gelen kart görünür.** Cevap gelmeyince ya da mesaj reddedilince çıkan kahverengi kart sohbetin en altına eklenir, ama liste ona kaymaz: kart yazma kutusunun altında yarım kalır, ve görmek için elle kaydırmak gerekir. Liste bugün yalnız yeni bir mesajda ve süren cevapta aşağı iniyor. Koşudan önce de böyleydi. *(349 tarayıcıda denenirken bulundu, 29 Eylül.)* **Sohbetin altına çıkan her kartta:** hata kartı, izin kartı ve oluşan dosya kartları — hepsi aynı yerde çıkıyor *(kullanıcı, 29 Eylül — "Sohbetin altına çıkan her şeyde … Hepsi aynı yerde çıkıyor, aynı sorunu yaşayabilirler.")*. **Okuyanı çekmez:** kullanıcı yukarıda eski mesajları okurken bir kart çıkarsa liste zıplamaz, kullanıcı yerinde kalır; süren cevap da böyle davranıyor *(kullanıcı — "Liste zıplamasın, bulunduğun yerde kal")*. | Sohbetin altındayken hata kartı, izin kartı ya da dosya kartı çıkınca bütünüyle görünüyor; yukarıda okurken çıkınca liste yerinde kalıyor. |

### Dalga 4 — dalga 3 birleşince

v9-1d v9-1c'nin; v9-4b v9-4a ile v9-2n'nin — proje ekranındaki seçiciyi v9-2n ekranla birlikte
kaldırır —; v9-2p, v9-2q ve v9-2r v9-2n'nin üstüne kurulur.

| # | İş | Bitti sayılır |
|---|---|---|
| 357 · v9-1d | ✅ **Kırpılmış sohbette çizgi.** `Continue here`'den sonra, modele hâlâ giden ilk mesajın üstünde bir çizgi: `Messages above this line are no longer sent to the model`. Eski mesajlar okunurken çizgi sohbetin alt kenarında bekler. Listede (5). *Kararları: v9-1; tasarım: 147, 182.* | Kırpılmış sohbette modele gitmeyen mesajlarla gidenlerin arasında çizgi; yukarı kaydırınca çizgi alt kenarda duruyor. |
| 358 · v9-4b | ✅ **Model seçici kalkar, ve model hiçbir yerde görünmez** *(29 Eylül'de değişti)*. **Mimari:** FOUNDATION'ın 6. kararı aynı parçada güncellenir: modellerin adlarını ve fiyatlarını `models.js`'ten okuyan kimse kalmıyor. Listede (7). *Kararları: v9-4; tasarım: 136, 157.* | Yazma kutusunda model seçici de modelin adı da yok. |
| 359 · v9-2p | ✅ **Projelerde arama.** All projects'te `Search projects` projelerin adında arar; ekran açılınca odak onda. Eşleşme yoksa `No projects match "…".` *Kararları: v9-2; tasarım: 135, 142, 167.* | Arama kutusuna yazınca liste daralıyor; eşleşme yoksa `No projects match "…".` yazıyor. |
| 360 · v9-2q | ✅ **Satırın `⋯` menüsü: Rename, Pin, Delete.** Her satırın `⋯`'sinde `Rename` — ad tarayıcının kutusunda değil, satırın yerinde düzenlenir —, `Pin` ya da `Unpin`, ve `Delete` — bugünkü onay penceresi, sohbet ve dosya sayısıyla. Projenin içinde hiç `⋯` yok. `Archive` v9-2t'de. *Kararları: v9-2; tasarım: 135, 161, 167.* | Satırın `⋯`'sinden proje yerinde yeniden adlandırılıyor, sabitlenip bırakılıyor, ve onayla siliniyor. |
| 381 | `UNALIGNED` **Panelin kenarını çekmek yazı seçmez.** Yan panelin sol kenarı çekilince — liste de açık dosya da — fare sürüklendiği yerdeki bütün yazıyı mavi seçiyor: mesajlar, kart, yazma kutusu. Madde 50'den beri böyle; 356 aynı kenarı açık dosyaya da verdi. *(356 tarayıcıda denenirken bulundu, 29 Eylül.)* | Panelin kenarı çekilirken sayfada hiçbir yazı seçilmiyor. |
| 361 · v9-2r | ✅ **Ad sorma ekranı.** Her `+ New project`'te ekranın ortasında ad sorulur: başlık `Name your project`, hiç proje yokken `Name your first project`. Enter ya da düğme projeyi yazılan adla açar ve boş sohbetine götürür; boş ad bir şey yapmaz. Bir proje varken üst çubuğun sağında `Cancel` durur, Esc de aynısını yapar: ikisi geldiği yere döner. Listede (3). *Kararları: v9-2; tasarım: 135, 153, 169, 195.* | `+ New project` ad soruyor; proje yazılan adla açılıyor ve boş sohbeti geliyor; `Cancel` ve Esc All projects'e dönüyor. |

### Dalga 5 — dalga 4 birleşince

v9-2s v9-2q'nun üstüne kurulur: ikisi de projenin menüsünü taşıyan yere dokunuyor, ve aynı anda koşarlarsa
biri ötekinin kullandığını silebilir. v9-2t v9-2p ile v9-2q'nun, v9-2u v9-2r'nin üstüne kurulur.

| # | İş | Bitti sayılır |
|---|---|---|
| 362 · v9-2s | ✅ **Kenar çubuğunda yalnız New chat ve sohbetler.** Proje açıkken kenar çubuğu dolu, belirgin bir `+ New chat`'le başlar; altında projenin bütün sohbetleri, sohbet yoksa `No chats yet.` Projeler listesi, `Recent chats` ve projelerin yanındaki `+` kalkar. *Kararları: v9-2; tasarım: 151, 152, 168.* | Kenar çubuğunda ilk göze çarpan `+ New chat`, altında projenin sohbetleri; projeler listesi yok. |
| 363 · v9-2t | ✅ **Arşiv.** Satırın `⋯`'sinde `Archive`: proje onaysız arşive gider, yerinde `<ad> archived · Undo` satırı kalır, ve `Undo` onu eski yerine koyar. `Archived` sekmesi sayısıyla: arşivdeki projeler, her birinin `⋯`'sinde `Rename`, `Unarchive` ve `Delete`. Arşiv boşken `No archived projects.`; hepsi arşivdeyse `Every project is archived.` *Kararları: v9-2; tasarım: 135, 161, 190, 191.* | `Archive` projeyi arşive alıyor ve yerinde `Undo` bırakıyor; Archived sekmesinde `Unarchive` projeyi geri getiriyor. |
| 364 · v9-2u | ✅ **All projects ve ad sorma ekranı yüklenirken ve yüklenemeyince.** Yüklenirken başlık, `+ New project`, arama ve sekmeler yerinde, listenin yerinde spinner; ad sorma ekranında ortada aynı spinner. Proje listesi okunamayınca iki ekranda da tek cümle, `Couldn't load projects.`, `Try again` ve `Copy`; `Copy` gelen hatayı olduğu gibi panoya koyar. *Kararları: v9-2; tasarım: 172, 173.* | Liste gelene kadar spinner dönüyor; sunucu hata verince cümle çıkıyor, `Try again` yeniden deniyor, `Copy` hatanın tam metnini kopyalıyor. |

### Dalga 6 — dalga 5 birleşince

v9-2v v9-2s ile v9-2w'nin üstüne kurulur: arama, sohbet listesinin üstüne ve katlanmış sütuna gelir.

| # | İş | Bitti sayılır |
|---|---|---|
| 365 · v9-2v | `ALIGNED` **Search chats.** `+ New chat`'in altında `Search chats` açık projenin sohbetlerinde arar: yazınca liste daralır, Enter ilk eşleşmeyi açıp odağı yazma kutusuna verir, Esc kutuyu boşaltır. Eşleşme yoksa `No chats match "…".` Katlanınca ikon sütununda bir arama ikonu: kenar çubuğunu açıp arama kutusuna odaklanır. *Kararları: v9-2; tasarım: 151, 168, 174.* | Arama yazınca sohbet listesi daralıyor; Enter ilk eşleşen sohbeti açıyor; katlanmış sütundaki arama ikonu kutuya götürüyor. |

### Prompt'lar — dalgalardan sonra, tek tek, bu sırayla

| # | İş | Bitti sayılır |
|---|---|---|
| 366 · v9-7a | `ALIGNED` **Liste yeni biçimde çıkar.** Her kare bir string yerine iki alanlı bir kayıt: `scene` ve `photo`. H3 prompt'unu QueenAgent yazmaz, queen-editor yazar *(29 Eylül)*. *Kararları: v9-7.* | QueenAgent'ın çıkardığı listede her kare, kendi senaryosunu ve fotoğraf prompt'unu taşıyan bir kayıt. |
| 367 · v9-8a | `ALIGNED` **Bütün skill'ler zayıf modeli bilir, ve `pov_` kalkar.** Prompt'lar zayıf bir text-to-image modeline gider; her sahne tek bir anın tek karesi ve 4 saniyelik bir video. Skill metinlerinin kelime tavanı yazılı bir kararla yükselir. *Kararları: v9-8.* | Her skill'in metni zayıf modeli, tek anı ve 4 saniyeyi söylüyor; hiçbir skill ya da araç `pov_` girdisi yazdırmıyor. |
| 368 · v9-9 | `ALIGNED` **Elbise çıkarma sahnesi senaryoya, aksi söylenmedikçe eklenmez.** *(Kullanıcı, 28 Eylül — "queen agent promtplarımn bir madde daha elbise çıkarma sahnesei senaryoya aksi söylenmediği sürece eklenmez".)* **Neden** *(kullanıcı, 29 Eylül — "abi bazen queen agent elbisesin değiştiği sahnelerde elbisesni çıktıüı framler yazmaya çalışıyor", "çıkaraıldığı ara sahneleri çizemiyor mesla bi sahnede var sonkirnde farklı bir elbise var yapar ama değiştiröe karaleri yaoamıtor")*: kıyafet sahneden sahneye değişebilir — bir sahnede bir elbise, sonrakinde başka bir elbise, ve model bunu çizer. Yazılmayan, aradaki kareler: elbisenin çıkarıldığı ya da değiştirildiği an. Zayıf model onları çizemiyor. **Yalnız Start a scenario'nun sahneleri yazdığı adımda** *(kullanıcı, 29 Eylül — "senrayoda olsa yeter sahnleri yzan madede satart senearyoda senaryoların yazıldığı madde")*: o adım, kullanıcı istemedikçe elbisenin çıkarıldığı ya da değiştirildiği anı sahne olarak yazmaz. Kullanıcı açıkça isterse o sahne yazılır. | Start a scenario, kullanıcı istemedikçe elbisenin çıkarıldığı ya da değiştirildiği anı sahne olarak yazmıyor; kıyafet bir sahneden ötekine değişebiliyor. Kullanıcı isterse o sahne yazılıyor. |
| 369 · v9-11 | `ALIGNED` **Konuşma senaryonun içine yazılır**, ki queen-editor'deki DeepSeek görüp H3 prompt'una eklesin. *(Kullanıcı, 29 Eylül — "ekstra queen agetn konuşam vs varsa sceneroyunun içinde yazması lazım ki queen editordeki deepsek görük eklesin anlaştırkm ı".)* Start a scenario sahneleri yazarken, kullanıcı bir karede konuşma istediyse onu o karenin sahne cümlesinin içine yazar; H3 prompt'unu yazan model senaryoyu gördüğü için onu ekler *(Queen Editor v8-3b)*. **Yalnız konuşma** *(kullanıcı — başka ekstra sorulunca: "başka yok gibi")*. | Kullanıcı bir karede konuşma isteyince Start a scenario onu o karenin sahne cümlesine yazıyor, ve cümle listeyle queen-editor'e gidiyor. |
| 370 · v9-8b | `ALIGNED` **Improve skill'i açılır, ilk kontrolüyle: tek an mı.** Kontroller tek yerde yazılır, ve Start a scenario onları son adımı olarak içerir. Seçicide en sonda yeni bir satır, açıklaması *Run four checks on a scenario's frames and prompts, and say yes after each one.* *(29 Eylül)*. Birden fazla anı anlatan kare tek ana iner ya da bölünür. Kontrol adımı sonunda ne değiştirdiğini gösterir ve onay bekler; değiştirdiği karenin fotoğraf prompt'unu yeniler, ve böldüğü kare kendi aksiyonunu ve fotoğraf prompt'unu alır. Listede (8). *Kararları: v9-8; tasarım: 138, 179.* | Improve seçicide en sonda, açıklamasıyla duruyor; seçilince birden fazla anı anlatan kareyi tek ana indiriyor ya da bölüyor, ne değiştiğini gösterip onay bekliyor, ve değişen karenin fotoğraf prompt'u yenileniyor. Start a scenario da bu kontrolle bitiyor. |
| 371 · v9-8c | `ALIGNED` **Kontrol: yalnız görünen parçalar.** Kamera açısından hangi karakterin hangi parçaları görünüyorsa prompt'a yalnız onlar girer; gerekirse görünürlük girdisi eklenir *(`man body no face`, kıyafetin `from behind` hâli gibi)*. *Kararları: v9-8.* | Improve'da ve Start a scenario'nun sonunda, açıdan görünmeyen özellikler prompt'tan çıkıyor. |
| 372 · v9-8d | `ALIGNED` **Kontrol: zayıf model bunu çizebilir mi.** Son hâldeki prompt'a bakar, ve çizilemeyecek olanı sadeleştirir. *Kararları: v9-8.* | Improve'da ve Start a scenario'nun sonunda, zayıf modelin çizemeyeceği prompt sadeleşiyor. |
| 373 · v9-8e | `ALIGNED` **Negatif prompt.** Senaryo başına tek liste, kadroya göre, kontrollerin en sonunda; prompt listesinin yanında ayrı bir dosyaya yazılır. Kullanıcının bulduğu dersler uygulanır. *Kararları: v9-8 ve v9-7.* | Start a scenario ve Improve bitince senaryonun negatif listesi kendi dosyasında duruyor. |
| 374 · v9-8f | `ALIGNED` **Edit prompts kontrollerle biter.** Bitince yalnız değiştirdiği karelerin kontrollerini yapar, ve kadro değiştiyse negatif liste yeniden yazılır. *Kararları: v9-8.* | Edit prompts bir kareyi değiştirince iş yalnız o karelerin kontrolüyle bitiyor, ve kadro değiştiyse negatif liste yeniden yazılıyor. |

### En sonda

| # | İş | Bitti sayılır |
|---|---|---|
| 375 · v9-6 | `ALIGNED` **Suffix system prompt'u güçlendirilecek.** *(Kullanıcı, 28 Eylül — "suffix system promptunu" güçlendirmek.)* **Kullanıcı kendisi yazar, ve madde en sonda durur** *(kullanıcı, 28 Eylül — "abi unu ben ypaıcam listenin en sonuna al bunu")*: koşu buraya geldiğinde spec, test ya da kod yazmaz; suffix'i kullanıcı değiştirir. | Kullanıcı yeni suffix'i yazdı. |
| 376 · v9-10 | `ALIGNED` **Token kullanımı optimize edilir:** gönderilen token azalır, ve daha büyük kısmı önbellekten gelir; aynı iş daha az paraya, kalite düşmeden. **En sonda, kullanıcıyla birlikte:** koşu buraya gelince durur ve kullanıcıyı bekler. *Kararları ve bugünkü bulgular: v9-10.* | Kullanıcıyla birlikte seçilen iş, öncekinden daha az token harcıyor, ve harcadığının daha büyük kısmı önbellekten geliyor. |

---

## Maddelerin kararları

Hizalamada kullanıcıyla konuşulanlar, maddenin bölünmeden önceki hâliyle. Parçalar yukarıda; bir
parçanın spec'i kendi maddesini buradan okur.

### v9-3 — Playwright MCP *(v9-3a, v9-3b)*

`ALIGNED` **Playwright MCP — bu depoda ayarı, ve QueenAgent'ın onunla kontrolü.** *(Kullanıcı, 23 Eylül. İlk v9'un 2. ve 3. maddeleriydi; 24 Eylül'de koşulmadan backlog'a döndü — "Playwringi backloga koy şimdilik gerek yok"; 28 Eylül'de buraya geldi.)* **En başta koşar** *(kullanıcı, 23 Eylül — "madde 1 yap böylece diğer maddelerde queen agentta playwright mcpyi kullanabiliriz"; 28 Eylül — "en başa al şimdi")*: öteki maddeler QueenAgent'ı tarayıcıda onunla kontrol edebilsin diye. İki yarısı var, ikisi de 23 Eylül'de konuşulup kapanmıştı. **Ayar** *("cihazda var bu repoda kullanmak için ayarlanmasını ekle tasklara ve queen agenta ekle")*: araç kullanıcı için değil, Claude için — Claude QueenAgent'ı tarayıcıda kendisi açar, ekran görüntüsünü alır ve arayüzü kullanır. Örnek [queen-design](../../../../queen-design/.mcp.json) *("sen karar ver queen design ayarı yaptıysa kopyalayabilirsin kullanımı")*: ayar depoda durur, sürüm sabittir *(`@latest` değil)*, tarayıcı arka planda açılır *("queen design gibi")*. Cihazda nasıl kurulu olduğu koşuda bulunacak *("araştırıp bulursun")*. **Kontrol** *("queen agent playwright mcp ile kontrol edilebilmek için düzenleme gerekiyorsa onu da ekle")*: Claude QueenAgent'ı açıp kullanıcının yerine kullanır ve bakar — *"tasarıma uyuyor mu, beklenen gibi çalışıyor mu"*. Açılan QueenAgent bu bilgisayarda yerel çalışan, Colab'daki değil. Gerçek AI çağrısı yapılabilir *("gerçek ai çağrısı yapma yapabilirsin evet")*. Önünde bir engel çıkmazsa bu yarı düzenleme yapılmadan kapanır.

### v9-7 — Senaryo listeyle gider *(v9-7a)*

**29 Eylül'de değişti: H3 prompt'unu QueenAgent yazmaz** *(kullanıcı, 29 Eylül — "abi aklıma şey geldi h3 promptlarını direkt agentta oluşturmak yerine direkt queen editor ai ksımına deepsek alalım hem senaryoyu hem fotoğrafı görürü ve düzgün bir prompt yazar ne diyorsun?", "daha kaliteli sonuç verir", "ve videoları beğenemzsek bir agenta yazarız ve çözülür"; "yol haritasını lütfen öyle güncelle")*. **Neden:** QueenAgent prompt'u fotoğraf üretilmeden önce yazıyor, ve zayıf model her zaman prompt'taki gibi çizmiyor; queen-editor'de yazan model üretilmiş fotoğrafı ve senaryoyu birlikte görür. **v9-7b kalktı**, numarası kaymadı. **Liste yine yeni biçimde çıkar**, ama her kayıt iki alanlı: `scene` ve `photo`. H3 prompt'unu queen-editor yazar — [Queen Editor v8](2026-09-25-queen-editor-v8-roadmap.md)'in v8-3b'si. Aşağıdaki hizalama metni 28 Eylül'ün hâli: H3 prompt'unu QueenAgent'ın yazmasına dair kısmı bu kararla düştü; MiniMax rehberinden okunanlar ise v8-3b'nin kaynağı olarak geçerli.


`ALIGNED` **H3 prompt'unu da QueenAgent yazar, ve senaryo listeyle gider.** *(Kullanıcı, 28 Eylül — "queen agent h3 promptunuda yazsın ne dersin ?", "bu haftanın asıl işi 1 olsun birde ne yapamya çalıştığımızda senaaryoda gitsin queen edtiore o da bir yer de yazın böylece kullanıcı maneuel eşleşmiş mi promptlar fotoğraf koalyca görebilir".)* **Bu haftanın asıl işi** *(kullanıcı, 28 Eylül)*. **Neden:** H3'e bugün giden prompt'u grok fotoğrafın SDXL etiketlerinden yazıyor, ve sahne kalitesi düşüyor *(kullanıcı — "h3 gibi çok güçlü bir video modeline sahibiz ama direkt promtplayamıyoruz h3 ü bildiğin üzere ve bu yüzden sahne kalitesi oldukça düşünyor")*. Fotoğrafla ve ne istendiği söylenerek grok'a elle yazdırılan prompt'lar açıkça daha iyi çıktı *(kullanıcı — "açıkça daha iyi denendi abi zatne kendimiz maneul güncelliyorduk promptları", "fotoğraf ne isteidğimiz söyliyuip groka veriyorduk")*. **Senaryo, QueenAgent'ın her kare için zaten yazdığı sahne cümlesidir** *(yapı dosyasının `scene` alanı)*. **Stil ayrıca söylenmez** *(kullanıcı — "bu referasn için geçerli abi normalde böyle bir problemimiz yok I2V de")*: gerçekçiye kayma referans modunda görüldü, I2V'de yok. **Her kare loop varsayılır** *(kullanıcı — "abi hepsinin loop varsay %95 öyle zaten gerisin biz manuel fixleriz")*: QueenAgent her H3 prompt'unu loop için yazar — hareket başladığı yere döner, hız sona kadar aynı kalır. Standart ya da bağlı modda üretilecek karenin prompt'unu kullanıcı elle düzeltir. **Kaynak: MiniMax'ın kendi rehberi** *(28 Eylül'de okundu; kullanıcı — "sadece kodda değil internttende arşatırabilrisin bu h3 promptu yazarkeden işnie yarar")* — [base rehber](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_base_en.md) ve [h3-prompt-writing skill'i](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/skills/h3-prompt-writing/SKILL.md). Oradan: bölümler bu sırayla `integrated_multimodal_description`, `overall_soundscape`, `non_diegetic_music`; fotoğraf yeniden anlatılmaz, prompt ona bağlanır ve oradan başlayan hareketin yolunu anlatır; kamera tipi, genliği ve hızıyla; anlatılan klibin süresine sığar; olay özeti ve *cinematic* gibi soyut kelime yerine somut görüntü ve ses. **H3 negatif almaz:** resmi belgelerde negatif alanı yok, uygulama da göndermiyor; kaçınılacak bir şey prompt'un içinde söylenir. Loop hakkında rehberde bir şey yok — loop kuralı bizim. **Liste yeni biçimde çıkar** *(kullanıcı — "abi şeyi konuşmadık şuan queen agent python lsitesi veriyor queen editorde python lsite ialıyor bu yapıyı düzenlemiz lazım farkındaysan"; karar — "ilk yöntemden gidleim")*: kopyala-yapıştır akışı aynı kalır, ama QueenAgent'ın çıkardığı listede her kare bir string yerine üç alanlı bir kayıt olur — `scene`, `photo`, `video`; H3 prompt'u elle düzeltilebilsin diye üç tırnak içinde, okunduğu gibi. **Senaryonun negatif listesi listeye girmez** *(kullanıcı — "abi negatif ayrı dursun queen agentta user manuel kopyala yapıştır yapsın")*: v9-8e onu ayrı bir dosyaya, prompt listesinin yanına yazar; kullanıcı kopyalayıp queen-editor'ün negatif alanına yapıştırır. **Listeyi okumak queen-editor'ün işi** — [Queen Editor v8](2026-09-25-queen-editor-v8-roadmap.md)'in v8-3'ü *(kullanıcı, 28 Eylül — "kabulu queen editore yazalım çünkü çok detalı bir günceleme")*: grok'un yedek kalması, senaryonun kartta nerede durduğu ve eski düz listenin okunması orada. **v8-3 önce biter:** bugünkü kutu yalnız string listesi okuyor, ve yeni listeye "Format hatası" der.

### v9-8 — Prompt yazma talimatları güçlenir *(v9-8a – v9-8f)*

**29 Eylül'de değişti:** H3 prompt'unu QueenAgent yazmadığı için *(v9-7'nin başındaki karar)* aşağıdaki akışın 6. adımı — H3 prompt'ları — düştü, ve kontrollerin ve Edit prompts'un bir karenin H3 prompt'unu yenilemesi de. Değişen karenin yenilenen yalnız fotoğraf prompt'u; böldüğü kare kendi aksiyonunu ve fotoğraf prompt'unu alır. Aşağıdaki metin 28 Eylül'ün hâli.

**29 Eylül — tasarımdan** *(tasarım: 138, 179)*: Improve seçicide en sonda, Edit prompts'tan sonra
durur; açıklaması *Run four checks on a scenario's frames and prompts, and say yes after each one.*
Açıklama sahibin açık noktasıydı, ve kullanıcı tasarımcının önerisini kabul etti *(v9-2'nin
kararları)*.


`ALIGNED` **QueenAgent'ın prompt yazarken kullandığı talimatlar güçlendirilecek: Start a scenario zayıf modeli bilir ve sonunda dört kontrol yapar; kontroller Improve skill'i olarak ayrıca da seçilir.** *(Kullanıcı, 28 Eylül — "queen agent şey ekledik mi promtplar güçlendirlekcek kısmını ve düzenlenecek"; hangisi olduğu sorulunca: "QueenAgent'ın prompt yazarken kullandığı talimatlar güçlendirilsin, yani modele giden metinler".)* **Sorun** *(kullanıcı — "abi bugun model promptların zayıf modele gittiğini bilmiyor sdxl için ve modlei nyapamayığı kadar komplex şeyleri yazıyor ve sıkıntı yaşıyoruz", "ama ben yapay zekaya belirtlp kontrol ettiğimde düzeltiyor")*. **Kullanıcının elle sorduğu dört soru dört ayrı adım olur** *(kullanıcı — "ben sana yapay zeka 6 yda 4 soru soruyoum dedim her biri 1 madde olsun savsaklama")*: **zayıf model** — "fotoğra üretene yapay zeka modeli çok zayıf sence yazdığın promptu bu yapayzeka üretevbilir"; **görünen parçalar** — "bu pov olayını var on ukaldırıyorum ve diyorumki ypatığın açıda o hangi karakterin hangi parçaları görünüuorsa onları yaz prompta yoksa model zayıf olduğu için o özellikleri öteki karakterler eklyior"; **negatif** — "senaryoya ve karakterlere özel negatic promtplar yazıdıyıroum karakterlerin özeliklkerinin karışmaması için"; **tek an** — "model çok zayıg ve tek bir anın fotoğrafının yapıyorum promptun veya senaryonun 1den fazla sahneyi analyıyorsa lütfen güncelle diyorum basit ve tek bir anı gösteicek şekilde yada bir kaç sahneye böl". **Start a scenario baştan sona iki şeyi bilir:** prompt'lar zayıf bir text-to-image modeline gider *(kullanıcı — "burdada biliyor abi zayıf bir model yazdığını")*, ve her sahne tek bir anın tek karesidir ve 4 saniyelik bir video olur *(kullanıcı — "h3 e de şey bilgisini vermemiz lazım her video 4sn oluyor")*. **Akışın sırası** *(kullanıcı — "abi bence şuank akış aynı sırada kalsın Sonra h3 gelsin sonra kontrol adımalrı başlasın")*: 1 plan; 2 karakterler ve kıyafetler, `pov_` girdisi olmadan; 3 mekânlar; 4 sahneler; 5 prompt'lar, bugünkü gibi; 6 H3 prompt'ları *(v9-7)*; 7 kontrol: tek an mı — önce bu, çünkü böldüğü kare sonraki kontrollere de girmeli; 8 kontrol: yalnız görünen parçalar — kamera açısı 5'te yazıldı; 9 kontrol: zayıf model bunu çizebilir mi — son hâldeki prompt'a bakar; 10 negatif prompt, senaryo başına tek liste, en sonda *(kullanıcı — "senaryo başına", "en son negatifide yazsın")*. **Bir kontrol bir kareyi değiştirirse o karenin fotoğraf ve H3 prompt'unu da günceller**, ve bölünen kare kendi aksiyonunu, fotoğraf ve H3 prompt'unu alır — yoksa H3 kontrolden önceki fotoğrafı anlatır ve liste eskir. **Improve ayrı bir skill**, kullanıcı istediğinde seçer *(kullanıcı kararı, 28 Eylül)*: 7–10. **Kontroller tek yerde yazılır**, ve Start a scenario onları son adımı olarak içerir *(kullanıcı — "plan bitince tek bir yer olsun improveu direkt çağırsın", "olur böyle yapalım")*; bugün bir skill ötekini çağıramıyor, iki metin birleşir. **Bütün skill'leri kapsar** *(kullanıcı — "bu dğeişikler bütün skilleri kapsasın")*: her skill zayıf modeli bilir, değiştirdiği karenin fotoğraf ve H3 prompt'unu yeniler, ve sonunda kontrolleri yapar. **Edit prompts** değiştirdiği karenin H3 prompt'unu da yeniden yazar *(kullanıcı kararı, 28 Eylül)*, ve bitince kontrollere geçer *(kullanıcı — "edit prompt bitince de improvu çağır desin")*. **Metin tavanı yazılı bir kararla yükselir** *(kullanıcı kararı, 28 Eylül)*: skill metinleri testlerle kısa tutuluyor — Start a scenario 450, Edit prompts 260 kelime *(Madde 123: zayıf bir model uzun metnin ortasını okumayı bırakıyordu)* — ve o kural bugünkünden zayıf bir model için konmuştu. **Improve seçicide yeni bir satır**, ekrana dokunduğu için tasarımcıya da gider — v9-2'nin listesinde (8). **Onay her kontrol adımının sonunda** *(kullanıcı — "sorun değil onay olsun görmek istiyorum ypaılan şeyi", "her kontrol eadımın sonunda abi")*: adım ne değiştirdiğini gösterir ve evet'i bekler. **Edit prompts'tan sonraki kontroller yalnız değiştirdiği karelere bakar**, ve kadro değiştiyse negatif liste de yeniden yazılır *(kullanıcı kararı, 28 Eylül)*. **Uzun bir senaryoda kontroller birkaç tura yayılır**, ve tur sınırı değişmez *(kullanıcı kararı, 28 Eylül)*: bir tur en çok 16 istek yapıyor; kalınan yeri plan dosyası tutar, kullanıcı "devam" der. **Negatif için kullanıcının bulduğu dersler** *(kullanıcının bu konuşma için verdiği not, 28 Eylül)*: negatif kişiye özel çalışmaz, asıl çözüm pozitif tarafta; koyu ten negatife yazılmaz — yazılınca adam beyaz çıktı, yerine adama özel karşıt etiketler girer *(`pale male`, `white man`)*; karakterin kendi özellikleri negatife girmez.

### v9-4 — Model menüsü *(v9-4a, v9-4b)*

**29 Eylül'de değişti: model hiç görünmez** *(kullanıcı, 28 Eylül, tasarım turunda — "Queen Flash,
bunu kaldıralım, vazgeçtim, beğenmedim, görünmesin model"; tasarımın 157'si)*. v9-4b'nin *modelin adı
yalnız bir yazı olarak görünür*'ü düştü. Aşağıdaki metin 28 Eylül'ün hâli.

`ALIGNED` **Model menüsü DeepSeek'in 10 Eylül değişikliğine göre yenilenecek.** *(DeepSeek'in [10 Eylül 2026 duyurusu](https://api-docs.deepseek.com/news/news260910), 11 Eylül'de okundu ve backlog'a yazıldı; 28 Eylül'de buraya geldi.)* Duyuruya göre üç şey değişti. **`deepseek-v4-pro` 14 Eylül 04:00 UTC'de kapandı:** istekler V4.1-Flash'a yönleniyor ve Flash fiyatından faturalanıyor, hata dönmüyor — *Queen Pro* seçen Flash alıyor, ekran Pro yazmaya devam ediyor. **Flash'ın fiyatı düştü:** giriş $0.22 → $0.15, çıkış $0.66 → $0.60 *(off-peak)*; menüdeki `$0.22 / $0.66 per 1M` yanlış. **`deepseek-v4-flash` artık eski ad:** V4.1-Flash'a yönlenen takma ad, modelin bugünkü adı `deepseek-flash`. **Pro kalkar, yalnız Queen Flash kalır** *(kullanıcı kararı, 28 Eylül)*, modelin bugünkü adıyla. **Seçici de kalkar**, modelin adı yalnız bir yazı olarak görünür *(kullanıcı kararı, 28 Eylül)*. Ekrana dokunduğu için tasarımcıya da gider — v9-2'nin listesinde (7).

### v9-1 — Sohbet sınırı *(v9-1a – v9-1d)*

**29 Eylül — tasarımdan** *(tasarım: 140, 146, 147, 182)*: dolu sohbetin bildirimi, mesaj
reddedilmeden, sohbet dolar dolmaz yazma kutusunun yerinde durur *(v9-1c)*; çember dörtte beşte,
40.000'de, yanındaki `N% full` ile önceden söyler *(v9-2i)*; kırpılmış sohbette modele gitmeyen
mesajları bir çizgi ayırır — **v9-1d, yeni parça**. Sahibin üç açık noktası tasarımcının önerisiyle
kaldı *(v9-2'nin kararları)*: `Continue here` onay istemez ve geri alınmaz, kırpılmış sohbet yeniden
dolunca yine çıkar, ve kırpmadan sonra çember modele hâlâ gideni okur. Aşağıdaki metin 28 Eylül'ün
hâli.

`ALIGNED` **Chat sınırlama hesaplaması değişecek: tavan yalnız sohbeti ölçer.** *(Kullanıcı, 25 Eylül — "chat sınırlama hesaplamasını değiştirelim"; 28 Eylül — "abi burda xontexti ölçelim o da chat olsun olur mu".)* **Bugün** ölçülen, son cevabın son isteğinin tamamı *([chat.py](../../../queen-agent/backend/features/workspace/domain/chat.py), `CONTEXT_CEILING`)*: sohbetin yanında system prompt, araç tarifleri, skill talimatı, o turun araç adımları, dosya adları ve açılan dosyalar kutusu da. **Olacak:** tavan ve gösterge yalnız sohbetin mesajlarını ölçer. **Açılan dosyalar kutusu da sayılmaz** *(kullanıcı — "sayılmıcak çünkü sonra yeni chat açıyoruz tekrar okuyor bir şey değişmiyor")*: sohbeti kutu yüzünden kapatmak bir şey kazandırmaz, yeni sohbet aynı dosyaları yeniden okur. **Tavan 50.000 kalır** *(kullanıcı — "tavan 50k kalsın")*. **Aynı sohbette devam** *(kullanıcı, 28 Eylül — "kullanıcı aynı chatten devam etme istersen claude coddeki gibi ama daha basit bir şekilde compose edebilcek", "direkt mesjaların üst kısmında kırpıcz 10k contexte kadar")*: kullanıcı isterse yeni sohbet açmak yerine aynı sohbette sürer; en eski mesajlar baştan kırpılır, sohbet 10.000'e inene kadar. Özet yok — Claude Code'daki gibi, ama daha basit. **Yalnız sohbet dolunca** *(kullanıcı kararı, 28 Eylül)*: bugünkü yeni sohbet uyarısının yanına bir de *burada devam et* seçeneği gelir. **Kırpılan mesajlar ekranda kalır** *(kullanıcı — "kalsın")*, yalnız modele gitmez. **Görünüşü yeni tasarımdan gelir** — v9-2'nin listesinde (5).

### v9-2 — Tasarım *(v9-2a – v9-2w)*

**29 Eylül'de bölündü** *(kullanıcı — "Desingner işini nitirdi queen agenta başlayabiliriz şimdi
roadmapı güncelelyelim desinge bakara"; dal: "tasarım içinde queen-agent-v3 bu branch ile mainin
farkına bak lütfen")*. Tasarım queen-design'ın `queen-agent-v3` dalında, ve `main`'le farkı okundu.
Tasarımcının v3 roadmap'i — queen-design'da
`docs/superpowers/roadmaps/2026-09-28-queen-agent-v3-roadmap.md`, yalnız o dalda — 63 madde; parçalardaki *tasarım: N* o belgenin maddesi, ve her biri orada kullanıcıyla hizalandı.
**Bir parçanın spec'i tasarımdan okur:** [`projects/queen-agent/`](../../../../queen-design/projects/queen-agent/)'in
sayfaları, `BEHAVIOUR.md` — sayfanın uygulamadan nerede bilerek ayrıldığı —, `DESIGN-STANDARD.md` —
ölçüler, renkler, sınıf adları — ve `APP-BUGS.md`. Tasarım QueenAgent'ın `dcf0a61c`'sine göre çizildi,
ve QueenAgent'ın kodu o günden beri değişmedi.

**Parça olmayanlar**, yalnız prototipi ilgilendirdikleri için: araştırma (133, 134, 188); A, B, C
yönleri ve karşılaştırmaları (142–145, 149); tuval ve belgeler (141, 148); durum şeridi (162, 163,
180); açıklama yazıları (160); sayfanın pencere genişliği (171); prototipin kod temizliği (170, 178,
183–185). 155'in uygulamaya düşen kısmı — `APP-BUGS.md`'nin 48'i — v9-2h'de.

**Listenin yerleri:** (1)–(3) v9-2a, v9-2b, v9-2j, v9-2n, v9-2p – v9-2w; (4) v9-2e; (5) v9-1c,
v9-1d, v9-2i; (6) v9-2a; (7) v9-4b; (8) v9-8b. Ötekiler tasarım turunda kullanıcının geri
bildiriminden doğdu: v9-2c, v9-2d, v9-2f, v9-2g, v9-2h, v9-2k, v9-2l, v9-2m, v9-2o.

**Tasarım turunda değişen iki karar:** (6)'nın *kalın*'ı düştü, sürüm adla aynı kalınlıkta
*(kullanıcı, 28 Eylül, tasarımın 159'u — "V8 kalın yazılmasın, Queen Editor yazıldığı gibi
yazılsın")*; (7)'de model hiç görünmez *(v9-4'ün kararları)*.

**29 Eylül'ün kararları:**

- **Sohbet silme kalkar** *(kullanıcı — Claude'un seçeneğini seçti: "Sohbet silme kalkar, tasarımdaki
  gibi. Projeyi silmek sohbetlerini de siler.")*: tasarımda sohbeti silmenin yeri yok. Bugün tek yeri
  proje ekranı; o ekran v9-2n'de kalkıyor, ve kenar çubuğundaki sohbet satırlarında × yok.
- **Sahibin üç açık noktası tasarımcının önerisiyle kalır** *(kullanıcı — "Üçü de öneri gibi
  kalsın.")*: `Continue here` onay istemez ve geri alınmaz, kırpılmış sohbet yeniden dolunca yine
  çıkar *(v9-1c)*; kırpmadan sonra çember modele hâlâ gideni okur *(v9-1b)*; Improve'un açıklaması
  *Run four checks on a scenario's frames and prompts, and say yes after each one.* *(v9-8b)*.
- **Parçalar toptan hizalandı** *(kullanıcı — Claude'un seçeneğini seçti: "Listeyi toptan onaylarsın,
  hepsini ALIGNED yazarım; düzeltmek istediğin parçayı söylersin")*. v9-2n ve v9-2r bölünmeden
  kaldı: ikisi de kendi içinde tek bir ekran.

Aşağıdaki metin 28 Eylül'ün hâli.

`ALIGNED` **QueenAgent'ın tasarımı güncellenecek, özellikle projelenme düzeltilecek.** *(Kullanıcı, 25 Eylül — "queen agent tasarımı güncellenecek, özellikle projelenme düzeltilecek".)* **Tasarımı tasarımcı yapar, ve tasarım koşu başlamadan gelir** *(kullanıcı, 28 Eylül — "tasarımı sen yapmıcan desingera vericez", "tasarım koşu başlamdan gelecek sıkıntı yok")*. **Tasarımcıya buradan prompt gitmez, ihtiyaçlar gider** *(kullanıcı — "sen prompt verme ihtiacları belirt sadece")*. **Tasarıma dokunan her madde bu listeye girer**, liste koşudan önce tasarımcıya gider, ve koşu gelen yeni tasarımı kullanır *(kullanıcı — "tasarıma dokunan her şey gidicek roadmapten önce atıcaz isteklerimiz yeni tasarım gelicek alıcaz kullanıcaz")*. (2), (3), (4) ve (6) backlog'dan geldi *(kullanıcı kararı, 28 Eylül)*. **(1) Projelenme düzeltilecek** *(kullanıcı, 25 Eylül)*. **(2) Proje yönetimi geliştirilecek** *(kullanıcı, 18 Eylül)*: bugün bir proje için yalnız iki eylem var — yeniden adlandırmak ve silmek — ve ikisi de hem kenar çubuğunun menüsünde hem proje ekranında duruyor. **(3) Yeni proje ve yeni sohbet açmak karmaşık** *(kullanıcı, 11 Eylül — v8'in test geçişi)*: bugün üç ayrı yer var — kenar çubuğunda *Projects*'in yanındaki `+`, bir proje seçiliyken üstteki *New chat*, ve hiç proje yokken açılan ayrı ekran. **(4) Kalem ile saat alt alta duruyor** *(kullanıcı, 11 Eylül — v8'in test geçişi; 28 Eylül — "yan yanda durmaktansa alt alta duruyor bunu tasarım düzelticek diyleim")*: bir mesajın altında sürüm şeridi `‹ 1/2 ›` ile kalem `✎` bir satırda, saat ile jeton sayısı ayrı bir satırda. **(5) Dolan sohbette *burada devam et*** *(v9-1c)*: sohbet 50.000'e dolunca yeni sohbet açmanın yanında bir de *burada devam et* seçeneği; seçilince en eski mesajlar modele gitmez ama ekranda kalır. **(6) Sürüm adın yanında** *(kullanıcı, 11 Eylül — v8'in test geçişi; v9-5 olarak yazıldı, 28 Eylül'de buraya katıldı)*: Madde 209 sürümü adın altına, soluk ve küçük koydu, ve bir dipnot gibi okunmuyor. Kullanıcının kararı: adın yanında, adla aynı boyda ve kalın. **Ayrıntısı tasarımcıya bırakılır**, ve gelen tasarım uygulanır *(kullanıcı — "burda tasarımcıya bırak ordan gelen tasarımı uygula")*. [v8'in test listesindeki](../../2026-09-10-queenagent-v8-test-listesi.md) *"adın altında"* satırı bu kararla reddedildi. **(7) Model seçici kalkar** *(v9-4b)*: tek model kalıyor, *Queen Flash*; adı yalnız bir yazı olarak görünür. **(8) Skill seçicide Improve** *(v9-8b)*: seçiciye yeni bir satır gelir. **Kullanıcıdan gereken:** tasarımcının yeni tasarımı, koşu başlamadan.

### v9-10 — Token kullanımı *(v9-10)*

`ALIGNED` **QueenAgent'ta token kullanımı optimize edilecek.** *(Kullanıcı, 29 Eylül — "queen agentta token kullanımını optimize et".)* **Hedef maliyet** *(kullanıcı, 29 Eylül — "abi dopru ve token chacede odaklanalım maliyete odaklanıyorum çünkü bir istek atıyorum 500k token harcıyor claudde subagetn açıyorum 15 dk çalışıyor 500k harcıyor bu büyük bir fark")*: aynı iş daha az paraya mal olur, ve cevapların kalitesi düşmez. **İki yandan:** gönderilen token azalır, ve daha büyük kısmı önbellekten gelir *(kullanıcı — "abi yani token kullanımıda optimöize edelim cache ile claude code nasıl 500k ile 30 dk çalışıyor biz tek istekte harcıyoruz mantıklı değil")*. **En sonda, kullanıcıyla birlikte yapılır** *(kullanıcı — "bunu en son al beraber yaoarız")*: koşu buraya gelince durur ve kullanıcıyı bekler. Nasıl yapılacağı, neyle ölçüleceği ve ekrandaki token sayıları o zaman birlikte konuşulur. **"read_file geliştirilecek" backlog'da kalır** *(kullanıcı, 29 Eylül — "evet ama bu backloga gidiyor")*.

**29 Eylül — tasarımdan** *(tasarım: 189, 192)*: biten cevabın altındaki tek sayı v9-2k'de ikiye
ayrılır, `cached` ve `missed`; aşağıdaki ilk bulgunun *bitince görünen* yarısı böylece düzelir.
Süren cevabın sayısı burada kalır.

**Bugün** *(29 Eylül'de koddan ve servislerin belgelerinden okundu; oranlar ölçülmedi — tek yerel sohbette token kaydı yok, gerçek sohbetler Colab'da)*:

- **Ekrandaki sayılar maliyeti göstermiyor.** DeepSeek'in `prompt_tokens`'ı önbellekten gelen ve gelmeyen kısmın toplamı *([belge](https://api-docs.deepseek.com/api/create-chat-completion))*; istemci onu `sent`, önbellekten geleni `cached` diye okuyor. Çalışırken görünen sayı `sent + cached + answered`, yani önbellekten gelen iki kez sayılıyor *([stream_answer.py](../../../queen-agent/backend/features/workspace/domain/usecases/stream_answer.py), `_volume`)*. Bitince görünen `sent + answered`, yani önbellekten gelen tam fiyat ödenmiş gibi *([ChatScreen.jsx](../../../queen-agent/frontend/src/features/workspace/ChatScreen.jsx), `Stamp`)*.
- **Önbellekten gelen 50 kat ucuz.** Flash'ta 1M token, yoğun olmayan / yoğun saatte: önbellekten gelen $0.003 / $0.006, gelmeyen $0.15 / $0.30, cevap $0.6 / $1.2 *([fiyatlar](https://api-docs.deepseek.com/quick_start/pricing))*. 500k'nın hepsi önbelleği kaçırsa bile en çok $0.075 / $0.15.
- **Açılan dosyalar ve talimat her istekte önbellek dışında kalıyor olmalı.** DeepSeek yalnız baştan birebir aynı kısmı önbellekten verir; önbellek noktaları isteğin sonu, cevabın sonu, istekler arasındaki ortak baş, ve uzun metinde sabit aralıklar — ve garanti yok *([belge](https://api-docs.deepseek.com/guides/kv_cache))*. Bizim istek sırası: sistem talimatı, sohbet, turun yeni adımları, dosya adları, açılan dosyalar, skill talimatı *([stream_answer.py](../../../queen-agent/backend/features/workspace/domain/usecases/stream_answer.py), `_asked`)*. Sonraki istekte yeni adımlar dosya adlarının önüne girer, ve önceki isteğin kuyruğu yenisinin başı olmaz. xAI da aynısını söylüyor: "only append new messages at the end" *([belge](https://docs.x.ai/developers/advanced-api-usage/prompt-caching/multi-turn))*.
- **Bir tur en çok 16 istek**, ve her biri her şeyi yeniden gönderir; `write_missing_actions` ayrıca ikinci bir modele istek atar.
- **Düşünme modu belirsiz.** Belgeye göre Flash'ta düşünme varsayılan olarak açık, ve araçlı isteklerde `reasoning_content` sonraki isteklerde geri gönderilmezse API 400 döner *([belge](https://api-docs.deepseek.com/guides/thinking_mode))*. Kod onu hiç ele almıyor, ve QueenAgent hata vermeden çalışıyor: kullanılan eski ad `deepseek-v4-flash` farklı davranıyor olabilir. Ölçülecek.
- **Claude Code karşılaştırması:** gösterdiği sayının neyi saydığı bulunamadı. Bu araçlarda tokenların büyük kısmı önbellek okuması, ve Anthropic onu normal fiyatın 0.1'iyle faturalar *([DEV](https://dev.to/flipslidersand/i-thought-i-used-1-billion-tokens-in-claude-code-last-week-turns-out-97-was-cache-1m2i))*.
