# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Internal tools monorepo. Each tool lives in its own subfolder with its own `CLAUDE.md`, `requirements.txt`, and entry points.

## Repository Structure

```
internal-tools/
├── desktop-toolbox/          # Desktop app bundling multiple internal tools (first module: video frame extraction)
│   └── CLAUDE.md             # Tool-specific docs
├── mmaudio-generate/         # Text-to-audio generation with MMAudio
│   └── CLAUDE.md             # Tool-specific docs
├── .gitignore
└── CLAUDE.md                 # This file (root index)
```

## Tools

- **[desktop-toolbox](desktop-toolbox/CLAUDE.md)** — Masaüstü uygulaması; birden fazla iç aracı modül olarak barındırır. İlk modül: video frame extraction (ilk kare çıkarma).
- **[mmaudio-generate](mmaudio-generate/CLAUDE.md)** — MMAudio modeli ile metin açıklamasından ses dosyası üretme (text-to-audio).

## Adding a New Tool

1. Create a new subfolder: `my-tool/`
2. Add a `CLAUDE.md` inside it with commands, architecture, and design decisions
3. Add a `requirements.txt` for its dependencies
4. Add the tool to the **Tools** list above

## Notebook Comment Conventions

Bütün Colab/Jupyter notebook'larında (`.ipynb`) ortak yorum & dokümantasyon standardı. Amaç: yorumların kodun **şu an** yaptığını doğru anlatması ve notebook'lar arası tutarlılık.

**Kural 0 — Kapsam:** Bu konvansiyon yalnızca **markdown hücrelerini, kod yorumlarını (`#`) ve docstring'leri** yönetir. Mevcut bir notebook'un yorumları güncellenirken **kod değiştirilmez** — `print(...)` ifadeleri, değişken değerleri, fonksiyon mantığı ve hücre sırası aynı kalır.

**Kural 1 — Dil:** İnsan-okur metin (markdown, yorum, docstring) **Türkçe**. İngilizce yalnızca: değişken/fonksiyon adları, kütüphane adları, kod sözdizimi, URL'ler ve yerleşik kısaltmalar (API, GPU, SRP, NSFW).

**Kural 2 — Üst başlık hücresi** (her notebook'un ilk markdown hücresi):
```
# <Araç Adı> — <tek satır amaç>

**Input:** ... | **Output:** ... | **Model/Veri:** ...

Sıra:
1. **CONFIG** — ...
2. ...
```

**Kural 3 — Bölüm başlıkları:** Her ana adım için markdown hücresi
```
## N) Başlık — kısa açıklama
```
Colab cell-title kullanan kod hücrelerinde:
```
# @title N) Başlık
```
Numaralar ardışık ve üst başlıktaki "Sıra" listesiyle eşleşir.

**Kural 4 — Banner/divider yorumu** (büyük hücre içi alt bölümler için tek standart):
```
# === Alt bölüm adı ===
```
Karışık `# ════`, `# >>>>`, `# ----` stilleri buna sadeleştirilir.

**Kural 5 — Inline yorum:** NE değil **NEDEN** anlatır, Türkçe. Config değişkenlerinde aynı satırda:
```python
MAX_CHUNK_DURATION = 10   # Model 8s'de eğitilmiş — büyük sapma kaliteyi düşürür
```

**Kural 6 — Docstring:** Türkçe, üç tırnak, tek cümle amaç/davranış:
```python
def composite_inpaint(...):
    """Orijinali base alır, sadece mask bölgesini inpaint çıktısından yapıştırır."""
```

**Kural 7 — Drift yasağı (en önemli):** Yorum/markdown kodun ŞU ANDA yaptığını anlatmalı. `# ESKI:`/`# YENI:` evrim izleri, eski boyut/davranış iddiaları, kullanılmayan değerlerin "aktifmiş gibi" anlatımı yasak. Kod ile yorum çelişiyorsa **yorum koda uydurulur** (kod asla yoruma uydurulmaz).

**Kural 8 — Durum-print stili** (yalnız **yeni** notebook'lar için öneri; mevcut print'ler kod olduğu için değiştirilmez): `✓` başarı, `❌` hata, `⚠️` uyarı, `⏭️` atlama. İsteğe bağlı ortak helper:
```python
def log(msg, level="INFO"):
    icons = {"INFO": "ℹ️ ", "OK": "✅", "WARN": "⚠️ ", "ERR": "❌"}
    print(f"{icons[level]} [{time.strftime('%H:%M:%S')}] {msg}")
```
