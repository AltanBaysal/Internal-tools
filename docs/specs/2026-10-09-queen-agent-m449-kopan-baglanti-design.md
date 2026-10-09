# Madde 449 · Kopan bağlantıdan sonra Try again — tasarım

**Tarih:** 9 Ekim 2026 · **Madde:** [v10 yol haritası](../roadmaps/2026-10-05-queen-agent-v10-roadmap.md),
449 · **Dal:** `feat/queenagent-v10`, ana klasörde · **Kurallar:**
[FOUNDATION](../../queen-agent/FOUNDATION.md) · [CODE-STANDARD](../../queen-agent/CODE-STANDARD.md) ·
**Öncesi:** [440](2026-10-09-queen-agent-m440-kara-kutu-design.md) — kayıttaki başarısız cevabın Try
again'i; Madde 349 — reddedilen cümleyi yazı kutusunun yeniden göndermesi.

## Ne, neden

v10'u deneyen QA'nın bulduğu, 440'tan önce de vardı *(kullanıcı, 9 Ekim — "gerisi doğru … onları da
bu roadmap'te çöz")*: tur sürerken bağlantı koparsa *"network error"* kartı çıkıyor, ve kartın Try
again'i soruyu metniyle yeniden gönderiyor. Sunucu soruyu kopmadan önce kaydetmişti; sohbette soru alt
alta iki kez duruyor.

Bugün, metinli bir gönderimde:

- Sunucu (`routes.py`'nin `post_message`'ı) soruyu `append_message`'le **cevabın durum satırından
  önce** diske yazar; akışın ilk olayı `chat`'tir, modelden önce, sohbetin id'siyle.
- Akış ortada koparsa `reader.read()` fırlatır, ve `useChat.js`'in `catch`'i bunu *"daha bir bayt
  gelmeden reddedildi"* gibi okur: balonu ekrandan çıkarır, kartı `refused` olarak kurar,
  `refusedReply`'ı doğru yapar ve hatayı yazı kutusuna fırlatır — kutu cümleyi geri alır. Kartın Try
  again'i (`retry`) o zaman kutuyu gönderir: metinli ikinci bir istek, ve sunucu soruyu ikinci kez
  yazar.

## Olacak

### 1 · Sorunun sunucuya ulaştığını söyleyen tek işaret: `chat` olayı

`send`'in içinde yerel bir `reached` — `chat` olayı gelince doğru olur. O olay geldiyse soru diskte:
sunucu onu soruyu yazdıktan sonra, ilk bayt olarak gönderiyor.

- **Neden `chat` olayı, `response.ok` değil:** ikisi de *"soru yazıldı"* der, ama taslakta doğan
  sohbetin id'sini yalnız `chat` olayı taşır, ve sözsüz Try again o id'ye gider (`{chat, mode}`).
  `useChat` o olayı zaten okuyor; `sse.js` değişmez, sunucu değişmez.
- **Kural tarayıcıya geçmiyor** (FOUNDATION, Karar 4): neyin cevaplanacağına sunucu karar verir
  (`is_owed_an_answer`); tarayıcı yalnız kendi gönderdiği isteğin nereye kadar gittiğini biliyor, ve
  hangi isteği yeniden göndereceğini o bilgiyle seçiyor — bugün de `refused`/`error` ayrımıyla yaptığı.

### 2 · Ulaştıysa — `catch`'in yeni kolu

- **Balon kalır:** soru diskte, ekran onu geri almaz.
- **Kart `error`'dur, `refused` değil:** *"gelmeyen bir cevap"*, Madde 349'un ayrımı. Böylece `retry`
  kutuya gitmez, `send(null, "", mode)` gönderir — sözsüz, oturumun moduyla.
- **Kutu cümleyi geri almaz:** hata fırlatılmaz. Cümle diskte; kutuda da kalsaydı, bir Enter onu
  ikinci kez yazardı.
- **Akışın kendi söylediği hata kalır:** kopmadan önce bir `error` olayı geldiyse kartın sözü odur
  (`setError((current) => current ?? failure.message)`), kayıt okumasındaki gibi — turun gerçek
  hatası kopuşun sözüyle örtülmez.
- Kart, bugünkü gibi yalnız turun koştuğu sohbette durur (`target === live.current`).

**Try again'e basınca:** sunucu açık satırın son mesajının kullanıcınınki olduğunu görür ve soruyu
cevaplar; ilk olayda (`chat`) kayıt yeniden okunur — 440'ın sözsüz gönderim için yazdığı kod —, ve
ekrandaki balon diskteki soruyla yer değiştirir; tur bitince cevap kayıtla gelir. Sohbette soru bir kez.

### 3 · Ulaşmadıysa — bugünkü gibi

`chat` olayı gelmeden düşen her şey — `fetch`'in reddi (*"Failed to fetch"*), sunucunun durum koduyla
reddi — bugünkü yoldan gider: balon çıkar, kart `refused`, cümle kutuya döner, Try again kutuyu
gönderir.

## Maliyet

Disk sunucunun Drive'ı; her satır bir gidiş-dönüş. Proje, sohbet ve dosya sayısıyla büyüyen bir şey
yok — hepsi O(1).

- **Kopuşun kendisi:** istek yok, disk yok. `catch` yalnız belleği değiştirir.
- **Kopuştan sonra Try again** (yeni yol): 1 POST — sunucuda sohbet dosyası 2 okuma (`post_message`'in
  `existing`'i ve `stream_answer`'ın kendi `get`'i, bugün de böyle), başarısız cevap yoksa
  `drop_failed_answer` yazmaz, turun kendi işleri, sonda cevap için 1 okuma + 1 yazma (ve kuyruktaki
  `projects.json` satırı) — ve 2 GET, her biri 1 okuma: `chat` olayındaki kayıt ve turun sonundaki.
- **Bugünkü yolla farkı**, tarayıcının GET'leri de sayılınca: yeni yol 5 okuma, 1 yazma; bugünkü
  metinli POST 5 okuma, 2 yazma — `existing`, `append_message`'in soruyu yeniden yazarken okuması ve
  yazması, `stream_answer`'ın `get`'i, sondaki cevabın okuması ve yazması, turun sonundaki GET. Okuma
  sayısı aynı (yeni yolda `append_message`'in okumasının yerini `chat` olayındaki GET alıyor), bir
  yazma eksik.

## Sınırlar

- **Bilinemeyen pencere:** istek sunucuya ulaşır, soru yazılır, ama bağlantı ilk olaydan önce koparsa
  — Drive'da `append_message`'in yazması sürerken, ya da durum satırıyla ilk olay arasında — tarayıcı
  sorunun yazıldığını bilemez, bunu ulaşmamış sayar, ve Try again soruyu yeniden gönderir. Kapatmak,
  sunucunun tanıyacağı bir anahtar ister (mesajla diske yazılan bir gönderim id'si); bu, kayıtta
  tutulanı değiştirir ve bu maddenin işi değil.
- **Sunucuda süren tur:** sunucu kopuşu ancak bir sonraki yazışında öğrenir; model isteği sürerken
  tur sürer. Try again o arada basılırsa aynı sohbette ikinci bir tur başlar, ve sunucu bir sohbette tek
  tur kuralı tutmuyor. Kopan tur cevabını yazmadan bitmişse (çoğunlukla: sonraki `Progress`'te düşer)
  sohbet tek cevapla kalır; tünel bağlantıyı sunucu tarafında açık tutarsa ilk tur cevabını yazar, ve
  sonra basılan Try again *"this chat has already been answered"* ile reddedilir — cevap sohbet
  yeniden açılınca görünür. Bugün de böyle; bu madde değiştirmiyor.
- **Taslakta kısa bir yarış:** kopuş, `chat` olayından birkaç milisaniye sonra — React adresi doğan
  sohbete geçiren çizimi yapmadan önce, ya da o çizimle onun etkisi arasında — işlenirse kart hiç
  görünmez (`target` doğan sohbet, `live` hâlâ taslak), ve kutu boştur; soru diskte kalır, sohbet
  yeniden açılınca görünür. Seyrek; düzeltmek doğum korumasını (`streamingInto`, Madde 88/106) da
  değiştirmeyi ister, ve bu maddede değişmez.
- Arka uçta yalnız `routes.py`'ye bir yorum: tarayıcı, sorunun yanıttan önce yazılmasına ve `chat`'in
  ilk olay olmasına dayanıyor. `sse.js`, `ChatScreen.jsx`, `Composer.jsx` değişmez. queen-editor'e
  dokunulmaz.

## Değişen dosyalar

- `queen-agent/frontend/src/features/workspace/useChat.js` — `reached`; `catch`'in iki kolu.
- `queen-agent/backend/features/workspace/presentation/routes.py` — yalnız yorum.
- `queen-agent/frontend/src/App.test.jsx` — testler; `stubTurn` sırayla birden çok akış alır.
- `queen-agent/frontend/dist` — yeniden derlenir.

## Testler (`App.test.jsx`)

- İlk olaydan sonra kopan akış: soru sohbette bir kez durur, kart kopuşun sözüyle, kutu boş; Try again
  sözsüz ve modla gider (`{chat: "c1", mode: "edit"}`), soru yine bir kez, ve cevap gelir.
- Taslakta ilk olaydan sonra kopan akış: adres doğan sohbete geçer, Try again o sohbete sözsüz gider.
- Bir düzenleme (`from`) ilk olaydan sonra koparsa: düzeltilmiş soru bir kez, eskisinin yerinde;
  Try again sözsüz gider. Bugün balon çıkıyor ve kart `refused`'du.
- Kopmadan önce akışın söylediği `error` kartta kalır, kopuşun sözü onun yerine geçmez.
- İlk olaydan önce düşen istek (`fetch` reddi): balon çıkar, cümle kutuya döner, Try again cümleyi
  metniyle gönderir. Durum koduyla reddin testleri (Madde 349) olduğu gibi kalır.

## Bitti sayılır

- Yukarıdaki testler yeşil, dört suite yeşil (`test_dist_is_committed` commit'e kadar kırmızı olabilir),
  `dist` yeniden derlenmiş.
- Kullanıcının denemesinde: tur ortasında bağlantı kopunca Try again'e basılınca soru sohbette bir kez
  duruyor ve cevaplanıyor; soru hiç gitmeden kopan bağlantıda Try again soruyu gönderiyor.
