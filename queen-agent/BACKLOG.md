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
write that file for you.Answer to …"*. `stream_answer.py`'de roundların sözleri `"".join(said)` ile
birleşiyor. **Gerçek modelle doğrulanmadı** *(kullanıcı, 9 Ekim — "gerçek kullanımda görünen bir problem
yok, bunu kontrol edilmedi diye işaretleyelim")*: QA sahte bir DeepSeek'le gördü; gerçek DeepSeek bir
araç çağırırken aynı cevapta söz söylüyor mu, bilinmiyor. Gerçek kullanımda görülürse ele alınır.

## 448'in taşıma kodu ve eski proje dosyaları silinecek

*(Kullanıcı, 9 Ekim — "kullandıktan sonra sileceğimiz bir sonraki roadmap'te".)* v10'un 448'i eski
projeleri her açılışta bir kerelik `projects.json`'a taşıyor ve eski dosyalara — proje başına
`project.json`, `pinned`, `archived` — dokunmuyor. Kullanıcı taşımanın çalıştığını gördükten sonra bir
sonraki QueenAgent roadmap'inde taşıma kodu ve bu eski dosyalar kalkar.

## Bir sohbette aynı anda iki tur koşabiliyor

*(Claude, 9 Ekim — v10'un 449'unu okuyan reviewer'ın bulduğu; 449'dan önce de vardı.)* Bağlantı kopunca
sunucu bunu ancak akışa bir sonraki yazışında öğreniyor; o arada Try again'e basılırsa aynı sohbette
ikinci bir tur başlıyor. Birinci tur bitince `finally`'si ikincinin Stop'unu ve bekleyen izin kartını
siliyor (`memory_stops.py`, `memory_permissions.py`, `stream_answer.py`): Stop ikinci turun o anki
isteğini kesmiyor, arada verilen Allow kayboluyor. Tünel birinci turu yaşatırsa sohbete iki cevap
yazılıyor. Çare: sohbet başına tek tur — ikinci isteği reddetmek ya da eskisini durdurmak, kullanıcının
seçimi — ve her turun yalnız kendi kaydını silmesi.

## Her turda sohbet dosyası iki kez okunuyor

*(Claude, 9 Ekim — 449'un reviewer'ı.)* Route sohbeti okuyor (`routes.py`'nin `existing`'i), sonra
`stream_answer` aynı dosyayı yeniden okuyor; metinli istekte `append_message` bir kez daha. Route'un
elindeki sohbet `stream_answer`'a verilirse her turda Drive'a bir gidiş-dönüş eksilir.

## Cevap zaten yazılmışken Try again döngüye giriyor

*(Claude, 9 Ekim — 449'un reviewer'ı.)* Bağlantı `done`'dan hemen önce koptuysa ya da tünel turu
yaşattıysa cevap diske yazılmış oluyor; Try again *"this chat has already been answered"* alıyor, kart
yerinde kalıyor ve cevap sohbet yeniden açılana kadar görünmüyor. O dalda kaydı bir kez okumak cevabı
gösterir.

## Cevap bekleyen soru için sonradan Try again yok

*(Claude, 9 Ekim — 449'un reviewer'ı.)* Kopan tur bir şey kaydetmiyor; sayfa yenilenince ya da sohbete
geri gelince soru cevapsız duruyor ve ekranda Try again yok — yalnız yeniden yazmak cevaplatıyor.
Sunucu sorunun cevap beklediğini biliyor (`is_owed_an_answer`).

## Bir frontend testi arada düşüyor

*(Claude, 9 Ekim — Queen Editor v9'un 439'unda görüldü.)* `src/features/workspace/ChatScreen.test.jsx`'in
"a stored answer keeps the calls it made, behind one card" testi bütün suite'te bir koşuda düştü; aynı
gün QA'nın koşusunda da bir test düşmüştü, adı yakalanmadı. Tek başına üç kez ve suite'le bir kez
geçti. Makine yükteyken vitest'in 5000 ms'lik süresini aşıyor olabilir — sebep gösterilmedi.
