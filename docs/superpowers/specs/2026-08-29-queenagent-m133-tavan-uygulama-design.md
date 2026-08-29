# Madde 133 · Tur 2 (uygulama) — Tasarım

**Testler:** [2026-08-29-queenagent-m133-tavan-testler-design.md](2026-08-29-queenagent-m133-tavan-testler-design.md)
**Kırmızı commit:** `33b2b57` · **Dal:** `feat/queenagent-m123-skill-rewrite`.

## Ne yazılıyor

Dört dosya, ve hiçbiri ön yüzde.

### 1. `chat.py` · `Usage` dördüncü sayıyı alır

`context: int = 0` — turun **son raundunun** `sent`'i. Üçünün yanına dördüncü olarak giriyor,
çünkü öteki üçü *"bu cevap ne harcadı"* sorusunu cevaplıyor ve bu *"konuşma nerede kaldı"*
sorusunu. Aynı nesnede duruyorlar çünkü ikisi de bir turun ölçüsü ve aynı anda öğreniliyor.

### 2. `chat.py` · `last_sent` → `last_context`

Ad artık yalan söylerdi: fonksiyon toplamı değil son raundu döndürüyor. Docstring'in yanlış çıkan
cümlesi de düşüyor — *"no single turn is large enough to cross it on its own"* — çünkü tam olarak
onun yanlışlığı bu maddeyi doğurdu. Yerine ne ölçüldüğü yazılıyor.

`is_full` değişmiyor: hâlâ `>= CONTEXT_CEILING`, ve sabit hâlâ 50k.

### 3. `stream_answer.py` · toplanmak yerine değiştirilir

`spent` dördüncü alanı **eklemiyor, yerine koyuyor**: her raundun `sent`'i bir öncekinden büyük
*(konuşma büyüyor)*, ve sonuncusu turun bittiği yer. Öteki üçü aynen toplanmaya devam ediyor.

### 4. `file_chat_store.py` · alan diske yazılır ve okunur

`_message_json` dördüncü anahtarı koşulsuz yazıyor — üçü nasıl yazılıyorsa öyle. `_as_usage`
`raw.get("context", 0)` ile okuyor, yani alanı olmayan eski kayıt sıfır dönüyor ve o sohbet dolu
sayılmıyor. **Göç yazılmıyor:** alan bir sonraki turda kendiliğinden doluyor.

### 5. `routes.py` · uç aynı şekli gönderir

Çağrı `last_context`'e dönüyor. **JSON anahtarı `context.sent` olarak kalıyor** — ön yüz onu
okuyor, ve değiştirmek `dist` derlemesi demek olurdu. Anahtar yanlış da değil: `context` nesnesinin
içinde `sent`, *"bağlam ne kadar gönderiyor"* diye okunuyor. Mesajın kendi `usage` nesnesine yeni
alan **eklenmiyor**: ekran onu çizmiyor, ve çizilmeyen bir sayıyı yollamak FOUNDATION 3'e çarpar.

## Değişmeyen

Kartın okuduğu sayı *(83)*, önbellek payı *(76, 124)*, `CONTEXT_CEILING = 50_000`, `is_full`'un
eşiği, cevapsız soruyu atlayarak geriye yürüme, ve uçtaki JSON şekli.

## Bilerek yapılmayanlar

Göç, ön yüz, `dist`. 134 ile 135 ayrı maddeler.
