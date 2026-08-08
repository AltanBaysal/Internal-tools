# prompt-chat — Grok sohbet tezgâhı

**Tarih:** 2026-08-08 · **Branch:** `feat/queen-editor-v2`
**Amaç:** Grok'un WAN 2.2 T2V prompt'u üretmedeki gücünü rahat denemek. Tek kullanıcı (geliştirici),
kendi makinesinde, `localhost`.

Bu araç **Queen Editor değildir ve ona bağlı değildir** — kendi klasöründe durur, onun hiçbir
dosyasını okumaz, kendi `package.json`'ı vardır. Bir deney tezgâhı: Grok'un çıktısı yeterince iyiyse
aynı mantık ileride Queen Editor'ın içine yazılır ve bu araç düşer.

## Ne çalışır

Tarayıcıda düz bir sohbet penceresi açılır ve doğrudan xAI API'siyle konuşur:

1. `npm install` bir kez; sonra her açılışta `npm run dev` → `http://localhost:5173`.
2. İlk açılışta üstteki alana API anahtarı yapıştırılır; `localStorage`'a yazılır, bir daha sorulmaz.
3. Alta mesaj yazılır → **Enter** gönderir, **Shift+Enter** alt satıra geçer (çok satırlı talimat
   yazılabilsin diye) → istek doğrudan `api.x.ai`'a gider → cevap sohbete düşer.
4. Cevap beklenirken gönderme kapalıdır ve yerinde "…" durur; cevap gelince açılır. Aynı anda iki
   istek uçmaz.
5. Her cevabın altında **Kopyala** durur — tek tıkla metnin tamamı panoya gider. Asıl döngü bu:
   üret → kopyala → `api.ipynb`'nin `PROMPTS` listesine yapıştır.
6. Sayfa yenilenirse sohbet sıfırlanır; anahtar ve model adı kalır.

Görünüş koyu ve sade, tek sütun: bir deney tezgâhı, ürün değil.

## Kapsam dışı

- **Backend / sunucu** — istek tarayıcıdan doğrudan gider. Bu mümkün, çünkü xAI CORS'a izin veriyor
  (2026-08-08'de preflight ile doğrulandı: `access-control-allow-origin: *`). Araya bir sunucu
  koymak burada hiçbir sorunu çözmez, yalnız çalıştırılacak ikinci bir şey ekler.
- **Yayına alma** — `vite build` çalıştırılabilir ama `dist/` repo'ya girmez ve hiçbir yere
  deploy edilmez. Queen Editor'ın "derlenmişi commit et" kuralı **buraya uğramaz**: o kural Colab
  npm çalıştırmadığı için vardır, bu araç Colab'a hiç gitmez.
- **System prompt** — düz sohbet. WAN talimatı istendiğinde ilk mesaj olarak elle yapıştırılır.
  Talimatı denemek için kod değiştirmek gerekmez, bu yüzden tezgâh olarak daha esnek.
- **Streaming** — gönder, bekle, cevabı bütün olarak gör.
- **Sohbetin kalıcılığı** — dosya yok, veritabanı yok, sunucu yok. Yenile → temiz sayfa.
- **Kullanıcı yönetimi, kullanım limiti** — tek kullanıcı, `localhost`.
- **`api.ipynb`'nin `PROMPTS` listesine yazma** — çıktı panoya kopyalanır, yapıştırmak elle.
  Sınır burası.
- **Markdown render** — cevap ham metin olarak, boşlukları korunarak basılır. Kopyalanan şeyin
  modelin yazdığının aynısı olması gerekiyor; ayrıca render kütüphanesi eklemek bu kadar küçük bir
  araç için gereksiz.
- **`temperature` / `max_tokens` ayarı** — istekte gönderilmez, xAI'ın varsayılanları kalır.
- **Queen Editor'ın tasarım dili (`vendor/kit`)** — kopyalanmaz; kendi sade CSS'i olur.

## 1. Stack ve dosya yapısı

**React 18 + Vite + Vitest** — Queen Editor'ın frontend'iyle **birebir aynı sürümler**. Sebep tek
bir cümlede: spec'in kendisi "işe yararsa mantık Queen Editor'a taşınır" diyor; aynı stack'te
yazılırsa o taşıma kopyala-yapıştır olur, başka bir şeyde yazılırsa arayüz baştan yazılır.

```
prompt-chat/
  package.json
  vite.config.js
  index.html
  README.md
  src/
    main.jsx        # mount
    App.jsx         # durum + yerleşim
    App.test.jsx
    Message.jsx     # tek balon + Kopyala
    Message.test.jsx
    chat.js         # saf mantık: istek gövdesi, hata metni
    chat.test.js
    api.js          # tek fetch burada
    api.test.js
    app.css
    test-setup.js
```

**Katman kuralı:** `chat.js` saftır — `fetch` yok, React yok, tarayıcı yok. `api.js` tek I/O
noktasıdır. `App.jsx` ve `Message.jsx` yalnız gösterir. Testin kolay olmasının sebebi bu ayrım.

## 2. API çağrısı

xAI, OpenAI ile uyumlu bir uç sunar:

```
POST https://api.x.ai/v1/chat/completions
Authorization: Bearer <anahtar>
Content-Type: application/json

{ "model": "<model>", "messages": [ {"role": "user", "content": "…"}, … ] }
```

Cevap `choices[0].message.content` içinde gelir.

Sohbetin tamamı her istekte yeniden gönderilir — sunucu tarafında oturum tutulmadığı için bağlamın
tek taşıyıcısı budur. Ekrandaki mesaj dizisi hem gösterimin hem isteğin kaynağıdır; ikinci bir
kopyası yoktur.

Ekranda **hata satırları da** durur ama isteğe girmez: xAI tanımadığı bir `role` görürse isteği
reddeder. Ayıklamayı `chat.js` yapar ve testi vardır.

## 3. Anahtar ve model

İkisi de ekranda birer alandır ve `localStorage`'da durur (`xai_key`, `xai_model`).

**Anahtar neden dosyada değil:** kaynağa gömülürse dosya commit edildiği anda anahtar git geçmişine
kalıcı olarak girer; geri almanın tek yolu anahtarı iptal etmektir. Alan olarak durduğunda dosya
rahatça commit edilir. `.env` de kullanılmaz — Vite'ta `VITE_` ile başlayan her değişken zaten
derlenmiş çıktıya gömülür, yani saklamış olmayız.

**Model neden ekranda:** varsayılan `grok-4.3`, ama konsoldaki tam model id'si doğrulanmadı. Yanlış
çıkarsa kod açılmadan kutudan düzeltilir. Başka bir modele ya da sağlayıcıya geçmek de aynı kutu —
model adı kodda tek bir yerde, varsayılan olarak geçer.

## 4. Hata

İstek 200 dışında dönerse sohbete kırmızı bir satır düşer: **HTTP kodu ve cevap gövdesi olduğu
gibi**. Sebep yorumlanmaz — 401 "anahtar süresi dolmuş" diye basılmaz, çünkü yanlış model adı da
401/404 döndürebilir. Ağ hatasında (istek hiç ulaşmadıysa) istisnanın kendi metni basılır.

## 5. Testler

`npm test` → Vitest, jsdom ortamında, tarayıcısız ve ağsız. Queen Editor'ın kalıbı aynen geçerli:
test dosyaları kaynağın yanında durur, `fetch` `vi.stubGlobal` ile sahtelenir, hiçbir test gerçek
saniye beklemez.

| Dosya | Neyi kanıtlar |
|---|---|
| `chat.test.js` | İstek gövdesi doğru kuruluyor ve **hata satırları ayıklanıyor**; hata metni `HTTP <kod> — <gövde>` biçiminde |
| `api.test.js` | 200'de içerik dönüyor; 200 dışında gövde **olduğu gibi** hataya geçiyor; ağ hatası yutulmuyor |
| `App.test.jsx` | Mesaj yazılıp gönderiliyor ve cevap ekrana düşüyor; beklerken buton kapalı; hata kırmızı satır oluyor; anahtar `localStorage`'dan geliyor |
| `Message.test.jsx` | **Kopyala** yalnız cevaplarda çıkıyor ve metnin tamamını satır sonlarıyla panoya yazıyor |

## 6. Doğrulama (elle, tarayıcıda)

Testlerin göremediği şeyler — gerçek ağ, gerçek pano, gerçek model:

1. `npm install` → `npm run dev` → sayfa açılır, anahtar alanı boş.
2. Anahtarı yapıştır, "merhaba" gönder → cevap gelir. Sayfayı yenile → anahtar hâlâ orada, sohbet
   boş.
3. Model alanına saçma bir değer yaz, gönder → xAI'ın kendi hata metni ekranda görünür (uydurma
   sebep yok).
4. Anahtarı boz, gönder → yine xAI'ın kendi 401 gövdesi görünür.
5. Uzun bir WAN talimatını ilk mesaj olarak yapıştır (Shift+Enter ile çok satırlı), ardından bir
   sahne özeti gönder → talimata uygun prompt gelir; üçüncü mesajda "daha kısa yaz" de → bağlamı
   koruduğu görülür.
6. Bir cevabın **Kopyala**'sına bas, boş bir dosyaya yapıştır → metin birebir aynı, satır sonları
   dahil.

5. madde aracın asıl sınavı: "Grok bu iş için yeterli mi" sorusunun ilk gerçek cevabı.

## Kararlar

- **Backend yok** — xAI CORS'a izin verdiği için gereksiz.
- **Queen Editor'la aynı stack ve aynı sürümler** — kodun oraya taşınması kopyala-yapıştır olsun diye.
- **Saf mantık `chat.js`'te ayrı durur** — testin tarayıcıya ve ağa ihtiyaç duymaması bu ayrımdan gelir.
- **Anahtar ve model ekranda, `localStorage`'da** — kaynak commit edilebilir kalsın ve yanlış model
  id'si kod değişikliği gerektirmesin diye. `.env` çözüm değil: Vite onu çıktıya gömer.
- **`dist/` commit edilmez** — Colab kuralı buraya işlemez, bu araç Colab'a gitmez.
- **Hata metni ham geçer** — sebep uydurulmaz.
- **System prompt yok** — talimatın kendisi de denenen şeyin parçası; onu mesaj olarak yazmak
  tezgâhı esnetir.
- **Her cevapta Kopyala butonu** — aracın varlık sebebi olan döngünün son adımı.
- **Koyu ve sade görünüm, tek sütun** — tasarım dili taşınmaz.
- **Bu araç geçici** — Queen Editor'a taşınacak olan koddur, dosya değil.
- **`CLAUDE.md`'ye üçüncü araç olarak bir bölüm eklenir** (repo kuralı: her araç kendi klasöründe ve
  orada belgelenir).
