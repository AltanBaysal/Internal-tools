# Madde 68 · Tur 1 (test) — Plan

**Tasarım:** [2026-08-26-queenagent-m68-tuketim-testler-design.md](../specs/2026-08-26-queenagent-m68-tuketim-testler-design.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Testlerin konuşacağı adlar

Madde 66'nın dersi: içe aktarılamayan bir ad `pytest`i toplama hatasına düşürüyor ve suite kırmızı
değil bozuk oluyor. O yüzden **adlar bu turda doğar**, davranış ikinci turda.

- **`Usage`** — `domain/chat.py`, `ToolCall`'un yanında. Üç tam sayı, hepsi sıfır varsayılanlı:
  `sent` (isteğin taşıdığı her şey), `cached` (bunun servisin elinde olan kısmı — `sent`'in içinde,
  üstünde değil), `answered` (modelin yazdığı). Yeniden ödenen sayı yok, çünkü o `sent - cached`.
- **`Message.usage: Usage = Usage()`** — `calls` ve `stopped`'ın yanında, aynı kuralla: boşken
  diske yazılmaz, taşımayan eski kayıt sıfır okunur.

Bu turda **yalnız adlar** yazılır: tip vardır ama kimse doldurmaz. `Engine.stream`'in üçüncü parça
tipini anlatan port belgesi ikinci tura kalır — bugün doğru olmayan bir sözü porta yazmak, belgeyi
koddan önce yalancı yapar.

## Dosyalar

`backend/tests/test_xai_client.py` · `test_stream_answer.py` · `test_file_chat_store.py` ·
`test_chats_api.py` · `frontend/src/features/workspace/ChatScreen.test.jsx`
Ve iki ad için: `backend/features/workspace/domain/chat.py`.

Yeni test dosyası yok — dördü de var olan dosyalara, kendi bölüm başlıkları altına eklenir.

## Testler

### `test_xai_client.py` — dört test

Var olan `_Lines` ve `_delta_line` yardımcıları kullanılır; tüketim taşıyan kare için bir
`_usage_line` eklenir.

Tüketim taşıyan bir kare `{"usage": {"sent": …, "cached": …, "answered": …}}` veriyor ve üç sayıyı
xAI'nin adlarından çeviriyor. Hem içerik hem tüketim taşıyan bir kare **ikisini birden** veriyor —
bugün her kare tek bir şey verebiliyor, ve gerçek akışta ikisi aynı karede geliyor.
`prompt_tokens_details` hiç yoksa önbellek sıfır okunuyor. Tüketimden söz etmeyen bir akış hiç
tüketim parçası vermiyor.

### `test_stream_answer.py` — beş test

Var olan `ScriptedEngine` kullanılır; tüketim parçası da bir parça olduğu için kurgu değişmiyor.
Durdurma için var olan `StopsAfter` kullanılır.

Cevap harcadığını hatırlıyor. İki turun sayıları toplanıyor — her tur ayrı bir akış, ayrı bir
harcama. Tek turun içinde tekrarlanan sayı iki kez sayılmıyor: akış içinde sayı kümülatif olduğu
için **en sonuncusu geçerli**. Hiç ölçülmemiş bir cevap sıfır taşıyor. Ortasında durdurulan cevap
o ana kadar ölçüleni saklıyor — girdi çoktan gönderilmiş ve ödenmiş.

### `test_file_chat_store.py` — iki test ve bir satır

Sıfır olmayan tüketim gidiş dönüş hayatta kalıyor. Tamamen sıfırsa `usage` diske hiç yazılmıyor.

Üçüncüsü — alanı taşımayan eski bir sohbetin sıfır okunması — ayrı bir test olmadı: aynı soruyu
`calls` ve `stopped` için soran test zaten duruyordu, ve üçüncü alanı oraya bir satır olarak eklemek
üç ayrı testin aynı dosyayı üç kez kurmasından iyi.

### `test_chats_api.py` — iki test

Mesajın JSON'u tüketimi taşıyor. Sıfır olduğunda da taşıyor — tarayıcı eline verilen şeyi çiziyor,
ve alanın yokluğu her okuyucuya bir kontrol yazdırırdı.

### `ChatScreen.test.jsx` — dört test

Cevabın altında `.token-count` satırı çiziliyor ve **tek sayı** taşıyor: `sent + answered`.
Tüketimi olmayan mesaj satır çizmiyor. Bin ve üstü `k` ile kısalıyor (`13.2k tokens`), altı olduğu
gibi yazılıyor (`342 tokens`). Kullanıcının kendi mesajı hiç satır taşımıyor — harcayan cevaptır.

Satırı bekleyen iki test onu **metniyle** arıyor, sınıfıyla değil: sınıfla arayan bir test eleman
yokken `null.textContent` üzerinde `TypeError` veriyor, ve o başarısızlık ne aradığını söylemiyor.
Metinle arayınca kayıp eleman kendi adıyla rapor ediliyor.

## Beklenen kırmızı

**Arka uçta 10, ön yüzde 2 kırmızı; 5 test de doğduğu anda yeşil.** Ayrımı önden yazıyorum çünkü
Madde 65'te bunun tersi oldu: yeşil diye yazılan bir test kırmızı çıktı ve plan yanlıştı.

| Dosya | Kırmızı | Doğduğu anda yeşil |
|---|---|---|
| `test_xai_client.py` | 3 | 1 — tüketimsiz akış zaten tüketim parçası vermiyor |
| `test_stream_answer.py` | 4 | 1 — ölçülmemiş cevap zaten sıfır taşıyor |
| `test_file_chat_store.py` | 1 | 1 — depo `usage` diye bir şey bilmiyor, yani yazmıyor da |
| `test_chats_api.py` | 2 | — |
| `ChatScreen.test.jsx` | 2 | 2 — hiçbir şey çizilmediği için "çizilmiyor" testleri geçiyor |

Doğduğu anda yeşil olan beşi **bekçi**: bugünkü doğru davranışı çiviliyorlar ve ikinci tur onu
bozarsa kırmızıya dönerler. Kırmızı olmamaları bir eksiklik değil, ama kırmızı **olmaları** da
sürpriz olmamalı — olurlarsa orada tahmin ettiğimden başka bir şey var demektir.

**Koşulduğunda çıkan:** arka uçta 10 kırmızı / 420 yeşil, ön yüzde 2 kırmızı / 487 yeşil. Tahminle
aynı; tek fark deponun üçüncü testinin ayrı bir test değil var olan bir teste eklenen bir satır
olması (yukarıda).

**Bu turda mekanik kırmızı yok.** Madde 67'de `stream_answer` bir parametre kazandığı için 32 test
imza yüzünden düşmüştü; bu madde hiçbir imzaya dokunmuyor. `Message` bir alan kazanıyor ama
varsayılanı var, ve eşitlik karşılaştırmaları iki tarafta da aynı varsayılanı görüyor. **Var olan
417 arka uç ve 485 ön yüz testinin hepsi yeşil kalmalı** — biri düşerse mekanik değil gerçek bir
kırılmadır.

## Bu turda yapılmayan

İstemcinin tüketime bakması · `stream_answer`'ın toplaması · deponun yazma/okuma yolları ·
`_chat_json`'ın alanı · `ChatScreen`'in satırı ve sayı kısaltıcısı · `workspace.css`'in stili ·
`ports.py`'nin belgesi. `dist` derlenmez.
