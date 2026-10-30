# Madde 521 · Birleşik export'ta ses parçadan parçaya taşmaz — tasarım

**Tarih:** 30 Ekim 2026 · **Madde:** [v11 yol haritası](../arsiv/roadmaps/2026-10-24-queen-editor-v11-roadmap.md#v11-20),
521 · v11-20 (yama v11.1) · **Dal:** `feat/queen-editor-v11.1` · **Plan:**
[2026-10-30-queen-editor-m521-birlesik-export-ses-tasmasi-plan.md](../plans/2026-10-30-queen-editor-m521-birlesik-export-ses-tasmasi-plan.md)
· **Kurallar:** queen-editor [FOUNDATION](../../queen-editor/FOUNDATION.md) ·
[CODE-STANDARD](../../queen-editor/CODE-STANDARD.md)

## Kabul koşulu (maddeden)

Birleşik export'ta her parçanın sesi kendi parçasında bitiyor; sesi kapalı bir parçaya öncekinin sesi
taşmıyor.

Kullanıcı — *"bu hatalarıda çöz istersen"*; BACKLOG'un işi (515'in QA'sı): *"Birleşik export'ta her
parçanın sesi sonrakine taşıyor"* — 440 Hz'lik bir parçanın sesi, ardından gelen sesi kapalı parçada
11.00–11.05 s arasında duyuldu. Ayrı export, ses kapatma (510/515), eski MMAudio sesleri (514) ve
videonun kopyalanması (`-c copy`) olduğu gibi kalır.

## Bugün: ölçülen neden

Ölçüm gerçek ffmpeg 7.1'le (imageio-ffmpeg'in ikilisi, `tmp/m510-qa/pylib`), deponun kendi
`FfmpegVideoExporter`'ıyla yapıldı: `piece`, `silent` ve `merge` aynen çalıştı, parçalar burada üretildi
(her sesli parçada baştan sona 440 Hz, her biri ayrı renkte). Bu makinede ffprobe yok; cevapları
`tmp/m521/measure.py` veriyor: sesin biçimi `ffmpeg -i`'den (515'in QA'sı gibi), bir akışın süresi mp4'ün
kendi `mdhd` kutusundan — ffprobe'un mov okuyucusunun süreyi aldığı yer. Resmin parça sınırları karelerin
renginden, sesin nerede duyulduğu 1 ms'lik pencerelerle okunuyor.

**Her parçanın sesi resminden uzun.** 3 s'lik (72 kare) her sesli parçanın çözülmüş sesi 3.019 s: aac
son çerçevesini 1024 örneğe tamamlıyor (130 × 1024 örnek). 440 Hz 3.000'de bitiyor, kalan 18.6 ms dolgu
sessizlik. H3'ün ya da bir katmanın sesi resmin son karesinden sonra da sürebilir; 5.1 s sesli 5 s'lik
parçada fark 108 ms. Baştaki aac gecikmesi (priming) değil: ilk parçanın sesi 0.000'da başlıyor, mp4'ün
edit list'i onu siliyor.

**concat her parçayı en uzun akışı kadar sayıyor.** Birleşimin `concat` filtresi bir parçanın süresini
resmi ve sesinden uzun olanla ölçüyor (ffmpeg'in belgesi). Sesi uzun her parça, sonraki bütün parçaları
resim ve ses birlikte o kadar geç başlatıyor. Arada kalan yeri birleşimin `-r 24`'ü resmin son karesini
tekrarlayarak dolduruyor: resim donup kalırken ses çalmaya devam ediyor. Resim ayrıca yalnız 1/24 s'lik
adımlarla yer değiştirebiliyor. Her parçanın sesi tam yerinde başlıyor, resmi ise en yakın kare adımına
oturuyor. Kayma her birleşimde dolgu kadar artıyor, bir kare tekrarlanınca sıfırlanıyor. 515'in ~50 ms'si
bu kayma, 50 ms'lik pencereyle okunmuş hali.

| Durum (önce, kırmızı) | Sonraki sessiz parçaya taşma | Tekrarlanan kare |
|---|---|---|
| 12 parça, sesli/sessiz sırayla, 3 s resim + 3 s ses (515'in kurgusu) | en çok **+20 ms** (sırayla +0, +20, −4, +14, −9, +10) | 3 |
| 6 parça, sesi wav katmanından (514'ün eski MMAudio'su gibi), 3 s | en çok **+20 ms** | 1 |
| 8 parça, sırayla, 5 s resim + 5.1 s ses | en çok **+26 ms**; ilk parçanın sesi donmuş resmin üstünde 100 ms daha | 10 |
| 20 parça, sırayla, H3 boyu (121 kare = 5.041667 s) + 5.1 s ses | en çok **+34 ms** | 16 |
| 20 parça, hepsi sesli, H3 boyu + 5.1 s ses | — | **30** (1.25 s donmuş resim; ses 102.168 s, resim 100.833 s) |

## Ne yapılır

### Her parçanın sesi resminin bittiği yerde kesilir

Birleşimin filtre grafiğinde her parçanın sesi `concat`'a girmeden resminin süresinde kesilir:
`[i:a]atrim=end=<resmin süresi>[ai]`, ve `concat` `[vi][ai]` çiftlerini birleştirir. Kesilen ses hiçbir
zaman resminden uzun olmaz. Kısa kalanı (`_with_sound`'un yazdığı sessizlik, 2.995 s) `concat` bugünkü
gibi sessizlikle doldurur. Böylece her parça tam resmi kadar sürer.

**Neden her parça sayısında kaymaz:** k'ıncı parçanın resmi de sesi de önceki parçaların resim
sürelerinin toplamında başlıyor. Toplamda sesten gelen bir terim kalmıyor, büyüyen bir şey yok. H3'ün
24 fps'lik parçaları kare adımına tam oturuyor; hiçbir kare tekrarlanmıyor. Geriye yalnız yuvarlama
kalıyor: ffprobe süreyi mikrosaniyeyle yazıyor, `atrim` en yakın örneğe yuvarlıyor. Parça başına en çok
yarım örnek (44.1 kHz'de 11 µs) fazla kalabiliyor. Bunun yarım kareyi (21 ms) bulup tek bir kareyi
kaydırması için ~1800 parça gerekiyor.

### Parçaya tek soru: resmin süresi ve sesi

Kesmek için her parçanın resminin süresi gerekiyor. Parçaya zaten soruluyordu: sesi var mı, biçimi ne
(madde 286). İki soru ayrı sorulsa her parça iki kez okunurdu. Bunun yerine soru tek oldu: `sound`'un
yerine `streams` geldi, resmin süresini ve sesin biçimini bir ffprobe çağrısıyla döndürüyor:

`ffprobe -v error -show_entries stream=codec_type,duration,sample_rate,channel_layout -of json <parça>`

- **JSON**, seçeneksiz: 288'in dersi, ffprobe yazıcının seçenek dizisini iki noktadan bölüyor; yazılmayan
  seçenek yanlış yazılamaz. Alanların adı var, ffprobe'un onları hangi sırayla yazdığına ya da hangi
  akışın önce geldiğine bakılmıyor.
- **Ses akışı yoksa** cevap `None`'dır, bugünkü gibi (madde 435'ten önceki WAN videoları).
- **Resmin süresi yoksa** (anahtar yok ya da `N/A`) o parçanın sesi kesilmeden girer, 521'den önce her
  parçanınki gibi: `cuts`'ta o parça için `None`, grafikte `[vi][i:a]`. Öteki parçalar yine kesilir. Her
  parça bizim kopyamızın yazdığı bir mp4 ve resminin süresi var; ama biraz taşan bir ses, hiç export
  olmamasından küçük bir zarar (FOUNDATION 1, reviewer). Tahmin edilen bir süre sesi yanlış yerden keserdi,
  tahmin edilmez. Süre sayı olarak okunuyor, filtre grafiğine dosyanın başlığında ne yazıyorsa o metin
  olarak gitmiyor.
- **Cevap JSON değilse** (ffprobe 0 döndü ama başka bir şey yazdı) export durur, dosyanın adı ve
  ffprobe'un yazdığıyla: *"<parça>: ffprobe JSON yerine şunu yazdı: …"* (ilk 200 karakter). Bir JSON
  okuyucusunun karakter konumlu şikâyeti ekrana çıkmaz.
- **Sesin biçiminden ffprobe'un vermediği değer** boş döner, ve `_with_sound` `anullsrc`'a yalnız verilen
  değerleri yazar: `anullsrc=r=44100`, hiçbiri yoksa `anullsrc`. `cl=` boş bırakılınca ffmpeg reddediyor
  (7.1'de denendi: *"Unable to parse option value "" as channel layout"*); yazılmayan değer anullsrc'un
  kendi varsayılanını alır, concat onu da öteki biçimler gibi çevirir. Bu 521'den önce de vardı (csv'de boş
  alan); reviewer'ın bulduğu, aynı değişiklikte düzeldi.
- **Sessizlik yazılan parça** (`_with_sound`) yeniden sorulmaz: resmi asıl parçanın kopyası, süresi aynı.

`_evened_out` artık birleştirilecek parçalarla birlikte kesim yerlerini döndürüyor; setin hiç sesi yoksa
`None`. `merge` ve `_filtergraph` "sesli mi" bayrağı yerine bu listeyi alıyor. Sesi olmayan setin grafiği
madde 478'deki gibi, kesim yok.

### Değişmeyenler

- **Ayrı export:** `piece` ve `silent` değişmez. Parçalar kopya, ses taşıyorsa bütün sesiyle.
- **Ses kapatma (510/515):** kapalı parça `silent`'la sessiz kesiliyor, birleşimde `_with_sound`
  sessizlik yazıyor. İkisi de aynı. Sessizlik de resminin süresinde kesiliyor; kısa olduğu için kesim
  boşa düşüyor.
- **Eski MMAudio sesleri (514):** `piece`'in yazdığı ses diğerleri gibi kesiliyor (yukarıdaki wav ölçümü).
- **Video:** parçalarda `-c copy` sürüyor. Birleşim madde 478'den beri zaten tek kodlama. Resim zinciri,
  `-r 24`, uyarı yazısı ve GPU/CPU seçimi aynı.

## Maliyet

Proje, sohbet ve Drive'daki dosya sayısından bağımsız. Parçalar makinenin kendi diskinde (`tempfile`),
Drive'a gidiş yok.

| İş | Ne yapar |
|---|---|
| Birleşik export, parça başına soru | değişmez: N parçaya N ffprobe çağrısı, her parça bir kez okunuyor. Cevap birkaç yüz bayt JSON. |
| Birleşim | değişmez: tek ffmpeg çağrısı, tek kodlama. `atrim` zaten çözülmüş sesten örnek atıyor; ek çözme ya da kodlama yok. |
| Süre | ölçülemeyecek kadar küçük: 20 parça, 100 s video, CPU x264, birleşim önce 12.5 / 14.0 s, sonra 13.0 / 13.2 s (sonrasında 30 tekrarlanan kare de kodlanmıyor). |
| Kalite | ses kaybı yok: ses birleşimde zaten bir kez çözülüp bir kez kodlanıyordu (478), bu değişmedi. Atılan tek şey parçanın son karesinden sonra çalan ses: aac dolgusu (sessizlik) ya da resminden uzun kalan ses — ki o hiçbir zaman kendi resminin altında değildi. |
| Ayrı export | değişmez. |

## Ne kaybolabilir, ne bozulabilir

- **Hiçbir şey yazılmaz ya da silinmez;** değişen yalnız birleşimin filtre grafiği ve parçaya sorulan
  soru. Birleşik dosyanın yazılışı, Drive'a bir kez gitmesi, iptal ve hata yolları aynı.
- **Resminden uzun ses birleşik export'ta kısalır.** Bir parçanın sesi son karesinden sonra da sürüyorsa
  o kuyruk birleşik dosyada yok, ayrı export'ta duruyor. Kabul koşulunun istediği bu: ses kendi parçasında
  bitiyor.
- **Süresiz bir resim birleşimi durdurmaz;** o parçanın sesi kesilmeden girer, 521'den önceki gibi en çok
  dolgusu kadar taşabilir. Bizim mp4'lerimizde olmuyor.
- **JSON olmayan bir cevap birleşimi durdurur,** dosyanın adı ve ffprobe'un yazdığıyla; hiçbir ffmpeg
  çağrısı yapılmaz, yarım dosya yazılmaz.

## Sınırlar

- **24 fps olmayan parça:** eski bir WAN videosu (16 fps) birleşimin `-r 24`'üyle kare adımına
  yerleşiyor, sınırı yarım kareye (~21 ms) kadar oynayabiliyor. Bu kayma birikmiyor; sesi kendi parçasıyla
  tam hizada. 24 fps'lik bir çıkışın sınırı bu.
- **Bu makinede ffprobe yok.** Kesim yerini veren `duration`'ı ölçümde `mdhd`'den okunan süre karşıladı
  (ffprobe'un mov okuyucusunun okuduğu alan). Bütün parçalarda kare sayısı / 24 ile aynı çıktı. Gerçek
  ffprobe'un cevabı aşağıda, Colab'da görülür.

## Yalnız Colab'da görülecek

Colab'ın gerçek ffprobe'uyla, kullanıcının sondaki denemesinde, birleşik export'un kestiği üç parça
üzerinde (`ffprobe -v error -show_entries stream=codec_type,duration,sample_rate,channel_layout -of json`):

- **Gerçek bir H3 parçası** (`piece`'in kendi sesiyle `-c copy` kopyası),
- **sesi kapalı bir parça** (`silent`'ın `-c copy -an` kopyası),
- **sessizlik yazılmış bir parça** (`_with_sound`'un `-sound.mp4`'ü).

Her birinde: JSON'un biçimi kodun okuduğu gibi mi (`streams` dizisi, `codec_type`, resmin `duration`'ı,
sesin `sample_rate`'i ve `channel_layout`'u), ve resim akışının `duration`'ı resmin gerçek süresine (kare
sayısı / fps) eşit mi. Bir edit list ffprobe'un akış süresini `mdhd`'dekinden farklı yapabilir; burada
ölçüm `mdhd`'yi okudu. Eşit değilse ses o farkla yanlış yerden kesilir.

## Ölçüm: önce (kırmızı) ve sonra (yeşil)

`python tmp/m521/measure.py <düzen> <resim s> <ses s>`. `M521_BEFORE=1` ile aynı ölçüm, 521'den önceki
exporter'la koşuyor (`git show HEAD:…` → `tmp/m521/before_exporter.py`). Düzen: `S` kendi sesli parça,
`W` sesi wav katmanından, `M` sesi kapalı.

| Durum | Önce: taşma / tekrarlanan kare | Sonra: taşma / tekrarlanan kare |
|---|---|---|
| `SMSMSMSMSMSM 3 3` | +20 ms / 3 | **+1 ms / 0** |
| `WMWMWM 3 3` | +20 ms / 1 | **+1 ms / 0** |
| `SMSMSMSM 5 5.1` | +26 ms / 10 | **+1 ms / 0** |
| `SMSMSMSMSMSMSMSMSMSM 5.02 5.1` (121 kare) | +34 ms / 16 | **+1 ms / 0** |
| `SSSSSSSSSSSSSSSSSSSS 5.02 5.1` | — / 30 | **— / 0** (resim 100.833 s, ses 100.844 s) |

Sonrasındaki ±1 ms ölçümün 1 ms'lik penceresi. Son satırdaki 11 ms, birleşik dosyanın kendi son aac
çerçevesinin dolgusu; ardından parça gelmiyor. Sonrasında 20 parçalık sırada her parçanın sesi resminin
başladığı karede başlıyor ve bittiği karede bitiyor (ör. 9. parça: resim 40.333–45.375, ses 40.333–45.376).

## Ne zaman bitti

- **Birim testleri** (`backend/tests/test_export.py`, ffmpeg'siz, komutun biçimi):
  - üç sesli parça, resimleri 5.041667 / 3.000000 / 10.083333 s:
    `[0:a]atrim=end=5.041667[a0];[1:a]atrim=end=3.0[a1];[2:a]atrim=end=10.083333[a2];[v0][a0][v1][a1][v2][a2]concat=…`,
    hiçbir parçanın sesi kesilmeden girmiyor (önce kırmızı);
  - sessizlik yazılan parça kendi resminin süresinde kesiliyor (`atrim=end=4.0`), ve yeniden sorulmuyor:
    iki parçaya iki soru;
  - sesi olmayan sette kesim yok, grafik 478'deki gibi;
  - ffprobe resmin süresini vermezse (`None`, `N/A`) o parçanın sesi kesilmeden giriyor
    (`[v0][a0][v1][1:a]concat…`), öteki kesiliyor, grafiğe `N/A` ya da `None` yazılmıyor;
  - ffprobe sesin kanal düzenini vermezse sessizlik `anullsrc=r=44100`, hiçbir değeri vermezse
    `anullsrc` — boş `cl=` yok;
  - JSON olmayan cevap *"a.mp4: ffprobe JSON yerine şunu yazdı: …"*, ve ffmpeg çağrılmıyor;
  - parçaya sorulan soru kelimesi kelimesine: `-show_entries stream=codec_type,duration,sample_rate,channel_layout -of json`;
  - grafiğin kelimesi kelimesine testi, sesli birleşimin, GPU'nun, sessizliğin ve biçiminin testleri
    `atrim`'le geçiyor. `FakeRun` ffprobe'un JSON'unu veriyor.
- **Gerçek ffmpeg ölçümü:** yukarıdaki tablo. Her durumda taşma 1 ms'lik pencerenin içinde, tekrarlanan
  kare yok.
- Ayrı export'un, ses kapatmanın (`test_mute.py`) ve kopyanın testleri değişmeden geçiyor. İki
  queen-editor takımı yeşil (`test_notebook_clones_its_branch.py`'nin iki testi kullanıcının Colab
  denemesi için kasten kırmızı).

## Aynı değişiklikte

BACKLOG'dan *"Birleşik export'ta her parçanın sesi sonrakine taşıyor"* silinir.
