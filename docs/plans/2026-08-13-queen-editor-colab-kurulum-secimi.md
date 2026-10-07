# Colab defterinde üretici seçimi — uygulama planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `app.ipynb` CONFIG'ine üç onay kutusu girsin; işaretlenen üreticinin modelleri (foto, video, ses) defterde insin, işaretlenmeyen hiç denenmesin.

**Architecture:** Defterin var olan indirme makinesi (`fetch`, `civitai_probe`, `check_safetensors`, `check_binary`) değişmiyor; üstüne üç veri listesi ve kutulara bakan bir seçim katmanı geliyor. Ses ayrı, çünkü ComfyUI'de değil uygulamanın kendi sürecinde çalışıyor: kütüphane + kendi ağırlıkları iki yeni hücrede. Uygulama tarafında iki satır: arayüzün "nasıl kurulur" cümlesi ve Flask'a geçen `QE_COMFY_ROOT`.

**Tech Stack:** Colab notebook (Python + `#@param` form), pytest (defterin metni üzerinde), vitest/React (tek metin sabiti), Vite build.

**Tasarım:** [2026-08-13-queen-editor-colab-kurulum-secimi-design.md](../specs/2026-08-13-queen-editor-colab-kurulum-secimi-design.md)

## Global Constraints

- **Dil:** kod, yorum, docstring, test adı ve commit mesajı **İngilizce**; defterin markdown hücreleri ve `print`/`assert`/`RuntimeError` metinleri **Türkçe**; bu doküman Türkçe.
- **Yorum kayması yasak:** yorum kodun ŞU ANKİ halini anlatır; `# OLD:`/`# NEW:` yok. Çakışmada yorum düzeltilir.
- **Hata mesajında sebep uydurulmaz:** komutun/servisin kendi çıktısı basılır (HTTP kodu + gövde, `stderr` kuyruğu).
- **Defter düzenlemesi `NotebookEdit` ile yapılır** (`ToolSearch` ile şemasını çek). `.ipynb`'yi elle JSON olarak yazmak yok.
- **Dosya adları `model_groups.py`'nin saydığı adlarla birebir aynı** olmalı — panel diski o adlarla okuyor.
- **`frontend/src/` değişirse** aynı commit'te `npm run build --prefix queen-editor/frontend` çıktısı (`frontend/dist/`) da girer.
- **Tek commit:** dört görev bittikten sonra hepsi tek commit. Commit mesajında **çift tırnak yok**.
- Test komutları (repo kökünden, `cd` yok):
  - `python -m pytest queen-editor/backend/tests -q`
  - `npm test --prefix queen-editor/frontend`

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `queen-editor/app.ipynb` | kurulum defteri: CONFIG kutuları, üç grubun indirmesi, ses motoru, markdown | Değişiyor (hücre `8215086b`, `f0df85b4`, `e086a5a5`, `34c9ff58`, `8de17e98`, `4d387058` + 3 yeni hücre) |
| `queen-editor/backend/tests/test_notebook_installs_the_producer_groups.py` | panelin saydığı dosya ile defterin indirdiği dosya arasındaki tek bağ | Yeni (eski `test_notebook_installs_the_photo_group.py` siliniyor) |
| `queen-editor/frontend/src/features/producers/useProducers.js` | "Kur"a basınca çıkan cümle | Tek sabit değişiyor |
| `queen-editor/frontend/dist/` | Colab'ın servis ettiği derlenmiş arayüz | Yeniden derleniyor |

---

### Task 1: CONFIG'de üç onay kutusu

**Files:**
- Test: `queen-editor/backend/tests/test_notebook_installs_the_producer_groups.py` (yeni)
- Sil: `queen-editor/backend/tests/test_notebook_installs_the_photo_group.py`
- Modify: `queen-editor/app.ipynb` — hücre `8215086b` (CONFIG)

**Interfaces:**
- Consumes: `backend.features.producers.domain.model_groups.GROUPS`
- Produces: defterde `INSTALL_PHOTO` / `INSTALL_VIDEO` / `INSTALL_AUDIO` (bool) ve `APP_DIR` (str) — Görev 2, 3 ve 4 bunları kullanıyor.

- [ ] **Step 1: Yeni test dosyasını yaz (eskisinin yerine)**

`queen-editor/backend/tests/test_notebook_installs_the_producer_groups.py`:

```python
"""The notebook installs what the panel counts.

The app reads a producer's group off the disk and the notebook is what puts it there
(FOUNDATION 9). Nothing connects the two lists at runtime, so a file added to the group and
forgotten in the notebook would leave the panel saying "kurulu değil" for good, with nobody able to
see why. This test is that connection.

The notebook is read, never run: a Colab cell cannot execute here. What text can still answer is
exactly what matters -- is every counted file named, and is each group behind its own switch.
"""
import json
import os

from backend.features.producers.domain.model_groups import GROUPS

NOTEBOOK = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "app.ipynb")

# Which CONFIG checkbox owns which producer.
SWITCH = {"photo": "INSTALL_PHOTO", "video": "INSTALL_VIDEO", "audio": "INSTALL_AUDIO"}


def _source():
    """Every cell's source as one blob. Parsed rather than read raw: the file is JSON, so a raw
    read would be searching escaped quotes and \\n instead of the code the cell runs."""
    with open(NOTEBOOK, encoding="utf-8") as handle:
        doc = json.load(handle)
    return "\n".join("".join(cell.get("source", "")) for cell in doc.get("cells", []))


def test_every_file_the_panel_counts_is_fetched_by_the_notebook():
    missing = [row["name"] for group in GROUPS.values() for row in group
               if row["name"] not in _source()]

    assert missing == [], f"Defter bu dosyaları indirmiyor: {missing}"


def test_every_producer_has_a_checkbox_of_its_own():
    """Colab draws a `#@param {type:"boolean"}` line as a checkbox: that is how the user picks.
    Default False, so nothing heavy starts by accident."""
    source = _source()

    for kind in GROUPS:
        assert f'{SWITCH[kind]} = False  #@param {{type:"boolean"}}' in source, \
            f"{kind}: CONFIG'de kapalı gelen bir onay kutusu yok"


def test_choosing_nothing_stops_the_notebook():
    """With no producer chosen the app opens and renders nothing -- a queued job waits forever.
    Hearing that in CONFIG costs a second; hearing it in the UI costs the whole setup run."""
    assert "assert INSTALL_PHOTO or INSTALL_VIDEO or INSTALL_AUDIO" in _source()


def test_the_cookie_is_only_demanded_by_the_groups_that_are_gated():
    """Only photo and video pull from Civitai. A sound-only run must not stop for a cookie it
    never sends. Pinned as the two lines together: `if INSTALL_PHOTO or INSTALL_VIDEO` appears
    elsewhere too, so the switch alone would prove nothing about the cookie."""
    assert ('if INSTALL_PHOTO or INSTALL_VIDEO:\n'
            '    assert len(COOKIE_VALUE or "") > 200') in _source()
```

- [ ] **Step 2: Testleri çalıştır, düştüklerini gör**

Run: `python -m pytest queen-editor/backend/tests/test_notebook_installs_the_producer_groups.py -q`
Expected: FAIL — `test_every_file_the_panel_counts_is_fetched_by_the_notebook` (video + ses dosyaları defterde yok), `test_every_producer_has_a_checkbox_of_its_own`, `test_choosing_nothing_stops_the_notebook`, `test_the_cookie_is_only_demanded_by_the_groups_that_are_gated`.

- [ ] **Step 3: Eski test dosyasını sil**

Sil: `queen-editor/backend/tests/test_notebook_installs_the_photo_group.py` — içindeki iki test yenisinde var (foto dosyaları `GROUPS` üzerinden, gated probe kuralı Görev 2'de geri geliyor).

- [ ] **Step 4: CONFIG hücresini değiştir**

`NotebookEdit` ile hücre `8215086b`'nin kaynağını şununla değiştir:

```python
# === CONFIG ===
# Ne kurulacağını buradan seç: Colab bu üç satırı sağdaki formda onay kutusu olarak çizer.
# İşaretlemediğin üreticinin modelleri hiç indirilmez.
#   fotoğraf ~8 GiB · video ~37 GiB (T4'ün diski çoğu zaman yetmez, A100 iste) · ses ~9 GiB
INSTALL_PHOTO = False  #@param {type:"boolean"}
INSTALL_VIDEO = False  #@param {type:"boolean"}
INSTALL_AUDIO = False  #@param {type:"boolean"}

# Asked before anything else: with no producer chosen the app still opens and still serves, but a
# queued job would sit waiting for a producer that never arrives. A second here beats a whole
# setup run.
assert INSTALL_PHOTO or INSTALL_VIDEO or INSTALL_AUDIO, (
    "❌ Hiçbir üretici seçilmedi — yukarıdaki kutulardan en az birini işaretle "
    "(INSTALL_PHOTO / INSTALL_VIDEO / INSTALL_AUDIO) ve hücreyi tekrar çalıştır."
)

# The GitHub token comes from Colab's Secrets store (🔑 in the left sidebar), NOT this cell
# -- set once per Google account, never pasted again, never in the notebook source or git.
# Add a secret named GITHUB_TOKEN (fine-grained, this repo, "Contents: read") and grant this
# notebook access. See README for the token setup.
from google.colab import userdata

try:
    GITHUB_TOKEN = userdata.get("GITHUB_TOKEN")
except Exception:
    GITHUB_TOKEN = ""   # secret missing or access not granted -> the assert below explains the fix

BRANCH       = "feat/queen-editor-v3"       # dev branch for now; switch to "main" after merge
REPO         = "AltanBaysal/Internal-tools" # <owner>/<repo>
CLONE_DIR    = "/content/Internal-tools"    # clone target on Colab's local disk
# The app is started from here, and MMAudio's own weights have to land here too: the library
# resolves ./weights and ./ext_weights against the working directory.
APP_DIR      = f"{CLONE_DIR}/queen-editor"
APP_PORT     = 8000                         # Flask port (matches backend/config.py)
DRIVE_FOLDER = "queenEditor"                # proje kökü (MyDrive altında) — adı buradan değiştir

# === ComfyUI (kurulum + üretim; backend QE_COMFY_URL ile bu adrese konuşur) ===
COMFY_PORT  = 8188
COMFY_ROOT  = "/content/ComfyUI"
COMFY_LOG   = "/content/comfyui.log"
COMFYUI_URL = f"http://127.0.0.1:{COMFY_PORT}"

# Civitai's gated models need the session cookie: two files of the photo group and four of the
# video group come from there. Like GITHUB_TOKEN it comes from Colab Secrets -- this notebook is
# committed, so a pasted session JWT would land in git.
try:
    COOKIE_VALUE = userdata.get("CIVITAI_COOKIE")
except Exception:
    COOKIE_VALUE = ""

# A video's prompt is written by xAI when the job's turn comes; the key comes from Secrets like the
# two above. No assert: a photo-only run needs no language model, and stopping the notebook over a
# key that run never uses would be wrong.
try:
    XAI_API_KEY = userdata.get("XAI_API_KEY")
except Exception:
    XAI_API_KEY = ""

assert GITHUB_TOKEN, (
    "❌ GITHUB_TOKEN yok — Colab solundaki 🔑 Secrets panelinden 'GITHUB_TOKEN' adıyla ekle "
    "ve bu notebook'a erişimi aç (fine-grained, yalnız bu repo, Contents: read)."
)
# Only the photo and video groups are gated; a sound-only run sends no cookie at all. Asserted here
# rather than at the download: hearing it now costs a second, hearing it after ComfyUI's install
# costs ten minutes.
if INSTALL_PHOTO or INSTALL_VIDEO:
    assert len(COOKIE_VALUE or "") > 200, (
        "❌ CIVITAI_COOKIE yok/çok kısa — Colab 🔑 Secrets'a 'CIVITAI_COOKIE' adıyla ekle: "
        "civitai.red → giriş → F12 → Application → Cookies → __Secure-civ-token değeri (ES256 JWT)"
    )

# SDXL needs a GPU. A CPU runtime has no driver at all, so nvidia-smi is missing rather than
# failing -- and ComfyUI would come up fine there and then fail on every render.
import subprocess as _sp
try:
    _gpu = _sp.run(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
                   capture_output=True, text=True)
    _gpu_name = _gpu.stdout.strip() if _gpu.returncode == 0 else ""
except FileNotFoundError:
    _gpu_name = ""
assert _gpu_name, (
    "❌ GPU yok — Runtime → Change runtime type → T4 GPU seç ve Run all'ı yeniden çalıştır"
)

_chosen = [name for name, on in (("fotoğraf", INSTALL_PHOTO), ("video", INSTALL_VIDEO),
                                 ("ses", INSTALL_AUDIO)) if on]
print(f"✓ GPU: {_gpu_name}")
print("✓ CONFIG hazır (token Colab Secrets'tan okundu)")
print(f"✓ Kurulacak üretici: {', '.join(_chosen)}")
print(f"✓ Dal: {BRANCH}  |  Repo: {REPO}  |  Hedef: {CLONE_DIR}")
print(f"✓ Proje kökü: MyDrive/{DRIVE_FOLDER}")
print(f"✓ xAI anahtarı: {'okundu' if XAI_API_KEY else 'yok — video prompt yazılamaz'}")
```

- [ ] **Step 5: Testleri çalıştır**

Run: `python -m pytest queen-editor/backend/tests/test_notebook_installs_the_producer_groups.py -q`
Expected: `test_every_file_the_panel_counts_is_fetched_by_the_notebook` hâlâ FAIL (video + ses dosyaları Görev 2'de geliyor), diğer üçü PASS.

---

### Task 2: İndirme hücresi üç gruba açılır

**Files:**
- Test: `queen-editor/backend/tests/test_notebook_installs_the_producer_groups.py` (test ekleniyor)
- Modify: `queen-editor/app.ipynb` — hücre `f0df85b4` (model indirme)

**Interfaces:**
- Consumes: `INSTALL_PHOTO/VIDEO/AUDIO`, `COMFY_ROOT`, `COOKIE_VALUE` (CONFIG); `log`, `run`, `human`, `head_text`, `check_safetensors` (yardımcılar hücresi)
- Produces: `MMAU` klasörü (ses fine-tune'unun yeri) — Görev 3 aynı ağaca yazmıyor, yalnız aynı üreticiyi tamamlıyor.

- [ ] **Step 1: Testleri ekle**

`test_notebook_installs_the_producer_groups.py` sonuna:

```python
def test_the_gated_files_are_fetched_the_way_that_works():
    """curl, not aria2c: Civitai redirects to its store, which answers 403 if the login cookie
    travels with the request. aria2c forwards it; curl drops it when the host changes."""
    source = _source()

    assert "civitai_probe" in source, "Ağır indirmeden önce kapılı erişim yoklanmalı"
    assert "civitai.red/api/download/models" in source


def test_an_unticked_group_costs_no_bytes():
    """The whole point of the checkboxes: a group's list is only reached through its own switch."""
    source = _source()

    for names, kind in ((("CIVITAI_PHOTO", "OPEN_PHOTO"), "photo"),
                        (("CIVITAI_VIDEO", "OPEN_VIDEO"), "video"),
                        (("OPEN_AUDIO",), "audio")):
        for name in names:
            assert f"{name} if {SWITCH[kind]} else []" in source, \
                f"{name} kendi anahtarının arkasında değil"


def test_the_disk_is_measured_before_the_download_starts():
    """All three together are ~54 GiB. Finding out the disk was too small halfway through leaves
    half-written files and no explanation."""
    assert "shutil.disk_usage" in _source()
```

- [ ] **Step 2: Testleri çalıştır, düştüklerini gör**

Run: `python -m pytest queen-editor/backend/tests/test_notebook_installs_the_producer_groups.py -q`
Expected: FAIL — `test_an_unticked_group_costs_no_bytes` ve `test_the_disk_is_measured_before_the_download_starts`.

- [ ] **Step 3: İndirme hücresini değiştir**

`NotebookEdit` ile hücre `f0df85b4`'ün kaynağını şununla değiştir. Makine (`check_binary`, `fetch`, `civitai_url`, `cookie_header`, `civitai_probe`) **birebir korunuyor**; değişen kısım klasör listesi, model listeleri ve akış:

```python
import os, glob, shutil

# === Target folders ===
COMFY = COMFY_ROOT
CKPT = f"{COMFY}/models/checkpoints"
LORA = f"{COMFY}/models/loras"
UPSC = f"{COMFY}/models/upscale_models"
BBOX = f"{COMFY}/models/ultralytics/bbox"   # UltralyticsDetectorProvider lists files as "bbox/<name>"
SAMS = f"{COMFY}/models/sams"
DIFF = f"{COMFY}/models/diffusion_models"
VAE  = f"{COMFY}/models/vae"
TENC = f"{COMFY}/models/text_encoders"
# ComfyUI never reads this one: sound runs in the app's own process. It lives under the same root
# because the panel and the sampler both hang off it, and a second root for one file would be the
# same knowledge written twice.
MMAU = f"{COMFY}/models/mmaudio"
for d in [CKPT, LORA, UPSC, BBOX, SAMS, DIFF, VAE, TENC, MMAU]:
    os.makedirs(d, exist_ok=True)

def check_binary(path, min_bytes):
    """State of a .pt/.pth model -> ("ok" | "partial" | "invalid", msg).

    Torch pickle/zip files carry no self-describing total length (unlike safetensors), so the
    honest cheap checks are: the head is not an HTML/JSON error page, and the size clears a loose
    floor (guards against truncated/error downloads, not an exact size). Below the floor counts
    as "partial" so an interrupted download stays resumable.
    """
    if not os.path.exists(path):
        return "invalid", "missing"
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        head = f.read(16)
    if head[:1] in (b"<", b"{"):
        return "invalid", f"error page? ({human(size)})"
    if size < min_bytes:
        return "partial", f"{human(size)} < taban {human(min_bytes)}"
    return "ok", human(size)

# === Single download function — shared flow for HF (aria2c) and Civitai (curl) (DRY) ===
def fetch(url, target_dir, filename, label, *, parallel, headers=None, validate=None):
    """Download + validate a model; anything invalid stops the run (fail-loud, nothing deleted).

    parallel=True -> aria2c (fast for large HF files), False -> curl (Civitai, login cookie).
    validate -> (path) -> (state, msg); default check_safetensors. .pt/.pth files pass a
    check_binary lambda because they have no self-describing length.
    Downloads land in <target>.part and are renamed only once the validator says "ok", so
    ComfyUI never sees a half-written file under the real model name.

    On failure the raw HTTP exchange is printed, not a summary of it: curl runs with
    --fail-with-body (non-zero exit, but the response body is kept instead of discarded) and -D
    (every response header of the redirect chain), so a Civitai 401/403 shows the server's own
    headers and body verbatim.
    """
    validator = validate or check_safetensors
    target = os.path.join(target_dir, filename)
    part = target + ".part"
    hdrs = f"/tmp/{filename}.headers"

    if os.path.exists(target):
        state, msg = validator(target)
        if state == "ok":
            log(f"{label}: zaten var ({msg})")
            return
        raise RuntimeError(f"{label}: {state} — {msg}\n{target}\n--- file head ---\n{head_text(target)}")

    resume = False
    if os.path.exists(part):
        state, msg = validator(part)
        if state == "invalid":
            # Resuming onto garbage would append good bytes to it and hide the problem.
            raise RuntimeError(f"{label}: .part {state} — {msg}\n{part}\n--- file head ---\n{head_text(part)}")
        if state == "ok":
            log(f"{label}: .part zaten tam ({msg}) — indirilmiyor")
        else:
            log(f"{label}: .part'tan devam ({msg})")
            resume = True

    if not os.path.exists(part) or resume:
        log(f"{label}: iniyor")
        if parallel:
            cmd = ["aria2c", "-x", "16", "-s", "16", "-k", "1M", "--continue=true",
                   "--console-log-level=warn", "--auto-file-renaming=false",
                   "--allow-overwrite=true", "-d", target_dir, "-o", os.path.basename(part)]
            if headers:
                cmd += ["--header", headers]
        else:
            cmd = ["curl", "-L", "-C", "-", "--fail-with-body", "--max-time", "1800",
                   "-D", hdrs, "-o", part]
            if headers:
                cmd += ["-H", headers]
        cmd.append(url)
        try:
            run(cmd, label, timeout=3600)
        except RuntimeError as e:
            raise RuntimeError(
                f"{e}\n{url.split('?')[0]}\n"
                f"--- response headers ---\n{head_text(hdrs)}\n"
                f"--- response body ---\n{head_text(part)}"
            ) from None

    state, msg = validator(part)
    if state != "ok":
        raise RuntimeError(f"{label}: {state} — {msg}\n{part}\n{url.split('?')[0]}\n"
                           f"--- response headers ---\n{head_text(hdrs)}\n"
                           f"--- file head ---\n{head_text(part)}")
    os.replace(part, target)
    log(f"{label}: indirildi ve doğrulandı ({msg})", "OK")

# Civitai auth: session cookie ONLY. A ?token= API key authenticates the request as that key's
# account -> creator-gated assets answer 401.
# Host = civitai.RED: the cookie is same-origin there. Sending it to .com is cross-domain and
# returns the login+turnstile page instead of the file.
def civitai_url(version_id):
    return f"https://civitai.red/api/download/models/{version_id}"

def cookie_header():
    return f"Cookie: __Secure-civ-token={COOKIE_VALUE}"

def civitai_probe(version_id, label):
    """Fail-fast: range-download the first 1KB to verify gated access BEFORE the heavy download.
    On non-2xx or a login wall, surface Civitai's ACTUAL response body -- no hardcoded guesses.
    """
    out = "/content/_probe.bin"
    code = (run(["curl", "-sL", "--max-time", "60", "-r", "0-1023",
                 "-H", cookie_header(), "-w", "%{http_code}", "-o", out,
                 civitai_url(version_id)], f"probe {label}") or "").strip()[-3:]
    body = b""
    if os.path.exists(out):
        with open(out, "rb") as f:
            body = f.read(512)
        os.remove(out)
    # success = 2xx AND the body is real binary (safetensors), not an HTML/JSON error page
    if code.startswith("2") and not body.startswith(b"<") and not body.startswith(b'{"'):
        log(f"{label}: erişim OK", "OK")
        return
    raise RuntimeError(f"❌ {label}: HTTP {code} — Civitai yanıtı: "
                       f"{body.decode('utf-8', 'replace').strip() or '(boş gövde — binary değil)'}")

# === What each producer needs. Data only: which list runs is the checkboxes' decision, below. ===
# Civitai rows: (version_id, target_dir, filename, label)
# Open rows:    (url, target_dir, filename, label, min_bytes) -- min_bytes None means safetensors,
#               a number means .pt/.pth, which carries no length of its own (check_binary).
# Every filename is the name the graph loads by, which is not always the name at the source.

CIVITAI_PHOTO = [
    (2744564, CKPT, "nova3DCGXL_ilV90.safetensors",               "Nova 3DCG XL IL v9.0"),
    (1552087, LORA, "USNR_STYLE_ILL_V1_lokr3-000024.safetensors", "USNR STYLE ILL v1.0"),
]
# The photo graph's default-ON FaceDetailer branch loads the detector + SAM at startup; the
# bypassed Ultimate SD Upscale branch reads Remacri the moment the user enables it.
OPEN_PHOTO = [
    ("https://huggingface.co/FacehugmanIII/4x_foolhardy_Remacri/resolve/main/4x_foolhardy_Remacri.pth",
     UPSC, "4x_foolhardy_Remacri.pth", "Remacri 4x upscaler", 50_000_000),
    ("https://huggingface.co/Bingsu/adetailer/resolve/main/face_yolov9c.pt",
     BBOX, "face_yolov9c.pt", "Yuz dedektoru (yolov9c)", 40_000_000),
    ("https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth",
     SAMS, "sam_vit_b_01ec64.pth", "SAM ViT-B", 300_000_000),
]

WAN22 = "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files"
WAN21 = "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files"
# The video graph has both distill LoRAs switched on in its Power Lora Loader -- I2V v2.0 does not
# ship lightx2v merged, so they have to be on disk. VAELoader asks for 'Wan2_1_VAE_fp32', which is
# not what the source calls the file: ComfyUI finds a model by its name on disk.
OPEN_VIDEO = [
    (f"{WAN22}/loras/wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors",
     LORA, "wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors", "Lightx2v I2V HIGH", None),
    (f"{WAN22}/loras/wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors",
     LORA, "wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors", "Lightx2v I2V LOW", None),
    (f"{WAN21}/vae/wan_2.1_vae.safetensors",
     VAE, "Wan2_1_VAE_fp32.safetensors", "Wan2.1 VAE", None),
    (f"{WAN21}/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors",
     TENC, "umt5_xxl_fp8_e4m3fn_scaled.safetensors", "UMT5-XXL", None),
]
# UNETLoader asks for the checkpoint pair, the Power Lora Loader for the Animations pair; Civitai
# serves all four under its own file names, so each lands under the name the graph names.
CIVITAI_VIDEO = [
    (2513182, DIFF, "SmoothMix_I2V_v2_High.safetensors",         "SmoothMix I2V v2 HIGH"),
    (2513186, DIFF, "SmoothMix_I2V_v2_Low.safetensors",          "SmoothMix I2V v2 LOW"),
    (2376136, LORA, "SmoothMix_Animations_XXX_High.safetensors", "SmoothMix Animations XXX HIGH"),
    (2376143, LORA, "SmoothMix_Animations_XXX_Low.safetensors",  "SmoothMix Animations XXX LOW"),
]

# The sound fine-tune, and only that: MMAudio's own vae, synchformer and base checkpoint come down
# with the library in the cell below, which is what knows where it keeps them.
OPEN_AUDIO = [
    ("https://huggingface.co/phazei/NSFW_MMaudio/resolve/main/"
     "mmaudio_large_44k_nsfw_gold_8.5k_final_fp16.safetensors",
     MMAU, "mmaudio_large_44k_nsfw_gold_8.5k_final_fp16.safetensors", "MMAudio NSFW fine-tune",
     None),
]

# === What this run installs (the checkboxes, and nothing else) ===
civitai_jobs = (CIVITAI_PHOTO if INSTALL_PHOTO else []) + (CIVITAI_VIDEO if INSTALL_VIDEO else [])
open_jobs = ((OPEN_PHOTO if INSTALL_PHOTO else [])
             + (OPEN_VIDEO if INSTALL_VIDEO else [])
             + (OPEN_AUDIO if INSTALL_AUDIO else []))

# Rounded up on purpose: an estimate that is too low fills the disk and leaves half-written files,
# while one that is too high costs a warning. Sound counts the library's own ~7 GiB too, which
# lands in the cell below rather than here.
SIZES = [(INSTALL_PHOTO, 8, "fotoğraf"), (INSTALL_VIDEO, 37, "video"), (INSTALL_AUDIO, 9, "ses")]
HEADROOM_GIB = 5    # renders, exports and .part files share this disk
need = sum(gib for on, gib, _ in SIZES if on)
free = shutil.disk_usage("/content").free / 1024**3
log(f"Seçim: {', '.join(name for on, _, name in SIZES if on)} — ~{need} GiB "
    f"| Diskte boş: {free:.1f} GiB")
if free < need + HEADROOM_GIB:
    raise RuntimeError(
        f"❌ Disk yetmiyor: ~{need} GiB model + {HEADROOM_GIB} GiB pay gerekiyor, "
        f"{free:.1f} GiB boş. Daha az üretici seç ya da diski daha büyük bir runtime aç "
        f"(video tek başına ~37 GiB)."
    )

# 1) Fail-fast: verify gated access before spending the download time
if civitai_jobs:
    log(f"Gated probe: {len(civitai_jobs)} asset")
    for vid, d, fn, label in civitai_jobs:
        civitai_probe(vid, label)

# 2) Open downloads (aria2c)
for url, d, fn, label, floor in open_jobs:
    fetch(url, d, fn, label, parallel=True,
          validate=(lambda p, m=floor: check_binary(p, m)) if floor else None)

# 3) Civitai — parallel=False: aria2c forwards the cookie to the B2 store on redirect and gets 403,
#    curl drops it cross-host and gets through.
for vid, d, fn, label in civitai_jobs:
    fetch(civitai_url(vid), d, fn, label, parallel=False, headers=cookie_header())

# === Summary (reaching here means everything downloaded + validated) ===
folders = []
if INSTALL_PHOTO:
    folders += [("checkpoints", CKPT, "*.safetensors"), ("upscale_models", UPSC, "*.pth"),
                ("ultralytics/bbox", BBOX, "*.pt"), ("sams", SAMS, "*.pth")]
if INSTALL_VIDEO:
    folders += [("diffusion_models", DIFF, "*.safetensors"), ("vae", VAE, "*.safetensors"),
                ("text_encoders", TENC, "*.safetensors")]
if INSTALL_PHOTO or INSTALL_VIDEO:      # both groups write loras
    folders += [("loras", LORA, "*.safetensors")]
if INSTALL_AUDIO:
    folders += [("mmaudio", MMAU, "*.safetensors")]
for title, folder, pattern in folders:
    print(f"\n📂 {title}/")
    for f in sorted(glob.glob(f"{folder}/{pattern}")):
        print(f"   {human(os.path.getsize(f))}  {os.path.basename(f)}")
log("Seçilen modeller indirildi ve doğrulandı", "OK")
```

- [ ] **Step 4: Testleri çalıştır**

Run: `python -m pytest queen-editor/backend/tests/test_notebook_installs_the_producer_groups.py -q`
Expected: PASS (yedi testin hepsi — video ve ses dosya adları artık defterde).

---

### Task 3: Ses motoru — kütüphane + kendi ağırlıkları

**Files:**
- Test: `queen-editor/backend/tests/test_notebook_installs_the_producer_groups.py` (test ekleniyor)
- Modify: `queen-editor/app.ipynb` — `f0df85b4`'ten sonra 1 markdown + 2 kod hücresi eklenir

**Interfaces:**
- Consumes: `INSTALL_AUDIO`, `APP_DIR` (CONFIG); `log`, `run` (yardımcılar hücresi)
- Produces: `import mmaudio` çalışır durumda + `APP_DIR/ext_weights`, `APP_DIR/weights` — uygulamanın `MMAudioSampler`'ı bunları okuyor.

- [ ] **Step 1: Testi ekle**

```python
def test_the_sound_box_installs_the_library_not_just_a_weight_file():
    """MMAudio runs inside the app's process, so `import mmaudio` has to work there -- a weight
    file with no library is not a producer. The base weights come with it: warming them here is
    what keeps the first sound job from stalling on a ~7 GiB download."""
    source = _source()

    assert "hkchengrex/MMAudio" in source, "Ses kutusu kütüphaneyi kurmuyor"
    assert "download_if_needed" in source, "MMAudio'nun kendi ağırlıkları öne alınmamış"


def test_the_sound_weights_land_where_the_app_will_look():
    """MMAudio resolves ./weights and ./ext_weights against the working directory, and the app is
    started from APP_DIR. Downloading them anywhere else means the app fetches them again."""
    assert "os.chdir(APP_DIR)" in _source()
```

- [ ] **Step 2: Testleri çalıştır, düştüklerini gör**

Run: `python -m pytest queen-editor/backend/tests/test_notebook_installs_the_producer_groups.py -q`
Expected: FAIL — iki yeni test.

- [ ] **Step 3: Markdown hücresini ekle**

`NotebookEdit` ile `f0df85b4`'ten sonra markdown hücresi:

```markdown
## Ses motoru (yalnız `INSTALL_AUDIO` işaretliyse)

Ses ComfyUI'de üretilmiyor: **MMAudio uygulamanın kendi sürecinde** çalışıyor, yani `import mmaudio`
orada çalışmak zorunda. Bu yüzden kutu işaretliyse kütüphane klonlanıp kuruluyor.

Ardından MMAudio'nun **kendi ağırlıkları** (vae, synchformer, taban checkpoint — ~7 GiB) iniyor.
Kütüphane bunları zaten kendi indiriyor; buradaki iş sırayı öne almak, yoksa ilk ses işi kuyrukta
sessizce bu indirmeyi bekletirdi. Dosyalar uygulamanın çalıştığı klasöre iner — MMAudio bu yolları
çalışma dizinine göre çözüyor, başka yere inen dosya uygulama için yok sayılır.
```

- [ ] **Step 4: Kütüphane hücresini ekle**

```python
# === Ses motoru — MMAudio kütüphanesi ===
# Sound is the one producer that is not a ComfyUI graph. Installed here, before the app starts: a
# library that appears after a process has begun is not visible to it.
import os

MMAUDIO_DIR = "/content/MMAudio"

if not INSTALL_AUDIO:
    log("Ses motoru: atlandı (INSTALL_AUDIO kapalı)")
else:
    if not os.path.isdir(MMAUDIO_DIR):
        run(["git", "clone", "--depth", "1", "https://github.com/hkchengrex/MMAudio.git",
             MMAUDIO_DIR], "clone MMAudio", timeout=300)
    # Editable install: the clone stays the package's source, so nothing is copied twice.
    run(["pip", "install", "-e", ".", "-q"], "pip install MMAudio", cwd=MMAUDIO_DIR, timeout=1800)
    log("MMAudio kütüphanesi kuruldu", "OK")
```

- [ ] **Step 5: Ağırlık hücresini ekle**

```python
# === Ses motoru — MMAudio'nun kendi ağırlıkları (~7 GiB) ===
# A cell of its own, not the one above: a package installed by pip in a cell may not be importable
# yet inside that same cell.
import os

if not INSTALL_AUDIO:
    log("MMAudio ağırlıkları: atlandı (INSTALL_AUDIO kapalı)")
else:
    assert os.path.isdir(APP_DIR), f"❌ Uygulama klasörü yok: {APP_DIR} — önce klon hücresini çalıştır"
    # MMAudio resolves ./weights and ./ext_weights against the WORKING DIRECTORY, and the app is
    # started from APP_DIR -- so this is the only folder where a download counts as installed.
    # Anywhere else and the app would fetch the same files again on its first sound job.
    _cwd = os.getcwd()
    os.chdir(APP_DIR)
    try:
        from mmaudio.eval_utils import all_model_cfg
        all_model_cfg["large_44k"].download_if_needed()   # the app's own model (mmaudio_sampler.py)
    finally:
        os.chdir(_cwd)
    log(f"MMAudio ağırlıkları hazır → {APP_DIR}", "OK")
```

- [ ] **Step 6: Testleri çalıştır**

Run: `python -m pytest queen-editor/backend/tests/test_notebook_installs_the_producer_groups.py -q`
Expected: PASS (dokuz test).

---

### Task 4: Defterin anlatısı + uygulamanın cümlesi

**Files:**
- Test: `queen-editor/backend/tests/test_notebook_installs_the_producer_groups.py` (bir test)
- Modify: `queen-editor/app.ipynb` — `34c9ff58`, `8de17e98`, `4d387058` (markdown), `e086a5a5` (Flask)
- Modify: `queen-editor/frontend/src/features/producers/useProducers.js`
- Modify: `queen-editor/frontend/dist/` (yeniden derlenir)

**Interfaces:**
- Consumes: `COMFY_ROOT`, `APP_DIR` (CONFIG)
- Produces: yok (son görev)

- [ ] **Step 1: Testi ekle**

```python
def test_the_app_is_told_where_the_notebook_installed():
    """The notebook owns the model tree now, so it is the side that names the path -- rather than
    both sides writing /content/ComfyUI and hoping they stay equal."""
    assert '"QE_COMFY_ROOT": COMFY_ROOT' in _source()
```

- [ ] **Step 2: Testi çalıştır, düştüğünü gör**

Run: `python -m pytest queen-editor/backend/tests/test_notebook_installs_the_producer_groups.py -q`
Expected: FAIL — `test_the_app_is_told_where_the_notebook_installed`.

- [ ] **Step 3: Flask hücresini düzelt (`e086a5a5`)**

İki değişiklik:

```python
APP_DIR = os.path.join(CLONE_DIR, "queen-editor")
FLASK_LOG = "/content/flask.log"
```
→
```python
FLASK_LOG = "/content/flask.log"      # APP_DIR CONFIG'de: ses ağırlıkları da oraya iniyor
```

ve:

```python
flask_env = {**os.environ, "QE_DRIVE_ROOT": DRIVE_ROOT, "QE_COMFY_URL": COMFYUI_URL,
             "QE_XAI_API_KEY": XAI_API_KEY or ""}
```
→
```python
flask_env = {**os.environ, "QE_DRIVE_ROOT": DRIVE_ROOT, "QE_COMFY_URL": COMFYUI_URL,
             "QE_COMFY_ROOT": COMFY_ROOT, "QE_XAI_API_KEY": XAI_API_KEY or ""}
```

Aynı hücredeki yorum da düzeltiliyor — "its Drive root, its ComfyUI address and its xAI key" artık dört şey ve biri model ağacı:

```python
# The backend reads its Drive root, its ComfyUI address, the model tree the cells above installed
# into, and its xAI key from the environment (backend/config.py) -- all decided in the cells above,
# not hardcoded in the app. The Civitai cookie is not among them: the app downloads nothing.
```

- [ ] **Step 4: Testi çalıştır**

Run: `python -m pytest queen-editor/backend/tests -q`
Expected: PASS (tüm takım).

- [ ] **Step 5: Giriş markdown'ı (`34c9ff58`)**

```markdown
# Queen Editor — Colab kurulumu

Bu defterin işi kurmak ve sunmak: Drive'ı bağlar → repoyu klonlar → **ComfyUI'yi kurar** (19 custom
node) → **seçtiğin üreticilerin modellerini indirir** → **Flask** arayüzü servis eder →
**cloudflared** linki basar. Üretim uygulamanın içinde oluyor: bir projeye girip kareler üretirsin,
her kare foto ile başlar ve üstüne video, ses katmanı alabilir; hepsi
`MyDrive/queenEditor/<proje>/` altına düşer.

> **Ne kurulacağını CONFIG'deki üç kutu söyler.** Üçü de kapalı gelir; en az birini işaretle.
> Fotoğraf ~8 GiB · video ~37 GiB · ses ~9 GiB. İşaretlemediğin üretici arayüzdeki **Üreticiler**
> panelinde "kurulu değil" görünür — kurulum bu defterin işidir, panelin değil.

> **Runtime → Change runtime type → T4 GPU** gerekiyor. **Video** seçtiysen T4'ün diski yetmez:
> A100 (Colab Pro) iste.

## Kullanım
1. Bu `app.ipynb`'yi Colab'a yükle (**File → Upload notebook**).
2. **🔑 Secrets** panelinde `GITHUB_TOKEN` olmalı (fine-grained, yalnız bu repo, `Contents: read`).
   Fotoğraf ya da video kuracaksan `CIVITAI_COOKIE` de gerekiyor (civitai.red → giriş yap → F12 →
   Application → Cookies → `__Secure-civ-token` değeri; ~30 günde bir yenilenir). Video
   üretecekseniz üçüncüsü: `XAI_API_KEY` — video prompt'unu yazan dil modeli için; yoksa foto
   üretimi yine çalışır.
3. CONFIG'de kurmak istediğin üreticileri işaretle.
4. **Runtime → Run all** → Drive izni ver → seçimine göre ~10-60 dk → en alttaki linke gir.
```

- [ ] **Step 6: ComfyUI markdown'ı (`8de17e98`)**

Son paragraf değişiyor (ses artık kuruluyor):

```markdown
## ComfyUI + Custom Node'lar (19)

İki grafiğin ihtiyacı olan paketler + Manager: ilk sekizi foto grafiği, kalanı video grafiği için.
Liste grafiklerin node künyelerinden çıkarıldı; kalan node'lar comfy-core, kurulum istemez. Biri
başarısız olursa hücre `RuntimeError` ile durur (fail-loud).

> **Node'lar seçime bağlı değil, hepsi kurulur.** Ağır olan modeller; node'lar birkaç dakika. Ses
> ise burada hiç yok: ComfyUI'de üretilmiyor, motoru aşağıda kendi hücresinde kuruluyor.
```

- [ ] **Step 7: Modeller markdown'ı (`4d387058`)**

```markdown
## Modeller — seçilen üreticiler, önce gated probe (~8 / ~37 / ~9 GiB)

CONFIG'de işaretlediğin grupların dosyaları iner; işaretlemediğin hiç denenmez. İndirmeden önce
**disk ölçülür**: yer yetmiyorsa hücre gerçek sayılarla durur, yarım dosya bırakmaz.

Gated erişim **ağır indirmeden önce** doğrulanır (ilk 1 KB): cookie ölmüşse GiB'larca dosyaya
başlamadan, Civitai'nin **gerçek yanıtıyla** durur. Bozuk/eksik dosyada hücre durur; bozuk dosya
silinmez, inceleme için diskte kalır. Dosyalar grafiğin beklediği adlarla iner — ad tutmazsa render
"model bulunamadı" ile düşer.

> **Model eklemek:** ilgili gruba (`CIVITAI_PHOTO`, `OPEN_PHOTO`, `CIVITAI_VIDEO`, `OPEN_VIDEO`,
> `OPEN_AUDIO`) bir satır ekle, yeter — checkpoint klasörüne inen her `.safetensors` arayüzdeki
> **Model** listesinde kendiliğinden görünür. Uygulama hangi modellerin kurulu olduğunu bilmez,
> ComfyUI'ye sorar. Ama arayüzün **Üreticiler** paneli grubun tamamını sayıyor: yeni dosya bir
> üreticinin çalışması için gerekiyorsa `backend/.../model_groups.py`'ye de eklenmeli.
```

- [ ] **Step 8: Arayüzün cümlesi (`useProducers.js`)**

```js
export const COLAB_INSTALL = "Bu üretici Colab defterinden kurulur — app.ipynb'de kutusunu işaretleyip çalıştır.";
```

Testler sabiti import ediyor, metin değişikliği onları kırmıyor.

- [ ] **Step 9: Frontend testleri**

Run: `npm test --prefix queen-editor/frontend`
Expected: PASS (307 test).

- [ ] **Step 10: Derle**

Run: `npm run build --prefix queen-editor/frontend`
Expected: `frontend/dist/` yeniden yazılır.

- [ ] **Step 11: Tam takım**

Run: `python -m pytest queen-editor/backend/tests -q`
Run: `npm test --prefix queen-editor/frontend`
Expected: ikisi de PASS.

- [ ] **Step 12: Commit**

```powershell
git add queen-editor/app.ipynb queen-editor/backend/tests queen-editor/frontend/src queen-editor/frontend/dist docs/superpowers
git commit -m @'
feat(queen-editor): pick what to install before installing it

Uc onay kutusu CONFIG e girdi: isaretlenen ureticinin modelleri iniyor,
otekiler hic denenmiyor. Video ve ses indirmeleri collab-toolbox ta
kanitlanmis hucrelerden geldi; indirme makinesi degismedi.

Ses kutusu MMAudio kutuphanesini de kuruyor ve kendi agirliklarini
uygulamanin calisma dizinine indiriyor -- kutuphane o yollari cwd ye
gore cozuyor, baska yere inen dosyayi uygulama yeniden indirirdi.

Disk indirmeden once olculuyor: ucu birden ~54 GiB.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
'@
```

---

## Self-Review

**Spec kapsamı:** CONFIG kutuları (G1) · seçim assert'i (G1) · koşullu çerez assert'i (G1) · `APP_DIR` (G1) · üç grup + anahtarlar (G2) · disk kontrolü (G2) · ses kütüphanesi + ağırlıkları (G3) · markdown'lar (G4) · `COLAB_INSTALL` (G4) · `QE_COMFY_ROOT` (G4) · testler (hepsi). Spec'te olup planda olmayan madde yok.

**Tip/ad tutarlılığı:** Liste adları tek: `CIVITAI_PHOTO`, `OPEN_PHOTO`, `CIVITAI_VIDEO`, `OPEN_VIDEO`, `OPEN_AUDIO` — testteki `f"{name} if {SWITCH[kind]} else []"` kalıbı bu adları arıyor, hücre de bu adlarla yazıyor (ara takma ad yok; ilk taslakta vardı ve test kalıbını yalancı çıkarıyordu). `MMAU` klasörü `model_groups.py`'deki `{"folder": "mmaudio"}` ile aynı.

**Dikkat:** Görev 1 bittiğinde `test_every_file_the_panel_counts_is_fetched_by_the_notebook` hâlâ kırmızı — bu bilerek, Görev 2 kapatıyor. Görev 1'i "tüm testler yeşil" diye bitirmeye çalışma.
