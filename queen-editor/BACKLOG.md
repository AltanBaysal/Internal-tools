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

### Export ekranı üretilen videoyu kuyrukta saymıyor

*(518'in QA'sı buldu, 30 Ekim; bu koşudan eski.)* Bir video üretilirken export ekranı "Üretim sürüyor — 0
video kuyrukta" diyor. Sayı galerinin `owed`'undan geliyor (`ExportScreen.jsx`), ve üretilmekte olan iş
orada sayılmıyor.

### Birleşik export'ta her parçanın sesi sonrakine taşıyor

*(515'in QA'sı buldu, 29 Ekim; bu koşudan eski, gerçek ffmpeg'le ölçüldü.)* Birleşik export'ta her
parçanın sesi bir sonraki parçanın içine ~50 ms taşıyor: 440 Hz'lik bir parçanın sesi, ardından gelen
sesi kapalı parçada 11.00–11.05 s arasında duyuldu. Büyük ihtimalle AAC'nin her parçaya eklediği dolgu,
birleşim yerlerinde birikiyor. Şimdilik düzeltilmiyor.

### Katmanı kırmızı karonun seçim dairesine basılamıyor

*(519'un QA'sı buldu, 30 Ekim; 519'dan eski.)* Galeride fotoğrafı inmiş ama bir katmanı kırmızı karoda
fare üstüne gelince Tekrar dene perdesi iniyor (`VEIL`, `zIndex: 3`), ve seçim dairesinin (`CHECK`,
`zIndex: 2`) üstünü örtüyor: daireye basılamıyor. Kare yine Tümünü seç'le ya da kare sayfasından
seçilebiliyor. 519'dan beri videosu kırmızı kopya kareler de böyle görünüyor.

### Video paneli zaten sırada olan videoyu da sayıyor

*(519'un QA'sı buldu, 30 Ekim; 519'dan eski.)* Videosu zaten sırada olan karelere iki varyantla basmadan
önce panel *"6 video üretilecek"* diyor, basış ise 3 iş ekliyor: kare başına karenin kendi videosu
eklenmiyor (513'ün "sırada olan yeniden eklenmez"i), yalnız kopyası. Kare sayısı doğru, varyant başına
tahmin değil (`LayerPanel`'in `owed`'u: kapsam × varyant).

### Aynı kimlik iki kez gelince kare iki kez sayılıyor

*(519'un coder'ı ve reviewer'ı buldu, 30 Ekim; denenmedi, bu koşudan eski.)* Kare listesi taşıyan
kapıların ortak denetimi `checked` (`domain/frame_list.py`) yalnız listenin metin dizisi olduğuna bakıyor,
aynı kimliğin iki kez gelmesine bakmıyor. `remove_frames` böyle bir kareyi cevabında iki kez sayıyor
(`deleted` ya da `removed`), `copy_frames` aynı kareye iki ikiz yapar. `dequeue_layer` bunu kendi içinde
ayıklıyor (`dict.fromkeys`). Düzeltme `checked`'te, bütün çağıranlar için: tekrar eden kimlik bir kez
sayılır.

### Aynı anda gelen kuyruk basışı ve yeniden adlandırma bir işi bekletebilir

*(511'in reviewer'ı buldu, 29 Ekim.)* Bir proje aynı anda hem kuyruğa iş alır hem yeniden adlandırılırsa
iş başlamadan kalabilir. Yol: basış işi `P` projesine yazar; yeniden adlandırma `P`'yi `Q`'ya taşır ve
adın tutucusunu `Q`'ya çevirir; basış ardından işçiyi eski adla, `P` ile alır; koşu var olmayan `P`'yi
okur, borç bulmaz ve `done` yayımlar — iş `Q`'da borçlu kalır. İki sekme ya da yeniden
adlandırma sürerken basan ajan gerekir. Düzeltme, işçiyi almakla yeniden adlandırmanın adı kimin
tuttuğunda anlaşmasını ister (ör. `start` artık var olmayan bir adı reddeder).

### Referans sırası ve arşiv işaretleri aynı anda iki yazmada birini kaybedebilir

*(512'nin coder'ı buldu, 29 Ekim; denenmedi.)* 512 projenin planını, kaydını ve galeri sırasını yazan
kapıları tek kilide aldı. Okunup bütün yeniden yazılan iki dosya hâlâ kilitsiz, aynı anda iki yazmada
sonra yazan öncekininkini siliyor:
- referans havuzunun sırası (`add_references`, `remove_reference`, `save_reference_order`);
- arşiv işaretleri (`arsiv.json`, `DriveProjectStore`): aynı anda iki arşive kaldırma birini kaybeder.

Düzeltme `DriveMuteStore`'un yolu: okuma ve yazma tek kilitte.

### Fotoğraf kaydına aynı anda iki satır yazılabilir

*(512'nin reviewer'ı buldu, 29 Ekim; Colab'da denenmedi.)* `DrivePhotoRecord.append` `photos.jsonl`'e
kilitsiz ekliyor; sıra (biten katmanın satırı) ve kapılar (kopya karenin satırları, işaretler) aynı
anda ekleyebiliyor. Yerel Linux'ta tek bir `O_APPEND` yazması ötekine karışmaz; Drive'ın FUSE bağlamasının
bunu koruyup korumadığı bilinmiyor. `chat_record` aynı yazmayı bu yüzden kilitliyor. Colab'da denenecek:
aynı anda çok sayıda satır ekleyip dosyada yarım ya da kayıp satır var mı.

513 de buna dayanıyor: bir kararın satırı (`from`'lu) ancak okunduğu durumun üstüne düşerse geçerli, ve
bu, satırların dosyada eklendikleri sırada durmasına bağlı. Denemede satırların sırası da bakılacak:
ekleme sırası ile dosyadaki sıra aynı mı.

### Kopyala'dan sonra galerinin seçimi kopyanın üstüne geçiyor

*(513'ün QA'sı buldu, 29 Ekim; 513'ten eski, ekranda.)* Kullanıcı bir kare seçip Kopyala'ya basınca
seçim, seçtiği karede değil kopyanın üstünde duruyor; ardından basılan "Videoları sil" kopyanın videosunu
sildi. Seçim karenin kimliğiyle değil dosya adıyla tutuluyor gibi görünüyor, ve kopya kare kaynağının
fotoğrafını, dolayısıyla adını paylaşıyor (madde 102). Düzeltme seçimi kimlikle tutmayı ister.

### Yeniden adlandırma bir videoyu boş prompt'la ürettirebilir

*(513'ün coder'ı buldu, 29 Ekim; denenmedi.)* Sıranın turu planı ve kaydı adın kapısında, tek adla okur
(513). Ama turun sonraki okumaları — karenin sözleri (`record.prompts`), altındaki fotoğraf, yazılmış
prompt (`written_prompts`) — o adla, kapının dışında yapılıyor. Yeniden adlandırma bunların arasına
düşerse çoğu okuma eski adda bir şey bulamaz ve deneme düşüp yeniden denenir. Ama taşıma tam fotoğrafın
okunmasıyla yazılmış prompt'un okunması arasına düşerse prompt boş gelir ve video boş prompt'la üretilip
yeni klasöre yazılır. Bitmiş bir şeyin yeniden üretilmesi değil; yanlış bir video. Düzeltme, turun
render'dan önceki okumalarının da aynı ada bağlanmasını ister (yazar çağrısı kapının dışında kalarak).

### Windows'ta okunan bir dosyanın üstüne kayıt düşebilir

*(512'nin coder'ı buldu, 29 Ekim; yalnız yerelde.)* Windows açık bir dosyanın üstüne `os.replace`'e izin
vermiyor (`[WinError 5] Access is denied`). Döngü ya da galeri bir dosyayı okurken onun kaydı gelirse
kayıt düşer ve ekran hatayı gösterir; hiçbir şey kaybolmaz. Colab Linux olduğu için orada olmaz.

### Kendi kutusu olan modelde bilinmeyen LoRA çizimi durdurmuyor

*(501'in reviewer'ı buldu, 28 Ekim.)* Madde 238'in kuralı: kutunun bilmediği bir LoRA çizimi durdurur,
çünkü yerine başka bir şeyle çizilen kare istenen kare değildir ve bunu söyleyen bir yer yoktur. Satırı
kendi kutusunu taşıyan modellerde — Krea 499'dan beri, DaSiWa 501'den beri — eski bir plan
satırındaki bilinmeyen LoRA ise sessizce kutunun ilk satırıyla çiziliyor (`catalog.drawn_with`).
Kuyruğa ekle böyle bir LoRA'yı zaten reddediyor; yalnız bir checkout'un bilmediği bir kimliği taşıyan
eski satırlarda olur. Düzeltme kararı kullanıcının: ya bu modellerde de çizim durur, ya kural 238'e
istisna olarak yazılır.

### Boşta Colab kapansın

*(Kullanıcı, 27 Ekim — "bence bunu roadmapten backloga koyalım şuanlık kapatmak yerine bildirim
yollasın sadece"; v11 roadmap'inin v11-2'sinden çıktı.)* Sıra 10 dk boş kalınca Queen Editor "orada
mısın?" diye sorar; *"sorudan sonra 5 dk da cevapp kalmazsa kapansın"*. Süren export ya da ajan iş
sayılır. Bugün geri sayım ve kutu yok ([509 · v11-8](../docs/arsiv/roadmaps/2026-10-24-queen-editor-v11-roadmap.md#v11-8)
kaldırdı); yalnız sıra boşalınca ya da durunca bir bildirim geliyor. Sekme kapalıyken bildirim de gitmez, A100'ü o
durumda ancak kapatma kurtarır. Açık soru: sekme kapalıyken kim sayar — bunu Colab tarafı yapmalı.

### Silinmiş fotoğraftan video, ve kopya karenin fotoğrafının üstüne yazılması

*(497'nin coder'ı buldu, 27 Ekim; denenmedi.)* `run_loop._source_for` ve `_end_for` karenin fotoğraf
hücresini durumuna bakmadan alıyor, bu yüzden silinmiş bir hücre de dosyasını veriyor. Yol: kopya kare
`C1_F`, `F.png`'yi paylaşıyor. `F`'in videosu sıradayken fotoğraf katmanı siliniyor; `remove_layer`
videoyu düşürmüyor, ve `F.png` kopya kare tuttuğu için diskte kalıyor. Video silinmiş fotoğraftan
yapılıyor, `F`'in fotoğraf yeri boş olduğu için videonun ilk karesi `F.png` olarak kaydediliyor, ve
`os.replace` kopya karenin resminin üstüne yazıyor.

### Galeriden yapılan bir işlemin hatası fotoğraf sekmesinde görünmüyor

*(497'nin coder'ı buldu, 27 Ekim.)* Galeriden yapılan bir yazma — sıralama, silme, kopyalama —
reddedilince hata `ProjectScreen`'in `error`'una gidiyor. GeneratePanel onu yalnız kendi Kuyruğa ekle'si
reddedilince gösteriyor, bu yüzden fotoğraf sekmesi açıkken bu hata ancak video, ses ya da sıra
sekmesine geçince görünüyor. Hata sunucunun cümlesini taşıyor; eksik olan yeri.

### Windows'ta sıranın süre satırı yazılamıyor

*(497'nin QA'sı buldu, 27 Ekim; yalnız yerelde.)* Windows'ta stdout cp1252 iken sıranın `⏱ …` satırı
yazılamıyor ve sıra 'charmap' hatasıyla duruyor; `PYTHONIOENCODING=utf-8` ile geçiyor. Colab UTF-8
olduğu için orada olmaz.

### Civitai yoklaması iyi bir dosyayı reddedebiliyor

*(484'ün reviewer'ı buldu, 21 Ekim.)* `colab/downloads.py`'nin `civitai_probe`'u ve `check_binary`'si
gelen ilk baytlar `<` ya da `{"` ile başlıyorsa cevabı hata sayıyor. Ama bir safetensors dosyası 8
baytlık başlık uzunluğuyla başlar, ve o uzunluğun ilk baytı 256'da bir 0x3C (`<`) olur — o dosya her
seferinde reddedilir. Tersine, boşluk ya da BOM'la başlayan bir hata sayfası geçer. Düzeltme:
`raw[8:10] == b'{"'`'ye bakmak; 484'ün deneme notebook'ları böyle yapıyor.

### Kopya karenin fotoğrafını Yeniden üret, modelini ve LoRA'sını kaybediyor

*(481'in reviewer'ı buldu, 20 Ekim.)* `regenerate.py` modeli ve LoRA'yı karenin kartından alıyor; kopya
karenin kartı kayıttan gelir ve ikisini taşımaz. Bu yüzden kopya karede fotoğrafı Yeniden üret,
uyarı vermeden grafiğin kendi modeline, LoRA'sız düşüyor. Doğru ayar, resmi yapan plan satırında —
481'in `copy_frame.py`'deki kuralı bunu buluyor; Yeniden üret de onu kullanabilir.

### Silinmiş bir kareye bağlanan kuyruktaki video

*(481'in reviewer'ı buldu, 20 Ekim.)* Bağlantılı modda bir videonun işi bir sonraki karenin kimliğini
taşır (`linkedTo`). O kare silinirse, `run_loop`'un `_end_for`'u hücrenin silindiğine bakmıyor
(`not cell`, `is_taken` değil) ve üreticiye boş bir son kare veriyor; iş her denemede düşer. Kare
silme (`remove_frames`) bugün bu yola varıyor. 481'in düzeltmesi böyle bir kareye hiç dokunmaz.

### Eski adla yeniden çizilen fotoğraf tarayıcıda eski görünebilir

*(481'in coder'ı buldu, 20 Ekim.)* Fotoğraflar bir yıl boyunca değişmez diye önbelleğe alınıyor
(`Cache-Control: … immutable`), çünkü bir ad hiç yeniden kullanılmıyor. İki yer bu kuralı bozuyor:
`retry_frame`'in "kırmızı bir şey yok" yolu silinmiş bir fotoğrafı aynı adla yeniden üretiyor, ve
`run_loop` fotoğrafı silinmiş bir kartta videonun ilk karesini `photo_file(fid)` adıyla kaydediyor.
İkisinde de o fotoğrafı daha önce görmüş bir tarayıcı eskisini göstermeye devam edebilir.

### Kodda var olmayan BEHAVIOUR.md'ye bağlantılar

*(480'in reviewer'ı buldu, 20 Ekim.)* `queen-editor/backend`'de 8 dosyada 14 yorum "BEHAVIOUR.md, Agent
panel" gibi bir yere bağlanıyor, ama repo'da — git geçmişinde de — öyle bir dosya hiç olmamış. Ya
bağlantılar doğru belgeye çevrilir ya kaldırılır. Kullanıcının göreceği bir şey değişmez.

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
[2026-09-21 export hızı araştırmasında](../docs/arsiv/research/2026-09-21-queen-editor-export-hizi.md).

### Loop'larda sona doğru tempo düşmesi — asıl çözüm

*(Kullanıcı, 23 Eylül — loop'lardaki tempo düşmesi için yapılan internet araştırmasının cevabından
şu paragrafı alıp: "Asıl çözüm: 3. yol. Hangi modelde yapılacağına göre iş değişiyor. H3'te iki uca
birden kare sabitleyerek loop'u kapatmak bir deneme maddesi olur. WAN'da ise yeni model (VACE)
gerektiriyor."; ve "bunu backlog'a at o zaman".)* **WAN 435'te Queen Editor'den çıktı:** geri gelirse
yalnız H3'ün yolu kalır. **Ayrıntılar kullanıcıyla konuşulacak.**

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

### Video prompt'ları üretilirken kullanıcı bir geri bildirim görecek

*(Kullanıcı, 2 Ekim — "queen editorde videoların promptları üretilriken usera bir feedback verelim
dondur snaıyor user".)* **Ayrıntılar kullanıcıyla konuşulacak.**

### Harcanan token görünecek: ne kadarı önbellekten, ne kadarı değil

*(Kullanıcı, 9 Ekim — "queen editor backlgounda queen eagetn gibi harcanan token ne kadar miss ne
kadar chacne vs gibi bir ksıım ekleyleim olur mu".)* QueenAgent bunu her cevabın altında gösteriyor
*(madde 354, `queen-agent/frontend/src/features/workspace/Stamp.jsx`)*: DeepSeek'e gidenin önbellekte
olan kısmı ve olmayan kısmı, iki ayrı sayı — önbellekteki token yaklaşık ellide bir fiyata. Queen
Editor'de DeepSeek'e Queen AI'ın prompt'ları ve agent gidiyor. **Ayrıntılar kullanıcıyla
konuşulacak:** nerede görüneceği — agent'ın cevabında, prompt'un kartında, projenin toplamında —, ve
kontrol isteklerinin (418) de sayılıp sayılmayacağı.

### Notebook GPU'suz oturumda da açılacak — üretici seçilmediyse

*(Kullanıcı, 5 Ekim — "gpusuz oturumda bir üretim araçı seçilyse hata versin bütün üretim araçları
kapalıysa çalışsın", "ama şuan bunu değiştirme"; v9'un 413'üne not olarak düşülmüştü. 13 Ekim —
"Şimdilik BACKLOG'a yazayım, sonraki roadmap'le birlikte gelsin".)*

**Claude'un geri söylediği, henüz onaylanmadı:** GPU'suz bir Colab oturumunda fotoğraf, video ve ses
kutularının hiçbiri işaretli değilse notebook GPU sormaz, sonuna kadar çalışır ve uygulamanın linki
gelir — projeler açılır, bakılır, export edilir, üretim yok. En az bir üretici işaretliyse ve GPU
yoksa notebook CONFIG'de bugünkü *"GPU yok"* hatasıyla durur.

**Bilinenler:**
- CONFIG bugün tam tersini yapıyor: hiçbir üretici işaretli değilse *"Hiçbir üretici seçilmedi"*
  diye duruyor *(13 Ağustos'un kurulum seçimi kararı; bu istek onu geri alıyor)*, ve GPU yoksa ne
  seçildiğine bakmadan duruyor.
- GPU'suz oturumda ComfyUI kalkmaz, ve ComfyUI hücresi 433'ten beri kalkmayan ComfyUI'de hata
  veriyor: üretici seçilmediyse ComfyUI'nin kurulup başlatılmaması gerekecek. Nasıl yapılacağı
  spec'te, kod okunduktan sonra.

### Notebook DaSiWa'yı kurarken zaman aşımına düşüyor — llama-cpp-python

*(Kullanıcı, 15 Ekim — Colab'da ComfyUI hücresi `RuntimeError: pip install ComfyUI-DaSiWa-Nodes:
timeout (300s)` ile düştü, hücre 6 dk 49 sn sürdü; "backloga yaz".)*

**Claude'un geri söylediği, henüz onaylanmadı:** ComfyUI hücresi DaSiWa'yı kurarken zaman aşımına
düşmez: `llama-cpp-python` kurulmaz, günlükte sam2'ninki gibi *"… kurulmuyor — grafiklerimiz
kullanmıyor"* satırı görünür, ve hücre yaklaşık beş dakika kısalır.

**Bilinenler:**
- DaSiWa'nın listesinde bugün `llama-cpp-python>=0.3.26` var. 314'ün 23 Eylül'de okuduğu listede
  yoktu *(testteki kopyası `backend/tests/test_colab_nodes.py`'de)*; DaSiWa listeyi 25–26 Eylül'de
  değiştirdi, ve aynı arada `safetensors`, `nvidia-ml-py` ve yalnız Windows'ta `amd-adlx` da geldi.
- Neden takıldığı: llama-cpp-python PyPI'da Linux için hazır paket vermiyor *(Claude'un bildiği, bu
  oturumda doğrulanmadı)*, pip llama.cpp'yi Colab'da derlemeye girişiyor, ve 300 saniye derleme
  bitmeden doluyor — 314'te sam2'nin yaşadığının aynısı.
- Bize gerekmiyor: DaSiWa `llama_cpp`'yi yalnız `nodes/llm_runtime.py`'de, yerel GGUF dil modelini
  yükleyen fonksiyonun içinde ve `try/except ImportError` ile alıyor — paket yoksa DaSiWa yine
  yüklenir. H3 grafiklerimiz *(`assets/workflow_video_h3_api.json`, `…_first_last_api.json`)* LLM
  düğümü kullanmıyor, ve `MiniMaxH3Director` bu satırdan önce de çalışıyordu.
- Düzelene kadar yeni bir oturumda hücre her seferinde aynı yere düşüyor: H3 kurulamıyor.
- Atlanan satırlar `colab/nodes.py`'nin `SKIPPED`'inde satırın tam metniyle duruyor; DaSiWa sürüm
  sınırını değiştirirse eşleşme kaçar. Nasıl yapılacağı spec'te, kod okunduktan sonra.

**Bağlı ama ayrı bir sorun, ayrı madde olup olmayacağı kararlaşmadı:** pip'i yarıda kalan bir düğüm,
aynı oturumda hücre yeniden çalışınca *"zaten var"* sayılıyor — `install_node` yalnız klasörün dolu
olmasına bakıyor. Hücre geçer, ama düğümün listesinden hiçbir şey kurulmamış olur; bu kez hatayı
gizlerdi.

### H3'ün yeni sürümüne geçilecek

*(Kullanıcı, 15 Ekim — "backloga h3 ün yeni sürümüne geçi ekle".)* Bugün kullanılan H3 dosyası
`MiniMaxH3/10Eros_Max_h3_TURBO-hybrid_beta5_int8.safetensors`; adını
`backend/features/producers/domain/model_groups.py` ve iki H3 grafiği *(`assets/workflow_video_h3_api.json`,
`…_first_last_api.json`)* okuyor. **Ayrıntılar kullanıcıyla konuşulacak:** hangi sürüme geçileceği.

### ComfyUI ve düğümler bizim sabitlediğimiz sürümden gelecek

*(Kullanıcı, 15 Ekim — rgthree'nin bozulmasından sonra: "comfyuiın kendi verisyonumuz hf ye vs bir
yere kaydedelim ordan indirelim daha tutarlı olur".)*

**Claude'un geri söylediği, henüz onaylanmadı:** Dışarıda yeni bir sürüm çıktı diye yeni bir oturum
bozulmaz. ComfyUI da düğümler de en son denenip çalışan sürümden gelir, ve sürüm ancak biz
güncellediğimizde değişir.

**Bilinenler:**
- Son beş günde dışarıdan iki kırılma geldi, ikisi de bir düğümden, ComfyUI'nin kendisinden değil.
  DaSiWa listesine `llama-cpp-python` ekledi, hücre zaman aşımına düştü (yukarıdaki madde). rgthree
  15 Ekim'de varsayılan dalını 2023'ten kalma `dev`'e çevirdi, Power Lora Loader kayboldu ve fotoğraf
  grafiği reddedildi — 470 rgthree'yi `main`'den klonlatarak kapattı.
- Bugün sabitlenmiş bir şey yok: `colab/comfy.py` ComfyUI'yi klonlayıp `git pull` yapıyor,
  `colab/nodes.py` düğümleri varsayılan dallarından en son hâlleriyle alıyor — rgthree hariç, o
  470'ten beri `main`'den, ama yine en son hâliyle. 470'in `BRANCHES` tablosu bu maddenin kuracağı
  yapının içine katılır: her düğüm bir sürüm alınca dal ayrı bir tablo olarak kalmaz.
- İki yol konuşuldu, nasıl yapılacağı spec'te: **(a)** kullanıcının önerisi, kendi kopyamızı HF'ye ya
  da başka bir yere koyup oradan indirmek; **(b)** Claude'un önerisi, ComfyUI'yi ve her düğümü bir
  commit'e sabitlemek (`git checkout <sha>`) — taşınacak kopya yok, (a) yalnız kaynak silinirse öne
  geçer.
- İki yol da düğüm listelerindeki aralıklı pip paketlerini *(ör. `transformers>=4.45.0`)* sabitlemez:
  onlar PyPI'dan güncel gelmeye devam eder.

### Düşük çözünürlükle video üretim hızı

*(Kullanıcı, 20 Ekim — haftalık planın 14. maddesi: "Video çözünürlüğünü düşürerek üretim hızını
artır"; "Risk: Kalite hedefleriyle (1. hedef, backlog'daki "ilk 1 dakika kalitesi") çelişebilir; HD
altına inilirse platformdaki HD avantajı kaybolabilir. Alternatif: düşük çözünürlükte üretip upscale
etmek." Aynı gün v10'a yazıldı, hizalanmadan döndü — "bu taskı backloga ekle".)*

**Bilinenler:**
- H3 videoyu bugün 576×864'te, 24 kare/saniyede üretiyor *(`assets/workflow_video_h3_api.json`,
  `…_first_last_api.json`)*; birleşik export onu 1920×1080'lik tuvale büyütüyor. Bir videonun ne
  kadar sürdüğü ölçülmedi.
- Düşürülecek boyut da H3'ün çalıştığı çözünürlüklerden biri olmalı *(kullanıcı, 20 Ekim, v10-3 için
  — "h3 ün çalıştığı oranlar var o oranlarda olmalı pixel sayılarındadikka et")*, ve v10-3'ün
  yatayından sonra o boyuttan ölçülür.
- *"İlk 1 dakika kalitesi"* bu deponun backlog'unda yok; ne dediği kullanıcıya sorulacak.
- Fotoğraf tarafının hızı ayrı bir iş: yukarıdaki *"Fotoğraf üretim hızı — hız LoRA'ları"*.

**Claude'un önerisi, henüz onaylanmadı:** aynı kare bugünkü ve H3'ün desteklediği bir alt boyutta
üretilir, iki süre ve iki video yan yana konur, kullanıcı seçer; upscale yalnız kalite yetmezse
denenir. **Ayrıntılar kullanıcıyla konuşulacak.**

### Uygulamanın mimari çizimi, ve yapıyı değiştiren işte önce çizim

*(Kullanıcı, 20 Ekim — "mimari diagram blok diagram uygulama için aslında bundan olsa çpk işime
yarardı kodu okumadan anlayabilirdim yada önce sende burda tasarlar sonra kodunu yazardın";
"şimdilik ypaamylaım backlgoa at".)* **Claude'un anlayışı, henüz onaylanmadı:** Queen Editor'ün bir
mimari çizimi olur — kutularla, düz metin: ekran, backend'in özellikleri, servisler, dış servisler
(Drive, ComfyUI, DeepSeek, xAI) —, kod okunmadan anlaşılır. Çizim kutu seviyesinde kalır, fonksiyona
inmez, ve yapıyı değiştiren bir iş onu aynı commit'te günceller. Yapıyı değiştiren bir işin spec'i bir
"bugün / sonra" çizimiyle başlar ve kod, kullanıcı çizimi onayladıktan sonra yazılır. QueenAgent'ın
backlog'unda aynısı var; "önce çizim" kuralı iki aracın ortak kuralı olacağı için CLAUDE.md'ye girer,
önce kullanıcıya gösterilerek. **Ayrıntılar kullanıcıyla konuşulacak.**

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

**İlk parça:** [v9-4](../docs/arsiv/roadmaps/2026-10-05-queen-editor-v9-roadmap.md) — salt
okunur sohbet *(kullanıcı, 5 Ekim)*.
