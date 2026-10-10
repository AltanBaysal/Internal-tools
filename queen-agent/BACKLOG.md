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

## Bir frontend testi arada düşüyor

*(Claude, 9 Ekim — Queen Editor v9'un 439'unda görüldü.)* `src/features/workspace/ChatScreen.test.jsx`'in
"a stored answer keeps the calls it made, behind one card" testi bütün suite'te bir koşuda düştü; aynı
gün QA'nın koşusunda da bir test düşmüştü, adı yakalanmadı. Tek başına üç kez ve suite'le bir kez
geçti. Makine yükteyken vitest'in 5000 ms'lik süresini aşıyor olabilir — sebep gösterilmedi.
