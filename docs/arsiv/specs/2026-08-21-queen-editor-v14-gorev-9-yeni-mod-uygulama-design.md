# v14 · Görev 9 — Detayda Yeni mod seçicisi · **uygulama turu**

**Kaynak:** [test turu](2026-08-21-queen-editor-v14-gorev-9-yeni-mod-testler-design.md) — kararlar
orada verildi ve commit edilmiş yirmi üç test onları tarif ediyor.

## Değişen dosyalar

### Motor tarafı

**`domain/production_mode.py`** üç şey kazanıyor:

- `InvalidMode` — `queue_layer`'dan taşınıyor. Modlar hakkında ve artık iki kullanım durumu atıyor.
- `validate(mode, kind)` — iki satırlık kural, iki çağıranın ortak evi.
- `frame_after(gallery, fid)` — `queue_layer._frame_after`'dan taşınıyor, gövdesi ve belgesi
  olduğu gibi.

Modül artık `layers` ve `queue` içe aktarıyor. Döngü yok: `queue` yalnız `layers` ve `photo_name`
okuyor.

**`domain/usecases/queue_layer.py`** iki tanımını kaybediyor ve `production_mode`'unkileri
çağırıyor. `InvalidMode`'u dışa vermeye devam etmiyor — `routes` de artık `production_mode`'dan
alıyor, çünkü bir adın tek evi olur.

**`domain/usecases/regenerate.py`**:

- `NoNextFrame` — bağlanacak kare yok. Kendi istisnası, çünkü mod geçerli ve istek anlaşılır; olmayan
  şey hedef.
- `mode=production_mode.STANDARD` parametresi, `validate` çağrısı, ve bağlı modda `frame_after`
  ile bulunan hedef.
- Planlanan iş `mode` ve — bağlıysa — `linkedTo` taşıyor. Mod verilmemişse iş bugünkü gibi kalıyor:
  varsayılan `STANDARD` ve o da işe yazılmıyor.

**`presentation/routes.py`** gövdedeki `mode`'u geçiriyor ve iki istisnayı 400'e çeviriyor.

### Ekran tarafı

**`production_modes.js`** `nounOf(mode, plain)` kazanıyor: modun yaptığı şeyin adı, standartta
çağıranın kendi kelimesi.

**`LayerPanel.jsx`**'in `MODE_WORDS`'ü `MODE_TAIL`'e iniyor — isim ortak eve gitti, kuyruk cümlesini
söyleyen hâlâ tek yer.

**`shared/api.js`** ve **`useGeneration.js`** modu beşinci argüman olarak taşıyor.

**`PhotoDetail.jsx`** formun üç parçasını çiziyor:

- `<select>` — `wf-input`, uygulamanın kendi açılır kutusu. Varsayılanı `madeIn`, o yoksa `STANDARD`.
- Kenarlık: değiştiyse vurgu, bağlanacak kare yoksa tehlike.
- Sebep satırı ve pasif buton — iki durum, iki cümle.
- "Ne doğacak" satırı: `Yeni bir kare açılır — {id} kopyası, {isim}.`

Üçü de yalnız video sekmesinde.

## Bitti sayılır

Dört komutun dördü de yeşil. `dist` bu commit'te derleniyor.
