# Backlog — Queen Editor

Gerçek ama henüz bir koşuya bağlanmamış işler. Sırası gelince buradan çıkar, o koşunun yol
haritasına girer.

İşler iki grupta durur: **Önemli** ve **Diğer**. Bir işin grubunu kullanıcı söyler; grup
söylenmeden eklenen iş Diğer'e girer.

---

## Önemli

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

### Editör kısmı eklenecek

*(Kullanıcı, 6 Eylül.)* Uygulama bugün **üretip dışa aktarıyor**: kare bir fotoğrafla başlıyor,
üstüne video ve ses biniyor, dışa aktarma hepsini tek klasörde birleştiriyor. Çıkanı **değiştiren**
hiçbir yer yok — beğenilmeyen kare yeniden üretiliyor.

Neyi kapsayacağı **kararlaşmadı**: fotoğrafın kendisine dokunmak mı *(kırpma, rötuş, inpaint)*,
video/ses tarafını kesip düzenlemek mi, yoksa karelerin sırasıyla oynamak mı.

### Gerçekçi bir model eklenecek

*(Kullanıcı, 18 Eylül — "gerçekçi bir model eklenecek".)* **Ayrıntılar kullanıcıyla konuşulacak.**

### Video prompt'unu yazan model fotoğrafı görsün

*(Kullanıcı, 21 Eylül — "bazen fotoğraf niyetimizle tutmuyor, ve video prompt ile fotoğraf tutmayınca
saçma şeyler ortaya çıkıyor".)* **v7'nin ilk maddesi olarak yazıldı, koşulmadan backlog'a döndü**
*(kullanıcı, 21 Eylül — "o kadar saçmalamıyormuş, test edildi")*: belirti beklenenden küçük çıktı.

**Bilinenler, geri gelirse işe yarar:**
- Bugün yazara verilen tek şey fotoğrafın **SDXL prompt'u** *(`data/xai_prompt_writer.py`)*, yani
  fotoğrafın *olması gereken* hâli. Fotoğraf niyetten saparsa hareket, orada olmayan bir sahneye
  yazılır.
- Kararlar alınmıştı: fotoğraf SDXL prompt'uyla **birlikte** gider ve talimat *"ikisi ayrılırsa
  fotoğraf kazanır"* der; yalnız **H3'ün yazarına**; fotoğraf gönderilemezse **iş düşer**, sessizce
  metin-yoluna dönülmez.
- İki engel: istemci bugün yalnız metin gönderiyor *(`services/xai/client.py`)*, ve modelin resim
  kabul etmesi gerekiyor — `grok-4.3` etmezse model ayarı değişir *(kullanıcı: "almazsa
  değiştiririz")*.
- **Maliyet ölçüldü** *(21 Eylül)*: xAI resmi 448×448 karolara bölüp karo başına 256 token sayıyor,
  artı bir karo, en çok altı karo — yani en çok ~1792 token. `grok-4.3`'ün girdisi $1.25/1M
  olduğundan kare başına ~$0.0008'den ~$0.0030'a çıkar; **1000 kare $0.75 yerine $3.00**.
  Küçültülmüş bir kopya *(448×672 ≈ 768 token)* bunu yarıdan aza indirir.

### Queen Editor Playwright MCP ile kontrol edilebilecek

*(Kullanıcı, 23 Eylül — "queen agent playwright mcp ile kontrol edilebilmek için düzenleme
gerekiyorsa onu da ekle", "queen editor olanları bakloga ekle".)* **Ayrıntılar kullanıcıyla
konuşulacak.**

## Diğer

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

### Fotoğraf modeli her şeyi NSFW'ye çeviriyor

*(Kullanıcı, 11 Eylül.)* Bugünkü fotoğraf modeli, **başka bir şey istense bile** çıkanı NSFW'ye
çeviriyor. Üretim çalışıyor ve kare geliyor — gelen kare istenen şey olmuyor. Yani eksik olan bir
yetenek değil, modelin kendi eğilimi.

**Kararlaşmadı:** çözümün yeni bir fotoğraf modeli eklemek mi *(bugünkünün yanına, kare bazında
seçilebilir)*, bugünküyü değiştirmek mi, yoksa LoRA ya da prompt tarafında kalmak mı olduğu.

### Video prompt'larında daha fazla kontrol

*(Kullanıcı, 19 Eylül — "video promptlarında daha fazla kontrol kazanmak".)* **Başlamadan önce
kullanıcıyla konuşulacak; ayrıntılar o konuşmada netleşecek.**

### Export hızı — çözme ve filtreler de karta

*(Kullanıcı, 21 Eylül, v6 testinin ortasında — "bu hız olayını backloga ekleyelim, şimdilik".)*
**v6'da madde 281 olarak yol haritasındaydı, koşulmadan backlog'a döndü.** Numara 281 olarak
kalır; geri gelirse aynı numarayla gelir.

**Bilinen, ve kullanıcının kendi ölçümü:** Colab'da `h264_nvenc` ile yapılan deneme kodlaması
döndü — yani **kart gerçekten kodluyor**, ve *"kodlama CPU'ya düşmüş"* ihtimali elendi. Geriye
kodlamanın etrafındaki CPU zinciri kalıyor: videoyu çözmek, 1920×1080 tuvale sığdırmak, bant
koymak, disclaimer'ı bindirmek — hepsi Colab'ın 2 vCPU'sunda.

**Ölçüm alındı** *(kullanıcı, 21 Eylül, Colab — 287'nin ekrana yazdığı dört satır)*:

| Adım | Süre |
|---|---|
| Videolar | 21,9 sn |
| Fotoğraflar | 0,5 sn |
| **Disclaimer** | **159,0 sn** |
| Drive'a kopyalama | 1,7 sn |

**Yani export'un %87'si tek adımda.** Diğer üçü toplam 24 saniye, ve 282'nin çözdüğü Drive yazması
artık 1,7 saniye. Kabaca 110 saniyelik video *(22 kare × ~5 sn)* 32 kare/saniyede ~3520 kare
eder, yani zincir **~22 kare/saniye** koşuyor — NVENC tek başına bunun kat kat üstünde olurdu, ve
kartın kodladığı doğrulandı. **Kalan aday, kodlamanın etrafındaki CPU zinciri.**

**Kararlaşmadı:** zincirin karta taşınıp taşınmayacağı. Taşımanın iki bilinen bedeli var —
`overlay_cuda` saydam PNG'de bozabiliyor *(girdinin `yuva420p`'ye çevrilip `hwupload` ile
yüklenmesi gerekiyor)*, ve yarım taşımak tam CPU'dan kötü. Kaldıraçların tamamı
[2026-09-21 export hızı araştırmasında](../docs/superpowers/research/2026-09-21-queen-editor-export-hizi.md).

### Loop'larda sona doğru tempo düşmesi — asıl çözüm

*(Kullanıcı, 23 Eylül — loop'lardaki tempo düşmesi için yapılan internet araştırmasının cevabından
şu paragrafı alıp: "Asıl çözüm: 3. yol. Hangi modelde yapılacağına göre iş değişiyor. H3'te iki uca
birden kare sabitleyerek loop'u kapatmak bir deneme maddesi olur. WAN'da ise yeni model (VACE)
gerektiriyor."; ve "bunu backlog'a at o zaman".)* **Ayrıntılar kullanıcıyla konuşulacak.**

### HF'nin yüksek hız ayarı — 429 çözülürse geri açılır

*(Kullanıcı, 23 Eylül — 312'nin ilk denemesinde H3 Qwen3-VL %69'da düştü: `HTTP status client error
(429 Too Many Requests), domain: https://us.gcp.cdn.hf.co/xorbs/…`; "internetten araştırır mısın
lütfen durumu", "araştırıp çözelim, bunun için madde açar mısın". 24 Eylül — "Hugging Face'in
ekstra hızını kapatalım, hata veriyor gibi, şimdilik kapatalım, backlog'a atalım".)*

**v7'de madde 313 olarak yol haritasındaydı, koşulmadan backlog'a döndü** *(kullanıcı, 24 Eylül)*;
ayarı madde 316 kapattı. Numara 313 olarak kalır; geri gelirse aynı numarayla gelir.

**Bilinenler:**
- Ayar açıkken Qwen3-VL 276–394 MB/s ile iniyordu, kapalıykenkinin 2–3 katı. 47 saniyede 10.2 GB'a
  vardıktan sonra HF'nin parça sunucusu 429 döndü; dosya ve koşu düştü. Ayar kapalıyken iki tam
  koşuda 429 hiç gelmedi; kapalı koşunun indirmesi 11 dk 18 sn sürdü.
- HF'nin belgelediği istek sınırları `/resolve/` adresleri için; parça sunucusunun (`cdn.hf.co`)
  sınırı hiçbir belgede yok *([Hub Rate limits](https://huggingface.co/docs/hub/rate-limits))*.
- Ayar paralel akışları 1 yerine 16'dan başlatıyor, tavanı 64'ten 124'e çıkarıyor, tamponları
  büyütüyor; HF onu en az 64 GB RAM'li makineler için yazıyor
  *([Using Xet Storage](https://huggingface.co/docs/hub/en/xet/using-xet-storage))*.
- `hf_xet`'in kaynağına göre parça indirmesindeki 429 yeniden deneniyor, sunucunun `Retry-After`'ına
  bakılmadan. Beklemeler 3, 9, 27, 81, 243 sn diye büyüyor, her biri rastgele kısaltılıyor ve en
  fazla 6 dakika *([xet-core](https://github.com/huggingface/xet-core))* — yani beş denemenin 47
  saniyede tükenmesi beklenmiyor. `hf_xet`'in neden bu kadar çabuk bıraktığı **bilinmiyor**.

**Geri gelirse ilk iş** ayar açıkken düşen bir koşunun `hf_xet` log'u:
`!grep -h -i -E "429|retry|concurrency" ~/.cache/huggingface/xet/logs/* | tail -n 80`. 429 yeniden
denendiyse `hf_xet`'e daha uzun deneme süresi vermek yetebilir; hiç denenmediyse ya da hemen
bırakıldıysa yeniden denemeyi bizim kodumuz yapar.

### Notebook sadeleşecek — kodu test edilebilir Python'a

*(Kullanıcı, 24 Eylül — "noteboboku sadeleştirmek kodları olanbildğince test edilevilir python
koduna dönüştürmek".)* **Ayrıntılar kullanıcıyla konuşulacak.**

### Üretim süreleri kaydedilip gösterilecek

*(Kullanıcı, 24 Eylül — "her fotoğraf video ses ne kadar sürede üretildi kayıt edilim ve
gösterleim".)* **Ayrıntılar kullanıcıyla konuşulacak.**

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
