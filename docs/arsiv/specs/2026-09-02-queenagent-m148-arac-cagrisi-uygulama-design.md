# Madde 148 · Tur 2 (uygulama) — Tasarım

**Kaynak:** [Tur 1 tasarımı](2026-09-02-queenagent-m148-arac-cagrisi-testler-design.md)
**Kırmızı commit:** `12ff460` *(3 kırmızı, 683 yeşil)*

## Şekli

Tek dosya: [client.py](../../../queen-agent/backend/services/xai/client.py). Üç parça.

**`_Calls` — parçaları tutan küçük bir toplayıcı.** `index` başına bir kayıt; `arguments`
**ekleniyor**, geri kalan her alan **yazılıyor**. Sıra ilk görülme sırası, `index`'in kendi sayısı
değil: alan bir kimlik, bir konum değil.

**`index` yoksa `0`.** xAI'nin tek parça çağrısında bu alan hiç yok, ve o yol bozulmadan geçmeli —
tek parça da bir parçadır.

**Çıkan kayıt `index` taşımıyor.** Yukarısı `id`, `function.name` ve `function.arguments` okuyor;
`index` taşımanın kendi muhasebesi ve orada işi yok. Bunun yan faydası, bugünkü
`test_a_tool_call_arrives_whole_in_one_frame`'in girdiyi birebir geri beklemesi — fazladan bir
anahtar onu kırardı.

**Çağrı akışın sonunda veriliyor.** Döngü bittikten sonra, ve yalnız bir şey biriktiyse. Boş liste
yayınlanmıyor: `stream_answer` metin ve sayı olmayan her şeyi çağrı sayıyor, yani boş bir liste
"araç istendi" diye okunurdu.

**`_spoken` ikiye ayrılıyor** — `_said` yalnız kelimeleri, `_fragments` yalnız parçaları veriyor.
Bugün tek fonksiyon ikisini birden döndürüyor ve bir kare her ikisini de taşıyabildiği için hangisi
kazanacağı sıraya kalmıştı; ayrılınca soru ortadan kalkıyor.

## Bilerek kabul edilen

**Kesilen bir akışın biriken parçaları gidiyor.** Son `yield` döngüden sonra, yani bir istisna onu
atlıyor. Doğrusu bu: kesilen tur zaten atılıyor *(FOUNDATION 1'in "yarım cevap saklanmaz" hâli)*, ve
yarım bir `arguments` geçerli JSON değil — çalıştırılsa kendi hatasıyla düşerdi.

## Değişmeyen

`stream_answer` ve yukarısı **tek satır bile** değişmiyor. Değişmek zorunda kalırsa düzeltme yanlış
katmandadır — ve bu tur onu sınayan tek şey `test_stream_answer.py`'nin bütünüyle yeşil kalması.
