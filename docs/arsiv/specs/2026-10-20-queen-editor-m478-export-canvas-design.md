# Madde 478 · Export'un tuvali — tasarım

**Tarih:** 20 Ekim 2026 · **Madde:** [v10 yol haritası](../roadmaps/2026-10-20-queen-editor-v10-roadmap.md),
478 · v10-3d · **Dal:** `feat/queen-editor-v10` · **Kurallar:** queen-editor
[FOUNDATION](../../../queen-editor/FOUNDATION.md) · [CODE-STANDARD](../../../queen-editor/CODE-STANDARD.md)
· **Önceki parçalar:** [476](2026-10-20-queen-editor-m476-orientation-design.md),
[477](2026-10-20-queen-editor-m477-orientation-screen-design.md)

## Kullanıcıdan gereken

Hiçbir şey. Madde 20 Ekim'de hizalandı. Karışık bir projenin birleşik export'u sorusunu ana ajan
20 Ekim'de yol haritasının sözünden cevapladı: 476'nın satırı eski dikey karelerin videosunun
*"16:9 export'ta bugünkü gibi bantlı görün[eceğini]"*, 478'inki dikey videoların yatayların yanında
bantlı kalacağını söylüyor. Yani bir birleşik export yatay ve dikey parçaları birlikte alır.

## Ne, neden

Birleşik export'ta yatay, 16:9 bir video 1920 × 1080'lik tuvali bantsız doldurur; dikey videolar
bugünkü gibi iki yanda bantla durur. Aynı projede ikisi bir arada olabilir: 476'dan beri eski kareler
dikey kalıyor, 477'den beri her üretim kendi yönünü seçiyor.

Karar videonun **gerçek boyutuyla** verilir, plan satırının `orientation` alanıyla değil: kopya
kareler ve 476'dan önceki kareler bu alanı taşımaz, alan onları yanlış sınıflar (reviewer'ın 476'dan
notu). Boyutu ffmpeg kendisi okur; uygulama hiçbir yerde yön sormaz.

## Bugün — koddan okunanlar

- **Parça kesmek kopyadır.** `FfmpegVideoExporter.piece` videoyu `-c copy` ile, ses katmanı varsa
  `-c:v copy` ile keser (madde 261); hiçbir parça kodlanmaz. Parçalar makinenin kendi diskinde
  (`store.piece_path(pieces_dir, …)`, madde 472), Drive'da değil.
- **Birleştirme concat demuxer'ıdır.** `merge` parçaların yollarını `pieces.txt`'ye yazar,
  `-f concat -safe 0 -i pieces.txt` ile tek bir akış olarak okur, ve tek bir `-filter_complex`'te
  sığdırıp uyarı yazısını bindirir:
  `[0:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2[c]`.
  Ses kopyalanır (`-map 0:a? -c:a copy`).
- **Farklı boyut reddedilir.** Demuxer parçaları olduğu gibi okur, boyut değiştiremez; bu yüzden
  `merge` önce her parçaya ffprobe ile boyutunu sorar (`size`) ve iki boyut görürse *"Videolar farklı
  ölçüde, birleştirilemez"* der. `size`'ı başka hiçbir yer çağırmıyor.
- **Ses eşitlenir.** `_evened_out` her parçaya sesini sorar (`sound`); bir parçada ses varsa, sessiz
  olanlara aynı biçimde sessizlik yazar (madde 286). concat her dosyada aynı akışları ister.

### Tek yönlü bir projede bugünkü süzgeç zaten doğru

ffmpeg'in `decrease`'i (`libavfilter/scale_eval.c`): `w = min(yuvarla(1080 · iw / ih), 1920)`,
`h = min(yuvarla(1920 · ih / iw), 1080)`; `pad` resmi `((1920 − w) / 2, (1080 − h) / 2)`'ye koyar.

| Parça | w | h | Bant (her yanda) |
|---|---|---|---|
| Yatay 1024 × 576 | 1080 · 1024 / 576 = **1920** (tam) | 1920 · 576 / 1024 = **1080** (tam) | 0 — bant yok |
| Dikey 576 × 864 | 1080 · 576 / 864 = **720** (tam) | 1920 · 864 / 576 = 2880 → 1080 | (1920 − 720) / 2 = **600** |

`scale` pikselin şeklini (SAR) `(oh · iw) / (ow · ih)` ile çarpar: yatayda 1105920 / 1105920, dikeyde
622080 / 622080, ikisi de 1; kare piksel kare kalır. 1920, 1080, 720 ve kaydırmalar 0 ve 600 çift
sayı, `yuv420p` için uygun.

**Eksik olan karışık proje:** iki boyut bir arada olunca birleşik export hiçbir şey birleştirmeden
düşüyor.

## Ne değişir

Hepsi `features/photo_generation/data/ffmpeg_video_exporter.py`'de.

### 1. Her parça tuvale kendi süzgecinde oturur, birleştirme concat süzgecidir

Parçalar kopya kesildiği için (yukarıda), boyutu kesimde düzeltmek her parçayı bir kez daha
kodlamak demek olurdu. Ana ajanın koşulu: kesim kodlamıyorsa concat süzgeci, tek çağrıda. Seçilen bu.

Tek ffmpeg çağrısı, girdileri sırayla parçalar ve en sonda uyarı yazısı:

```
ffmpeg -y -threads 1 -i 01.mp4 -threads 1 -i 02.mp4 … -i d.png -filter_complex "<grafik>" -map [v] -r 24 <kodlayıcı> [-map [a] -c:a aac -b:a 192k] hedef
```

Grafiği `_filtergraph` kurar (eski adı `_stamp`; artık yalnız damgalamıyor).

Grafik, `n` parça için:

```
[0:v]FIT[v0];[1:v]FIT[v1];…
[v0][0:a][v1][1:a]…concat=n=N:v=1:a=1[c][a];        (ses yoksa: [v0][v1]…concat=n=N:v=1:a=0[c];)
[N:v]scale=1536:-1[d];[c][d]overlay=(W-w)/2:H-h-43:enable='lt(t,60)'[v]
```

`FIT` = `scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1`

- **`scale` + `pad`** bugünküyle aynı, yalnız birleşmiş akışa değil her parçaya ayrı uygulanır.
  Yukarıdaki tablo değişmez: yatay doldurur, dikey 600'er piksel bantlı.
- **`setsar=1`:** concat süzgeci her parçada boyutun **ve** SAR'ın aynı olmasını ister, değilse
  *"Input link … parameters (size …, SAR …) do not match"* der (`avf_concat.c`). Bizim parçalarımızda
  SAR zaten 1 çıkıyor (yukarıda); satır, SAR'ı yazılmamış (0:1) bir dosyanın birleştirmeyi
  düşürmemesi için.
- **Kare hızı birleştirmenin çıkışında, `-r 24`:** concat süzgeci farklı kare hızlarını reddetmez,
  çıkışı VFR (bilinmeyen hız) yapar. mp4 çıkışında ffmpeg CFR'ye geçer ve hızı bilmeyince 25'e düşer
  (*"Falling back to a default value of 25fps"*): 24'lük H3 videosu kare çoğaltılarak 25'e
  çevrilirdi. Hız bu yüzden çıkışa bir kez yazılır. 24, H3'ün Director'ının `frame_rate`'i (iki
  grafikte de): H3 parçası bütün karelerini korur, eski 16'lık bir WAN parçası 24'e çoğaltılır. Sayı
  `MERGED_FPS` adıyla tuvalin yanında yazılı; bir test onu iki H3 grafiğinin `frame_rate`'ine bağlar.

  **Parçanın zincirinde değil:** her parçanın sonuna konan bir `fps=24` süzgeci o parçanın son
  karesini düşürür. QA bunu ffmpeg 7.1'le ölçtü: 72 karelik iki parça 144 yerine 142, üç parça 192
  yerine 189 kare veriyor; `eof_action=pass`, `round=up` ya da concat'ten sonra `fps` düzeltmiyor.
  Çıkıştaki `-r 24` ile aynı ffmpeg 7.1'de sessiz, sesli, tek parçası sesli ve 24/16 karışık kümeler
  tam sayıda kare veriyor (144, 192), hız 24 CFR. Colab'ın ffmpeg'i başka bir sürüm; Colab
  denemesi onunla bakar.
- **Ses:** ffmpeg'in belgesi (concat süzgeci): *"the filtering system will automatically select a
  common pixel format for video streams, and a common sample format, sample rate and channel layout
  for audio streams, but other settings, such as resolution, must be converted explicitly"*. Örnekleme
  hızı ve kanal düzeni farklı parçalar için ayrıca `aresample` gerekmiyor; ffmpeg ortak biçimi kendisi
  seçip dönüştürür. Ama her parçanın bir ses akışı **olmalı** (`[i:a]` olmayan bir akışı adlandırırsa
  ffmpeg durur), bu yüzden `_evened_out` kalır. Belge ayrıca sesi videodan kısa olan parçanın
  sessizlikle tamamlandığını söylüyor, yani ses kaymaz.
- **Ses artık kopyalanmaz, `aac` ile kodlanır:** bir süzgecin çıkışı kopyalanamaz. Bit hızı
  `SOUND_BITRATE = "192k"`, H3'ün Combine'ının iki grafikteki `audio_bitrate`'i; bir test ikisini
  bağlar. Birleşik dosyanın sesi parçalarınkinden ince çıkmaz.
- **Girdi başına `-threads 1`:** her parçanın çözücüsü tek iş parçacığıyla sınırlanır (aşağıda,
  Maliyet).

### 2. Boyut reddi ve `size` kalkar

Red, demuxer'ın iki boyutu okuyamadığı için vardı. Concat süzgecinde her parça kendi süzgecinden
1920 × 1080 çıkar; red gereksiz. `size`'ı başka çağıran yok; o da kalkar. Bir parça okunamazsa
ffmpeg'in son satırı hata olarak çıkar (`_ffmpeg_run`), tahmin edilmiş bir sebep değil.

### 3. `pieces.txt` kalkar

Yollar ffmpeg'e argüman olarak gider; liste dosyası, yazılması, silinmesi ve tırnak kaçışı yok.
`run_export.py`'deki `JOINED` yorumu `pieces.txt`'yi anıyor, düzeltilir.

### 4. Bayat yorumlar

Dosyanın başındaki *"the pieces are 480x720"* ve `_stamp`'taki *"a 480x720 frame becomes 720x1080"*
bugünkü boyutlarla yazılır: 1024 × 576 ve 576 × 864.

## Maliyet

Koddan ve ffmpeg'in belgesinden sayıldı, ölçülmedi.

| | Bugün | Sonra |
|---|---|---|
| Drive | birleştirme Drive'a gitmez; bitince tek kayıt (`copy_export`) | aynı |
| ffprobe | parça başına 2 (boyut, ses) | parça başına 1 (ses) |
| ffmpeg süreci | 1 (+ sessiz parça başına 1 kopya) | aynı |
| Kodlama | tüm zaman çizelgesi bir kez | aynı; ses de bir kez `aac`, 192k |
| Makinenin diski | `pieces.txt` yazılır, silinir | hiçbir şey |

**Bellek, N açık girdi.** Concat süzgecinde ffmpeg bütün girdileri baştan açar ve grafiği kurabilmek
için her birinden ilk kareyi çözer; her parçanın demuxer'ı ve H.264 çözücüsü işin sonuna kadar
açık kalır. Bellek parça sayısıyla **O(N)** büyür; parça başına ne kadar tuttuğu ölçülmedi, Colab
denemesinde ölçülür. Projeler 20–48 kare (export özeti örneği *"22 video · 1:50 dk"*, panelin
*"48 kare kuyruğa eklendi"*'si).

Her parçanın girdisinden önce `-threads 1` durur: çözücü tek iş parçacığıyla çalışır, ve iş
parçacığı başına tuttuğu kareler ve bağlamlar tek bir taneye iner. Concat bir anda yalnız bir
parçayı okuduğu için aynı anda yalnız bir çözücü çalışır; sınır hız kaybettirmez. Uyarı yazısı tek
bir resim, sınır gerekmiyor.

**Neden parça başına kodlama değil:** her parça tuvale ayrı kodlansa demuxer kopyayla birleştirebilirdi,
ama uyarı yazısı birleşmiş akışın ilk dakikasına bindirildiği için (madde 250) birleştirme yine
kodlar. Her kare iki kez kodlanır: birleştirme süresi kabaca iki katına çıkar (kullanıcı GPU'dan önce
beş dakikayı aşan bir birleştirme ölçmüştü, madde 253), ve ikinci kayıplı kuşak. Bellek tasarrufu
buna değmiyor.

**Komut uzunluğu:** grafik parça başına ~150 karakter. Linux'ta tek argümanın sınırı 128 KiB, yani
~800 parça; projeler bunun çok altında.

## Ne kaybolabilir, ne bozulabilir

- **Yeni dosya yok**, Drive'a yeni yazma yok. Birleşmiş dosya bugünkü gibi makinede kesilir ve bitince
  tek kayıtla Drive'a gider; düşen bir birleştirme Drive'da hiçbir şey bırakmaz (474'ün temizliği
  değişmez).
- **Aynı anda iki export:** export koşucusu aynı modu ikinci kez başlatmaz; ortak bir dosya kalmadı
  (`pieces.txt` gitti).
- **URL'den gelen değer** süzgece girmez: grafikte yalnız sayılar ve parça indeksleri var, yollar
  `piece_path`'in verdiği `NN.mp4`'ler ve argüman olarak gidiyor.
- **Çökme:** bugünküyle aynı, parçalar makinenin diskinde.

## Bu maddenin kararları

1. **Concat süzgeci, tek çağrı** — parçalar kopya kesildiği için; parça başına kodlama süreyi iki
   katına çıkarırdı.
2. **Her parça kendi `scale` + `pad` + `setsar=1`'inden geçer.** Karar ffmpeg'in okuduğu gerçek
   boyutla verilir; satırın `orientation` alanı okunmaz.
3. **Ses için ayrıca `aresample` yok:** belgeye göre concat süzgeci ortak biçimi kendisi seçer.
4. **`size`, boyut reddi ve `pieces.txt` kalkar.**
5. **`MERGED_FPS = 24`, birleştirmenin çıkışında `-r`**, parçanın zincirinde değil (son kare
   düşmesin diye); iki H3 grafiğinin `frame_rate`'ine bir testle bağlı.
6. **Girdi başına `-threads 1`**, bellek O(N) ve ölçümü Colab'da.
7. **Ses `aac`, `SOUND_BITRATE = "192k"`**, iki H3 grafiğinin `audio_bitrate`'ine bir testle bağlı.

## Sınırlar

- **Ayrı export dışarıda:** videoları olduğu gibi kopyalar; madde yalnız birleşik tuvalden söz ediyor.
- **Kırpma yok:** `increase` yerine `decrease`, dikey kare kesilmez, bantlanır (madde 259, FOUNDATION 1).
- **Frontend'de yalnız bir yorum** değişir: `ExportScreen.jsx` birleştirmeye *"a concat copy"*
  diyordu. `dist` yeniden kuruldu ve değişmedi (yorumlar derlemeye girmez).
- **Hata cümlesi ffmpeg'in son satırıdır** (`_ffmpeg_run`). Son satır her zaman sebebin tamamını
  taşımayabilir; bu madde onu değiştirmez (reviewer'ın bulgusu, ana ajanın kararıyla bırakıldı).
- **`_with_sound` olduğu gibi kalır:** sessiz parçaya sessizlik ayrı bir kopya çağrısıyla yazılır;
  bunun süzgecin içine alınması bu maddenin işi değil (reviewer'ın bulgusu, ana ajanın kararıyla
  bırakıldı).
- ffmpeg bu makinede kurulu değil: testler komutu okur, ffmpeg'i çalıştırmaz. QA ve coder gerçek
  birleştirmeyi `tmp/qa-m478/`'deki betiklerle, makinedeki bir ffmpeg 7.1 ikilisini yolundan
  çalıştırarak denedi; Colab'ın kendi sürümü Colab denemesinde.

## Bitti sayılır

1. Testler gösteriyor ki:
   - birleşik export tek ffmpeg çağrısı, her parça ayrı bir girdi ve önünde `-threads 1`, uyarı
     yazısı en sonda;
   - her parça `scale=1920:1080:…decrease,pad=…,setsar=1`'den geçiyor; birleştirme
     `concat=n=N:v=1:a=1` (ses varken) ya da `a=0`, çıkışında `-r 24`;
   - yatay 1024 × 576'lık bir parça, dikey 576 × 864'lük bir parça ve ikisinin karışık bir kümesi
     aynı süzgeçle birleşiyor, red yok, boyut sorulmuyor; `decrease`'in hesabı H3'ün iki boyutunda
     yatayda 1920 × 1080 / bant 0, dikeyde 720 × 1080 / bant 600 veriyor;
   - `MERGED_FPS` iki H3 grafiğinin `frame_rate`'ine eşit;
   - sesli kümede — yalnız bir parçası sesli olanda da — ses `aac`, 192k ile kodlanıyor ve `[a]`
     eşleniyor, sessiz kümede ses eşlenmiyor; `SOUND_BITRATE` iki H3 grafiğinin `audio_bitrate`'ine
     eşit;
   - sessiz parçaya sessizlik yazma, GPU denemesi ve ffmpeg'in kendi hata sözü bugünkü gibi;
   - liste dosyası yazılmıyor.
2. İki satır yeşil: `python -m pytest queen-editor -q` ve `npm test --prefix queen-editor/frontend`.
3. Kullanıcının Colab denemesi, koşunun sonunda *(kullanıcı)*: yatay H3 videosu ve fotoğrafı
   (475'in figür tekrarı riski dahil), ve **karışık bir projenin birleşik export'u** — yatay parça
   tuvali bantsız dolduruyor, dikey parça bantlı, ses kaymıyor; ffmpeg'in bu birleştirmedeki bellek
   kullanımı ölçülür.
