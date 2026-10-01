# Madde 409 — Fotoğraf üretimi SageAttention ile, uygulama turunun planı

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*. **Commit yok** — sahibi
> değişikliği VS Code'un Changes'inde okur *(kullanıcı, 1 Ekim)*.

**Hedef:** Test turunun on iki kırmızısı yeşil; geri kalan her şey — defterin tavanı dahil — yeşil
kalır.

**Yaklaşım:** Karar `colab/attention.py`'de tek fonksiyon; defter kutuyu çizer, fonksiyonu ComfyUI
hücresinde çağırır, ve dönen bayrakları başlatma komutuna ekler.

**Araçlar:** Python standart kütüphanesi (`subprocess`), `colab.console`.

**Spec:** [m409 uygulama turu](../specs/2026-10-01-queen-editor-m409-sageattention-uygulama-design.md)

## Her yere geçerli kurallar

- Kod ve yorumlar **İngilizce**; konsol satırları ve defterin markdown'ı **Türkçe**.
- Defterin kod hücrelerinde yorum yok, yalnız bölüm başlıkları. `BRANCH` satırına dokunulmaz. Defter
  29.000 karakteri geçmiyor.
- Workflow'lar, ComfyUI'nin kodu, `backend/` ve `frontend/` değişmez; dist yok.

---

## Görev 1: `colab/attention.py`

**Dosya:** Oluştur: `queen-editor/colab/attention.py`

- [ ] **Adım 1: Modül.**

```python
"""SageAttention for ComfyUI, on the cards that can run it (madde 409).

The owner's trial: a CONFIG box, ticked by default, to be taken out again if it does not pay ("iyi
çalışmıyorsa silicem"). It changes what comes out. SDXL's attention and WAN's run through it, so a
photo or a WAN video from the same seed comes out very close to, not the same as, one made without
it. H3's graphs pick their own attention backend, and MMAudio runs outside ComfyUI.
"""
import subprocess

from colab.console import log, run

# The build PyPI holds: a 20 kB wheel of Triton kernels that leaves torch alone. 2.x is not on PyPI,
# and would be compiled from source on every fresh machine.
PACKAGE = "sageattention==1.0.6"

# Ampere and later, the cards the kernels are written for: A100 is 8.0, L4 8.9, H100 9.0; a T4 is 7.5.
LOWEST = 8.0


def sage_attention_flags(wanted):
    """What ComfyUI's command gets on top of today's: --use-sage-attention, or nothing.

    The flag comes only after pip said yes. Given it without the package, ComfyUI exits while it
    starts (comfy/ldm/modules/attention.py), so a failed install costs the speed-up and never the
    session."""
    if not wanted:
        log("SageAttention: atlandı (SAGE_ATTENTION kapalı)")
        return []
    card = subprocess.run(["nvidia-smi", "--query-gpu=name,compute_cap", "--format=csv,noheader"],
                          capture_output=True, text=True)
    name, capability = card.stdout.strip().rsplit(", ", 1)
    if float(capability) < LOWEST:
        log(f"SageAttention: atlandı — {name}, compute capability {capability} "
            f"(en az {LOWEST} gerekiyor)")
        return []
    log(f"SageAttention kuruluyor — {name}, compute capability {capability}…")
    try:
        run(["pip", "install", PACKAGE], "pip install sageattention", timeout=300)
    except RuntimeError as failure:
        log(f"SageAttention kurulamadı — ComfyUI onsuz başlayacak:\n{failure}", "WARN")
        return []
    log("SageAttention kuruldu — ComfyUI --use-sage-attention ile başlayacak", "OK")
    return ["--use-sage-attention"]
```

## Görev 2: Defter

**Dosya:** Değiştir: `queen-editor/queeneditor.ipynb`

- [ ] **Adım 1: CONFIG** *(`8215086b`)* — `VIDEO_H3 = False  #@param {type:"boolean"}` satırının
  altına:

```
#@markdown ---
#@markdown ### SageAttention
#@markdown Modelin attention hesabını hızlandıran bir kütüphane, yalnız destekleyen kartta kurulur.
#@markdown A100, L4 ve H100 destekliyor; T4'te ComfyUI onsuz, eskisi gibi başlar.
#@markdown Açıkken fotoğraf ve WAN videosu aynı seed'le birebir aynı değil, çok yakın çıkar; H3 ve ses değişmez.
#@markdown Kapatınca her kartta eskisi gibi.
SAGE_ATTENTION = True  #@param {type:"boolean"}
```

- [ ] **Adım 2: Yardımcılar** *(`df871d38`)* — `from colab.nodes import install_node`'un altına
  `from colab.attention import sage_attention_flags`; son satır:

```python
print("✓ Ortak yardımcılar hazır (klondan: colab/console.py, colab/downloads.py, colab/nodes.py, "
      "colab/attention.py)")
```

- [ ] **Adım 3: ComfyUI hücresi** *(`8e4cc402`)* — `!pip install -q -U hf_xet`'in altına:

```
# === SageAttention ===
SAGE_FLAGS = sage_attention_flags(SAGE_ATTENTION)
```

- [ ] **Adım 4: Başlatma hücresi** *(`2bc455dd`)* — komut satırı:

```python
    ["python", "main.py", "--listen", "127.0.0.1", "--port", str(COMFY_PORT)] + SAGE_FLAGS,
```

## Görev 3: Belgeler

- [ ] **Adım 1: README, *Run*** — üretici kutularının paragrafının altına:

```markdown
`SAGE_ATTENTION` comes ticked: the owner's trial of SageAttention, to be taken out if it does not
pay (madde 409). Where the card can run it — [colab/attention.py](colab/attention.py) says which —
ComfyUI starts with it, and a photo or a WAN video from the same seed comes out very close to, not
the same as, one made without it; H3 picks its own attention, and MMAudio runs outside ComfyUI.
Untick it and ComfyUI starts as before.
```

- [ ] **Adım 2: CODE-STANDARD, *Notebook code*** — modül listesi:
  `the console helpers (`console.py`), the model downloads (`downloads.py`), the custom node installs
  (`nodes.py`) and SageAttention (`attention.py`)`.

## Görev 4: Koşu

- [ ] **Adım 1: Dört satırı koş**, paralel, yazıldığı gibi — hepsi yeşil; defter tavanın altında.
- [ ] **Adım 2: Commit yok.** Kod, defter, belgeler, spec'ler ve planlar çalışma ağacında kalır.
