# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Internal tools monorepo. Each tool lives in its own subfolder with its own `CLAUDE.md`, `requirements.txt`, and entry points.

## Çalışma Kuralları

**Gerekmedikçe shell/terminal komutu (Bash, PowerShell, git CLI) çalıştırma.** Keşif, okuma, arama ve düzenleme için özel araçları kullan: Read, Grep, Glob, Edit, Write, NotebookEdit. Dosya okuyarak veya bu araçlarla yapılabilecek bir işi komuta dökme.

**Komut gerçekten gerekiyorsa, önce KESİNLİKLE nedenini açıkça yaz** — hangi işi hangi araçla yapamadığını ve o komutun neyi sağladığını tek cümleyle belirt, sonra çalıştır.

## Repository Structure

```
internal-tools/
├── collab-toolbox/           # Colab notebook koleksiyonu (AI medya üretim/temizleme araçları)
│   └── CLAUDE.md             # Tool-specific docs
├── desktop-toolbox/          # Desktop app bundling multiple internal tools (first module: video frame extraction)
│   └── CLAUDE.md             # Tool-specific docs
├── .gitignore
└── CLAUDE.md                 # This file (root index)
```

## Tools

- **[collab-toolbox](collab-toolbox/CLAUDE.md)** — Google Colab notebook koleksiyonu: foto/video/ses üretimi (ComfyUI + WAN/SDXL/MMAudio), video dönüştürme, kare çıkarma, watermark tespit & silme. Ortak girdi/çıktı kanalı Google Drive.
- **[desktop-toolbox](desktop-toolbox/CLAUDE.md)** — Masaüstü uygulaması; birden fazla iç aracı modül olarak barındırır. İlk modül: video frame extraction (ilk kare çıkarma).

## Adding a New Tool

1. Create a new subfolder: `my-tool/`
2. Add a `CLAUDE.md` inside it with commands, architecture, and design decisions
3. Add a `requirements.txt` for its dependencies
4. Add the tool to the **Tools** list above

## Notebook Comment Conventions

Bütün Colab/Jupyter notebook'ları (`.ipynb`) için ortak standart. Amaç: yorumlar kodun **şu an** yaptığını anlatsın, notebook'lar tutarlı olsun.

- **Kapsam:** Yalnızca markdown hücreleri, kod yorumları (`#`) ve docstring'leri yönetir. Sadece yorum güncellenirken **kod değişmez** (print ifadeleri, değerler, fonksiyon mantığı, hücre sırası aynı kalır).
- **Dil — okuyucuya göre ayrılır:**
  - **Türkçe** = insana görünen metin: markdown hücreleri, bölüm başlıkları ve runtime'da basılan string'ler (`print` / `log` / `assert` / `RuntimeError` mesajları).
  - **İngilizce** = koda bakan metin: kod yorumları (`#`) ve docstring'ler.
  - Zaten İngilizce: değişken/fonksiyon adları, kütüphane adları, sözdizimi, URL'ler, kısaltmalar (API, GPU, SRP, NSFW).
- **Üst başlık hücresi** (ilk markdown): `# <Araç> — <amaç>`, ardından `**Input:** … **Output:** …`, sonra numaralı "Sıra" listesi.
- **Bölüm başlıkları:** markdown `## N) Başlık — kısa açıklama` (numaralar ardışık, "Sıra" ile eşleşir). Colab cell-title'da `# @title N) Başlık`.
- **Hücre içi divider:** tek stil `# === sub-section ===` (`# ════`, `# >>>>`, `# ----` buna sadeleşir).
- **Yorum NEDEN'i anlatır, NE'yi değil** — kısa, İngilizce. Config satırında aynı satırda: `MAX_CHUNK_DURATION = 10  # model trained on 8s — large drift hurts quality`.
- **Drift yasağı (en önemli):** yorum/markdown kodun ŞU ANDA halini anlatır; `# ESKI:`/`# YENI:` izleri, eski davranış iddiaları yasak. Çelişkide **yorum koda uydurulur**, kod yoruma değil.
- **Durum-print + fail-loud:** `✓`/`✅` ok, `❌` hata, `⚠️` uyarı, `⏭️` atlama. Ortak `log(msg, level)` helper'ı ve bozuk indirme / başlamayan servis için `RuntimeError` (fail-loud) yerleşik kalıptır (bkz. [collab-toolbox/CLAUDE.md](collab-toolbox/CLAUDE.md)).
