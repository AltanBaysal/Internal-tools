# Madde 137 · Tur 2 (uygulama) — Tasarım

**Kaynak:** [2026-08-31-queenagent-m137-son-tur-testler-design.md](2026-08-31-queenagent-m137-son-tur-testler-design.md)
**Kırmızı commit:** `24b92b1` — 6 kırmızı, 647 yeşil.
**Dal:** `feat/queenagent-m137-son-tur`.

## Ne yeşile dönecek

Altı test. Beşi `LAST_ROUND` adının yokluğunu gösteriyor; altıncısı,
`test_the_last_round_is_offered_no_tools`, davranışın kendisini sayıyla söylüyor — son raunt bugün
sekiz araç teklif ediliyor, boş liste bekleniyor.

## Üç dosya

### 1. `prompt.py` — `LAST_ROUND` doğar

`SYSTEM_PROMPT`'un yanına, aynı sesle yazılmış tek bir metin. Söylemesi gerekenler test tarafından
çivili: *last round*, *no tool*, *what is left*, *next step*.

Dosyanın docstring'i genişler. Bugün *"before every answer"* diyor, ve bu metin her cevaba değil bir
cevabın son rauntuna gidiyor — cümle koda uydurulur.

**`SYSTEM_PROMPT`'a eklenmiyor, ayrı duruyor.** Taban yönerge her istekte gidiyor ve önbelleğin
sabit başlangıcı o; içine turun nerede durduğunu söyleyen bir cümle koymak her rauntun önekini
bozardı. Ayrı sabit, isteğin kuyruğuna ayrı biniyor.

### 2. `stream_answer.py` — döngü rauntu tanır, `_asked` söyler

`_asked` beşinci bir parametre alır (`last=False`) ve doğruyken `LAST_ROUND`'u **en sona** ekler.

**Erken `return` düşüyor.** Bugünkü gövde `if not instruction: return asked` ile çıkıyor, ve skill
seçilmemiş bir sohbette kapanış cümlesi o kapıdan hiç geçemezdi — testlerden biri tam o durumu
koşuyor. Yerine her parça kendi `if`'iyle ekleniyor ve tek bir `return` kalıyor; sıra
*isimler → kutu → yönerge → kapanış* olarak okunur duruyor.

Döngü sayacını okur:

```
for index in range(MAX_ROUNDS):
    last = index == MAX_ROUNDS - 1
```

ve `last` iki yere gider: `_asked`'a, ve `tools=None if last else TOOL_SPECS` olarak `engine.stream`'e.
`XaiClient._request` `if tools:` ile yazdığı için `None` istekte hiç anahtar bırakmıyor —
transport'ta değişiklik yok.

Bugün `for _ in range(...)` yazıyor; sayacın adı ilk kez burada gerekiyor.

### 3. `tools.py` — yorum koda uyar

`MAX_ROUNDS`'un üstündeki blok *"Sixteen rounds carry it"* diyor. Bundan sonra on beşi taşıyor ve on
altıncısı kapatıyor. Sayı değişmiyor, cümlesi değişiyor.

## Değişmeyen

`MAX_ROUNDS = 16`. `append_message`'ın boş mesaj kuralı. İzin kapısı, durdurma, `usage` toplaması,
bağlam kabı, `x-grok-conv-id`. Ön yüz ve `dist` — madde ekranda yeni bir şey çizmiyor.

## Nasıl görülecek

`python -m pytest queen-agent -q` altı kırmızıyı yeşile çevirir ve 647'nin hiçbirini kırmızıya
düşürmez. Node kurulduğunda `npm test --prefix queen-agent/frontend` de koşulur; bu madde ön yüze
dokunmadığı için beklenen, olduğu gibi yeşil.
