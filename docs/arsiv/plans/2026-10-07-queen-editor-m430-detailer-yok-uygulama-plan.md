# Madde 430 — Fotoğrafta hiçbir detailer çalışmaz, uygulama planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Hedef:** Fotoğraf grafiği detailer'sız, notebook yüz dedektörünü, SAM'i ve Impact-Subpack'i
kurmuyor, üreticiler paneli o iki dosyayı aramıyor — test turunun beş kırmızısı yeşil.

**Mimari:** Grafik bir JSON asset; düğümler silinir, Save Image VAE Decode'a bağlanır. Panelin
listesi bir Python sabiti. Notebook'ta üç hücre değişir.

**Araçlar:** Edit, NotebookEdit, pytest.

**Spec:** [m430 uygulama turu](../specs/2026-10-07-queen-editor-m430-detailer-yok-uygulama-design.md)

## Genel kısıtlar

- Testler bu turda değişmez.
- `colab/downloads.py` ve Impact-Pack'in satırı değişmez.
- Notebook yalnız NotebookEdit ile değişir; `PHOTO_GIB = 2 +` kalır.
- Commit mesajında çift tırnak yok, amend yok.

---

### Görev 1: Grafik

**Dosya:** `queen-editor/assets/workflow_api.json`

- [ ] `"5"`, `"6"`, `"9"`, `"14"`, `"19"`, `"24"`, `"31"`, `"37"`, `"42"`, `"44"`, `"57"` düğümlerini
  sil.
- [ ] `"50"`'nin girdisi:

```json
      "images": [
        "33",
        0
      ]
```

### Görev 2: Üreticiler paneli ve yorumlar

**Dosyalar:** `queen-editor/backend/features/producers/domain/model_groups.py:18-38`,
`queen-editor/backend/features/photo_generation/data/comfy_photo_generator.py:8`,
`queen-editor/colab/nodes.py:11-15`

- [ ] `GROUPS["photo"]`'nun başındaki yorum:

```python
    # What the photo graph reads. The checkpoint and the loras are the render itself, and Remacri
    # is read by the bypassed Ultimate SD Upscale the moment it is switched on. The graph runs no
    # detailer (madde 430), so no detector and no SAM is counted.
```

- [ ] `UltralyticsDetectorProvider lists this one…` yorumu ve iki satır (`ultralytics/bbox`,
  `sams`) çıkar.
- [ ] `comfy_photo_generator.py`:
  `"40" Seed (rgthree) -> KSampler and both wildcard processors read it`.
- [ ] `nodes.py`'nin yorumunun son cümlesi:

```python
# build environment of its own. Impact-Pack took 3 dk 13 sn of a 6 dk 2 sn cell on the user's run. No
# graph of ours loads a SAM, and Impact-Pack imports sam2 only when it is installed.
```

### Görev 3: Notebook

**Dosya:** `queen-editor/queeneditor.ipynb`

- [ ] Giriş hücresi (`34c9ff58`): `(21 custom node)` → `(20 custom node)`.
- [ ] Başlık (`8de17e98`): `## ComfyUI + Custom Node'lar (20)`.
- [ ] ComfyUI hücresi (`8e4cc402`): `("ComfyUI-Impact-Subpack", …)` satırı çıkar.
- [ ] Yardımcılar hücresi (`df871d38`):
  `from colab.downloads import hf_fetch, civitai_fetch, download_summary`.
- [ ] Modeller hücresi (`f0df85b4`):
  - `BBOX = …` ve `SAMS = …` satırları, ve `makedirs` listesinden `BBOX, SAMS`.
  - `HF_PHOTO`'dan `("Bingsu/adetailer", "face_yolov9c.pt", …)` satırı.
  - `OPEN_PHOTO = [...]` bloğu, `open_jobs = …` satırı, `# === Open downloads ===` bloğu.
  - Özette `("ultralytics/bbox", BBOX, "*.pt"), ("sams", SAMS, "*.pth")`.

### Görev 4: Takımı koş, commit'le, maddeyi kapat

- [ ] Dört satır, paralel:
  `python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend` ·
  `python -m pytest queen-editor -q` · `npm test --prefix queen-editor/frontend`
- [ ] Beklenen: dört satır yeşil.
- [ ] Commit: spec, plan, grafik, `model_groups.py`, `comfy_photo_generator.py`, `nodes.py`,
  notebook — `feat(queen-editor): 430 -- …`.
- [ ] Roadmap: 430 `✅`, *Durum* 18/19; ayrı bir `docs(queen-editor): 430 is done -- …` commit'i.
