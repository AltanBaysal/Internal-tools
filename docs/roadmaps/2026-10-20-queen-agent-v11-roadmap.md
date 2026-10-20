# QueenAgent — Yol Haritası v11

**Tarih:** 2026-10-20 · **Koşu dalı:** `feat/queenagent-v11` *(henüz açılmadı)* · **Durum:** 0/3 · hizalanmadı
**Öncesi:** [v10](2026-10-05-queen-agent-v10-roadmap.md) — 27/27 kapandı ve main'e birleşti.
**Kaynak:** Maddelerin hepsi kullanıcının 19 – 25 Ekim haftası için yazdığı plandan, 20 Ekim'de
verildi: v11-1 planın 10. maddesi, v11-2 12.'si, v11-3 13.'sü. Üçü de
[BACKLOG.md](../../queen-agent/BACKLOG.md)'den bir girdiyi içine aldı, ve girdiler oradan çıkarıldı:
v11-1 *"Bazı projeler kayboldu"*, v11-2 *"Süren tur ekranda canlı akmıyor, F5'le güncelleniyor"*,
v11-3 *"read_file geliştirilecek"*. Girdilerin sözleri, bilinenleri ve sorulacakları tablonun altında,
maddenin kendi başlığında.
**Queen Editor'de de:** planın 10. maddesi iki uygulama için *("Uygulamalar")*; Queen Editor'deki
aynısı [Queen Editor v10](2026-10-20-queen-editor-v10-roadmap.md)'un v10-1'i. **İki araç ayrı proje**
*(kullanıcı, 8 Ekim — "abi iki aracı tutan bir test olamsın bunu istemiorum bunalr tammaen ayrı bir
proje")*: iki madde ayrı yazılır, ayrı koşar, ve ikisini bağlayan bir test yazılmaz.
**Hangi koşunun önce koşacağı kullanıcıya sorulacak.** v9 ile v10'da iki koşu aynı anda açık durmadı
*(kullanıcı, 5 Ekim — "iki roadmepi ortak koşmacayğız ve ortak klasöür olmayacak önce queen editoru
koşucaz bitiricez sonra queen agnetı koşucaz")*; o söz o iki koşu içindi.

**Numaralar:** maddeler v11-1 – v11-3 diye yazıldı, ve koşu başlarken ortak sayaçtan gerçek
numaralarını alır. Sayaçta en yüksek numara bugün 470 (Queen Editor v9).

**Sıra, dalgalarla** — tablonun sırası dalgaların sırası. Bir dalganın maddeleri aynı anda koşabilir
ve aynı yere dokunmaz; dalga, öncekiler birleşince başlar. Dalgalar kod derin okunmadan, backlog'un
bilinenlerinden ve klasörlere bir bakıştan kuruldu: spec'ler yazılınca yeniden bakılır.

- **Dalga 1:** v11-1, v11-3. v11-1 kaydın yoluna — proje ve sohbet deposu, `queued_write.py`'nin
  yazıcısı, `store.py` — ve ekranın hata hâline dokunur; v11-3 ajanın araçlarına — `tools.py`,
  `usecases/read_file.py`, ve araçların modele giden açıklamaları, `prompt.py`. Ekrana yalnız v11-1
  dokunur. *Tahmin:* v11-1, Drive'a ulaşılamamayı okumada da hata yaparsa `read_file.py`'nin
  "file not found"una değebilir; öyleyse v11-3 onun arkasından koşar. v11-1'in kodu, tasarımı
  kullanıcıdan dönmeden başlamaz.
- **Dalga 2:** v11-2. Düzeltmesi turun dinlenişine — `routes.py`'nin `_listened`'ı, `useChat.js` —
  ya da notebook'un tüneline dokunur, yani v11-1'le ekranı ve `routes.py`'yi paylaşabilir: onun
  arkasından. **İlk iki adımı kod değil** — kullanıcının cevabı ve sebebin gösterilmesi —, dalgayı
  beklemeden yapılabilir.

---

| # | İş | Bitti sayılır |
|---|---|---|
| v11-1 | `UNALIGNED` · **Kayıt başarısı yanlış gösteriliyor: "başarılı", veri kalıcı yere yazıldıktan sonra görünecek.** *(Kullanıcı, 20 Ekim — "Başarılı mesajı, veri kalıcı hafızaya yazıldıktan sonra gösterilsin", "Sorun: Uygulamalar veriyi sadece cache'e yazınca "başarılı" gösteriyor; kalıcı kayıt yapılmadan işlem tamamlanmış görünüyor. Veri kaybı riski."; aynı gün — "bunu aslıdna architecture güncelleme gibi yapabilirz", "uygulama data nın nereye yazıldığını bilmez sadeve save yapar ve save bekler işlem başarılı dönünce devam eder gibi")* **Backlog'daki "Bazı projeler kayboldu" buraya katıldı** *(kullanıcı, 13 Ekim — "şuan queenagentta projeer kayboldu bazıalrı nasıl olduğunu anlamadık backloga at bunu araştırmamzı alzım")*: 13 Ekim'in incelemesinin en olası yolu *(B)* tam bu — Drive bağlantısı kopukken ekran başarılı dedi, yazmalar Drive'a hiç ulaşmadı. **Bugün** proje değişikliği bellekte yapılır ve istek hemen cevaplanır; dosyayı arkadan bir yazıcı yazar *(447, [queued_write.py](../../queen-agent/backend/features/workspace/data/queued_write.py))*, ve yazıcı üç denemeden sonra yalnız log'a yazıp bırakır. **Claude'un anlayışı, henüz onaylanmadı:** bu tek tek yazmalara yama değil, bir mimari değişikliği. Uygulama tek bir *save* çağırır, onu bekler, ve ancak save başarılı dönünce devam eder. Save'in üstünde hiçbir şey verinin Drive'a mı, bir önbelleğe mi, başka bir yere mi gittiğini bilmez; bu bilgi yalnız save'in arkasında durur. Save başarılı dönmek için verinin kalıcı yere yazılmasını bekler, yani başarı ancak kalıcı yere yazıldıktan sonra görünür. Save düşerse uygulama devam etmez, ekran hatayı save'in söylediği gibi gösterir, ve değişiklik olmuş gibi görünmez. Kullanıcının 13 Ekim isteği de buraya girer: Drive'a ulaşılamazsa QueenAgent devam etmez, hata gösterir. **Yapının kendisi değiştiği için spec'ten önce tasarım** *(CLAUDE.md'nin Subagents bölümü)*: reviewer bir tasarım çizer, ana agent onu tartışır, ve tasarım koddan önce kullanıcıya gider; spec ondan sonra yazılır. **Kullanıcıya sorulacak:** (1) hangi yazmalar save'den geçer — proje değişiklikleri, sohbetin mesajları, ajanın yazdığı dosyalar, hepsi mi; kullanıcının *"uygulama … sadeve save yapar"*ı hepsini söylüyor gibi, ama onaylanmadı; (2) "kalıcı" nerede başlar — Drive bağlantısının makinedeki önbelleği mi, Drive'ın kendisi mi: save neyi bekler; (3) 447'nin kararı yerini bu yeni şekle mi bırakıyor: 447'nin kuyruğu isteği yazma diske ulaşmadan cevaplıyor, kullanıcının yeni sözü ise save'i beklemeyi söylüyor — 9 Ekim'in kararı *(kullanıcı — "bu yazmaları Flask yönetir, Drive değil; Flask'a öyle bir özellik ekle, queue gibi", "flask tak diye kapanırsa kaybolsun sıkıntı yok")* bununla değişiyor mu; (4) Drive'a ulaşılamazsa okumalar da durur mu — boş liste yerine hata. Bilinenler aşağıda, *v11-1*'in başlığında. | Sorulanların cevabıyla netleşir. Kullanıcının sözünden: uygulamanın kaydettiği her yer save'i çağırıp bekliyor, ve verinin nereye yazıldığını save'in üstünde hiçbir şey bilmiyor. Başarı ekranda ancak save başarılı döndükten sonra görünüyor. Düşen bir save işlemi durduruyor: uygulama devam etmiyor, ekran hatayı save'in söylediğiyle gösteriyor, ve değişiklik başarılı görünmüyor. Drive'a ulaşılamayan bir oturumda QueenAgent boş bir liste göstermiyor, hata gösteriyor. Tasarım koddan önce kullanıcıya gitti. |
| v11-2 | `UNALIGNED` · **Canlı akış çalışmıyor: süren tur ekranda canlı akacak.** *(Kullanıcı, 20 Ekim — haftalık planın 12. maddesi, üç adımla: v10'dan önce Colab'da token ve araç çağrılarının canlı akıp akmadığını cevaplamak; sebebin Cloudflare Quick Tunnel olduğunu, yazılı iki yoldan biriyle göstermek; gösterilince düzeltmeyi uygulamak.)* **Backlog'daki "Süren tur ekranda canlı akmıyor, F5'le güncelleniyor" buraya katıldı** *(kullanıcı, 13 Ekim — "queen agenttta o arkaplanda çalışıyor ama değişikleri steam etmiyor token artışını toolcalları vs ben f5 e basınca güncelleniyor neden incelerm sin"; incelemeden sonra: "backloa aekle bunu")*. **Bugün** tur sunucuda sürüyor, ama token sayısı ve araç çağrıları ekrana tur sürerken gelmiyor; sayfa yenilenince o anki hâl görünüyor. **Sebep gösterilmedi, ve gösterilmeden düzeltilmez.** Sırası planın üç adımı: (1) kullanıcının cevabı, (2) sebebin gösterilmesi, (3) düzeltme — şekli gösterilen sebebe göre. Bilinenler ve iki yol aşağıda, *v11-2*'nin başlığında. | Sebep gösterildi ve maddeye yazıldı. Colab'da, notebook'un açtığı adresten, tur sürerken token sayısı ve araç çağrıları ekrana geldikçe görünüyor; F5 gerekmiyor. |
| v11-3 | `UNALIGNED` · **grep ve read_file geliştirilecek: ajan büyük bir dosyanın yalnız gereken kısmını okur.** *(Kullanıcı, 20 Ekim — "grep ve read_file gibi araçları geliştir".)* **Backlog'daki "read_file geliştirilecek" buraya katıldı** *(kullanıcı, 28 Eylül — "büyük dosyalarının hepsinide okumak zorunda kalmasın gerekli kısımlarını okusun", "read file geliştirilecek diyelim"; 29 Eylül — "bir de sürekli jsonu baştan okuyuo güncellemek ai için zor olabilir belki readi geliştirirsek sadeece alakalı maddeler okur ve analiz eder")*. **Bugün** `read_file` yalnız dosyanın adını alır ve dosyanın tamamını döner *([read_file.py](../../queen-agent/backend/features/workspace/domain/usecases/read_file.py), [tools.py](../../queen-agent/backend/features/workspace/domain/tools.py))*; ajanın araçları arasında grep diye bir araç yok. Dosyayı değiştiren yapılı araçlar ise var — `set_character`, `add_frame`, `update_frame` ve öteki. **Claude'un anlayışı, henüz onaylanmadı:** ajan bir dosyada aradığını bulabilir ve yalnız gereken kısmı okur — bir JSON'da yalnız alakalı maddeleri —, dosyanın tamamını okumak zorunda kalmaz. **Kullanıcıya sorulacak:** (1) "grep" yeni bir arama aracı mı — tek dosyada mı, projenin bütün dosyalarında mı; (2) read_file neyi okur: satır aralığı mı, JSON'un bir maddesi mi — bir kare, bir karakter —, ikisi mi; (3) hangi dosyalar büyük ve sorun çıkarıyor; (4) maliyetin ölçülüp ölçülmeyeceği — backlog'daki *"Token kullanımı optimize edilecek"* aynı yere değiyor ama ayrı kalıyor. | Sorulanların cevabıyla netleşir. Kullanıcının sözünden: büyük bir proje dosyasında ajan, dosyanın tamamını okumadan aradığını buluyor ve yalnız alakalı kısmı okuyor; sohbetteki adımlarda bu görünüyor. |

---

### v11-1 — Kayıt başarısı *("Bazı projeler kayboldu"yu içine aldı)*

Backlog girdisinden, 13 Ekim'deki hâliyle. Bazı projeler QueenAgent'ın listesinde artık görünmüyor;
nasıl olduğu anlaşılmadı. **Sebep gösterilmedi**, ve gösterilmeden düzeltilmez.

**Araştırmanın bakacağı yerler** *(Claude, 13 Ekim — commit'lerden, sebep sayılmadan)*: v10'da proje
kaydı değişti. 447'den beri projelerin bilgisi tek bir `projects.json`'da, sunucu onu açılışta bir kez
okuyup bellekte tutuyor ve değişiklikleri sıralı bir yazıcıyla diske yazıyor. 448 eski projeleri her
açılışta bir kerelik oraya taşıyor; okunamayan, diskin reddettiği ya da zamanı metin olmayan bir projeyi
bütünüyle atlayıp log'a yazıyor, ve eski dosyalara dokunmuyor. *(Backlog'daki "448'in taşıma kodu ve
eski proje dosyaları silinecek" ayrı bir girdi olarak duruyor; aşağıdaki A ile E bu taşımadan.)*

**Kullanıcının tahmini ve isteği** *(13 Ekim — "muhtemelen collabtin drive ile bağlantısı koptu böyle
bir şey olursa ilerlemyemliyiz hata gösteremlyiiz")*: Colab'ın Drive bağlantısı kopmuş olabilir.
Claude'un anlayışı, henüz onaylanmadı: Drive'a ulaşılamazsa QueenAgent hiçbir şeyi okumuş ya da yazmış
gibi devam etmez — boş bir liste göstermez, diske bir şey yazmaz —, ekranda bunu söyleyen bir hata
gösterir. Tahmin, sebep gösterilene kadar tahmin.

**İnceleme, 13 Ekim** *(bir subagent; kodda ve gerçek backend sınıflarıyla bir betikte denendi, Colab'da
değil. Hangisinin kullanıcıya olduğu kullanıcının kanıtıyla belli olur)*. 447'den *(9 Ekim)* beri açılan
bir projenin klasöründe `project.json` yok: satırı `projects.json`'dan düşerse onu bir daha hiçbir şey
listelemez, çünkü 448'in taşıması yalnız `project.json`'lu klasörleri okuyor. Daha eski projeler sonraki
açılışta eski dosyalarından geri gelir.

- **A — gösterildi, en güçlüsü:** açılışta `projects.json` bulunamazsa sunucu onu "hiç proje yok" sayar
  *(`file_project_store.py`'nin `_loaded`'ı)*, ve 448'in taşıması aynı açılışta eski projeleri bulup
  `projects.json`'ı yalnız onlarla **yeniden yazar** *(`old_projects.py`'nin `move_old_projects`'i,
  `take_in`)*. Drive'ın Colab bağlantısı duran bir dosyaya "bulunamadı" diyebiliyor
  *([colabtools #5970](https://github.com/googlecolab/colabtools/issues/5970), Mayıs 2026)*. Görülen: 9
  Ekim'den sonra açılan bütün projeler gider; eskiler 447'den önceki ad, iğne ve arşiv hâlleriyle geri
  gelir; kaybolanların klasörleri Drive'da durur.
- **B — gösterildi:** Drive oturum ortasında koparsa
  *([colabtools #3441](https://github.com/googlecolab/colabtools/issues/3441))* değişiklikler yalnız
  bellekte ya da makinenin kendi diskinde kalır, ekran başarılı der; sonraki açılışta gider. Yazıcı üç
  denemeden sonra yalnız log'a yazıp bırakıyor.
- **C — gösterildi:** aynı `projects.json`'da iki sunucu — başka bir Colab oturumu, ya da Serve hücresi
  yeniden çalışırken kapanmamış eski sunucu —: her biri kendi kopyasını bütün olarak yazar, sonuncu
  ötekinin eklediklerini siler.
- **D — şüphe:** oturum bittiğinde Drive'ın yerel önbelleğinde kalmış yazmalar; notebook Drive'ın
  `flush_and_unmount`'unu hiç çağırmıyor.
- **E — gösterildi:** 448 okuyamadığı eski bir projeyi her açılışta atlıyor; v9 onu listeliyordu.
- **F — şüphe, kayıp yok:** 12 Ekim 12:16'dan *(`e6bedf8b`)* önce açılmış bir oturum hâlâ v9'u çalıştırır,
  ve v9 v10'da açılan projeleri göstermez.
- **Elendi:** sohbet satırı yazmaları (463, 467) proje satırına dokunmuyor; proje yalnız onaylanan
  Delete'le gidiyor; ekran yalnız Archived sekmesi ve aramayla gizliyor.

**Drive hatasının yutulduğu ya da boş sonuca döndüğü yerler** *(kullanıcının isteği için, aynı
inceleme)*: `projects.json` bulunamazsa boş liste; `store.py`'nin `list_dir`'i olmayan klasörü boş liste
sayıyor; `_into_folder` "bulunamadı" alan her yazmada bütün klasör zincirini yeniden açıyor; yazıcının
düşen yazması yalnız log'da; silmede "bulunamadı" yok sayılıyor; bulunamayan sohbet ve dosya "chat not
found" / "file not found" oluyor; başka her disk hatası ekrana yalnız "HTTP 500" olarak geliyor; sağlık
kontrolü kökü hiç yoklamıyor, ve notebook kökün gerçekten Drive'da olduğuna bakmıyor.

**Kullanıcı baktı, 13 Ekim** *("durmuyorlar baktım muhtmelen mount koptu ama kullanırken bir hata
lamadığım için fark edemedim")*: eski `projects.json` ne sürüm geçmişinde ne çöp kutusunda. Kullanırken
hiçbir hata görülmedi. Bu B'yle bağdaşıyor: kopuk bağlantıda yazmalar Drive'a hiç ulaşmaz, ekran yine
başarılı der — Drive'ın geçmişinde de bu yüzden iz kalmaz. Gösterilmedi; log yok.

**Kullanıcıya hâlâ sorulacak ve bakılacak** *(13 Ekim'den)*: hangi projeler kayboldu ve en son ne zaman
görüldüler; hepsi 9 Ekim'den sonra mı açıldı (evetse A–D); Drive'daki klasörleri duruyor mu —
kullanıcının *"durmuyorlar"*ı eski `projects.json` için mi klasörler için mi, belli değil; arşivde mi; ve mümkünse kaybolduğu Colab
oturumunun sunucu log'u. Serve hücresinin log'unda ilk v10 açılışından sonraki bir açılışta *"Moving
projects of the old layout into projects.json"* satırı A'yı gösterir; *"projects.json was not written
… [Errno 107]"* B'yi; *"Old project … was not moved"* E'yi.

### v11-2 — Canlı akış *("Süren tur ekranda canlı akmıyor"u içine aldı)*

**Bilinenler** *(Claude, 13 Ekim)*:

- Kodda bir kusur bulunmadı: tur her değişiklikte sürümünü artırıp dinleyenleri uyandırıyor
  (`live_turns.py`'nin `apply`'ı), `GET …/events` her değişiklikte bütün snapshot'ı bir kare olarak
  gönderiyor (`routes.py`'nin `_listened`'ı), ve ekran her kareyi çiziyor (`useChat.js`'in `heard`'ü).
- Canlı akışı 462 kurdu *(10 Ekim)*: tarayıcı turu EventSource'la, SSE olarak dinliyor. QA onu yalnız
  yerelde, tünelsiz denedi.
- Notebook uygulamayı bir Cloudflare Quick Tunnel'dan (trycloudflare) açıyor, ve Cloudflare'in belgesi
  *"Quick Tunnels do not support Server-Sent Events (SSE)"* diyor
  *([Limitations](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/do-more-with-tunnels/trycloudflare/))*.
  Tünel kareleri tutuyorsa görülen tam bu: tur sürerken hiçbir şey, F5'te o anki hâl, sonda cevap.
- Bununla bağdaşmayan: 461'den önceki akış da `text/event-stream`'di, ama POST'tu ve `fetch`'le
  okunuyordu. O akış Colab'da canlı aktıysa tüneli bozan SSE'nin kendisi değil GET/EventSource farkı
  olabilir — düzeltmenin şeklini bu belirler.

**Adım 1 — kullanıcıya sorulacak:** v10'dan önce *(10 Ekim'den önce)* Colab'da token ve araç çağrıları
canlı akıyor muydu.

**Adım 2 — sebebi gösterecek iki yol:** (1) Claude bu bilgisayarda cloudflared'le saniyede bir satır
gönderen küçük bir test sunucusunu bir dakikalığına Quick Tunnel'dan açar, GET ile POST'u ve
`text/event-stream` ile başka bir türü yan yana ölçer — bir dakikalığına internete açık bir adres
oluştuğu için kullanıcının onayıyla. (2) Kullanıcı Colab'da tur sürerken F12 → Network → `events` →
EventStream'e bakar: satırlar canlı mı, tur bitince topluca mı geliyor. **Hangi yolun seçileceği
kullanıcıya sorulacak.**

**Adım 3 — düzeltme:** gösterilen sebebe göre; şekli spec'te.

### v11-3 — grep ve read_file *("read_file geliştirilecek"i içine aldı)*

Backlog girdisinde sözlerden başka bir şey yoktu: *"Ayrıntılar kullanıcıyla konuşulacak."* Sorulacaklar
tablodaki satırda. Araçların açıklamaları modele gider *(`prompt.py`'nin `READ_FILE`'ı ve
`THE_FILES_NAME`'i)*: madde onları da değiştirir.
