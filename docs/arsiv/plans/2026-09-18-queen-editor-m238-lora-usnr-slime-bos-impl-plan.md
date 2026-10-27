# Madde 238 · LoRA kutusu: USNR, Slime, Boş — uygulama turunun planı

**Spec:** [uygulama turu](../specs/2026-09-18-queen-editor-m238-lora-usnr-slime-bos-uygulama-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

## Adımlar

**1 · Katalog ve liste.** `domain/catalog.py`, `list_models.py`.

**2 · Render.** `comfy_photo_generator.py`; `ports.py` ve `plan_store.py`'nin yorumları.

**3 · Kuyruk isteği.** `start_batch.py` (`InvalidLora`), `routes.py`.

**4 · Ayarlar.** `settings_store.py`, `save_settings.py`, projects `routes.py`.

**5 · Ön yüz.** `api.js`, `ProjectScreen.jsx`, `useModels.js`, `GeneratePanel.jsx`,
`PhotoDetail.jsx`.

**6 · Yorumlar.** `model_groups.py` ve defterin `CIVITAI_PHOTO` yorumu. Diff kelime kelime okunur.

**7 · Takım koşulur**, dördü de. Beklenen: hepsi yeşil.

**8 · `npm run build --prefix queen-editor/frontend`**, `dist/` kaynakla aynı commit'e girer.

**9 · Yol haritasında 238 işaretlenir**, Durum 25/27 olur. Commit'lenir ve push edilir.
