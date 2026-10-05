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

## Diğer

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

### Videoda uzaktaki yüzler daha detaylı olacak

*(Kullanıcı, 24 Eylül — "yüzler bir tık daha detaylı olsa videonun gerisine göre daha güzel olur,
böyle face detailer tarzı şeyler var mı"; H3'ün referanslı test videolarından sonra: "yakın çekimde
çok iyi, uzakta sıkıntı", "backloga atalım bunu şimdilik".)* **Ayrıntılar kullanıcıyla
konuşulacak.**

### HF indirmesi arada yarıda düşüyor

*(Kullanıcı, 2 Ekim — "arada oluyor"; H3 Eros Max beta5 %97'de düştü: `File reconstruction
error: CAS Client Error: Request middleware error: error sending request for url
(https://us.gcp.cdn.hf.co/xorbs/…)`.)* **Ayrıntılar kullanıcıyla konuşulacak.**

### Video prompt'ları üretilirken kullanıcı bir geri bildirim görecek

*(Kullanıcı, 2 Ekim — "queen editorde videoların promptları üretilriken usera bir feedback verelim
dondur snaıyor user".)* **Ayrıntılar kullanıcıyla konuşulacak.**

### Export'u Drive'da bulmak zor

*(Kullanıcı, 3 Ekim — "queen editorun exportunu driveda bulmak çok zor çünkü ilk proje dosyasını
sonra içidne export bulmak lazım", "Exporltar ve projeler iki klasöre ayrılsa ve exportlarda export
tarhi ve proje adı olarak adlandırılsa bulması oldukça kolaylaşırdı".)* **Ayrıntılar kullanıcıyla
konuşulacak.**

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
