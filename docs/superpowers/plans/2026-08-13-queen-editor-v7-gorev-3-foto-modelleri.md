# Görev 3 — Foto modelleri kurulum listesine girsin (uygulama planı)

**Spec:** [Görev 3](../specs/2026-08-13-queen-editor-v7-gorev-3-foto-modelleri-design.md) ·
**Roadmap:** [v7](2026-08-13-queen-editor-v7-roadmap.md) · Blok 2

**Amaç:** Foto grafiğinin beş dosyası model listesine girsin; "foto kurulu mu" sorusu dosyalardan
cevaplansın ve kendi kendine cevap veren üretici dalı silinsin.

## Global kısıtlar

- Kod, yorum, docstring ve test adları **İngilizce**; kullanıcıya görünen metin Türkçe.
- Ön yüz değişmiyor → `npm run build` gerekmez.
- Defter bu görevde değişmez.
- Görev sonunda **tek commit**.

## Dosyalar

- **Değiştir:** `queen-editor/backend/features/producers/domain/model_groups.py`
- **Değiştir:** `queen-editor/backend/features/producers/domain/usecases/list_producers.py`
- **Değiştir:** `queen-editor/backend/features/photo_generation/data/comfy_photo_generator.py`
- **Değiştir:** `queen-editor/backend/main.py`
- **Değiştir:** `queen-editor/backend/tests/test_producers.py`
- **Değiştir:** `queen-editor/backend/tests/test_producers_routes.py`
- **Değiştir:** `queen-editor/backend/tests/test_comfy_photo_generator.py`

---

### Adım 1 — Foto grubunun testini yaz

`test_producers.py` sonuna:

```python
def test_the_photo_group_carries_everything_the_graph_reads():
    rows = model_groups.GROUPS["photo"]

    assert [(row["folder"], row["name"]) for row in rows] == [
        ("checkpoints", "nova3DCGXL_ilV90.safetensors"),
        ("loras", "USNR_STYLE_ILL_V1_lokr3-000024.safetensors"),
        ("upscale_models", "4x_foolhardy_Remacri.pth"),
        ("ultralytics/bbox", "face_yolov9c.pt"),
        ("sams", "sam_vit_b_01ec64.pth"),
    ]
    assert all(row["url"] for row in rows)


def test_only_the_civitai_rows_of_the_photo_group_need_a_key():
    gated = [row["name"] for row in model_groups.GROUPS["photo"] if row.get("auth")]

    assert gated == ["nova3DCGXL_ilV90.safetensors",
                     "USNR_STYLE_ILL_V1_lokr3-000024.safetensors"]
```

### Adım 2 — Koş, kırmızı olduğunu gör

Çalıştır: `python -m pytest queen-editor -q`

Beklenen: **FAIL** — foto grubu boş.

### Adım 3 — Foto grubunu yaz

`model_groups.py`, `GROUPS` içinde `"photo": []` yerine:

```python
    # What the photo graph reads. The checkpoint and the lora are the render itself; the other
    # three are branches of the same graph -- the default-on FaceDetailer loads the detector and
    # SAM at startup, and the bypassed Ultimate SD Upscale reads Remacri the moment it is switched
    # on. Two of five would make "the photo producer is installed" a lie.
    "photo": [
        {"folder": "checkpoints", "name": "nova3DCGXL_ilV90.safetensors",
         "url": f"{CIVITAI_DOWNLOAD}/2744564", "auth": CIVITAI},
        {"folder": "loras", "name": "USNR_STYLE_ILL_V1_lokr3-000024.safetensors",
         "url": f"{CIVITAI_DOWNLOAD}/1552087", "auth": CIVITAI},
        {"folder": "upscale_models", "name": "4x_foolhardy_Remacri.pth",
         "url": "https://huggingface.co/FacehugmanIII/4x_foolhardy_Remacri/resolve/main/"
                "4x_foolhardy_Remacri.pth"},
        # UltralyticsDetectorProvider lists this one as "bbox/<name>", so the folder is nested.
        {"folder": "ultralytics/bbox", "name": "face_yolov9c.pt",
         "url": "https://huggingface.co/Bingsu/adetailer/resolve/main/face_yolov9c.pt"},
        {"folder": "sams", "name": "sam_vit_b_01ec64.pth",
         "url": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth"},
    ],
```

Modül docstring'inin son paragrafı ("An empty group means…") artık karşılıksız — sil.

### Adım 4 — Koş, yeşil olduğunu gör

Çalıştır: `python -m pytest queen-editor -q`

Beklenen: yeni iki test **PASS**. Foto grubuna bakan eski testler hâlâ kendi fixture'larını
kullandığı için kırılmamalı.

### Adım 5 — Fallback'in gittiğini söyleyen testleri yaz

`test_producers.py` içinde:

- `FakeProducer` sınıfını sil.
- `test_a_producer_without_a_group_answers_for_itself` ve
  `test_a_producer_that_cannot_answer_is_not_quietly_called_missing` testlerini sil.
- `test_a_kind_with_neither_a_group_nor_a_producer_is_not_installed` yerine:

```python
def test_a_kind_with_no_group_is_not_installed():
    assert list_producers(GROUPS, FakeFiles())[0]["installed"] is False
```

- Kalan `list_producers(...)` çağrılarından üçüncü argümanı çıkar (satır 71, 81, 87, 110).

`test_producers_routes.py` içinde de:

```python
        list_producers=lambda: list_producers(GROUPS, files, running=runner.status()),
```

`test_comfy_photo_generator.py` içinde `test_the_photo_producer_is_installed_when_the_renderer_
lists_a_model` ve `..._lists_none` testlerini sil.

### Adım 6 — Koş, kırmızı olduğunu gör

Çalıştır: `python -m pytest queen-editor -q`

Beklenen: **FAIL** — `list_producers` hâlâ üç argüman istiyor.

### Adım 7 — Fallback'i sil

`list_producers.py`:

```python
"""What the Üreticiler panel draws: three rows, each with a name and an answer.

Installed means the producer's declared model group is on this machine, file by file. A kind with
no group is not installed -- which is the rule the engine already applies when it refuses to
dispatch a job type nobody can do.
"""
from backend.features.producers.domain.producers import NAMES, ORDER


def list_producers(groups, files, running=None):
    rows = []
    for kind in ORDER:
        group = groups.get(kind) or []
        installed = bool(group) and all(
            files.exists(spec["folder"], spec["name"]) for spec in group)
        row = {"id": kind, "name": NAMES[kind], "installed": installed}
        if running and running.get("kind") == kind:
            row["installing"] = {key: running.get(key) for key in ("done", "total", "file")}
        rows.append(row)
    return rows
```

`comfy_photo_generator.py`'den `installed()` metodunu sil (docstring'iyle birlikte).

`main.py`:

```python
    list_producers=lambda: list_producers(GROUPS, _model_files,
                                          running=_install_runner.status()),
```

ve üstündeki yorumu yeni gerçeğe göre yaz: her üretici kendi dosya grubuyla yargılanır.

### Adım 8 — Tam takım

Çalıştır: `python -m pytest queen-editor -q` ve
`npm test --prefix queen-editor/frontend -- --run`

Beklenen: ikisi de **PASS**.

### Adım 9 — Commit

```bash
git add queen-editor docs/superpowers
git commit -m "feat(queen-editor): the photo producer is a model group like the others"
```
