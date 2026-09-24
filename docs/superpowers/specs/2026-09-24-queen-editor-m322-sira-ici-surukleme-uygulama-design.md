# Madde 322 — Sıralama: galerinin kendi sürüklemesi, bir sıranın içinde, uygulama turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7-kol-a` *(Kol A)* · **Tur:** 2/2 — takım yeşile döner.

**Testler:** [m322 test turu](2026-09-24-queen-editor-m322-sira-ici-surukleme-testler-design.md),
`5ec2322d`.

## Sunucu

Değişmiyor — test turunun *"Sunucu: değişmiyor"* bölümü.

## Ekran — `ReferencePanel.jsx`

- **Sürüklemenin iki yarısı.** Bırakışın okuduğu, bugünkü gibi bir ref: `drag.current = { kind,
  name }`. Çizilen, iki state: `lifted` *(taşınan kutunun adı)* ve `over` *(yeri açılan kutunun
  adı)*. Ref kalıyor, çünkü bırakış sürüklemenin başlangıcının yazdığını, tarayıcı ikisini nasıl
  toplarsa toplasın okumak zorunda — bugünkü `sends the order a drag makes` üç olayı tek `act`
  içinde ateşliyor ve bırakış hâlâ ilk çizimin elinden geliyor. Ad, çünkü sıra adla anahtarlı.
- **`DRAGGED`** galerininkinin kopyası *(Gallery.jsx, `DRAGGED` — tasarımın `.dragged`'ı)*, yorumu
  nereden geldiğini söylüyor. `lifted` kutu `{ ...TILE, ...DRAGGED }` giyiyor.
- **`SLOT`** havuzun kendisi: tasarımın `.rv-tile.is-over::before`'u — `position: absolute`, sol üst,
  144 × 108, `2px dashed var(--accent)`, `var(--r-sm)`, `var(--bg-3)`. Kutunun **son** çocuğu olarak
  çiziliyor, yani yüzün, numaranın ve ×'in üstünde duruyor *(`--bg-3` opak)*. Ad ve süre satırları
  `visibility: hidden` alıyor: yerlerinde kalıyorlar, sıra yüksekliğini koruyor — galerinin gizli
  başlığı, tasarımın `> * { visibility: hidden }`'ı.
- **Yer açan:** `handleDragOver(kind, name, event)` — sürüklenen bu sıranın tipinden değilse hiçbir
  şey yapmıyor *(varsayılan duruyor, tarayıcı bırakış göstermiyor)*; öyleyse `preventDefault` ve
  `setOver(name)`. `Ekle` kartı sürüklemeyi hiç dinlemiyor, dinlemeye de başlamıyor.
- **Taşınan kutu kendi üstünde yer açmıyor:** `open = over === row.name && lifted !== row.name` —
  galerinin `!dragging`'i. Kendi üstüne dönünce başka yerdeki yuva da gidiyor, galerideki gibi.
- **`handleDragStart(kind, name)`** ref'i ve `lifted`'ı yazıyor. **`endDrag()`** ref'i ve iki
  state'i boşaltıyor; `onDragEnd` onu çağırıyor, `handleDrop` da ref'i
  okuduktan hemen sonra. Sıranın hesabı ve yollanışı olduğu gibi.
- **`Tile`** `lifted`, `open`, `onDragOver`, `onDragEnd` alıyor; bugünkü satır içi `preventDefault`
  gidiyor.
- **Kol B'nin satırları** *(bileşenin docstring'i, imza, havuzun `useState`'i, `setPool`)*:
  dokunulmuyor. Yeni state'ler `drag` ref'inin hemen altında.

### Seçilmeyen yollar

- **Sürüklemenin tamamı state'te.** Bugünkü bekçi kırılırdı: tek `act` içinde bırakış, başlangıcın
  state'ini henüz görmeyen çizimin elinden geliyor.
- **Galerinin `DRAGGED`'ını paylaşmak.** Bu klasörde hiçbir bileşen dosyası düz bir değer dışa
  vermiyor; paylaşılan değerler kendi `.js` modüllerinde *(`layer_words.js`)*. O yol yeni bir dosya
  ve galeriye bir değişiklik — kopyadan fazla parça. Havuz tasarımın ölçülerini zaten kendi üstünde
  taşıyor *(`.rv-*`)*; `.dragged` da onlardan biri. `SLOT` zaten paylaşılamaz: galerininki kare,
  havuzunki 144 × 108.
- **Yüzü yuvayla değiştirmek** *(galerinin yolu)*. Yuva her yer değiştirdiğinde video kutusunun
  `<video>`'su sökülüp yeniden kurulurdu, ilk karesi yeniden yüklenirdi. Tasarım çocukları yerinde
  bırakıp üstlerine çiziyor.
- **Kutuyu gizleyip yalnız yuvayı göstermek.** Gizli bir öğe imleci almıyor: yuva çizili dururken ad
  satırının şeridi bırakışı kabul etmezdi.

**Resim kendisi sürüklenmiyor** *(`draggable={false}`, galerinin resmi gibi)* — koşucunun
kontrolünde eklendi. Tarayıcıda resim kendiliğinden sürüklenebilir; açık kalsa imlecin altında kutu
değil çıplak resim giderdi. Test sormuyor: jsdom sürükleme görüntüsü çizmiyor.

## Doğruluğunu yitiren yorumlar

| Dosya | Olacak |
|---|---|
| `ReferencePanel.jsx` — `drag` ref'i | *"nothing is drawn from it"* doğru kalıyor ama eksik: çizilen, yanındaki iki state |

## Dist

Kolda derlenmez — [yol haritası](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md), *320–324 iki
paralel kolda*: birleşme commit'i bir kez derler.

## Bitti sayılır

Dört test satırı yeşil; kod, spec ve plan tek commit.
