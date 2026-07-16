# CLAUDE.md

Internal tools monorepo. Her araç kendi alt klasöründe yaşar; kendi `CLAUDE.md`, `requirements.txt` ve giriş noktalarıyla. Yeni araç eklerken: alt klasör + kendi `CLAUDE.md` + `requirements.txt` aç, alttaki **Tools** listesine ekle.

## Çalışma Kuralları

**Gerekmedikçe shell/terminal komutu (Bash, PowerShell, git CLI) çalıştırma.** Keşif, okuma, arama ve düzenleme için özel araçları kullan: Read, Grep, Glob, Edit, Write, NotebookEdit. Dosya okuyarak veya bu araçlarla yapılabilecek bir işi komuta dökme.

**Komut gerçekten gerekiyorsa, önce KESİNLİKLE nedenini açıkça yaz** — hangi işi hangi araçla yapamadığını ve o komutun neyi sağladığını tek cümleyle belirt, sonra çalıştır.

## Tools

- **[collab-toolbox](collab-toolbox/CLAUDE.md)** — Google Colab notebook koleksiyonu: foto/video/ses üretimi (ComfyUI + WAN/SDXL/MMAudio), video dönüştürme, kare çıkarma, watermark tespit & silme. Ortak girdi/çıktı kanalı Google Drive.
- **[desktop-toolbox](desktop-toolbox/CLAUDE.md)** — Masaüstü uygulaması; birden fazla iç aracı modül olarak barındırır. İlk modül: video frame extraction (ilk kare çıkarma).

## Notebook Comment Conventions

Bütün Colab/Jupyter notebook'ları (`.ipynb`) için ortak standart. Amaç: yorumlar kodun **şu an** yaptığını anlatsın, notebook'lar tutarlı olsun.

- **Kapsam:** Yalnızca markdown hücreleri, kod yorumları (`#`) ve docstring'leri yönetir. Sadece yorum güncellenirken **kod değişmez** (print ifadeleri, değerler, fonksiyon mantığı, hücre sırası aynı kalır).
- **Dil — okuyucuya göre ayrılır:**
  - **Türkçe** = insana görünen metin: markdown hücreleri, bölüm başlıkları ve runtime'da basılan string'ler (`print` / `log` / `assert` / `RuntimeError` mesajları).
  - **İngilizce** = koda bakan metin: kod yorumları (`#`) ve docstring'ler.
  - Zaten İngilizce: değişken/fonksiyon adları, kütüphane adları, sözdizimi, URL'ler, kısaltmalar (API, GPU, SRP, NSFW).
- **Üst başlık hücresi** (ilk markdown): `# <Araç> — <amaç>`, ardından `**Input:** … **Output:** …`, sonra numaralı "Sıra" listesi.
- **Bölüm başlıkları:** markdown `## N) Başlık — kısa açıklama` (numaralar ardışık, "Sıra" ile eşleşir). Colab cell-title'da `# @title N) Başlık`.
- **Hücre içi divider:** tek stil `# === sub-section ===`.
- **Yorum NEDEN'i anlatır, NE'yi değil** — kısa, İngilizce. Örn: `MAX_CHUNK_DURATION = 10  # model trained on 8s — large drift hurts quality`.
- **Drift yasağı (en önemli):** yorum/markdown kodun ŞU ANDA halini anlatır; `# ESKI:`/`# YENI:` izleri, eski davranış iddiaları yasak. Çelişkide **yorum koda uydurulur**, kod yoruma değil.
- **Durum-print + fail-loud:** `✓`/`✅` ok, `❌` hata, `⚠️` uyarı, `⏭️` atlama. Ortak `log(msg, level)` helper'ı ve bozuk indirme / başlamayan servis için `RuntimeError` (fail-loud) yerleşik kalıptır (bkz. [collab-toolbox/CLAUDE.md](collab-toolbox/CLAUDE.md)).
- **Hata mesajında sebep uydurma:** hata fırlatırken nedeni tahmin etme — komutun/servisin **gerçek çıktısını** bas (HTTP kodu + yanıt gövdesi, `stderr`/log tail). Tek sabit sebebi hardcode etme (örn. Civitai 401 = "cookie expired" değil; yanlış selector da 401 verir).
