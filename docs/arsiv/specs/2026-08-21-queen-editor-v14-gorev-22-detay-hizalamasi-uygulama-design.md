# v14 · Görev 22 — Detayın görsel hizalaması · **uygulama turu**

**Kaynak:** [test turu spec'i](2026-08-21-queen-editor-v14-gorev-22-detay-hizalamasi-testler-design.md) ·
kırmızı commit `877045a` (Python'da 3, frontend'de 26 kırmızı).

Altı dosya: iki motor tarafında, dördü ön yüzde.

## 1 · Motor: negatif yola çıkıyor

`regenerate` yeni bir `negative` parametresi alıyor ve yeni karenin satırına onu yazıyor — bugün
kaynağın negatifini yazıyor. Kural değişmiyor: negatif yalnız **fotoğrafın** satırına giriyor,
üstündeki katmanlar altlarındakinden yapıldığı için negatif taşımıyorlar.

Yol `prompt`'un yolunu izliyor: gövdedeki değer string değilse boş sayılıyor. Ekranda ne
gösterildiyse o iniyor.

## 2 · Sahne

| Ne | Nasıl |
|---|---|
| Üst boşluk | `padding: 24` → `"48px 24px 24px"`, sahneye `data-stage` |
| Şerit | `top: 16` → `12` |
| Bekleyen kutu | "bekliyor" 12 → **14**, "henüz üretilmedi" 12 → **10** ve `--ink-3` → `--ink-4` |
| Hatalı kutu | Başlık `Mono 12` → `Note 13`, sebep `Note 12` → `Mono 11` |
| Katman üretilirken | Resim duruyor, üstüne `Making` iniyor — `frame_status.jsx`'te, `Rendering`'in yanında |
| Kopya kare | Köşeye ikinci hap: "kaynak foto · kopya kare" |

`Making` yalnız **resmi olan** karede doğuyor. Fotoğrafın kendisi üretilirken tutulacak resim yok;
orada `Rendering` kalıyor. Fark bu istisnayı anmıyor, testi anıyor.

## 3 · Basışın hatırası ikiye ayrılıyor

Bugün `sent` katman adlarından oluşan bir liste ve iki ayrı basış onu aynı biçimde dolduruyor:
yeniden üretmek yeni bir kare açıyor, tekrar denemek bu kareyi kuyruğa geri koyuyor. Köşedeki hapın
hangisini söyleyeceğini bilmesi için liste ne olduğunu da taşıyor:

```js
const [sent, setSent] = useState([]);            // { layer, retry }
const wasSent = (layer) => sent.some((one) => one.layer === layer);
const retried = sent.some((one) => one.retry);
```

İki liste tutmak yerine tek liste: aynı basışı iki yerde hatırlamak, ikisinin ayrışabileceği
anlamına gelir.

## 4 · Yıkıcı düğme dört duruma açılıyor

```
foto sekmesi        → Sil · Kuyruktan çıkar · Kareyi sil   (bugünkü üç metin)
katmanı olan sekme  → Videoyu sil — kare kalır / Sesi sil — video kalır
kuyruktaki katman   → Kuyruktan çıkar                       (fark 99)
hatalı katman       → Kareyi sil                            (fark 100)
```

Son ikisi kareyi kuyruktan/galeriden alıyor, katmanı değil — motorda katmanı tek başına kuyruktan
alan bir basış yok (**38. karar**).

**Onay penceresi hangisi olduğunu artık `open`'dan çıkarmıyor.** `confirming` bayrağı `asking`
oluyor: `"frame"` ya da `"layer"`. Sebep hatalı katman: orada silinen şey **kare**, ama açık sekme
foto değil — eski kural o pencerede katman metnini gösterirdi.

`DANGER` kalıbı pasifken bırakılıyor (**fark 111**): kırmızı basışın bedeline dair bir uyarı, ve
basılamayan bir düğmenin bedeli yok.

## 5 · Metinler

| Ne | Bundan sonra |
|---|---|
| Tekrar dene düğmesi | "Tekrar dene — bu kareye" |
| Tekrar denendi hapı | "kuyrukta — tekrar denenecek" |
| Kuyruğa girdi hapı | nabız atan nokta (`alive`) |
| Katman onayının gövdesi | "P0_0_V1_0.mp4 ve üzerindeki ses kalıcı olarak silinir…" |
| Kare onayının başlığı | "1 kare silinsin mi?" |

Katman onayının gövdesi artık bir kalıptan üretiliyor: `DESTRUCTIVE[open].body` bir metin değil,
dosya adını alan bir fonksiyon.

## 6 · Kutular

Negatif `PromptBox`'a geçiyor. Kendi `changed` hesabı var — prompt'unki katmanı okuyor, negatifinki
karenin negatifini. `words` sözlüğüne `negative` anahtarı giriyor; hiçbir katman bu adı taşımadığı
için çakışma yok.

İki kutu da monospace (**fark 117**): yazılabilir olanın sınıfı `wf-note` → `wf-mono`, salt okunur
olanın içindeki `Note` → `Mono`.

## 7 · Oynatıcı

Zaman etiketleri, ilerleme çizgisi ve dalga sahnenin **içine** giriyor: sahne `data-scene`, satır
`data-track` ve mutlak konumlu, alt kenardan 10 yukarıda. Çizgi çerçevesini bırakıyor, yatağı saydam
beyaz oluyor; çalınmamış çubuklar da öyle. Saat beyaza ve gölgeye dönüyor — altındaki zemin artık
panel değil, videonun kendisi.

Oynat düğmesi ince çerçeve ve daha opak zemin alıyor, içindeki metin karakteri yerine çizim geliyor:
`PlayGlyph` zaten var, `PauseGlyph` ekleniyor.

Çerçeve **uzun adlarla** yazılıyor (`borderWidth` / `borderStyle` / `borderColor`) — kısayolun geri
okunacağının garantisi yok.

## Bitti sayılır

Dört komut da yeşil: 384 / 474 / 697 / 519. `dist` aynı commit'te derleniyor.
