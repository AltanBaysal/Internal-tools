# Madde 229 · Model listesi ComfyUI'ye gitmeyecek — uygulama turunun planı

**Spec:** [uygulama turu](../specs/2026-09-17-queen-editor-m229-model-listesi-uygulama-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

## Adımlar

**1 · `list_models.py`.** İmza `list_models(chosen)`. Boş dal gider, belge yalnız tarifleri anlatır.

**2 · Checkpoint sorusu silinir.** `ports.PhotoGenerator.models`, `ComfyPhotoGenerator.models`,
`ComfyClient.checkpoints` — artık `json` kullanmayan bir import kalırsa o da.

**3 · `routes.py`.** `/api/models` doğrudan `{"models": list_models()}` döner.

**4 · `main.py` ve `config.py`.** Tesisat `partial(list_models, config.PHOTO_RECIPES)`; yorum boş
listenin bugünkü anlamını söyler.

**5 · Takım koşulur**, dördü de. Beklenen: dördü yeşil.

**6 · Commit.** Ön yüz değişmediği için `dist` yok. Madde roadmap'te işaretlenir.
