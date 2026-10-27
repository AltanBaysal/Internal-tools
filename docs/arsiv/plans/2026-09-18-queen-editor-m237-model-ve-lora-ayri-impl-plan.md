# Madde 237 · Model ve LoRA ayrı iki kutu — uygulama turunun planı

**Spec:** [uygulama turu](../specs/2026-09-18-queen-editor-m237-model-ve-lora-ayri-uygulama-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

## Adımlar

**1 · Katalog.** `domain/catalog.py` yazılır, `domain/recipes.py` silinir. `list_models.py`'ye
`list_loras`.

**2 · Render ve çağrı şekli.** `comfy_photo_generator.py` model ve LoRA'yı ayrı çözer. `ports.py`,
`run_loop.py`, video ve ses üreticileri `lora` alır.

**3 · Plan.** `start_batch.py`, `regenerate.py`, `plan_store.py`.

**4 · Uç nokta ve bağlama.** `routes.py`, `config.py`, `main.py`; `test_photo_routes.py`'nin
`make_client`'ı.

**5 · Defter.** CONFIG, giriş ve modeller açıklamaları, modeller hücresi *(probe düzeltmesi dahil)*,
Flask hücresi. Diff kelime kelime okunur.

**6 · Ön yüz.** `api.js`, `useModels.js`, `GeneratePanel.jsx`, `ProjectScreen.jsx`,
`SidePanel.jsx`, `PhotoDetail.jsx`.

**7 · Takım koşulur**, dördü de. Beklenen: hepsi yeşil.

**8 · `npm run build --prefix queen-editor/frontend`**, `dist/` kaynakla aynı commit'e girer.

**9 · Yol haritasında 237 işaretlenir**, Durum 23/26 olur. Commit'lenir ve push edilir.
