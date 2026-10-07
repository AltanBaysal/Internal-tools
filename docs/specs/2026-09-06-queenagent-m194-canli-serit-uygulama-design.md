# Madde 194 · uygulama turu — canlı tur şeridi

**Kaynağı:** [test turu](2026-09-06-queenagent-m194-canli-serit-testler-design.md), `f5ea906`'da
ön yüzde 7 kırmızı ve arka uçta bir `ImportError`.

---

## Beş dosya

| Dosya | Ne oluyor |
|---|---|
| `stream_answer.py` | `Progress` sınıfı, `_volume`, ve üç `yield` |
| `routes.py` | `event: progress` |
| `useChat.js` | `progress` durumu — `streamingCalls` ile aynı kurallar |
| `ChatScreen.jsx` | `LiveStrip`, `Stamp`'in yerinde |
| `workspace.css` | şerit ve dönen spinner |

Artı `dist`, aynı commit'te.

## `Progress` nerede duruyor

`stream_answer.py`'nin kendisinde. Emsal ikiye ayrılıyor — `FileStarted`/`FileWritten` `tools.py`'de,
`PermissionWanted`/`Waiting` `permission.py`'de — ve ortak kural şu: **parça, onu doğuran şeyin
yanında duruyor.** Bunu doğuran şey turun kendisi, ve tur bu modül. `routes.py` zaten buradan
`stream_answer`'ı alıyor.

Alan adı `round`, gömülü `round()`'u gölgeliyor — yalnız üretilen `__init__`'in imzasında, ve o
gövde `round()` çağırmıyor. Karşılığı, telde ve ekranda okunan kelimenin kodda da aynı olması.

## Üç `yield`, ve neden üç

```
raundun başında          -> sayı 0 bile olsa raunt numarası hemen ilerler
raundun usage'ından sonra -> motor bunu akış kapanırken söylüyor; sayının asıl kımıldadığı an
aracın faturasından sonra -> Madde 176'nın ikinci isteği, raundun ortasında
```

İkincisi ve üçüncüsü aynı cümleyi söylüyor — *toplam değişti* — ama iki ayrı yerde değişiyor, ve
tek bir yerden ikisini birden yakalamanın yolu yok.

## `_volume`

`sent + cached + answered`. **Fatura değil**: `cached` de telden geçiyor, sadece ucuza. Damga
`sent + answered` göstermeye devam ediyor, ve fark bilerek — yol haritasının cümlesi *"şerit bu tur
ne kadar büyüdü sorusunu cevaplıyor, faturayı değil"*. Tur bitince rakam değişir; **değişmeyen şey
yer ve tasarım**, ve göze zıplayan da o olurdu.

## Şerit

`Stamp`'in çizildiği iki yerde de onun yerine geçiyor: bekleyen kutu *(üç nokta)* ve akan kutu.
`progress` yoksa `Stamp` kalıyor.

`msg__stamp` sınıfını taşıyor artı `msg__stamp--live`. Tur bitince koşan kutu kaybolup kaydın
mesajı çiziliyor, ve ikisi aynı satır gibi görünüyor.

**Spinner CSS'in.** `@keyframes` ile dönen bir yay. Bir `setInterval` React meşgulken bekler, ve
donmuş görünmeme derdi tam o anda başlıyor.

**Kelime bir `setInterval` ile dönüyor**, `WORD_MS` *(3000)*, rastgele bir yerden başlayarak. On
altı gerund; hiçbiri ne yapıldığını söylemiyor, çünkü bilgi taşıyan iki parça zaten yanında.

## Yeşilin nasıl görüleceği

Dört sabit test satırı, sırayla, birebir. `ImportError` kalkınca arka ucun gerçek kırmızıları
görünür ve onlar da kapanır; ön yüzde 7 kırmızı gider. `queen-editor` kımıldamaz. Sonra
`npm run build --prefix queen-agent/frontend`, ve `dist` bu commit'e girer.
