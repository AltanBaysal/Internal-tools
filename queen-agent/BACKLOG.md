# Backlog — QueenAgent

Gerçek ama henüz bir koşuya bağlanmamış işler. Sırası gelince buradan çıkar, o koşunun yol
haritasına girer.

## Akış sadeleşecek, yük ajana bırakılacak

*(Kullanıcı, 28 Eylül — "queen agentın agenti deepsek v1 flash senin gibi oldukça güçlü bir model biz
bu akışı nasıl daha basitleştiriz ve agenta bırakırız yükü", "komplesliği azaltlaım ve agenta
özgürlük sunalım", "abi bunuda backloga alalım yapyalım ilk yöntemden gidleim sonra farkıda görmüş
oluruz hem".)* **Ayrıntılar kullanıcıyla konuşulacak.**

## read_file geliştirilecek

*(Kullanıcı, 28 Eylül — "büyük dosyalarının hepsinide okumak zorunda kalmasın gerekli kısımlarını
okusun", "read file geliştirilecek diyelim"; 29 Eylül — "bir de sürekli jsonu baştan okuyuo güncellemek
ai için zor olabilir belki readi geliştirirsek sadeece alakalı maddeler okur ve analiz eder".)*
**Ayrıntılar kullanıcıyla konuşulacak.**

## Token kullanımı optimize edilecek

*(Kullanıcı, 29 Eylül — "queen agentta token kullanımını optimize et", "bunu en son al beraber
yaoarız"; 30 Eylül — "bunu backloga at şimdilik".)* v9'da 376 olarak hizalandı ve koşulmadı;
konuşulanlar [v9'un](../docs/roadmaps/2026-09-25-queen-agent-v9-roadmap.md) v9-10 bölümünde.
**Ayrıntılar kullanıcıyla konuşulacak.**

## Suffix system prompt'u güçlendirilecek

*(Kullanıcı, 28 Eylül — "suffix system promptunu" güçlendirmek, "abi unu ben ypaıcam listenin en
sonuna al bunu"; 30 Eylül — "şuan son task olan suffix güncelelmesi backloga".)* v9'da 375 olarak
hizalandı ve koşulmadı: suffix'i kullanıcı kendisi yazar. **Ayrıntılar kullanıcıyla konuşulacak.**

## Start a scenario spicy skill'i açılacak

*(Kullanıcı, 29 Eylül — "bir de start senrayo spicy diye bir ksill açıcaz ama şimdi değil ozaman
konuşurz".)* **Ayrıntılar kullanıcıyla konuşulacak.**

## Yapı basitleşecek

*(Kullanıcı, 1 Ekim — "queen agent backlogun yapıyı basitleştiriceyğimizde ekler msini".)*
**Ayrıntılar kullanıcıyla konuşulacak.**

## Elbiselerde karışıyor

*(Kullanıcı, 2 Ekim — "queen agent backloga elbiselerde karışıyor ekler misin".)* **Ayrıntılar
kullanıcıyla konuşulacak.**

## Kenar çubuğunun "Couldn't load chats." hali tasarımdan iki yerde ayrı

*(Claude, 9 Ekim — v10'un 444'ünü yapan coder'ın karşılaştırması; tasarım `queen-design`'ın
`queen-agent-v4` dalı, 219.)* Tasarımda sohbetler okunamayınca *Search chats* soluk ve basılamaz
(`disabled`, opacity 0.4); uygulamada açık kalıyor — bir şey göstermiyor, Enter bir şey açmıyor. Boşluk:
tasarımda cümleyle düğmeler arası 12 px, altta boşluk yok; uygulamada 10 px ve altta 10 px. 444 yalnız
Copy'nin görünüşünü aldı.

## Araç çağrısının yanındaki sözler son cevaba bitişik yazılıyor

*(Claude, 9 Ekim — v10'un 445'ini deneyen QA'da görüldü; 445'ten gelmiyor.)* Bir round araç
çağrısıyla birlikte söz de söylerse, o söz son cevabın başına boşluksuz ekleniyor: ekranda *"Let me
write that file for you.Answer to …"*. `run_turn.py`'de roundların sözleri `"".join(said)` ile
birleşiyor. **Gerçek modelle doğrulanmadı** *(kullanıcı, 9 Ekim — "gerçek kullanımda görünen bir problem
yok, bunu kontrol edilmedi diye işaretleyelim")*: QA sahte bir DeepSeek'le gördü; gerçek DeepSeek bir
araç çağırırken aynı cevapta söz söylüyor mu, bilinmiyor. Gerçek kullanımda görülürse ele alınır.

## 448'in taşıma kodu ve eski proje dosyaları silinecek

*(Kullanıcı, 9 Ekim — "kullandıktan sonra sileceğimiz bir sonraki roadmap'te".)* v10'un 448'i eski
projeleri her açılışta bir kerelik `projects.json`'a taşıyor ve eski dosyalara — proje başına
`project.json`, `pinned`, `archived` — dokunmuyor. Kullanıcı taşımanın çalıştığını gördükten sonra bir
sonraki QueenAgent roadmap'inde taşıma kodu ve bu eski dosyalar kalkar.

## Sürüm değiştirmek kenar çubuğunun sırasını güncellemiyor

*(Claude, 10 Ekim — 452'nin reviewer'ı.)* Sürüm değiştirmek sohbetin son kullanımını değiştirebiliyor
— etkin satırın son mesajı başka olur *(447)* —, sunucuda kenar çubuğunun sırası da değişiyor; ekran
yalnız sohbeti yeniden okuyor, sıra bir sonraki tura kadar eski kalıyor. Continue here sırayı
değiştirmiyor: kırpma yalnız mesajı işaretliyor *(452'nin QA'sı denedi)*.

## Proje açılınca sohbet listesi iki kez okunuyor

*(Claude, 10 Ekim — 452'nin QA'sı gördü; 452'den önce de vardı.)* All projects'ten bir proje açınca
`GET …/chats` iki kez gidiyor. İkisi de bellekten cevaplanıyor, diske gidilmiyor; Drive'ın tünelinde
bir gidiş-dönüş fazla.

## Suffix system prompt'a iki boş satırla ekleniyor

*(Claude, 10 Ekim — 455'in reviewer'ı.)* `SYSTEM_PROMPT_SUFFIX` bir satır sonuyla başlıyor, ve
`system_prompt()` araya bir boş satır daha koyuyor: ikisi arasında iki boş satır var, docstring bir
diyor. Davranış eskisi gibi; yalnız docstring yanlış.

## Gönderilen mesaja bir anahtar

*(Claude, 10 Ekim — mimarın sohbet tasarımının isteğe bağlı 5. adımı, [tmp/chat-turn-design.md](../tmp/chat-turn-design.md).)*
Soru sunucuya yazılıp cevabı tarayıcıya ulaşmadan bağlantı koparsa tarayıcı soruyu gitmemiş sayar ve
yeniden gönderince soru iki kez yazılır *(449'un sınırı)*. Tarayıcının ürettiği bir anahtar ve sunucunun
bellekteki son gönderimler haritası bu aralığı kapatır.

## Proje silinirken aynı anda gelen mesaj klasörü yeniden açabiliyor

*(Claude, 10 Ekim — 461'in coder'ı ve reviewer'ı.)* Proje silmek, projenin canlı turu varsa 409 alıyor;
ama bakış ile taşıma tek adım değil. Silme bakıp hiçbir tur görmedikten hemen sonra aynı projeye bir
mesaj sohbeti tutarsa, sohbeti okuyup soruyu yazarken çöpe taşınan projenin klasörünü bir sohbet
dosyasıyla yeniden açabiliyor. Listede görünmüyor, çöpteki proje bütün kalıyor; yalnız diskte sahipsiz
bir klasör. **Önerilen çözüm** (reviewer): silme projeye bir "kapanıyor" işareti koysun, `reserve` o
işaretli projede sohbet tutmasın — bakmak ve işaretlemek tek kilit altında.

## Stop, model daha ilk sözünü söylemeden de hemen kessin

*(Claude, 10 Ekim — v10'un 460'ının reviewer'ı buldu; v10'da 464 olarak yazıldı, kullanıcı backlog'a aldı —
"hepsi için önerdiğini yap sıkıntı yok".)* `client.py` isteği kesme imkânını ancak `urlopen` döndükten, yani
servis cevaba başladıktan sonra alıyor. Servis daha cevap vermeden basılan Stop yalnız bir işaret koyuyor ve
istek en fazla `MODEL_IDLE_SECONDS` (180 sn) sonra iniyor. Kapatmak için istemci bağlantıyı istek gitmeden
açmalı (`urlopen` yerine `http.client`); bu, istemcinin taşıma yolunu ve testlerin `opener` dikişini değiştirir.

## Reddedilen bir isteğin kartındaki Try again o isteği değil turu dener

*(Claude, 10 Ekim — v10'un 463'ünü deneyen QA'da görüldü; 463'ten eski.)* Sürüm değiştirme ya da kırpma
reddedilince `useChat.js`'in `setError`'u *"Couldn't get a response."* kartını gösteriyor; kartın Try
again'i sohbetin `…/retry` kapısını çağırıyor, reddedilen isteği yeniden göndermiyor. Cevaplanmış sohbette
bir şey yapmadan kartı kapatıyor; son cevabı başarısız ya da cevapsız bir sohbette ise bir tur başlatır.

## Bir frontend testi arada düşüyor

*(Claude, 9 Ekim — Queen Editor v9'un 439'unda görüldü.)* `src/features/workspace/ChatScreen.test.jsx`'in
"a stored answer keeps the calls it made, behind one card" testi bütün suite'te bir koşuda düştü; aynı
gün QA'nın koşusunda da bir test düşmüştü, adı yakalanmadı. Tek başına üç kez ve suite'le bir kez
geçti. Makine yükteyken vitest'in 5000 ms'lik süresini aşıyor olabilir — sebep gösterilmedi.

## Kadın karakterin kafası görünüyorsa yüzü de görünür

*(Kullanıcı, 12 Ekim — "kadın akrakterin akfası görünüyorsa ama yüzü görünüyorsa yinde yüz eitkeleride
korunur yani kafa arkadan gibi bir yapı oluşturulamaz nedeni ise çok kırlıyor kadın aynı akdın gibi
durmuyor"; "sdxl ayna ekleme gibi bir bir kaç kural daha eklicez".)* Claude'un anlayışı: kadın
karakterin kafası karedeyse yüzü de görünür ve yüz etiketleri korunur; kafanın arkadan göründüğü bir
kare kurulmaz, çünkü o karede kadın başka biri gibi çıkıyor. Ayna kuralının yanında SDXL kuralı olarak
girer. Bugünkü `SDXL_DOCUMENT` ise kamera açısına göre etiketleri gizlenen ayrı girdiler kurulmasını
söylüyor, gizli kafa örneğiyle *(Rule 1)*; yeni kural bununla birlikte okunacak. **Ayrıntılar
kullanıcıyla konuşulacak.**

## Saç, göz ve kıyafet sahneler arasında sabit kalır

*(Kullanıcı, 12 Ekim — "karakter tanımlanıyorsa saç ve göz rengi net bir şekilde saç rengi tanımlansın
sahnler arasında kadın değişmesin elibseler içinde rengi şekli sabitlensin yani bir sahnde beyaz bir
sahnede siyah görmeyleim tutarlılık içöin".)* Bir karakter tanımlanırken saç ve göz rengi açıkça
yazılır, ve kadın sahneden sahneye değişmez. Kıyafetin rengi ve biçimi de sabitlenir: bir sahnede
beyaz, ötekinde siyah olmaz. "Elbiselerde karışıyor" girişiyle *(2 Ekim)* aynı soruna değiyor.
**Ayrıntılar kullanıcıyla konuşulacak.**

## Vücut kılı varsayılan olarak yok

*(Kullanıcı, 12 Ekim — "ve default vucüt kılı olmadığı varsayılsın kullancıı söylemdiği sürece ayna
gibi".)* Kullanıcı istemedikçe karakterlerde vücut kılı olmaz — ayna kuralı gibi, yalnız kullanıcı
isteyince girer. **Ayrıntılar kullanıcıyla konuşulacak.**

## Stil: gerçekçiye yakın mı, çizim gibi mi kullanıcıya sorulur

*(Kullanıcı, 12 Ekim — "3d, cgi, photorealistic, realistic, sketch, monochrome, glow, bunları negative
eklemdğimizde farklı bir taz çıkıyor ve eklemessek farkalı default bunların negative eklenmiş hali ama
yinede usera sorulsun gerçekçiye yakın mı yoksa daha çim gibi ister msiiniz diye".)* `3d`, `cgi`,
`photorealistic`, `realistic`, `sketch`, `monochrome` ve `glow` negatif listede olunca bir stil, olmayınca
başka bir stil çıkıyor. Varsayılan: yedisi de negatif listede. Yine de kullanıcıya sorulur: gerçekçiye
yakın mı, yoksa daha çizim gibi mi. Negatif listeyi bugün Start a scenario'nun Step 10'u ve Improve'un
Step 5'i yazıyor. **Ayrıntılar kullanıcıyla konuşulacak.**

## Süren tur ekranda canlı akmıyor, F5'le güncelleniyor

*(Kullanıcı, 13 Ekim — "queen agenttta o arkaplanda çalışıyor ama değişikleri steam etmiyor token
artışını toolcalları vs ben f5 e basınca güncelleniyor neden incelerm sin"; incelemeden sonra:
"backloa aekle bunu".)* Tur sunucuda sürüyor, ama token sayısı ve araç çağrıları ekrana tur
sürerken gelmiyor; sayfa yenilenince o anki hâl görünüyor. **Sebep gösterilmedi**, ve gösterilmeden
düzeltilmez.

**Bilinenler** *(Claude, 13 Ekim)*:
- Kodda bir kusur bulunmadı: tur her değişiklikte sürümünü artırıp dinleyenleri uyandırıyor
  (`live_turns.py`'nin `apply`'ı), `GET …/events` her değişiklikte bütün snapshot'ı bir kare olarak
  gönderiyor (`routes.py`'nin `_listened`'ı), ve ekran her kareyi çiziyor (`useChat.js`'in `heard`'ü).
- Canlı akışı 462 kurdu *(10 Ekim)*: tarayıcı turu EventSource'la, SSE olarak dinliyor. QA onu
  yalnız yerelde, tünelsiz denedi.
- Notebook uygulamayı bir Cloudflare Quick Tunnel'dan (trycloudflare) açıyor, ve Cloudflare'in
  belgesi *"Quick Tunnels do not support Server-Sent Events (SSE)"* diyor
  *([Limitations](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/do-more-with-tunnels/trycloudflare/))*.
  Tünel kareleri tutuyorsa görülen tam bu: tur sürerken hiçbir şey, F5'te o anki hâl, sonda cevap.
- Bununla bağdaşmayan: 461'den önceki akış da `text/event-stream`'di, ama POST'tu ve `fetch`'le
  okunuyordu. O akış Colab'da canlı aktıysa tüneli bozan SSE'nin kendisi değil GET/EventSource farkı
  olabilir — düzeltmenin şeklini bu belirler.

**Sebebi gösterecek iki yol:** (1) Claude bu bilgisayarda cloudflared'le saniyede bir satır gönderen
küçük bir test sunucusunu bir dakikalığına Quick Tunnel'dan açar, GET ile POST'u ve `text/event-stream`
ile başka bir türü yan yana ölçer — bir dakikalığına internete açık bir adres oluştuğu için
kullanıcının onayıyla. (2) Kullanıcı Colab'da tur sürerken F12 → Network → `events` → EventStream'e
bakar: satırlar canlı mı, tur bitince topluca mı geliyor. **Kullanıcıya sorulacak:** v10'dan önce
*(10 Ekim'den önce)* Colab'da token ve araç çağrıları canlı akıyor muydu.

## Bazı projeler kayboldu

*(Kullanıcı, 13 Ekim — "şuan queenagentta projeer kayboldu bazıalrı nasıl olduğunu anlamadık backloga
at bunu araştırmamzı alzım".)* Bazı projeler QueenAgent'ın listesinde artık görünmüyor; nasıl olduğu
anlaşılmadı. **Sebep gösterilmedi**, ve gösterilmeden düzeltilmez.

**Araştırmanın bakacağı yerler** *(Claude, 13 Ekim — commit'lerden, sebep sayılmadan)*: v10'da proje
kaydı değişti. 447'den beri projelerin bilgisi tek bir `projects.json`'da, sunucu onu açılışta bir
kez okuyup bellekte tutuyor ve değişiklikleri sıralı bir yazıcıyla diske yazıyor. 448 eski projeleri
her açılışta bir kerelik oraya taşıyor; okunamayan, diskin reddettiği ya da zamanı metin olmayan bir
projeyi bütünüyle atlayıp log'a yazıyor, ve eski dosyalara dokunmuyor.

**Kullanıcıdan gereken:** hangi projeler kayboldu ve en son ne zaman görüldüler; Drive'daki klasörleri
duruyor mu; arşivde mi; ve mümkünse projelerin kaybolduğu Colab oturumunun sunucu log'u.

**Kullanıcının tahmini ve isteği** *(13 Ekim — "muhtemelen collabtin drive ile bağlantısı koptu böyle
bir şey olursa ilerlemyemliyiz hata gösteremlyiiz")*: Colab'ın Drive bağlantısı kopmuş olabilir.
Claude'un anlayışı, henüz onaylanmadı: Drive'a ulaşılamazsa QueenAgent hiçbir şeyi okumuş ya da
yazmış gibi devam etmez — boş bir liste göstermez, diske bir şey yazmaz —, ekranda bunu söyleyen bir
hata gösterir. Tahmin, sebep gösterilene kadar tahmin.

**İnceleme, 13 Ekim** *(bir subagent; kodda ve gerçek backend sınıflarıyla bir betikte denendi, Colab'da
değil. Hangisinin kullanıcıya olduğu kullanıcının kanıtıyla belli olur)*. 447'den *(9 Ekim)* beri
açılan bir projenin klasöründe `project.json` yok: satırı `projects.json`'dan düşerse onu bir daha hiçbir
şey listelemez, çünkü 448'in taşıması yalnız `project.json`'lu klasörleri okuyor. Daha eski projeler
sonraki açılışta eski dosyalarından geri gelir.
- **A — gösterildi, en güçlüsü:** açılışta `projects.json` bulunamazsa sunucu onu "hiç proje yok" sayar
  *(`file_project_store.py`'nin `_loaded`'ı)*, ve 448'in taşıması aynı açılışta eski projeleri bulup
  `projects.json`'ı yalnız onlarla **yeniden yazar** *(`old_projects.py`'nin `move_old_projects`'i,
  `take_in`)*. Drive'ın Colab bağlantısı duran bir dosyaya "bulunamadı" diyebiliyor
  *([colabtools #5970](https://github.com/googlecolab/colabtools/issues/5970), Mayıs 2026)*. Görülen: 9
  Ekim'den sonra açılan bütün projeler gider; eskiler 447'den önceki ad, iğne ve arşiv hâlleriyle geri
  gelir; kaybolanların klasörleri Drive'da durur.
- **B — gösterildi:** Drive oturum ortasında koparsa *([colabtools #3441](https://github.com/googlecolab/colabtools/issues/3441))*
  değişiklikler yalnız bellekte ya da makinenin kendi diskinde kalır, ekran başarılı der; sonraki
  açılışta gider. Yazıcı üç denemeden sonra yalnız log'a yazıp bırakıyor.
- **C — gösterildi:** aynı `projects.json`'da iki sunucu — başka bir Colab oturumu, ya da Serve
  hücresi yeniden çalışırken kapanmamış eski sunucu —: her biri kendi kopyasını bütün olarak yazar,
  sonuncu ötekinin eklediklerini siler.
- **D — şüphe:** oturum bittiğinde Drive'ın yerel önbelleğinde kalmış yazmalar; notebook Drive'ın
  `flush_and_unmount`'unu hiç çağırmıyor.
- **E — gösterildi:** 448 okuyamadığı eski bir projeyi her açılışta atlıyor; v9 onu listeliyordu.
- **F — şüphe, kayıp yok:** 12 Ekim 12:16'dan *(`e6bedf8b`)* önce açılmış bir oturum hâlâ v9'u
  çalıştırır, ve v9 v10'da açılan projeleri göstermez.
- **Elendi:** sohbet satırı yazmaları (463, 467) proje satırına dokunmuyor; proje yalnız onaylanan
  Delete'le gidiyor; ekran yalnız Archived sekmesi ve aramayla gizliyor.

**Drive hatasının yutulduğu ya da boş sonuca döndüğü yerler** *(kullanıcının isteği için, aynı
inceleme)*: `projects.json` bulunamazsa boş liste; `store.py`'nin `list_dir`'i olmayan klasörü boş liste
sayıyor; `_into_folder` "bulunamadı" alan her yazmada bütün klasör zincirini yeniden açıyor; yazıcının
düşen yazması yalnız log'da; silmede "bulunamadı" yok sayılıyor; bulunamayan sohbet ve dosya "chat not
found" / "file not found" oluyor; başka her disk hatası ekrana yalnız "HTTP 500" olarak geliyor; sağlık
kontrolü kökü hiç yoklamıyor, ve notebook kökün gerçekten Drive'da olduğuna bakmıyor.

**Kullanıcıya sorulacak ve bakılacak:** kaybolan projelerin hepsi 9 Ekim'den sonra mı açıldı (evetse
A–D). Serve hücresinin log'unda ilk v10 açılışından sonraki bir açılışta *"Moving projects of the old
layout into projects.json"* satırı A'yı gösterir; *"projects.json was not written … [Errno 107]"* B'yi;
*"Old project … was not moved"* E'yi. Drive'da `projects.json`'ın sürüm geçmişi ya da Drive'ın
çöp kutusu eski `projects.json`'ı tutuyor olabilir.

**Kullanıcı baktı, 13 Ekim** *("durmuyorlar baktım muhtmelen mount koptu ama kullanırken bir hata
lamadığım için fark edemedim")*: eski `projects.json` ne sürüm geçmişinde ne çöp kutusunda. Kullanırken
hiçbir hata görülmedi. Bu B'yle bağdaşıyor: kopuk bağlantıda yazmalar Drive'a hiç ulaşmaz, ekran yine
başarılı der — Drive'ın geçmişinde de bu yüzden iz kalmaz. Gösterilmedi; log yok.

## Birden çok proje tek seferde arşivlenecek

*(Kullanıcı, 13 Ekim — "arşivleme için tek tek seçtiriyor bunuda düzeltelim".)* Bugün bir proje,
All projects'te kendi satırının `⋯`'sindeki `Archive`'la arşivleniyor *(v9'un 363'ü)*; birkaç proje
için bu birkaç ayrı basış. **Claude'un anlayışı, henüz onaylanmadı:** All projects'te birden çok proje
seçilir ve tek basışla birlikte arşivlenir. **Ayrıntılar kullanıcıyla konuşulacak:** seçimin ekranda
nasıl göründüğü — tasarımcının mı, Claude'un mu çizeceği —, Unarchive'ın ve Delete'in de toplu olup
olmayacağı, ve `<ad> archived · Undo` satırının birden çok projede ne diyeceği.

## Karakter karışması negatif listeyle düzeltilecek

*(Kullanıcı, 14 Ekim — "backlgoa karakter karışmasının negatif düzeltilmesini ekle".)* Bugün Start a
scenario'nun Step 10'u, Improve'un Step 5'i ve negatif listenin ortak metni *(`prompt.py`)* negatif
listeyi karakterlerin özelliklerinin karışmasına — birinin saçının ötekinde çıkmasına — odaklıyor:
karakterin bir özelliği listeye yazılmaz, onun yerine karşıt etiketler yazılır. **Claude'un anlayışı,
henüz onaylanmadı:** karakter karışmasını negatif listeyle önlemenin bu yolu düzeltilecek. Neyin
yanlış çıktığı ve yerine ne isteneceği bilinmiyor. "Elbiselerde karışıyor" *(2 Ekim)* ve "Saç, göz ve
kıyafet sahneler arasında sabit kalır" *(12 Ekim)* girişleriyle aynı soruna değiyor. **Ayrıntılar
kullanıcıyla konuşulacak.**

## Sahnelere alkol eklenmeyecek

*(Kullanıcı, 14 Ekim — "alkol eklmesini yasakalylaım".)* **Claude'un anlayışı, henüz onaylanmadı:**
ajan sahnelere alkol — kadeh, şişe, içki — eklemez. Kullanıcı açıkça isterse girip girmeyeceği, ve
kuralın yalnız sahnelere mi yoksa negatif listeye de mi yazılacağı bilinmiyor. **Ayrıntılar
kullanıcıyla konuşulacak.**
