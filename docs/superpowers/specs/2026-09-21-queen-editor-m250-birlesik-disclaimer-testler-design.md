# Madde 250 · Birleşik export'ta disclaimer ilk 1 dakika — test turunun tasarımı

**Tarih:** 21 Eylül 2026 · **Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md) ·
**Öncesi:** [249'un uygulama turu](2026-09-21-queen-editor-m249-disclaimer-uygulama-design.md)

## Kullanıcıdan gereken

Hiçbir şey. PNG 249'da geldi ve yerinde duruyor; süre, duruş ve sınır karesi kararı da 21 Eylül'de
align olundu.

## Bugün ne oluyor

Birleşik export parçaları makinenin diskinde kesiyor — 249'dan sonra **temiz kopya**, bindirme yok —
ve `merge()` onları `concat` ile kopyalayarak birleştiriyor. Birleşmiş dosyada disclaimer hiç yok.

`merge()` bugün iki şey yapıyor: her parçaya ölçüsünü soruyor *(madde 218'den beri: kopyalayarak
birleştirmek yalnız ölçüler aynıyken doğru)*, sonra `concat` listesini yazıp ffmpeg'i koşuyor ve
listeyi siliyor.

## Seçilen yol

**Bindirme birleştirmenin kendi çağrısında.** `concat` girdisinin üstüne aynı ffmpeg çağrısında
biniyor: birleştirme zaten tek bir okuma, ve filtre o okumanın üstünde duruyor. Böylece

- **saat doğru saat olur** — `enable='lt(t,60)'` birleşmiş zaman çizgisinin `t`'sine bakıyor, yani
  60. saniye parçanın ortasına düşse de disclaimer tam orada kalkıyor *(kullanıcı kararı)*;
- **parça başına hesap yok** — hangi karenin kaçıncı saniyede başladığını kimsenin bilmesi
  gerekmiyor, ffmpeg zaten birleşmiş akışı sayıyor;
- **yol haritasının `concat` riski hiç doğmuyor** — yeniden kodlanmış parçayla kopyalanmış parça yan
  yana gelmiyor, çünkü parçaların hepsi kopya ve kodlama birleşmiş akışın üstünde bir kez oluyor.

**Ölçü sorusu yerinde kalıyor.** `merge()` parçalara ölçüsünü sormaya devam ediyor, ve ayrı
ölçüler yine birleştirmeyi durduruyor. Bindirme kodlama getirdiği için *"farklı ölçüler bozuk dosya
yazar"* gerekçesi zayıflıyor, ama madde bunu değiştirmiyor: iki oranı tek dosyada birleştirmenin
cevabı kullanıcının hiç istemediği bir kırpma ya da bir bant olurdu, ve o kararı 218 verdi.

**Ölçek aynı kaynaktan.** Bindirmenin genişliği ve alt boşluğu birleşmiş videonun ölçüsünden
geliyor — ki o da parçaların ölçüsü, `merge()` zaten elinde tutuyor. Yeni bir ffprobe çağrısı yok:
249'un `_stamp()`'i o ölçüyü videodan okuyor, burada ise zaten okunmuş olanı kullanıyor.

## Çivilenecek olgular

| # | Ne diyor | Bugün |
|---|---|---|
| 1 | Birleştirme tek çağrıda hem birleştiriyor hem bindiriyor: `concat` girdisi, PNG ikinci girdi, `overlay=...:enable='lt(t,60)'`, `libx264` | **kırmızı** |
| 2 | Bindirmenin sayıları parçalara sorulan ölçüden geliyor: `848x480` parçalarda `scale=678` ve alt boşluk `19` | **kırmızı** |
| 3 | `concat` listesi yine yazılıp yine siliniyor | **yeşil** *(249 dokunmadı, 250 de bozmamalı)* |
| 4 | Ayrı ölçüler birleştirmeyi yine durduruyor, ve hiçbir şey yazılmıyor | **yeşil** *(duran iki test; bindirme bu kuralı kaldırmıyor)* |
| 5 | Parçalar yine temiz kesiliyor — birleşik modda hiçbir parça bindirme taşımıyor | **yeşil** *(249'un `a_merged_export_cuts_its_pieces_clean`'i; burada tekrarlanmıyor)* |

3, 4 ve 5 duran testlerin işi, ve bu turda yeni bir test almıyorlar: 3 ile 4'ü
`test_merging_hands_ffmpeg_a_list_and_takes_it_away_again`, `test_mixed_sizes_stop_the_merge_and_name_what_was_found`
ve `test_nothing_is_merged_when_the_sizes_disagree` tutuyor — üçü de yeni komutta aynı şeyi görmeye
devam ediyor. Takım iki kırmızıyla toplanıyor.

**Bir şey bilerek çivilenmiyor:** 60. saniyeye ortasından denk gelen karenin kendisi. Testin
görebileceği şey komut, ve komutta duran `enable='lt(t,60)'` o kararın tamamı — kaç parçanın
bindirme taşıdığını ffmpeg'e sormanın yolu, ffmpeg'i koşmak.

## Bu turda değişen

`backend/tests/test_export.py`, iki yeni test:

- `a_merged_export_joins_and_stamps_in_one_call` *(1)*
- `the_merged_disclaimer_is_measured_from_the_pieces_it_joins` *(2)*

`STAMP` ve `ENCODE` sabitleri 249'da yazıldı ve burada da kullanılıyor: bindirme aynı bindirme,
yalnız bindiği akış farklı.
