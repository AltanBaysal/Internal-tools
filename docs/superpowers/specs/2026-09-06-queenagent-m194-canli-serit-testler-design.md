# Madde 194 · test turu — koşan tur mesajın altında canlı görünür

**Kaynağı:** [v8 yol haritası](../plans/2026-09-06-queenagent-v8-roadmap.md), Madde 194.

---

## Bugün ne oluyor

Turun ilerlemesi **arka uçta zaten var**: `stream_answer` raundları tek tek koşuyor *(`for index in
range(MAX_ROUNDS)`)* ve `spent`'i raunt raunt topluyor. Eksik olan bunun **ön yüze ulaşması** — akışa
konan çerçeveler `chunk`, `call`, `file-start`, `file`, `permission`, `done`, `error`. Hiçbiri
"kaçıncı raunttayız" ya da "şu ana kadar ne kadar" demiyor.

Ekranda, uzun bir tur boyunca, üç yanıp sönen nokta var. Damga *(`Stamp`)* turun **sonunda** düşüyor.

## Ne kurulacak

### Arka uç — `Progress`, üç yerden

`stream_answer` yeni bir parça yayıyor: `Progress(round, of, tokens)`.

| Nerede | Neden |
|---|---|
| Her raundun başında | Raunt sayısı **hemen** ilerlesin; ilk raundun jetonu 0'dır ve öyle görünür |
| Raundun `usage`'ı toplandıktan sonra | Sayının kımıldadığı asıl an — motor bunu akış kapanırken söylüyor |
| Bir aracın kendi faturası eklendikten sonra | `write_frame_prompt` ve `write_missing_actions` raundun **ortasında** harcıyor |

`routes.py` bunu `event: progress` olarak yazıyor.

**Sayı `sent + cached + answered`** — turun toplam hacmi. Yalnız `sent` işin yarısını gizlerdi:
`cached` de gidiyor, sadece ucuza. Deneme 4'te rahatsız eden **277.6k** tam olarak buydu.

> **Damgadaki sayı bundan farklı, ve bilerek.** Damga `sent + answered` gösteriyor — o **fatura**.
> Şerit *"bu tur ne kadar büyüdü"* sorusunu cevaplıyor. Yol haritasının kendi cümlesi: *"faturayı
> değil — fatura turun sonunda damgada duruyor."* Yani tur bitince rakam değişir; değişmeyen şey
> yer ve tasarım.

### Ön yüz — şerit damganın yerinde

`useChat` `progress`'i tutuyor, `finally`'de temizliyor, ve `visible` kapısından geçiriyor —
`streamingCalls` ile aynı kurallar.

`ChatScreen`'de koşan kutunun altında, `Stamp`'in yerinde:

```
⟳ Ideating… · round 4/16 · 12.3k tokens
```

**İngilizce**, Türkçe değil: QueenAgent'ın arayüzü bilerek İngilizce *(CLAUDE.md)*, ve damga zaten
`tokens` diyor. Yol haritasındaki `jeton` belgenin dili, arayüzün değil.

**Spinner CSS ile dönüyor, JS ile değil.** Asıl mesele donmuş görünmemek, ve React meşgulken bir
`setInterval` de bekler — CSS animasyonu beklemez. Zaten en çok tam o anda gerekiyor.

**Kelime birkaç saniyede bir değişiyor**, rastgele bir yerden başlayıp sırayla. Gerundlu, esprili,
ve ne yapıldığını söylemeye **çalışmayan**: bilgi taşıyan iki parça zaten yanında duruyor.

**`progress` yokken şerit yok.** Turun ilk çerçevesi gelene kadar üç nokta duruyor; `round 0/16`
diyen bir şerit ölçülmemiş bir şeyi iddia ederdi.

## Testler

### `test_stream_answer.py`

1. **koşan tur kaçıncı raunttaysa onu söylüyor** — tek raundluk turda `Progress(1, MAX_ROUNDS, 0)`,
   ve her şeyden önce.
2. **her raunt kendini söylüyor** — iki raundluk turda 1 ve 2 geçiyor.
3. **sayı telden geçen her şey** — `sent + cached + answered`. *Boş geçmez:* yalnız `sent`'e eşit
   olmadığı da aranıyor.
4. **aracın kendi faturası raundun ortasında sayıyı oynatıyor** — `write_frame_prompt` harcıyor, ve
   aynı raunt numarasıyla daha büyük bir sayı geliyor.

Artı üç **düzeltme**: `produced[:-1] == ["He", "llo"]` ve iki `produced[0] is FileStarted` satırı,
konuları başka olduğu hâlde yeni parçanın yanından geçtikleri için.

### `test_chats_api.py`

5. **çerçeve tele çıkıyor** — `event: progress`, içinde `"round": 1` ve `"of": 16`.

Artı iki **düzeltme**: çerçeve adlarını birebir listeleyen iki satır.

### `App.test.jsx`

6. **şerit koşarken ekranda** — akış `progress` taşıyor, ekranda `round 2/16` ve `12.3k tokens`.
7. **tur bitince şerit gidiyor, damga kalıyor** — aynı yerde.

### `ChatScreen.test.jsx`

8. **tek satır, damganın yerinde** — spinner, kelime, raunt ve jeton yan yana, `msg__stamp`'in
   içinde.
9. **kelime kendi kendine değişiyor** — sahte saatle ileri sarılınca başka bir kelime.
10. **spinner JS'e bağlı değil** — sahte saat hiç ilerlemeden de orada. Donmuş görünmemenin
    dayanağı bu.
11. **`progress` yokken şerit yok** — üç nokta duruyor.

## Kırmızının nasıl görüleceği

Dört sabit test satırı, sırayla, birebir. `queen-agent`'ın iki tarafı da kırmızı: arka uçta yeni
`Progress` beklentileri artı beş düzeltilmiş satır, ön yüzde altı şerit testi. `queen-editor`
kımıldamıyor — **739 · 591** yerinde.
