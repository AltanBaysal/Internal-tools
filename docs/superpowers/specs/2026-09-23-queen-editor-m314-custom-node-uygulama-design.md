# Madde 314 — Custom node hücresi kısalıyor, implementasyon turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 2/2 — kod, takım yeşile döner.
**Turun testleri:** [m314 test turu](2026-09-23-queen-editor-m314-custom-node-testler-design.md),
`b9a397f1` ile kırmızı commit'lendi.

**Kullanıcıdan gereken:** yok.

## `colab/nodes.py` — yeni

- **`SKIPPED`** — kurulmayan satırlar, bugün tek satır: `git+https://github.com/facebookresearch/sam2`.
  Yorumu sebebini söylüyor: Impact-Pack'in listesinden; hazır paketi yok, pip onu makinede derliyor ve
  derleme ortamına torch'u CUDA kütüphaneleriyle yeniden kuruyor; kullanıcının koşusunda Impact-Pack
  6 dk 2 sn'nin 3 dk 13 sn'si; grafiğimiz SAM'in ilk sürümünü `segment-anything` ile yüklüyor, ve
  Impact-Pack `sam2`'yi yalnız kuruluysa import ediyor. Kural satıra bağlı, node'a değil: aynı satırı
  başka bir liste de isterse o da atlanır ve konsolda görünür.
- **`install_node(name, url, folder)`** — bugünkü döngünün gövdesi, yolları mutlak:
  - Hedef `folder/name`. Varsa ve doluysa `<ad>: zaten var`, dönüş.
  - `<ad>: cloning...` — satırın saati node'un başlangıcı; kullanıcı her node'un süresini bu
    satırların arasından okuyor.
  - `run(["git", "clone", "--depth", "1", "--recurse-submodules", url, hedef], "clone <ad>",
    timeout=180)`.
  - Klasör boşsa `RuntimeError("<ad>: klon sonrası klasör boş")`.
  - `requirements.txt` varsa `run(["pip", "install", "-q", "-r", <liste>], "pip install <ad>",
    timeout=300)`. Komut artık bir liste; bugünkü kabuk dizgesiyle aynı işi yapıyor.
- **`_kept(req, name)`** — pip'e verilecek liste. `SKIPPED`'den satır yoksa node'un kendi listesi.
  Varsa her atlanan satır için
  `<ad>: <satır> kurulmuyor — grafiklerimiz kullanmıyor (madde 314)` basılıyor, ve listenin o satırsız
  kopyası aslının yanına, `requirements.queen-editor.txt` adıyla yazılıyor. Kopya aslının yanında,
  çünkü pip bir listenin içindeki `-r` / `-c` yollarını listenin durduğu yere göre çözüyor. Satırların
  sırası korunuyor.

## Defter

- **Yardımcılar (`df871d38`):** `from colab.nodes import install_node` ekleniyor, ve hazır satırı
  `colab/nodes.py`'yi de sayıyor.
- **ComfyUI (`8e4cc402`), `# === Custom nodes ===` bölümü:** liste kelimesi kelimesine kalıyor. Döngü
  tek çağrıya iniyor:

  ```python
  for name, url in CUSTOM_NODES:
      install_node(name, url, f"{COMFY_ROOT}/custom_nodes")
  ```

  `import os` ile `%cd /content/ComfyUI/custom_nodes` gidiyor: ikisini de yalnız döngü kullanıyordu.
  Sonraki hücreler ya mutlak yol ya kendi `cwd`'leriyle çalışıyor. `N custom node hazır` satırı ve
  `hf_xet` kurulumu yerinde kalıyor.

## CODE-STANDARD

- **`Notebook code (colab/)`:** modüller arasında `nodes.py` da sayılıyor, ve listelerin defterde
  kaldığını söyleyen cümle node listesini de kapsıyor.
- **`Independence from collab-toolbox` tablosu:** kopya olarak başlayıp `colab/`'a taşınanlar
  arasında custom node kurulumu da var — madde 314.
- **`Tests`:** sahte olan çağrılar arasında git ve pip de var.

## Bitti sayılır

Dört test satırı koşulur ve dördü de yeşil. Defter 29.000 karakter tavanının altında kalır.
