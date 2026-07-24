# WAN 2.2 arbuzai I2V — API modu Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `wan22-arbuzai` klasörünü `video_generator/` altına terfi ettir ve UI hiç açmadan görsel+prompt'tan Drive'a mp4 üreten `api.ipynb`'yi yaz.

**Architecture:** Kardeş `wan22-smooth-t2v/api.ipynb` şablon — `ComfyClient`, `load_workflow`, `describe_comfy_error`, poll döngüsü ve `/view` indirmesi birebir kopyalanır. Değişen: model listeleri, üç node id'si, bir de yeni "görsel yükle" hücresi. Notebook grafiği okur ve **üç alan** yazar; LoRA/çözünürlük/step grafikten gelir.

**Tech Stack:** Jupyter (Colab), ComfyUI HTTP API (`/prompt`, `/history`, `/view`, `/upload/image`), `requests`, Google Drive.

**Kaynak spec:** [2026-07-19-wan22-arbuzai-api-design.md](../specs/2026-07-19-wan22-arbuzai-api-design.md)

## Global Constraints

- **Commit yalnız kullanıcı söyleyince atılır.** Plan commit adımlarını içerir ama tetikleyen kullanıcıdır; kendiliğinden commit yok.
- **`docs/superpowers/` COMMIT EDİLMEZ.** `git add`'e her zaman **açık dosya yolu** verilir; `git add .` / `git add -A` **yasak**.
- **Branch:** mevcut `feat/wan22-smooth-t2v` — yeni branch açılmaz. **Paralel oturum var:** `CLAUDE.md`, `instructions.md`, `indirilecekler.md` ve `wan22-smooth-t2v/` altındaki dosyalar başka bir oturum tarafından düzenleniyor; **hiçbirine dokunulmaz**, `git commit --amend` kullanılmaz.
- **Python çalıştırılmaz.** Dosya incelemek Read/Grep; JSON doğrulaması PowerShell `ConvertFrom-Json`.
- **Dil:** notebook markdown hücreleri ve runtime çıktısı (`print`/`log`/`assert`/`RuntimeError`) **Türkçe**; kod yorumları ve docstring'ler **İngilizce**.
- **Yorum kuralı:** yorum WHY anlatır; `# OLD:` / `# NEW:` yok, yorum kodun **şu anki** halini anlatır.
- **Grafiğe yazılan tek üç alan:** LoadImage `287`, PromptGenerator `233:240` (prompt + seed), Seed `210`. LoRA, ağırlık, çözünürlük, step, cfg, RIFE — **dokunulmaz**.
- **`workflow_api.json` içeriği değişmez.** Taşınır, yeniden adlandırılır; tek byte düzenlenmez.
- **Drive kökü:** `/content/drive/MyDrive/imageToVideoV2` — grafik `DRIVE_ROOT/workflow_api.json`, çıktı `DRIVE_ROOT/output/`.
- **Kapsam dışı:** toplu üretim, N seed varyasyonu, modelleri Drive'da önbellekleme, `instructions.md` yazımı, `CLAUDE.md` tablosuna satır ekleme (paralel oturum o dosyada çalışıyor).

## Dosya yapısı

| Dosya | Sorumluluk |
|---|---|
| `collab-toolbox/video_generator/wan22-arbuzai/manual.ipynb` | ComfyUI'yi tünelle açar, grafiği elle kurmak/denemek için (mevcut, yalnız adı değişiyor) |
| `collab-toolbox/video_generator/wan22-arbuzai/workflow_manual.json` | v5.0 grafiğinin tam UI export'u (mevcut, yalnız adı değişiyor) |
| `collab-toolbox/video_generator/wan22-arbuzai/workflow_api.json` | IMAGE2VIDEO grubunun API export'u — `api.ipynb`'nin çalıştırdığı graf |
| `collab-toolbox/video_generator/wan22-arbuzai/api.ipynb` | **Yeni.** UI açmadan üretim |

---

### Task 1: Klasörü terfi ettir, dosyaları yeniden adlandır

**Files:**
- Move: `collab-toolbox/video_experiments/wan22-arbuzai/` → `collab-toolbox/video_generator/wan22-arbuzai/`
- Rename: `wan22-arbuzai.ipynb` → `manual.ipynb`
- Rename: `workflow.json` → `workflow_manual.json`
- Move: `workflowapi.json` (repo kökü) → `collab-toolbox/video_generator/wan22-arbuzai/workflow_api.json`

**Interfaces:**
- Consumes: —
- Produces: Task 2'nin kopyalayacağı `manual.ipynb` ve yanına yazılacağı klasör yolu.

**Neden komut:** dosya taşıma/yeniden adlandırma Read/Write ile yapılamaz; `git mv` geçmişi korur ve değişikliği rename olarak kaydeder.

- [ ] **Step 1: Hedef yol boş mu — kontrol et**

```powershell
Test-Path collab-toolbox\video_generator\wan22-arbuzai
```

Beklenen: `False`. `True` ise DUR — paralel oturum önden taşımış olabilir, durumu kullanıcıya sor.

- [ ] **Step 2: Klasörü taşı**

```bash
git mv collab-toolbox/video_experiments/wan22-arbuzai collab-toolbox/video_generator/wan22-arbuzai
```

Beklenen: çıktı yok.

- [ ] **Step 3: İki dosyayı yeniden adlandır**

```bash
git mv collab-toolbox/video_generator/wan22-arbuzai/wan22-arbuzai.ipynb collab-toolbox/video_generator/wan22-arbuzai/manual.ipynb
git mv collab-toolbox/video_generator/wan22-arbuzai/workflow.json collab-toolbox/video_generator/wan22-arbuzai/workflow_manual.json
```

- [ ] **Step 4: API export'unu klasöre taşı**

Kökteki dosya git'te izlenmiyor, o yüzden `git mv` değil düz `mv`:

```bash
mv workflowapi.json collab-toolbox/video_generator/wan22-arbuzai/workflow_api.json
```

- [ ] **Step 5: İçerik değişmedi mi — doğrula**

```powershell
Get-FileHash -Algorithm SHA256 collab-toolbox\video_generator\wan22-arbuzai\workflow_manual.json | Select-Object -ExpandProperty Hash
```

Beklenen: `9FEEFC6FE6DC45B1FA53C1CE3E0CD6550262F208930C3A56BB49DE329E997FF8`. Farklıysa DUR — taşıma sırasında dosya bozulmuş.

- [ ] **Step 6: API export'u hâlâ geçerli JSON ve API formatında mı**

```powershell
$w = Get-Content collab-toolbox\video_generator\wan22-arbuzai\workflow_api.json -Raw | ConvertFrom-Json
"UI formati mi: " + [bool]($w.PSObject.Properties.Name -contains 'nodes')
"287 / 233:240 / 210 var mi: " + [bool]$w.'287' + " " + [bool]$w.'233:240' + " " + [bool]$w.'210'
```

Beklenen: `UI formati mi: False` ve `287 / 233:240 / 210 var mi: True True True`. Biri `False` ise DUR — Task 2'nin node id'leri tutmaz.

- [ ] **Step 7: Klasörün son hali**

```bash
ls -1 collab-toolbox/video_generator/wan22-arbuzai/
git status --short
```

Beklenen dosyalar: `manual.ipynb`, `workflow_api.json`, `workflow_manual.json`. `git status`'ta `docs/` untracked kalmalı, `CLAUDE.md` ve `wan22-smooth-t2v/` altındaki değişiklikler **dokunulmamış** görünmeli.

- [ ] **Step 8: Commit (kullanıcı söyleyince)**

```bash
git add collab-toolbox/video_generator/wan22-arbuzai/manual.ipynb collab-toolbox/video_generator/wan22-arbuzai/workflow_manual.json collab-toolbox/video_generator/wan22-arbuzai/workflow_api.json
git commit -F- <<'EOF'
refactor(wan22-arbuzai): promote out of video_experiments

The manual notebook ran end to end on Colab and produced video, which is the
bar video_experiments/ exists to clear. The folder now sits next to
imageToVideo and wan22-smooth-t2v under video_generator/.

Renamed to the naming its sibling settled on: manual.ipynb drives the graph by
hand behind a tunnel, workflow_manual.json is the full four-group UI export.
workflow_api.json is the IMAGE2VIDEO group exported through Workflow → Export
(API) -- a different file, not a conversion of the other one.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF
git show --stat --name-status HEAD
```

Beklenen: üç yol da `R` (rename) veya `A` (add) olarak listelenir, `docs/` yok.

---

### Task 2: api.ipynb — UI açmadan üretim

**Files:**
- Create: `collab-toolbox/video_generator/wan22-arbuzai/api.ipynb` (kaynak: `collab-toolbox/video_generator/wan22-smooth-t2v/api.ipynb`)

**Interfaces:**
- Consumes: Task 1'in `manual.ipynb`'si (model listesi oradan alınır) ve `workflow_api.json`'u (node id'leri oradan doğrulandı).
- Produces: `generate(prompt, image_name, seed=None) -> str` (kaydedilen Drive yolu), `upload_image() -> str` (ComfyUI'ın verdiği sunucu tarafı dosya adı).

**Yaklaşım:** kardeş `api.ipynb` kopyalanır, 15 hücreye çıkarılır. Kopyada 13 hücre var (0-12); **6 hücre değişir, 2 hücre eklenir**, kalan 7 hücre parmak sürülmeden kalır.

Dokunulmayanlar: `2) Ortak Yardımcılar` md+kod (`log`/`human`/`head_text`/`run`/`check_safetensors`/`describe_comfy_error`), `3) Custom node'lar` kod (16'lık liste), `5) ComfyUI'yi başlat` md+kod, `1) CONFIG` md.

Bu hücreler kopyayla birlikte iki yeni şey getiriyor, ikisi de korunacak: `1) CONFIG` md'sindeki "PROMPT'u üç tırnağın arasına yaz" yönergesi, ve yardımcılar hücresinin başındaki `assert "COMFY_ROOT" in globals()` kapısı. O assert, CONFIG hücresi çalışmadan 2-3. bölüme geçilmesini engelliyor — CONFIG'de patlayan bir hata yoksa ancak ~5 dakikalık kurulumdan sonra 4. bölümde görülüyordu. **Yazacağın CONFIG hücresi `COMFY_ROOT`'u tanımlamak zorunda**, yoksa kapı kendi notebook'unu kilitler.

**Adım sırası önemli.** Hücre id'leri konumsal (`cell-0`, `cell-1`, …), yani ekleme sonrası kendinden sonrakiler kayar. Bu yüzden önce üstteki index'ler (12, 11) düzenlenir, sonra ekleme yapılır, sonra ekleme noktasının **altında kalan** index'ler (8, 7, 5, 2, 0) düzenlenir — hepsi 10'un altında olduğu için kaymadan etkilenmezler.

- [ ] **Step 1: Kardeş notebook'u kopyala**

```powershell
Copy-Item collab-toolbox\video_generator\wan22-smooth-t2v\api.ipynb collab-toolbox\video_generator\wan22-arbuzai\api.ipynb
```

- [ ] **Step 2: Kopyayı oku, hücre index'lerini teyit et**

Read: `collab-toolbox/video_generator/wan22-arbuzai/api.ipynb`

Beklenen 13 hücre: `0` md başlık · `1` md CONFIG · `2` code CONFIG · `3` md helpers · `4` code helpers · `5` md custom nodes · `6` code custom nodes · `7` md modeller · `8` code modeller · `9` md başlat · `10` code başlat · `11` md üret · `12` code üret.

- [ ] **Step 3: Hücre 12 (kod, üret) — I2V sürümüyle değiştir**

Kardeşten farkı: üç node id, `set_image`, `produced_files` ile tam temizlik, `generate` imzası.

```python
import copy, json, os, random, time, uuid, requests

class ComfyExecutionError(RuntimeError):
    """A prompt failed inside ComfyUI. Carries the raw error, plus whether it is infra-level.
    infra=True -> a model loader node failed, so the model is broken or missing."""
    def __init__(self, text, traceback_text, infra):
        super().__init__(text)
        self.text = text
        self.traceback_text = traceback_text
        self.infra = infra

# === Node ids (from workflow_api.json) ===
# Opaque strings, not numbers: "233:240" is a subgraph-flattened id.
IMAGE_NODE  = "287"       # LoadImage, inputs.image -> the uploaded file's server-side name
PROMPT_NODE = "233:240"   # PromptGenerator, inputs.prompt -> CLIPTextEncode 176
SEED_NODE   = "210"       # Seed (rgthree) -> KSamplerAdvanced 236:206 noise_seed

# === Template I/O + patchers (SRP: one function injects one field) ===
def load_workflow(path):
    with open(path, encoding="utf-8") as f:
        wf = json.load(f)
    if "nodes" in wf:
        raise RuntimeError(
            "workflow_api.json UI formatında — ComfyUI'de 'Workflow → Export (API)' ile kaydet"
        )
    for node_id in (IMAGE_NODE, PROMPT_NODE, SEED_NODE):
        if node_id not in wf:
            raise RuntimeError(f"Workflow'da {node_id} node yok — graf değişmiş, node id'leri güncelle")
    return wf

def set_image(workflow, image_name):
    workflow[IMAGE_NODE]["inputs"]["image"] = image_name

def set_prompt(workflow, prompt):
    workflow[PROMPT_NODE]["inputs"]["prompt"] = prompt

def set_seed(workflow, seed):
    """Both seeds: the sampler's noise seed and PromptGenerator's own, so a rerun with the same
    seed reproduces the video even when the prompt uses wildcard syntax.

    The graph ships Seed (rgthree) at -1. rgthree randomises in the frontend widget, which does
    not exist in API mode -- sending -1 through would pin every run to the same noise.
    """
    workflow[SEED_NODE]["inputs"]["seed"] = seed
    workflow[PROMPT_NODE]["inputs"]["seed"] = seed

def produced_files(history_entry):
    """Every file this prompt wrote, as ComfyUI-relative paths.

    The graph has two savers: VHS_VideoCombine (mp4) and SaveImage (last frame png). Only the
    video goes to Drive, but both are cleared off the Colab disk.
    """
    paths = []
    for node_output in history_entry.get("outputs", {}).values():
        for key in ("gifs", "videos", "images"):
            for item in node_output.get(key, []):
                if item.get("type", "output") != "output":
                    continue                       # temp previews are not on disk as outputs
                paths.append(os.path.join(item.get("subfolder", ""), item["filename"]))
    return paths

# === ComfyUI HTTP client ===
class ComfyClient:
    def __init__(self, base_url):
        self.base = base_url.rstrip("/")
        self.client_id = str(uuid.uuid4())

    def submit(self, workflow):
        r = requests.post(f"{self.base}/prompt",
                          json={"prompt": workflow, "client_id": self.client_id}, timeout=30)
        if r.status_code >= 400:
            raise RuntimeError(f"POST /prompt -> HTTP {r.status_code}\n{r.text}")
        data = r.json()
        if data.get("node_errors"):
            raise RuntimeError("POST /prompt -> node_errors\n"
                               + json.dumps(data["node_errors"], indent=2, ensure_ascii=False))
        return data["prompt_id"]

    def wait(self, prompt_id, timeout):
        start = time.time()
        while True:
            if time.time() - start > timeout:
                raise TimeoutError(f"prompt {prompt_id}: {timeout}s içinde bitmedi")
            history = requests.get(f"{self.base}/history/{prompt_id}", timeout=30).json()
            if prompt_id in history:
                entry = history[prompt_id]
                status = entry.get("status", {})
                if status.get("status_str") == "error":
                    raise ComfyExecutionError(*describe_comfy_error(status))
                return entry
            time.sleep(POLL_INTERVAL)

    def save_output_video(self, history_entry, save_path):
        """Pull the produced video over /view — independent of ComfyUI's output subfolder layout.
        The extension filter is what keeps SaveImage's png out of Drive."""
        for node_output in history_entry.get("outputs", {}).values():
            for key in ("gifs", "videos", "images"):
                for item in node_output.get(key, []):
                    if not item.get("filename", "").lower().endswith((".mp4", ".webm", ".mov")):
                        continue
                    r = requests.get(f"{self.base}/view", timeout=300, params={
                        "filename":  item["filename"],
                        "subfolder": item.get("subfolder", ""),
                        "type":      item.get("type", "output"),
                    })
                    r.raise_for_status()
                    with open(save_path, "wb") as f:
                        f.write(r.content)
                    return
        raise RuntimeError("history'de video çıktısı yok:\n"
                           + json.dumps(history_entry.get("outputs", {}), indent=2, ensure_ascii=False))

# === One render, end to end ===
def generate(prompt, image_name, seed=None):
    """Image + prompt -> queue -> wait -> Drive. Returns the saved path."""
    seed = random.randint(0, 2**31 - 1) if seed is None else seed
    save_path = os.path.join(OUTPUT_DIR, f"{time.strftime('%Y%m%d_%H%M%S')}.mp4")

    workflow = load_workflow(WORKFLOW_PATH)
    set_image(workflow, image_name)
    set_prompt(workflow, prompt)
    set_seed(workflow, seed)

    client = ComfyClient(COMFYUI_URL)
    log(f"seed={seed}  |  görsel={image_name}  |  {prompt[:50]}{'…' if len(prompt) > 50 else ''}")
    t0 = time.time()
    prompt_id = client.submit(workflow)
    log(f"kuyrukta: {prompt_id}")

    try:
        history = client.wait(prompt_id, TIMEOUT_PER_RENDER)
    except ComfyExecutionError as e:
        print(e.text)
        print(e.traceback_text)
        raise RuntimeError("Üretim başarısız — yukarıdaki ComfyUI hatasına bak") from None

    client.save_output_video(history, save_path)
    # ComfyUI's own copies (video + last-frame png) are dropped so a long session does not fill
    # the Colab disk.
    for rel in produced_files(history):
        local = os.path.join(COMFY_OUTPUT_DIR, rel)
        if os.path.exists(local):
            os.remove(local)

    size_mb = os.path.getsize(save_path) / 1024**2
    log(f"bitti ({time.time() - t0:.0f}s, {size_mb:.1f} MB) → {save_path}", "OK")
    return save_path

video_path = generate(PROMPT, IMAGE_NAME, SEED)
```

- [ ] **Step 4: Hücre 11 (markdown, üret) — I2V metnine çevir**

```markdown
## 7) Üret

**Tekrar çalıştırılacak hücre bu.** Yeni prompt için CONFIG'deki `PROMPT`'u değiştir ve buraya dön — kurulumu ve görsel yüklemeyi tekrarlamaya gerek yok. **Başka bir görsel** için önce 6. hücreyi tekrar çalıştır.

Grafiğe yazılan üç alan: LoadImage **287** (yüklediğin görsel), PromptGenerator **233:240** (prompt + seed), Seed **210**. LoRA'lar, ağırlıklar, çözünürlük, step, cfg — hepsi grafikten gelir, buradan değiştirilmez.

`SEED = None` ise her çalıştırmada rastgele seed üretilir ve **ekrana basılır**; beğendiğin çıktıyı tekrar üretmek için CONFIG'e o sayıyı yaz.

Çıktı `output/YYYYAAGG_SSDDSS.mp4` olarak Drive'a yazılır. Grafiğin son kare PNG'si Drive'a **gitmez**, Colab diskinden de silinir.
```

- [ ] **Step 5: Hücre 10'dan sonra iki yeni hücre ekle — görsel yükleme**

Önce markdown (`insert`, `cell_type: markdown`, hedef `cell-10`'un ardı):

```markdown
## 6) Görseli Yükle

Hücreyi çalıştır → dosya seçme penceresi açılır → bilgisayarından **bir** görsel seç. Görsel ComfyUI'nin `input/` klasörüne yüklenir; grafiğe yazılacak ad ComfyUI'nin döndürdüğü addır (aynı adlı dosya varsa sunucu adı değiştirebilir, o yüzden kendi tahminimizi kullanmıyoruz).

Aynı görselle birden çok video üretecekseniz bu hücreyi tekrar çalıştırmaya gerek yok — 7. hücre yeter.
```

Sonra kod (`insert`, `cell_type: code`, eklenen markdown'ın ardı):

```python
from google.colab import files
import requests

def upload_image():
    """Colab file picker -> ComfyUI's input/ folder. Returns the name the SERVER reports.

    ComfyUI may rename on collision, so its answer is the only name guaranteed to resolve; a
    locally guessed filename would silently point LoadImage at the wrong image.
    """
    picked = files.upload()
    if not picked:
        raise RuntimeError("❌ Dosya seçilmedi — hücreyi tekrar çalıştır ve bir görsel seç")
    if len(picked) > 1:
        raise RuntimeError(f"❌ {len(picked)} dosya seçildi — tek görsel yükle")

    name = next(iter(picked))
    r = requests.post(f"{COMFYUI_URL}/upload/image",
                      files={"image": (name, picked[name])},
                      data={"overwrite": "true"}, timeout=120)
    if r.status_code >= 400:
        raise RuntimeError(f"POST /upload/image -> HTTP {r.status_code}\n{r.text}")

    remote = r.json()["name"]
    log(f"görsel yüklendi: {remote} ({human(len(picked[name]))})", "OK")
    return remote

IMAGE_NAME = upload_image()
```

- [ ] **Step 6: Hücre 8 (kod, modeller) — arbuzai model listeleri**

`WAN22`/`WAN21` satırından itibaren aşağıdaki blok gelir; `fetch` / `civitai_url` / `cookie_header` / `civitai_probe` tanımları ve altındaki üç adım kardeşteki gibi **aynen kalır**. Hücre başındaki hedef klasör bloğunda `LORA` da tanımlanmalı:

```python
# === Target folders ===
COMFY = COMFY_ROOT
DIFF  = f"{COMFY}/models/diffusion_models"
LORA  = f"{COMFY}/models/loras"
for d in ["diffusion_models", "loras", "text_encoders", "vae"]:
    os.makedirs(f"{COMFY}/models/{d}", exist_ok=True)
```

```python
# === HuggingFace models (aria2c) ===
WAN22 = "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files"
WAN21 = "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files"

HF_MODELS = [
    # (url, target_dir, filename, label)
    # The exported graph has both distill LoRAs enabled in Power Lora Loader 201/200, so they have
    # to be on disk before the render -- I2V v2.0 does not have lightx2v merged.
    (f"{WAN22}/loras/wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors", LORA, "wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors", "Lightx2v I2V HIGH"),
    (f"{WAN22}/loras/wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors",  LORA, "wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors",  "Lightx2v I2V LOW"),
    # VAE: VAELoader 191 asks for 'Wan2_1_VAE_fp32.safetensors', so land the base under that name
    (f"{WAN21}/vae/wan_2.1_vae.safetensors",                          f"{COMFY}/models/vae",           "Wan2_1_VAE_fp32.safetensors",            "Wan2.1 VAE"),
    (f"{WAN21}/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors", f"{COMFY}/models/text_encoders", "umt5_xxl_fp8_e4m3fn_scaled.safetensors", "UMT5-XXL"),
]

# === Civitai gated models (curl + login cookie) ===
# Civitai serves these under its own file names; UNETLoader 197/186 ask for
# SmoothMix_I2V_v2_High/Low.safetensors and Power Lora Loader 201/200 for the Animations pair,
# so every file lands under the name the graph names.
CIVITAI_MODELS = [
    # (version_id, target_dir, filename, label)
    (2513182, DIFF, "SmoothMix_I2V_v2_High.safetensors",         "SmoothMix I2V v2 HIGH"),
    (2513186, DIFF, "SmoothMix_I2V_v2_Low.safetensors",          "SmoothMix I2V v2 LOW"),
    (2376136, LORA, "SmoothMix_Animations_XXX_High.safetensors", "SmoothMix Animations XXX HIGH"),
    (2376143, LORA, "SmoothMix_Animations_XXX_Low.safetensors",  "SmoothMix Animations XXX LOW"),
]
```

Hücrenin sonundaki özet bloğu `loras/` klasörünü de listeler:

```python
# === Summary (reaching here means everything downloaded + validated) ===
print("\n📂 diffusion_models/")
for f in sorted(glob.glob(f"{DIFF}/*.safetensors")):
    print(f"   {human(os.path.getsize(f))}  {os.path.basename(f)}")
print("📂 loras/")
for f in sorted(glob.glob(f"{LORA}/*.safetensors")):
    print(f"   {human(os.path.getsize(f))}  {os.path.basename(f)}")
log("Tüm modeller indirildi ve doğrulandı", "OK")
```

- [ ] **Step 7: Hücre 7 (markdown, modeller) — I2V metnine çevir**

```markdown
## 4) Modeller — önce gated probe, sonra indir (~36 GiB)

Gated erişim **ağır indirmeden önce** doğrulanır (ilk 1 KB): cookie ölmüşse 27 GiB'lık checkpoint indirmeye başlamadan, Civitai'nin **gerçek yanıtıyla** durur.

Bozuk/eksik inen dosyada hücre `RuntimeError` ile durur; bozuk dosya **silinmez**, inceleme için diskte kalır.

Dosyalar kaynağın kendi adıyla değil, **grafiğin istediği adla** iner: UNETLoader **197**/**186** `SmoothMix_I2V_v2_High/Low.safetensors`, VAELoader **191** `Wan2_1_VAE_fp32.safetensors`, Power Lora Loader **201**/**200** ise `wan2.2_i2v_lightx2v_...` ve `SmoothMix_Animations_XXX_...` arıyor. Ad tutmazsa render "model bulunamadı" ile düşer.

**Distill LoRA'lar iniyor** çünkü export'ta 201/200 dolu: I2V v2.0'da lightx2v checkpoint'e merge **edilmemiş**.

**İnmeyen (bilerek):** T2V checkpoint'leri, `clip_vision_h.safetensors`, MMAudio dosyaları — API grafiğinde hiçbiri yok.
```

- [ ] **Step 8: Hücre 5 (markdown, custom node'lar) — tek cümleyi düzelt**

```markdown
## 3) ComfyUI + Custom Node'lar (16)

Liste `manual.ipynb` ile birebir aynı — API grafiği aynı grafiğin IMAGE2VIDEO grubunun export'u, dolayısıyla aynı node class'larına ihtiyacı var.

Biri başarısız olursa hücre `RuntimeError` ile durur (fail-loud); eksik node ileride "node not found" olarak karşımıza çıkmaz.
```

- [ ] **Step 9: Hücre 2 (kod, CONFIG) — I2V sürümü**

```python
# === Google Drive — en başta mount edilir ===
# Auth istemi ilk saniyede çıksın: 36 GiB'lık model indirmesinin ortasında beklemesin.
from google.colab import drive
drive.mount('/content/drive')

# === Prompt + seed — değiştirip 7. hücreyi tekrar çalıştır ===
# Üç tırnak: video prompt'ları çok satırlı olur ve içlerinde " geçer; tek tırnak ikisinde de
# "unterminated string literal" verir.
PROMPT = """
"""
SEED   = None                # None -> her çalıştırmada rastgele üretilir ve ekrana basılır

# === Drive ===
DRIVE_ROOT        = "/content/drive/MyDrive/imageToVideoV2"
WORKFLOW_FILENAME = "workflow_api.json"      # DRIVE_ROOT altında, API format

# === Civitai login-gated download ===
# civitai.red -> log in -> F12 -> Application -> Cookies -> __Secure-civ-token değerini yapıştır
# (çift tıkla -> Ctrl+A -> Ctrl+C; tek tık hücreyi kırpar ve `assert len>200` yine geçer).
# NOTE: auth moved to auth.civitai.com -> the cookie NAME is __Secure-civ-token (NOT the old
#   __Secure-civitai-token) and the value is a short ES256 JWT (~420 chars), not the old long JWE.
# Cookie only; never a ?token= API key -> gated assets answer 401.
COOKIE_VALUE = "eyJhbGciOiJFUzI1NiIsImtpZCI6ImNpdml0YWktZGV2LTIwMjYtMDYtZWMiLCJ0eXAiOiJKV1QifQ.eyJzaWduZWRBdCI6MTc4MjY0Mjc0NjMwMywic3ViIjoiMTE0OTgwOTgiLCJpYXQiOjE3ODI2NDI3NDYsImV4cCI6MTc4NTIzNDc0NiwianRpIjoiNmFkMTcxNTktNWJiMy00YTQ2LWEzYzctYjFjNjRmYzUxMzU4IiwiaXNzIjoiaHR0cHM6Ly9hdXRoLmNpdml0YWkuY29tIn0.FnTlCXmO4fkKXl3nDikNE1VeGGOlNYcmpMcv1bJl4MdazltlcnUVYyluJK9qT68QM_1kuzs6guhpsalRKU9frQ"

# === Render ===
TIMEOUT_PER_RENDER = 30 * 60   # saniye — bu süre içinde bitmezse fail-loud
POLL_INTERVAL      = 5         # saniye — /history yoklama aralığı

# === Derived paths ===
COMFY_PORT       = 8188
COMFYUI_URL      = f"http://127.0.0.1:{COMFY_PORT}"
WORKFLOW_PATH    = f"{DRIVE_ROOT}/{WORKFLOW_FILENAME}"
OUTPUT_DIR       = f"{DRIVE_ROOT}/output"

COMFY_ROOT       = "/content/ComfyUI"
COMFY_OUTPUT_DIR = f"{COMFY_ROOT}/output"
COMFY_LOG        = "/content/comfyui.log"

import os
os.makedirs(OUTPUT_DIR, exist_ok=True)
assert len(COOKIE_VALUE) > 200, "❌ COOKIE_VALUE boş/çok kısa — civitai.red'den __Secure-civ-token (ES256 JWT) yapıştır"
assert os.path.exists(WORKFLOW_PATH), f"❌ Workflow yok: {WORKFLOW_PATH} — manual.ipynb'de 'Workflow → Export (API)' ile kaydedip Drive'a koy"
assert PROMPT.strip(), "❌ PROMPT boş — yukarıya prompt'unu yaz"

print(f"✓ Drive: {DRIVE_ROOT}")
print(f"✓ Cookie: {len(COOKIE_VALUE)} char  |  Timeout: {TIMEOUT_PER_RENDER // 60} dk")
print(f"✓ Seed: {SEED if SEED is not None else 'her çalıştırmada rastgele'}")
print(f"✓ Prompt: {PROMPT[:70]}{'…' if len(PROMPT) > 70 else ''}")
print("=== GPU ===")
!nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
```

- [ ] **Step 10: Hücre 0 (markdown, başlık) — I2V sürümü**

```markdown
# WAN 2.2 arbuzai I2V — API (görsel + prompt gir, video al) — Colab

Görsel yükle, prompt yaz, çalıştır → video Drive'a düşer. ComfyUI arka planda **API** olarak çalışır; **UI açılmaz, tünel yok.**

> Grafiği elle kurcalamak, LoRA/ayar denemek istiyorsan bu değil — **`manual.ipynb`**. O ComfyUI'yi tünelle açar.

**Input:** `PROMPT` (CONFIG) + elle yüklenen görsel + `workflow_api.json` (Drive) · **Output:** `MyDrive/imageToVideoV2/output/YYYYAAGG_SSDDSS.mp4`

```
imageToVideoV2/             ← Drive'da senin oluşturacağın klasör
├── workflow_api.json   ← manual.ipynb'de Export (API) ile kaydettiğin graf
└── output/             ← üretilen videolar, zaman damgalı (otomatik oluşur)
```

Sıra:
1. **CONFIG** — Drive mount + prompt
2. **Ortak Yardımcılar** — log + fail-loud run + model doğrulama
3. **ComfyUI + custom node'lar** (16)
4. **Modeller** — önce gated probe, sonra indir (~36 GiB)
5. **ComfyUI'yi başlat** (arka planda, API)
6. **Görseli yükle** — dosya seçme penceresi
7. **Üret** — kuyruğa at, videoyu Drive'a yaz

> **Yeni prompt için:** CONFIG'deki `PROMPT`'u değiştir ve **sadece 7. hücreyi** tekrar çalıştır. Yeni görsel için önce 6. hücre.

> **LoRA'lar grafikte.** Ağırlıkları `manual.ipynb` + UI'da ayarlayıp **Export (API)** ile dondurursun; bu notebook onlara dokunmaz, yalnız görsel/prompt/seed yazar.
```

- [ ] **Step 11: Notebook geçerli JSON mu — doğrula**

```powershell
Get-Content collab-toolbox\video_generator\wan22-arbuzai\api.ipynb -Raw | ConvertFrom-Json | Select-Object -ExpandProperty cells | Measure-Object | Select-Object Count
```

Beklenen: `Count : 15` (13 + eklenen iki hücre).

- [ ] **Step 12: T2V kalıntısı kalmadı mı**

Grep (`output_mode: content`) `collab-toolbox/video_generator/wan22-arbuzai/api.ipynb` üzerinde:

```
SmoothMix_T2V|2768924|2768944|TextToVideo|t2v_lightx2v|230:229|33\.5 GiB|Smooth T2V|TEXT2VIDEO
```

Beklenen: **0 eşleşme**.

> Node id'leri **tırnaksız** aranıyor. `.ipynb` içinde kod bir JSON string'i, yani kaynaktaki `"230:229"` dosyada `\"230:229\"` olarak duruyor — `"230:229"` desenini ararsan hiçbir zaman eşleşmez ve temiz olmayan bir notebook temiz raporlanır.

- [ ] **Step 13: I2V tarafı yerinde mi**

Grep (`output_mode: content`, `-o`) aynı dosyada:

```
IMAGE_NODE|PROMPT_NODE|SEED_NODE|233:240|imageToVideoV2|upload_image|set_image|produced_files|2513182|2376136
```

Beklenen, her biri en az 1 kez: `IMAGE_NODE` · `PROMPT_NODE` · `SEED_NODE` · `233:240` · `imageToVideoV2` · `upload_image` · `set_image` · `produced_files` · `2513182` · `2376136`. Biri hiç çıkmıyorsa o adım eksik uygulanmış.

Ayrıca `SEED_NODE` satırının değeri **210** olmalı, kardeşten gelen 82 değil — Read ile üret hücresine bakıp teyit et.

- [ ] **Step 14: Commit (kullanıcı söyleyince)**

```bash
git add collab-toolbox/video_generator/wan22-arbuzai/api.ipynb
git commit -F- <<'EOF'
feat(wan22-arbuzai): render through the API, no UI

Copied from wan22-smooth-t2v/api.ipynb: the client, the /history poll, the
/view download and describe_comfy_error are the versions already proven there.
What changed is what this graph needs -- an image, and four models the T2V graph
does not use.

The notebook writes three fields and nothing else: LoadImage 287, PromptGenerator
233:240 and Seed 210. LoRAs, weights, resolution, steps and cfg stay in the graph,
set by hand in manual.ipynb and frozen through Workflow → Export (API). That
keeps this file out of rgthree's Power Lora Loader widget format.

Seed 210 arrives as -1 in the export. rgthree randomises in the frontend widget,
which does not exist in API mode, so -1 would pin every render to identical
noise; a real integer is always written and printed.

The image goes up through /upload/image and the graph gets the name the SERVER
returns -- ComfyUI renames on collision, and a locally guessed name would point
LoadImage at the wrong file. The graph also saves a last-frame png; the
extension filter keeps it out of Drive and both files are cleared off the Colab
disk after each render.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF
git show --stat --name-only HEAD
```

Beklenen: tek dosya — `collab-toolbox/video_generator/wan22-arbuzai/api.ipynb`.

---

## Uygulama sırasında değişen

Görsel alma tek hücre olarak planlanmıştı (bölüm 6: seç + gönder). Kullanıcı uygulama sırasında haklı bir itiraz getirdi: o hâliyle dosya seçme penceresi ~40 dakikalık model indirmesinin **sonrasında** açılıyor, yani görsel seçilmediyse run orada patlıyor. İkiye bölündü:

- **1. bölüm, CONFIG'in hemen altı** — `files.upload()` ile dosya seçilir, `/content/<ad>` olarak diske yazılır, `IMAGE_LOCAL` tanımlanır. `human()` henüz tanımlı değil (2. bölüm), boyut satır içinde biçimlendirilir.
- **6. bölüm** — `upload_image(IMAGE_LOCAL)` dosyayı `/upload/image`'a gönderir ve **sunucunun döndürdüğü** adı `IMAGE_NAME`'e koyar. Bu adım burada kalmak zorunda: endpoint ComfyUI ayakta olmadan çalışmıyor.

Notebook 15 değil **16 hücre**. Bölüm numaraları değişmedi.

## Doğrulama — kullanıcı elle yapar (Colab)

Yerelde çalıştırılamaz (A100 + `/content` + Drive). Kabul kriteri: **UI hiç açılmadan Drive'a doğru bir mp4 düşer.**

1. Drive'da `MyDrive/imageToVideoV2/` oluştur, `workflow_api.json`'u içine koy.
2. `api.ipynb`'yi Colab'a yükle, A100 seç, CONFIG'e prompt yaz, **Run all**.
3. Gated probe 4 asset için geçer, modeller iner, ComfyUI 90 sn içinde ayağa kalkar.
4. 6. hücrede dosya seçme penceresi açılır, görsel seçilir, "görsel yüklendi: ..." basılır.
5. 7. hücre seed'i basar, kuyruk id'sini basar, biter → `output/YYYYAAGG_SSDDSS.mp4` Drive'da.
6. Video, `manual.ipynb` + UI ile aynı ayarlardan çıkana benzer (LoRA'lar grafikten geldiği için aynı olmalı).
7. `SEED`'i sabit bir sayıya çekip iki kez çalıştır → **aynı** video. Sonra değiştir → **farklı** video. (Spec risk 2'nin testi: `-1` tuzağı gerçekten kapanmış mı.)
8. Drive'da PNG **yok**; `/content/ComfyUI/output/` altında artık dosya kalmamış.

Çıkan her gözlem spec'in "Riskler / açık uçlar" bölümüne işlenir — tahmin değil, run'da ne olduysa o.
