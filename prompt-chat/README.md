# prompt-chat

Grok ile düz sohbet eden bir deney tezgâhı. Amaç: WAN 2.2 T2V prompt'larını üretirken
modelin ne kadar işe yaradığını rahat denemek.

## Çalıştırma

```bash
cd prompt-chat
npm install     # bir kez
npm run dev     # http://localhost:5173
```

İlk açılışta üstteki alana [console.x.ai](https://console.x.ai)'dan aldığın API anahtarını
yapıştır. Anahtar tarayıcının `localStorage`'ında kalır, kaynağa yazılmaz; bu yüzden kod
rahatça commit edilebilir. (`.env` de kullanılmaz — Vite `VITE_` ile başlayan değişkenleri
derlenmiş çıktıya gömer, yani saklamış olmazdın.)

Yanındaki alan model adıdır (varsayılan `grok-4.3`). Konsolda görünen id farklıysa buradan
düzelt — kod değiştirmen gerekmez. Başka bir modele geçmek de aynı kutu.

## Kullanım

Enter gönderir, Shift+Enter alt satıra geçer. Her cevabın altındaki **Kopyala** metnin
tamamını panoya alır; oradan `api.ipynb`'nin `PROMPTS` listesine yapıştırırsın.

Sohbet bellekte durur: sayfayı yenilersen sıfırlanır. Anahtar ve model adı kalır.

System prompt yoktur — talimatını ilk mesaj olarak sen yapıştırırsın. Böylece talimatı
değiştirmek için kodu açman gerekmez; denenen şey modelin yanı sıra talimatın kendisi de.

## Test

```bash
npm test
```

Vitest, jsdom ortamında koşar: tarayıcı açılmaz, ağa çıkılmaz, `fetch` sahtelenir.

## Sınırlar

Bu bir tezgâh, ürün değil: tek kullanıcı, `localhost`, kalıcılık yok, deploy yok.
`dist/` repo'ya girmez. Grok'un çıktısı yeterince iyiyse aynı mantık Queen Editor'ın içine
yazılır ve bu araç düşer.
