# Madde 329 — Eros Max beta5 ve yarı güçte Mystic XXX, uygulama turunun planı

> **Koşum:** bu oturumda, satır satır. Commit orkestratörün.

**Hedef:** `86986bf7`'nin on iki kırmızı testi yeşil, geri kalan her şey — defterin tavanı dahil —
yeşil kalıyor.

**Spec:** [m329 uygulama turu](../specs/2026-09-24-queen-editor-m329-eros-max-uygulama-design.md)

## Her yere geçerli kurallar

- Eros'un adı grafikte ve grupta `MiniMaxH3/10Eros_Max_h3_TURBO-hybrid_beta5_int8.safetensors`,
  defterde `10Eros_Max_h3_TURBO-hybrid_beta5_int8.safetensors`.
- Yorum ve docstring **İngilizce** ve yalnız *neden*; defterin kod hücresine yorum girmiyor.
- Testlere dokunulmuyor; üretici, ekran, README ve `MIRRORLESS` değişmiyor.
- Grafikler ve defter ham metinlerinde düzenleniyor: yeniden export yok, biçim değişmiyor.

---

## Görev 1: İki grafik

**Dosyalar:** Değiştir: `queen-editor/assets/workflow_video_h3_api.json` ve
`queen-editor/assets/workflow_video_h3_first_last_api.json`.

- [ ] **Adım 1: Dört model düğümü.** İkisinde de `1512:2586` ve `1512:2588`:

```
önce:  "unet_name": "MiniMaxH3/dasiwa_minimax_h3_ref2va_v2_pruned_hybrid_turbo_int8_row-wise_convrot_runtime_mixed.safetensors",
sonra: "unet_name": "MiniMaxH3/10Eros_Max_h3_TURBO-hybrid_beta5_int8.safetensors",
```

`"weight_dtype": "default"` olduğu gibi.

- [ ] **Adım 2: Mystic'in gücü.** İkisinde de `2678.inputs.stack_data`'da, dosyanın ham metninde:

```
önce:  ...\"lora\":\"MysticXXX_MMH3-V4.safetensors\",\"str\":1,\"vs\":1,\"as\":1}...
sonra: ...\"lora\":\"MysticXXX_MMH3-V4.safetensors\",\"str\":0.5,\"vs\":1,\"as\":1}...
```

## Görev 2: Panelin grubu

**Dosya:** Değiştir: `queen-editor/backend/features/producers/domain/model_groups.py` — `H3_VIDEO`'nun
ilk satırı.

- [ ] **Adım 1: Satır.**

```python
H3_VIDEO = [
    {"folder": "diffusion_models",
     "name": "MiniMaxH3/10Eros_Max_h3_TURBO-hybrid_beta5_int8.safetensors"},
    {"folder": "text_encoders", "name": "qwen3vl_32b_minimax_h3_int4_convrot.safetensors"},
```

## Görev 3: Defter

**Dosya:** Değiştir: `queen-editor/queeneditor.ipynb` — modeller hücresinde `HF_H3` ve `CIVITAI_H3`.
Hücre tek bir JSON dizesi; düzenleme ham metinde, kaçışlı tırnak ve `\n`'lerle.

- [ ] **Adım 1: `HF_H3`'ün başı.** Hücrenin okunduğu hâliyle:

```python
HF_H3 = [
    ("TenStrip/10Eros-Max", "10Eros_Max_h3_TURBO-hybrid_beta5_int8.safetensors",
     H3DIFF, "10Eros_Max_h3_TURBO-hybrid_beta5_int8.safetensors", "H3 Eros Max beta5", None),
    ("Abiray/MiniMax-H3-GGUF", "text_encoders/qwen3vl_32b_minimax_h3_int4_convrot.safetensors",
```

- [ ] **Adım 2: `CIVITAI_H3`.** DaSiWa'nın üç satırlık girdisi gidiyor:

```python
CIVITAI_H3 = [
    (3228867, LORA, "H3_Motion_BoosterV2.safetensors", "H3 Motion Booster"),
    (3266628, LORA, "MysticXXX_MMH3-V4.safetensors", "H3 Mystic XXX"),
]
```

- [ ] **Adım 3: Defter hâlâ geçerli JSON** — `test_notebook_*` dosyaları onu `json.load` ile okuyor;
  bozuksa ilk koşuda hepsi düşer.

## Görev 4: Koşu

- [ ] **Adım 1: Dört satırı koş**, paralel, yazıldığı gibi — hepsi yeşil; defter tavanın altında.
  Tavan kırmızıysa satır kısaltılmıyor, durulup soruluyor.
- [ ] **Adım 2: Durup dön** — commit orkestratörün: grafikler, grup, defter, spec ve bu plan,
  `feat(m329): …`.
