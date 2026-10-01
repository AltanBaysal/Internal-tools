# Madde 409 — Fotoğraf üretimi SageAttention ile, uygulama turu

**Koşu:** [Queen Editor v8](../roadmaps/2026-09-25-queen-editor-v8-roadmap.md) · **Dal:**
`feat/queen-editor-v8`, ölçümden sonra en sonda · **Parça:** 409 · v8-4 · **Tur:** 2/2 — kırmızı
testleri yeşile çeviren kod. **Testler:** [m409 test turu](2026-10-01-queen-editor-m409-sageattention-testler-design.md).
**Commit'lenmez:** sahibi Changes'te okur, ve onun onayıyla commit'lenir.

**Kullanıcıdan gereken — yok.** Kararlar test spec'inde: kutu varsayılan işaretli, karar
`colab/attention.py`'de, bayrak yalnız pip "tamam" dedikten sonra.

## Parçalar

### 1. `queen-editor/colab/attention.py` — yeni

Modülün docstring'i kodun söyleyemediğini söyler: bu sahibinin denemesi, varsayılan işaretli, işe
yaramazsa kalkacak *(kullanıcı — "iyi çalışmıyorsa silicem")*; ve neyi değiştirdiği — SDXL'in ve WAN'ın
attention'ı ondan geçer, aynı seed çok yakın ama birebir aynı olmayan resmi verir; H3'ün grafikleri
attention'ı kendisi seçer, MMAudio ComfyUI'nin dışında.

İki sabit, üstlerinde nedenleriyle:

- `PACKAGE = "sageattention==1.0.6"` — PyPI'daki 20 kB'lık, torch'a dokunmayan Triton wheel'i; 2.x
  PyPI'da yok, her taze makinede kaynaktan derlenirdi.
- `LOWEST = 8.0` — Ampere ve sonrası: A100 8.0, L4 8.9, H100 9.0; T4 7.5.

**`sage_attention_flags(wanted)`** — ComfyUI'nin bugünkü komutuna eklenecek bayraklar:

1. `wanted` yanlışsa: `log("SageAttention: atlandı (SAGE_ATTENTION kapalı)")`, `[]`. Karta da pip'e de
   bir şey sorulmaz. Satır, ses motoru hücresinin *"Ses motoru: atlandı (INSTALL_AUDIO kapalı)"*'sıyla
   aynı biçimde.
2. Kart `subprocess.run(["nvidia-smi", "--query-gpu=name,compute_cap", "--format=csv,noheader"],
   capture_output=True, text=True)` ile sorulur; `stdout.strip().rsplit(", ", 1)` adı ve compute
   capability'yi verir.
3. `float(capability) < LOWEST` ise: `log(f"SageAttention: atlandı — {name}, compute capability
   {capability} (en az {LOWEST} gerekiyor)")`, `[]`.
4. Yoksa: `log(f"SageAttention kuruluyor — {name}, compute capability {capability}…")`, sonra
   `run(["pip", "install", PACKAGE], "pip install sageattention", timeout=300)`. pip'in çıktısı
   hücreye akar *(madde 398)*; `-q` verilmez.
5. `run` `RuntimeError` atarsa: `log(f"SageAttention kurulamadı — ComfyUI onsuz başlayacak:\n{failure}",
   "WARN")`, `[]`. Mesaj `run`'ın verdiği: etiket, pip'in çıkış kodu ve pip'in son satırları — sebep
   uydurulmaz.
6. Başarılıysa: `log("SageAttention kuruldu — ComfyUI --use-sage-attention ile başlayacak", "OK")`,
   `["--use-sage-attention"]`.

Fonksiyonun docstring'i neden bayrağın pip'ten sonra geldiğini söyler: paket yokken bayrak verilirse
ComfyUI açılırken kapanıyor (`comfy/ldm/modules/attention.py`); başarısız kurulum hızı götürür,
oturumu değil.

**`colab/console`'dan `log` ve `run`**, `colab/nodes.py` gibi. `subprocess` modül olarak içe
aktarılır, çağrı `subprocess.run(...)`.

**Bilinçli olarak yok:** nvidia-smi'nin cevap vermediği ya da sayı olmayan bir şey döndüğü dal —
CONFIG kartı zaten soruyor ve kart yoksa durduruyor; Colab'ın sürücüleri `compute_cap`'i biliyor.
Olursa `float` kendi hatasıyla, nvidia-smi'nin söylediğini göstererek durur. Kurulumdan sonra ayrı bir
`import sageattention` yoklaması da yok *(test spec'i)*.

### 2. Defter — `queen-editor/queeneditor.ipynb`

**CONFIG** *(`8215086b`)* — video modellerinin kutularının altına, `assert`'lerden önce:

```
#@markdown ---
#@markdown ### SageAttention
#@markdown Modelin attention hesabını hızlandıran bir kütüphane, yalnız destekleyen kartta kurulur.
#@markdown A100, L4 ve H100 destekliyor; T4'te ComfyUI onsuz, eskisi gibi başlar.
#@markdown Açıkken fotoğraf ve WAN videosu aynı seed'le birebir aynı değil, çok yakın çıkar; H3 ve ses değişmez.
#@markdown Kapatınca her kartta eskisi gibi.
SAGE_ATTENTION = True  #@param {type:"boolean"}
```

Her satır bir cümle: Colab satırları ayrı da çizse birleştirse de okunur. Bayrağın adı metinde geçmez
*(test 11)*.

**Yardımcılar hücresi** *(`df871d38`)* — `from colab.attention import sage_attention_flags`, ve son
satır klondan gelen dört dosyayı sayar.

**ComfyUI hücresi** *(`8e4cc402`)* — sona, hf_xet'ten sonra, kendi başlığıyla:

```
# === SageAttention ===
SAGE_FLAGS = sage_attention_flags(SAGE_ATTENTION)
```

Sona, çünkü hücrenin çıktısının son satırları ondan geliyor: sahibi kartın neden atlandığını ya da
kurulduğunu yirmi bir node'un satırları arasında değil, hücrenin sonunda görür.

**Başlatma hücresi** *(`2bc455dd`)* — komut `[... "--port", str(COMFY_PORT)] + SAGE_FLAGS`. Başka bir
şey değişmez.

Defter yaklaşık 700 karakter uzar; tavan 29.000 *(madde 239)*.

### 3. Belgeler

- **README, *Run*:** üretici kutularının paragrafının altına kısa bir paragraf — kutu varsayılan
  işaretli, sahibinin denemesi ve işe yaramazsa kalkacak; destekleyen kartta ComfyUI onunla başlar
  *(hangi kart: `colab/attention.py`)*; fotoğraf ve WAN aynı seed'le çok yakın ama birebir aynı değil;
  H3 ve MMAudio değişmez; kutu kaldırılınca ComfyUI eskisi gibi başlar. README CONFIG'in kutularını
  anlatıyor, ve bu kutu çıktıyı değiştiren tek kutu — kodun söyleyemediği bu.
- **CODE-STANDARD, *Notebook code*:** defterin klondan içe aktardığı modüllerin listesine `attention.py`
  eklenir — liste bugün tam, ve eksik kalırsa yanlış olur.

## Bilinçli olarak yapılmayan

- Workflow'lar (`assets/workflow_*.json`), ComfyUI'nin kodu, `backend/` ve `frontend/` değişmez; dist
  yok.
- `colab/console.py` değişmez.
- Başlatma hücresinin log satırı değişmez: kurulumun satırı bayrağı söylüyor, ve ComfyUI kendi log'una
  *"Using sage attention"* yazıyor.
- Yol haritasına dokunulmaz. Hiçbir şey commit'lenmez.

## Bitti sayılır

Dört satır yeşil: `test_colab_attention.py`'nin sekizi ve defterin dört yeni testi yeşile döner,
bekçiler ve değişen test yeşil kalır, defter tavanın altında.
