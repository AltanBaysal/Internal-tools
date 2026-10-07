# Madde 333 · H3'ün modeli Eros'a dönüyor — test turunun planı

**Spec:** [test turu](../specs/2026-09-24-queen-editor-m333-eros-kalici-testler-design.md) ·
**Tur:** 1/2 — yalnız testler.

**Adlar:** `EROS = "MiniMaxH3/10Eros_Max_h3_TURBO-hybrid_beta5_int8.safetensors"`;
DaSiWa `"MiniMaxH3/dasiwa_minimax_h3_ref2va_v2_pruned_hybrid_turbo_int8_row-wise_convrot_runtime_mixed.safetensors"`.

## Görev 1 — `test_workflow_asset.py`

- [ ] `test_both_h3_graphs_load_dasiwa_hybrid_turbo_v2` → `test_both_h3_graphs_load_eros_max_beta5`;
  `expected = {(EROS, "default")}`; docstring 333'ü anlatır *(iki model denendi, Eros seçildi)*.

## Görev 2 — `test_comfy_h3_video_generator.py`

- [ ] `test_every_h3_video_is_rendered_with_dasiwa_hybrid_turbo_v2` →
  `test_every_h3_video_is_rendered_with_eros_max_beta5`; beklenen `{EROS}`.

## Görev 3 — `test_notebook_installs_the_producer_groups.py`

- [ ] DaSiWa'nın sürüm testi yerine:

```python
def test_the_notebook_fetches_eros_max_from_its_author_s_repo_into_the_h3_diffusion_models():
    """Madde 333, the user's pick after trying both (329, 332): the file the author says to use by
    default (TURBO-hybrid int8), from the Hugging Face repo the Civitai page points at -- Civitai's
    own version link hands out a different, w4a8 file. A row of HF_H3: only an H3 run reaches it
    (test_an_unticked_group_costs_no_bytes), and hf_fetch uploads nothing, so the file never touches
    the mirror. H3DIFF is where the graph's MiniMaxH3/ prefix looks."""
    cell = _cell("HF_H3 = [")
    listing = cell[cell.find("HF_H3 = ["):]
    listing = listing[:listing.find("\n]")]

    assert re.search(r'\(\s*"TenStrip/10Eros-Max",'
                     r'\s*"10Eros_Max_h3_TURBO-hybrid_beta5_int8\.safetensors",'
                     r'\s*H3DIFF,\s*"10Eros_Max_h3_TURBO-hybrid_beta5_int8\.safetensors",',
                     listing), f"HF_H3'te Eros satırı yok:\n{listing}"
```

- [ ] Eros'un "gitti" testi yerine:

```python
def test_the_retired_dasiwa_h3_checkpoint_is_gone_from_the_notebook():
    """Eros took its place (madde 333). A row left behind would still bring ~21 GB down on every H3
    run, for a file no graph loads. The file itself stays in the mirror (the user's call, "dasiwa
    silinmesin, dursun"): the notebook only stops fetching it."""
    source = _source()

    for leftover in ("dasiwa_minimax_h3_ref2va_v2_pruned_hybrid_turbo_int8_"
                     "row-wise_convrot_runtime_mixed.safetensors", "3314686"):
        assert leftover not in source, f"Defterde DaSiWa H3'ten iz kaldı: {leftover}"
```

## Görev 4 — `test_producers.py`

- [ ] `H3_FILES`'ın ilk satırı `("diffusion_models", EROS)`.

## Görev 5 — koşu ve commit

- [ ] Dört satır, yazıldığı gibi ve paralel; `queen-editor` pytest'te yalnız sekiz kırmızı.
- [ ] Commit: dört test dosyası, spec, plan —
  `test(m333): every H3 video loads Eros from its author's repo again, and DaSiWa leaves the notebook (red)`.
