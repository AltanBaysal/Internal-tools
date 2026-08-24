# v14 Görev 36 — Fotoğraf inerken karonun bekleme hâli: TEST döngüsü tasarımı

**Tarih:** 2026-08-25 · **Kaynak:** Kullanıcı, 25 Ağustos
**Yol haritası:** [v14](../plans/2026-08-20-queen-editor-v14-roadmap.md) madde 36

## Sorun

İki ayrı sorun, tek bir bekleme hâlinde.

### Halka sol üstte ve deforme

`TileImage`, fotoğraf inerken yer tutucuyu çiziyor ve ona `<img>`'in kendi style'ını olduğu gibi
veriyor. O style'ın içinde `display: "block"` var — galeri karoyu öyle çiziyor, ve bir resim için
doğru olan bu.

Yer tutucu ise resim değil, `.wf-img` sınıflı bir `<div>`, ve o sınıfın işi halkayı ortalamak:
`display: flex` ile. Çağıranın `display: "block"`'u onu eziyor.

Ortalama gidince halka artık flex öğesi değil. Halka bir `<span>` ve varsayılanı `display: inline`.
**Satır içi bir öğede `width` ve `height` uygulanmaz.** 28×28'lik yuvarlak, 2px kenarlı sıfır
boyutlu bir kutuya çöküyor: satır içeriğinin başladığı yerde — sol üstte — deforme bir yay.

İki gerçek tek sebepten çıkıyor: **sol üstte olması ve deforme olması aynı şeyin iki yüzü.**
Ortalayan kutu geri geldiğinde ikisi birden düzelir; ayrı ayrı düzeltilecek iki şey değil.

Kanıt kodun kendisinde: aynı bileşen galeride üretiliyor karosu için ve detay sayfasında da
çiziliyor, ve o iki yerde çağıranın style'ı `display` taşımıyor — orada halka yuvarlak ve ortada.
Bozuk olan yalnız indirme yolu.

### Aynı anda çizgi ve halka

Bekleyen karo iki sınıf birden taşıyor: `wf-img` (gri çapraz çizgi) ve `wf-img--loading` (mor çapraz
çizgi). İkisi de aynı özelliği boyuyor, sonraki kazanıyor.

Sonuç: bekleyen karo mor çizgi + dönen halka; **hiç gelmeyen** fotoğraf gri çizgi, halkasız. Zıt iki
şey aynı dokuyu paylaşıyor ve aralarındaki farkı tek başına halka taşıyor.

## Ne test ediliyor

Karo indirirken halkasını ortalayan bir kutuda tutuyor, ve arkasında çizgi yok. Yani madde 36'nın
"bitti sayılır" cümlesi.

Bu döngüde **kod değişmiyor.** Testler yazılır, kırmızı görülür, kırmızı commit'lenir.

## Nerede test ediliyor

`TileImage.test.jsx`'te, dosyanın *what the tile shows* bloğunda. Bileşenin adı `Rendering` ama
kullanıcının gördüğü şey karo, ve o blok zaten karonun neye benzediğini anlatıyor.

Testler style'ı **galerinin verdiği style ile** çağırıyor — `display: "block"` dahil. Bugün dosyadaki
testlerin hiçbiri `TileImage`'a style geçirmiyor, dolayısıyla hiçbiri hatayı doğuramıyor: style
olmadan `display` de yok, ezilen bir şey de yok. Hatanın görülebilmesi için gerçek çağıranın
verdiğinin verilmesi gerekiyor.

## jsdom ne söyleyebilir

jsdom yerleşim hesaplamıyor: bir halkanın gerçekten yuvarlak çizildiğini hiçbir test göremez. Ama
satır içi style'ı okuyabiliyor, ve **deformasyonun sebebi tam olarak orada**: ortalayan kutu varsa
halka blok seviyesinde bir flex öğesi olur ve ölçüleri uygulanır; yoksa olmaz.

Yani `display`'in `flex` olduğunu iddia etmek, "halka ortada" ile "halka yuvarlak" iddialarının
ikisinin birden tek dayanağını iddia etmek demek. İki ayrı test yazmak, aynı şeyi iki kez sormak
olurdu.

## Yazılacak testler

| | Test | Bugün |
|---|---|---|
| 1 | Galeri `display: block` dese bile yer tutucu ortalayan bir kutu | **kırmızı** |
| 2 | Bekleyen karonun arkasında çizgi yok | **kırmızı** |
| 3 | Hiç gelmeyen fotoğrafın sessiz kutusu çizgisini koruyor | yeşil — tutucu |

Tutucu 3 boşuna değil: çizgi "piksel yok" demenin yolu ve gelmeyen fotoğrafın tek işareti o. Çizgiyi
beklemeden alırken oradan da almak, iki hâli bu kez ters yönden aynı yapardı.

Halkanın varlığını iddia eden testler dosyada zaten var (*turns while it waits its turn* ve *shows a
turning holder while the picture is coming*) — yenisi yazılmıyor.

## Kapsam dışı

- **`vendor/styles.css`.** Elle düzenlenmiyor. `.wf-spinner`'ın kendisi kusursuz; onu bozan, içine
  konduğu kutu.
- **Halkanın kendine `display` verilmesi.** Ortalayan kutu geri geldiğinde halka zaten blok
  seviyesinde bir flex öğesi oluyor; ikinci bir çare, ilkinin çalıştığını gizlerdi.
- **Diğer bekleme hâlleri** — üretiliyor karosu ve detay sayfası bugün doğru çiziliyor ve
  değişmiyor.
- **Kod.** Bu döngü yalnız test.

## Derlenmiş çıktı

Bu döngüde ön yüz **kaynağı** değişmiyor, yalnız test dosyası. `dist` tazelenmiyor.
