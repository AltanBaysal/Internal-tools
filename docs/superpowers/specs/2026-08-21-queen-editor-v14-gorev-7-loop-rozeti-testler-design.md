# v14 · Görev 7 — Galeride loop rozeti · **test turu**

**Kaynak:** [yol haritası v14](../plans/2026-08-20-queen-editor-v14-roadmap.md) 7. madde —
[İstek 3](../plans/2026-08-20-queen-editor-istekler.md) ve
[fark listesi](../research/2026-08-20-queen-editor-tasarim-v4-farklari.md) 63.

## Sorun

Fark 63: *"loop modunda üretilmiş videosu olan kare sol altta 'video' yerine 'loop' yazar; ikisi aynı
yeri paylaşır, bir arada asla görünmez. Sesi de varsa yanına 'ses' eklenir."*

Bugün loop videolu kare öteki videolu karelerle aynı rozeti taşıyor — çünkü **üretilmiş bir videonun
modu hiçbir yerde yazılı değil.** Mod kuyruktaki işe yazılıyor (2. madde) ve motor onu okuyup bitiş
karesini seçiyor, ama iş bitip satır yazıldığında mod satırla birlikte gelmiyor. Rozet bir yana,
detay sayfası da (8. madde) aynı bilgiyi soracak.

Yani bu madde bir rozetten fazlası: **modun kayda geçmesi** ve oradan galeriye ulaşması.

## Zincir

```
run_loop        işin modunu üretilen katmanın satırına yazar
photo_record    satırdaki modu hücreye katlar
list_frames     kareye modes: {video: "loop"} olarak verir
owned()         video satırının kelimesini "loop" ile değiştirir
```

## Kararlar

### 1 · Mod kayda geçiyor, plandan türetilmiyor

Plan ne istendiğini söylüyor, kayıt ne olduğunu — `list_frames`'in kendi başlığındaki ayrım. Rozet
var olan videonun ne olduğunu söylüyor, dolayısıyla kaynağı kayıt.

Plandan okumak da mümkündü: iş orada duruyor ve modu üstünde. Ama bir karenin videosu silinip
yeniden yapılabiliyor ve planda o karenin iki video işi kalıyor; hangisinin ekrandaki videoyu
ürettiğini plan söylemiyor.

### 2 · Modu olmayan iş satırına mod yazmıyor

Modu yalnız video işi taşıyor — `queue_layer` alanı yalnız ona koyuyor. Motor bu kuralı ikinci kez
yazmıyor: işin alanı varsa satıra geçiyor, yoksa geçmiyor. Fotoğrafın ve sesin her satırına
`"standard"` yazmak, göründüğü satırların neredeyse tamamında hiçbir şey söylemeyen bir alan olurdu.

Yazılan değer motorun render sırasında okuduğu değerin aynısı (`production_mode.of`), çünkü satırın
işi videonun ne olduğunu söylemek.

### 3 · Karenin alanı bir harita: `modes: {layer: mode}`

`errors: {layer: sebep}` ile birebir aynı şekil, aynı kural: yalnız satırında mod olan katmanlar
haritada. Bugün tek anahtarlı bir harita, çünkü modu olan tek katman video.

Düz bir `videoMode` alanı da olurdu. Olmadı, çünkü ikinci bir katman mod kazandığı gün adının
değişmesi gerekirdi — ve hem galeri hem detay sayfası aynı soruyu soruyor: *bu katman hangi modda
yapıldı.*

### 4 · Kopyalanan katman modunu da götürüyor

`carry_layers`, ses kopyasına kaynağın video satırını veriyor. Mod gitmezse ikizin karosu "video"
yazarken aslının karosu "loop" yazar — aynı dosya için iki ayrı cevap.

### 5 · Kelime değiştiriliyor, eklenmiyor

`owned()` katman başına tek satır döndürüyor; loop kelimesi video satırının kelimesinin yerine
geçiyor. "Bir arada asla görünmez" böylece bir kuralla değil, yapıyla sağlanıyor — ortada ikinci bir
satır yok.

### 6 · Küçük harfle "loop"

Panelin etiketi "Loop", çünkü orası bir seçim listesinin satırı. Bu ise fotoğrafın üstüne konan bir
kelime ve komşuları "video" ile "ses".

### 7 · Silme onayı değişmiyor

`lostLayers` katmana göre sayıyor, karonun kelimesine göre değil: silinecek olan hâlâ bir video.

### 8 · Bağlı modun rozeti yok

Fark 63 yalnız loop'u anıyor. Bağlı video da bir video; nereye vardığı detay sayfasının işi
(8. madde).

## Yazılacak testler

**Motor — `test_photo_usecases.py`**

1. Loop işinin ürettiği satır modunu söylüyor.
2. Standart video işinin satırı da söylüyor — ikisi ayırt edilebilsin diye.
3. Mod alanı taşımayan bir iş satırına mod yazmıyor.

**Kayıt — `test_photo_record.py`**

4. Satırdaki mod hücreye katlanıyor.
5. Modsuz satırın hücresinde anahtar hiç yok.

**Galeri cevabı — `test_photo_usecases.py`**

6. `list_frames` kareye `modes: {"video": "loop"}` veriyor.
7. Modsuz videonun karesinde anahtar hiç yok.

**Kopya — `test_photo_usecases.py`**

8. Ses kopyası kaynağın video modunu da götürüyor.

**Karo — `Gallery.test.jsx`**

9. Loop videolu kare "loop" yazıyor.
10. Aynı karede "video" hiç görünmüyor.
11. Standart videolu kare "video" yazmaya devam ediyor.
12. Sesi de olan loop karesi "loop" ve "ses" yazıyor.
13. Patlamış bir loop videosu hiçbir kelime taşımıyor — o karo hapın işi.

**Değişen sahte:** `FakeRecord.slots` gerçek kaydı taklit ediyor, dolayısıyla o da modu hücreye
katlıyor. Sahtenin gerçeğinden geri kalması, motor testlerini gerçekte olmayan bir dünyada
koştururdu.

## Bitti sayılır

Dört komutun dördü de koşuyor, on üç testin dokuzu kırmızı çıkıyor ve commit ediliyor. Kaynak
dosyalara bu turda dokunulmuyor.

Dördü doğuştan yeşil: 3 ve 5 birer yokluk ölçüyor (`mode` alanı bugün hiç yazılmıyor), 11 ve 13
bugünkü doğru davranışı tarif ediyor (düz video "video" der, patlamış katman hiçbir şey demez).
Nöbetleri uygulama turundan sonra başlıyor.
