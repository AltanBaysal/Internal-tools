# Queen Editor — Yol Haritası v7

**Tarih:** 2026-09-21 · **Koşu dalı:** `feat/queen-editor-v7` · **Durum:** 0/16
**Öncesi:** [v6](2026-09-21-queen-editor-v6-roadmap.md) — koşuyor. v7 o kapandıktan sonra kendi
dalında başlar.
**Kaynak:** Maddelerin hepsi kullanıcının 21 Eylül'deki sözlerinden doğdu. Referans ailesi
*(267–275)* backlog'da **"Referansla içerik üretimi — H3 ile"** başlığıyla da duruyordu *(18 Eylül)*;
aynı iş olduğu kullanıcıyla doğrulandı ve girdi
[BACKLOG.md](../../../queen-editor/BACKLOG.md)'den çıkarıldı.

**Belge v6 dalında yazıldı** *(kullanıcı, 21 Eylül — "sen bu dalda oluştur roadmapi sıkıntı yok")*.
Başlıktaki dal koşunun dalı; yazıldığı yer başka.

**Numara kimliktir, sıra değildir.** v6 249 ve 250 ile açıldı ve koşarken 261'e kadar madde ekledi;
277–280 [QueenAgent v9](2026-09-21-queen-agent-v9-roadmap.md)'da. Numaralar **262'den** başlıyor; 281
konuşma sürerken eklendi ve numarası en büyük olsa da **ilk koşuyor** *(kullanıcı kararı)*.
**Bu belge iki kez yeniden numaralandı** *(21 Eylül)*: ilk taslak 251–252'yi, ikincisi 255–269'u
kullanıyordu, ve v6 biz yazarken ikisini de aldı. Numara tekrar kullanılmadığı için maddeler
taşındı — hiçbir spec eskilerine atıf yapmamıştı. **Bunun kuralı yok**, ve 276'da yazılacaklardan
biri de bu: koşulmayan bir yol haritası yazılırken numara nasıl ayrılır.

**Koşulacak sıra bu dosyanın sırası**, ve bu koşuda numara sırasıyla aynı.

## Nasıl koşulacak

**Her madde iki tur.** Önce yalnız testler: spec → plan → testleri yaz → commit; takım kırmızı kalır.
Sonra implementasyon: spec → plan → kodu yaz → commit; takım yeşile döner.

**İki aile ve iki tek madde var; hepsi 21 Eylül'de kullanıcıyla konuşuldu.** **281 en başta, tek
başına** *(kullanıcı — "bu madde ilk madde olsun, son olmasın")*; 262–266 kart modelini değiştiriyor;
267–275 referansla video üretimini kuruyor, ve kararları aşağıda tek yerde duruyor — maddeler oraya
yaslanıyor, her satır tekrarlamıyor. Bölünmelerinin sebebi kullanıcının isteği: *"olabildiğince küçük
test edilebilir maddeler böl, böylece geliştirme kolaylaşır"*.

**276 ötekiler gibi koşmaz.** Kullanıcıyla birlikte, adım adım yazılır — metni kullanıcı okur ve
kararlar o anda verilir. Koşunun en sonunda durmasının sebebi bu.

**Bu koşu kullanıcıdan hiçbir şey beklemiyor.** Bir ara 275 için REF2VA'ya konmuş bir Export (API)
dosyası istenecekti — video ve ses referansının `timeline_data`'da hangi alanlarla yazıldığı
bilinmiyordu. **Node'un kaynağı okununca gerek kalmadı** *(21 Eylül)*; alanlar 275'in satırında,
adlarıyla duruyor.

## Referansla video üretiminin kararları

*(Kullanıcı, 21 Eylül — "task olarak referans video üretimi eklemek istiyorum".)* 267–275 bu kararları
uyguluyor.

- **Yalnız H3.** WAN'da böyle bir mod yok; H3 kurulu değilken referans modu çalışmaz.
- **Havuz, H3 ne alıyorsa onu alır:** 9 fotoğraf, 3 video, 3 ses — toplam 12. Her klip 2–15 sn;
  görsel toplamı ve ses toplamı ayrı ayrı 15 sn'yi geçemez.
- **Sınırı uygulama hesaplar ve reddeder**, H3'ün hatasına bırakılmaz: o hata Colab loglarında kalır,
  kullanıcı görmez.
- **Havuz projede kalıcı** — fotoğraf prompt'ları gibi, kullanıcı silene kadar durur.
- **Havuz solda**, kartların yanında açılan bir panelde, tipe göre sıralar hâlinde. VS Code gibi
  kapanabilir; kart penceresi kapanamaz.
- **Yuva sabit, boşluk yasak.** Silince numaralar kaymaz; arada boş yuva kalırsa üretim başlamaz ve
  uygulama boşluğu söyler, kullanıcı sürükle-bırakla kapatır. Sebebi H3'ün kendi kuralı: referansları
  yoğun paketleyip **sıraya göre** numaralandırıyor, yuvanın numarasına göre değil — boşluk sessizce
  yanlış referansı işaret ederdi, ve sessiz hata en kötüsü.
- **Üretim video penceresinden**, *standart / referans* seçimiyle. Referans modunda loop ve sonrakine
  bağlama yok. Pencere fotoğraf panelindeki gibi **toplu prompt** ve **varyant** alır; satırı
  *"N prompt × M varyant = K kart"* der, çünkü referans modunda ortada kare yoktur — üretim kart
  doğurur.
- **Kart fotoğrafla doğmaz, fotoğraf arkadan gelir.** Video indiğinde ilk karesi çıkarılıp kartın
  fotoğraf yuvasına yazılır *(madde 266)* — galeride hızlı dolaşmak için, çünkü video yüklemek
  yavaş. Fotoğraf önkoşul değil sonuçtur; sıradan bir katmandır ve silinebilir, silinince kart
  videosunu çizer.
- **Prompt H3'ün REF2VA biçiminde:** altı bölüm — `subject_definitions`, `summary`,
  `retention_analysis`, `detailed_description`, `overall_soundscape`, `non_diegetic_music` — ve
  referanslara etiketle atıf: `<Subject N>`, `<Picture N>`, `<Video N>`, `<Audio N>`, tipe göre ayrı
  ve sıraya göre numaralı. Kullanıcı elle yazabilir; ya da QueenAgent üretir
  *([v9, madde 279](2026-09-21-queen-agent-v9-roadmap.md))*.
- **Video süresi 4 saniye**, bugünkü gibi grafikten. Çeşitlendirme ileride.
- **Ses:** bugünkü H3 video kartı ne yapıyorsa o — otomatik ses katmanı yok, istenirse sonradan
  eklenir.
- **Tekrar dene basit tutuluyor:** havuzun o anki hâliyle üretir, kart kendi referanslarını
  hatırlamaz. Sonucu açıkça yazılıyor: havuz değiştikten sonra tekrar denenen kart başka bir şey
  üretir. Bilerek seçildi — hatırlatmanın bedeli, şimdilik değmeyen bir arayüz.
- **Yeni model inmiyor.** Grafiğin `ref2va_model` yuvası defterin zaten indirdiği checkpoint'i
  yüklüyor, ve REF2VA'nın istediği ses VAE'si de kurulu.

---

| # | İş | Bitti sayılır |
|---|---|---|
| 281 | **Video prompt'unu yazan model fotoğrafı görecek.** *(Kullanıcı, 21 Eylül — "bazen fotoğraf niyetimizle tutmuyor, ve video prompt ile fotoğraf tutmayınca saçma şeyler ortaya çıkıyor … ilk başta direkt fotoğrafı da veririz".)* **Bugün** yazara verilen tek şey fotoğrafın **SDXL prompt'u**, yani fotoğrafın *olması gereken* hâli *(`data/xai_prompt_writer.py`)*. Fotoğraf niyetten saptıysa hareket, orada olmayan bir sahneye yazılıyor — kullanıcının gördüğü saçmalığın kaynağı bu. **Olacak:** karenin **fotoğrafı da** modele gidiyor, SDXL prompt'uyla birlikte, ve talimat çelişkiyi karara bağlıyor: **ikisi ayrılırsa fotoğraf kazanır**. Böylece niyet kaybolmuyor ama hareket gerçekten oradaki sahneye yazılıyor. **Yalnız H3'ün yazarına** *(kullanıcı kararı)*. **İki engel, ikisi de küçük:** istemci bugün yalnız metin gönderiyor — mesajın içeriği parça listesine dönecek *(`services/xai/client.py`)*; ve modelin resim kabul etmesi gerekiyor — `grok-4.3` etmiyorsa model ayarı değişir *(kullanıcı: "almazsa değiştiririz, sıkıntı yok")*. **Fotoğraf gönderilemezse iş düşer** ve sebebi sunucunun kendi cümlesiyle görünür; sessizce metin-yoluna dönmek, aynı saçmalığı sebebi görünmeden üretmek olurdu. **Maliyeti ölçüldü** *(21 Eylül)*: xAI resmi 448×448 karolara bölüp karo başına 256 token sayıyor, artı bir karo, en çok altı karo — yani bir resim en çok ~1792 token. `grok-4.3`'ün girdisi $1.25/1M olduğundan kare başına ~$0.0008'den ~$0.0030'a çıkıyor; **1000 kare $0.75 yerine $3.00**. Küçültülmüş bir kopya göndermek bunu yarıdan aza indiriyor *(448×672 ≈ 768 token)*; hangi ölçünün yeteceği spec'te ölçülür. | Fotoğrafı SDXL prompt'undan sapmış bir karede üretilen video, prompt'un değil **fotoğrafın** sahnesine göre hareket ediyor; fotoğraf gönderilemediğinde iş düşüyor ve sebebi ekranda yazıyor. |
| 262 | **Kutu kimliği: kart artık bir fotoğraf değil.** *(Kullanıcı, 21 Eylül — "cardlar ve üretimin asla fotoğrafa bağlı olmaması lazım, bir sürü yapı var, esnek olması lazım sistemin", ve "card'ı bir içerik olarak görmektense bir kutu gibi görebiliriz".)* **Bugün** galeri planı okurken yalnız **fotoğraf işlerini** satır sayıyor; kartın durumu ve adı fotoğrafından geliyor *([list_frames.py:94-99](../../../queen-editor/backend/features/photo_generation/domain/usecases/list_frames.py#L94-L99))*. Videoyla doğan bir kart bugün galeride hiç görünmez. **Olacak:** kart kendi kimliğiyle var olan bir **kutu**; hangi katmanla doğduğu onun varlığını belirlemiyor. **Kayıt katmanı zaten kutu** — kaydın birimi `(kart, yuva)` çifti *(`domain/layers.py`)* — yani değişen şey galerinin fotoğraf varsayımı, veri modeli değil. **Boş kutu yaşamaz** *(kullanıcı kararı)*: son katmanı gidince kart da gider, galeri bugünkü gibi temiz kalır, ve "kutu" koddaki model olarak durur, ekranda görünmez. | Videoyla doğmuş, fotoğrafı olmayan bir kart galeride görünüyor ve durumu videosundan okunuyor. |
| 263 | **Bağımlılık tek kurala iniyor.** **Bugün** iki kural var: ses videonun üstüne biner, ve her şey fotoğrafın üstüne. **Olacak:** tek kural kalıyor — **ses videoya bağlı**. Fotoğraf serbest: video artık fotoğraf beklemiyor, ve fotoğrafa kimse bağlı değil. Bir katman silinince giden şey *"üstündekiler"* değil, **ona bağlı olanlar** oluyor. | Fotoğrafı olmayan bir karta video üretilebiliyor; videosu olan karta ses binebiliyor; videosu olmayana binemiyor. |
| 264 | **Fotoğraf da silinebilir bir katman.** **Bugün** fotoğrafı silmek kartı silmek demek, ve `remove_layer` fotoğrafı hiç kabul etmiyor *([remove_layer.py:15](../../../queen-editor/backend/features/photo_generation/domain/usecases/remove_layer.py#L15))*. **Olacak:** fotoğraf da öteki katmanlar gibi silinir, yuvası boşalır, kart durmaya devam eder — **son katman gidince kutu gider**. Fotoğrafı silinen kartın videosu durur: video zaten üretilmiştir, fotoğrafa ihtiyacı yoktur. | Fotoğrafı silinen kart galeride videosuyla duruyor; videosu da silinince kart galeriden gidiyor. |
| 265 | **Kartı sil, ekranda tek hareket.** *(Kullanıcı, 21 Eylül — "biz silme ve temizleme yaparken bunun da sıkıntısını yaşıyorduk: fotoğraf geç sil, geri videoya geç".)* **Bugün** sunucu tarafı bunu zaten yapıyor — `remove_frames` kartın sahip olduğu her katmanı diskten çıkarıyor — ama ekran kullanıcıyı katman seçmeye zorluyor. **Olacak:** seçili kartlar katman seçtirmeden, içindeki her şeyle birlikte siliniyor. | Seçili üç kart tek hareketle siliniyor; fotoğrafları, videoları ve sesleri diskten gidiyor. |
| 266 | **Video indiğinde ilk karesi fotoğraf yuvasına yazılıyor.** *(Kullanıcı, 21 Eylül — "card'da olabilir bence, bazen hızlıca dolanmak istiyoruz ve videonun yüklenmesi daha yavaş sürüyor".)* Fotoğrafı olmayan bir karta video indiğinde ilk karesi `ffmpeg` ile çıkarılıp fotoğraf yuvasına yazılıyor. Galeri ve export bundan hiç haberdar olmuyor: ikisi de zaten fotoğrafı çiziyor ve yazıyor. **Bir üretim işi ilk kez iki yuvayı birden dolduruyor** — bugün her iş tek yuva doldurur, ve bu maddeyle değişen tek kural bu. | Fotoğrafsız bir karta video indikten sonra kartın fotoğraf yuvası dolu, ve galeri videoyu değil o kareyi çiziyor. |
| 267 | **Referans havuzu diskte.** Referans dosyaları projenin klasörüne yazılıyor, listeleniyor, siliniyor. Tarayıcı Drive'a uzanmadığı için yükleme de okuma da sunucudan geçer *(FOUNDATION 4)*, ve havuz diskte durur *(FOUNDATION 2)*. Sınır yok, ekran yok — yalnız saklama. | İki referans yükleniyor, listeleniyor, biri siliniyor; sunucu yeniden başlatılınca kalan hâlâ orada. |
| 268 | **Havuzun sınırları sunucuda.** Adet *(9 fotoğraf / 3 video / 3 ses)*, klip süresi *(2–15 sn)* ve toplamlar *(görsel 15 sn, ses 15 sn)* doğrulanıyor. Süre dosyanın kendisinden okunuyor — `ffprobe`; ffmpeg zaten kurulu. | Onuncu fotoğraf, 20 saniyelik bir klip ve toplamı taşıran bir ekleme reddediliyor; reddin cümlesi hangi sınıra takıldığını söylüyor. |
| 269 | **Havuz ekranda.** Kartların solunda kapanabilir panel; tipe göre sıralar; yükleme ve silme. Sıranın başlığı doluluğu söylüyor *("Fotoğraflar 4/9")*. Panelin açık mı kapalı mı olduğu tarayıcının bileceği şey, sunucuya sorulmaz. | Ekrandan iki referans ekleniyor, biri siliniyor, panel kapanıp açılıyor; sayfa yenilenince havuz duruyor. |
| 270 | **Sıralama ve boşluk.** Referanslar sürükle-bırakla sıralanıyor, ve arada kalan boş yuva ekranda görünüyor. | Bir referans sürüklenip yeri değişiyor, sıra sunucuya yazılıyor; ortadaki bir referans silinince kalan boşluk ekranda görülüyor. |
| 271 | **Video penceresinde referans modu.** *Standart / referans* seçimi; referans seçilince pencere toplu prompt ve varyant alıyor, loop ile sonrakine bağlama kapanıyor. Satır *"N prompt × M varyant = K kart"* diyor. | Pencerede referans seçilince prompt kutusu ve varyant satırı geliyor, loop ve bağlama seçilemiyor, ve satır kaç kart doğacağını söylüyor. |
| 272 | **Üretimin reddi.** Üç durumda üretim başlamıyor ve sebebini söylüyor: H3 kurulu değil, havuz boş, arada boş yuva var. | Üç durumun her birinde üretim kuyruğa hiç girmiyor ve ekrandaki cümle hangisi olduğunu söylüyor. |
| 273 | **Referans işi kart doğuruyor.** Kuyruğa giren referans işi yeni kartlar yaratıyor — N prompt × M varyant kadar, fotoğraf katmanı olmadan. *262 ve 263'ün üstünde duruyor; üretici bu maddede sahte, o yüzden kartlar henüz boş.* | Üç prompt ve iki varyantla altı kart doğuyor, hiçbirinde fotoğraf katmanı yok, ve galeri onları gösteriyor. |
| 274 | **Üretici REF2VA'yı koşuyor — fotoğraf referanslarıyla.** H3 üreticisi `mode`'u `REF2VA` yapıyor, havuzun fotoğraflarını ComfyUI'ye yükleyip timeline'a yazıyor, mp4'ü alıyor. Grafik değişmiyor; fotoğraf referansının alanları elimizdeki export'tan okunuyor. | Fotoğraf referanslarıyla referans modunda üretilen kartın videosu iniyor ve referansa benziyor. |
| 275 | **Video ve ses referansları da giriyor.** Timeline'a video ve ses satırları da yazılıyor. **Alanları node'un kaynağından okundu** *(21 Eylül, [nodes_minimax_h3_director.py](https://github.com/darksidewalker/ComfyUI-DaSiWa-Nodes/blob/main/nodes/nodes_minimax_h3_director.py))*, yani tahmin yok: bir satır `type` *(`image` · `video` · `audio`)*, `value` *(yüklenen dosyanın adı)*, `slot` ve `order` *(sıra; varsayılanları listedeki indeks)*, `enabled` *(varsayılan `true`)*, `trim_start` / `trim_end` *(varsayılan `0` / `None` — klip kırpması)*, `duration`, `start`, `id` taşıyor. Yalnız video satırında bir alan daha var: **`media_mode`**, üç değerden biri — `video` · `audio` · `video_audio` — ve grafiğin arayüzündeki V / A / V+A düğmeleri bu. Video ve ses de fotoğraf gibi ComfyUI'ye yüklenip adıyla anılıyor, yani üreticinin bugünkü yükleme yolu aynen kullanılıyor. | Havuzunda video ve ses de bulunan bir üretimde ikisi de H3'e gidiyor, ve inen videoda etkileri görülüyor. |
| 276 | **CLAUDE.md, yol haritası ve backlog madde yazımı için güncellenecek.** *(Kullanıcı, 21 Eylül — "claude core roadmap ve backlog madde yazımı için güncellenecek".)* **Bu madde kullanıcıyla birlikte, adım adım yapılır** *(kullanıcı, 21 Eylül — "bu maddeyi aslında seninle beraber adım adım yapacağız, o an kararlaştıracağız, ben promptları vs okuyacağım; bu senin yapabileceğin bir şey değil")*: metin tek başına yazılmaz, kullanıcı okur ve kararlar o anda verilir. **Koşunun en sonunda**, bu sebeple. Bugün CLAUDE.md'nin yol haritası bölümü maddenin ne zaman yazıldığını, nasıl sıralandığını ve nasıl koşulduğunu söylüyor; **içinin nasıl yazılacağı** için tek cümlesi var, ve **backlog kelimesi hiç geçmiyor**. Bu belgenin iki kez yeniden numaralanması da buraya bir kural borcu bıraktı: koşulmayan bir yol haritası yazılırken numara nasıl ayrılır. | Kullanıcıyla birlikte yazılıp kullanıcı tarafından onaylanınca. |
