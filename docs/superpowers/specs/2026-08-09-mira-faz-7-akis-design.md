# Mira — Faz 7: Akış (Madde 15-16)

**Tarih:** 2026-08-09 · **Branch:** `feat/mira-v1`
**Üst belgeler:** [tasarım v1](2026-08-09-mira-v1-design.md) ·
[yol haritası](../plans/2026-08-09-mira-v1-roadmap.md) · [Faz 6](2026-08-09-mira-faz-6-grok-design.md)

**Kapsam:** cevabın parça parça akması (Madde 15) · hata kartı ve **Try again** (Madde 16).
**Kapsam dışı:** araçlar (Faz 8) · çevrimdışı şeridi (Faz 14).

---

## 1 · Akış nereden geçer

Faz 6'nın `POST …/answer` uç noktası **SSE'ye döner**. Değişen tek yer burası — Faz 6'da cevabı ayrı
bir uç noktaya koymanın sebebi tam olarak buydu.

Doğrulanmış biçim (xAI dokümanı): istek gövdesinde `"stream": true`, cevap `data: {...}` satırları,
metin `choices[0].delta.content`, bitiş `data: [DONE]`.

Kendi uç noktamız aynı kalıbı kullanır ama **kendi olaylarıyla**:

| Olay | Ne taşır | Ekranda |
|---|---|---|
| `chunk` | `{"text": "…"}` | üç nokta söner, metin birikir |
| `done` | güncel sohbetin tamamı | biriken metin sunucunun kaydıyla değişir |
| `error` | `{"error": "…"}` | hata kartı + **Try again** |

**Neden `done` bütün sohbeti taşıyor:** biriken metin tarayıcının elindeki tahmindir; diske ne
yazıldığı sunucunun cevabıdır. İkisini eşitlemek yerine sonuncuyu doğru kabul etmek, bir daha
"ekranda ne var, diskte ne var" sorusunu doğurmuyor.

## 2 · Yarım metin saklanmaz

Akış ölürse `ai` mesajı **hiç yazılmaz**. Kullanıcı mesajı yerinde kalır — tasarımın hata hâli
"the user message stays" diyor.

Gerekçe: yarım bir cevabı kalıcı kılmak, tasarımın "cevap ya vardır ya yoktur" diline aykırı; kullanıcı
o yarım metnin devamının gelip gelmeyeceğini bilemez ve dosya üretimi (Faz 8) yarıda kalmış bir
düşünceden doğamaz.

## 3 · Hata, akış başladıktan sonra

HTTP durumu ilk bayt gittiğinde kilitlenir; bu yüzden akış içindeki arıza **502 olamaz**. Hata bir
`error` olayı olarak akışın içinden gelir ve gövdesinde motorun gerçek satırı durur.

Akış hiç başlayamazsa (sohbet yok) klasik durum kodu döner: **404**.

## 4 · Try again

Hata kartı **"Couldn't get a response."** yazar ve yanında **Try again** durur.

**Tasarımın cümlesi kısaltıldı.** Prototip *"Couldn't get a response. The connection dropped."* diyor;
ikinci cümle uydurulmuş bir sebep. Bağlantı kopmuş olabilir, ama 401 de aynı kartı çıkarır, yanlış
model adı da. Kart artık sebebi iddia etmiyor: altında mono bir satırda **sunucunun gerçek çıktısı**
duruyor. Bu, "asla sebep uydurma" kuralının doğrudan uygulaması.

Basınca **yeni bir mesaj gönderilmez** — sohbet zaten cevap borçlu, yalnız `answer` yeniden istenir.
Böylece kullanıcının cümlesi ikinci kez yazılmaz.

Faz 6'da konan kural ("hatadan sonra kendiliğinden tekrar sorma") yerinde kalıyor; **Try again** o
kuralı elle çözen tek yol.

## 5 · Katmanlar

| Katman | Değişiklik |
|---|---|
| services/xai | `stream(messages, tools=None)` — `data:` satırlarını çözer, metin parçaları üretir |
| domain/ports | `Engine.stream(messages, tools=None)` |
| domain/usecases | `stream_answer(...)` — parçaları verir, **bitince** `ai` mesajını yazar |
| data | `XaiEngine.stream` |
| presentation | `POST …/answer` artık `text/event-stream` |
| frontend | `shared/sse.js` — `fetch` + okuyucu; `useChat` biriken metni tutar; `ChatScreen` onu çizer |

`EventSource` kullanılmaz: yalnız GET yapabiliyor, bizim uç noktamız POST. `fetch` + `body.getReader()`
aynı işi görüyor ve testte sahtelenmesi kolay.

## 6 · Testler

1. `XaiClient.stream` `data:` satırlarını metin parçalarına çeviriyor ve `[DONE]`'da duruyor.
2. Bozuk bir `data:` satırı akışı düşürmüyor, atlanıyor.
3. `stream_answer` parçaları veriyor ve **bitince** mesajı yazıyor.
4. Akış ortada patlarsa sohbete hiçbir şey yazılmıyor.
5. Rota `text/event-stream` döndürüyor; `chunk`, `done` sırası doğru.
6. Bilinmeyen sohbet 404 (akış başlamadan).
7. Ön yüz: parçalar geldikçe metin birikiyor, üç nokta ilk parçada sönüyor.
8. Ön yüz: `error` olayı hata kartını çıkarıyor ve kullanıcı mesajı duruyor.
9. Ön yüz: **Try again** yeni mesaj göndermiyor, yalnız `answer`'ı yeniden istiyor.

## 7 · Kabul kriteri

`pytest` ve `npm test` yeşil. Gerçek anahtarla: cevap harf harf birikiyor; anahtar bozukken hata
kartı çıkıyor, düzeltip **Try again**'e basınca cevap geliyor ve mesaj ikinci kez yazılmıyor.
