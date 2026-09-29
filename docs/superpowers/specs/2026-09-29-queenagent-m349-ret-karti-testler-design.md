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
2. **Try again reddedileni yeniden gönderir.** Karar (teknik, benim): reddedilen istek aynen
   yeniden gider — bir mesaj reddedildiyse aynı cümle, aynı skill, mode ve model, bir düzeltmeyse
   aynı `from` ile; reddedilen bir Try again'se yine yazısız istek. Neden: kart *"cevap alınamadı"*
   diyor, ve reddedilen bir mesajda cevabı alınacak şey o mesaj. Tasarımdaki gibi yazısız istek
   (`send(null)`) göndermek, diskte bekleyen soru yokken sunucudan *"this chat has already been
   answered"* ya da taslakta *"there is nothing here to answer"* döndürür — bağlantı kopup gelince
   bile mesaj gitmez. Yeniden reddedilirse kart sunucunun yeni yazısıyla kalır.
3. **Ret, sonraki gönderişe taşınmaz.** Reddedilen mesajdan sonra başka bir mesaj gönderilir ve onun
   cevabı akışta hata verirse, Try again artık yazısız isteği gönderir — eski ret cümlesini değil.
4. **Cümle yine kutuya döner** (FOUNDATION'ın birinci ilkesi): mevcut test kalır. Kalıcı bir ret
   (dolu sohbet) karşısında kullanıcı cümlesini kutudan alıp yeni sohbete taşıyabilir. Bilinen bir
   sonuç: Try again kabul edilirse cümle kutuda da durur; kullanıcı onu siler. Kutuyu dışarıdan
   boşaltmak Composer'ın taslağına ikinci bir sahip ekler — bu madde bunu yapmaz.

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

Adım adım dökümü [test turunun planında](../plans/2026-09-29-queenagent-m349-ret-karti-testler-plan.md).
