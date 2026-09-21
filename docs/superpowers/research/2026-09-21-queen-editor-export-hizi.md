# Export'un hızı — kaldıraçlar, bedelleri ve ölçülecekler

**Başlangıç:** 2026-09-21 · **Kaynak:** Kullanıcı bildirimi, v6 yol haritası 249–250 ·
**Ölçüm:** **yok** — bu belge ölçümden önce yazıldı

Bu belge *"birleştirme 5 dakikadan fazla sürdü, verimli çalışıyor mu"* sorusunun cevabına
hazırlıktır. **Hüküm vermiyor**, çünkü tek bir sayı ölçülmedi; yaptığı şey **zinciri adlandırmak,
kaldıraçları bedelleriyle sıralamak, ve her birini hangi ölçümün açtığını yazmak**.

Depoda bunun bir örneği var: galeri yavaşlığında altı aday sayılmış, zincir halka halka ölçülmüş, ve
**ölçüm sıralamayı tersine çevirmişti** — en alttaki aday suçlu çıktı
*([2026-08-23](2026-08-23-queen-editor-galeri-yavasligi.md))*. Burada da tahminle başlanmıyor.

---

## 0 · Bilinen ve bilinmeyen

**Bilinen, koddan:**

- 249'dan önce export **hiçbir şeyi kodlamıyordu** — `-c copy`, yani iş disk ve Drive işiydi.
- 249 ile 250 kodlamayı **kaçınılmaz** kıldı: bindirme yeni bir görüntüdür, kopyalanamaz.
- Kodlama bugün **CPU'da**: `libx264 -preset veryfast -crf 18`. Colab'ın T4 kutusunda **2 vCPU**
  var, ve **T4 export boyunca boş duruyor**.
- Birleşik export parçaları **makinenin kendi diskine** kesiyor *(madde 235)*, Drive'a değil; yalnız
  birleşmiş dosya Drive'a yazılıyor.
- Ayrı export'ta her parça **kendi ffmpeg çağrısı**, ve her parça için bir **ffprobe** daha
  *(bindirmenin ölçüsü videodan okunuyor)*.

**Bilinmeyen, ve tahmin yazılmıyor:**

- O projede **kaç video ve kaç dakika** olduğu. Kodlama süresi doğrudan buna bağlı, ve sayı export
  ekranında yazıyor *("N video export edilecek · MM:SS")*.
- Colab'ın ffmpeg'i **NVENC ile derlenmiş mi**.
- Bir kodlamanın gerçek hızı — ne `libx264` ne `h264_nvenc` için elde fps yok.

**Kullanıcının ölçümü, ve tek kıyas:** T4'te birleştirme **5 dakikadan fazla**; kendi CPU'lu
makinesinde normal bir editör benzer işi **2-3 dakikada** yapıyor. Kıyas yönü doğru — Colab'ın 2
vCPU'su tipik bir masaüstünün çok altında.

**Drive'ın payı, depoda ölçülmüş tek sayıyla:** soğuk **3.34 MB/sn**, sıcak 572 MB/sn
*([2026-08-23](2026-08-23-queen-editor-galeri-yavasligi.md))*. 30-60 MB'lık birleşmiş bir dosya en
kötü hâlde **~10-20 saniye** eder. Beş dakikayı açıklamıyor: **darboğaz Drive değil.**

---

## 1 · Zincir, halka halka

Bir export'un yaptığı işler, sırayla — hangisinin ne kadar sürdüğü bilinmiyor, ama **hangisinin var
olduğu** biliniyor:

| # | Halka | Ayrı export | Birleşik export |
|---|---|---|---|
| 1 | Kaynak videoyu Drive'dan okumak | kare başına | kare başına |
| 2 | `ffprobe` ile ölçü sormak | **kare başına bir süreç** | parça başına bir süreç *(zaten vardı)* |
| 3 | Parçayı kesmek | bindirmeyle **kodlanıyor** | **kopyalanıyor** |
| 4 | Birleştirmek | — | `concat` + bindirme, **tek geçişte kodlanıyor** |
| 5 | Sonucu Drive'a yazmak | kare başına | bir kez |

Buradan çıkan iki şey:

- **Birleşik export'un kodlaması tek geçiş** — kullanıcının istediği *"önce birleştir, sonra son
  videoya ekle"* şekli bu, ve iki ayrı adımdan (birleştir → sonra bindir) hızlı, çünkü o videoyu iki
  kez okuyup iki kez yazardı.
- **Ayrı export'ta kodlama kaçınılmaz ve her parçada** — bir parça ~5 saniye, yani 60 saniyelik
  pencere parçanın tamamını kaplıyor; atlanacak bir bölüm yok.

---

## 2 · Kaldıraçlar

Beklenen kazanca göre sıralı. **Hiçbirinin sayısı ölçülmedi**; "beklenen" sözcüğü her satırda
ciddidir.

### K1 · Kodlamayı GPU'ya vermek — `h264_nvenc`

Aynı kutuda bir T4 var ve export boyunca hiçbir şey yapmıyor. NVENC, GPU'nun **ayrı bir kodlama
bloğu**: CUDA çekirdeklerini meşgul etmiyor, VRAM'den çok az istiyor, yani ComfyUI ayakta dururken
de kullanılabilir olması beklenir.

- **Beklenen kazanç:** en büyüğü. 480 × 720 gibi küçük bir görüntüde NVENC'in gerçek zamanın kat
  kat üstünde çalışması beklenir; 2 vCPU'lu `libx264` ise bu ölçüde gerçek zamana yakın.
- **Bedeli:** dosya aynı kalitede biraz daha büyük olur *(NVENC'in sıkıştırma verimi x264'ün
  altındadır)*.
- **Riski:** ffmpeg'in NVENC ile derlenmiş olmaması. O zaman komut *"Unknown encoder"* ile düşer —
  yani **varsayılmaz, sorulur**: ffmpeg'e bir kez hangi kodlayıcıları taşıdığı sorulup seçim ona
  göre yapılır.
- **Açan ölçüm:** `ffmpeg -hide_banner -encoders | grep -i nvenc`.

### K2 · CPU'da ayarı sertleştirmek — `ultrafast`, daha yüksek `crf`

`veryfast` → `ultrafast` ve `crf 18` → `crf 23`.

- **Beklenen kazanç:** kat kat değil, ama belirgin. NVENC yoksa tek yol bu.
- **Bedeli:** dosya büyür, ve `crf 23` gözle *"kayıpsıza yakın"* olmaktan çıkar — 480 genişlikte
  farkın görünüp görünmeyeceği **denenmeden bilinmez**.
- **Riski:** yok; her ffmpeg'de çalışır.

### K3 · Yalnız ilk dakikayı kodlamak, gerisini kopyalamak *(yalnız birleşik)*

Disclaimer ilk 60 saniyede. Kalan bölüm bindirme taşımıyor, yani **teorik olarak** kopyalanabilir:
5 dakikalık bir videoda karelerin beşte biri kodlanır.

- **Beklenen kazanç:** videonun uzunluğuyla doğru orantılı. **1 dakikalık bir projede sıfır.**
- **Bedeli ve riski büyük:** kodlanmış bölümle kopyalanmış bölümü tek `concat`'te yan yana koymak,
  ikisinin kodlayıcı parametrelerinin birebir aynı olmasını istiyor; kesme noktası da bir keyframe'e
  düşmek zorunda. 250 bu riski **bilerek** doğurmadı. Ve iki geçiş demek: videoyu iki kez okumak.
- **Açan ölçüm:** projelerin tipik uzunluğu. Tipik proje bir dakikanın altındaysa bu kaldıraç
  **hiç açılmaz**.

### K4 · `ffprobe` çağrılarını azaltmak

Ayrı export'ta kare başına bir süreç daha. Birleşik export ölçüleri zaten topluyor.

- **Beklenen kazanç:** süreç başına milisaniyeler — 22 karede toplamı bir saniyenin altı.
- **Hüküm:** kaldıraç değil. Buraya sayılmasının sebebi, sayılmadığında *"belki odur"* diye geri
  gelmesi.

### K5 · Sesi yeniden kodlamamak

Birleştirme sesi zaten `copy` ediyor. Ayrı export'ta ses katmanı `aac`'ye yazılıyor, ve bu 249'dan
önce de öyleydi.

- **Hüküm:** kazanılacak bir şey yok. Zaten yapılıyor.

### K6 · Ekranın susmaması

Kaldıraç değil, ama şikâyetin yarısı bu: beş dakika boyunca ekran *"birleştiriliyor"* yazıp
**hiçbir ilerleme göstermiyor**. ffmpeg'in `-progress` çıktısı okunabilir ve *"%N"* ya da
*"MM:SS / MM:SS"* olarak gösterilebilir.

- **Beklenen kazanç:** sıfır saniye, ve buna rağmen listenin en tepesine yakın: beş dakikanın ne
  kadarının kaldığını bilmek, beş dakikayı üç dakikaya indirmekle aynı şeyi çözüyor.
- **Bedeli:** `piece()` ve `merge()` bugün `subprocess.run` ile bekliyor; ilerleme okumak akışı
  canlı okumayı gerektiriyor, yani exporter'ın çağrı biçimi değişiyor.

### K7 · Çıkış kapısı — bindirmeyi hiç yakmamak

Disclaimer videoya yakılmasa *(klasöre ayrı dosya, ya da başa eklenen bir kare)* export yine
kopyalama olurdu ve bu belgenin konusu kalmazdı.

- **Hüküm:** kullanıcı 21 Eylül'de bindirmeyi seçti, ve gerekçesi yerinde — izleyen disclaimer'ı
  görmeli. Buraya yazılmasının sebebi öneri olması değil, **bedelin nereden geldiğini** göstermesi:
  kodlama disclaimer'ın kendisinden geliyor, kötü bir algoritmadan değil.

---

## 3 · Ölçüm planı — üç sayı

Üçü de defterde birer satır, ve üçü birlikte kaldıraçların hepsini açıyor:

```
# 1 — NVENC var mı?  (K1'i açar ya da kapatır)
!ffmpeg -hide_banner -encoders | grep -i nvenc

# 2 — İş ne kadar?  (K3'ü açar ya da kapatır)
#     Export ekranındaki "N video export edilecek · MM:SS" satırı

# 3 — Kodlama ne kadar hızlı?  (K1 ile K2'yi kıyaslar)
#     Bir parçayı yazmadan kodla: ne dosya yazılır ne Drive'a dokunulur
!time ffmpeg -hide_banner -i PARCA.mp4 -c:v libx264    -preset veryfast -crf 18 -f null -
!time ffmpeg -hide_banner -i PARCA.mp4 -c:v h264_nvenc -preset fast -rc vbr -cq 23 -f null -
```

Üçüncüsü asıl cevabı veriyor: iki satırın süresi arasındaki oran, GPU'ya geçmenin gerçek kazancı.
`-f null -` çıktıyı diske yazmadığı için ölçtüğü şey **yalnız kodlama**.

---

## 4 · Sıra önerisi

1. **Üç sayı ölçülür.** Hiçbir kod değişmeden, defterde üç satır.
2. **K1, NVENC varsa.** Kodlayıcı varsayılmaz, ffmpeg'e sorulur; yoksa bugünkü `libx264` kalır.
3. **K2, NVENC yoksa** — ya da NVENC'le birlikte, hâlâ yavaşsa.
4. **K6 her hâlde.** Hızdan bağımsız, ve şikâyetin yarısı o.
5. **K3 yalnızca** tipik proje bir dakikadan belirgin uzunsa. Değilse kapalı kalır.

**Yol haritasındaki karşılığı:** 253 K1'i taşıyor *(ve kodlayıcıyı sormayı, varsaymamayı)*. K6 ile
K2 henüz madde değil; ölçüm geldiğinde numaralarını alırlar.
