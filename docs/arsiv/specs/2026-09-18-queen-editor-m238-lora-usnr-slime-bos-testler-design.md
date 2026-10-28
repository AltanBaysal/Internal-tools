# Madde 238 · LoRA kutusu: USNR, Slime, Boş — test turunun tasarımı

**Tarih:** 18 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

## Kullanıcıdan gereken

Hiçbir şey. Üç soru 18 Eylül'de soruldu ve cevaplandı *(maddenin satırında)*:

1. Kutu **her modelde USNR ile açılıyor**, DaSiWa'da da.
2. **Proje son seçilen LoRA'yı hatırlıyor**, Model kutusu gibi.
3. Liste okunamazsa arayüz düğmeyi kapatmıyor; **neyin geçerli olduğunu backend söylüyor**
   *(kullanıcı: "backend hata döndersin, bunu UI problemi yapmayalım")*.

## Bugün ne oluyor

Madde 237'den beri LoRA kutusu `Standart` ile açılıyor, değeri boş. Standart **modelin kendi
dizilimi** demek *(`domain/catalog.py`, her modelin `loras`'ı)*: Nova'da USNR 0.8, DaSiWa'da hiçbiri.
Kutudaki tek gerçek LoRA Slime. Yani USNR tek başına bir seçim değil: DaSiWa'nın üstüne konamıyor,
Nova'dan da çıkarılamıyor. LoRA seçimi projeye yazılmıyor, ve kuyruk isteğindeki LoRA hiç
denetlenmiyor — tanınmayan bir LoRA ancak render'da düşüyor.

## Ne olacak

**Kutuda üç satır, bu sırayla:** `USNR` *(0.8)*, `Slime` *(0.9, tetikli)*, `Boş` *(hiç LoRA yok)*.
Değerleri `usnr`, `slime`, `none`. **Modelin kendi dizilimi kalkıyor:** model yalnız bir checkpoint,
yükleyicinin yuvalarını kutudaki seçim dolduruyor.

**Varsayılan USNR, iki yerde aynı kuralla.** Panel boş bir kutuyu sunucunun ilk satırıyla dolduruyor
— Model kutusunun bugünkü kuralı — ve sunucu USNR'yi ilk sırada veriyor. Render eden yer de LoRA
söylemeyen bir kareyi USNR ile üretiyor.

**Boş'un kendi değeri var, çünkü boş değer *söylenmemiş* demek.** Boş'u boş bir değerle taşımak iki
yerde bozulurdu:

- Panel boş kutuyu ilk satırla doldurduğu için, Boş seçen kullanıcının kutusu USNR'ye geri dönerdi.
- Diskteki kareler boş değeri *Standart* anlamında taşıyor. Nova'da Standart USNR'di, yani boş değeri
  USNR okumak o kareleri üretildikleri gibi bırakıyor.

Tek istisna: 237 ile 238 arasındaki birkaç saatte DaSiWa + Standart ile gönderilmiş bir kare yeniden
üretilirse USNR ile çıkar. Göç yazılmıyor *(kullanıcı, madde 237: "migration'a çok takılma")*.

**Eski değerler bugünkü gibi.** `recipe:nova3dcg` Nova + USNR, `recipe:slime` Nova + Slime, elenen
iki Nova Nova + USNR. Modelsiz ve çıplak dosya adlı kareler grafiğin kendi LoRA'sıyla üretiliyor, o
da USNR.

**Proje LoRA'yı hatırlıyor.** Ayar dosyası modelin yanında `lora`'yı da taşıyor; "Kuyruğa ekle"ye
basılınca yazılıyor, proje açılınca kutu onunla açılıyor. Eski ayar dosyalarında LoRA yok: boş
okunuyor, panel de ilk satırla dolduruyor. Kayıtlı bir LoRA listede artık yoksa kutu onu **kendi
değeriyle seçili tutuyor**, Model kutusunun bugünkü kuralıyla: kullanıcıyı sessizce başka bir satıra
kaydırmak, seçmediği bir LoRA ile üretmek olurdu.

**Neyin geçerli olduğunu backend söylüyor.** Kuyruk isteği katalogda olmayan bir LoRA taşıyorsa
reddediliyor. Sebep cümlesi, kutunun adıyla *(`field: "lora"`)* düğmenin altına geliyor ve kuyruğa
hiçbir şey girmiyor. Boş, `usnr`, `slime` ve `none` geçiyor. Bu, kurulumu denetlemek değil: LoRA
dosyaları her fotoğraf kurulumunda iniyor. Denetlenen, uygulamanın kendi listesi. Bilmediği bir LoRA
hiçbir makinede üretilemez, ve bunu düğmede söylemek karenin sonra düşmesinden iyidir. Render'ın kendi
reddi de kalıyor: plandaki eski kareleri o koruyor.

**Kare detayı LoRA'yı adıyla yazıyor.** LoRA söylemeyen bir karede satır **çizilmiyor**. Oraya bir
ad yazmak uydurmak olurdu: `recipe:slime` kareleri Slime ile üretildi ama LoRA'ları boş, ve DaSiWa'nın
birkaç saatlik kareleri LoRA'sız üretildi. Modelsiz karede Model satırı da aynı sebeple çizilmiyor.

**Liste gelmeden** LoRA kutusu, Model kutusu gibi `yükleniyor…` diyor ve kapalı duruyor. **Liste
okunamazsa** kutu `liste okunamadı` diyor ve kapalı duruyor. Düğme açık kalıyor, istek elindeki
seçimle gidiyor — projenin kayıtlı LoRA'sı, ya da hiç seçilmemişse boş değer, yani USNR. İkisi de
geçerli; geçersizse backend söylüyor. Bugünkü `Standart` yedeği gidiyor: sunucunun bildiği bir adı ön
yüze kopyalardı *(FOUNDATION, Karar 4)*.

**Defter değişmiyor.** İki LoRA dosyası zaten her fotoğraf kurulumunda iniyor. Değişen tek şey, USNR'nin
artık her modelin üstüne seçilebilmesi, yani inmesinin boşa olmaması.

## Çivilenecek olgular

| # | Ne diyor | Bugün |
|---|---|---|
| 1 | Katalogdaki LoRA'lar USNR ve Slime, bu sırayla | **kırmızı** |
| 2 | LoRA listesi USNR, Slime, Boş — değerleri `usnr`, `slime`, `none` | **kırmızı** |
| 3 | `/api/models` aynı üç satırı veriyor | **kırmızı** |
| 4 | LoRA söylemeyen bir Nova karesi USNR ile üretiliyor | yeşil *(bekçi)* |
| 5 | LoRA söylemeyen bir DaSiWa karesi de USNR ile üretiliyor | **kırmızı** |
| 6 | USNR seçilen kare yalnız USNR'yi yüklüyor ve prompt'a dokunmuyor, iki modelde de | **kırmızı** |
| 7 | Boş seçilen kare hiç LoRA yüklemiyor ve prompt'a dokunmuyor, iki modelde de | **kırmızı** |
| 8 | Slime seçilen kare yalnız Slime'ı yüklüyor, tetiğini prompt'un başına koyuyor | yeşil *(bekçi)* |
| 9 | Eski `recipe:*`, modelsiz ve çıplak dosya adlı kareler bugünkü gibi üretiliyor | yeşil *(bekçi)* |
| 10 | Katalogda olmayan bir LoRA'lı kuyruk isteği `lora` alanıyla reddediliyor, plan boş kalıyor | **kırmızı** |
| 11 | Boş, `usnr`, `slime`, `none` kuyruğa giriyor | yeşil *(bekçi)* |
| 12 | Ayar dosyası LoRA'yı yazıp okuyor; eskisi ve yanlış tiptekisi boş okunuyor | **kırmızı** |
| 13 | Ayarları kaydeden istek LoRA'yı taşıyor | **kırmızı** |
| 14 | Panel projenin kayıtlı LoRA'sıyla açılıyor | **kırmızı** |
| 15 | Kayıt yoksa kutu ilk satırla doluyor, dokunulmadan gönderilen kare USNR ile gidiyor | **kırmızı** |
| 16 | Boş seçimi korunuyor ve `none` olarak gidiyor | yeşil *(bekçi)* |
| 17 | "Kuyruğa ekle" ayarları LoRA ile birlikte kaydediyor | **kırmızı** |
| 18 | Liste gelmeden LoRA kutusu `yükleniyor…` diyor ve kapalı | **kırmızı** |
| 19 | Liste okunamayınca kutu `liste okunamadı` diyor, düğme açık, istek kayıtlı seçimle gidiyor | **kırmızı** |
| 20 | Listede artık olmayan kayıtlı bir LoRA kendi değeriyle seçili kalıyor | **kırmızı** |
| 21 | `useModels` okunamayan bir listeyi boş bir LoRA listesiyle bildiriyor | **kırmızı** |
| 22 | Kare detayı LoRA'yı adıyla yazıyor: USNR, Slime, Boş | yeşil *(bekçi)* |
| 23 | LoRA söylemeyen bir kare detayda LoRA satırı çizmiyor | **kırmızı** |

## Bu turda değişen

Yalnız testler:

- **Kırmızıyı taşıyan testler:** `test_photo_usecases.py`, `test_comfy_photo_generator.py`,
  `test_photo_routes.py`, `test_settings_store.py`, `test_projects_routes.py`,
  `test_project_usecases.py`, `GeneratePanel.test.jsx`, `useModels.test.jsx`,
  `PhotoDetail.test.jsx`, `ProjectScreen.test.jsx`.
- **Yalnız adı ve yorumu değişenler:** `Standart`'ı anan testler. `test_plan_store.py`'deki ikisi,
  `test_photo_usecases.py`'deki biri ve `test_photo_routes.py`'deki biri artık *söylenmemiş* diyor;
  davranışları aynı.
- **Ayar dosyasının şeklini birebir çivileyen testler** *(`test_settings_store.py`,
  `test_projects_routes.py`, `test_project_usecases.py`)*: beklenen sözlüklerine `lora` giriyor.
- **`test_notebook_installs_the_producer_groups.py`:** modelin standart LoRA'larını dolaşan döngüsü
  gidiyor, çünkü modeller artık LoRA taşımıyor. USNR katalogdaki LoRA'lar arasına geçtiği için aynı
  soruyu LoRA döngüsü soruyor.
