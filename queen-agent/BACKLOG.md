# Backlog — QueenAgent

Gerçek ama henüz bir koşuya bağlanmamış işler. Sırası gelince buradan çıkar, o koşunun yol
haritasına girer.

## Akış sadeleşecek, yük ajana bırakılacak

*(Kullanıcı, 28 Eylül — "queen agentın agenti deepsek v1 flash senin gibi oldukça güçlü bir model biz
bu akışı nasıl daha basitleştiriz ve agenta bırakırız yükü", "komplesliği azaltlaım ve agenta
özgürlük sunalım", "abi bunuda backloga alalım yapyalım ilk yöntemden gidleim sonra farkıda görmüş
oluruz hem".)* **Ayrıntılar kullanıcıyla konuşulacak.**

## Ajanın dosya araçları Claude Code'unkiler gibi olacak

*(Kullanıcı, 20 Ekim — "grep ve read_file gibi araçları geliştir"; 28 Eylül — "büyük dosyalarının
hepsini de okumak zorunda kalmasın gerekli kısımlarını okusun".)* **v11'de v11-3 olarak hizalandı,
koşulmadan backlog'a döndü** *(kullanıcı, 22 Ekim — "backloga al")*; hizalanan hâli
[v11'in](../docs/roadmaps/2026-10-20-queen-agent-v11-roadmap.md) geçmişinde, 22 Ekim'den önceki
commit'lerde.

**Kararlaşanlar:** önce bir agent Claude Code'un araçlarını ve nasıl çalıştıklarını Türkçe bir belgede
listeler, ana agent kontrol eder; sonra seçilen araçların tasarımı — Read'in `offset`/`limit`'i, Grep'in
arama ve çevre satırları gibi — QueenAgent'ın ajanına kopyalanır. Bugünkü yapılı araçlar
(`set_character`, `add_frame`, …) kalır *(kullanıcı — "set character falan silinmez")*. **Bugün**
`read_file` dosyanın tamamını döner, grep diye bir araç yok
*([read_file.py](backend/features/workspace/domain/usecases/read_file.py))*. Araçların modele giden
açıklamaları `prompt.py`'de *(`READ_FILE`, `THE_FILES_NAME`)*.

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

## 448'in eski proje dosyaları silinecek

*(Kullanıcı, 9 Ekim — "kullandıktan sonra sileceğimiz bir sonraki roadmap'te".)* v10'un 448'i eski
projeleri `projects.json`'a taşıdı ve eski dosyalara — proje başına `project.json`, `pinned`,
`archived` — dokunmadı. **Taşıma kodu** 490'la *(v11-1)* silindi *(kullanıcı, 20 Ekim — "sil")*;
burada yalnız bu eski dosyalar kalıyor, Drive'da silinmeyi bekliyorlar.

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

## Birden çok proje tek seferde arşivlenecek

*(Kullanıcı, 13 Ekim — "arşivleme için tek tek seçtiriyor bunuda düzeltelim".)* Bugün bir proje,
All projects'te kendi satırının `⋯`'sindeki `Archive`'la arşivleniyor *(v9'un 363'ü)*; birkaç proje
için bu birkaç ayrı basış. **Claude'un anlayışı, henüz onaylanmadı:** All projects'te birden çok proje
seçilir ve tek basışla birlikte arşivlenir. **Ayrıntılar kullanıcıyla konuşulacak:** seçimin ekranda
nasıl göründüğü — tasarımcının mı, Claude'un mu çizeceği —, Unarchive'ın ve Delete'in de toplu olup
olmayacağı, ve `<ad> archived · Undo` satırının birden çok projede ne diyeceği.

## Uygulamanın mimari çizimi, ve yapıyı değiştiren işte önce çizim

*(Kullanıcı, 20 Ekim — "mimari diagram blok diagram uygulama için aslında bundan olsa çpk işime
yarardı kodu okumadan anlayabilirdim yada önce sende burda tasarlar sonra kodunu yazardın";
"şimdilik ypaamylaım backlgoa at".)* **Claude'un anlayışı, henüz onaylanmadı:** QueenAgent'ın bir
mimari çizimi olur — kutularla, düz metin: ekran, backend'in özellikleri, servisler, dış servisler
(Drive, DeepSeek) —, kod okunmadan anlaşılır. Çizim kutu seviyesinde kalır, fonksiyona inmez, ve yapıyı
değiştiren bir iş onu aynı commit'te günceller. Yapıyı değiştiren bir işin spec'i bir "bugün / sonra"
çizimiyle başlar ve kod, kullanıcı çizimi onayladıktan sonra yazılır. Queen Editor'ün backlog'unda
aynısı var; "önce çizim" kuralı iki aracın ortak kuralı olacağı için CLAUDE.md'ye girer, önce
kullanıcıya gösterilerek. **Ayrıntılar kullanıcıyla konuşulacak.**

## Veri ve kayıt akışı baştan tasarlanacak

*(Kullanıcı, 20 Ekim — "abi burası çok karmaşık ve bir şewy analayamıyorum hiç contexti olamayn 2
agente bunu sıfırdan tasarlattıralım basit olmalı solid olmalı drive istek sayısnı minimzie etmeli";
"doylarda agnetın güncellendiği an güncellenmelş"; sonra — "yada abi bu kadar büyük bir işe
girmeyelin şuanlık".)* Şimdilik yalnız küçük düzeltme yapıldı:
490, [v11-1](../docs/roadmaps/2026-10-20-queen-agent-v11-roadmap.md) — bağlantı kontrolü ve 448'in silinmesi.
**490'dan kalanlar** *(coder'ı ve reviewer'ı buldu, 22 Ekim)*: kök okunur ama `projects.json`
yanlışlıkla "bulunamadı" derse açılış hâlâ boş başlar; notebook'un CONFIG'i kökün gerçekten Drive'da
olduğuna bakmıyor; `/api/health` bağlantıya bakmıyor; proje oluşturma, ad değiştirme, sabitleme ve
arşiv bellekten cevap veriyor, Drive kopukken yazmaları yalnız log'a düşüyor; aynı oturumda Drive
yeniden bağlanınca uygulama Serve yeniden çalışana kadar her işlemi reddediyor, ve cümlesi bunu
söylemiyor.

**Kullanıcının Claude'la 20 Ekim'de konuştuğu istekler:**

1. Basit, SOLID, gereksiz parçası yok.
2. Drive'a tek bir yer ulaşır; başka hiçbir şey Drive'ı ya da yolları bilmez.
3. Gereksiz Drive isteği yok, ama gereken bir istek sayıyı düşürmek için kesilmez *("ama gerçekten
   gereken bir isteği de minimize etmek için azaltmasın gereksiz istek atılmasın yani")*. Her tasarım
   her işlemin Drive isteklerini ve her birinin neden gerektiğini listeler.
4. Ekran canlı: ajanın değiştirdiği dosya hemen görünür, F5 gerekmez. Stream ve hook yalnız örnekti;
   tasarımcılar serbest.
5. Ajan hiçbir zaman Drive'ı beklemez.
6. Değişiklikler hemen görünür (optimistik) — elle yapılanlar da: ad değiştirme, arşivleme, silme,
   gönderme *("bunlar direkt görünsün optimistik olsun kayıt edilemezse hata ile eski haline
   dönsün")*. Kayıt düşerse gerçek hatayla görünür bir uyarı çıkar — biçimi tasarımın kararı, snackbar
   ya da başka —, ve ekran son kaydedilmiş hâline döner.
7. Ekranda "kaydedildi" yok *("userın ekranda kaydedildi görmesine gerek yok")*.
8. Drive'daki sorun bir şey okunurken ya da yazılırken, ya da sayfa açılırken / F5'te fark edilir, bir
   zamanlayıcıyla değil. Ajan turu sürerken en geç turun kaydında *("tur sonunda fark etsin sorun
   yok")*. O zaman ajan durur ve uyarı görünür.
9. Bağlantı yokken Colab'ın kendi diskine hiçbir şey yazılmaz.
10. Drive'a ulaşılamazsa hata; hiçbir zaman boş bir proje listesi.
11. Düşen bir kayıt kaydedilmemiş işi bırakır: tekrar dene düğmesi yok, kendiliğinden yeniden deneme
    yok *("user bu arkadaki logiği bilmez karıştırma o yüzden kendi de otomatik kaydetme kaybolsun
    şimdilik")*.
12. Oturum ölürse kaydedilmemiş iş kaybolabilir *("sıkıntı yok")*.
13. Bağlantı dosyayı kabul ettikten sonraki birkaç saniyelik Google yüklemesi kabul edildi.
14. Drive API'si yok; Colab'ın bağlantısı.
15. Bugünkü veri kayıpsız taşınır.
16. Aynı Drive'da iki sunucu: olduğu gibi kalır *("şu an sorunsuz çalışıyor böyle kalsın")*.
17. Her tasarım bir "Colab'da nasıl denenir" bölümü yazar — ör. ajan çalışırken Drive'ın bağlantısı
    kesilince ne görülür. QA en sonda dener.

**Tasarım** bağlamı olmayan iki mimarın, her birinin ayrı ayrı işi; ondan önce kullanıcı istekleri bir
kez daha hizalar.
