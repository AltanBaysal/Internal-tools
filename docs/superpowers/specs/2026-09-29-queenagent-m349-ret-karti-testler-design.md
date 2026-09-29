# Madde 349 — Sunucunun reddi de hata kartı · test turu

**Kaynak:** [yol haritasının 349'u](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md) (v9-2f);
tasarımcının v3 roadmap'inin 193'ü — *"refused ve error'un farkı ne abi, aynı yapalım, hata ile aynı
şeyi yapalım"* (kullanıcı, 29 Eylül). Tasarımda (`chat/index.html`, `turnParts`) ret de
`failureCard`'ı çiziyor; kırmızı `.refused` satırı yok.

**Kullanıcıdan gereken:** hiçbir şey.

## Bugün

Sunucu bir mesajı akış başlamadan reddedince (dolu sohbet, bulunmayan sohbet ya da proje, boş
cümle, cevaplanmış sohbette Try again) ya da istek hiç ulaşamayınca, `useChat` `refused`'ı tutar ve
`ChatScreen` onu kırmızı bir `<p className="refused">` olarak çizer — kart yok, `Try again` yok.
Akışın içinden gelen hata (`error`, ör. sağlayıcının 401'i) kahverengi kartı çizer.

## Ne kanıtlanacak

1. **Ret de kahverengi kart.** `refused` gelince ekranda `Couldn't get a response.`, altında
   sunucunun kendi yazısı (kartın `failure__detail`'inde, geldiği gibi) ve `Try again` var;
   `.refused` satırı yok.
2. **Try again, reddedilen cevabı yeniden gönderir — kutunun gönderişiyle.** Kart *"cevap
   alınamadı"* diyor, ve reddedilen bir mesajda cevabı alınacak şey o mesaj. Tasarımdaki gibi yazısız
   istek (`send(null)`) göndermek, diskte bekleyen soru yokken sunucudan *"this chat has already been
   answered"* ya da taslakta *"there is nothing here to answer"* döndürür — bağlantı kopup gelince
   bile mesaj gitmez. **Cümlenin tek sahibi kutu** *(koordinatör, 29 Eylül — ilk geçişte hem kutu hem
   Try again cümleyi tutuyordu, ve kabul edilen bir Try again'den sonra cümle kutuda kalıp ikinci kez
   gönderilebiliyordu)*: ret cümleyi kutuya geri verir (FOUNDATION'ın birinci ilkesi — kalıcı bir
   retten sonra kullanıcı onu kutudan alıp yeni sohbete taşır), ve Try again kutunun Send'iyle aynı
   iştir: kutudaki cümle gider, kutu boşalır; yeniden reddedilirse cümle kutuya döner ve kart
   sunucunun yeni yazısıyla kalır.
3. **Ret, sonraki gönderişe taşınmaz.** Reddedilen mesajdan sonra başka bir mesaj gönderilir ve onun
   cevabı akışta hata verirse, Try again artık yazısız isteği gönderir — eski ret cümlesini değil.
4. **Kabul edilen Try again'den sonra kutu boş.** Cümle bir kez gider, ve geride kalmaz.
5. **Ret kartı söylendiği sohbette kalır.** Başka bir sohbete ya da taslağa geçince kart gider:
   Try again'i kutuyu gönderir, ve orada basılsa cümleyi o sohbete yazardı. Tasarımın da kararı
   (`APP-BUGS.md` 3 — *"another chat or the draft takes it away"*). İlk geçişin uygulaması bunu
   testsiz yazmıştı *(koordinatör, 29 Eylül: kod taahhüt edilmiş testlerin anlattığıdır)*; o iki satır
   bu turun kırmızı commit'inde çıkarılır ki testin kırmızısı görülsün, ve uygulama turunda geri
   gelir.

## Testler ne tutar, ne tutmaz

**`ChatScreen.test.jsx`** — *"a message that was never sent is not told as an answer that never
came"* bugünkü davranışı anlatıyor; yerine: *"a refused message draws the failure card with the
server's words"* — `refused` ile kart, sunucunun cümlesi `failure__detail`'de, `Try again` `onRetry`'ı
çağırıyor, `.refused` yok.

**`App.test.jsx`:**

- *"the user bubble shows before the server answers, and a refusal hands the words back"* — ret
  sonrası `Couldn't get a response.` artık var; `.refused` yok. Balon gidiyor, cümle kutuya dönüyor —
  bunlar olduğu gibi kalır.
- Yeni: *"Try again after a refusal sends the refused message again"* — iki POST da reddedilir;
  ikincinin gövdesi birincininkiyle aynı. Yakalanmayan bir ret (unhandled rejection) vitest'i
  kırmızı yapar, bu yüzden test Try again'in reddi de yuttuğunu tutar.
- Yeni: *"a refusal is not carried into a later send's Try again"* — ret, sonra kabul edilen ama
  akışta hata veren bir mesaj, sonra Try again: üçüncü POST'un gövdesi `{ chat: "c1" }`.

**İkinci geçiş (koordinatörün iki notu), `App.test.jsx`:**

- `stubRefusingChat` iki sohbet taşır (`Hi` ve `Other`) ve kenar çubuğunun satırlarını verir.
- Yeni: *"a sentence sent again by Try again does not stay in the box"* — ret, kutuda `hello`;
  Try again kabul edilir: ikinci POST `hello`'yu taşır, kart gider, kutu boş.
- Yeni: *"a refusal's card stays in the chat it was said in"* — ret, sonra kenar çubuğundan `Other`:
  kart yok.
- Yeni: *"a refusal's card does not follow the user into the draft"* — ret, sonra `New chat`: kart
  yok.
- Reddedilen bir düzeltmenin (edit) Try again'i için test yok: düzeltmenin cümlesi retten sonra
  hiçbir yerde durmuyor (`APP-BUGS.md` 7, bu maddenin değil), ve Try again orada da yazısız sorar —
  ilk geçişten önceki davranış.

**Tutmaz:** `workspace.css`'teki `.refused` kuralının yokluğu — m341'deki gibi, yokluğu kilitlemek
ölçü değil iz olur; ekranda `.refused` olmadığını ChatScreen'in ve App'in testleri tutuyor.
Proje ekranından gönderilen mesajın reddi — bugün de orada çizilmiyor, bu madde ona dokunmuyor.

## Bu turda yazılmayanlar

- `ChatScreen.jsx`, `useChat.js` ve `workspace.css` değişmez; uygulama turunda.
- `dist` derlenmez: koşuyu yöneten Claude birleştirirken derler.

## Nasıl görülür

CLAUDE.md'deki dört satır. `npm test --prefix queen-agent/frontend` kırmızı verir: ChatScreen'in yeni
testi ve App'in üç testi (ikisi yeni, biri güncellendi) — bugün ret kırmızı satır, Try again yok.
Üçüncü yeni test (*"a refusal is not carried…"*) bugün de geçebilir: ret satırı Try again sunmadığı
için akış hatasının kartındaki Try again yazısız gider; bu test uygulamanın getireceği hatırlamayı
kilitler. Öteki süitler yeşil. Kırmızı hâliyle commit edilir.

İkinci geçişte: ön uç 700 test, üç kırmızı — üç yeni test. Kutu testi kırmızı, çünkü ilk geçişin
Try again'i cümleyi hook'tan yeniden gönderiyor ve kutu dolu kalıyor; sohbet ve taslak testleri
kırmızı, çünkü `useChat`'in yükleme etkisindeki iki `setRefused(null)` bu commit'te çıkarılıyor.

Adım adım dökümü [test turunun planında](../plans/2026-09-29-queenagent-m349-ret-karti-testler-plan.md).
