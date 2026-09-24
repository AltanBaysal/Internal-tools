# Madde 314 — Custom node hücresi kısalıyor, implementasyon turunun planı

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*.

**Hedef:** `b9a397f1`'in sekiz kırmızısı yeşile dönsün.

**Yaklaşım:** Döngünün gövdesi `colab/nodes.py`'ye `install_node` olarak taşınıyor; `sam2` satırı
listenin bir kopyasıyla dışarıda kalıyor. Defterde iki hücre değişiyor — hücrelerin kaynağı
NotebookEdit ile bütün olarak yazılıyor, `git diff` yalnız hedef satırları göstermeli. CODE-STANDARD üç
yerde `nodes.py`'yi sayıyor.

**Spec:** [m314 implementasyon turu](../specs/2026-09-23-queen-editor-m314-custom-node-uygulama-design.md)

## Her yere geçerli kurallar

- Kod, yorum ve docstring İngilizce, konsol metinleri Türkçe.
- Defterin kod hücrelerinde yorum yok, yalnız bölüm başlıkları. Defter 29.000 karakteri geçmiyor.
- Testler dört satırla koşulur.

---

## Görev 1: `colab/nodes.py`

**Dosya:** Oluştur: `queen-editor/colab/nodes.py`

- [ ] **Adım 1: Modül.**

```python
"""Custom node installs for the notebook: each node cloned into ComfyUI's custom_nodes and its own
requirements installed, save the lines in SKIPPED.

The list of nodes stays in the notebook, where it is counted against the heading over it; what is here
is how one node comes in, which a cell could not test (madde 314).
"""
import os

from colab.console import log, run

# Impact-Pack's list ends with sam2 straight from GitHub. It has no ready package: pip builds it on the
# machine, and its build asks for torch, which pip installs again -- CUDA libraries and all -- in a
# build environment of its own. Impact-Pack took 3 dk 13 sn of a 6 dk 2 sn cell on the user's run. Our
# photo graph loads SAM's first version through segment-anything, and Impact-Pack imports sam2 only
# when it is installed.
SKIPPED = {"git+https://github.com/facebookresearch/sam2"}


def _kept(req, name):
    """The list pip is handed: the node's own, or a copy of it without the lines in SKIPPED. The copy
    sits beside the original because pip resolves a -r or -c inside a list from where the list is."""
    with open(req, encoding="utf-8") as f:
        lines = f.read().splitlines()
    skipped = [line.strip() for line in lines if line.strip() in SKIPPED]
    if not skipped:
        return req
    for line in skipped:
        log(f"{name}: {line} kurulmuyor — grafiklerimiz kullanmıyor (madde 314)")
    kept = os.path.join(os.path.dirname(req), "requirements.queen-editor.txt")
    with open(kept, "w", encoding="utf-8") as f:
        f.write("".join(f"{line}\n" for line in lines if line.strip() not in SKIPPED))
    return kept


def install_node(name, url, folder):
    """One node into folder/name: cloned shallow with its submodules, and its requirements installed.
    A node already there is left alone, so a second Run all costs nothing. The line a node starts with
    carries the time, and the gap to the next one is how long the node took."""
    target = os.path.join(folder, name)
    if os.path.exists(target) and os.listdir(target):
        log(f"{name}: zaten var")
        return
    log(f"{name}: cloning...")
    run(["git", "clone", "--depth", "1", "--recurse-submodules", url, target], f"clone {name}",
        timeout=180)
    if not os.listdir(target):
        raise RuntimeError(f"{name}: klon sonrası klasör boş")
    req = os.path.join(target, "requirements.txt")
    if os.path.exists(req):
        run(["pip", "install", "-q", "-r", _kept(req, name)], f"pip install {name}", timeout=300)
```

## Görev 2: Defter

**Dosya:** `queen-editor/queeneditor.ipynb` — iki hücre, NotebookEdit ile.

- [ ] **Adım 1: Yardımcılar (`df871d38`)** — `from colab.downloads …` satırının altına:

```python
from colab.nodes import install_node
```

  ve hazır satırı:

```python
print("✓ Ortak yardımcılar hazır (klondan: colab/console.py, colab/downloads.py, colab/nodes.py)")
```

- [ ] **Adım 2: ComfyUI (`8e4cc402`)** — `# === Custom nodes ===` başlığının altındaki `import os` ile
  `%cd /content/ComfyUI/custom_nodes` gidiyor; `CUSTOM_NODES` listesi olduğu gibi; döngü:

```python
for name, url in CUSTOM_NODES:
    install_node(name, url, f"{COMFY_ROOT}/custom_nodes")
```

  `log(f"{len(CUSTOM_NODES)} custom node hazır", "OK")` ve `# === HF downloader ===` bölümü yerinde.

- [ ] **Adım 3: `git diff -U0 --word-diff=porcelain queen-editor/queeneditor.ipynb`** — yalnız bu
  satırlar değişmiş olmalı.

## Görev 3: CODE-STANDARD

**Dosya:** `queen-editor/CODE-STANDARD.md`

- [ ] **Adım 1: `Independence from collab-toolbox` tablosu** — *"The model downloads started as a
  copy too and moved to `colab/` in madde 310, where they run under test"* →
  *"The model downloads and the custom node install started as copies too and moved to `colab/` —
  madde 310 and 314 — where they run under test"*.
- [ ] **Adım 2: `Notebook code (colab/)`** — modüller: *"the console helpers (`console.py`), the model
  downloads (`downloads.py`) and the custom node installs (`nodes.py`)"*; listeler: *"The lists stay in
  the notebook: what to download next to the boxes that choose it, which nodes to install in the
  ComfyUI cell."*
- [ ] **Adım 3: `Tests`** — *"the curl/aria2c call replaced"* → *"the curl/aria2c, git and pip calls
  replaced"*.

## Görev 4: Koşu, commit'ler

- [ ] **Adım 1: Dört satırı koş** — dördü de yeşil.
- [ ] **Adım 2: Yeşil commit** — `nodes.py`, defter, CODE-STANDARD, bu spec ve bu plan:
  `feat(m314): …`.
- [ ] **Adım 3: Yol haritası** — 314 ✅, *Kapandı* notu, *Durum: 22/23*; ayrı `docs(m314)` commit'i.
