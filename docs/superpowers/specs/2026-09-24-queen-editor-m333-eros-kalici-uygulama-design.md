# Madde 333 — H3'ün modeli Eros'a dönüyor, uygulama turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 2/2 — takım yeşile döner.

**Testler:** [m333 test turu](2026-09-24-queen-editor-m333-eros-kalici-testler-design.md), `b87dd57b`.

332'nin üç yerdeki değişikliği tersine dönüyor; hedef, 329'un modeli.

## Grafikler

Dört `UNETLoader`'ın `unet_name`'i `MiniMaxH3/10Eros_Max_h3_TURBO-hybrid_beta5_int8.safetensors`;
`weight_dtype` `default`. JSON düzenlenerek, dosya başına iki satır.

## `model_groups.H3_VIDEO`

İlk satırın adı Eros'unki, tek satırda — 329'daki gibi.

## Defter

329'un yeşil commit'indeki *(`61d20466`)* hâli: `HF_H3`'ün başında Eros, `CIVITAI_H3`'te DaSiWa yok.
O commit'ten bu yana deftere yalnız 332 dokundu ve o da 329'dan önceki hâline dönmüştü — yani
`61d20466`'daki dosya bugün istenenin harfi harfine aynısı. Dosya oradan geri alınıyor. Aynadaki
DaSiWa'ya defter hiç dokunmuyor.

## Değişmeyen

Yığın, Mystic, `MIRRORLESS`, 331'in talimatı, disk tahmini, README. Ekran ve dist değişmiyor.

## Bitti sayılır

Dört test satırı yeşil, `skip` / `xfail` yok; v7'nin son maddesi kapanıyor.
