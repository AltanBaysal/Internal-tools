# Madde 501 · Femboy ve futa LoRA'ları, deneme — tasarım

**Tarih:** 27 Ekim 2026 · **Madde:** [v11 yol haritası](../roadmaps/2026-10-24-queen-editor-v11-roadmap.md#v11-4),
501 · v11-4 · **Dal:** `feat/queen-editor-v11` · **Kurallar:**
[NOTEBOOK-STANDARD](../../collab-toolbox/NOTEBOOK-STANDARD.md) · **Defter:**
[collab-toolbox/photo_generator/nova-3dcg/manual.ipynb](../../collab-toolbox/photo_generator/nova-3dcg/manual.ipynb)
*(28 Ekim'den beri; aşağıda, "Yapılırken değişti")* · **Plan:** [2026-10-27-queen-editor-m501-femboy-futa-lora-deneme-plan.md](../plans/2026-10-27-queen-editor-m501-femboy-futa-lora-deneme-plan.md)

## Ne, neden

Kullanıcı, 27 Ekim — *"Seninle birlikte, deneme notebook'unda. femboysXL ve Civitai'den 1–2 aday daha
ComfyUI'de denenir, hangisinin kalacağına sen karar verirsin."*; *"bunu yapalım sonra karar veridğimizi
queen editore koyarız"*. Sonra futa da girdi, aynı denemeye: *"futa içinde 3 model indirir msiin"*;
*"bu taskı femboyla berabe yap zaten nerdeyse aynı şeyler 3 model yer,ne 6 tane denerim"*.

Bu adım yalnız denemeyi hazırlar: bir Colab defteri, tek oturumda altı aday — üç femboy, üç futa —
kullanıcının ComfyUI'de koşacağı. Queen Editor'ün koduna dokunulmaz. Kullanıcı her gruptan birini
seçince madde ikinci adımıyla sürer (aşağıda, "Seçimden sonra").

## Yapılırken değişti *(28 Ekim)*

**Deneme Nova'nın kendi defterine taşındı, ayrı deneme defteri silindi.** Kullanıcı Colab'da altı
workflow'u bozuk gördü; `photo_generator/nova-3dcg/workflow_manual.json`'u aynı ComfyUI'ye elle
sürükleyince de *"Loading aborted due to error reloading workflow data TypeError: t.findInputSlot is not
a function"* çıktı, kaynağı `/extensions/ComfyUI-Impact-Pack/impact-pack.js`. Kararı *(kullanıcı, 28 Ekim
— "photo generator novaya gerekli loraları indirttir ordan direkt kullanıp test edeyim foto
experimentide silelim")*: altı aday [nova-3dcg/manual.ipynb](../../collab-toolbox/photo_generator/nova-3dcg/manual.ipynb)'nin
`CIVITAI_MODELS`'ına girdi (sürümler ve dosya adları aynı), aday tablosu — LoRA, güç, tetik — her
üretimin adımları ve kullanıcının ne getireceği "Nova preset" hücresine; Queen Editor'ün grafiğinden
workflow kuran 5. bölüm ve onun karşılaştırması gitti. Workflow'u kullanıcı sürükler, adayı Power Lora
Loader'a kendisi ekler.

**Kareler çıktı** *(kullanıcı, 28 Ekim — "ben senden kare yamanı istemedim yazdığı nyerdende temizle
promtpları")*: prompt'ları kullanıcı kendisi yazar, defterden yalnız tetikleri ister. F, G, H, 1 ve 3
kareleri, onlara dayanan karşılaştırma ve 48 resim sayısı defterden ve bu belgeden silindi; POSITIVE'e
adayın tetiği + `, ` + kullanıcının kendi prompt'u yazılır.

**Hatanın sebebi, koddan:** Impact-Pack'in `js/impact-pack.js`'i (Main, son commit 2026-04-20), satır 639:
ImpactSwitch'in `onConnectionsChange`'i grafik yüklenirken `node.connect(link_info.origin_slot, node.id,
'input1')` çağırıyor — hedef olarak node'un kendisini değil numarasını veriyor. Arayüzün `LGraphNode.connect`'i
bir numarayı yalnız `typeof target_node === 'number'` ise node'a çeviriyor. ComfyUI_frontend'in
`b4ae6344` commit'i ("Brand local node IDs", 1.47.6'dan beri) node numaralarını yazıya çevirdi
(`toNodeId = String`); yazı olan numara çevrilmeden geçiyor ve `t.findInputSlot` bir yazının üstünde
çağrılıyor. ComfyUI 1.47.10'u 2026-07-23'te istemeye başladı, bugün 1.57.6'yı istiyor; Impact-Pack'te
bunu düzelten bir commit yok. **Sabitleme:** `manual.ipynb`'nin 3. bölümü ComfyUI'nin gereksinimlerinden
sonra `comfyui-frontend-package==1.46.15`'i kurar — o değişiklikten önceki son sürüm. ComfyUI yalnız
uyarır. Grafik zaten 1.45.20'yle kaydedilmiş (`extra.frontendVersion`).

**Yerelde denendi** (CPU, `tmp/` altında, sonra silindi): ComfyUI `79cf64c` ve 3. bölümün sekiz paketi;
`workflow_manual.json` arayüze sürüklemenin yaptığı gibi (`app.handleFile`) yüklendi. 1.57.6'da
kullanıcının gördüğü pencere birebir çıktı, yığın `impact-pack.js:639` → `ComfyNode.connect`, node
numaraları `string`. 1.46.15'te hata yok, 75 node'un hepsi kayıtlı bir türde (eksik node yok), 140 bağ,
`graphToPrompt` 32 node veriyor; arayüzün işaretlediği tek şey inmemiş üç model (`fabricatedXL_v70`, yüz
dedektörü, SAM) — Colab'da yüz dedektörü ve SAM iner, checkpoint elle seçilir.
Üretim yerelde koşulmadı.

## Adaylar

Civitai API'si, 27 Ekim; LoRA, indirme sayısına göre, Illustrious sürümü olanlar. Seçim ölçüsü: Nova ve
DaSiWa'nın tabanı Illustrious'a uyum, yenilik, indirme sayısı; tek bir karakter ya da çizim tarzı değil,
genel bir kavram. İndirme sayısı modelin bütün sürümlerinin toplamı.

**Tetik:** sayfanın eğitim sözcükleri, sayılar (`1boy`, `1futa`, `2girls`) ve beden ya da eylem
etiketleri çıkarılarak — onları prompt'un kendisi söyler; Queen Editor'ün `catalog.with_trigger`'ı gibi prompt'un önüne
konur. **Güç:** sayfanın önerdiği; önermeyende 1,0, yükleyicinin kendi değeri. Talimat 0,7'yi de denetir.

### Femboy

| | LoRA | Sürüm | Taban | İndirme | Güç | Tetik |
|---|---|---|---|---|---|---|
| A | [femboysXL](https://civitai.com/models/289006) | v1.0 · 324974 · 2024-02 | SDXL 1.0 (Animagine XL 3.0'da eğitilmiş) | 13.573 | 1,0 | `otoko no ko, crossdressing, trap, androgynous` |
| B | [Femboy illustrious](https://civitai.com/models/1738161) | v1.3 · 2693790 · 2026-03 | Illustrious | 6.137 | 1,0 | `Fboy` |
| C | [Femboy, Sissy, Feminine Male](https://civitai.com/models/1922853) | IL · 2176350 · 2025-09 | Illustrious | 2.552 | 1,0 | `1femboy, lean male chest, feminine male` |

- **A** kullanıcının adını verdiği aday; en çok indirilen, ama Illustrious'ta değil Animagine'de
  eğitilmiş (dosyanın header'ı, `ss_sd_model_name`). SDXL olduğu için yüklenir; ne kadar tuttuğu
  denemenin sorusu.
- **B** Illustrious'ta en çok indirilen femboy LoRA'sı ve en yenisi. v1.3'ün sayfası tetik yazmıyor;
  önceki sürümleri `Fboy` diyor. **Tahmin:** defter dosyanın kendi eğitim etiketlerini basar, ve
  kullanıcı orada başka bir sözcük görürse tetiği workflow'da düzeltir.
- **C** Illustrious'ta ikinci genel femboy kavramı; tetiği sayfanın tek satırı.

### Futa

| | LoRA | Sürüm | Taban | İndirme | Güç | Tetik |
|---|---|---|---|---|---|---|
| D | [Flaccid Futa](https://civitai.com/models/2063309) | v3.0 IL · 2698395 · 2026-02 | Illustrious | 3.358 | 0,6 (sayfa: 0,4 – 0,8) | `flaccid futa` |
| E | [Futa on Female](https://civitai.com/models/1107758) | Illustrious v2 · 1457484 · 2025-02 | Illustrious | 9.850 | 1,0 | `futa with female` |
| F | [Futa on Male / Futadom 2](https://civitai.com/models/891832) | Illustrious v2 · 2066157 · 2025-08 | Illustrious | 12.743 | 1,0 | `futa on male, futa with male, futanari` |

- **D** futa'nın bedeni, üçünün en yenisi; v3.0 stilize checkpoint'ler için nötr bir tarza yeniden
  eğitilmiş. Güç önerisi olan tek sayfa; aralığın ortasından açılır.
- **E** ve **F** Illustrious'ta en çok indirilen iki futa kavramı, biri bir kadınla biri bir erkekle.
  İkisi de **eylem** LoRA'sı: eğitim satırları partnerli sahneler. Illustrious'ta genel bir futa beden
  kavramı az; D'den sonra en genel ve en çok indirilenler bunlar.
- **`男の娘、ふたなり` (otoko no ko, futanari, ILL v2.0) futa adayı olarak da seçilmedi:** güç önerisi
  olan bir beden kavramı, ama tek tetikle iki ayrı şeyi — femboy'u ve futa'yı — öğretiyor; iki gruptan
  birinin prompt'unu ötekine çekebilir.
- Seçilmeyenlerin tamamı ve nedenleri `instructions.md`'de.

## Deneme nasıl kuruluyor

**Gördüğü, Queen Editor'ün çizeceği olsun diye** workflow'lar Queen Editor'ün kendi fotoğraf
grafiğinden kurulur. O grafik API biçiminde (`queen-editor/assets/workflow_api.json`), ComfyUI'nin
Workflows paneli ise arayüz biçimini açar. Queen Editor'ün grafiği nova-3dcg denemesinin arayüz
grafiğinden (`collab-toolbox/photo_generator/nova-3dcg/workflow_manual.json`) export edilmiş; node
numaraları aynı. Defter ikisini de reponun `main`'inden okur ve:

1. **karşılaştırır**: API'deki her node arayüzde aynı numarayla ve açık mı; her bağı aynı node'dan mı
   (kapalı bir node'un içinden geçen bağ, export'un yaptığı gibi arkasındaki node'a kadar izlenir); elle
   yazılmış her değeri arayüzdeki node'un kutularında var mı. Tutmazsa durur ve farkları basar.
   27 Ekim'de karşılaştırma iki grafik arasında yalnız `36`'nın türünü buldu.
2. node türü farklıysa Queen Editor'ünkini alır: `36` `CLIPTextEncode` → `CLIPTextEncodeBREAK`;
3. her aday için Queen Editor'ün yazdıklarını yazar: `45` checkpoint (Nova; DaSiWa elle), `27` Power
   Lora Loader'a **yalnız aday** (Queen Editor'de bir LoRA seçilince USNR kapanır, `_set_loras`), `3`
   POSITIVE'e tetik ve bir prompt, `40` seed'e sabit `20261027` (adaylar aynı gürültüden).

Workflow'un adı adayın kaydedilen dosya adı.

**Negatif Queen Editor'deki gibi değil.** Queen Editor grafiğin negatifini hiç kullanmaz: panelin negatif
kutusuna yazılanı yazar (`routes.py`, `start_batch`; proje başına saklanır, boşsa boş —
`comfy_photo_generator._graph`). Örnek senaryonun negatifi yok; deneme grafiğin kendi negatifini tutar
ve talimat bunu söyler.

**Grafikler GitHub'dan:** `GITHUB_TOKEN` isteğe bağlı, CONFIG'de Krea'nın `HF_TOKEN`'ı gibi okunur.
Varsa iki dosya GitHub'ın API'sinden iner (`/repos/…/contents/<yol>?ref=main`, `Authorization` ve
`Accept: application/vnd.github.raw`) — repo kapansa da; yoksa açık `raw.githubusercontent.com`
adresinden. Token yalnız bir başlıkta gider; hiçbir mesaj isteğin başlıklarını basmaz.

**Karşılaştırmanın sınırı:** bir değer node'un `widgets_values`'unun herhangi bir yerinde aranır,
kutunun kendi sırasında değil (arayüz dosyası kutuları adlandırmıyor), ve Python'da `True`/`False`
`1`/`0`'a eşit. İkisi de karşılaştırmayı gevşetir: bir farkı kaçırabilir, olmayan bir fark uyduramaz.

Bu iki dosya arasındaki eşleşmeyi yazan kod yok, yalnız bu defter; Queen Editor ve nova-3dcg
değişmiyor.

**Kurulum** Queen Editor'ün dersleriyle: rgthree `main` dalından (madde 470), Impact-Pack'in `sam2`'si
kurulmaz (madde 314). Paketler arayüz grafiğinin istediği sekiz; ComfyUI-Manager ve DaSiWa-Nodes yok.
ComfyUI ayağa kalkınca `/object_info` bir kez sorulur ve Queen Editor'ün grafiğindeki her node türü
orada aranır.

**İndirme** Krea denemesinin yolu: önce boş disk, sonra her Civitai dosyasının ilk 1 KB'ı çerezle,
sonra tek bağlantılı `curl`'le `.part`'a, header'dan doğrulama, yerine taşıma. Ayna yok (madde 327).
Yüz dedektörü ve SAM açık adreslerinden, taban boyla.

## Maliyet

Hepsi defterin bir koşusunda, kullanıcının makinesinde; Queen Editor'ün çalışma anına bir şey eklenmez.

- Ağ: 10 model dosyası (~15,9 GB: checkpoint'ler 13,9, altı aday 1,6, yüz düzeltmesi 0,4) ve en fazla 8
  Civitai probe'u; GitHub'dan 2 dosya (~110 KB); ComfyUI'ye 1 `/object_info`. Yeniden çalıştırmada
  yerindeki dosyalar inmez, yerindeki workflow'lar yazılmaz.
- Disk: her LoRA'nın header'ı özet için bir kez daha okunur (altı dosya, birkaç KB); okunamayan bir
  header'ın hatası ham basılır ve özet sürer — dosyalar o noktada inmiş ve doğrulanmış. Her workflow önce
  `.part`'a yazılır, sonra yerine taşınır; kullanıcının aynı adla kaydettiği bir workflow ezilmez.

## Ne kırılabilir

- **Repo kapanırsa** token'sız açık adres 404 döner ve 5. bölüm GitHub'ın cevabıyla durur;
  `GITHUB_TOKEN` Secrets'a eklenince API'den iner.
- **Grafikler ayrılırsa** (biri değişip öteki değişmezse) 5. bölüm farkları basıp durur; o zaman
  workflow'lar Queen Editor'ün çizeceğini göstermezdi.
- B'nin tetiği tahmin (yukarıda). E ve F'nin tetikleri partner adlandırıyor (yukarıda).

## Seçimden sonra

- Her gruptan seçilen LoRA, Queen Editor'de Nova ve DaSiWa'nın **ortak LoRA kutusuna** girer:
  `catalog.LORAS`'a birer satır — dosya, güç, tetik — ve notebook'ta `CIVITAI_PHOTO`'ya sürümü. Bu,
  maddenin ikinci adımı; ayrı bir spec ve planla, kullanıcının seçimiyle yazılır.
- Aynı adımda, seçilenler Queen Editor'e girerken, altı adayın satırı `nova-3dcg/manual.ipynb`'nin
  `CIVITAI_MODELS`'ından çıkar, deneme bölümü de "Nova preset" hücresinden: defter her oturumda
  ~1,5 GiB'ı boşuna indirmez.
- Seçilen bir LoRA bir tetik cümlesi gibi **özel bir prompt** istiyorsa — tetik dışında, karakter
  tarifinde ya da karenin kimi adlandırdığında bir şey — ana ajan QueenAgent v12 yol haritasına
  `UNALIGNED` yeni bir madde açar *(kullanıcı, 27 Ekim — "şöyle özel bir prompt gerkeilyors mesela bir
  tetik çümlesi bu roadmpai koşarken queen agent yeni bir görev aç unaligned gerkiyorsa tabi")*.
  Tetiğin kendisini Queen Editor ekler (`with_trigger`); o QueenAgent'a bir şey gerektirmez.
- Denemenin sonucu yol haritasının maddesine yazılır (kabul koşulu: *"Femboy ve futa adaylarının deneme
  sonucu yazılı"*).

## Seçim *(28 Ekim)*

Kullanıcı, 28 Ekim — *"tamam test ettim / bunlar dasiwa için olacak / 2 senecek olucak / 1 futa sadece
futa flaccid olacak 0.50 ile / 2. seçenekte futa on male olacak buda 0.50 futa flaccid 1.00 futa on male
olucak 2 lora / novada ikisde iyi çalımıyor çünkü / tetik kelilerini queen editor otomaik eklicek"*.

- **Yalnız DaSiWa.** Yukarıdaki "Seçimden sonra"nın *ortak kutu*su yerine: iki LoRA da Nova'da iyi
  çizmiyor, o yüzden Nova'nın kutusu bugünkü gibi kalır — USNR, Slime, Boş.
- **DaSiWa'nın LoRA kutusunda iki yeni seçenek:**

  | Seçenek | Yükleyicide (`27`) | Tetik, prompt'un önünde |
  |---|---|---|
  | **Futa** | `futa_flaccid_v3` 0,50 | `flaccid futa` |
  | **Futa on male** | `futa_flaccid_v3` 0,50 + `futa_on_male_il_v2` 1,00 | `flaccid futa, futa on male, futa with male, futanari` |

- **Femboy seçilmedi;** Queen Editor'e femboy girmez.
- **QueenAgent'a madde açılmadı:** kullanıcı yalnız tetikleri istedi ve onları Queen Editor ekler; özel
  bir prompt istenmedi.

### Nasıl kuruldu

- **DaSiWa'nın kendi kutusu** (`catalog.DASIWA_LORAS`). Kutu bugüne kadar Nova ve DaSiWa'nın ortak
  listesiydi (`catalog.LORAS`); yalnız DaSiWa'ya iki seçenek eklemenin yolu 499'un Krea ve Qwen için
  açtığı yol: modelin satırında kendi kutusu (`"loras"`). Kutu ortak listenin satırları — her biri tek
  dosya olarak, ortak satırdan kurulur, iki kez yazılmaz — ve iki futa seçeneği. Satır biçimi Krea'nınki:
  üst üste konan dosyalar ve bir tetik; "Futa on male", Krea'nın "SNOFS + Slime"ı gibi iki dosya. İki
  tetik, dosyalarla aynı sırada, `, ` ile tek tetik olarak yazılır; `with_trigger` onu bugünkü gibi
  prompt'un önüne koyar.
- **Panel değişmedi:** modelin satırında kutu varsa panel o kutuyu gösterir, hiçbir modeli adıyla
  bilmeden. DaSiWa negatif alır, satırı negatif hakkında bir şey söylemez; negatif kutusu kalır.
- **Hangi kutu kuralı tek yerde** *(review'dan sonra)*: `catalog.box_row(model, lora)` — modelin
  satırı kutu taşıyorsa o kutudaki satır, taşımıyorsa ortak kutunun satırı tek dosya olarak; kutu
  tutmuyorsa None. `start_batch`'in kontrolü, `drawn_with` ve `own_pick` onu kullanır.
  `catalog.pick(model, lora)` bir karenin çizildiği seçim: `drawn_with`'ten geçer, ortak kutuda boş
  seçim varsayılan, Boş dosyasız bir seçim, bilinmeyen None.
- **Kuyruğa ekle** DaSiWa'nın seçimini DaSiWa'nın kutusunda arar, Nova'nınkini ortak kutuda: Nova'da
  Futa reddedilir. DaSiWa'da boş seçim kutunun ilk satırı, USNR, olarak kaydedilir (`drawn_with`) —
  çizdiği bugünküyle aynı.
- **Grafik** (`comfy_photo_generator._pick`): `catalog.pick`'in seçimini alır, None'da çizimi durdurur,
  Power Lora Loader'ı `lora_1`'den başlayarak seçimin dosyalarıyla doldurur — "Futa on male"de
  `lora_1` ve `lora_2`.
- **Defter** (`queeneditor.ipynb`): `CIVITAI_DASIWA` iki satır (2698395, 2066157; denemenin dosya
  adlarıyla), `CIVITAI_PHOTO`'ya `+ (CIVITAI_DASIWA if PHOTO_DASIWA else [])` ile girer — yalnız DaSiWa
  işaretliyse iner. `civitai_fetch` önce HF aynası, yoksa Civitai, sonra aynaya yükler; ikisi
  `MIRRORLESS`'te değil. Disk hesabına `+ (1 if PHOTO_DASIWA else 0)` (228.460.108 + 228.482.300 B,
  ~0,43 GiB, Krea ve Qwen'inkiler gibi yukarı yuvarlanmış).
- **Üretici paneli** (`model_groups`) iki dosyayı saymaz: bir checkpoint gibi bir kutuya bağlılar, ve
  inmezlerse defterin indirme hücresi durur.
- **Nova'nın defteri** (`nova-3dcg/manual.ipynb`): altı adayın `CIVITAI_MODELS` satırları, "Nova preset"
  hücresindeki "Femboy ve futa denemesi" bölümü ve son hücrenin iki ipucu satırı çıktı; başlıklar
  denemeden önceki ~15 GiB'a döndü. Arayüzün 1.46.15 sabitlemesi, rgthree'nin `main` dalı ve http2
  tüneli kalır.

### Maliyet

Çalışma anına istek eklenmez. Model listesi aynı tek cevapta DaSiWa'nın satırına beş satırlık kutusunu
koyar; bir kare yine bir grafik ve bir ComfyUI işi. Defter DaSiWa işaretliyse iki dosya daha indirir
(~0,43 GiB): ilk koşuda Civitai'den, çerezle (ikisi girişli), sonra aynadan.

### Ne kırılabilir

- **DaSiWa'nın seçimi artık kendi kutusunda tutulur.** Bugüne kadar Nova'da seçilen Slime DaSiWa'ya
  geçince de Slime görünüyordu; şimdi her kutu kendi seçimini tutar (499'un kuralı) ve DaSiWa kendi
  seçimi yapılana kadar USNR'de açılır. Slime'la gönderilmiş eski bir DaSiWa projesi Slime'da açılır.
- **DaSiWa'nın bilinmeyen bir LoRA'sı** çizimi durdurmaz, kutunun ilk satırıyla çizilir — Krea ve Qwen'in
  499'dan beri kuralı; bir testle sabit. Kuyruğa ekle bilinmeyeni zaten reddeder; yalnız eski bir
  satırda olabilir. 238'e aykırı olduğu için BACKLOG'da (*"Kendi kutusu olan modelde bilinmeyen LoRA
  çizimi durdurmuyor"*).
- İlk koşuda iki dosya aynada yoksa `CIVITAI_COOKIE` gerekir.

### Ne zaman bitti (ikinci adım)

- DaSiWa'nın LoRA kutusunda Futa ve Futa on male var, Nova'nınkinde yok.
- Futa ile bir kare `futa_flaccid_v3` 0,50'yle ve `flaccid futa, ` ile başlayan prompt'la; Futa on male
  ile iki LoRA'yla ve iki tetikle çiziliyor.
- `PHOTO_DASIWA` işaretliyse iki dosya iniyor, değilse inmiyor.
- Nova'nın defterinde aday kalmadı.
- Gerçek kareler ve indirme kullanıcının Colab denemesinde.

## Ne zaman bitti (deneme adımı)

- `femboy-futa-lora/` klasöründe defter, `instructions.md` ve `indirilecekler.md` var; defter Krea ve
  Qwen denemelerinin biçiminde ve NOTEBOOK-STANDARD'a uygun.
- 5. bölümün kodu bu makinede iki gerçek grafikle ve defterin kendi aday listesiyle çalıştırıldı:
  karşılaştırma geçti, altı workflow yazıldı, `36`'nın türü değişti ve altısında `27`, `3`, `40`, `45`
  beklenen değerlerde. GitHub'ın API adresi `Accept:
  application/vnd.github.raw` ile ham dosyayı veriyor; özetin hata yolu bozuk bir header'la denendi.
- Kullanıcı defteri Colab'da koşup her gruptaki üç adayı karşılaştırabiliyor.
- *(28 Ekim'den beri, yukarıdaki ilk iki maddenin — `femboy-futa-lora/` klasörü ve 5. bölümün workflow'ları —
  yerine)* Altı aday `nova-3dcg/manual.ipynb`'den iniyor, adaylar ve tetikleri onun "Nova preset"
  hücresinde yazılı — kare yok, prompt'u kullanıcı yazar —, `workflow_manual.json` arayüz 1.46.15'le yerelde hatasız
  yükleniyor ve `femboy-futa-lora/` silindi.
