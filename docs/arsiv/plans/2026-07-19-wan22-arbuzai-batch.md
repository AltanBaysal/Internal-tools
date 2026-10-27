# WAN 2.2 arbuzai I2V — batch üretim Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `api.ipynb`'yi yerinde batch'e çevir — Drive'daki `input/N.<ext>` fotolarını CONFIG'deki `PROMPTS[N]` ile eşleştirip her biri için `output/N.mp4` üret, var olanı atla.

**Architecture:** Notebook'un kurulum yarısı (yardımcılar, custom node'lar, modeller, ComfyUI başlatma) hiç değişmez. Dosya seçici hücresi **plan hücresine** dönüşür: `input/` taranır, eşleşme tablosu indirmeden önce basılır. Üretim hücresi tek render yerine `process_all()` döngüsü çalıştırır; `/upload/image` döngünün içine iner çünkü her fotoğrafın kendi sırası vardır.

**Tech Stack:** Jupyter (Colab), ComfyUI HTTP API (`/prompt`, `/history`, `/view`, `/upload/image`), `requests`, Google Drive.

**Kaynak spec:** [2026-07-19-wan22-arbuzai-batch-design.md](../specs/2026-07-19-wan22-arbuzai-batch-design.md)

## Global Constraints

- **Commit yalnız kullanıcı söyleyince.** Sıra: değişiklikleri yaz → doğrula → **stage'le ve ne stage'lendiğini göster** → kullanıcı onaylayınca commit. Commit mesajı kısa tutulur (tek satır + `Co-Authored-By`), uzun gövde yazılmaz.
- **`git add`'e her zaman açık dosya yolu.** `git add .` / `git add -A` **yasak**.
- **Paralel oturum var:** `CLAUDE.md`, `instructions.md` ve `wan22-smooth-t2v/` altındaki dosyalar başka bir oturumca düzenleniyor — **hiçbirine dokunulmaz**, `git commit --amend` kullanılmaz. `git mv`/`git add` index'i paylaştığı için gereksiz staging yapılmaz.
- **Python çalıştırılmaz.** Dosya incelemek Read/Grep; JSON doğrulaması PowerShell `ConvertFrom-Json`.
- **Dil:** notebook markdown hücreleri ve runtime çıktısı (`print`/`log`/`assert`/`RuntimeError`) **Türkçe**; kod yorumları ve docstring'ler **İngilizce**.
- **Yorum kuralı:** yorum WHY anlatır; `# OLD:` / `# NEW:` yok, yorum kodun **şu anki** halini anlatır.
- **Grafiğe yazılan tek üç alan:** LoadImage `287`, PromptGenerator `233:240` (prompt + seed), Seed `210`. LoRA, ağırlık, çözünürlük, step, cfg — **dokunulmaz**.
- **`workflow_api.json` ve `workflow_manual.json` değişmez.**
- **Dokunulmayan hücreler:** 2) Ortak Yardımcılar md+kod, 3) Custom node'lar md+kod, 4) Modeller md+kod, 5) ComfyUI'yi başlat md+kod. Bunlar `COMFY_ROOT` üzerinden CONFIG'e bağlı (`assert "COMFY_ROOT" in globals()`), o yüzden CONFIG hücresi `COMFY_ROOT`'u tanımlamayı **sürdürmek zorunda**.
- **Kapsam dışı:** foto başına N render, seed listesi, prompt'ları Drive dosyasından okuma, paralel üretim, dosya seçici akışının korunması, `instructions.md`, `CLAUDE.md`.

## Dosya yapısı

Tek dosya değişir: `collab-toolbox/video_generator/wan22-arbuzai/api.ipynb`.

Başlangıç: **16 hücre**. Bitiş: **14 hücre** (dosya seçici → plan hücresine dönüşür; ayrı yükleme md+kod çifti silinir, işi üretim döngüsüne geçer).

| # | Hücre | Durum |
|---|---|---|
| 0 | Başlık (md) | değişir |
| 1 | `1) CONFIG` (md) | değişir |
| 2 | CONFIG (kod) | değişir |
| 3 | **Plan** (kod) | dosya seçicinin yerine yazılır |
| 4-5 | `2) Ortak Yardımcılar` md+kod | dokunulmaz |
| 6-7 | `3) Custom Node'lar` md+kod | dokunulmaz |
| 8-9 | `4) Modeller` md+kod | dokunulmaz |
| 10-11 | `5) ComfyUI'yi Başlat` md+kod | dokunulmaz |
| 12-13 | `6) Görseli ComfyUI'ya Yükle` md+kod | **silinir** |
| 14-15 | `7) Üret` md+kod | `6) Üret` olur, batch döngüsü gelir |

---

### Task 1: Planlama yarısı — CONFIG + eşleşme tablosu

Bu task tek başına test edilebilir: Run all'ı 3. hücrede durdurup tabloyu görebilirsin, tek bayt model inmeden.

**Files:**
- Modify: `collab-toolbox/video_generator/wan22-arbuzai/api.ipynb` (hücre 3, 2, 1, 0)

**Interfaces:**
- Produces: `PROMPTS: list[str]` · `INPUT_DIR: str` · `PLAN: list[tuple[int, str, str | None, str, str]]` — satır başına `(n, action, image_path, prompt, reason)`, `action` ∈ `{"ÜRET", "ATLA"}`. Task 2 yalnız `PLAN`'ı ve `OUTPUT_DIR`'ı tüketir.

Hücreler **aşağıdan yukarı** düzenlenir (3 → 2 → 1 → 0). Bu task ekleme/silme yapmadığı için index'ler kaymaz.

- [ ] **Step 1: Hücre 3 (dosya seçici) → plan hücresi**

Dosya seçici tamamen gider; yerine bu gelir:

```python
# === Üretim planı — indirmeden önce, bilerek ===
# loop_maker's rule: decide the whole run before a GPU minute is spent. A short PROMPTS list or a
# missing photo shows up here, not after ~40 minutes of model downloads.
# log()/human() belong to section 2 and are not defined yet, so this cell prints plainly.
import os, glob

IMAGE_EXTS = ("png", "jpg", "jpeg", "webp")

def scan_images():
    """input/ -> {number: [paths]}. Extension case is ignored on purpose: phone cameras write
    .JPG, and Colab's filesystem is case-sensitive, so a literal '<n>.jpg' match would report a
    photo that is sitting right there as missing."""
    found = {}
    for path in glob.glob(f"{INPUT_DIR}/*"):
        stem, ext = os.path.splitext(os.path.basename(path))
        if stem.isdigit() and ext[1:].lower() in IMAGE_EXTS:
            found.setdefault(int(stem), []).append(path)
    return found

IMAGES = scan_images()

def find_image(n):
    """One path or None. Two files sharing a number is an error, never a guess."""
    hits = IMAGES.get(n, [])
    if len(hits) > 1:
        names = sorted(os.path.basename(h) for h in hits)
        raise RuntimeError(f"❌ {n} numarası için birden fazla dosya: {names} — birini sil")
    return hits[0] if hits else None

def build_plan(prompts):
    """One row per prompt index -> (n, action, image_path, prompt, reason).

    An empty prompt is a deliberate 'skip this number' switch: PROMPTS is a flat list, so blanking
    an entry is the only way to disable one number without shifting every number after it.
    """
    rows = []
    for n, prompt in enumerate(prompts):
        image = find_image(n)
        out = f"{OUTPUT_DIR}/{n}.mp4"
        if not prompt.strip():
            rows.append((n, "ATLA", None, "", "prompt boş"))
        elif image is None:
            rows.append((n, "ATLA", None, prompt, f"fotoğraf yok (input/{n}.*)"))
        elif os.path.exists(out) and os.path.getsize(out) > 0:
            rows.append((n, "ATLA", image, prompt, "çıktı zaten var"))
        else:
            rows.append((n, "ÜRET", image, prompt, ""))
    return rows

def images_without_prompt(prompts):
    """Numbered photos past the end of PROMPTS. A flat list has no holes, so running off its end
    is the only way a photo can lack a prompt."""
    return sorted(os.path.basename(p)
                  for n, paths in IMAGES.items() if n >= len(prompts)
                  for p in paths)

PLAN = build_plan(PROMPTS)

print(f"\n{'#':>3}  {'KARAR':<6}  {'FOTOĞRAF':<16}  AÇIKLAMA")
print("-" * 72)
for n, action, image, prompt, reason in PLAN:
    name = os.path.basename(image) if image else "—"
    detail = reason if reason else prompt.strip().replace("\n", " ")[:34]
    print(f"{n:>3}  {action:<6}  {name:<16}  {detail}")

for name in images_without_prompt(PROMPTS):
    print(f"  ⚠️  {name} atlandı — PROMPTS listesinde o numara yok ({len(PROMPTS)} prompt var)")

_to_render = sum(1 for r in PLAN if r[1] == "ÜRET")
print("-" * 72)
print(f"Üretilecek: {_to_render}  |  Atlanacak: {len(PLAN) - _to_render}")

if _to_render == 0:
    raise RuntimeError("❌ Üretilecek video yok — yukarıdaki tabloya bak (foto eksik, prompt boş ya da hepsi zaten üretilmiş)")
```

- [ ] **Step 2: Hücre 2 (CONFIG kod) — `PROMPT` → `PROMPTS`, `INPUT_DIR` eklenir**

```python
# === Google Drive — en başta mount edilir ===
# Auth istemi ilk saniyede çıksın: 36 GiB'lık model indirmesinin ortasında beklemesin.
from google.colab import drive
drive.mount('/content/drive')

# === Prompt listesi — index = fotoğraf numarası (PROMPTS[0] -> input/0.*) ===
# Üç tırnak: video prompt'ları çok satırlı olur ve içlerinde " geçer; tek tırnak ikisinde de
# "unterminated string literal" verir.
# Boş bırakılan bir madde ("") o numarayı atlar -- listeyi kaydırmadan tek numarayı kapatmanın yolu.
PROMPTS = [
    """
    """,
]
SEED = None                  # None -> her video için ayrı rastgele seed; sayı verirsen hepsinde o

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
TIMEOUT_PER_RENDER = 30 * 60   # saniye — bir video bu sürede bitmezse fail-loud
POLL_INTERVAL      = 5         # saniye — /history yoklama aralığı

# === Derived paths ===
COMFY_PORT       = 8188
COMFYUI_URL      = f"http://127.0.0.1:{COMFY_PORT}"
WORKFLOW_PATH    = f"{DRIVE_ROOT}/{WORKFLOW_FILENAME}"
INPUT_DIR        = f"{DRIVE_ROOT}/input"
OUTPUT_DIR       = f"{DRIVE_ROOT}/output"

COMFY_ROOT       = "/content/ComfyUI"
COMFY_OUTPUT_DIR = f"{COMFY_ROOT}/output"
COMFY_LOG        = "/content/comfyui.log"

import os
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
assert len(COOKIE_VALUE) > 200, "❌ COOKIE_VALUE boş/çok kısa — civitai.red'den __Secure-civ-token (ES256 JWT) yapıştır"
assert os.path.exists(WORKFLOW_PATH), f"❌ Workflow yok: {WORKFLOW_PATH} — manual.ipynb'de 'Workflow → Export (API)' ile kaydedip Drive'a koy"
assert any(p.strip() for p in PROMPTS), "❌ PROMPTS'ta dolu tek bir prompt yok — yukarıya prompt'larını yaz"

print(f"✓ Drive: {DRIVE_ROOT}")
print(f"✓ Cookie: {len(COOKIE_VALUE)} char  |  Timeout: {TIMEOUT_PER_RENDER // 60} dk/video")
print(f"✓ Seed: {SEED if SEED is not None else 'video başına rastgele'}")
print(f"✓ {len(PROMPTS)} prompt ({sum(1 for p in PROMPTS if not p.strip())} tanesi boş — atlanacak)")
print("=== GPU ===")
!nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
```

- [ ] **Step 3: Hücre 1 (`1) CONFIG` md)**

```markdown
## 1) CONFIG

Google Drive **burada** mount edilir: auth istemi ilk saniyede çıksın, 36 GiB'lık model indirmesinin ortasında seni beklemesin.

Doldurulacak yer `PROMPTS` — **liste sırası fotoğraf numarasıdır**: `PROMPTS[0]` → `input/0.*`, `PROMPTS[1]` → `input/1.*`. Her prompt üç tırnağın arasına yazılır; çok satırlı olabilir, içinde `"` geçebilir.

Bir numarayı bu turda üretmek istemiyorsan prompt'unu **boş bırak** (`""`) — liste kaymaz, o numara atlanır.

Hemen alttaki hücre `input/` klasörünü tarayıp **üretim planını basar**: hangi numara üretilecek, hangisi neden atlanacak. Tablo indirmeden önce çıkar, yani yanlış eşleşmeyi 40 dakika sonra değil ilk saniyelerde görürsün.

Cookie'nin süresi dolmuşsa (~30 gün) `civitai.red`'den yenile.
```

- [ ] **Step 4: Hücre 0 (başlık md)**

```markdown
# WAN 2.2 arbuzai I2V — Batch API (numaralı fotolar + prompt listesi) — Colab

Drive'a numaralı fotoları koy, CONFIG'e prompt listesini yaz, çalıştır → her eşleşme için bir video Drive'a düşer. ComfyUI arka planda **API** olarak çalışır; **UI açılmaz, tünel yok.**

> Grafiği elle kurcalamak, LoRA/ayar denemek istiyorsan bu değil — **`manual.ipynb`**. O ComfyUI'yi tünelle açar.

```
imageToVideoV2/             ← Drive'da senin oluşturacağın klasör
├── workflow_api.json   ← manual.ipynb'de Export (API) ile kaydettiğin graf
├── input/              ← 0.png, 1.jpg, 2.png … (numara = eşleşme anahtarı)
└── output/             ← 0.mp4, 1.mp4 … (otomatik oluşur)
```

**Eşleşme:** `PROMPTS[0]` ↔ `input/0.*` ↔ `output/0.mp4`. Uzantı serbest (png/jpg/jpeg/webp).

Sıra:
1. **CONFIG** — Drive mount + prompt listesi · ardından **üretim planı** basılır
2. **Ortak Yardımcılar** — log + fail-loud run + model doğrulama
3. **ComfyUI + custom node'lar** (16)
4. **Modeller** — önce gated probe, sonra indir (~36 GiB)
5. **ComfyUI'yi başlat** (arka planda, API)
6. **Üret** — sırayla her fotoğraf: yükle, render et, Drive'a yaz

> **Yarıda kalırsa baştan çalıştır.** Çıktısı olan numaralar atlanır, kalanlar üretilir. Bir videoyu yeniden üretmek için Drive'dan `output/N.mp4`'ü sil.

> **Girdilerin hepsi indirmeden önce belli** — Drive izni, prompt listesi, fotoğraflar. Uzun indirme başladıktan sonra hiçbir şey sorulmaz.

> **LoRA'lar grafikte.** Ağırlıkları `manual.ipynb` + UI'da ayarlayıp **Export (API)** ile dondurursun; bu notebook onlara dokunmaz, yalnız fotoğraf/prompt/seed yazar.
```

- [ ] **Step 5: JSON hâlâ geçerli mi**

```powershell
Get-Content collab-toolbox\video_generator\wan22-arbuzai\api.ipynb -Raw | ConvertFrom-Json | Select-Object -ExpandProperty cells | Measure-Object | Select-Object Count
```

Beklenen: `Count : 16` (bu task hücre eklemez/silmez).

- [ ] **Step 6: Dosya seçici gitti mi, plan geldi mi**

Grep (`output_mode: content`, `-o`) `collab-toolbox/video_generator/wan22-arbuzai/api.ipynb`:

```
files\.upload|IMAGE_LOCAL|build_plan|images_without_prompt|PROMPTS|INPUT_DIR|PLAN = build_plan
```

Beklenen: `files.upload` ve `IMAGE_LOCAL` → **0 eşleşme** · `build_plan`, `images_without_prompt`, `PLAN = build_plan`, `PROMPTS`, `INPUT_DIR` → en az 1'er eşleşme.

> Not: bu adımda `IMAGE_LOCAL` hâlâ 13. hücrede (`upload_image(IMAGE_LOCAL)`) geçiyor olabilir — o hücre Task 2'de siliniyor. Eşleşme çıkarsa **yalnız 13. hücrede** olduğunu Read ile doğrula, başka yerde çıkarsa Step 1 eksik uygulanmış.

---

### Task 2: Üretim döngüsü

**Files:**
- Modify: `collab-toolbox/video_generator/wan22-arbuzai/api.ipynb` (hücre 15, 14; hücre 13 ve 12 silinir)

**Interfaces:**
- Consumes: Task 1'in `PLAN` listesi, `OUTPUT_DIR`, `SEED`, `TIMEOUT_PER_RENDER`, `POLL_INTERVAL`; 2. bölümün `log` / `human` / `describe_comfy_error`'ı.
- Produces: `output/<n>.mp4` dosyaları; `process_all(plan)` ekrana özet basar.

Sıra: **önce 15, sonra 14, sonra 13 sil, sonra 12 sil.** Sondan silmek öndeki index'leri kaydırmaz.

- [ ] **Step 1: Hücre 15 (üret kod) — batch döngüsü**

```python
import json, os, random, time, uuid, requests

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

MAX_CONSECUTIVE_FAILURES = 3   # a batch that keeps failing is broken, not unlucky

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
    not exist in API mode -- sending -1 through would pin every render to the same noise.
    """
    workflow[SEED_NODE]["inputs"]["seed"] = seed
    workflow[PROMPT_NODE]["inputs"]["seed"] = seed

def produced_files(history_entry):
    """Every file this prompt wrote, as ComfyUI-relative paths.

    The graph has two savers: VHS_VideoCombine (mp4) and SaveImage (last frame png). Only the
    video goes to Drive, but both are cleared off the Colab disk so a long batch does not fill it.
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

    def upload_image(self, local_path):
        """Push one image into ComfyUI's input/ folder. Returns the name the SERVER reports.

        ComfyUI may rename on collision, so its answer is the only name guaranteed to resolve; a
        locally guessed filename would silently point LoadImage at the wrong image.
        """
        name = os.path.basename(local_path)
        with open(local_path, "rb") as f:
            r = requests.post(f"{self.base}/upload/image",
                              files={"image": (name, f)},
                              data={"overwrite": "true"}, timeout=120)
        if r.status_code >= 400:
            raise RuntimeError(f"POST /upload/image -> HTTP {r.status_code}\n{r.text}")
        return r.json()["name"]

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

# === One image, end to end ===
def generate_one(client, n, image_path, prompt, seed):
    """One photo + prompt -> output/<n>.mp4. Returns the saved path."""
    save_path = f"{OUTPUT_DIR}/{n}.mp4"
    image_name = client.upload_image(image_path)

    workflow = load_workflow(WORKFLOW_PATH)
    set_image(workflow, image_name)
    set_prompt(workflow, prompt)
    set_seed(workflow, seed)

    prompt_id = client.submit(workflow)
    history = client.wait(prompt_id, TIMEOUT_PER_RENDER)
    client.save_output_video(history, save_path)

    for rel in produced_files(history):
        local = os.path.join(COMFY_OUTPUT_DIR, rel)
        if os.path.exists(local):
            os.remove(local)
    return save_path

# === The batch ===
def process_all(plan):
    """Render every ÜRET row in order. Skips, failures and the reason for each are printed.

    A loader failure stops the batch: the model is broken or missing, so every remaining video
    would hit the identical error. A video-specific failure only costs that video.
    """
    todo = [row for row in plan if row[1] == "ÜRET"]
    client = ComfyClient(COMFYUI_URL)
    done = skipped = failed = 0
    consecutive = 0
    t_batch = time.time()

    log(f"Batch başlıyor — {len(todo)} video")
    for n, _action, image_path, prompt, _reason in todo:
        out = f"{OUTPUT_DIR}/{n}.mp4"
        # Re-check the disk: an earlier run of this cell may have produced it already.
        if os.path.exists(out) and os.path.getsize(out) > 0:
            log(f"{n}: zaten var — atlandı")
            skipped += 1
            continue

        seed = random.randint(0, 2**31 - 1) if SEED is None else SEED
        log(f"{n}: {os.path.basename(image_path)}  seed={seed}  |  "
            f"{prompt.strip()[:45]}{'…' if len(prompt.strip()) > 45 else ''}")
        t0 = time.time()
        try:
            path = generate_one(client, n, image_path, prompt, seed)
        except ComfyExecutionError as e:
            print(e.text)
            print(e.traceback_text)
            if e.infra:
                raise RuntimeError(
                    f"Altyapı hatası ({e.text.splitlines()[0]}) — batch durduruldu, kalan videolar denenmedi"
                ) from None
            failed += 1
            consecutive += 1
            log(f"{n}: başarısız — atlanıyor ({consecutive}/{MAX_CONSECUTIVE_FAILURES})", "ERR")
            if consecutive >= MAX_CONSECUTIVE_FAILURES:
                raise RuntimeError(f"Üst üste {consecutive} video başarısız — batch durduruldu") from None
            continue

        consecutive = 0
        done += 1
        log(f"{n}: bitti ({time.time() - t0:.0f}s, {os.path.getsize(path) / 1024**2:.1f} MB) → {path}", "OK")

    log(f"Batch bitti ({(time.time() - t_batch) / 60:.0f} dk) — "
        f"üretildi: {done}, atlandı: {skipped}, başarısız: {failed}", "OK")

process_all(PLAN)
```

- [ ] **Step 2: Hücre 14 (üret md) — `7) Üret` → `6) Üret`**

```markdown
## 6) Üret

Plan tablosunda **ÜRET** yazan her numara sırayla işlenir: fotoğraf ComfyUI'ya yüklenir, render edilir, `output/N.mp4` olarak Drive'a yazılır, ComfyUI'daki kopyalar silinir.

Grafiğe yazılan üç alan: LoadImage **287** (o numaranın fotoğrafı), PromptGenerator **233:240** (prompt + seed), Seed **210**. LoRA'lar, ağırlıklar, çözünürlük, step, cfg — hepsi grafikten gelir.

**Yarıda kalırsa** notebook'u baştan çalıştır: çıktısı olan numaralar hem plan hücresinde hem döngü içinde atlanır, kaldığı yerden devam eder.

**Hata olursa:** model yükleyici hatası batch'i durdurur (her video aynı hatayı alırdı). Tek videoya özgü hata yalnız o videoyu atlar; üst üste 3 hata batch'i durdurur. Bir video 30 dakikada bitmezse `TimeoutError` ile durulur — kalanları üretmek için notebook'u tekrar çalıştırman yeter.

Seed her video için ayrı üretilir ve loglanır; `SEED`'e sayı verirsen hepsinde o kullanılır.
```

- [ ] **Step 3: Hücre 13 (eski yükleme kodu) silinir**

NotebookEdit, `edit_mode: delete`, `cell_id: cell-13`. İşi `ComfyClient.upload_image` devraldı.

- [ ] **Step 4: Hücre 12 (eski `6) Görseli ComfyUI'ya Yükle` md) silinir**

NotebookEdit, `edit_mode: delete`, `cell_id: cell-12`.

- [ ] **Step 5: JSON geçerli ve hücre sayısı doğru mu**

```powershell
Get-Content collab-toolbox\video_generator\wan22-arbuzai\api.ipynb -Raw | ConvertFrom-Json | Select-Object -ExpandProperty cells | Measure-Object | Select-Object Count
```

Beklenen: `Count : 14`.

- [ ] **Step 6: Tek-görsel kalıntısı kalmadı mı**

Grep (`output_mode: content`, `-o`):

```
files\.upload|IMAGE_LOCAL|IMAGE_NAME|def generate\(|7\) Üret|Görseli ComfyUI'ya Yükle
```

Beklenen: **0 eşleşme**. (`generate_one` var, `generate(` yok; `upload_image` artık `ComfyClient` metodu.)

- [ ] **Step 7: Batch tarafı yerinde mi**

Grep (`output_mode: content`, `-o`):

```
process_all|generate_one|MAX_CONSECUTIVE_FAILURES|PLAN|build_plan|INPUT_DIR|PROMPTS
```

Beklenen, her biri en az 1 kez. `process_all` ≥2 (tanım + `process_all(PLAN)` çağrısı), `generate_one` ≥2 (tanım + çağrı).

- [ ] **Step 8: Bölüm numaraları tutarlı mı**

Read ile markdown başlıklarını gözden geçir: `1) CONFIG` → `2) Ortak Yardımcılar` → `3) ComfyUI + Custom Node'lar` → `4) Modeller` → `5) ComfyUI'yi Başlat` → `6) Üret`. Atlanan/yinelenen numara olmamalı; başlık hücresindeki 6 maddelik sıra listesiyle de eşleşmeli.

- [ ] **Step 9: Stage'le ve kullanıcıya göster (commit etme)**

```bash
git add collab-toolbox/video_generator/wan22-arbuzai/api.ipynb
git diff --cached --stat
git status --short
```

Stage'de yalnız `api.ipynb` görünmeli. Kullanıcı onaylayınca:

```bash
git commit -q -F- -- collab-toolbox/video_generator/wan22-arbuzai/api.ipynb <<'EOF'
feat(wan22-arbuzai): batch üretim — numaralı fotolar + prompt listesi

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF
```

---

## Doğrulama — kullanıcı elle yapar (Colab)

Yerelde çalıştırılamaz (A100 + `/content` + Drive). Kabul kriteri: **eşleşen her fotoğraf için `output/N.mp4` üretilir, atlananlar nedeniyle loglanır.**

1. Drive'da `imageToVideoV2/input/` altına `0.png`, `1.png`, `2.png` koy; CONFIG'e 3 prompt yaz → Run all.
2. **Plan tablosu** üç satırı da `ÜRET` gösterir, "Üretilecek: 3" basar — model inmeden önce.
3. Batch biter, `output/0.mp4`, `1.mp4`, `2.mp4` Drive'da. Loglarda her video için seed görünür.
4. **Resume:** `output/1.mp4`'ü sil, notebook'u baştan çalıştır → plan tablosunda 0 ve 2 "çıktı zaten var" ile ATLA, yalnız 1 üretilir.
5. **Boş prompt:** `PROMPTS[2] = ""` yap → 2 "prompt boş" ile atlanır.
6. **Eksik foto:** `input/1.png`'i sil → 1 "fotoğraf yok" ile atlanır, diğerleri üretilir.
7. **Fazla foto:** `input/`'a `9.png` koy (listede 9. prompt yok) → `⚠️ 9.png atlandı — PROMPTS listesinde o numara yok` uyarısı çıkar, batch normal devam eder.
8. Drive'da PNG yok; `/content/ComfyUI/output/` altında artık dosya kalmamış.

Çıkan her gözlem spec'e işlenir — tahmin değil, run'da ne olduysa o.
