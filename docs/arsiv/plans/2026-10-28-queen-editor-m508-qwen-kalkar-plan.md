# Madde 508 · Qwen kalkar — plan

**Madde:** [v11 yol haritası](../roadmaps/2026-10-24-queen-editor-v11-roadmap.md#v11-7), 508 · v11-7 ·
**Dal:** `feat/queen-editor-v11` · **Spec:**
[2026-10-28-queen-editor-m508-qwen-kalkar-design.md](../specs/2026-10-28-queen-editor-m508-qwen-kalkar-design.md)

Test önce: önce testler Qwen'in yokluğunu ve eski satırın davranışını söyler (kırmızı), sonra kod çıkar
(yeşil).

## 1. Testler

- `backend/tests/test_comfy_qwen_photo_generator.py` — silinir.
- `backend/tests/test_photo_usecases.py` — model listesi `nova3dcg`, `dasiwa`, `krea2`; Qwen'in liste
  testi `list_models(["qwen21turbo"]) == []` olur (bilmediği kimliği düşürür); iki parametre
  listesinden Qwen satırları çıkar.
- `backend/tests/test_comfy_photo_generator.py` — yeni test: `qwen21turbo` + `translucent_penetration`
  "Tanınmayan LoRA" ile durur, `qwen21turbo` + `none` checkpoint yükleyicisine dosya adı gibi yazılır.
  Krea ve Qwen diyen docstring yalnız Krea der.
- `backend/tests/test_composition_root.py` — `qwen21turbo` karesi fotoğraf grafiğine gider
  (`45`'in `ckpt_name`'i `qwen21turbo`).
- `backend/tests/test_producer_contract.py` — `GRAPHS`'tan Qwen'in yolu, `QwenComfy` ve Qwen'in sözleşme
  testi çıkar.
- `backend/tests/test_producers.py` — `any`'de `QWEN_FILES` yok; "yalnız Qwen'li makine" testi çıkar.
- `backend/tests/test_workflow_asset.py` — Qwen'in grafik testleri, `_qwen`, boyut testi ve
  parametreli bağ testindeki Qwen satırı çıkar; grafik listesi Qwen'siz, ve Qwen'in grafiğinin
  `assets/`'te olmadığını söyleyen bir satır.
- `backend/tests/test_notebook_installs_the_producer_groups.py` — Qwen'in indirme, kutucuk ve disk
  testleri çıkar; klasör testi `INSTALL_VIDEO or INSTALL_KREA2`'yi bekler; klon testi yalnız Krea'nın
  grafiğine bakar ve Qwen'inkinin listede olmadığını, "dört grafik" yazdığını söyler; defterde
  `QWEN` ve `PHOTO_QWEN21TURBO` geçmediğini söyleyen bir test.
- `backend/tests/test_lora_chain.py` — docstring yalnız Krea.
- `frontend/src/features/photo_generation/GeneratePanel.test.jsx`, `PhotoDetail.test.jsx` — Qwen
  örnekleri çıkar; Krea'nınkiler kalır.

## 2. Kod

- `catalog.py` — `QWEN`, `SLIME_QWEN`, `QWEN_LORAS`, Qwen satırı; yorumlar.
- `comfy_qwen_photo_generator.py`, `assets/workflow_photo_qwen_api.json` — silinir.
- `main.py` — import ve `PhotoByModel`'deki Qwen; yorum.
- `config.py` — `QWEN_WORKFLOW_PATH`.
- `model_groups.py` — `QWEN_FILES` ve `any`'deki yeri; yorumlar.
- `photo_by_model.py`, `comfy_graph.py`, `lora_chain.py`, `comfy_krea_photo_generator.py`,
  `fix_photo.py`, `regenerate.py`, `list_producers.py` — yorumlar yalnız Krea.
- `queeneditor.ipynb` — 1. hücre: kutucuk ve assert; klon hücresi: liste ve "dört grafik"; modeller
  hücresi: `PHOTO_MODELS` satırı, `HF_QWEN`, `CIVITAI_QWEN`, `INSTALL_QWEN`, `CIVITAI_PHOTO`, `HF_PHOTO`,
  `PHOTO_GIB`, `FOLDERS`. JSON düzeni korunur (kaynak tek string).
- `queen-editor/BACKLOG.md` — 501'den kalan maddede "Krea ve Qwen" → "Krea".

## 3. Bitiş

- `queen-editor/` altında `qwen` araması: yalnız Krea'nın ve H3'ün Qwen3-VL/Qwen Image VAE dosyaları,
  BACKLOG'un tarihçesi ve 508'in kendi testleri.
- Dört takım tek tek; `test_notebook_clones_its_branch.py`'nin iki testi `BRANCH` yüzünden düşer.
- Ekran kaynağı değişmediği için `dist` yeniden derlenmez.
- Roadmap: 508 ✅, başlık "Bitti · 7/7 · dal `feat/queen-editor-v11`".
