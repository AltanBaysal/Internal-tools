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
`CIVITAI_MODELS`'ına girdi (sürümler ve dosya adları aynı), denemenin tabloları, F, G, H, 1 ve 3
kareleri, ne karşılaştırılacağı ve kullanıcının ne getireceği "Nova preset" hücresine; Queen Editor'ün
grafiğinden workflow kuran 5. bölüm ve onun karşılaştırması gitti. Workflow'u kullanıcı sürükler, adayı
Power Lora Loader'a kendisi ekler. Bu grafikte `CLIPTextEncodeBREAK` yok, bu yüzden karelerde `BREAK`
yerine virgül var.

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

**Tetik:** sayfanın eğitim sözcükleri, karenin kendisi söylediği sayılar (`1boy`, `1futa`, `2girls`) ve
beden ya da eylem etiketleri çıkarılarak; Queen Editor'ün `catalog.with_trigger`'ı gibi prompt'un önüne
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
- **Üç futa adayı da iki kare çizer** *(ana ajanın kararı, 27 Ekim, review'dan sonra)*: tek kişilik
  **Kare G** — D'nin ölçüsü, ve E ile F'nin tetiği bir partner adlandırırken partnersiz bir karede ne
  yaptıkları — ve partnerli **Kare H** — futa ve senaryonun erkek karakteri, E ile F'nin eğitildiği şey.
  H'deki partner erkek: senaryonun ikinci karakteri o, ve F'nin eşleşmesi; E'nin bir erkeği ne yaptığı
  da bir sonuç. Futa workflow'ları G'yle açılır, H'yi kullanıcı yapıştırır.
- **Karşılaştırma, iki checkpoint'te:** femboy'larda F, Kare 1, Kare 3 (18 resim); futa'larda G, H,
  Kare 1, Kare 3 (24 resim); LoRA'sız F, G, H (6 resim) — **48 resim**.
- **`男の娘、ふたなり` (otoko no ko, futanari, ILL v2.0) futa adayı olarak da seçilmedi:** güç önerisi
  olan bir beden kavramı, ama tek tetikle iki ayrı şeyi — femboy'u ve futa'yı — öğretiyor; iki gruptan
  birinin karesini ötekine çekebilir.
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
   POSITIVE'e tetik + grubunun karesi, `40` seed'e sabit `20261027` (adaylar aynı gürültüden).

Bir adayın satırı grubunu taşır (`femboy` / `futa`), ve grup workflow'un hangi kareyle açılacağını
seçer: **Kare F** — örnek senaryonun kapı önü karesi, kadın karakterin yerine bir femboy — ya da **Kare
G** — aynı kare, aynı kadın futanari olarak. **Kare H** — aynı futa ve senaryonun erkek karakteri,
yatakta — yalnız `instructions.md`'de. Üçü de QueenAgent'ın `build_prompts`'unun biçiminde; H'de
senaryonun karakter satırındaki `solo` yok, iki kişilik bir karede yanlış olduğu için. Workflow'un adı
adayın kaydedilen dosya adı.

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

## Ne zaman bitti (bu adım)

- `femboy-futa-lora/` klasöründe defter, `instructions.md` ve `indirilecekler.md` var; defter Krea ve
  Qwen denemelerinin biçiminde ve NOTEBOOK-STANDARD'a uygun.
- 5. bölümün kodu bu makinede iki gerçek grafikle ve defterin kendi aday listesiyle çalıştırıldı:
  karşılaştırma geçti, altı workflow yazıldı, `36`'nın türü değişti ve altısında `27`, `3`, `40`, `45`
  beklenen değerlerde — femboy'larda Kare F, futa'larda Kare G. GitHub'ın API adresi `Accept:
  application/vnd.github.raw` ile ham dosyayı veriyor; özetin hata yolu bozuk bir header'la denendi.
- Kullanıcı defteri Colab'da koşup her gruptaki üç adayı karşılaştırabiliyor.
- *(28 Ekim'den beri, yukarıdaki ilk iki maddenin — `femboy-futa-lora/` klasörü ve 5. bölümün workflow'ları —
  yerine)* Altı aday `nova-3dcg/manual.ipynb`'den iniyor, deneme
  onun "Nova preset" hücresinde yazılı, `workflow_manual.json` arayüz 1.46.15'le yerelde hatasız
  yükleniyor ve `femboy-futa-lora/` silindi.
