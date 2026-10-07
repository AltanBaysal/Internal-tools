# Madde 310 — HF indiricisi, implementasyon turunun planı

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*.

**Hedef:** `2944861c`'nin kırmızısı yeşile dönsün: indirme kodu `colab/`'a taşınır, HF dosyaları
`hf_fetch` ile iner, her indirme kaynağını ve hızını basar.

**Yaklaşım:** Modülün fonksiyonları defterden olduğu gibi taşınıyor; yeni olan `hf_fetch`, tek
yargı (`_judge` / `_settled`) ve hız satırı (`_landed`). Defterde üç hücre `NotebookEdit` ile
yeniden yazılıyor; değişmeyen satırlar harfi harfine kalıyor.

**Araçlar:** Python stdlib, `huggingface_hub.hf_hub_download` (Colab'da, fonksiyonun içinde import),
`hf_xet`.

**Spec:** [m310 implementasyon turu](../specs/2026-09-23-queen-editor-m310-hf-indirici-uygulama-design.md)

## Her yere geçerli kurallar

- Kod, yorum, docstring **İngilizce**; konsol metinleri **Türkçe**, defterden olduğu gibi.
- Defterin kod hücrelerinde yorum yok, yalnız `# === … ===` başlıkları *(madde 239)*.
- `colab/` uygulamadan hiçbir şey import etmiyor; uygulama `colab/`'ı import etmiyor.
- Testler dört satırla koşulur; `skip` / `xfail` yok.

---

## Görev 1: `colab/`

**Dosyalar:** Oluştur: `queen-editor/colab/__init__.py` *(boş)*, `queen-editor/colab/console.py`,
`queen-editor/colab/downloads.py`

**Arayüzler:** testlerin beklediği adlar — `STAGE`, `check_safetensors`, `check_binary`,
`strip_unreferenced_tail`, `fetch(url, target_dir, filename, label, *, parallel, headers=None,
floor=None)`, `hf_fetch(repo, path, target_dir, filename, label, *, floor=None)`, `civitai_url`,
`cookie_header(cookie)`, `civitai_probe(version_id, label, cookie)`; `downloads` `run`'ı kendi ad
alanında tutuyor.

- [ ] **Adım 1: `console.py`**

```python
"""What every notebook cell prints and runs with.

The notebook imports these from its clone (madde 310). They were cells before, and a cell never runs
under pytest.
"""
import os
import subprocess
import time


def log(msg, level="INFO"):
    icons = {"INFO": "ℹ️ ", "OK": "✅", "WARN": "⚠️ ", "ERR": "❌"}
    print(f"{icons.get(level, '·')} [{time.strftime('%H:%M:%S')}] {msg}")


def human(b):
    for u in ["B", "KB", "MB", "GB"]:
        if b < 1024:
            return f"{b:.1f}{u}"
        b /= 1024
    return f"{b:.1f}TB"


def head_text(path, limit=4000):
    """The start of a file as text: how a failed download shows what actually came down -- an error
    page, more often than not."""
    if not os.path.exists(path):
        return "(dosya yok)"
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        text = f.read(limit).decode("utf-8", errors="replace")
    return text + (f"\n… (+{human(size - limit)})" if size > limit else "")


def run(cmd, label, cwd=None, timeout=3600):
    """A shell call that fails loud, with the command's own last lines rather than a guessed cause."""
    try:
        r = subprocess.run(cmd, shell=isinstance(cmd, str), cwd=cwd,
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"{label}: timeout ({timeout}s)")
    if r.returncode != 0:
        tail = "\n".join((r.stderr or r.stdout or "").strip().splitlines()[-5:])
        raise RuntimeError(f"{label}: exit {r.returncode}\n{tail}")
    return r.stdout
```

- [ ] **Adım 2: `downloads.py`** — `check_safetensors`, `check_binary`, `strip_unreferenced_tail` ve
  `civitai_probe`'un gövdesi defterden harfi harfine; yeni olanlar:

```python
"""Model downloads for the notebook: every file comes down validated, and its line says where it came
from and how fast.

The lists of what to download stay in the notebook, next to the boxes that choose them -- addresses
live there (FOUNDATION 9). What is here is how a file comes down, which a cell could not test.
"""
import json
import os
import struct
import subprocess
import time

from colab.console import head_text, human, log, run

# hf_hub_download writes the repo's folders and its own .cache under local_dir. Neither belongs among
# ComfyUI's models, so a file lands here and is moved into place: a rename on one disk, not a copy.
STAGE = "/content/hf_stage"


def _judge(path, label, floor):
    """A file with a floor -- .pth, .pt -- has no header to read and is judged by its size. A
    safetensors first loses the stamp some quantizers leave after the last tensor (NOTEBOOK-STANDARD,
    section 3)."""
    if floor:
        return check_binary(path, floor)
    strip_unreferenced_tail(path, label)
    return check_safetensors(path)


def _settled(path, label, floor):
    """The verdict's message, or a RuntimeError showing how the file starts. A bad file is never
    passed on and never deleted: it stays where it is, for inspection."""
    state, msg = _judge(path, label, floor)
    if state != "ok":
        raise RuntimeError(f"{label}: {state} — {msg}\n{path}\n--- file head ---\n{head_text(path)}")
    return msg


def _landed(label, source, size, took, msg):
    log(f"{label}: indirildi — {source}, {human(size)}, {took:.0f} sn, "
        f"{size / took / 2**20:.1f} MB/s ({msg})", "OK")


def fetch(url, target_dir, filename, label, *, parallel, headers=None, floor=None):
    """A file by its address. parallel=True is aria2c's sixteen connections. A gated file goes by
    curl: Civitai redirects to its store, the store answers 403 when the login cookie comes along,
    and curl drops the cookie when the host changes where aria2c carries it."""
    target = os.path.join(target_dir, filename)
    part = target + ".part"
    hdrs = f"/tmp/{filename}.headers"

    if os.path.exists(target):
        log(f"{label}: zaten var ({_settled(target, label, floor)})")
        return

    resume = False
    if os.path.exists(part):
        state, msg = _judge(part, label, floor)
        if state == "invalid":
            raise RuntimeError(f"{label}: .part {state} — {msg}\n{part}\n--- file head ---\n{head_text(part)}")
        if state == "ok":
            log(f"{label}: .part zaten tam ({msg}) — indirilmiyor")
        else:
            log(f"{label}: .part'tan devam ({msg})")
            resume = True

    start, before = time.perf_counter(), (os.path.getsize(part) if os.path.exists(part) else 0)
    if not os.path.exists(part) or resume:
        log(f"{label}: iniyor")
        if parallel:
            cmd = ["aria2c", "-x", "16", "-s", "16", "-k", "1M", "--continue=true",
                   "--console-log-level=warn", "--auto-file-renaming=false",
                   "--allow-overwrite=true", "-d", target_dir, "-o", os.path.basename(part)]
            if headers:
                cmd += ["--header", headers]
        else:
            cmd = ["curl", "-L", "-C", "-", "--fail-with-body", "--max-time", "7200",
                   "-D", hdrs, "-o", part]
            if headers:
                cmd += ["-H", headers]
        cmd.append(url)
        try:
            run(cmd, label, timeout=7200)
        except RuntimeError as e:
            raise RuntimeError(
                f"{e}\n{url.split('?')[0]}\n"
                f"--- response headers ---\n{head_text(hdrs)}\n"
                f"--- response body ---\n{head_text(part)}"
            ) from None

    state, msg = _judge(part, label, floor)
    if state != "ok":
        raise RuntimeError(f"{label}: {state} — {msg}\n{part}\n{url.split('?')[0]}\n"
                           f"--- response headers ---\n{head_text(hdrs)}\n"
                           f"--- file head ---\n{head_text(part)}")
    os.replace(part, target)
    _landed(label, url.split("/")[2], os.path.getsize(target) - before,
            time.perf_counter() - start, msg)


def hf_fetch(repo, path, target_dir, filename, label, *, floor=None):
    """A file by its repo and path, through Hugging Face's own downloader. With hf_xet behind it the
    file's Xet chunks come straight from storage in parallel; an address went through HF's bridge,
    which cuts a plain download to 8.7 MB/s on most of its servers (xet-core #821)."""
    # Imported here: Colab ships it, and this module has to import where it is not installed.
    from huggingface_hub import hf_hub_download

    target = os.path.join(target_dir, filename)
    if os.path.exists(target):
        log(f"{label}: zaten var ({_settled(target, label, floor)})")
        return

    log(f"{label}: iniyor (HF)")
    start = time.perf_counter()
    try:
        got = hf_hub_download(repo, path, local_dir=STAGE)
    except Exception as e:
        raise RuntimeError(f"{label}: HF {repo}/{path} — {type(e).__name__}: {e}") from None
    msg = _settled(got, label, floor)
    os.replace(got, target)
    _landed(label, "HF", os.path.getsize(target), time.perf_counter() - start, msg)


def civitai_url(version_id):
    return f"https://civitai.red/api/download/models/{version_id}"


def cookie_header(cookie):
    return f"Cookie: __Secure-civ-token={cookie}"
```

  `civitai_probe(version_id, label, cookie)`: gövde defterdeki, `cookie_header()` yerine
  `cookie_header(cookie)`.

## Görev 2: Defter

**Dosyalar:** Değiştir: `queen-editor/queeneditor.ipynb` — hücreler `df871d38`, `8e4cc402`, `f0df85b4`.

- [ ] **Adım 1: Yardımcılar hücresi (`df871d38`)** — tamamı:

```python
# === Shared helpers ===
import sys

assert "COMFY_ROOT" in globals(), "❌ Önce 1) CONFIG hücresini çalıştır"

for _name in [n for n in sys.modules if n == "colab" or n.startswith("colab.")]:
    del sys.modules[_name]
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)
from colab.console import log, human, run
from colab.downloads import fetch, hf_fetch, civitai_url, cookie_header, civitai_probe

print("✓ Ortak yardımcılar hazır (klondan: colab/console.py, colab/downloads.py)")
```

- [ ] **Adım 2: Sistem hücresi (`8e4cc402`)** — sonuna:

```python
# === HF downloader ===
!pip install -q -U hf_xet
```

- [ ] **Adım 3: Modeller hücresi (`f0df85b4`)**:
  - İlk satır `import os, glob, shutil`.
  - `check_binary`, `strip_unreferenced_tail`, `# === Download ===`, `# === Civitai ===` bölümleri
    gidiyor.
  - HF listeleri, satır `(repo, yol, klasör, dosya adı, etiket, taban)`:

```python
HF_PHOTO = [
    ("FacehugmanIII/4x_foolhardy_Remacri", "4x_foolhardy_Remacri.pth",
     UPSC, "4x_foolhardy_Remacri.pth", "Remacri 4x upscaler", 50_000_000),
    ("Bingsu/adetailer", "face_yolov9c.pt",
     BBOX, "face_yolov9c.pt", "Yuz dedektoru (yolov9c)", 40_000_000),
]
OPEN_PHOTO = [
    ("https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth",
     SAMS, "sam_vit_b_01ec64.pth", "SAM ViT-B", 300_000_000),
]

WAN22 = "Comfy-Org/Wan_2.2_ComfyUI_Repackaged"
WAN21 = "Comfy-Org/Wan_2.1_ComfyUI_repackaged"
HF_VIDEO = [
    (WAN22, "split_files/loras/wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors",
     LORA, "wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors", "Lightx2v I2V HIGH", None),
    (WAN22, "split_files/loras/wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors",
     LORA, "wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors", "Lightx2v I2V LOW", None),
    (WAN21, "split_files/vae/wan_2.1_vae.safetensors",
     VAE, "Wan2_1_VAE_fp32.safetensors", "Wan2.1 VAE", None),
    (WAN21, "split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors",
     TENC, "umt5_xxl_fp8_e4m3fn_scaled.safetensors", "UMT5-XXL", None),
    (WAN21, "split_files/clip_vision/clip_vision_h.safetensors",
     CLIPV, "clip_vision_h.safetensors", "CLIP Vision H", None),
]

HF_H3 = [
    ("Abiray/MiniMax-H3-GGUF", "text_encoders/qwen3vl_32b_minimax_h3_int4_convrot.safetensors",
     TENC, "qwen3vl_32b_minimax_h3_int4_convrot.safetensors", "H3 Qwen3-VL", None),
    ("Kijai/MiniMax-H3-experimental", "minimax_h3_video_vae_int8_convrot.safetensors",
     H3VAE, "minimax_h3_video_vae_int8_convrot.safetensors", "H3 video VAE", None),
    ("Comfy-Org/MiniMax-H3", "vae/minimax_h3_audio_vae_fp32.safetensors",
     H3VAE, "minimax_h3_audio_vae_fp32.safetensors", "H3 ses VAE", None),
    ("Kijai/MiniMax-H3-TAE", "vae_approx/taeh3.safetensors",
     TAE, "taeh3.safetensors", "H3 TAE", None),
]

HF_AUDIO = [
    ("phazei/NSFW_MMaudio", "mmaudio_large_44k_nsfw_gold_8.5k_final_fp16.safetensors",
     MMAU, "mmaudio_large_44k_nsfw_gold_8.5k_final_fp16.safetensors", "MMAudio NSFW fine-tune",
     None),
]
```

  - İşler ve indirmeler:

```python
hf_jobs = ((HF_PHOTO if INSTALL_PHOTO else [])
           + (HF_VIDEO if VIDEO_MODEL == "wan" else [])
           + (HF_H3 if VIDEO_MODEL == "h3" else [])
           + (HF_AUDIO if INSTALL_AUDIO else []))
open_jobs = OPEN_PHOTO if INSTALL_PHOTO else []

# === Gated probe ===
if civitai_jobs:
    log(f"Gated probe: {len(civitai_jobs)} asset")
    for vid, d, fn, label in civitai_jobs:
        civitai_probe(vid, label, COOKIE_VALUE)

# === Hugging Face downloads ===
for repo, path, d, fn, label, floor in hf_jobs:
    hf_fetch(repo, path, d, fn, label, floor=floor)

# === Open downloads ===
for url, d, fn, label, floor in open_jobs:
    fetch(url, d, fn, label, parallel=True, floor=floor)

# === Civitai downloads ===
for vid, d, fn, label in civitai_jobs:
    fetch(civitai_url(vid), d, fn, label, parallel=False, headers=cookie_header(COOKIE_VALUE))
```

- [ ] **Adım 4: Artık** — defterde `head_text`, `check_safetensors`, `check_binary`, `json.`,
  `struct.` ve `time.`'a başka bir hücrenin dayanıp dayanmadığı Grep ile aranır; kendi import'u
  olmayan bir kullanıcı çıkarsa o hücreye import eklenir.

## Görev 3: CODE-STANDARD, koşu, commit'ler

- [ ] **Adım 1: "Setup cells" satırı** — sol hücre:

```markdown
Setup cells — custom nodes, headless ComfyUI — copied **verbatim** into `queeneditor.ipynb`, because that machinery is proven. The model downloads started as a copy too and moved to `colab/` in madde 310, where they run under test
```

- [ ] **Adım 2: Yeni bölüm**, `## Infrastructure (backend/web/)`'in altına:

```markdown
## Notebook code (`colab/`)
The notebook's own code: what `queeneditor.ipynb` imports from its clone — the console helpers
(`console.py`) and the model downloads (`downloads.py`). It sits outside `backend/` because the app
downloads nothing ([FOUNDATION 9](FOUNDATION.md)): the app never imports `colab/`, and `colab/`
imports nothing from the app. The lists of what to download stay in the notebook, next to the boxes
that choose them. Why a module and not cells: a cell never runs under pytest, and the notebook has a
size ceiling (madde 239).
```

- [ ] **Adım 3: Tests bölümüne bir paragraf:**

```markdown
Notebook code: `colab/` runs under pytest with the network faked — Hugging Face's downloader swapped
in `sys.modules`, the curl/aria2c call replaced — and real files on disk.
```

- [ ] **Adım 4: Dört satırı koş** — dördü de yeşil.

- [ ] **Adım 5: Yeşil commit** — `colab/`, defter, CODE-STANDARD, bu spec ve bu plan.

- [ ] **Adım 6: Yol haritası** — 310 ✅, *Kapandı* notu commit'lerin kısa hash'iyle, *Durum:
  19/20*; ayrı `docs(m310)` commit'i.

## Beklenen

Dört satır yeşil: `2944861c`'nin yirmi kırmızısı döner, defterin boyutu tavanın çok altına iner.
