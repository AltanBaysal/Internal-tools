# Madde 322 — Sıralama: galerinin kendi sürüklemesi, bir sıranın içinde, test turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7-kol-a` · **Tur:** 1/2 — yalnız testler, kırmızı commit'lenir.

**Kullanıcıdan gereken — yok.**

## Bugün ne oluyor

Kutu sürüklenebiliyor ve bırakınca sıra sunucuya gidiyor *(madde 300)*, ama sürükleme ekranda hiçbir
şey çizmiyor: taşınan kutu yerinde düz duruyor, imlecin altındaki kutu değişmiyor. Her kutu, hangi
sıradan gelirse gelsin, üstüne gelen her sürüklemeyi kabul ediyor *(`onDragOver` her seferinde
`preventDefault`)*: tarayıcı başka bir sıranın üstünde de *"bırakılabilir"* gösteriyor, bırakılınca
`handleDrop` tipi tutmayanı sessizce düşürüyor. `Ekle` kartı sürüklemeyi hiç dinlemiyor.

## Kurallar

1. **Taşınan kutu galerinin `.dragged`'ını giyiyor** *(Gallery.jsx, `DRAGGED` — `rotate(-3deg)
   scale(1.04) translate(14px, -10px)` ve gölge)*: sürükleme başladığı anda, bitene kadar.
2. **İmlecin altındaki kutu, aynı sıradansa, yerini galerinin kesikli yuvasına bırakıyor** —
   `2px dashed var(--accent)` *(Gallery.jsx, `SLOT`; tasarımın `.rv-tile.is-over::before`'u da aynı
   çizgi)*. Sürükleme bitince yuva gidiyor.
3. **Başka bir sıra ve `Ekle` kartı yer açmıyor.** Üstlerine gelen sürüklemenin varsayılanı iptal
   edilmiyor, yani tarayıcı orada bırakmayı kabul etmiyor ve yuva çizilmiyor; bırakılsa da hiçbir şey
   gönderilmiyor. Tasarımın kendi eli bu: `if (!refDrag || refDrag.kind !== kind) return;`,
   `preventDefault`'tan önce.
4. **Bırakınca sıra bugünkü gibi kuruluyor ve yazılıyor:** taşınan çıkıyor, yuvanın yerine giriyor,
   gerisi kayıyor; bütün sıra `saveReferenceOrder`'la gidiyor, ekran cevabı çiziyor. Hesap galerininkiyle
   zaten aynı *(Gallery.jsx `handleDrop`: süz, sonra yuvanın indeksine koy)*, değişmiyor.

**Hangi yerin bırakmayı kabul ettiği ekranın işi** *(FOUNDATION 4 — "what is enabled")*; sıranın
kendisi ve numaraları sunucunun.

**Görünüş sürükleme başlar başlamaz geliyor, galerideki gibi.** Tasarım sayfası `.dragged`'ı sıfır
süreli bir zamanlayıcıdan sonra ekliyor — tarayıcı sürükleme resmini almadan kutu eğilmesin diye;
uygulamanın galerisi eklemiyor, ve satır galeriyi söylüyor. Test `dragStart`'tan hemen sonra okuyor.

## Sunucu: değişmiyor

- `save_reference_order` başka tipten bir adı **reddetmiyor**: gönderilen her anahtarın altına,
  havuzda duran her adı tipine bakmadan yazıyor.
- Ama o ad hiçbir yere **oturmuyor**: `references.placed` her tipin listesini yalnız o tipin
  dosyalarıyla okuyor, yani `picture` altına yazılmış `dans.mp4` hiçbir fotoğraf yuvası tutmuyor ve
  H3'ün numarası kaymıyor. Tip dosyanın uzantısından geldiği için o ad hiçbir gün fotoğraf olamaz.
- Ekran zaten öyle bir sıra yollamıyor: bırakış yalnız taşınan kutunun kendi sırasını kuruyor.

322 sunucuya dokunmuyor; sunucu testi yazılmıyor.

## Yazılacak testler

### `ReferencePanel.test.jsx` — yeni blok *"dragging within a row"*

Havuz: fotoğraf sırasında `bir.png`, `iki.png`; video sırasında `dans.mp4`. Sürüklenen `iki.png`. İki
yardımcı: `slotIn(öğe)` öğenin kendisinde ya da içinde çizgisi `2px dashed var(--accent)` olanı
buluyor — `Ekle` kartının kendi kesikli çizgisi `1px dashed var(--border)`, karışmıyor; `opens(öğe)`
üstüne `dragOver` ateşleyip varsayılanın iptal edilip edilmediğini söylüyor *(`fireEvent`'in dönüşü
`dispatchEvent`'inki)*.

1. **Yeni** `lifts the tile in flight the way the gallery does, until the drag ends` —
   `dragStart(iki)`: `iki`'nin `transform`'u `rotate(-3deg)` içeriyor, `bir`'inki boş;
   `dragEnd(iki)`: `iki`'ninki boş. *Bugün kırmızı:* kutunun hiç `transform`'u yok.
2. **Yeni** `opens the gallery's dashed slot under the pointer, until the drag ends` —
   `dragStart(iki)`, `bir`'in üstüne `dragOver`: kabul ediliyor ve `bir`'de kesikli yuva var;
   `dragEnd(iki)`: havuzun hiçbir yerinde yuva yok. *Bugün kırmızı:* kabul ediliyor ama yuva çizilmiyor.
3. **Yeni** `opens no place in another row, and a drop there sends nothing` — `dragStart(iki)`,
   `dans.mp4`'ün üstüne `dragOver`: kabul edilmiyor, havuzda yuva yok; `dans.mp4`'e `drop`:
   `saveReferenceOrder` çağrılmıyor. *Bugün kırmızı:* her kutu her sürüklemeyi kabul ediyor.
4. **Yeni, bugün de geçen** `opens no place on the Ekle card, and a drop there sends nothing` —
   `dragStart(iki)`, fotoğraf sırasının kendi `Ekle` kartının üstüne `dragOver`: kabul edilmiyor, yuva
   yok; karta `drop`: hiçbir şey gönderilmiyor. Bugün kart sürüklemeyi hiç dinlemediği için geçiyor.
   **Uygulama turunun yazacağı kodu bekliyor:** sırayı bütünüyle bırakma alanı yapan bir yol *(ör.
   sıranın sonuna bırakmak için)* kartı da yer açar hâle getirirdi, ve bu test onu yakalar.

## Değişen — yok

`sends the order a drag makes` aynen kalıyor: `iki` `bir`'in üstüne sürüklenip bırakılınca sıra
`[iki, bir]` — galerinin kuralıyla da aynı cevap. Başka hiçbir test sürüklemeye dokunmuyor.

## Bekçiler

- `ReferencePanel.test.jsx`: `sends the order a drag makes` *(bırakışın sırası ve yollanışı)*;
  319'un bloğu — özellikle `follows a row's last reference with one Ekle card` *(kartın hemen önünde
  son kutu: kutulara sarmalayıcı eklemek onu kırar)* ve `draws each reference at 144 × 108 with its
  slot number on it`; 320'nin ve 321'in blokları.
- `Gallery.test.jsx`: `reports the new order when a frame is dropped`,
  `does not go to the server for a frame dropped where it already was`,
  `puts the dragged look on every card in the block` — uygulama galerinin `DRAGGED`'ını ve `SLOT`'unu
  paylaşmaya kalkarsa.
- Sunucu: `test_each_kind_counts_its_own_slots` *(`test_references.py`)*;
  `test_the_order_the_user_dragged_is_stored`, `test_a_sent_order_keeps_only_the_names_the_pool_holds`
  *(`test_reference_usecases.py`)*; `test_the_order_is_saved_and_read_back`
  *(`test_reference_routes.py` — "sayfa yenilenince sıra duruyor")*.

## Test yazılmayan

- **Yuvanın ölçüsü** *(144 × 108, tasarımın `::before`'u)* ve görünüşün geri kalanı *(gölge,
  ölçek)*: satır kesikli yuvayı ve eğilmeyi söylüyor; galerinin testi de `rotate(-3deg)`'den ötesini
  okumuyor.
- **Taşınan kutunun kendi üstünde yuva açmaması** — galerinin `!dragging`'i; satır söylemiyor,
  uygulama galeriden alır.
- **Video ve ses sıraları** — aynı bileşen, aynı yol; testler fotoğrafla yazılıyor.
- **Sıranın hesabı** — değişmiyor; bekçisi `sends the order a drag makes`.

## Bitti sayılır

Dört test satırı koşulur; `queen-editor` vitest'te 1–3 kırmızı, 4 yeşil; pytest ve `queen-agent`
satırları yeşil.
