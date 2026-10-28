# v14 · Görev 19 — Her sekme yalnız kendi katmanını gösterir · **uygulama turu**

**Kaynak:** [test turu spec'i](2026-08-21-queen-editor-v14-gorev-19-sekme-kendi-katmani-testler-design.md) ·
kırmızı commit `a4ad67c` (481 testin 6'sı kırmızı).

Tek dosya: `PhotoDetail.jsx`. Değişikliğin tamamı **silme** — sütun eksilerek sadeleşiyor.

## 1 · `shown` gidiyor

```js
const shown = LAYER_ORDER.slice(0, LAYER_ORDER.indexOf(open) + 1);
```

Bu satır *"açık sekmeye kadarki bütün katmanlar"* fikrinin kendisi ve fikrin ikinci yarısı geri
alındı. İki kullanıcısı da gidiyor, dolayısıyla satır da.

`LAYER_WORD` de onunla gidiyor: iki kullanımı da `shown`'ın içindeydi. Prompt etiketlerinin katman
adını taşıması (fark 88) 21. maddenin işi ve o başka kelimeler istiyor — bugünden bekleyen bir
sabit bırakmanın anlamı yok.

## 2 · Üst grup iki satır

```
Sıra           3 / 12
Dosya adı      P0_0.png        ← üretilmemişse "Dosya adı (planlanan)"
Üretim modu    Loop            ← yalnız video sekmesinde ve yalnız modu olan videoda
```

Ad satırı artık koşulsuz: hangi sekme açık olursa olsun aynı etiket, aynı değer. Bugün etiketi
`shown.length === 1` koşuluna bakıyordu — yani "yanımda başka satır var mı" sorusuna — ve o soru
ortadan kalkıyor.

Değer ifadesi olduğu gibi kalıyor: `frame.layers.photo || frame.file`. Kopya karede kaynağın
resmini gösteriyor, ve bu maddede değişen bir şey değil.

Her satırın başlığı `data-field` alıyor — grubun tamamının bir liste olarak okunabilmesi için.

## 3 · Tek prompt kutusu

Açık katman `done` ise yazılabilir kutu, değilse salt okunur kutu. Altındakiler için döngü yok,
çünkü altındakiler yok.

Negatif foto sekmesinde kalıyor.

## 4 · Bekleyen kutunun tek satırı

`TextBlock`'un `hint`'i ortalanıyor ve cümlesi değişiyor:

**"Prompt yok — üretim sırası geldiğinde eklenecek."**

Ortalama yalnız ipucuna ait, gerçek metne değil: bir prompt sola dayalı okunur, bir yokluk
bildirimi kutunun ortasında durur.

Koşul da sadeleşiyor. Bugün `layer === open && openState === "pending" && layer !== "photo"` diyor;
ilk parçası artık her zaman doğru (tek katman var), sonuncusu ise gereksiz — bekleyen bir
fotoğrafın da prompt'u vardır ama o kutuya kullanıcının kendi yazdığı metin gelir, yani `hint`
zaten hiç okunmaz. Yine de kalıyor: bir fotoğraf prompt'unu **kim yazacak** sorusunun cevabı
kullanıcının kendisi, ve o cümle orada yalan olurdu.

## Değişmeyen

- Sekme şeridi, oynatıcı, silme düğmeleri, yeniden üret formu, "Üretim modu" satırı.
- `stateOf`, `has`, `holds`, `typed`, `changed` — okunma yerleri azaldı, kuralları değil.

## Bitti sayılır

Dört komut da yeşil: 384 / 474 / 694 / 481. `dist` aynı commit'te derleniyor.
