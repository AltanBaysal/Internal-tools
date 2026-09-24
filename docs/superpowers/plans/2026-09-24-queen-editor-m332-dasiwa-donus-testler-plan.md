# Madde 332 · H3'ün modeli DaSiWa'ya dönüyor — test turunun planı

**Spec:** [test turu](../specs/2026-09-24-queen-editor-m332-dasiwa-donus-testler-design.md) ·
**Tur:** 1/2 — yalnız testler, kaynak kod değişmiyor.

**Sabit:** `DASIWA = "MiniMaxH3/dasiwa_minimax_h3_ref2va_v2_pruned_hybrid_turbo_int8_row-wise_convrot_runtime_mixed.safetensors"`
— testlerde bu ad iki parçaya bölünmüş dizeyle yazılır *(satır uzunluğu)*.

## Görev 1 — grafik testleri (`test_workflow_asset.py`)

- [ ] `test_both_h3_graphs_load_eros_max_beta5` → `test_both_h3_graphs_load_dasiwa_hybrid_turbo_v2`;
  docstring madde 332'yi anlatır, `expected` DaSiWa'nın adı ve `"default"`. Gövde aynı.
- [ ] `test_the_h3_graphs_carry_motion_booster_alone_at_seventy` docstring'inde *"Eros is tried alone,
  its author having folded Mystic XXX into the checkpoint itself"* → *"Mystic XXX came off with madde
  330"*. Assert'e dokunulmaz.

## Görev 2 — üretici testleri (`test_comfy_h3_video_generator.py`)

- [ ] `test_every_h3_video_is_rendered_with_eros_max_beta5` →
  `test_every_h3_video_is_rendered_with_dasiwa_hybrid_turbo_v2`; beklenen küme `{DaSiWa'nın adı}`.
- [ ] `test_no_h3_video_is_rendered_with_mystic_xxx` docstring'inde *"Eros is tried alone"* →
  *"the stack carries Motion Booster alone"*.

## Görev 3 — defter testleri (`test_notebook_installs_the_producer_groups.py`)

- [ ] Eros'un `HF_H3` testi yerine:

```python
def test_the_notebook_fetches_dasiwa_by_its_version_into_the_h3_diffusion_models():
    """Madde 332: back to the model H3 ran on before 329, fetched as it was then -- by its Civitai
    version, through the mirror (madde 311). A row of CIVITAI_H3, which only an H3 run reaches
    (test_an_unticked_group_costs_no_bytes); H3DIFF is where the graph's MiniMaxH3/ prefix looks."""
    cell = _cell("CIVITAI_H3 = [")
    listing = cell[cell.find("CIVITAI_H3 = ["):]
    listing = listing[:listing.find("\n]")]

    assert re.search(r'\(3314686,\s*H3DIFF,\s*"dasiwa_minimax_h3_ref2va_v2_pruned_hybrid_turbo_int8_'
                     r'row-wise_convrot_runtime_mixed\.safetensors",', listing), \
        f"CIVITAI_H3'te DaSiWa satırı yok:\n{listing}"
```

- [ ] DaSiWa'nın "gitti" testi yerine:

```python
def test_the_retired_eros_max_is_gone_from_the_notebook():
    """DaSiWa took its place back (madde 332). A row left behind would still bring 21 GB down on every
    H3 run, for a file no graph loads."""
    source = _source()

    for leftover in ("TenStrip/10Eros-Max", "10Eros_Max_h3_TURBO-hybrid_beta5_int8"):
        assert leftover not in source, f"Defterde Eros'tan iz kaldı: {leftover}"
```

## Görev 4 — grup (`test_producers.py`)

- [ ] `H3_FILES`'ın ilk satırı:

```python
    ("diffusion_models", "MiniMaxH3/dasiwa_minimax_h3_ref2va_v2_pruned_hybrid_turbo_int8_"
                         "row-wise_convrot_runtime_mixed.safetensors"),
```

## Görev 5 — koşu ve commit

- [ ] Dört satır, yazıldığı gibi ve paralel. Beklenen: `queen-editor` pytest'te yalnız sekiz kırmızı
  *(spec, Bitti sayılır)*.
- [ ] Commit: dört test dosyası, spec, plan —
  `test(m332): every H3 video loads DaSiWa again, fetched by its version, and Eros leaves the notebook (red)`.
