# v13 Görev 1 — Galeri resim kuyruğu: İMPLEMENTASYON döngüsü (tasarım)

**Tarih:** 2026-08-14 · **Araç:** queen-editor · **Dal:** `feat/queen-editor-v3`
**Yol haritası:** [v13](../plans/2026-08-14-queen-editor-v13-roadmap.md) · **Döngü:** 2/2
**Testler:** [test spec'i](2026-08-14-queen-editor-v13-gorev-1-testler-design.md) ·
commit `1017c98` (on dört test kırmızı)

## Ne geliyor

**Kuyruk bir sayaç ve bir sıra tutar.** Uçuştaki sayı tavanın altındayken sıranın başındakine slot
verilir; tavan doluyken isteyen sıraya girer. Bir bilet bırakıldığında slot geri döner ve sıra
ilerler. Vazgeçmiş bir bilet sırada bulunduğunda atlanır — ama **atlanırken durulmaz**, yoksa
ekrandan çıkmış tek bir karo arkasındaki her karoyu rehin alırdı. Bir bilet ne kadar çok
bırakılırsa bırakılsın bir slot açar; yüklenip sonra ekrandan kalkan karo tam olarak iki kez
bırakıyor.

**Karo üç şeyi bağlar.** Gözlemci ona yaklaştığını söyler, kuyruk sırasının geldiğini söyler,
`<img>` işinin bittiğini söyler. Bileti bir referansta tutar, çünkü onu bırakan dört yol var ve
üçü olaydan geliyor: `load`, `error`, uzaklaşma, sökülme. Dördü de aynı çağrıya çıkıyor — bırakma
tek yol olduğu için hiçbiri unutulamıyor.

**Gözlemcisi olmayan tarayıcıda karo baştan "yakın" doğar.** Bu bir zarafet değil, hayatta kalma:
olmayan bir yapıcıya `new` demek olduğu yerde patlar ve galeriyi komple götürür. jsdom da öyle bir
tarayıcı, ve mevcut `Gallery.test.jsx` takımını ayakta tutan şey bu satır.

**`Gallery.jsx`'in `<img>`'i `<TileImage>` olur.** `loading="lazy"` gider: `src`'yi artık kuyruk
veriyor ve karo zaten ekrana yaklaşmışken o öznitelik ikinci bir kapıdan başka bir şey değil.
Karonun geri kalanı — bağlantı, rozetler, sürükleme, seçim — tek satır değişmiyor.

## Bunun bir şey kaybettirdiği yer

**Galeri artık karo karo dolar.** Aynı anda iki resim indiği için büyük bir galeride dolma gözle
görülür biçimde sıralı olur. Kabul: tıkanmayı çözen şey bu, ve hızı getirecek olan küçük önizleme
kendi tasarımını bekliyor. Tavan kırılmayı durdurur, hızı önizleme getirir.

**Her karo kendi gözlemcisini yaratır.** Yüz karo yüz gözlemci demek. Paylaşılan tek bir gözlemci
mümkün ama bir kayıt defteri ve sökülme muhasebesi ister; bu görev bir tıkanmayı çözüyor, gözlemci
altyapısı yazmıyor. Ölçülmüş bir maliyeti yok, ve olursa kendi görevi olur.

## Kalan risk, açıkça

**Tavan doğru şeyi çözmüyor olabilir.** Çekişmenin bağlantı slotu mu bant doygunluğu mu olduğu
ölçülmedi (test spec'inde tablosu var). İkisini de aynı tavan düşürür, ama üçüncü bir sebep varsa
tavan onu düşürmez. Colab turunda zaman aşımı sürerse ilk iş DevTools'ta `Stalled` ile
`Content Download` süresine bakmak — o iki sayı hangi hikâyenin doğru olduğunu tek başına söyler.

**Yaklaşma payı bir tahmin.** Gözlemcinin görüş alanından ne kadar önce tetikleneceği (`rootMargin`)
ölçüyle değil muhakemeyle seçiliyor: dar olursa karo boş görünüp sonra dolar, geniş olursa bakılmamış
karolar sıraya girip tavanı yer. Turdan sonra ayarlanacak bir sayı, ve tek yerde duruyor.

Burada tarayıcı yok; bu spec ikisini de çözemez, sakladığı da yok.

## Değişen yerler

| Dosya | Ne olacak |
|---|---|
| `.../shared/image_queue.js` | iskeletin yerine tavan, sıra ve slot iadesi |
| `.../photo_generation/TileImage.jsx` | iskeletin yerine gözlemci, bilet ve bırakma |
| `.../photo_generation/Gallery.jsx` | `state === "done"` dalındaki `<img>` `<TileImage>` olur |
| `queen-editor/frontend/dist/` | yeniden derlenir (aynı commit) |

## Bitti sayılır

`npm test --prefix queen-editor/frontend` → 353 geçen, 0 düşen. `dist/` aynı commit'te yeniden
derlenmiş olur. Galerinin gerçekten açıldığı ve zaman aşımının gittiği Colab turunun cevabı.
