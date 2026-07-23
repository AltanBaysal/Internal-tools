# WAN 2.2 T2V — LoRA takası (SmoothMix Animations seti) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `wan22-smooth-t2v`'nin iki notebook'u da I2V tabanlı `WAN_General_NSFW` çifti yerine SmoothMix yazarının T2V-native altı LoRA'sını indirsin; iki listenin LoRA bloğu birebir aynı olsun.

**Architecture:** Değişiklik yalnız indirme listesinde ve dokümanlarda. Her iki notebook'ta `CIVITAI_MODELS` listesine altı satır girer, iki satır çıkar; `api.ipynb`'ye eksik olan `LORA` klasör sabiti ve `loras/` özeti eklenir. Grafiklere dokunulmaz — LoRA'lar UI'da elle takılıp Export (API) ile grafiğe girene kadar videoya etki etmez.

**Tech Stack:** Jupyter notebook (`.ipynb`, NotebookEdit ile düzenlenir), Google Colab, Civitai gated download (curl + cookie).

**Spec:** [2026-07-21-t2v-lora-swap-design.md](../specs/2026-07-21-t2v-lora-swap-design.md)

## Global Constraints

- **COMMIT YOK.** Kullanıcı 2026-07-21'de açıkça söyledi: *"bir şeyi git'e ekleyip commit etme şuan, iş bitene kadar — ben söylerim."* Hiçbir task'ta `git add` ya da `git commit` çalıştırılmaz. Tüm iş bitince kullanıcı söyleyecek.
- **Branch: `feat/wan22-smooth-t2v-api`.** Yeni branch açma.
- **`--amend` KULLANMA.** Aynı çalışma ağacında ikinci bir Claude oturumu var.
- **Shell komutu.** İnceleme için Read/Grep, düzenleme için NotebookEdit/Edit. Hücre sayısı doğrulaması Grep ile `"cell_type"` sayımıdır; notebook JSON'ı ayrıca doğrulanmaz — NotebookEdit bozuk JSON'ı ayrıştıramaz, başarılı düzenleme zaten kanıttır.
- **Dil** (kök `CLAUDE.md`): markdown hücreleri + runtime çıktısı (`print`/`log`/`assert`) **Türkçe**; kod yorumları + docstring'ler **İngilizce**.
- **`workflow_api.json` / `workflow_manual.json` değiştirilmez.** Bu iş grafiğe dokunmuyor.
- **`collab-toolbox/video_generator/imageToVideo.ipynb` değiştirilmez.** Aynı NSFW LoRA çiftini indiriyor ama o araç I2V — LoRA orada base'iyle uyumlu.
- **Altı version ID sabit** (Civitai API'den 2026-07-21'de doğrulandı): Style 2318650/2318707, Animation 2309690/2309689, Futanari 2476982/2474616. Hepsi base `Wan Video 2.2 T2V-A14B`.
- **XXX Animations çifti (2376136/2376143) eklenmez** — I2V-A14B, kullanıcı kararı: inmesin.
- **Boyut:** LoRA başına ~300 MB. Yeni toplam iki notebook için de **~35.3 GiB**.

---

### Task 1: `manual.ipynb` — LoRA listesini değiştir

**Files:**
- Modify: `collab-toolbox/video_generator/wan22-smooth-t2v/manual.ipynb` (cell-8, model indirme kod hücresi)

**Interfaces:**
- Consumes: hücrede zaten tanımlı `DIFF`, `LORA` sabitleri ve `fetch()` / `civitai_probe()` / `civitai_url()` / `cookie_header()` fonksiyonları.
- Produces: `CIVITAI_MODELS` listesi — 8 satır (2 checkpoint + 6 LoRA). Task 2 bunun LoRA bloğunun birebir aynısını `api.ipynb`'ye koyar.

- [ ] **Step 1: `CIVITAI_MODELS` bloğunu yorumuyla birlikte değiştir**

Hücredeki şu blok:

```python
# === Civitai gated models (curl + login cookie) ===
# Civitai serves these as smoothMixWan2214BI2V_t2v*V30.safetensors; UNETLoader 37/56 ask for
# SmoothMix_T2V_*_v3.safetensors, so they land under the name the graph expects.
# The NSFW LoRAs are trained for I2V-A14B (model 1307155 has no T2V version) -> if output looks
# wrong, bypass them first before blaming T2V itself.
CIVITAI_MODELS = [
    # (version_id, target_dir, filename, label)
    (2768924, DIFF, "SmoothMix_T2V_High_v3.safetensors", "SmoothMix T2V v3 HIGH"),
    (2768944, DIFF, "SmoothMix_T2V_Low_v3.safetensors",  "SmoothMix T2V v3 LOW"),
    (2073605, LORA, "WAN_General_NSFW_HIGH.safetensors", "WAN General NSFW HIGH"),
    (2083303, LORA, "WAN_General_NSFW_LOW.safetensors",  "WAN General NSFW LOW"),
]
```

şununla değişir:

```python
# === Civitai gated models (curl + login cookie) ===
# Civitai serves the checkpoints as smoothMixWan2214BI2V_t2v*V30.safetensors; UNETLoader 37/56 ask
# for SmoothMix_T2V_*_v3.safetensors, so they land under the name the graph expects.
# The LoRAs are the checkpoint author's own collection (model 2040641), all trained on T2V-A14B,
# so they match this graph. They do nothing until they are loaded in the UI: High belongs in Power
# Lora Loader 109, Low in 110, and the prompt needs a trigger word (SmoothMixAnime /
# SmoothMixRealism, or the Futanari set's own words).
# The collection's XXX Animations pair is deliberately absent -- it is I2V-A14B, the same base
# mismatch that got the previous NSFW pair dropped.
CIVITAI_MODELS = [
    # (version_id, target_dir, filename, label)
    (2768924, DIFF, "SmoothMix_T2V_High_v3.safetensors", "SmoothMix T2V v3 HIGH"),
    (2768944, DIFF, "SmoothMix_T2V_Low_v3.safetensors",  "SmoothMix T2V v3 LOW"),
    (2318650, LORA, "SmoothMix_Style_High.safetensors",     "SmoothMix Style HIGH"),
    (2318707, LORA, "SmoothMix_Style_Low.safetensors",      "SmoothMix Style LOW"),
    (2309690, LORA, "SmoothMix_Animation_High.safetensors", "SmoothMix Animation HIGH"),
    (2309689, LORA, "SmoothMix_Animation_Low.safetensors",  "SmoothMix Animation LOW"),
    (2476982, LORA, "SmoothMix_Futanari_High.safetensors",  "SmoothMix Futanari HIGH"),
    (2474616, LORA, "SmoothMix_Futanari_Low.safetensors",   "SmoothMix Futanari LOW"),
]
```

Hücrenin geri kalanı (`COMFY`/`DIFF`/`LORA` sabitleri, `os.makedirs` döngüsü, `fetch()`, `HF_MODELS`, probe döngüsü, indirme döngüleri, `loras/` özeti) **aynen kalır** — hepsi liste üzerinden dönüyor, satır sayısından bağımsız.

- [ ] **Step 2: Aynı hücredeki indirme boyutunu güncelle**

Hücrede `~35 GiB` geçen log/print satırı varsa `~35.3 GiB` yapılır. Grep ile `35 GiB` ara (bu notebook'ta 22. ve 168. ham satırlarda geçiyor: biri markdown başlık hücresi, biri model bölümü).

- [ ] **Step 3: Eski çiftin gittiğini doğrula**

Grep tool ile `manual.ipynb` içinde `WAN_General_NSFW|1307155|2073605|2083303` ara.
Expected: **0 eşleşme**.

- [ ] **Step 4: Yeni ID'lerin geldiğini doğrula**

Grep tool ile `manual.ipynb` içinde `2318650|2318707|2309690|2309689|2476982|2474616` ara.
Expected: **6 eşleşme** (hücre tek JSON satırıysa 1 satırda 6 kez).

- [ ] **Step 5: Hücre sayısının değişmediğini doğrula**

Grep tool ile `manual.ipynb` içinde `"cell_type"` say.
Expected: düzenlemeden önceki sayıyla aynı.

---

### Task 2: `api.ipynb` — aynı LoRA setini indir

**Files:**
- Modify: `collab-toolbox/video_generator/wan22-smooth-t2v/api.ipynb` (cell-10 model indirme kodu; cell-0 başlık; cell-9 model bölümü markdown'ı)

**Interfaces:**
- Consumes: Task 1'in `CIVITAI_MODELS` LoRA bloğu — **birebir aynı altı satır**, aynı sırada, aynı dosya adlarıyla.
- Produces: `api.ipynb`'de `LORA` sabiti (`f"{COMFY}/models/loras"`) — hücrenin özet bloğu kullanır.

- [ ] **Step 1: `LORA` klasör sabitini ekle**

cell-10'da şu iki satır:

```python
COMFY = COMFY_ROOT
DIFF  = f"{COMFY}/models/diffusion_models"
```

şu üç satır olur:

```python
COMFY = COMFY_ROOT
DIFF  = f"{COMFY}/models/diffusion_models"
LORA  = f"{COMFY}/models/loras"
```

Alttaki `os.makedirs` döngüsü `loras` klasörünü zaten oluşturuyor, ona dokunulmaz.

- [ ] **Step 2: `CIVITAI_MODELS` bloğunu değiştir**

cell-10'daki şu blok:

```python
# === Civitai gated models (curl + login cookie) ===
# Civitai serves these as smoothMixWan2214BI2V_t2v*V30.safetensors; UNETLoader 37/56 ask for
# SmoothMix_T2V_*_v3.safetensors, so they land under the name the graph expects.
# No distill LoRA here: T2V v3 has lightx2v merged into the checkpoint, and the exported graph
# runs 6 steps at cfg 1 with every Power Lora Loader empty.
CIVITAI_MODELS = [
    # (version_id, target_dir, filename, label)
    (2768924, DIFF, "SmoothMix_T2V_High_v3.safetensors", "SmoothMix T2V v3 HIGH"),
    (2768944, DIFF, "SmoothMix_T2V_Low_v3.safetensors",  "SmoothMix T2V v3 LOW"),
]
```

şununla değişir (LoRA satırları Task 1'le birebir aynı):

```python
# === Civitai gated models (curl + login cookie) ===
# Civitai serves the checkpoints as smoothMixWan2214BI2V_t2v*V30.safetensors; UNETLoader 37/56 ask
# for SmoothMix_T2V_*_v3.safetensors, so they land under the name the graph expects.
# No distill LoRA: T2V v3 has lightx2v merged into the checkpoint, and the graph runs 6 steps at
# cfg 1 without one.
# The style LoRAs below are the same set manual.ipynb downloads -- the two lists are kept aligned
# so a LoRA-enabled graph exported from the UI runs here without touching this notebook. They have
# no effect until that export happens: this graph's Power Lora Loaders are empty.
CIVITAI_MODELS = [
    # (version_id, target_dir, filename, label)
    (2768924, DIFF, "SmoothMix_T2V_High_v3.safetensors", "SmoothMix T2V v3 HIGH"),
    (2768944, DIFF, "SmoothMix_T2V_Low_v3.safetensors",  "SmoothMix T2V v3 LOW"),
    (2318650, LORA, "SmoothMix_Style_High.safetensors",     "SmoothMix Style HIGH"),
    (2318707, LORA, "SmoothMix_Style_Low.safetensors",      "SmoothMix Style LOW"),
    (2309690, LORA, "SmoothMix_Animation_High.safetensors", "SmoothMix Animation HIGH"),
    (2309689, LORA, "SmoothMix_Animation_Low.safetensors",  "SmoothMix Animation LOW"),
    (2476982, LORA, "SmoothMix_Futanari_High.safetensors",  "SmoothMix Futanari HIGH"),
    (2474616, LORA, "SmoothMix_Futanari_Low.safetensors",   "SmoothMix Futanari LOW"),
]
```

- [ ] **Step 3: Özet bloğuna `loras/` ekle**

cell-10'un sonundaki:

```python
# === Summary (reaching here means everything downloaded + validated) ===
print("\n📂 diffusion_models/")
for f in sorted(glob.glob(f"{DIFF}/*.safetensors")):
    print(f"   {human(os.path.getsize(f))}  {os.path.basename(f)}")
log("Tüm modeller indirildi ve doğrulandı", "OK")
```

şu olur:

```python
# === Summary (reaching here means everything downloaded + validated) ===
print("\n📂 diffusion_models/")
for f in sorted(glob.glob(f"{DIFF}/*.safetensors")):
    print(f"   {human(os.path.getsize(f))}  {os.path.basename(f)}")
print("\n📂 loras/")
for f in sorted(glob.glob(f"{LORA}/*.safetensors")):
    print(f"   {human(os.path.getsize(f))}  {os.path.basename(f)}")
log("Tüm modeller indirildi ve doğrulandı", "OK")
```

- [ ] **Step 4: cell-0'daki LoRA notunu değiştir**

Başlık hücresinin sonundaki:

```markdown
> **LoRA yok, olması da gerekmiyor.** SmoothMix T2V v3'te lightx2v checkpoint'e merge edilmiş (model sayfası: *"Just as T2V v2.0 it has light2xv baked in it"*); ayrıca yüklemek iki kez uygular ve çıktıyı bozar. Graf 6 step / cfg 1 ile LoRA'sız çalışır.
```

şununla değişir:

```markdown
> **Distill LoRA yok, olması da gerekmiyor.** SmoothMix T2V v3'te lightx2v checkpoint'e merge edilmiş (model sayfası: *"Just as T2V v2.0 it has light2xv baked in it"*); ayrıca yüklemek iki kez uygular ve çıktıyı bozar. Graf 6 step / cfg 1 ile çalışır.

> **Stil LoRA'ları iner ama kendiliğinden etki etmez.** SmoothMix Animations seti (Style / Animation / Futanari) `manual.ipynb` ile aynı şekilde `loras/` klasörüne iner — iki notebook'un listesi hizalı tutuluyor. Videoya etki etmesi için `manual.ipynb`'de UI'da Power Lora Loader **109** (High) / **110** (Low) üzerinden takıp **Export (API)** ile Drive'daki `workflow_api.json`'u güncellemen gerekir; o zaman bu notebook'ta kod değişikliği gerekmez.
```

- [ ] **Step 5: İndirme boyutlarını güncelle**

`api.ipynb`'de `33.5 GiB` iki yerde geçiyor (ham satır 6 = cell-0 içindeki bölüm listesi, ham satır 107 = cell-9 model bölümü başlığı). İkisi de **`35.3 GiB`** olur.

- [ ] **Step 6: İki listenin hizalı olduğunu doğrula**

Grep tool ile her iki notebook'ta `SmoothMix_Style_High|SmoothMix_Style_Low|SmoothMix_Animation_High|SmoothMix_Animation_Low|SmoothMix_Futanari_High|SmoothMix_Futanari_Low` ara.
Expected: `manual.ipynb` ve `api.ipynb`'nin **ikisinde de altı ad** geçiyor.

- [ ] **Step 7: `LORA` sabitinin tanımlı olduğunu doğrula**

Grep tool ile `api.ipynb` içinde `LORA  = ` ara.
Expected: 1 eşleşme. (Tanımsız `LORA` kullanımı hücreyi `NameError` ile patlatırdı.)

- [ ] **Step 8: Hücre sayısının değişmediğini doğrula**

Grep tool ile `api.ipynb` içinde `"cell_type"` say.
Expected: **15**.

---

### Task 3: `dependencies.md` — manifesti güncelle

**Files:**
- Modify: `collab-toolbox/video_generator/wan22-smooth-t2v/dependencies.md`

**Interfaces:**
- Consumes: Task 1 ve 2'nin ürettiği liste (dosya adları, version ID'ler, klasör).
- Produces: yok.

- [ ] **Step 1: Baştaki "hangi notebook neyi indirir" tablosunu değiştir**

Şu blok:

```markdown
**Hangi notebook neyi indirir:**

| Notebook | İner | Toplam |
|---|---|---|
| `manual.ipynb` | aşağıdaki listenin tamamı | ~34.7 GiB |
| `api.ipynb` | aynısı, **NSFW LoRA'lar hariç** — API grafiğinde LoRA loader'ları boş, yerleri yok | ~33.5 GiB |
```

şununla değişir:

```markdown
**Hangi notebook neyi indirir:** ikisi de **aynı seti**, ~35.3 GiB. Bu bilinçli bir kural — listeler hizalı tutulur ki UI'da LoRA'lı bir graf export edildiğinde `api.ipynb` notebook'a dokunmadan çalışsın.

> `api.ipynb` LoRA'ları indirir ama **kullanmaz**: API grafiğinin Power Lora Loader'ları boş. Etki etmeleri için `manual.ipynb`'de UI'da takılıp **Export (API)** ile Drive'daki graf güncellenmeli.
```

- [ ] **Step 2: §2 girişindeki model kaynağını düzelt**

Şu satır:

```markdown
İki ayrı Civitai modelinden geliyor: checkpoint'ler **1995784**'ten (SmoothMix WAN 2.2), LoRA'lar **1307155**'ten (WAN General NSFW).
```

şununla değişir:

```markdown
İki ayrı Civitai modelinden geliyor, ikisi de aynı yazarın: checkpoint'ler **1995784**'ten (SmoothMix WAN 2.2), LoRA'lar **2040641**'den (SmoothMix Animations WAN 2.2).
```

- [ ] **Step 3: §2 tablosundaki iki NSFW satırını altı yeni satırla değiştir**

Çıkacak satırlar:

```markdown
| loras | `WAN_General_NSFW_HIGH.safetensors` | **2073605** | NSFW-22-H-e8.safetensors | ~0.57 GiB | ⚠️ base `Wan Video 2.2 **I2V**-A14B` |
| loras | `WAN_General_NSFW_LOW.safetensors` | **2083303** | (2.2 LOW v0.08a nightly) | ~0.57 GiB | ⚠️ base `Wan Video 2.2 **I2V**-A14B` |
```

Girecek satırlar:

```markdown
| loras | `SmoothMix_Style_High.safetensors` | **2318650** | (Style High) | ~0.3 GiB | ✅ base `Wan Video 2.2 T2V-A14B` |
| loras | `SmoothMix_Style_Low.safetensors` | **2318707** | SmoothMixStyle_Low.safetensors | ~0.3 GiB | ✅ base `Wan Video 2.2 T2V-A14B` |
| loras | `SmoothMix_Animation_High.safetensors` | **2309690** | (Animation High) | ~0.3 GiB | ✅ base `Wan Video 2.2 T2V-A14B` |
| loras | `SmoothMix_Animation_Low.safetensors` | **2309689** | (Animation Low) | ~0.3 GiB | ✅ base `Wan Video 2.2 T2V-A14B` |
| loras | `SmoothMix_Futanari_High.safetensors` | **2476982** | (Futanaris and Males High) | ~0.3 GiB | ✅ base `Wan Video 2.2 T2V-A14B` |
| loras | `SmoothMix_Futanari_Low.safetensors` | **2474616** | (Futanaris and Males Low) | ~0.3 GiB | ✅ base `Wan Video 2.2 T2V-A14B` |
```

"Civitai'nin verdiği ad" kolonunda yalnız **2318707** için gerçek dosya adı doğrulandı (`SmoothMixStyle_Low.safetensors`); diğer beşi parantez içinde sürüm adıyla yazılıyor. **Uydurma dosya adı yazma** — istersen Civitai API'sinden (`https://civitai.red/api/v1/models/2040641`) teyit edip parantezleri gerçek adlarla değiştir.

- [ ] **Step 4: "NSFW LoRA riski" blockquote'unu değiştir**

Şu blok:

```markdown
> **NSFW LoRA riski.** Model 1307155'in dört sürümü de I2V-A14B; T2V sürümü **yok**. Kullanıcı isteğiyle iniyor. Çıktı bozuksa **önce bunu bypass et** — yoksa "T2V mi kötü, LoRA mı uyumsuz" ayrışmaz.
```

şununla değişir:

```markdown
> **LoRA kullanımı.** Altısı da T2V-A14B tabanlı, yani grafiğin base'iyle uyumlu — I2V tuzağı bu sette yok. Ama **takmak yetmez, trigger word şart**: Style ve Animation için prompt'ta `SmoothMixAnime` ya da `SmoothMixRealism` geçmeli, Futanari çifti kendi kelimeleriyle (`futanari`, `flaccid`, `erect`, …). Yazarın önerdiği strength **0.5–1.0**; High → Power Lora Loader **109**, Low → **110**.
>
> **Setin XXX Animations çifti (2376136 / 2376143) bilerek inmiyor** — koleksiyondaki tek I2V-A14B tabanlı çift, yani buraya kadar ayıkladığımız uyumsuzluğun aynısı.
>
> Önceki `WAN_General_NSFW` çifti (model 1307155, I2V tabanlı) 2026-07-21'de bu listeden çıkarıldı. `video_generator/imageToVideo.ipynb`'de **duruyor** — o araç I2V, LoRA orada uyumlu.
```

- [ ] **Step 5: Kalıntı kalmadığını doğrula**

Grep tool ile `dependencies.md` içinde `WAN_General_NSFW|1307155|2073605|2083303` ara.
Expected: yalnız Step 4'te bilerek yazılan tarihsel cümledeki `1307155` ve `WAN_General_NSFW` geçişleri. Tabloda **0**.

---

### Task 4: `instructions.md` — LoRA uyarısını daralt, kullanım tarifi ekle

**Files:**
- Modify: `collab-toolbox/video_generator/wan22-smooth-t2v/instructions.md` (satır 21 blockquote, satır 32 boyut, satır 36 kullanım adımı, satır 44 not, satır 81 boyut)

**Interfaces:**
- Consumes: Task 1–3'ün ürettiği davranış.
- Produces: yok.

- [ ] **Step 1: Satır 21'deki "LoRA EKLEME" blockquote'unu daralt**

Şu blok:

```markdown
> ⚠️ **LoRA EKLEME.** Yazar Power Lora Loader'ları (**109** / **110**) boş bırakmış ve sampler **6 step / cfg 1**'e ayarlı — bu ikisi çelişmiyor: SmoothMix T2V v3'te lightx2v checkpoint'e **merge edilmiş** (model sayfası: *"Just as T2V v2.0 it has light2xv baked in it"*). Elle bir distill LoRA daha eklersen iki kez uygulanır ve çıktı bozulur. **Boş bırak** — 18 Tem 2026'da UI'da doğrulandı, sıfır LoRA en iyi sonucu veriyor.
```

şununla değişir:

```markdown
> ⚠️ **Distill/hız LoRA'sı EKLEME.** Yazar Power Lora Loader'ları (**109** / **110**) boş bırakmış ve sampler **6 step / cfg 1**'e ayarlı — bu ikisi çelişmiyor: SmoothMix T2V v3'te lightx2v checkpoint'e **merge edilmiş** (model sayfası: *"Just as T2V v2.0 it has light2xv baked in it"*). Elle bir distill LoRA daha eklersen iki kez uygulanır ve çıktı bozulur. 18 Tem 2026'da UI'da doğrulandı: **hız LoRA'sı olmadan** en iyi sonuç alınıyor.
>
> Bu yasak **stil/hareket LoRA'larını kapsamıyor** — 109/110 tam da onlar için duruyor. `loras/` klasörüne inen SmoothMix Animations seti oraya takılabilir (bkz. Kullanım adım 6).
```

- [ ] **Step 2: Satır 32'deki indirme boyutunu güncelle**

`(~35 GiB iner.)` → `(~35.3 GiB iner.)`

- [ ] **Step 3: Satır 36'daki kullanım adımını değiştir**

Şu satır:

```markdown
6. **Power Lora Loader 109/110'a dokunma** — boş kalacaklar (yukarıdaki uyarı).
```

şununla değişir:

```markdown
6. **Power Lora Loader 109/110** — hız LoRA'sı ekleme (yukarıdaki uyarı). Stil denemek istersen `loras/`ten seç: **High → 109**, **Low → 110**, aynı setten çift olarak, strength **0.5**'ten başla — ve prompt'a trigger word yaz (`SmoothMixAnime` / `SmoothMixRealism`; Futanari çifti kendi kelimeleriyle). Trigger word olmadan LoRA sessizce etkisiz kalır.
```

- [ ] **Step 4: Satır 44'teki NSFW notunu değiştir**

Şu madde:

```markdown
- **NSFW LoRA I2V için eğitilmiş** (`Wan Video 2.2 I2V-A14B`; T2V sürümü yok). İniyor ama garantisi yok — çıktı bozuksa **önce onu bypass et**, sonra T2V'yi yargıla.
```

şununla değişir:

```markdown
- **İnen LoRA'lar T2V-native** (SmoothMix Animations, model 2040641) — eski `WAN_General_NSFW` çifti I2V tabanlı olduğu için 2026-07-21'de çıkarıldı. Yine de **çıktıya etkisi UI'da henüz ölçülmedi**: bozuk sonuç görürsen önce LoRA'ları bypass edip karşılaştır.
```

- [ ] **Step 5: Satır 81'deki API indirme boyutunu güncelle**

`(~33.5 GiB iner)` → `(~35.3 GiB iner)`

- [ ] **Step 6: Satır 61'in korunduğunu doğrula**

Grep tool ile `instructions.md` içinde `tuzağa düştük` ara.
Expected: **1 eşleşme** — bu cümle tarihsel olarak doğru ve base-model kısıtını öğretiyor, **silinmemeli**.

---

### Task 5: Repo genelinde son tarama

**Files:** yok — yalnız doğrulama.

**Interfaces:**
- Consumes: Task 1–4.

- [ ] **Step 1: Eski çift yalnız doğru yerlerde kalmış mı**

Grep tool ile `collab-toolbox/` içinde `WAN_General_NSFW` ara.
Expected: yalnız `video_generator/imageToVideo.ipynb` (üç yerde: `LORA_STRENGTHS`, `CIVITAI_MODELS`, markdown) ve `video_experiments/deneme-listesi.md`. `wan22-smooth-t2v/` altındaki notebook'larda **0**.

- [ ] **Step 2: Altı yeni ID üç dosyada da var mı**

Grep tool ile `collab-toolbox/` içinde `2318650|2318707|2309690|2309689|2476982|2474616` ara.
Expected: `manual.ipynb`, `api.ipynb`, `dependencies.md` — üç dosya.

- [ ] **Step 3: XXX çiftinin hiçbir yere sızmadığını doğrula**

Grep tool ile repo genelinde `2376136|2376143` ara.
Expected: yalnız `docs/superpowers/specs/2026-07-21-t2v-lora-swap-design.md` (bilerek dışlandığı yazılı). Notebook'larda **0**.

- [ ] **Step 4: Boyut tutarlılığı**

Grep tool ile `collab-toolbox/video_generator/wan22-smooth-t2v/` içinde `33\.5 GiB|34\.7 GiB|~35 GiB` ara.
Expected: **0 eşleşme** — hepsi `35.3 GiB` olmuş olmalı.

---

### Task 6: Colab doğrulaması (kullanıcıda)

**Files:** yok — çalıştırma adımı.

**Interfaces:**
- Consumes: Task 1–5'in tamamı.

Notebook'lar birim testle doğrulanmıyor; doğrulama Colab koşusu. Kullanıcı A100 ile:

- [ ] **Step 1: `manual.ipynb` Run all**

Beklenen: gated probe **8 asset** için geçer (2 checkpoint + 6 LoRA); özet `loras/` altında altı dosyayı ~300 MB olarak listeler.

- [ ] **Step 2: UI'da Style çiftini tak**

Power Lora Loader **109** → `SmoothMix_Style_High`, **110** → `SmoothMix_Style_Low`, strength **0.5**. Prompt'a `SmoothMixAnime` ekle, üret.

- [ ] **Step 3: LoRA'sız karşılaştırma**

Aynı prompt ve aynı seed ile 109/110'u bypass edip bir daha üret. **Asıl soru:** stil kontrolü geldi mi, kalite düştü mü?

- [ ] **Step 4: Sonucu bildir**

Beğenilirse **Export (API)** ile Drive'daki `workflow_api.json` güncellenir; `api.ipynb` kod değişikliği olmadan LoRA'lı üretir. Beğenilmezse strength ve trigger word denemeleri, ya da set değişikliği konuşulur.

- [ ] **Step 5: Commit**

Kullanıcı "commit et" dediğinde: bu işin dosyaları (`manual.ipynb`, `api.ipynb`, `dependencies.md`, `instructions.md`, spec ve bu plan) **pathspec ile** commit'lenir. Kullanıcı söylemeden commit yok.
