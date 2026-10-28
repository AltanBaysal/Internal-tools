# Madde 332 · H3'ün modeli DaSiWa'ya dönüyor — uygulama turunun planı

**Spec:** [uygulama turu](../specs/2026-09-24-queen-editor-m332-dasiwa-donus-uygulama-design.md) ·
**Testler:** `5e630d47` · **Tur:** 2/2.

**Ad:** `dasiwa_minimax_h3_ref2va_v2_pruned_hybrid_turbo_int8_row-wise_convrot_runtime_mixed.safetensors`.

## Görev 1 — grafikler

- [ ] `queen-editor/assets/workflow_video_h3_api.json` ve `workflow_video_h3_first_last_api.json`:
  `"unet_name": "MiniMaxH3/10Eros_Max_h3_TURBO-hybrid_beta5_int8.safetensors"` →
  `"unet_name": "MiniMaxH3/<ad>"`, her dosyada iki yerde *(`replace_all`)*.

## Görev 2 — grup

- [ ] `model_groups.py`, `H3_VIDEO`'nun ilk satırı:

```python
    {"folder": "diffusion_models",
     "name": "MiniMaxH3/dasiwa_minimax_h3_ref2va_v2_pruned_hybrid_turbo_int8_"
             "row-wise_convrot_runtime_mixed.safetensors"},
```

## Görev 3 — defter

- [ ] 329'dan sonra deftere başka bir commit dokunmadı *(`git log 86986bf7..HEAD -- queen-editor/queeneditor.ipynb`
  yalnız `61d20466`)*, yani dosya `git checkout 86986bf7 -- queen-editor/queeneditor.ipynb` ile geri
  alınıyor. Sonuç: `HF_H3`'te Eros yok, `CIVITAI_H3 = [`'in ardında:

```python
    (3314686, H3DIFF,
     "dasiwa_minimax_h3_ref2va_v2_pruned_hybrid_turbo_int8_row-wise_convrot_runtime_mixed.safetensors",
     "DaSiWa H3 Hybrid Turbo v2"),
```

## Görev 4 — koşu, işaret, commit

- [ ] Dört satır, yazıldığı gibi ve paralel; dördü de yeşil.
- [ ] Yol haritasında 332 ✅, `Durum` 40/40.
- [ ] Commit: iki grafik, `model_groups.py`, defter, spec, bu plan, yol haritası —
  `feat(m332): H3 renders with DaSiWa again, fetched by its version through the mirror, Eros leaves the notebook; v7 at 40/40`.
