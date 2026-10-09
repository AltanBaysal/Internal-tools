# v14 · Görev 12 — Toplu katman silme · **uygulama turu**

**Kaynak:** [test turu](2026-08-21-queen-editor-v14-gorev-12-toplu-katman-silme-testler-design.md) —
kararlar orada verildi ve commit edilmiş 18 test onları tarif ediyor.

## Değişen dosyalar

| Dosya | Ne kazanıyor |
|---|---|
| `domain/frame_list.py` | **yeni** — kimlik listesinin tek kuralı |
| `domain/usecases/remove_frames.py` | `InvalidFiles`'ı bırakıyor |
| `domain/usecases/copy_frames.py` | kendi `InvalidFrames`'ini bırakıyor |
| `domain/usecases/remove_layer.py` | çoğul imza, tek geçişli hesap, atlama |
| `presentation/routes.py` | gövde `frames`, 400 |
| `frontend/src/shared/api.js` | çağrı listeye dönüyor |
| `…/useGeneration.js` | kancanın imzası |
| `…/PhotoDetail.jsx` | tek elemanlı liste |
| `…/ProjectScreen.jsx` | galeriye bağlanması |
| `…/layer_words.js` | düğmelerin ve pencerelerin sözleri |
| `…/Gallery.jsx` | iki düğme, iki pencere |

### 1 · Gövde kuralı ortak eve

`frame_list.py` iki şey taşıyor: `InvalidFrames` ve `checked(frames, what)`. `what` yalnız cümlenin
başındaki fiil — "Silinecek", "Kopyalanacak", "Katmanı silinecek" — yani hangi işin reddedildiği
mesajda duruyor ve kural tek yerde.

`remove_frames`'in `InvalidFiles`'ı gidiyor. Adı zaten bayattı: rota `body.get("frames")` okuyor,
gövdede `files` diye bir şey yok.

### 2 · Tek geçişli hesap

`remove_layer` artık kimlik listesi alıyor ve `remove_frames`'in biçimini alıyor: **hangi dosyaların
gideceği tek satır yazılmadan önce** hesaplanıyor.

Bu bir üslup tercihi değil, doğruluk şartı. Bir videoyu iki kare tutuyorsa ve ikisi de aynı basışta
bırakıyorsa dosya gitmeli. Kare kare gidilseydi ikinci kare hesaplanırken birincinin satırı henüz
kayda yansımamış olabilir, ve dosya diskte kalırdı.

İki liste hazırlanıyor: kapanacak yuvalar, ve kapanan katmanın **üstünde** kuyruğun hâlâ borçlu
olduğu işler. İkincisi bugünkü kuralın aynısı, yalnız artık kare kare değil basış başına.

Bilinmeyen kimlik `continue` ile atlanıyor; `FrameMissing` bu kullanım durumundan çıkıyor.

### 3 · Sözler `layer_words.js`'te

`LAYER_ACTIONS` iki satır: hangi katman, düğme ne diyor, karenin o katmanı için hangi ad kullanılıyor
(`videosu` / `sesi`), ve pencerede ne kaldığı.

`layerConfirm(layer, held, selected)` pencerenin tamamını veriyor — başlık, gövde, **ve genişlik**.
Genişliğin sözlerle gelmesi madde 105: atlama cümlesi olan pencere bir beden daha geniş (420),
olmayan 400.

Bu dosyanın kendi cümlesi zaten şunu diyordu: *"the gallery's tile badges and the two delete confirms
have to agree"*. Üçüncü ve dördüncü pencere de aynı eve giriyor.

### 4 · Galeride pencere artık isimli

`confirming` bir bayrak değil, **hangi pencere**: `null` / `"frames"` / `"video"` / `"audio"`. Aynı
anda bir pencere açık, ve durumun kendisi hangisi olduğunu söylüyor. Escape ve Ctrl + D'nin
`if (confirming) return` koruması olduğu gibi çalışıyor — `null` yanlış değerdir.

Kırmızı düğme biçimi üç düğmede birden kullanıldığı için modül sabitine çıkıyor (`DANGER`), detay
sayfasında zaten öyle duruyor.

`holding(layer)` seçimin o katmanı gerçekten taşıyan yarısını veriyor — `layer_words.owned` ile, yani
galerinin karoya yazdığı sözle. Hem düğmenin çizilip çizilmeyeceğini hem pencerenin sayısını hem de
gönderilen listeyi o belirliyor: üçü tek cevaptan çıkıyor.

## Bitti sayılır

Dört komutun dördü de yeşil. `dist` bu commit'te derleniyor, yol haritası 12/31 oluyor.
