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

## SDXL prompting belgesi yazılacak

*(Kullanıcı, 29 Eylül — "şuan sdxle özel instructıonlar çok dağılmış durumda farktettiysen toolara vs
bence sdxl prompting diye güzel bir dokuman yazalım ai onu okusu sdxl skill de olur karmaşıklı
azaltalım ztenc cahced yaparsak bunu o kadar malşyetide olmaz"; 29 Eylül — "sdxl yeteneklere kesinlik
ayna ekleme kısmınıda koyalım bunda yazar msıının bu taska çünkü aynayı çok kötü ekliyor kalite
düşünyor user özellike sorarsa eklensin", "ayna eklenmemesi olucak".)* **Ayrıntılar kullanıcıyla konuşulacak.**

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

## Bağlantı koptuktan sonra Try again soruyu iki kez yazıyor

*(Claude, 9 Ekim — v10'un 440'ını deneyen QA'da görüldü; 440'tan önce de vardı.)* Tur sürerken sunucu
kapandı, ekranda *"network error"* kartı çıktı, ve kartın Try again'i soruyu metniyle yeniden gönderdi:
kayıtta soru iki kez duruyor. `useChat.js`'in `catch`'i, sunucu soruyu yazdıktan sonra kopan bir akışı
"daha bir bayt gelmeden reddedildi" gibi okuyup `refusedReply`'i kuruyor. Mod doğru gidiyordu.

## Arşivlenirken Unarchive'a basılırsa sıra karışabilir

*(Claude, 9 Ekim — v10'un 441'ini okuyan reviewer'da görüldü; Undo'da da vardı.)* Arşivin cevabı
gelmeden Unarchive'a basılırsa ekran projeyi arşivin kendi cevabı gelene kadar arşivli çizer, Unarchive
daha önce cevaplasa bile. Sunucu iki PATCH'i aynı anda işlerse ikisi ters sırayla da yazılabilir. Pencere
arşivleme sürdükçe açık — arşivlemenin yavaşlığı v10'un 446'sında araştırılıyor.

## Unarchive'dan sonra odak kayboluyor

*(Claude, 9 Ekim — v10'un 441'ini deneyen QA'da görüldü.)* Archived sekmesinde Unarchive'a basınca
basılan ⋯ satırıyla gider ve odak sayfanın gövdesine düşer. 441'de Archive'dan sonra odak sıradaki
satırın ⋯'sine geçiyor; Unarchive'da aynısı istenirse buradan.

## Dar ekranda dosya paneli sohbeti kapatıyor

*(Claude, 9 Ekim — v10'un 442'sini deneyen QA'da görüldü; 442'den gelmiyor, main'de olup olmadığına
bakılmadı.)* 400 px genişlikte kenar çubuğu kapalıyken Project files paneli sohbetin çoğunu örtüyor;
kenar çubuğu açılınca panel ince bir şerit oluyor, ama hata kartının yazısı harf harf alt satıra
kayıyor. Ekran görüntüleri `tmp/qa442-narrow-folded.png` ve `tmp/qa442-narrow-open.png`'de.

## Var olan bir sohbette konuşunca proje listesinin sırası güncellenmiyor

*(Claude, 9 Ekim — v10'un 443'ünü deneyen QA'da görüldü; bütün projelerde, 443'ten gelmiyor.)* Var olan
bir sohbette mesaj gönderip projeden çıkınca All projects proje satırını eski yerinde ve eski
zamanıyla gösteriyor; sunucu onu çoktan en yeni sayıyor. `App.jsx` listeyi yalnız sohbet doğunca ya da
dosyalar değişince yeniden okuyor, var olan sohbette tur bitince değil.

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
birleşiyor.

## Bir frontend testi arada düşüyor

*(Claude, 9 Ekim — Queen Editor v9'un 439'unda görüldü.)* `src/features/workspace/ChatScreen.test.jsx`'in
"a stored answer keeps the calls it made, behind one card" testi bütün suite'te bir koşuda düştü; aynı
gün QA'nın koşusunda da bir test düşmüştü, adı yakalanmadı. Tek başına üç kez ve suite'le bir kez
geçti. Makine yükteyken vitest'in 5000 ms'lik süresini aşıyor olabilir — sebep gösterilmedi.
