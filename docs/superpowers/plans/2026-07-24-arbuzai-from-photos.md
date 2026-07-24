# arbuzai I2V — foto-tanıyan batch Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `wan22-arbuzai/api_from_photos.ipynb` — `input/N_<harf>.png` (foto generator çıktısı) tanınır, `PROMPTS[N]` o numaranın tüm fotolarına uygulanır, her foto `VARIANTS` videoya döner (`N_<harf>.mp4` / `N_<harf>_<v>.mp4`).

**Architecture:** `wan22-arbuzai/api.ipynb` kopyalanır (varyantlı hâli); 6 hücre değişir (0,1,2,3,12,13), geri kalanı (yardımcılar, custom node, model, başlatma) aynen kalır. Değişen tek mantık: girdi tarayıcı (numaralı tek foto → numara+harf çoklu foto) + çıktı adlandırma. Spec: `docs/superpowers/specs/2026-07-24-arbuzai-from-photos-design.md`.

**Tech Stack:** Colab notebook (.ipynb), ComfyUI HTTP API, `re` (dosya adı deseni).

## Global Constraints

- **Dil:** notebook markdown + runtime çıktısı Türkçe; kod yorumu/docstring İngilizce.
- **Python çalıştırma yok**; inceleme Grep/Read. Komut yalnız gerekliyse gerekçesiyle (bu planda 1: ipynb kopyası — Read+Write JSON'u yeniden encode eder, `cp` birebir kopyalar).
- **Git'e hiçbir şey eklenmez** — kullanıcı Colab'da doğrulayana kadar stage/commit yok.
- **Grafik, modeller, `manual.ipynb`, `api.ipynb`, foto generator dokunulmaz.** Yalnız yeni `api_from_photos.ipynb`.
- Node id'leri değişmez: `IMAGE_NODE="287"`, `PROMPT_NODE="233:240"`, `SEED_NODE="210"`.
- Drive: paylaşımlı `imageToVideoV2` (arbuzai ile aynı); `workflow_api.json` zaten orada.
- `VARIANTS = 1` default; seed sabitse varyant `v` için `SEED + v`.
- Çıktı: `VARIANTS==1` → `N_<harf>.mp4`; `VARIANTS>1` → `N_<harf>_<v>.mp4` (v 1'den).

---

### Task 1: api_from_photos.ipynb

**Files:**
- Create: `collab-toolbox/video_generator/wan22-arbuzai/api_from_photos.ipynb` (api.ipynb kopyası + 6 hücre)

**Interfaces:**
- Consumes: `wan22-arbuzai/api.ipynb` (iskelet, varyantlı hâl). Değişmeyen fonksiyonlar: `ComfyClient` (dahil `upload_image`, `save_output_video`), `load_workflow`, `set_image/set_prompt/set_seed`, `produced_files`, `describe_comfy_error`.
- Produces: `scan_photos() -> {int: {str: [str]}}`, `find_photo(number, letter) -> str`, `out_path(number, letter, v) -> str`, `build_plan(prompts) -> [(number, letter, v, action, image_path, prompt, reason)]`, `generate_one(client, save_path, image_name, prompt, seed) -> str`, `process_all(plan)`.

- [ ] **Step 1: Kopyala** — komut gerekçesi: ipynb JSON'unu Read+Write yeniden encode eder; `cp` birebir kopyalar.

```bash
cp "collab-toolbox/video_generator/wan22-arbuzai/api.ipynb" "collab-toolbox/video_generator/wan22-arbuzai/api_from_photos.ipynb"
```

- [ ] **Step 2: Cell 0 (markdown, başlık) — replace:**

```markdown
# WAN 2.2 arbuzai I2V — Foto-tanıyan Batch API (N_a.png → video) — Colab

Foto generator'ın çıktılarını (`1_a.png, 1_b.png, …`) doğrudan videoya çevirir: beğendiğin fotoları `input/`'a kopyala, o numaranın video prompt'unu **bir kez** yaz, çalıştır. Yeniden adlandırma yok, aynı prompt'u tekrar yazma yok. ComfyUI arka planda **API** olarak çalışır; **UI açılmaz, tünel yok.**

> Numaralı tek foto (`0.png, 1.png`) ile çalışmak istiyorsan bu değil — **`api.ipynb`**. Grafiği kurcalamak istiyorsan **`manual.ipynb`**.

```
imageToVideoV2/             ← arbuzai ile paylaşılan Drive klasörü
├── workflow_api.json   ← manual.ipynb'de Export (API) ile kaydettiğin graf
├── input/              ← 1_a.png, 1_b.png, 3_c.png … (foto generator'dan kopyala)
└── output/             ← 1_a.mp4 / 1_a_1.mp4, 1_a_2.mp4 … (otomatik oluşur)
```

**Eşleşme:** `input/N_<harf>.png` → `PROMPTS[N]` (o numaranın **tüm** fotolarına aynı prompt). Uzantı serbest (png/jpg/jpeg/webp).

**Çıktı:** her foto → `VARIANTS` video (farklı seed → farklı hareket). `VARIANTS=1` → `N_<harf>.mp4`; `VARIANTS=2` → `N_<harf>_1.mp4, N_<harf>_2.mp4`.

Sıra:
1. **CONFIG** — Drive mount + prompt listesi · ardından **üretim planı** basılır
2. **Ortak Yardımcılar** — log + fail-loud run + model doğrulama
3. **ComfyUI + custom node'lar** (16)
4. **Modeller** — önce gated probe, sonra indir (~36 GiB)
5. **ComfyUI'yi başlat** (arka planda, API)
6. **Üret** — her foto × varyant: yükle, render et, Drive'a yaz

> **Yarıda kalırsa baştan çalıştır.** Çıktısı olan atlanır, kalanlar üretilir. Yeniden üretmek için Drive'dan o mp4'ü sil.

> **Video pahalı.** Her render A100'de dakikalar sürer; toplam = foto sayısı × `VARIANTS`. Default `VARIANTS=1`.

> **LoRA'lar grafikte.** `manual.ipynb` + UI'da ayarlayıp Export (API) ile dondurursun; bu notebook onlara dokunmaz, yalnız fotoğraf/prompt/seed yazar.
```

- [ ] **Step 3: Cell 1 (markdown, CONFIG intro) — replace:**

```markdown
## 1) CONFIG

Google Drive **burada** mount edilir: auth istemi ilk saniyede çıksın, 36 GiB'lık model indirmesinin ortasında seni beklemesin.

Doldurulacak yer `PROMPTS` — **liste sırası fotoğraf numarasıdır**: `PROMPTS[1]` → `input/1_*.png` (o numaranın bütün harfleri). Her prompt üç tırnağın arasına yazılır; çok satırlı olabilir, içinde `"` geçebilir.

`VARIANTS` her foto için kaç video üretileceğidir (farklı seed). Video pahalı olduğu için default 1 — yani foto başına tek video. Aynı fotodan seed varyasyonu istersen 2+ yap.

Bir numarayı bu turda üretmek istemiyorsan prompt'unu **boş bırak** (`""`) — o numaranın tüm fotoları atlanır.

Hemen alttaki hücre `input/` klasörünü tarayıp **üretim planını basar**: hangi foto/varyant üretilecek, hangisi neden atlanacak. Tablo indirmeden önce çıkar.

Cookie'nin süresi dolmuşsa (~30 gün) `civitai.red`'den yenile.
```

- [ ] **Step 4: Cell 2 (kod, CONFIG) — replace.** api.ipynb cell 2'nin kopyası; `VARIANTS=2`→`1`, `VARIANT_LETTERS` ve onun assert'i kalkar, yerine `VARIANTS>=1` assert. Tam metin:

```python
# === Google Drive — en başta mount edilir ===
# Auth istemi ilk saniyede çıksın: 36 GiB'lık model indirmesinin ortasında beklemesin.
from google.colab import drive
drive.mount('/content/drive')

# === Prompt listesi — index = fotoğraf numarası (PROMPTS[1] -> input/1_*.png) ===
# Üç tırnak: video prompt'ları çok satırlı olur ve içlerinde " geçer; tek tırnak ikisinde de
# "unterminated string literal" verir.
# Boş bırakılan bir madde ("") o numaranın tüm fotolarını atlar.
PROMPTS = [
    """
    """,
]
SEED = None                  # None -> her varyant için ayrı rastgele seed; sayı verirsen varyant v için SEED+v
VARIANTS = 1                 # foto başına kaç video (farklı seed) — video pahalı, default tek

# === Drive (arbuzai api.ipynb ile paylaşılır) ===
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
assert VARIANTS >= 1, "❌ VARIANTS en az 1 olmalı"

print(f"✓ Drive: {DRIVE_ROOT}")
print(f"✓ Cookie: {len(COOKIE_VALUE)} char  |  Timeout: {TIMEOUT_PER_RENDER // 60} dk/video")
print(f"✓ Seed: {SEED if SEED is not None else 'varyant başına rastgele'}  |  Varyant: {VARIANTS}")
print(f"✓ {len(PROMPTS)} prompt ({sum(1 for p in PROMPTS if not p.strip())} tanesi boş — atlanacak)")
print("=== GPU ===")
!nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
```

- [ ] **Step 5: Cell 3 (kod, üretim planı) — replace.** Girdi tarayıcı numara+harf desenine geçer. Tam metin:

```python
# === Üretim planı — indirmeden önce, bilerek ===
# loop_maker's rule: decide the whole run before a GPU minute is spent. A wrong filename or an
# already-complete output folder shows up here, not after ~40 minutes of model downloads.
# log()/human() belong to section 2 and are not defined yet, so this cell prints plainly.
import os, glob, re

IMAGE_EXTS = ("png", "jpg", "jpeg", "webp")
PHOTO_RE = re.compile(r"^(\d+)_([a-z]+)$", re.IGNORECASE)   # photo-generator naming: <number>_<letter>

def scan_photos():
    """input/ -> {number: {letter: [paths]}}. Recognises the photo-generator output naming
    (<number>_<letter>.<ext>). Extension case is ignored on purpose: phone cameras write .JPG and
    Colab's filesystem is case-sensitive, so a literal match would report a present photo as missing.
    Files that don't fit the pattern (e.g. a bare 0.png meant for api.ipynb) are ignored, so the two
    notebooks can share one input/ folder."""
    found = {}
    for path in glob.glob(f"{INPUT_DIR}/*"):
        stem, ext = os.path.splitext(os.path.basename(path))
        m = PHOTO_RE.match(stem)
        if m and ext[1:].lower() in IMAGE_EXTS:
            number, letter = int(m.group(1)), m.group(2).lower()
            found.setdefault(number, {}).setdefault(letter, []).append(path)
    return found

PHOTOS = scan_photos()

def find_photo(number, letter):
    """The single path for <number>_<letter>, or fail-loud if the same stem exists in two
    extensions (1_a.png + 1_a.jpg) — which one is meant is never guessed."""
    hits = PHOTOS.get(number, {}).get(letter, [])
    if len(hits) > 1:
        names = sorted(os.path.basename(h) for h in hits)
        raise RuntimeError(f"❌ {number}_{letter} için birden fazla dosya: {names} — birini sil")
    return hits[0]

def out_path(number, letter, v):
    """Output path for photo <number>_<letter>, seed-variant v (0-indexed).
    VARIANTS==1 -> no variant suffix (1_a.mp4); else 1-indexed suffix (1_a_1.mp4, 1_a_2.mp4)."""
    stem = f"{number}_{letter}"
    return f"{OUTPUT_DIR}/{stem}.mp4" if VARIANTS == 1 else f"{OUTPUT_DIR}/{stem}_{v + 1}.mp4"

def build_plan(prompts):
    """One row per (photo, seed-variant) -> (number, letter, v, action, image_path, prompt, reason).
    PROMPTS[number] is shared by every photo of that number; an empty prompt skips the number."""
    rows = []
    for number, prompt in enumerate(prompts):
        for letter in sorted(PHOTOS.get(number, {})):
            image = find_photo(number, letter)
            for v in range(VARIANTS):
                out = out_path(number, letter, v)
                if not prompt.strip():
                    rows.append((number, letter, v, "ATLA", None, "", "prompt boş"))
                elif os.path.exists(out) and os.path.getsize(out) > 0:
                    rows.append((number, letter, v, "ATLA", image, prompt, "çıktı zaten var"))
                else:
                    rows.append((number, letter, v, "ÜRET", image, prompt, ""))
    return rows

def photos_without_prompt(prompts):
    """Photos whose number is past the end of PROMPTS -> no prompt to pair with."""
    return sorted(os.path.basename(p)
                  for number, byletter in PHOTOS.items() if number >= len(prompts)
                  for paths in byletter.values() for p in paths)

PLAN = build_plan(PROMPTS)

print(f"\n{'ÇIKTI':>9}  {'KARAR':<6}  {'FOTOĞRAF':<16}  AÇIKLAMA")
print("-" * 78)
for number, letter, v, action, image, prompt, reason in PLAN:
    disp = f"{number}_{letter}" if VARIANTS == 1 else f"{number}_{letter}_{v + 1}"
    name = os.path.basename(image) if image else "—"
    detail = reason if reason else prompt.strip().replace("\n", " ")[:34]
    print(f"{disp:>9}  {action:<6}  {name:<16}  {detail}")

for name in photos_without_prompt(PROMPTS):
    print(f"  ⚠️  {name} atlandı — PROMPTS listesinde o numara yok ({len(PROMPTS)} prompt var)")

_to_render = sum(1 for r in PLAN if r[3] == "ÜRET")
print("-" * 78)
print(f"Üretilecek: {_to_render}  |  Atlanacak: {len(PLAN) - _to_render}")

if _to_render == 0:
    raise RuntimeError("❌ Üretilecek video yok — yukarıdaki tabloya bak (foto yok, prompt boş ya da hepsi zaten üretilmiş)")
```

- [ ] **Step 6: Cell 12 (markdown, üret intro) — replace:**

```markdown
## 6) Üret

Plan tablosunda **ÜRET** yazan her çıktı sırayla işlenir: fotoğraf ComfyUI'ya (foto başına bir kez) yüklenir, render edilir, Drive'a yazılır (`N_<harf>.mp4` veya `N_<harf>_<v>.mp4`), ComfyUI'daki kopyalar silinir.

Grafiğe yazılan üç alan: LoadImage **287** (o fotoğraf), PromptGenerator **233:240** (prompt + seed), Seed **210**. LoRA'lar, ağırlıklar, çözünürlük, step, cfg — hepsi grafikten gelir.

**Yarıda kalırsa** notebook'u baştan çalıştır: çıktısı olanlar hem plan hücresinde hem döngü içinde atlanır, kaldığı yerden devam eder.

**Hata olursa:** model yükleyici hatası batch'i durdurur (her video aynı hatayı alırdı). Tek videoya özgü hata yalnız onu atlar; üst üste 3 hata batch'i durdurur. Bir video 30 dakikada bitmezse `TimeoutError` ile durulur — kalanları üretmek için notebook'u tekrar çalıştırman yeter.

Seed her varyant için ayrı üretilir ve loglanır; `SEED`'e sayı verirsen varyant `v` için `SEED + v` kullanılır.
```

- [ ] **Step 7: Cell 13 (kod, üretim döngüsü) — replace.** `ComfyExecutionError`, node id'leri, `load_workflow`, `set_*`, `produced_files`, `ComfyClient` **aynen kalır** (api.ipynb'den); yalnız `generate_one` ve `process_all` değişir. Tam metin:

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

# === One render, end to end ===
def generate_one(client, save_path, image_name, prompt, seed):
    """One render: already-uploaded photo + prompt + seed -> save_path.
    save_path comes from process_all (out_path handles the VARIANTS naming)."""
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
    would hit the identical error. A video-specific failure only costs that render.
    """
    todo = [row for row in plan if row[3] == "ÜRET"]
    client = ComfyClient(COMFYUI_URL)
    uploaded = {}   # image_path -> server-side name; each photo uploads once, reused by its variants
    done = skipped = failed = 0
    consecutive = 0
    t_batch = time.time()

    log(f"Batch başlıyor — {len(todo)} video")
    for number, letter, v, _action, image_path, prompt, _reason in todo:
        save_path = out_path(number, letter, v)
        disp = os.path.splitext(os.path.basename(save_path))[0]
        # Re-check the disk: an earlier run of this cell may have produced it already.
        if os.path.exists(save_path) and os.path.getsize(save_path) > 0:
            log(f"{disp}: zaten var — atlandı")
            skipped += 1
            continue

        if image_path not in uploaded:              # upload the photo once, reused by all its variants
            uploaded[image_path] = client.upload_image(image_path)

        seed = random.randint(0, 2**31 - 1) if SEED is None else SEED + v
        log(f"{disp}: {os.path.basename(image_path)}  seed={seed}  |  "
            f"{prompt.strip()[:45]}{'…' if len(prompt.strip()) > 45 else ''}")
        t0 = time.time()
        try:
            path = generate_one(client, save_path, uploaded[image_path], prompt, seed)
        except ComfyExecutionError as e:
            print(e.text)
            print(e.traceback_text)
            if e.infra:
                raise RuntimeError(
                    f"Altyapı hatası ({e.text.splitlines()[0]}) — batch durduruldu, kalan videolar denenmedi"
                ) from None
            failed += 1
            consecutive += 1
            log(f"{disp}: başarısız — atlanıyor ({consecutive}/{MAX_CONSECUTIVE_FAILURES})", "ERR")
            if consecutive >= MAX_CONSECUTIVE_FAILURES:
                raise RuntimeError(f"Üst üste {consecutive} video başarısız — batch durduruldu") from None
            continue

        consecutive = 0
        done += 1
        log(f"{disp}: bitti ({time.time() - t0:.0f}s, {os.path.getsize(path) / 1024**2:.1f} MB) → {path}", "OK")

    log(f"Batch bitti ({(time.time() - t_batch) / 60:.0f} dk) — "
        f"üretildi: {done}, atlandı: {skipped}, başarısız: {failed}", "OK")

process_all(PLAN)
```

---

### Task 2: Doğrulama (grep — commit YOK)

**Files:** yok (salt okuma)

**Interfaces:**
- Consumes: Task 1'in `api_from_photos.ipynb`'si.
- Produces: kullanıcıya test raporu. Commit kullanıcı doğrulaması SONRASI.

Grep desenleri **tırnaksız düz token** (`.ipynb` kod hücreleri escaped JSON — tırnaklı desen eşleşmez).

- [ ] **Step 1: Olması gerekenler** — `api_from_photos.ipynb` içinde ≥1 eşleşme:
`scan_photos` · `PHOTO_RE` · `find_photo` · `out_path` · `photos_without_prompt` · `import os, glob, re` · `number, letter, v, action, image, prompt, reason` · `image_path not in uploaded` · `generate_one(client, save_path` · `VARIANTS == 1` · `imageToVideoV2`

- [ ] **Step 2: Olmaması gerekenler** — `api_from_photos.ipynb` içinde 0 eşleşme (eski arbuzai-varyant desenleri tam dönüşmüş olmalı):
`scan_images` · `find_image` · `VARIANT_LETTERS` · `images_without_prompt` · `generate_one(client, n, letter` · `row[2] ==` · `n, letter, _action, image_path` (eski 6'lı unpack)

- [ ] **Step 3: Değişmemesi gerekenler** — `api_from_photos.ipynb`'de hâlâ mevcut: `IMAGE_NODE` · `233:240` · `upload_image` · `save_output_video` · `describe_comfy_error` · `SmoothMix` · `set_image` · `VARIANTS`.

- [ ] **Step 4: Kullanıcıya raporla** — Colab test adımları (spec'in Doğrulama bölümü). Stage/commit yapılmaz.

---

## Self-review notu

- Spec kapsaması: girdi tarayıcı `N_<harf>` (Step 5 `scan_photos`/`PHOTO_RE`), numara→prompt paylaşımı (Step 5 `build_plan` `PROMPTS[number]`), `VARIANTS=1` default (Step 4), koşullu adlandırma (Step 5 `out_path`), foto bir kez yükleme (Step 7 `uploaded` image_path cache), paylaşımlı Drive + desen ayrımı (Step 4 `imageToVideoV2` + Step 5 `scan_photos` docstring), çift-dosya fail-loud (Step 5 `find_photo`), prompt-yok/boş atlama (Step 5), resume + hata sınıflandırması (Step 7).
- Tip tutarlılığı: `build_plan` → 7'li `(number, letter, v, action, image_path, prompt, reason)`; `process_all` `row[3]` filtresi + 7'li unpack; `generate_one(client, save_path, image_name, prompt, seed)` — cell 3 (`out_path`) ve cell 13 (`process_all` çağrısı) aynı imzayı kullanıyor; `_to_render` `r[3]`.
- DRY: `scan_photos`/`find_photo`/`out_path` yeni; `ComfyClient`/`set_*`/`produced_files`/`load_workflow` dokunulmadı.
