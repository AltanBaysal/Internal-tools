# Madde 286 · Parçaların ses akışı — test turunun tasarımı

**Tarih:** 21 Eylül 2026 · **Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md) ·
**Kurallar:** [FOUNDATION](../../../queen-editor/FOUNDATION.md) ·
[CODE-STANDARD](../../../queen-editor/CODE-STANDARD.md)

## Kullanıcıdan gereken

**Hiçbir şey.** Yön kullanıcının kararı *(21 Eylül — "sesi olmayan karelere sessiz eklenir gayet
basit")*.

## Teşhis, ve nereye kadar doğrulandı

`merge()` her parçaya **ölçüsünü** soruyor ve uyuşmazsa reddediyor; **akış düzenini** hiç sormuyor.
Parçaların sesi ise üç ayrı yoldan geliyor:

| Kare | `piece()`'in yolu | Parçada ses |
|---|---|---|
| Ses katmanı var | `-map 0:v:0 -map 1:a:0 -c:a aac` | **var** (aac) |
| Ses katmanı yok, kaynak videonun kendi sesi var *(H3, madde 243)* | `-c copy` — bütün akışları kopyalar | **var** (kaynağın kodeki) |
| Ses katmanı yok, kaynağın sesi de yok *(WAN)* | `-c copy` | **yok** |

Üçüncü satır birinci ya da ikinciyle aynı projede buluştuğunda parçaların akış düzeni farklı
oluyor, ve `concat` demuxer'ı bütün dosyaların aynı akışlara sahip olmasını istiyor.
**`-map 0:a?` bunu kurtarmıyor:** o yalnız *hiç sesi olmayan* bir sete izin veriyor.

**Doğrulanmadı, ve doğrulanamaz:** bu makinede ffmpeg yok, testler komutu okuyor. O yüzden bu tur
belirtiyi değil **kuralı** çiviliyor: parçaların akış düzeni tek olacak. Kural doğruysa bozulma hiç
olmuyor; teşhis yanlışsa kural zararsız — hiçbir sette fazladan iş yapmıyor *(4. olgu)*.

**Neden koşunun başında:** sessizce bozulan bir çıktı, yavaş bir çıktıdan kötüdür. FOUNDATION 1
*(kullanıcının işi kutsaldır)* FOUNDATION 3'ün önünde, ve hiçbir hata mesajı bu bozulmayı
söylemiyor.

## Tasarım kararı: kural `merge()`'te, `piece()`'te değil

**`piece()` dokunulmuyor** — üç argüman, iki dal, 261'in bıraktığı gibi. Sebebi iki tane:

- **Ayrı export kullanıcının teslim ettiği dosya**, ve ona sessiz bir ses eklemek *"hiç
  ellemeyelim"* denen şeye dokunmak olur. H3 kaynağının sesini yeniden kodlamak ise doğrudan
  kaliteye dokunur.
- **Bayrak 261'de bilerek silindi.** Geri koymak, aynı işi iki yerden yönetmek olurdu.

**Kural birleştirmenin kendi işi**, ve ölçü kuralının yanında duruyor: `concat`'in sözleşmesini
bilen tek yer orası.

## Kural: tek cümle

**Parçalardan birinin sesi varsa, hepsinin olmalı.** Sesi olmayan parçanın yanına, sesi olanın
**örnekleme hızı ve kanal düzenine** uyan sessiz bir ses yazılıyor, ve birleştirme o yeni dosyayı
okuyor.

**Sonucu, üç sette:**

- Hepsinin sesi var → fazladan hiçbir şey yazılmıyor.
- Hiçbirinin sesi yok → fazladan hiçbir şey yazılmıyor *(`-map 0:a?` bu seti zaten taşıyor)*.
- **Karışık** → yalnız sessiz olanlar yeniden yazılıyor.

Yani yaygın iki durumda **maliyet sıfır**, ve iş yalnız bozulmanın gerçekten mümkün olduğu sette
yapılıyor.

## Çivilenen olgular

**1 · Her parçaya sesi soruluyor.** Ölçü sorusunun yanında, parça başına **bir** soru:
`ffprobe -select_streams a:0 -show_entries stream=sample_rate,channel_layout`. Sesi olmayan dosya
**boş** cevap veriyor, ve boş cevap *"ses yok"* demek — hata değil.

**2 · Sessiz parçaya sessiz ses yazılıyor.** `anullsrc` girdisi, video `-c:v copy`, ses `aac`, ve
`-shortest` *(`anullsrc` sonsuz akar)*. Videonun tek karesi bile yeniden kodlanmıyor.

**3 · Sessizlik, sesi olanın ölçüsüne uyuyor.** Örnekleme hızı ve kanal düzeni ffprobe'un okuduğu
parçadan geliyor — `anullsrc=r=48000:cl=stereo` gibi sabit bir tahmin değil, çünkü uyuşmayan bir
ses akışı `concat`'i yine durdurur.

**4 · Tek düzenli setlerde fazladan çağrı yok.** Hepsi sesli ve hiçbiri sesli setlerde yazma
çağrısı yalnız birleştirmenin kendisi — bugünkü davranış birebir korunuyor.

**5 · Birleştirme yeni dosyayı okuyor.** `concat` listesinde sessiz parçanın yerine onun sesli
kopyası yazılıyor; sıra hiç değişmiyor.

**6 · Birleştirmenin kendisi değişmiyor.** Aynı filtre zinciri *(259'un tuvali)*, aynı kodlayıcı
*(253, 257)*, aynı `-map 0:a?`, aynı `-c:a copy`.

**7 · `piece()` üç argümanda kalıyor.** 261 yerinde.

**8 · Yeni dosyalar parçaların yanında doğuyor**, yani `/tmp`'de *(235)*; Drive'daki klasöre bu
maddeden hiçbir şey girmiyor, ve `run_export` o klasörü zaten silip gidiyor.

## Kapsam dışı, ve bilerek

**Kodek uyuşmazlığı.** İki sesli parça farklı kodek ya da farklı hızda olabilir — bizim ses
yolumuz aac üretiyor, H3 kaynağının kendi sesi ise kaynağın kodeki. **Bunun için elimizde hiçbir
belirti yok**, ve düzeltmesi *her_ parçanın sesini yeniden kodlamak olurdu: bedeli gerçek, sebebi
varsayım *(FOUNDATION 3)*. Bu madde yalnız **varlık/yokluk** farkını kapatıyor, ve o fark koddan
okunabilen tek kesin fark.

## Kırmızı: üç, ve iki test doğuştan yeşil

Beş test yazıldı, **üçü kırmızı** *(olgu 1, 2+3, 3'ün ölçüsü)*. 4. olgunun iki testi — hepsi sesli
ve hiçbiri sesli setler — **bugün de yeşil**, çünkü bugün de tek yazma çağrısı var ve parçalar
verildiği gibi birleşiyor. Yazılmalarının sebebi bu: **kuralın bedava kalmasının bekçisi** onlar.
Uygulama her sete sessizlik yazmaya kalkarsa ikisi birden kırmızıya döner.

**Bir test de ayarlandı, silinmedi:** `test_merging_asks_every_piece_how_big_it_is` bütün ffprobe
çağrılarını sayıyordu, ve ikinci soru eklenince sayı değişti. Adı **ölçü** sorusunu söylüyor, o
yüzden yalnız onu süzüyor — testin anlamı aynı kaldı.
