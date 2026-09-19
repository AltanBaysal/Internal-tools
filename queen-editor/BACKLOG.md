# Backlog — Queen Editor

Gerçek ama henüz bir koşuya bağlanmamış işler. Sırası gelince buradan çıkar, o koşunun yol
haritasına girer.

---

### MiniMax H3'te turbo: checkpoint mi, LoRA mı

*(Kullanıcı, 18 Eylül — "turbo olayını backlog'a yaz, user ile konuşulup align olunacak".)* 213'ün
denemesi sırasında çıktı.

**Bilinen:** Kullanıcının paylaştığı tarif normal bir checkpoint'e hızı LoRA'yla veriyor:
**DaSiWa Hybrid v1** *(Civitai sürüm 3251526, adında `turbo` yok)* + **`lightx2v_4step_v0.1`**
*("Minimax H3 Turbo Loras")*. `minimax-h3/manual.ipynb` ise hızı checkpoint'in içinde taşıyan
**DaSiWa Hybrid Turbo v2**'yi *(3314686)* indiriyor ve grafik onunla 8 adımda koşuyor —
[indirilecekler.md § 6](../collab-toolbox/video_experiments/minimax-h3/indirilecekler.md).

**Bilinmeyen:** Turbo checkpoint'in üstüne bir hız LoRA'sı daha takmanın hızlandırmayı iki kez
uygulayıp uygulamadığı. Depoda WAN için aynı uyarı var, H3'te **denenmedi**. `lightx2v_4step`'in
adresini kullanıcı verdi *(Civitai sürüm 3206543)*, linkiyle birlikte
[indirilecekler.md § 7](../collab-toolbox/video_experiments/minimax-h3/indirilecekler.md)'de duruyor.

**Kararlaşmadı:** hangi yolun kullanılacağı. **Başlamadan önce kullanıcıyla konuşulur**, ve varılan
karar buraya yazılır.

### Fotoğraf üretim hızı — hız LoRA'ları

Üretim hızlansın; yol olarak hız LoRA'ları denenecek. Kazanç fotoğraf tarafında görünüyor, video
zaten hızlı koşacak şekilde ayarlı.

**v5'te madde 220 olarak denendi ve geri alındı** *(kullanıcı, 16 Eylül — "olmuyor gibi")*. Numara
220 olarak kalır; geri gelirse aynı numarayla gelir.

**Denenen:** DMD2'nin kendi 4 adımlık LoRA'sı (`tianweiy/DMD2`, `dmd2_sdxl_4step_lora_fp16`), 0.7
ağırlıkla, LCM / `sgm_uniform`, 8 adım, CFG 1.5 — Nova'nın yaratıcısı Crody'nin **Nova Reality XL
IL v9.0 DMD2** sürümüne verdiği ayarlar. Nova 3DCG için Crody böyle bir sürüm yayınlamamış.
**Sonuç:** bir üretim **90 saniye** sürdü. Neden bu kadar sürdüğü **bilinmiyor**: normal ayarın
süresi, adım başına süre ve GPU elde yok. Geri gelirse oradan başlar — önce iki log yan yana.

**Bilinenler, geri gelirse işe yarar:**
- Grafikte yüz düzeltici ana örnekleyiciyle **aynı modeli ve aynı CFG'yi** kullanıyor
  *(`workflow_api.json` node 31 ← 44 ← 27, CFG node 18)*: LoRA ikisini birden etkiliyor, ve
  düzelticinin 14 adımı hızlanmıyor.
- CFG tam 1 değilse her adım bugünkü kadar sürüyor; kazanç yalnız adım oranından gelir.
- Genel SDXL'den damıtılmış LoRA'lar (DMD2, Hyper-SDXL, SDXL-Lightning) Illustrious'a ancak yaklaşık
  uyar. Illustrious üzerinde eğitilmiş bir DMD2 var *(Civitai 1850983, V7.5 / V6)* — denenmedi.
- Hyper-SDXL'in **8-step CFG** LoRA'sı CFG 5–8'i koruyor: negative prompt ve yüz düzeltici bugünkü
  gibi çalışır, kazanç daha az. Denenmedi.

### Fotoğrafta NSFW detailer

*(Kullanıcı, 16 Eylül.)* Fotoğraf grafiğinde NSFW detailer açılacak.

**v5'te madde 219 olarak yol haritasındaydı, koşulmadan backlog'a döndü** *(kullanıcı, 17 Eylül)*.
Numara 219 olarak kalır; geri gelirse aynı numarayla gelir.

**Bilinenler:** Bugün üretim grafiğinde **tek** dedektör var, o da yüz: `bbox/face_yolov9c.pt`,
`workflow_api.json`'da iki yerde *(94 ve 446)*. Creator'ın tam grafiğinde üç dal daha duruyor ve
**bypass'lı oldukları için export'a hiç girmemişler**: NSFW
*(`segm/ntd11_anime_nsfw_segm_v5-variant1.pt`)*, el *(`bbox/hand_yolov9c.pt`)* ve göz
*(`bbox/Eyeful_v2-Individual.pt`)*. **Üç dosya da depoda hiçbir yerde inmiyor**, ne defterde ne
`model_groups`'ta; yani bugün o dal açılsa "model bulunamadı" ile düşer. Detailer, FaceDetailer'ın
başka bölgeye uygulanmış hâli: bölgeyi buluyor, kırpıp tam çözünürlükte yeniden render ediyor ve
düşük denoise ile geri yapıştırıyor. **Bedeli** her fotoğrafta bir kırpma render'ı daha, kabaca
**%20-40 süre**.

**Kararlaşmadı:** Yalnız NSFW mi açılacak, yoksa el ve göz de mi *(üçü de ayrı dedektör, ayrı
süre)*? Dedektörlerin kaynağı da henüz bulunmadı. **Kullanıcıdan gereken:** dalı ComfyUI'da açıp
çıkana bakması, beğenirse de **Export (API)**'yi yeniden vermesi. Dal bizim dosyada olmadığı için
grafik yeniden export edilmeden koda giremez.

### queen-editor'ün defteri, aynı model için manuel defterden yavaş açılıyor

*(Kullanıcı, 17 Eylül — "comfyui manuel denersem fotoğraf vs daha hızlı iniyor, queen editörde çok
daha yavaş"; ardından: "üretim hızı değil, yüklenip cloudflare verme hızı".)*

**v5'te madde 233 olarak yol haritasındaydı, koşulmadan backlog'a döndü** *(kullanıcı, 18 Eylül)*.
Numara 233 olarak kalır; geri gelirse aynı numarayla gelir.

Konu dosyaların ekrana gelmesi değil, **defterin açılış süresi**.
`photo_generator/nova-3dcg/manual.ipynb` fotoğraf için ~10 dakikada açılıyor, `queeneditor.ipynb`
aynı modelle ~20 dakika sürüyor gibi — **ölçülmedi**. **Önce ölçülecek, sorun varsa çözülecek**
*(kullanıcı)*.

**İki defterden okunan aday, henüz sebep değil** *(17 Eylül)*: manuel defter **8** custom node
kuruyor, queen-editor **20** — aradaki 11'i yalnız video grafiğinin, ve defterin kendi notu
*"node'lar seçime bağlı değil, hepsi kurulur"* diyor. Birkaçı kendi pip bağımlılıklarını kuruyor.
Küçük ekler de var: repo klonu, `ffmpeg` kurulumu, `cloudflared` indirmesi.

**Ölçüm:** Colab'ın gösterdiği hücre süreleri, iki defterde aynı modelle yan yana. **Kullanıcıdan
gereken:** iki defteri aynı fotoğraf seçimiyle açıp her hücrenin süresini vermesi.

### Kare başına negatif prompt alınacak

*(Kullanıcı, 17 Eylül.)* İş iki görevdir: negatif prompt'ları **QueenAgent üretir**, queen-editor
**alır ve kullanır**. Bu görev queen-editor'ün yarısı. Üreten yarı
[QueenAgent'ın backlog'unda](../queen-agent/BACKLOG.md) *"Kare başına negatif prompt üretilecek"*
başlığıyla duruyor.

Kareler kendi negatif prompt'larıyla gelebilecek, gerekiyorsa her kare için ayrı. Üç katmanın her
biri kendi başlığında:

#### Fotoğraf

Fotoğraf karesi kendi negatif prompt'unu alır ve onunla üretilir.

#### Video

Video katmanı kendi negatif prompt'unu alır ve onunla üretilir.

#### Ses

Ses katmanı kendi negatif prompt'unu alır ve onunla üretilir.

**Kararlaşmadı:** Negatif gelmeyen kare ya da katman ne olacak? Bugünkü varsayılanla mı üretilecek?

**Başlamadan önce kullanıcıyla ayrıntılı konuşulur** *(kullanıcı, 17 Eylül)*. Madde sırası gelince
koşulacak, ama ilk turun spec'i yazılmadan önce üç başlığın her biri kullanıcıyla tek tek konuşulur.
Varılan kararlar da buraya ya da maddenin satırına yazılır.

### Video LoRA denemesi — anatomik hatalar

Video üretiminde anatomik hatalar çıkıyor; üretim tarifinin LoRA'ları değiştirilip denenecek.

### Cumshot güncellemesi — video LoRA'ları

*(Kullanıcı, 17 Eylül.)* Video tarafında cumshot için LoRA'lar denenecek. Kullanıcının sakladığı
bağlantılar aşağıda. Açıklamalar yalnız bağlantının kendi adından okunuyor, sayfalar henüz
açılmadı.

**Modeller:**
- [HMCumshot — MiniMax H3 için](https://civitai.red/models/2857340/hmcumshot-cumshot-lora-for-minimax-h3?modelVersionId=3238531)
  *(sürüm 3238531)*. MiniMax H3 için olduğundan v5'in 213. maddesiyle ilgili.
- [Epic Cumshots](https://civitai.red/models/2621242/epic-cumshots?modelVersionId=2946870)
  *(sürüm 2946870)*
- [CumFacial — WAN 2.2](https://civitai.red/models/1962545/cumfacial-wan22?modelVersionId=3112727)
  *(sürüm 3112727)*
- [F4C3SPL4SH — WAN 2.2 i2v](https://civitai.red/models/1922973/f4c3spl4sh-cumshot-i2v-wan-22-video-lora-k3nk?modelVersionId=2176450)
  *(sürüm 2176450)*

**Örnek görseller:**
[141692376](https://civitai.red/images/141692376),
[142849014](https://civitai.red/images/142849014),
[142760376](https://civitai.red/images/142760376),
[140992432](https://civitai.red/images/140992432)

**Kararlaşmadı:** hangi LoRA'nın kullanılacağı, hangi video modeliyle (bugünkü WAN 2.2 mi, MiniMax
H3 mü) ve uygulamada nasıl seçileceği.

### Karakter LoRA'sı eklenecek

*(Kullanıcı, 6 Eylül.)* Aynı kişinin her karede aynı çıkması için. Bugün bunu tutan tek şey etiket:
QueenAgent karakteri bir kez yazıp onu adlayan her kareye koyuyor, ama etiket bir yüzü sabitlemiyor.

**Kararlaşmadı:** hazır bir LoRA yüklemek mi, yoksa karakter başına eğitmek mi — ve eğitilecekse o
işin nerede koşacağı.

### Editör kısmı eklenecek

*(Kullanıcı, 6 Eylül.)* Uygulama bugün **üretip dışa aktarıyor**: kare bir fotoğrafla başlıyor,
üstüne video ve ses biniyor, dışa aktarma hepsini tek klasörde birleştiriyor. Çıkanı **değiştiren**
hiçbir yer yok — beğenilmeyen kare yeniden üretiliyor.

Neyi kapsayacağı **kararlaşmadı**: fotoğrafın kendisine dokunmak mı *(kırpma, rötuş, inpaint)*,
video/ses tarafını kesip düzenlemek mi, yoksa karelerin sırasıyla oynamak mı.

### Konuşma özelliği eklenecek

*(Kullanıcı, 11 Eylül.)* Karelerde konuşma olacak. Ne olduğu **daha detaylandırılacak** — kullanıcı
bunu sonraya bıraktı, ve buraya bir tahmin yazılmıyor.

**Kararlaşmadı:** karakterin videoda konuşması mı *(ağzın sözle uyumu)*, kareye konuşma sesinin
binmesi mi *(metinden ses, bugünkü ses katmanının yanına ya da yerine)*, yoksa ikisi birden mi. Bunun
ardından gelen soru da açık: konuşmanın metnini kim yazıyor — kullanıcı mı, QueenAgent mı.

### Karta sağ tık — bağlam menüsü

*(Kullanıcı, 11 Eylül.)* Karta sağ tıklanınca bir menü açılacak ve oradan iş yapılabilecek; kullanıcı
ikisini saydı, **silme** ve **kopyalama**, ve *"vs"* diyerek listeyi açık bıraktı. Yine **Windows
gibi**.

Eylemlerin kendisi bugün var — seçim barında duruyorlar. Menü yeni bir yetenek değil, aynı işlere
ikinci bir kapı.

**Kararlaşmadı:** menüde silme ve kopyalama dışında ne olacağı. Ve asıl soru: birden çok kart
seçiliyken sağ tıklanan menü **seçimin tamamına** mı uygulanır yoksa yalnız tıklanan karta mı —
Windows'ta seçime uygulanır, ama bu karar burada da aynı olmak zorunda değil.

### Fotoğraf modeli her şeyi NSFW'ye çeviriyor

*(Kullanıcı, 11 Eylül.)* Bugünkü fotoğraf modeli, **başka bir şey istense bile** çıkanı NSFW'ye
çeviriyor. Üretim çalışıyor ve kare geliyor — gelen kare istenen şey olmuyor. Yani eksik olan bir
yetenek değil, modelin kendi eğilimi.

**Kararlaşmadı:** çözümün yeni bir fotoğraf modeli eklemek mi *(bugünkünün yanına, kare bazında
seçilebilir)*, bugünküyü değiştirmek mi, yoksa LoRA ya da prompt tarafında kalmak mı olduğu.

### Gerçekçi bir model eklenecek

*(Kullanıcı, 18 Eylül — "gerçekçi bir model eklenecek".)* **Ayrıntılar kullanıcıyla konuşulacak.**

### Video prompt'larında daha fazla kontrol

*(Kullanıcı, 19 Eylül — "video promptlarında daha fazla kontrol kazanmak".)* **Başlamadan önce
kullanıcıyla konuşulacak; ayrıntılar o konuşmada netleşecek.**

### Modeller bir yere yüklenip daha hızlı indirilebilir mi

*(Kullanıcı, 19 Eylül — "modelleri bir yere yükleyip daha hızlı indirebilir miyiz".)* **Ayrıntılar
kullanıcıyla konuşulacak.**

## MiniMax H3

*(Kullanıcı, 18 Eylül.)* MiniMax H3 üzerindeki yeni işler.

### Referansla içerik üretimi — H3 ile

*(Kullanıcı, 18 Eylül.)* H3 kullanılarak referansla içerik üretimi. **Ayrıntılar kullanıcıyla
konuşulacak.**

### H3 denemeleri

*(Kullanıcı, 18 Eylül — "belki biraz daha denersek daha kaliteli bir şeyler çıkarabiliriz".)*
**Ayrıntılar kullanıcıyla konuşulacak.**

---

## Hedefler

**Bölünmeden koşuya giremeyecek kadar büyük işler.** Yukarıdaki liste bir yol haritasının olduğu gibi
alabileceği maddeleri tutuyor; burası ise tek madde olmayı reddedenleri.

Bir hedefin sırası geldiğinde yapılan **ilk iş onu parçalara ayırmaktır**. Parçalar yukarıdaki
listeye ya da doğrudan o koşunun yol haritasına gider; hedefin kendisi, parçaları bitene kadar
burada durur.

### AI agent implement edilecek

*(Kullanıcı, 11 Eylül.)* Kullanıcının kendi tarifi: **çok büyük ve zorlayıcı bir iş**, küçük parçalara
bölünerek yapılacak. Buraya yazılmasının sebebi bu.

**Kararlaşmadı — henüz hiçbiri:** agent'ın queen-editor'ün içinde ne yapacağı; bu depoda zaten duran
**QueenAgent'la ilişkisi** *(onun taşınması mı, yanına ayrı bir şey mi, ikisinin konuşması mı)*; ve
parçalanmanın nereden başlayacağı. Üçü de sırası gelince detaylandırılacak, ve buraya bir tahmin
yazılmıyor.
