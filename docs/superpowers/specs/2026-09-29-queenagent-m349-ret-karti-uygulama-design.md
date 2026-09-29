# Madde 349 — Sunucunun reddi de hata kartı · uygulama turu

**Kaynak:** [yol haritasının 349'u](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md) (v9-2f);
tasarımın 193'ü. Testler: [test turunun spec'i](2026-09-29-queenagent-m349-ret-karti-testler-design.md).

**Kullanıcıdan gereken:** hiçbir şey.

## Ne değişir

**`ChatScreen.jsx`** — kırmızı `<p className="refused">` gider. `refused` ve `error` aynı kartı
çizer: `Couldn't get a response.`, altında gelen yazı olduğu gibi, ve `Try again`. İkisi birden
doluysa (akışın hatasından sonra bağlantı kopar) tasarımdaki gibi iki kart, önce ret. Kart bir
kez yazılır — `[refused, error]`'dan dolu olanlar üstünden geçilir; ayrı bir bileşen dosyası
açılmaz, çünkü kart yalnız burada çiziliyor. Kartın Try again'i `onRetry`'a kutuyu gönderen bir
fonksiyon verir: `onRetry(() => box.current.submit())`.

**Reddedilen cümlenin tek sahibi kutu** *(ikinci geçiş, koordinatör, 29 Eylül)*. İlk geçişte hook
reddedilen isteğin argümanlarını tutuyor ve Try again onları yeniden gönderiyordu; ret de cümleyi
kutuya geri verdiği için cümlenin iki sahibi vardı, ve kabul edilen bir Try again'den sonra cümle
kutuda kalıp ikinci kez gönderilebiliyordu. İki yol tartıldı:

- *Ret cümleyi kutuya geri vermez, kartın Try again'i onu gönderir.* Kalıcı bir retten (dolu sohbet,
  silinmiş sohbet) sonra cümle hiçbir yerde görünmez; kullanıcı onu alıp yeni sohbete taşıyamaz, ve
  sohbet değişince kart gidince cümle de gider — FOUNDATION'ın birinci ilkesine aykırı.
- **Try again, kutunun Send'iyle aynı iştir** — seçilen. Kutu zaten cümleyi tutuyor, boşaltıyor,
  gönderiyor ve reddedilirse geri alıyor; Try again bu işi ikinci kez yazmaz, onu çağırır. Kutu
  kalıcı bir retten sonra da cümleyi tutar, ve kullanıcı cümleyi değiştirdiyse Try again değişmiş
  hâlini gönderir — kutuda ne varsa o. Skill, mode ve model o anda seçili olanlardır, tasarımın da
  istediği gibi (`APP-BUGS.md` 5: *"Try again runs in the mode in force"*).

**`Composer.jsx`** — `forwardRef` ile sarılır ve `useImperativeHandle` ile kendi `submit`'ini verir.
Taslağın sahibi yine yalnız Composer; dışarıdan yalnız "şimdi gönder" denebilir. Taslağı yukarı
taşımak (kontrollü bileşen) ProjectScreen'in kutusunu da değiştirirdi — daha çok parça.

**`useChat.js`** — reddedilen isteğin argümanları yerine tek bir bilgi tutulur: ret bir cevaba mı
(yazılı ve `from`'suz) geldi. `retry(sendBox)`: ekranda ret varken ve ret bir cevabınsa
`sendBox()`; yoksa bugünkü gibi yazısız `send(null)`. Yazısız yol şunları kapsar: akışın hatası;
reddedilen bir Try again — yazısız istek aynen yeniden gider; ve reddedilen bir düzeltme — onun
cümlesi retten sonra hiçbir yerde tutulmuyor (`APP-BUGS.md` 7, bu maddenin değil), hook'ta da
tutulmaz, çünkü tutulursa ikinci sahip yine doğar. `send(null)` fırlatmaz, kutunun `submit`'i
kendi reddini yakalar; `retry`'nin artık `catch`'e ihtiyacı yok.

**Başka sohbete ya da taslağa geçince ret kartı gider.** Yükleme etkisinin iki dalında `setError`'un
yanında `setRefused(null)`: kartın Try again'i kutuyu gönderir, ve başka sohbette basılsa cümleyi o
sohbete yazardı. Tasarımın da kararı (`APP-BUGS.md` 3). İkinci geçişin testleri tutuyor.

**`workspace.css`** — `.refused` kuralı ve yorumu gider; başka yerde kullanılmıyor.

## Değişmeyenler

- Reddedilen balon yine geri alınır, cümle yine kutuya döner (Composer'ın `catch`'i).
- Akışın hatasındaki Try again yine yazısız sorar; App'in bugünkü testi bunu tutuyor.
- `App.jsx` değişmez: `refused={chat.refused}` ve `onRetry={chat.retry}` zaten veriliyor.
- `dist` derlenmez: koşuyu yöneten Claude birleştirirken derler.

## Nasıl görülür

Dört satır yeşil: queen-agent'ın ön ucu 700. Tarayıcıda: dolu bir sohbette (ya da sunucu kapalıyken)
bir mesaj gönderilince kırmızı satır yerine kahverengi kart, altında sunucunun yazısı, cümle kutuda;
`Try again` kutudakini gönderir ve kutu boşalır. Başka bir sohbete geçince kart yok.

Adım adım dökümü [uygulama turunun planında](../plans/2026-09-29-queenagent-m349-ret-karti-uygulama-plan.md).
