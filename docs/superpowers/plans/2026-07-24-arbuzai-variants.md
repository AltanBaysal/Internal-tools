# arbuzai I2V — girdi başına N varyant Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `wan22-arbuzai/api.ipynb`'ye `VARIANTS` eklemek — her foto+prompt için N video (`output/N_a.mp4, N_b.mp4, ...`), her varyant farklı seed.

**Architecture:** Mevcut api.ipynb'de 6 hücre değişir (3 kod + 3 markdown); geri kalanı (yardımcılar, custom node, model, başlatma) aynen kalır. `build_plan` satırları varyant düzeyine iner, `generate_one` yüklü foto adını dışarıdan alır, `process_all` foto başına bir kez yükleyip varyantları döner. Spec: `docs/superpowers/specs/2026-07-24-arbuzai-variants-design.md`.

**Tech Stack:** Colab notebook (.ipynb), ComfyUI HTTP API. Değişiklik yalnız Python hücrelerinde.

## Global Constraints

- **Dil:** notebook markdown + runtime çıktısı (`print`/`log`/`assert`/`RuntimeError`) Türkçe; kod yorumu/docstring İngilizce.
- **Python çalıştırma yok**; inceleme Grep/Read. Komut yalnız gerekliyse gerekçesiyle (bu planda 1: ipynb kopyası gerekmez — dosya yerinde düzenlenir; kopya komutu yok).
- **Git'e hiçbir şey eklenmez** — kullanıcı Colab'da doğrulayana kadar stage/commit yok.
- **Grafik, modeller, `manual.ipynb`, foto generator dokunulmaz.** Yalnız `wan22-arbuzai/api.ipynb`.
- Node id'leri değişmez: `IMAGE_NODE="287"`, `PROMPT_NODE="233:240"`, `SEED_NODE="210"`.
- `VARIANTS = 2` default; `SEED` sabitse varyant `v` için `SEED + v`.
- Çıktı hep harfli: `output/N_<harf>.mp4` (`VARIANTS=1` bile `N_a.mp4`).

---

### Task 1: api.ipynb — VARIANTS

**Files:**
- Modify: `collab-toolbox/video_generator/wan22-arbuzai/api.ipynb` (cell 0, 1, 2, 3, 12, 13)

**Interfaces:**
- Consumes: mevcut `ComfyClient`, `load_workflow`, `set_image/set_prompt/set_seed`, `produced_files`, `describe_comfy_error` (değişmez).
- Produces: `build_plan(prompts) -> [(n, letter, action, image_path, prompt, reason)]`, `generate_one(client, n, letter, image_name, prompt, seed) -> path`, `process_all(plan)`.

- [ ] **Step 1: Cell 0 (markdown, başlık) — Drive düzeni + "bir video" ifadeleri varyanta göre güncellenir.** NotebookEdit `replace`, tam metin:

```markdown
# WAN 2.2 arbuzai I2V — Batch API (numaralı fotolar + prompt listesi + varyant) — Colab

Drive'a numaralı fotoları koy, CONFIG'e prompt listesini yaz, çalıştır → her foto+prompt için `VARIANTS` video Drive'a düşer. ComfyUI arka planda **API** olarak çalışır; **UI açılmaz, tünel yok.**

> Grafiği elle kurcalamak, LoRA/ayar denemek istiyorsan bu değil — **`manual.ipynb`**. O ComfyUI'yi tünelle açar.

```
imageToVideoV2/             ← Drive'da senin oluşturacağın klasör
├── workflow_api.json   ← manual.ipynb'de Export (API) ile kaydettiğin graf
├── input/              ← 0.png, 1.jpg, 2.png … (numara = eşleşme anahtarı)
└── output/             ← 0_a.mp4, 0_b.mp4, 1_a.mp4 … (otomatik oluşur)
```

**Eşleşme:** `PROMPTS[0]` ↔ `input/0.*` → `output/0_a.mp4, 0_b.mp4, …`. Uzantı serbest (png/jpg/jpeg/webp). Varyant = aynı foto + aynı prompt, farklı seed → farklı hareket.

Sıra:
1. **CONFIG** — Drive mount + prompt listesi · ardından **üretim planı** basılır
2. **Ortak Yardımcılar** — log + fail-loud run + model doğrulama
3. **ComfyUI + custom node'lar** (16)
4. **Modeller** — önce gated probe, sonra indir (~36 GiB)
5. **ComfyUI'yi başlat** (arka planda, API)
6. **Üret** — her foto × varyant: yükle, render et, Drive'a yaz

> **Yarıda kalırsa baştan çalıştır.** Çıktısı olan varyantlar atlanır, kalanlar üretilir. Bir videoyu yeniden üretmek için Drive'dan `output/N_<harf>.mp4`'ü sil.

> **Video pahalı.** Her render A100'de dakikalar sürer; `VARIANTS`'ı foto sayısıyla çarp, toplam süreyi ona göre bekle. Default 2.

> **LoRA'lar grafikte.** Ağırlıkları `manual.ipynb` + UI'da ayarlayıp **Export (API)** ile dondurursun; bu notebook onlara dokunmaz, yalnız fotoğraf/prompt/seed yazar.
```

- [ ] **Step 2: Cell 1 (markdown, CONFIG intro) — VARIANTS satırı eklenir.** NotebookEdit `replace`, tam metin:

```markdown
## 1) CONFIG

Google Drive **burada** mount edilir: auth istemi ilk saniyede çıksın, 36 GiB'lık model indirmesinin ortasında seni beklemesin.

Doldurulacak yer `PROMPTS` — **liste sırası fotoğraf numarasıdır**: `PROMPTS[0]` → `input/0.*`, `PROMPTS[1]` → `input/1.*`. Her prompt üç tırnağın arasına yazılır; çok satırlı olabilir, içinde `"` geçebilir.

`VARIANTS` her foto için kaç video üretileceğidir (çıktılar `0_a.mp4, 0_b.mp4, …`). Video pahalı olduğu için default 2; artırınca toplam süre foto sayısı × varyant kadar büyür.

Bir numarayı bu turda üretmek istemiyorsan prompt'unu **boş bırak** (`""`) — liste kaymaz, o numaranın tüm varyantları atlanır.

Hemen alttaki hücre `input/` klasörünü tarayıp **üretim planını basar**: hangi numara/varyant üretilecek, hangisi neden atlanacak. Tablo indirmeden önce çıkar, yani yanlış eşleşmeyi 40 dakika sonra değil ilk saniyelerde görürsün.

Cookie'nin süresi dolmuşsa (~30 gün) `civitai.red`'den yenile.
```

- [ ] **Step 3: Cell 2 (kod, CONFIG) — `VARIANTS`, `VARIANT_LETTERS`, assert, print eklenir.** NotebookEdit `replace`. Mevcut hücrenin tam kopyası + 4 nokta değişir (SEED yorumu, VARIANTS satırı, VARIANT_LETTERS, assert, print). Tam metin:

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
SEED = None                  # None -> her varyant için ayrı rastgele seed; sayı verirsen varyant v için SEED+v
VARIANTS = 2                 # foto başına kaç video (a, b, ...) — video pahalı, düşük tut

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

VARIANT_LETTERS = "abcdefghijklmnopqrstuvwxyz"

import os
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
assert len(COOKIE_VALUE) > 200, "❌ COOKIE_VALUE boş/çok kısa — civitai.red'den __Secure-civ-token (ES256 JWT) yapıştır"
assert os.path.exists(WORKFLOW_PATH), f"❌ Workflow yok: {WORKFLOW_PATH} — manual.ipynb'de 'Workflow → Export (API)' ile kaydedip Drive'a koy"
assert any(p.strip() for p in PROMPTS), "❌ PROMPTS'ta dolu tek bir prompt yok — yukarıya prompt'larını yaz"
assert 1 <= VARIANTS <= len(VARIANT_LETTERS), f"❌ VARIANTS 1-{len(VARIANT_LETTERS)} arası olmalı (harfle adlandırılıyor)"

print(f"✓ Drive: {DRIVE_ROOT}")
print(f"✓ Cookie: {len(COOKIE_VALUE)} char  |  Timeout: {TIMEOUT_PER_RENDER // 60} dk/video")
print(f"✓ Seed: {SEED if SEED is not None else 'varyant başına rastgele'}  |  Varyant: {VARIANTS}")
print(f"✓ {len(PROMPTS)} prompt ({sum(1 for p in PROMPTS if not p.strip())} tanesi boş — atlanacak)")
print("=== GPU ===")
!nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
```

- [ ] **Step 4: Cell 3 (kod, üretim planı) — `build_plan` ve tablo varyant düzeyine iner.** NotebookEdit `replace`. `scan_images`/`find_image`/`images_without_prompt` **aynen kalır**; yalnız `build_plan`, tablo döngüsü ve `_to_render` değişir. Tam metin:

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
    """One row per (prompt index, variant letter) -> (n, letter, action, image_path, prompt, reason).

    An empty prompt is a deliberate 'skip this number' switch: PROMPTS is a flat list, so blanking
    an entry is the only way to disable one number (all its variants) without shifting the rest.
    """
    rows = []
    for n, prompt in enumerate(prompts):
        image = find_image(n)
        for v in range(VARIANTS):
            letter = VARIANT_LETTERS[v]
            out = f"{OUTPUT_DIR}/{n}_{letter}.mp4"
            if not prompt.strip():
                rows.append((n, letter, "ATLA", None, "", "prompt boş"))
            elif image is None:
                rows.append((n, letter, "ATLA", None, prompt, f"fotoğraf yok (input/{n}.*)"))
            elif os.path.exists(out) and os.path.getsize(out) > 0:
                rows.append((n, letter, "ATLA", image, prompt, "çıktı zaten var"))
            else:
                rows.append((n, letter, "ÜRET", image, prompt, ""))
    return rows

def images_without_prompt(prompts):
    """Numbered photos past the end of PROMPTS. A flat list has no holes, so running off its end
    is the only way a photo can lack a prompt."""
    return sorted(os.path.basename(p)
                  for n, paths in IMAGES.items() if n >= len(prompts)
                  for p in paths)

PLAN = build_plan(PROMPTS)

print(f"\n{'ÇIKTI':>7}  {'KARAR':<6}  {'FOTOĞRAF':<16}  AÇIKLAMA")
print("-" * 74)
for n, letter, action, image, prompt, reason in PLAN:
    name = os.path.basename(image) if image else "—"
    detail = reason if reason else prompt.strip().replace("\n", " ")[:34]
    print(f"{f'{n}_{letter}':>7}  {action:<6}  {name:<16}  {detail}")

for name in images_without_prompt(PROMPTS):
    print(f"  ⚠️  {name} atlandı — PROMPTS listesinde o numara yok ({len(PROMPTS)} prompt var)")

_to_render = sum(1 for r in PLAN if r[2] == "ÜRET")
print("-" * 74)
print(f"Üretilecek: {_to_render}  |  Atlanacak: {len(PLAN) - _to_render}")

if _to_render == 0:
    raise RuntimeError("❌ Üretilecek video yok — yukarıdaki tabloya bak (foto eksik, prompt boş ya da hepsi zaten üretilmiş)")
```

- [ ] **Step 5: Cell 12 (markdown, üret intro) — varyant + seed formülü yansıtılır.** NotebookEdit `replace`, tam metin:

```markdown
## 6) Üret

Plan tablosunda **ÜRET** yazan her `N_<harf>` sırayla işlenir: fotoğraf ComfyUI'ya (foto başına bir kez) yüklenir, render edilir, `output/N_<harf>.mp4` olarak Drive'a yazılır, ComfyUI'daki kopyalar silinir.

Grafiğe yazılan üç alan: LoadImage **287** (o numaranın fotoğrafı), PromptGenerator **233:240** (prompt + seed), Seed **210**. LoRA'lar, ağırlıklar, çözünürlük, step, cfg — hepsi grafikten gelir.

**Yarıda kalırsa** notebook'u baştan çalıştır: çıktısı olan varyantlar hem plan hücresinde hem döngü içinde atlanır, kaldığı yerden devam eder.

**Hata olursa:** model yükleyici hatası batch'i durdurur (her video aynı hatayı alırdı). Tek videoya özgü hata yalnız o varyantı atlar; üst üste 3 hata batch'i durdurur. Bir video 30 dakikada bitmezse `TimeoutError` ile durulur — kalanları üretmek için notebook'u tekrar çalıştırman yeter.

Seed her varyant için ayrı üretilir ve loglanır; `SEED`'e sayı verirsen varyant `v` için `SEED + v` kullanılır (dört varyant aynı seed'i alsaydı dört kez aynı video çıkardı).
```

- [ ] **Step 6: Cell 13 (kod, üretim döngüsü) — `generate_one` yüklü foto adını alır, `process_all` foto başına bir kez yükler.** NotebookEdit `replace`. `ComfyExecutionError`, node id'leri, `load_workflow`, `set_*`, `produced_files`, `ComfyClient` (dahil `upload_image`, `save_output_video`) **aynen kalır**; yalnız `generate_one` ve `process_all` değişir. Tam metin:

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

# === One variant, end to end ===
def generate_one(client, n, letter, image_name, prompt, seed):
    """One variant: already-uploaded photo + prompt + seed -> output/<n>_<letter>.mp4.
    The photo name comes in from process_all, which uploads each photo once for all its variants."""
    save_path = f"{OUTPUT_DIR}/{n}_{letter}.mp4"

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
    would hit the identical error. A video-specific failure only costs that variant.
    """
    todo = [row for row in plan if row[2] == "ÜRET"]
    client = ComfyClient(COMFYUI_URL)
    uploaded = {}   # n -> server-side image name; each photo uploads once, lazily on its first rendered variant
    done = skipped = failed = 0
    consecutive = 0
    t_batch = time.time()

    log(f"Batch başlıyor — {len(todo)} video")
    for n, letter, _action, image_path, prompt, _reason in todo:
        out = f"{OUTPUT_DIR}/{n}_{letter}.mp4"
        # Re-check the disk: an earlier run of this cell may have produced it already.
        if os.path.exists(out) and os.path.getsize(out) > 0:
            log(f"{n}_{letter}: zaten var — atlandı")
            skipped += 1
            continue

        if n not in uploaded:                       # upload the photo once, reused by all its variants
            uploaded[n] = client.upload_image(image_path)

        v = VARIANT_LETTERS.index(letter)
        seed = random.randint(0, 2**31 - 1) if SEED is None else SEED + v
        log(f"{n}_{letter}: {os.path.basename(image_path)}  seed={seed}  |  "
            f"{prompt.strip()[:45]}{'…' if len(prompt.strip()) > 45 else ''}")
        t0 = time.time()
        try:
            path = generate_one(client, n, letter, uploaded[n], prompt, seed)
        except ComfyExecutionError as e:
            print(e.text)
            print(e.traceback_text)
            if e.infra:
                raise RuntimeError(
                    f"Altyapı hatası ({e.text.splitlines()[0]}) — batch durduruldu, kalan videolar denenmedi"
                ) from None
            failed += 1
            consecutive += 1
            log(f"{n}_{letter}: başarısız — atlanıyor ({consecutive}/{MAX_CONSECUTIVE_FAILURES})", "ERR")
            if consecutive >= MAX_CONSECUTIVE_FAILURES:
                raise RuntimeError(f"Üst üste {consecutive} video başarısız — batch durduruldu") from None
            continue

        consecutive = 0
        done += 1
        log(f"{n}_{letter}: bitti ({time.time() - t0:.0f}s, {os.path.getsize(path) / 1024**2:.1f} MB) → {path}", "OK")

    log(f"Batch bitti ({(time.time() - t_batch) / 60:.0f} dk) — "
        f"üretildi: {done}, atlandı: {skipped}, başarısız: {failed}", "OK")

process_all(PLAN)
```

---

### Task 2: Doğrulama (grep — commit YOK)

**Files:** yok (salt okuma)

**Interfaces:**
- Consumes: Task 1'in düzenlediği `api.ipynb`.
- Produces: kullanıcıya test raporu. Commit kullanıcı doğrulaması SONRASI.

Grep desenleri **tırnaksız düz token** (`.ipynb` kod hücreleri escaped JSON — tırnaklı desen eşleşmez).

- [ ] **Step 1: Olması gerekenler** — `wan22-arbuzai/api.ipynb` içinde ≥1 eşleşme:
`VARIANTS` · `VARIANT_LETTERS` · `uploaded` · `SEED + v` · `n}_{letter}.mp4` · `generate_one(client, n, letter` · `row[2] == "ÜRET"` · `n, letter, action, image, prompt, reason`

- [ ] **Step 2: Olmaması gerekenler** — `wan22-arbuzai/api.ipynb` içinde 0 eşleşme:
`{n}.mp4` (harfsiz çıktı; regex `.` yeni `{n}_{letter}.mp4` biçimine takılmaz çünkü `{n}` ardından `_` gelir, `mp4` değil) · `generate_one(client, n, image_path` (eski imza) · `row[1] == "ÜRET"` (eski indeks) · `n, _action, image_path, prompt, _reason in todo` (eski 5'li unpack — yeni hali `n, letter, _action, ...`)

- [ ] **Step 3: Değişmemesi gerekenler** — `api.ipynb`'de hâlâ mevcut: `IMAGE_NODE` · `233:240` · `upload_image` · `save_output_video` · `describe_comfy_error` · `SmoothMix` · `set_image` (grafik/video altyapısı korundu).

- [ ] **Step 4: Kullanıcıya raporla** — Colab test adımları (spec'in Doğrulama bölümü) + eski harfsiz `N.mp4` uyarısı. Stage/commit yapılmaz.

---

## Self-review notu

- Spec kapsaması: `VARIANTS=2` + assert (Step 3), harfli çıktı `N_<harf>.mp4` (Step 3-4-6), varyant düzeyi plan (Step 4), `SEED+v` (Step 6), foto bir kez yükleme (`uploaded` dict, Step 6), varyant düzeyi resume (Step 4 plan + Step 6 döngü içi disk kontrolü), boş prompt/foto yok tüm varyantları atlar (Step 4 `build_plan`). Eski çıktı uyarısı Step 4 raporunda.
- Tip tutarlılığı: `build_plan` → 6'lı `(n, letter, action, image_path, prompt, reason)`; `process_all` `row[2]` filtresi + 6'lı unpack; `generate_one(client, n, letter, image_name, prompt, seed)` — cell 3 ve cell 13 aynı şekli kullanıyor.
- `scan_images`/`find_image`/`images_without_prompt`/`ComfyClient`/`set_*`/`produced_files` değişmedi — DRY, dokunulmadı.
