# Madde 349 — Sunucunun reddi de hata kartı · uygulama turu

**Kaynak:** [yol haritasının 349'u](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md) (v9-2f);
tasarımın 193'ü. Testler: [test turunun spec'i](2026-09-29-queenagent-m349-ret-karti-testler-design.md).

**Kullanıcıdan gereken:** hiçbir şey.

## Ne değişir

**`ChatScreen.jsx`** — kırmızı `<p className="refused">` gider. `refused` ve `error` aynı kartı
çizer: `Couldn't get a response.`, altında gelen yazı olduğu gibi, ve `Try again`. İkisi birden
doluysa (akışın hatasından sonra bağlantı kopar) tasarımdaki gibi iki kart, önce ret. Kart bir
kez yazılır — `[refused, error]`'dan dolu olanlar üstünden geçilir; ayrı bir bileşen dosyası
açılmaz, çünkü kart yalnız burada çiziliyor.

**`useChat.js`** — reddedilen gönderişin argümanları (`text, skill, mode, model, from`) bir ref'te
tutulur. `retry`, ekranda ret kartı varken (`refused` doluyken) o argümanlarla `send`'i yeniden
çağırır; yoksa bugünkü gibi yazısız `send(null)`. Hangi Try again'in ne göndereceği bu yüzden ret
kartının kendisine bağlı: kart gidince — sonraki gönderiş onu temizler — Try again yine yazısız
sorar. Yeniden gönderilen cümle yine reddedilirse `send` fırlatır; `retry` bunu yutar, çünkü kart
sunucunun yeni yazısıyla zaten duruyor ve cümle ilk retten beri kutuda.

**Başka sohbete geçince ret kartı gider.** Hook, sohbet değişince `error`'u siliyor ama `refused`'ı
silmiyordu (tasarımın `APP-BUGS.md` 3'ü: ret satırı kullanıcıyı izliyor). Satır yalnız bir yazıyken
bu bir görüntü kusuruydu; kart Try again taşıyınca zarar olur — başka sohbette basılan Try again,
reddedilen cümleyi o sohbete yazardı. Bu yüzden `refused` da `error`'la aynı yerde silinir: yükleme
etkisinin iki dalında. Taahhüt edilmiş testlerin dışında kalan tek satır bu; tasarımın o maddedeki
kararıyla da aynı (*"another chat or the draft takes it away"*).

**`workspace.css`** — `.refused` kuralı ve yorumu gider; başka yerde kullanılmıyor.

## Değişmeyenler

- Reddedilen balon yine geri alınır, cümle yine kutuya döner (Composer'ın `catch`'i).
- Akışın hatasındaki Try again yine yazısız sorar; App'in bugünkü testi bunu tutuyor.
- `App.jsx` değişmez: `refused={chat.refused}` ve `onRetry={chat.retry}` zaten veriliyor.
- `dist` derlenmez: koşuyu yöneten Claude birleştirirken derler.

## Nasıl görülür

Dört satır yeşil: queen-agent'ın ön ucu 697. Tarayıcıda: dolu bir sohbette (ya da sunucu kapalıyken)
bir mesaj gönderilince kırmızı satır yerine kahverengi kart, altında sunucunun yazısı; `Try again`
aynı mesajı yeniden gönderir.

Adım adım dökümü [uygulama turunun planında](../plans/2026-09-29-queenagent-m349-ret-karti-uygulama-plan.md).
