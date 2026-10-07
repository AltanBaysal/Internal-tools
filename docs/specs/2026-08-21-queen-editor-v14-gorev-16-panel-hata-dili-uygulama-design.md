# v14 · Görev 16 — Panel hata dili · **uygulama turu**

**Kaynak:** [test turu spec'i](2026-08-21-queen-editor-v14-gorev-16-panel-hata-dili-testler-design.md) ·
kırmızı commit `23c31ee` (467 testin 13'ü kırmızı).

Tek dosya: `LayerPanel.jsx`.

## Sebep bir fonksiyon

Bugün sebep diye bir şey yok — `owed` sıfırsa katmanın tek cümlesi yazılıyor. Bundan sonra bir
fonksiyon, bir insanın bakacağı sırada okuyor:

```
refusalOf(words, can, scope, scoped, variants) -> cümle | null

  varyant kutusu boş                 → "Varyant sayısı girilmedi — en az 1 yaz."
  kapsamda iş var                    → null
  bu katmanın asılabileceği kare yok → words.noBase
  kapsam seçili karelerse            → words.chosenNoBase
  kalan tek ihtimal                  → words.allHeld
```

`can` — `eligible(frames, layer)`, yani bu katmanın **hiç** asılabileceği kareler. Boş olması ile
kapsamın boş olması ayrı iki şey, ve tasarımın dört cümlesini birbirinden ayıran da bu.

**Ölü dal yok.** Video için `can` üretilmiş karelerin kendisi, dolayısıyla `!can.length` "hiç
üretilmiş kare yok" demek — video'nun `noBase` cümlesi bu. Ses için `can` videosu olan kareler,
`noBase` da onu söylüyor. Her cümle geçilebilir bir daldan çıkıyor.

**Sıra neden bu.** Varyant en önde, çünkü kullanıcının gözünün önündeki kutu o. `can` seçimden
önce, çünkü hiç malzeme yokken "seçtiklerinde yok" demek kullanıcıyı yanlış yere baktırır. En sonda
`allHeld`: geriye kalan tek ihtimal, ve tahmin değil çıkarım.

## Katman başına üç cümle

`WORDS`'ün `empty` alanı üçüyle değişiyor:

| | video | audio |
|---|---|---|
| `noBase` | "Henüz üretilmiş kare yok." | "Videosu olan kare yok." |
| `chosenNoBase` | "Seçili karelerin fotoğrafı henüz üretilmedi." | "Seçili karelerin videosu henüz üretilmedi." |
| `allHeld` | "Tüm karelerin videosu var." | "Tüm karelerin sesi var." |

Dördüncü cümle katmandan bağımsız, modül düzeyinde tek sabit.

## Buton

`disabled={!owed || submitting || missingProducer}` → `disabled={submitting || missingProducer}`.

`!owed` gidiyor: eksik alan butonu kilitlemiyor. `missingProducer` kalıyor — tasarımın kendi
istisnası, 5. karar okunduğunda "üretici henüz burada değil" hâline karşılık geliyor ve panelin
tepesindeki kart onu zaten yazıyor.

## Kırmızı kart

Yeşil onay kartının birebir ikizi: aynı `wf-stroke` kutusu, aynı yer, `--danger` çerçevesi ve
`--danger-bg` zemini, başında `✕`. Yeşilin `✓`'sinin durduğu yerde duruyor ve aynı sebeple ayrı bir
parça: işaret cevabı bir bakışta taşıyor ve metnin ikinci satırına sarmıyor.

Butonun altındaki sıra: **yeşil kart → kırmızı kart → tahmin → hiçbir şey.** Boş kapsamın kendi
cümlesi tümüyle gidiyor; yapacak iş yokken orada bir şey yazmıyor.

## Varyant kutusu

Boşken `--danger` çerçevesi alıyor. Odaktan çıkınca sessizce `1`'e dönen `onBlur` **kalkıyor** —
kutu kırmızı kalabilmeli, ve boşluğun cevabı basıldığında veriliyor.

## Sebep ne zaman siliniyor

```js
useEffect(() => { setRefused(null); }, [chosen, scope, variants]);
```

Üçü de sebebi doğuran şeyin parçası: hangi kareler, hangi kapsam, hangi sayı. Biri kımıldadığında
sebep bayat bir cevap oluyor. Galeriden gelen seçim de bunun içinde — kullanıcı orada başka kareler
seçtiğinde panelin altındaki cümle artık onlardan söz etmiyor.

Basma anı bu üçünün hiçbirini değiştirmiyor, dolayısıyla sebep basıştan sonra duruyor.

## Değişmeyen

- `GeneratePanel.jsx` — fotoğraf paneli bu maddenin dışında (test turu spec'i, kapsam dışı).
- `Süre` bloğu, kapsam satırının adı, model satırı — 17. madde.
- `eligible`, `neighbours`, `acceptsVariants` — kurallar aynı, okunma yerleri arttı.

## Bitti sayılır

Dört komut da yeşil: 384 / 474 / 694 / 467. `dist` aynı commit'te derleniyor.
