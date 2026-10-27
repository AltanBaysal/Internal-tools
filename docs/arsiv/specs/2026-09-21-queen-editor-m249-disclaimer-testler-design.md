# Madde 249 · Tekli export'ta disclaimer — test turunun tasarımı

**Tarih:** 21 Eylül 2026 · **Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md)

## Kullanıcıdan gereken

**Disclaimer PNG'si** — bu turda değil, implementasyon turunda. Testler dosyanın *piksellerine* değil
*ölçüsünden çıkan sayılara* bakıyor, ve o sayılar videodan geliyor; ama depoda duran bir dosya
olduğunu çivileyen bir test var, ve o dosya gelene kadar kırmızı kalıyor — bu turda kalması gereken
renk de o.

Kullanıcıyla 21 Eylül'de align olunan ve burada tartışılmayan kararlar: **genişliğin %80'i**, alt
kenardan **yüksekliğin %4'ü**, PNG'nin **kendi saydamlığı**, videoların **hepsi**, ve **60 saniye**.

## Bugün ne oluyor

`FfmpegVideoExporter.piece()` kareyi kopyalıyor: sessizse `-c copy`, sesliyse ses `aac`'ye kodlanıp
video yine kopyalanıyor *(`data/ffmpeg_video_exporter.py`)*. Videonun görüntüsüne dokunan hiçbir şey
yok, ve export'un saniyeler sürmesinin sebebi bu.

`run_export` iki modu ayırıyor *(`domain/usecases/run_export.py`)*: `separate`'in parçaları
export'un kendisi, `merged`'in parçaları birleştirmenin iskelesi.

## Seçilen yol

**Bindirme `piece()`'in içinde, ve ayrı ayrı export'a özel.** `piece()` bir `disclaimer` bayrağı
alıyor; `run_export` onu `mode != MERGED` ile veriyor. Birleşik modun parçaları temiz kalıyor, çünkü
250'de disclaimer birleşmiş dosyanın saatine bakacak ve parçaların saatine bakan bir bindirme oraya
yanlış cevap verir.

**Sayılar videodan okunuyor, sabit piksel yok.** Genişlik ve alt boşluk `size()`'ın ffprobe'dan
aldığı ölçüden hesaplanıyor — 480 × 720'de `384` ve `29`. ffmpeg'in kendi ifadeleriyle yapılabilecek
tek şey ortalamak *(`(W-w)/2`)*; ölçeklemenin videonun genişliğini bilmesi gerekiyor, ve onu bilen
ffmpeg filtresi `scale2ref` — kullanımdan kalkıyor. `size()` zaten bu dosyada duruyor ve hatasını
ffprobe'un kendi sözleriyle söylüyor.

**Bindirme kopyalamayı bitiriyor.** Görüntü `libx264` ile yeniden kodlanıyor; sesin yolu değişmiyor.
Kodlama ayarı `-preset veryfast -crf 18 -pix_fmt yuv420p`: `veryfast` Colab'ın CPU'sunda en az
bekletendir, `crf 18` gözle kayıpsıza yakındır, `yuv420p` de dosyanın her oynatıcıda açılmasını
sağlar.

**PNG girdi sırasında ikinci, ses üçüncü.** Bugün ses ikinci girdi; PNG'yi sona koymak filtrenin
girdi numarasını sesin varlığına bağlardı. Sıra `video, PNG, ses` olunca filtre her iki durumda
`[1:v]` diyor.

**Dosya depoda, grafikler gibi.** `queen-editor/disclaimer.png`, ve yerini `config.py` söylüyor —
`WORKFLOW_PATH` ile aynı kalıp. `main.py` onu `FfmpegVideoExporter`'a veriyor, testler kendi yolunu
veriyor.

## Çivilenecek olgular

| # | Ne diyor | Bugün |
|---|---|---|
| 1 | Sessiz bir parça, disclaimer istendiğinde: PNG ikinci girdi, `scale=384:-1`, `overlay=(W-w)/2:H-h-29:enable='lt(t,60)'`, `libx264` | **kırmızı** |
| 2 | Sesli bir parça: PNG ikinci, ses üçüncü girdi; `-map [v] -map 2:a:0`, ses yine `aac` ve `-shortest` | **kırmızı** |
| 3 | Sayılar videonun ölçüsünden geliyor: `848x480` bir videoda `scale=678` ve alt boşluk `19` | **kırmızı** |
| 4 | Disclaimer istenmediğinde komut bugünkü kalıyor — `-c copy`, yeniden kodlama yok | **yeşil** *(bugünkü davranış; bayrağın varsayılanını çiviliyor)* |
| 5 | `separate` export'ta `run_export` her parça için disclaimer istiyor | **kırmızı** |
| 6 | `merged` export'ta hiçbir parça için istemiyor | **yeşil** *(bayrak yok; 250'ye kadar öyle kalacağını çiviliyor)* |
| 7 | `config.DISCLAIMER_PATH`'in gösterdiği dosya depoda duruyor | **kırmızı** *(dosya henüz yok)* |

4 ve 6 bugün de geçiyor, ve bilerek: ikisi de bu turda *değişmemesi* gereken şeyi tutuyor. 4'ü
zaten duran `a_silent_piece_is_copied_rather_than_re_encoded` tutuyor — bayrağın varsayılanı `False`
olduğu için o test yeni imzada da aynı komutu görüyor, ve yeni bir test yazmak onun ikinci kopyası
olurdu. Takım yeşil toplanmıyor: 1, 2, 3, 5 ve 7 kırmızı.

**Ölçek oranı ve saniye testte ikinci kez yazılmıyor.** Komutun içindeki `384`, `29` ve `60`
hesabın sonucu, oranın kendisi değil: `0.8` ve `0.04` yalnız üretim kodunda duruyor. m248'in
gerekçesi — elle verilmiş bir karar iki yerde durmaz — burada oranlar için geçerli, sonuçlar için
değil, çünkü test edilen şey komutun kendisi.

## Bu turda değişen

`backend/tests/test_export.py`, altı yeni test *(hepsi mevcut `FakeRun` ve `FakeExporter` ile —
yeni bir iskele yok)*:

- `a_stamped_piece_carries_the_disclaimer_over_its_first_minute` *(1)*
- `a_stamped_piece_with_a_sound_keeps_the_sound_and_the_disclaimer` *(2)*
- `the_disclaimer_is_measured_from_the_video_it_goes_on` *(3)*
- `a_separate_export_asks_for_the_disclaimer_on_every_piece` *(5)*
- `a_merged_export_cuts_its_pieces_clean` *(6)*
- `the_disclaimer_ships_in_the_repo` *(7)*

7 de bu dosyada, kendi dosyasında değil: tek bir olgu için ikinci bir test dosyası açmak, disclaimer
ile ilgili her şeyin bir arada durmasından daha iyi bir şey vermiyor.

`FakeExporter.piece` disclaimer bayrağını da kaydediyor — 5 ile 6'nın bakacağı yer o.

Ön yüze dokunulmuyor: bu maddede ekranda değişen bir şey yok, yani `dist` build'i de yok.
