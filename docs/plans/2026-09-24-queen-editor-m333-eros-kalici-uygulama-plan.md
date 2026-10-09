# Madde 333 · H3'ün modeli Eros'a dönüyor — uygulama turunun planı

**Spec:** [uygulama turu](../specs/2026-09-24-queen-editor-m333-eros-kalici-uygulama-design.md) ·
**Testler:** `b87dd57b` · **Tur:** 2/2.

## Görev 1 — grafikler

- [ ] İki H3 grafiğinde `"unet_name": "MiniMaxH3/dasiwa_…_mixed.safetensors"` →
  `"unet_name": "MiniMaxH3/10Eros_Max_h3_TURBO-hybrid_beta5_int8.safetensors"`, her dosyada iki yer
  *(`replace_all`)*.

## Görev 2 — grup

- [ ] `model_groups.py`, `H3_VIDEO`'nun ilk satırı:

```python
    {"folder": "diffusion_models",
     "name": "MiniMaxH3/10Eros_Max_h3_TURBO-hybrid_beta5_int8.safetensors"},
```

## Görev 3 — defter

- [ ] `git log 61d20466..HEAD -- queen-editor/queeneditor.ipynb` yalnız 332'nin commit'ini göstermeli;
  gösteriyorsa `git checkout 61d20466 -- queen-editor/queeneditor.ipynb`. Ardından defterde
  `3314686` ve `dasiwa_minimax_h3` geçmiyor, `TenStrip/10Eros-Max` geçiyor.

## Görev 4 — koşu, işaret, commit, push

- [ ] Dört satır, yazıldığı gibi ve paralel; dördü de yeşil.
- [ ] Yol haritasında 333 ✅, `Durum` 41/41.
- [ ] Commit: iki grafik, `model_groups.py`, defter, spec, bu plan, yol haritası —
  `feat(m333): H3 settles on Eros from its author's repo, DaSiWa stays in the mirror unfetched; v7 at 41/41`;
  push.
