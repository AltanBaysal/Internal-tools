# Madde 430 — Fotoğrafta hiçbir detailer çalışmaz, test turu planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Hedef:** Grafiğin detailer'sız olduğunu, Save Image'ın VAE Decode'dan okuduğunu, grafikte asılı
düğüm kalmadığını, üreticiler panelinin ve notebook'un yüz dedektörünü ve SAM'i artık aramadığını
tutan testler — bugün kırmızı.

**Mimari:** Grafik bir asset; testler onu `config.WORKFLOW_PATH`'ten okur, düğümleri sınıflarıyla
ve bağlantılarıyla sorar, id'leriyle değil. Notebook okunur, çalıştırılmaz.

**Araçlar:** pytest.

**Spec:** [m430 test turu](../specs/2026-10-07-queen-editor-m430-detailer-yok-testler-design.md)

## Genel kısıtlar

- Yalnız testler; grafik, `model_groups.py`, notebook ve `colab/` bu turda değişmez.
- Dört satır CLAUDE.md'deki gibi, paralel, borusuz, daraltılmadan.
- Test adları ve docstring'ler İngilizce, assert mesajları Türkçe.

---

### Görev 1: Grafiğin testleri

**Dosya:** `queen-editor/backend/tests/test_workflow_asset.py`

- [ ] `test_the_positive_encoder_understands_break`'in docstring'inde
  `Only this node changes. Both KSampler and ToDetailerPipe read the positive from its output, so
  one swap covers the detailer too.` yerine:

```python
    Only this node changes, and KSampler reads the positive from its output.
```

- [ ] `test_every_graph_makes_a_portrait_frame`'in ardına, `_model_files`'tan önce:

```python
def test_the_photo_graph_runs_no_detailer():
    """Madde 430: the user tried every detailer the graph's author ships -- NSFW, hand, eyes -- and
    none did meaningful work (219), then asked for none at all, the face one included: "abi hiç bir
    detailer açık olmasın direkt". Asked by class rather than by id, so a detailer coming back
    under a new id still turns this red."""
    photo = _graphs()[0]

    found = sorted({node["class_type"] for node in photo.values()
                    if "Detailer" in node["class_type"] or "Detector" in node["class_type"]
                    or node["class_type"] == "SAMLoader"})
    assert not found, f"Fotoğraf grafiğinde detailer düğümü var: {found}"


def test_the_photo_graph_saves_the_decoded_picture():
    """With the detailer gone the picture is saved as the sampler made it: straight out of VAE
    Decode, the way the user's own export reads with the detailer groups switched off."""
    photo = _graphs()[0]
    savers = [node for node in photo.values() if node["class_type"] == "SaveImage"]

    assert len(savers) == 1, f"Grafikte {len(savers)} Save Image var"
    source = savers[0]["inputs"]["images"][0]
    assert photo[source]["class_type"] == "VAEDecode", \
        f"Save Image resmi VAE Decode'dan değil {photo[source]['class_type']}'dan alıyor"


def test_every_node_of_the_photo_graph_feeds_the_saved_picture():
    """What a removed branch leaves behind carries no detailer in its name: the settings it read,
    the model patch only it used, the panel that compared its before and after. An export with the
    branch switched off has none of them, so walking back from the saved picture has to reach
    every node there is."""
    photo = _graphs()[0]
    saver = next(node_id for node_id, node in photo.items() if node["class_type"] == "SaveImage")

    reached, waiting = set(), [saver]
    while waiting:
        node_id = waiting.pop()
        if node_id in reached:
            continue
        reached.add(node_id)
        waiting += [value[0] for value in photo[node_id]["inputs"].values()
                    if isinstance(value, list) and len(value) == 2 and isinstance(value[0], str)]

    hanging = sorted(set(photo) - reached)
    assert not hanging, f"Kaydedilen resme ulaşmayan düğümler: {hanging}"
```

### Görev 2: Üreticiler panelinin testi

**Dosya:** `queen-editor/backend/tests/test_producers.py:99-115`

- [ ] `test_the_photo_group_carries_everything_the_graph_reads`'in docstring'i ve listesi:

```python
def test_the_photo_group_carries_everything_the_graph_reads():
    """The checkpoint is the one row naming a kind rather than a file: which model is on the machine
    is the user's pick since Madde 140, and the graph renders with whichever it was handed. The
    other three are named by the file itself. The face detector and SAM left with the detailer
    (madde 430): a group naming them would call the producer uninstalled over files nothing loads."""
    rows = model_groups.GROUPS["photo"]

    assert rows[0] == {"folder": "checkpoints", "suffix": ".safetensors"}
    assert [(row["folder"], row["name"]) for row in rows[1:]] == [
        ("loras", "USNR_STYLE_ILL_V1_lokr3-000024.safetensors"),
        # Both loras come with the group whichever models were installed: the lora box is a pick
        # made per batch, and tying the panel's count to it would make "installed" mean something
        # different per machine.
        ("loras", "translucent_penetration_v5.safetensors"),
        ("upscale_models", "4x_foolhardy_Remacri.pth"),
    ]
```

### Görev 3: Notebook'un testleri

**Dosyalar:** `queen-editor/backend/tests/test_notebook_installs_the_producer_groups.py`,
`queen-editor/backend/tests/test_colab_nodes.py:76-79`

- [ ] `test_the_photo_estimate_counts_only_what_the_group_always_takes`'in docstring'inde
  `both loras, the upscaler,\n    the detector, the SAM.` yerine `both loras and the upscaler.`
- [ ] `test_the_retired_dasiwa_h3_checkpoint_is_gone_from_the_notebook`'un ardına:

```python
def test_the_face_detailer_s_files_are_gone_from_the_notebook():
    """The photo graph runs no detailer since madde 430. A row left behind would still bring the
    detector and SAM down on every photo run, and the Subpack's install with them -- the package
    gives the graph nothing but the detector node. The folders go too: a cell making them and a
    summary listing them would be the same leftover."""
    source = _source()

    for leftover in ("face_yolov9c.pt", "sam_vit_b_01ec64.pth", "Bingsu/adetailer",
                     "ComfyUI-Impact-Subpack", "ultralytics", "models/sams"):
        assert leftover not in source, f"Defterde yüz detailer'ından iz kaldı: {leftover}"
```

- [ ] `test_impact_pack_is_installed_without_sam2`'nin docstring'inde
  `Our graph loads SAM's first version, sam_vit_b, through\n    segment-anything, and Impact-Pack
  imports sam2 only when it is installed (madde 314).` yerine:

```python
    environment of its own. No graph of ours loads a SAM (madde 430), and Impact-Pack imports sam2
    only when it is installed (madde 314)."""
```

### Görev 3b: Açık adresli indirme de gidiyor *(spec'in eki)*

**Dosya:** `queen-editor/backend/tests/test_notebook_installs_the_producer_groups.py`

- [ ] `test_an_unticked_group_costs_no_bytes`: `("CIVITAI_PHOTO", "OPEN_PHOTO", "HF_PHOTO")` yerine
  `("CIVITAI_PHOTO", "HF_PHOTO")`.
- [ ] `test_the_models_cell_ends_with_the_download_summary`: `open_jobs` döngüsünü arayan assert
  çıkar.
- [ ] `test_the_face_detailer_s_files_are_gone_from_the_notebook`: artıklara `"OPEN_PHOTO"` ve
  `"open_jobs"` eklenir; docstring'e: `SAM was the one file fetched by a plain address, so the list
  of those and its loop go with it.`
- [ ] Ayrı bir kırmızı commit: `test(queen-editor): Madde 430 red, second part -- …`.

### Görev 4: Takımı koş ve commit'le

- [ ] Dört satır, paralel:
  `python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend` ·
  `python -m pytest queen-editor -q` · `npm test --prefix queen-editor/frontend`
- [ ] Beklenen: **beş kırmızı**, hepsi `queen-editor` pytest satırında —
  `test_the_photo_graph_runs_no_detailer`, `test_the_photo_graph_saves_the_decoded_picture`,
  `test_every_node_of_the_photo_graph_feeds_the_saved_picture`,
  `test_the_photo_group_carries_everything_the_graph_reads`,
  `test_the_face_detailer_s_files_are_gone_from_the_notebook`. Öteki üç satır yeşil.
- [ ] Commit: spec, plan ve dört test dosyası — `test(queen-editor): Madde 430 red -- …`. Çift tırnak
  yok; son satır `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
