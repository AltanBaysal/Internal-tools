# v14 Görev 37 — Export fotoğrafları da taşır: TEST döngüsü tasarımı

**Tarih:** 2026-08-25 · **Kaynak:** Kullanıcı, 25 Ağustos
**Yol haritası:** [v14](../plans/2026-08-20-queen-editor-v14-roadmap.md) madde 37

## Sorun

Export bugün yalnız video yazıyor: her kare için `01.mp4`, `02.mp4`…, birleşik modda bir de
`<proje>.mp4`. Fotoğraflar hiç girmiyor, ve dışarı taşınan bir işten geriye yalnız videolar kalıyor.

## Ne test ediliyor

Videosu yazılan her kare, fotoğrafını da exportun içindeki `photos/` klasörüne bırakıyor — videosuyla
**aynı numarayla**. Yani `01.mp4`'ün karesinin fotoğrafı `01.png`.

Ve aynı fotoğraf iki kez yazılmıyor.

Bu döngüde **kod değişmiyor.** Testler yazılır, kırmızı görülür, kırmızı commit'lenir.

## İki modun aynı klasöre inmesi

Kullanıcının sorduğu yer, ve deponun kendisi doğruluyor: `make_export_folder` klasörü dakikaya kadar
adlandırıyor ve `exist_ok=True` ile açıyor. Yorumu da bunu söylüyor — *"aynı açılışın iki exportu tek
klasöre iner"*. Birleşik ve ayrı aynı dakikada alınırsa `photos/` ikisinin ortak klasörü olur.

İki mod da `exportable()`'ın verdiği aynı sırayı yürüdüğü için `01` iki modda da aynı kare. Yani
ikinci modun yazacağı şey, birincinin yazdığının aynısı.

## Kural nerede duruyor

**"Zaten oradaysa dokunma" deponun işi, alanın değil.**

Alan katmanı sorup sonra yazsaydı, iki iş parçacığı arasında bir aralık kalırdı: ikisi de "yok"
görür, ikisi de yazar, ve aynı dosyaya birlikte yazan iki kopyalama yarım dosya demektir. Depo
tarafında karar tek bir işlemin içinde kalıyor.

Bunun testler açısından sonucu: **iki ayrı dosyada iki ayrı test.**

- `test_export.py` — alan katmanı: fotoğraf depoya doğru numarayla veriliyor mu, videosu olmayan
  kare bir şey veriyor mu.
- `test_photo_store.py` — depo: aynı hedefe ikinci kez kopyalama ne yapıyor.

Alan testinin sahte deposu "varsa atla" kuralını taklit etmiyor. Etseydi test kodu değil kendi
sahtesini sınardı.

## Uzantı varsayılmıyor

Numara exportun, uzantı fotoğrafın. `.png` sabit yazılmıyor: kaynak dosya `.jpg` ise export de
`02.jpg` olur. Bugün kayıtlar `.png` taşıyor ama bunu koda gömmek, ilk `.jpg` geldiğinde adı yanlış
olan bir dosya demek.

## Yazılacak testler

`test_export.py`'de üçü:

| | Test | Bugün |
|---|---|---|
| 1 | Her exporte giren karenin fotoğrafı videosunun numarasıyla veriliyor | **kırmızı** |
| 2 | Kaynağın uzantısı korunuyor | **kırmızı** |
| 3 | Videosu olmayan kare fotoğrafını da vermiyor | **kırmızı** |

`test_photo_store.py`'de biri:

| | Test | Bugün |
|---|---|---|
| 4 | Aynı hedefe ikinci kopyalama dosyayı yeniden yazmıyor | **kırmızı** |

**Dördü de bugün düşüyor, tutucu dahil.** Üçüncüsü "videosu olmayan bir şey vermez" diyor ama
bugün *hiçbir* kare bir şey vermiyor, yani sayı tutmaz. Anlamını uygulamadan sonra kazanıyor: orada
koruduğu şey, `photos/`'un `.mp4` listesiyle birebir kalması — "bütün kareler"e kaymaması. Kullanıcının
kararı orada duruyor.

## Bilerek test edilmeyen

- **İptal ve hata.** `remove_dir(folder)` klasörü olduğu gibi alıyor ve `photos/` onun içinde;
  mevcut iki test (`store.removed == [FOLDER]`) bunu zaten söylüyor. Yeni bir cümle eklemezdi.
- **İlerleme sayacı.** `written`/`total` videoyu sayıyor ve saymaya devam ediyor; fotoğraf
  videosunun yanında gidiyor, ayrı bir adım değil. Mevcut test bunu zaten tutuyor.

## Kapsam dışı

- **Ön yüz.** Export ekranının özeti video sayıyor ve o cümle değişmiyor.
- **Videosu olmayan karelerin fotoğrafları.** Kullanıcı kararı: `photos/` yalnız exporta gireni
  taşır.
- **Kod.** Bu döngü yalnız test.

## Derlenmiş çıktı

Bu iş arka yüzde. Ön yüz kaynağı hiç açılmıyor, `dist` tazelenmiyor.
