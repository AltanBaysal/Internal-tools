# Madde 332 — H3'ün modeli DaSiWa'ya dönüyor, uygulama turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 2/2 — takım yeşile döner.

**Testler:** [m332 test turu](2026-09-24-queen-editor-m332-dasiwa-donus-testler-design.md), `5e630d47`.

329'un üç yerdeki değişikliği tersine dönüyor; başka hiçbir şey değişmiyor.

## Grafikler — iki H3 export'u

Dört `UNETLoader`'ın `unet_name`'i
`MiniMaxH3/dasiwa_minimax_h3_ref2va_v2_pruned_hybrid_turbo_int8_row-wise_convrot_runtime_mixed.safetensors`.
`weight_dtype` `default`'ta. JSON düzenlenerek, yeniden export yok; dosya başına iki satır.

## `model_groups.H3_VIDEO`

İlk satırın adı DaSiWa'nın — 329'dan önceki gibi iki parçalı dizeyle, satır uzunluğu yüzünden.

## Defter

- `HF_H3`'ün ilk satırı *(Eros)* gidiyor; liste Qwen3-VL ile açılıyor.
- `CIVITAI_H3`'ün başına 329'dan önceki satır dönüyor:
  `(3314686, H3DIFF, "dasiwa_…_mixed.safetensors", "DaSiWa H3 Hybrid Turbo v2")`, üç satıra
  sarılmış hâliyle. Defter kodunda yorum yok *(defterin kuralı)*. 329'dan sonra deftere başka bir
  commit dokunmadığı için dosya 329'un kırmızı commit'inden *(`86986bf7`)* olduğu gibi geri alınıyor —
  elle yeniden yazmak yerine, harfi harfine aynısı.

## Değişmeyen

Yığın, Mystic'in satırı ve `MIRRORLESS`, 331'in talimatı, disk tahmini, README *(H3'ün modelini
anmıyor — 329'da tarandı)*. Ekran ve dist değişmiyor.

## Bitti sayılır

Dört test satırı yeşil, `skip` / `xfail` yok.
