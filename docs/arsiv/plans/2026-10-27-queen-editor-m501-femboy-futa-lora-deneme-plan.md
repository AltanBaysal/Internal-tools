# Madde 501 · Femboy ve futa LoRA'ları — Colab deneme kurulumu — plan

**Madde:** [v11 yol haritası](../roadmaps/2026-10-24-queen-editor-v11-roadmap.md#v11-4), 501 · v11-4 ·
**Dal:** `feat/queen-editor-v11` · **Spec:**
[2026-10-27-queen-editor-m501-femboy-futa-lora-deneme-design.md](../specs/2026-10-27-queen-editor-m501-femboy-futa-lora-deneme-design.md)
· **Önce:** 484'ün ve 485'in deneme defterleri
([qwen-image-21/](../../../collab-toolbox/photo_experiments/qwen-image-21/),
[krea-2/](../../../collab-toolbox/photo_experiments/krea-2/)) ve nova-3dcg'nin arayüz grafiği
([photo_generator/nova-3dcg/](../../../collab-toolbox/photo_generator/nova-3dcg/)).

**Kullanıcının istediği (27 Ekim):** femboysXL ve Civitai'den 1–2 femboy LoRA'sı daha, sonra 3 futa
LoRA'sı; tek defter, tek Colab oturumu, ComfyUI'de elle *("bu taskı femboyla berabe yap zaten nerdeyse
aynı şeyler 3 model yer,ne 6 tane denerim")*. Her gruptan seçilen LoRA sonra Queen Editor'de Nova ve
DaSiWa'nın LoRA kutusuna girer; bu plan yalnız denemeyi kurar.

**Ana ajanın brifi:** gördüğü Queen Editor'ün çizeceği olsun — Queen Editor'ün fotoğraf grafiği,
yükleyicide yalnız aday, USNR kapalı, tetik prompt'un önünde; iki checkpoint Queen Editor'ün indirdiği;
`CIVITAI_COOKIE` öteki denemelerdeki gibi.

İşaretler: **✅** kaynaktan ya da dosyanın kendisinden doğrulandı · **≈** doğrulanmadı.

---

## 0. Kararlar

- **Workflow'lar arayüz biçiminde, Queen Editor'ün grafiğinden kurulur.** Queen Editor'ün grafiği API
  biçiminde (`queen-editor/assets/workflow_api.json`); Workflows paneli arayüz biçimini açar. Grafik
  `collab-toolbox/photo_generator/nova-3dcg/workflow_manual.json`'dan export edilmiş, node numaraları
  aynı ✅ (32 API node'unun hepsi arayüzde, açık, aynı bağlarla ve aynı değerlerle; tek fark `36`'nın türü
  ve yazılan dört node — 27 Ekim'de karşılaştırıldı). Defter ikisini GitHub'dan okur ve dönüşümü kendi
  yapar; üretilmiş bir workflow repoya girmez.
- **Repo bugün açık** ✅ (`raw.githubusercontent.com` token'sız 200). Kapanırsa diye `GITHUB_TOKEN`
  isteğe bağlı: varsa GitHub'ın API'si *(review, 2.)*.
- **Folder:** `photo_experiments/femboy-futa-lora/`, defter `femboy-futa-lora.ipynb` (futa girince
  `femboy-lora/`'dan, henüz commit'lenmemişken adı değişti).
- **Güç:** sayfanın önerdiği, önermeyende 1,0. **Tetik:** sayfanın eğitim sözcükleri, sayılar ve beden ya
  da eylem etiketleri çıkarılarak.

---

## 1. İnecek dosyalar

Civitai'deki boyutlar API'nin `sizeKB × 1024`'ü ✅ (27 Ekim). Girişli dosyaların header'ı girişsiz
okunamadı; yalnız femboysXL'inki okundu ✅.

### 1.1 Queen Editor'ün checkpoint'leri — `checkpoints/`

| Sürüm | Dosya | Bayt |
|---|---|---|
| Nova 3DCG XL IL v9.0 · 2744564 | `nova3DCGXL_ilV90.safetensors` | 6.938.530.484 |
| DaSiWa EpitaphEcstasy · 3012006 | `DasiwaIllustriousAnime_epitaphecstasy.safetensors` | 6.938.115.222 |

Queen Editor'ün `PHOTO_CHECKPOINTS`'ındaki sürümler ve adlar ✅. Nova girişsiz, DaSiWa girişle ✅.

### 1.2 Adaylar — `loras/`

| Grup | Sürüm | Kaydedilen ad | Bayt | Güç | Tetik |
|---|---|---|---|---|---|
| femboy | femboysXL v1.0 · 324974 | `femboysXL_v1` | 489.722.956 | 1,0 | `otoko no ko, crossdressing, trap, androgynous` |
| femboy | Femboy illustrious v1.3 · 2693790 | `femboy_illustrious_v1_3` | 228.456.460 | 1,0 | `Fboy` ≈ |
| femboy | Femboy, Sissy, Feminine Male IL · 2176350 | `femboy_new_tos_il` | 228.476.020 | 1,0 | `1femboy, lean male chest, feminine male` |
| futa | Flaccid Futa v3.0 IL · 2698395 | `futa_flaccid_v3` | 228.460.108 | 0,6 | `flaccid futa` |
| futa | Futa on Female IL v2 · 1457484 | `futa_on_female_il_v2` | 228.479.108 | 1,0 | `futa with female` |
| futa | Futa on Male IL v2 · 2066157 | `futa_on_male_il_v2` | 228.482.300 | 1,0 | `futa on male, futa with male, futanari` |

Seçimin gerekçesi ve seçilmeyenler spec'te ve `instructions.md`'de. femboysXL'in header'ı:
`ss_sd_model_name = cagliostrolab/animagine-xl-3.0`, etiket sayımı boş ✅. B'nin v1.3 sayfası tetik
yazmıyor; v1.2 ve V1 `Fboy` ✅. D'nin sayfası 0,4 – 0,8 ✅. Beşi girişli ✅ (girişsiz `401`).

### 1.3 Yüz düzeltmesi

`ultralytics/bbox/face_yolov9c.pt` (Bingsu/adetailer, 51.648.019 B ✅ HF listesi) ve
`sams/sam_vit_b_01ec64.pth` (Meta, ~375 MB ≈); taban boyları Queen Editor'ünkiler (40 MB / 300 MB).

### 1.4 Toplam

Civitai 15.508.722.658 B ✅ (koddan da aynı çıkıyor), yüz düzeltmesiyle ≈ 15,9 GB.

---

## 2. Adımlar, dosya dosya

### 2.1 `collab-toolbox/photo_experiments/femboy-futa-lora/femboy-futa-lora.ipynb`

Krea'nın `turbo.ipynb`'sinin biçiminde, 13 hücre.

- [x] **Hücre 0 (başlık):** madde, altı aday, gereken sırlar, sıra, ~15,9 GB.
- [x] **Hücre 1–2 (CONFIG):** `CIVITAI_COOKIE` standardın iki assert'iyle; `GITHUB_TOKEN` isteğe bağlı,
  Krea'nın `HF_TOKEN`'ı gibi `try/except`; değerler basılmaz. GPU. Drive mount yok (Drive kullanılmıyor).
- [x] **Hücre 3–4 (yardımcılar):** `log`, `human`, `head_text`, `run`, `check_safetensors` Krea'dan;
  `check_binary` nova-3dcg'den, birebir.
- [x] **Hücre 5–6 (ComfyUI + 8 paket):** arayüz grafiğinin node'larının paketleri; rgthree `main`
  dalından (madde 470), Impact-Pack'in `sam2`'si listeden çıkarılarak (madde 314). Manager ve DaSiWa-Nodes
  yok.
- [x] **Hücre 7–8 (modeller):** `CHECKPOINTS`, `CANDIDATES` `(grup, sürüm, dosya, bayt, etiket, güç,
  tetik)`, `OPEN`. Sıra: boş disk → probe'lar → açık dosyalar → Civitai. `civitai_fetch` Krea'nınki,
  `fileId`'siz; `open_fetch` `.part`'a, `check_binary`, `os.replace`. Özet: klasörler, sonra her adayın
  header'ından eğitildiği model ve en sık etiketleri (`trained_on`).
- [x] **Hücre 9–10 (workflow'lar):** `fetched(path)` — token'la API, token'sız ham adres; `differences()`
  — API'deki her node arayüzde var ve açık mı, bağları aynı node'dan mı (kapalı node'un içinden
  izlenerek), değerleri kutularda mı; tutmazsa durur. Farklı türü Queen Editor'ünkine çevirir
  (`36` → `CLIPTextEncodeBREAK`). Aday başına `candidate_graph`: `45` Nova, `27` yalnız aday, `3` tetik ve
  bir prompt, `40` sabit seed. `.part`'a yaz, `os.replace`; aynı adlı dosya
  varsa dokunma.
- [x] **Hücre 11–12 (başlat):** Krea'nınki; ayağa kalkınca bir `/object_info` ve Queen Editor'ün
  grafiğindeki her node türü orada aranır; tünel; altı workflow'un listesi.

### 2.2 `instructions.md`

- [x] İki aday tablosu (femboy, futa): link, sürüm, taban, indirme, güç, tetik, workflow; nedenler ve
  seçilmeyenler.
- [x] Çalıştırma, ne söylenecek; negatifin tek fark olduğu.

### 2.3 `indirilecekler.md`

- [x] Workflow'ların kaynağı, 8 paket, checkpoint'ler, altı aday (kaydedilen ve Civitai'deki adlarıyla),
  yüz düzeltmesi, toplam, inmeyenler, klasör düzeni.

### 2.4 `collab-toolbox/README.md`

- [x] `photo_experiments/` satırına `femboy-futa-lora/`.

### 2.5 Bitiş

- [x] Bütün kod hücreleri `ast.parse` ile ayrıştırılıyor; `.ipynb` geçerli JSON.
- [x] Hücre 10, hücre 8'in aday listesiyle bu makinede iki gerçek grafiğe karşı koşuldu: karşılaştırma
  geçti, `36` çevrildi, altı workflow yazıldı ve `27`, `3`, `40`, `45` beklenen değerlerde.
- [x] Suite yok: queen-editor/ ve queen-agent/ altında kod değişmedi.
- [x] Yol haritasına dokunulmadı; commit ana ajanın.

### 2.6 Review'un düzeltmeleri *(27 Ekim)*

- [x] **1.** Bu plan.
- [x] **2. Kapalı repo:** CONFIG `GITHUB_TOKEN`'ı isteğe bağlı okur; varsa `fetched()`
  `https://api.github.com/repos/AltanBaysal/Internal-tools/contents/<yol>?ref=main`'e `Authorization` ve
  `Accept: application/vnd.github.raw` ile gider, yoksa ham adrese. Token basılmaz. API adresi bu başlıkla
  ham dosyayı veriyor ✅ (token'sız, açık repoda denendi: 200, `application/vnd.github.raw`, 9.800 B).
- [x] **3.** Özet her adayın header'ını kendi `try`'ında okur; okunamazsa `okunamadı — {tür}: {mesaj}`
  basar ve sürer ✅ (bozuk bir dosyayla denendi).
- [x] **4. Negatif:** hücre 9 ve `instructions.md` — Queen Editor grafiğin negatifini kullanmaz, panelin
  negatif kutusundakini yazar (proje başına; boşsa boş); örnek senaryonun negatifi yok, deneme grafiğinkini
  tutar.
- [x] **5.** `differences()`'ın docstring'i: değer `widgets_values`'ta sırasından bağımsız aranır, ve
  `True`/`False` `1`/`0`'a eşit — bir farkı kaçırabilir, uyduramaz.
- [x] **7.** `civitai_fetch`'te §3'ü anan yorum geri geldi: bozuk dosya saklanır, ama bu `.part`'ın
  baytları bir safetensors header'ıyla başlamıyor ve başı basıldı, o yüzden silinir.
- [x] **8.** Spec `…-m501-femboy-futa-lora-deneme-design.md` oldu; ona giden başka link yoktu.

### 2.7 Yapılırken değişti: deneme Nova'nın defterine *(28 Ekim)*

Kullanıcı Colab'da workflow'ları bozuk gördü ve `workflow_manual.json` elle de *"t.findInputSlot is not a
function"* ile yüklenmedi; kararı *"photo generator novaya gerekli loraları indirttir ordan direkt
kullanıp test edeyim foto experimentide silelim"*. Gerekçe ve kanıt spec'te, "Yapılırken değişti".

- [x] **Sebep, koddan ✅:** Impact-Pack `js/impact-pack.js:639` `node.connect(…, node.id, 'input1')`;
  ComfyUI_frontend `b4ae6344` (1.47.6+) node numaralarını yazı yaptı, `connect` yalnız sayıyı node'a
  çeviriyor. 1.45.20, 1.49.6, 1.53.6, 1.55.18, 1.57.4 ve 1.57.6'nın `LGraphNode`'u okundu.
- [x] **`photo_generator/nova-3dcg/manual.ipynb`, 3. bölüm:** `requirements.txt`'ten sonra
  `comfyui-frontend-package==1.46.15`, `run()` ile (fail-loud), nedenini yazan yorumla; markdown'da bir
  paragraf. *(Review'dan sonra)* rgthree, Queen Editor'ün `BRANCHES`'ı gibi `main` dalından (madde 470).
- [x] **4. bölüm:** `CIVITAI_MODELS`'a altı aday, deneme defterindeki sürüm ve adlarla (324974, 2693790,
  2176350, 2698395, 1457484, 2066157); başlıklarda ~16,5 GiB.
- [x] **"Nova preset" hücresi:** "Femboy ve futa denemesi (v11 madde 501)" — aday tablosu (LoRA, güç,
  tetik), her üretimin dört adımı (POSITIVE: tetik + `, ` + kullanıcının kendi prompt'u), ne getirilecek.
- [x] **Kareler çıktı** *(kullanıcı, 28 Ekim — "ben senden kare yamanı istemedim yazdığı nyerdende temizle
  promtpları")*: prompt'ları kullanıcı yazar, yalnız tetikleri ister. Kareler, onlara dayanan
  karşılaştırma ve resim sayısı defterden, spec'ten ve bu plandan silindi.
- [x] **5. bölüm:** son hücrenin ipucularına deneme için iki satır, karesiz.
- [x] **`git rm -r collab-toolbox/photo_experiments/femboy-futa-lora/`**; `collab-toolbox/README.md`'deki
  cümle nova-3dcg'nin defterine döndü; spec'in defter linki yeni yere.
- [x] **Yerel deneme ✅** (`tmp/` altında, CPU, sonra silindi): 1.57.6'da kullanıcının penceresi birebir;
  1.46.15'te hatasız, eksik node yok.
- [x] Dört suite.

### 2.8 Seçim: DaSiWa'ya iki futa seçeneği *(28 Ekim)*

Kullanıcı, 28 Ekim — *"tamam test ettim / bunlar dasiwa için olacak / 2 senecek olucak / 1 futa sadece
futa flaccid olacak 0.50 ile / 2. seçenekte futa on male olacak buda 0.50 futa flaccid 1.00 futa on male
olucak 2 lora / novada ikisde iyi çalımıyor çünkü / tetik kelilerini queen editor otomaik eklicek"*.
Femboy seçilmedi. Neden ve nasıl spec'te, "Seçim".

- [x] **Önce testler** (kırmızı görüldü): `test_photo_usecases.py` — DaSiWa'nın listede kendi kutusu
  (USNR, Slime, Futa, Futa on male, Boş), ortak satırların ortak listeden kurulduğu, iki futa satırının
  dosya, güç ve tetiği, DaSiWa'nın seçimi kaydedip negatifi tuttuğu, Nova'da futa'nın ve DaSiWa'da
  SNOFS'un reddedildiği; `test_comfy_photo_generator.py` — Futa `lora_1`'de 0,5 ve tetik, Futa on male
  `lora_1` + `lora_2` ve iki tetik, Nova'da futa çizimi durdurur; `test_notebook_installs_the_producer_groups.py`
  — `CIVITAI_DASIWA`'nın iki sürümü, aynadan, DaSiWa'nın kutusunun arkasında, disk hesabında, ve bir
  checkpoint'in kendi kutusundaki her dosya defterde.
- [x] **`backend/features/photo_generation/domain/catalog.py`:** `LORAS` `MODELS`'ın üstüne alındı (DaSiWa'nın
  kutusu ondan kurulur); `FUTA_FLACCID`, `FUTA_ON_MALE`, iki tetik; `_one_file`; `DASIWA_LORAS`; DaSiWa'nın
  satırına `"loras": DASIWA_LORAS`. Docstring'ler.
- [x] **`backend/features/photo_generation/data/comfy_photo_generator.py`:** `_lora` → `_pick(model, lora)`:
  kendi kutusu olan model `own_pick`, öteki ortak kutu, ikisi de `{"files", "trigger"}`; `_set_loras`
  seçimin dosyalarını alır.
- [x] **`start_batch.py`, `list_models.py`, `model_groups.py`:** yalnız yorumlar.
- [x] **`queeneditor.ipynb`:** `CIVITAI_DASIWA`, `+ (CIVITAI_DASIWA if PHOTO_DASIWA else [])`,
  `+ (1 if PHOTO_DASIWA else 0)`. `BRANCH` satırına dokunulmadı.
- [x] **Frontend:** kod değişmedi — panel kutuyu modelin satırından okur. `GeneratePanel.test.jsx`'e
  DaSiWa'nın kutusu (dört test) ve "her kutu kendi seçimini tutar" testinde DaSiWa'nın artık kendi seçimi;
  `GeneratePanel.jsx` ve `PhotoDetail.jsx`'te yalnız yorumlar; dist yeniden derlendi.
- [x] **`collab-toolbox/photo_generator/nova-3dcg/manual.ipynb`:** altı aday satırı, "Femboy ve futa
  denemesi" bölümü, son hücrenin iki ipucu satırı ve başlıklardaki ~16,5 GiB çıktı. Hücreler denemeden
  önceki (`6cf5c5b5`) hâllerine döndü; arayüz sabitlemesi, rgthree `main` ve http2 kaldı. JSON düzeni
  aynı (NotebookEdit, hücre kaynakları tek satır).
- [x] Dört suite.

### 2.9 Review'un düzeltmeleri *(28 Ekim)*

- [x] **Kural domain'e:** `catalog.find_own_lora` → `catalog.box_row` (kutu taşıyan satırın kutusu, yoksa
  ortak kutunun satırı `_one_file`'la); `catalog.pick` (çizilen seçim: `drawn_with`, ortak kutuda
  varsayılan, Boş dosyasız, bilinmeyen None). `start_batch`, `drawn_with`, `own_pick` `box_row`'u;
  üretecin `_pick`'i `catalog.pick`'i kullanır, yalnız None'da durur. `with_trigger`'ın docstring'i.
- [x] **Yorumlar:** `catalog.py`'nin modül docstring'i, `plan_frames`'in docstring'i, DaSiWa'nın boş
  seçim testi; model sayan yorumlar *"satırı kutu taşıyan model"* oldu (`start_batch.py`,
  `list_models.py`, `catalog.py`, `GeneratePanel.jsx`, `PhotoDetail.jsx`). Dist değişmedi.
- [x] **DaSiWa'da bilinmeyen id** ilk satıra düşer, bir üreteç testiyle sabit; `queen-editor/BACKLOG.md`'ye
  238'e aykırılığı yazan madde.
- [x] `test_dasiwa_s_shared_rows_are_the_shared_box_s_own` çıktı.
- [x] **`model_groups.py`:** rgthree'nin eksik dosyada ne yaptığı bu repoda okunamadı; yorum yalnız
  indirme hücresinin durduğunu söylüyor.

---

## 3. Maliyet ve bozulabilecekler

- **İstekler:** dosya başına bir indirme, yerinde olan için ağa gidilmez; Civitai dosyası başına bir
  1 KB'lık probe (en fazla 8); GitHub'a 2, ComfyUI'ye 1 istek. N dosyada O(N).
- **Çerez yok ya da bayat:** CONFIG'de ya da probe'larda, ağır bir dosya inmeden durur.
- **Yarım dosya:** `.part`'ta doğrulanır, ancak sonra gerçek adına taşınır. Bozuk bir dosya yerinde
  kalır, hücre durur. Civitai'nin `.part`'ı bir sonraki koşuda yargılanır: yarımsa devam, tamsa yerine,
  header'ı bozuksa başı basılıp silinir.
- **Kullanıcının kaydı:** Workflows'ta aynı adla bir dosya varsa dokunulmaz.
- **Grafikler ayrılırsa** hücre 10 durur ve farkları basar.

---

## 4. Doğrulanamayanlar

- **Rgthree'nin LoRA satırı** `widgets_values`'tan kuruluyor ≈ — `configure()`'ının kaynağından ✅
  okundu, ComfyUI'de açılmadı.
- **B'nin tetiği** `Fboy` ≈; defterin etiket sayımı gösterecek.
- **Adayların Nova ve DaSiWa'da nasıl çizdiği:** sayfalardaki örneklerin üretim bilgisi girişsiz
  okunmuyor ≈. Denemenin sorusu bu.
- **E ve F'nin partnersiz bir prompt'ta ne yaptığı**, ve E'nin bir erkekle ne yaptığı ≈.
