# Madde 214 · Slime girl — test turunun tasarımı

**Tarih:** 16 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

## Kullanıcıdan gereken ve ne geldiği

Yol haritası üç şey istiyordu: **kararın kendisi** *(LoRA mı, tarif mi, yalnız prompt mu)*, yol LoRA
ise **dosyanın verilmesi**, ve çıkan işi **kullanıcının görmesi**. İlk ikisi geldi.

Kullanıcı ComfyUI'da denedi ve kararını denemeye dayanarak verdi:

- Aday üç dosyaydı — `DaSiWa True Slime Girls`, `Translucent Penetration`, ve bugün grafikte kurulu
  duran `USNR STYLE`. Üçü de **Illustrious** tabanlı, yani bizim checkpoint'lerimizle aynı aileden.
- **Kazanan: `translucent_penetration_v5` @ 0.9, tek başına.** DaSiWa'nınki denendi ve elendi
  *("baya kötü patlıyor")*; **USNR de kapalı**.
- Taban model **`nova3DCGXL_ilV90`** — bugün zaten indirilebilen bir checkpoint. Yeni checkpoint yok.

Üçüncü şart — çıkan videoyu görmesi — bu turun değil, uygulama turunun sonunda.

## Yol haritasının bu maddedeki bir cümlesi yanlış çıktı

Madde 214 videoyu işaret ediyordu: *"LoRA'nın **WAN 2.2 I2V** tabanlı olması ve **High + Low çifti**
gelmesi"*. Kullanıcının getirdiği referans bir **fotoğraf** LoRA'sı. Doğru akış şu, ve video tarafına
hiç dokunmuyor:

> Fotoğraf grafiği slime kareyi üretir → video grafiği o kareyi oynatır.

Video I2V olduğu için görünüşü kareden miras alıyor. Uygulama turunda yol haritasının satırı da
düzeltilecek.

## Karar: liste tarif listesi olacak

Kullanıcının kendi cümlesi: *"ordaki model sadece modeli değil lora dizilimi de temsil edebilir"*, ve
*"notebooktan biz model değil tarif seçiyor gibi davranalım"*.

Yani **kutular tarif kutusu**, ve uygulamanın listesi seçilen tariflerdir:

| Defterde seçili | Uygulamanın listesi |
|---|---|
| Nova 3DCG | `Nova 3DCG XL` |
| Slime | `Slime` |
| Nova 3DCG + Slime | `Nova 3DCG XL`, `Slime` |

Yalnız Slime seçiliyken Nova **görünmez** — oysa `nova3DCGXL_ilV90` diskte durur, çünkü Slime'ın
checkpoint'i odur.

## Bugün ne var, ve neden yetmiyor

**Model listesi bir dosya listesi.** Uygulamada da sunucuda da yazılı bir liste yok, bilerek:

- [client.py:31](../../../queen-editor/backend/services/comfy/client.py) ComfyUI'a
  `/object_info/CheckpointLoaderSimple` diye soruyor; cevaptaki adlar listenin ta kendisi.
- [list_models.py](../../../queen-editor/backend/features/photo_generation/domain/usecases/list_models.py)
  onu olduğu gibi geçiriyor — *"the app keeps no list of its own"*.
- Seçilen ad kareye **metin** olarak yazılıyor
  ([plan_store.py:65](../../../queen-editor/backend/features/photo_generation/data/plan_store.py)) ve
  üretimde grafiğin `45` numaralı node'una geçiyor
  ([comfy_photo_generator.py:45](../../../queen-editor/backend/features/photo_generation/data/comfy_photo_generator.py)).
  **Boş metin = grafiğin kendi checkpoint'i.**
- **LoRA'ya kimse dokunmuyor:** `27` numaralı Power Lora Loader grafikte ne ile geliyorsa o — `lora_1`
  = USNR 0.8, açık *([workflow_api.json:215](../../../queen-editor/workflow_api.json))*.

Diskten okumak yetmiyor, çünkü yalnız Slime seçili kurulumda `nova3DCGXL` yine diskte olur ve sunucu
onu listeler. **Hangi tariflerin seçildiğini bilen tek taraf defterdir.** Defter uygulamaya zaten
bir şey söylüyor — `"QE_COMFY_ROOT": COMFY_ROOT` — seçilen tarif kimlikleri de aynı yoldan geçecek.

## Tarif

**Tarif tablosu uygulamada, adresler defterde.** Ad ve LoRA dizilimi uygulamanın *(grafiği yamayan
taraf)*, sürüm kimliği ve boyut defterin *(indiren taraf)*. İkisini bir test eşitler — tıpkı bugün
kutularla satırları eşitleyen
[test_every_photo_model_has_a_checkbox_of_its_own](../../../queen-editor/backend/tests/test_notebook_installs_the_producer_groups.py)
gibi.

| Tarif | Etiket | Checkpoint | LoRA | Tetik |
|---|---|---|---|---|
| `nova3dcg` | Nova 3DCG XL | `nova3DCGXL_ilV90.safetensors` | USNR 0.8 | — |
| `novaorange` | Nova Orange XL | `novaOrangeXL_rexV10.safetensors` | USNR 0.8 | — |
| `novaanime` | Nova Anime XL | `novaAnimeXL_ilV190.safetensors` | USNR 0.8 | — |
| **`slime`** | **Slime** | `nova3DCGXL_ilV90.safetensors` | **`translucent_penetration_v5` 0.9** | `translucent penetration` |

**LoRA'ların ikisi de her kurulumda iniyor** *(USNR 895 MB, translucent 167 MB)*. Tarifler yalnız
checkpoint'i ve `27`'ye yazılanı değiştiriyor; hangi LoRA'nın hangi kutuya bağlı olduğunu paneldeki
"kurulu mu" sayımına taşımak, onu tarif seçimine bağımlı ve kırılgan yapardı.

**Trigger'ı uygulama ekliyor.** Tarif kendi tetik kelimesini taşıyor ve prompt'un başına geçiyor.
Gerekçe: LoRA açık ama `translucent penetration` prompt'ta değilse çıkan şey normal bir fotoğraftır —
"Slime" seçip normal sonuç almak sessiz bir arıza olur.

**Değer biçimi geriye dönük.** Tarif değeri `recipe:<id>`; hiçbir dosya adıyla karışmaz. Çıplak
dosya adı ve boş metin bugünkü anlamlarını koruyor, yani daha önce planlanmış her kare aynen bugünkü
gibi render olur. Defter tarif listesi geçirmediyse *(depoyu defterisiz koşturan her yer)* liste
bugünkü davranışına düşer: sunucunun saydığı checkpoint'ler.

## Çivilenecek olgular

### Liste

| # | Ne diyor | Bugün |
|---|---|---|
| 1 | Defterin seçtiği tarifler listeye kendi etiketleriyle ve defterdeki sırayla geliyor | **kırmızı** |
| 2 | Seçilmeyen tarif listede yok — checkpoint'i diskte olsa bile | **kırmızı** |
| 3 | Tarif satırının değeri `recipe:<id>` | **kırmızı** |
| 4 | Defter hiçbir şey söylemediyse liste sunucunun checkpoint'leri — bugünkü davranış | yeşil, ve öyle kalmalı |
| 5 | Tanınmayan bir kimlik listeye girmiyor, ve tanınanları düşürmüyor | **kırmızı** |

### Üretim

| # | Ne diyor | Bugün |
|---|---|---|
| 6 | `recipe:slime` geldiğinde `45`'e tarifin **checkpoint'i** yazılıyor, değerin kendisi değil | **kırmızı** |
| 7 | `27`'de yalnız tarifin LoRA'ları açık kalıyor, kendi ağırlıklarıyla — Slime'da USNR kapanıyor | **kırmızı** |
| 8 | Tarifin tetik kelimesi prompt'un başına ekleniyor | **kırmızı** |
| 9 | Tetiksiz tarifte prompt olduğu gibi gidiyor, ve negatife hiç dokunulmuyor | **kırmızı** |
| 10 | Çıplak dosya adı `45`'i yazıp `27`'yi olduğu gibi bırakıyor | 45 yeşil, 27 **kırmızı** |
| 11 | Boş model hem `45`'i hem `27`'yi olduğu gibi bırakıyor | 45 yeşil, 27 **kırmızı** |
| 12 | Tanınmayan bir `recipe:` kimliği **durduruyor** — sessizce normale düşmüyor | **kırmızı** |
| 13 | Tarif seçilmişken grafikte `27` yoksa hata o node'u adıyla söylüyor | **kırmızı** |

Onikincisi sessiz arızaya karşı: tanınmayan bir tarif normale düşerse kullanıcı Slime seçip normal
fotoğraf alır ve sebebini hiçbir yerde göremez. Onüçüncüsü grafiğin yeniden export edilmesine karşı —
`45` için bugün var olan kontrolün aynısı, ama yalnız ihtiyaç duyulduğunda, çünkü `27`'yi her render
için şart koşmak tarif kullanmayan bir grafiği de kırardı.

### Kurulum

| # | Ne diyor | Bugün |
|---|---|---|
| 14 | Defterdeki tarif kutuları ile uygulamanın tarif tablosu birebir aynı kimlikleri taşıyor | **kırmızı** |
| 15 | Her tarif kendi anahtarının arkasında — seçilmeyen tarif bir bayta mal olmuyor | **kırmızı** |
| 16 | İki tarif aynı checkpoint'i istiyorsa dosya bir kez iniyor ve diskte bir kez sayılıyor | **kırmızı** |
| 17 | Defter seçilen tarif kimliklerini uygulamaya geçiriyor | **kırmızı** |
| 18 | Tariflerin adını verdiği her LoRA foto grubunun saydığı dosyalar arasında | **kırmızı** |
| 19 | Panelin saydığı her dosyayı defter indiriyor | 18 kırmızı olduğu için **kırmızı** |

Onaltıncısı Nova + Slime birlikte seçildiğinde 7 GiB'ın iki kez inmesine ve disk uyarısının iki kez
saymasına karşı. Ondokuzuncusu zaten var
*([test_notebook_installs_the_producer_groups.py:70](../../../queen-editor/backend/tests/test_notebook_installs_the_producer_groups.py))* —
18 yeşile dönünce kendiliğinden defteri de zorlar.

### Ön yüz

| # | Ne diyor | Bugün |
|---|---|---|
| 20 | Kutu etiketi gösteriyor, seçilince değeri gönderiyor | **kırmızı** |
| 21 | Hiçbir şey kayıtlı değilken ilk satır seçili geliyor | yeşil, ve öyle kalmalı |
| 22 | Kayıtlı seçim listede yoksa seçili kalıyor ve *"artık kurulu değil"* çıkıyor | **kırmızı** *(bugün ad karşılaştırıyor, satır değil)* |
| 23 | Kare detayında tarif, **seçildiği adla** yazıyor — `recipe:slime` değil `Slime` | **kırmızı** |
| 24 | Satır listesi gelmediyse kare neyi sakladıysa o yazıyor — satır boş kalmıyor | yeşil, ve öyle kalmalı |

Yirmiüçüncüsü bir adresin ekrana düşmesine karşı: kullanıcı listeden *"Slime"* seçiyor, ve kare
detayı ona `recipe:slime` diyemez. Etiketin tek kaynağı sunucunun verdiği satır listesi, o yüzden
detay sayfası da onu okuyor — ve okuyamadığında sustuğu değil, kaydı gösterdiği için 24 var.

## Bu turda değişen

Yalnız testler:

- `queen-editor/backend/tests/test_photo_usecases.py` — 1–5
- `queen-editor/backend/tests/test_photo_routes.py` — uç noktanın yeni biçimi *(olgu 4'ün rota tarafı)*
- `queen-editor/backend/tests/test_comfy_photo_generator.py` — 6–13
- `queen-editor/backend/tests/test_notebook_installs_the_producer_groups.py` — 14–17
- `queen-editor/backend/tests/test_producers.py` — 18
- `queen-editor/frontend/src/features/photo_generation/GeneratePanel.test.jsx` — 20–22
- `queen-editor/frontend/src/features/photo_generation/PhotoDetail.test.jsx` — 23–24

Tarif modülü, üretici, rota, ön yüz, defter ve `dist` uygulama turunun işi.
