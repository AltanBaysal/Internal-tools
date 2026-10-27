# Madde 329 — H3'ün modeli Eros Max beta5, Mystic XXX yarı güçte, uygulama turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 2/2 — takım yeşile döner.

**Testler:** [m329 test turu](2026-09-24-queen-editor-m329-eros-max-testler-design.md),
`86986bf7`.

Eros'un adı üç yerde aynı dize: grafikte ve grupta `MiniMaxH3/10Eros_Max_h3_TURBO-hybrid_beta5_int8.safetensors`,
defterde `MiniMaxH3/`'süz, çünkü klasörü `H3DIFF` veriyor. Üretici değişmiyor — model düğümlerine de
yığına da dokunmuyor, ikisi de grafiğin içinde.

## Grafikler — iki H3 export'u

- **Dört model düğümü:** iki grafikte de `1512:2586` ve `1512:2588` *(`UNETLoader`)*, `unet_name`
  DaSiWa'nın adından Eros'unkine dönüyor. `weight_dtype` `default`'ta kalıyor — DaSiWa'nın int8'i de
  öyle yükleniyordu, ve Eros da int8.
- **Yığın:** `2678`'in `stack_data`'sında Mystic'in yuvasında `"str":1` `"str":0.5` oluyor. Yuvanın
  `vs`'i ve `as`'i, Motion Booster ve boş yuvalar olduğu gibi.
- Grafikler yeniden export edilmiyor, biçimleri değişmiyor: dosya başına fark üç değer.

## `model_groups.H3_VIDEO`

- İlk satır: `{"folder": "diffusion_models", "name": "MiniMaxH3/10Eros_Max_h3_TURBO-hybrid_beta5_int8.safetensors"}`,
  DaSiWa'nın yerinde. Satırın kendi yorumu yoktu, gerekmiyor da: grubun başındaki yorum
  *(`MiniMaxH3/` adın parçası)* Eros için de doğru.

## Defter

- **`HF_H3`'ün başına bir satır**, öteki H3 satırlarının kalıbında, iki satıra bölünmüş:
  `("TenStrip/10Eros-Max", "10Eros_Max_h3_TURBO-hybrid_beta5_int8.safetensors", H3DIFF,
  "10Eros_Max_h3_TURBO-hybrid_beta5_int8.safetensors", "H3 Eros Max beta5", None)`. Başta, çünkü grup
  da modelle başlıyor. Etiket öteki H3 satırlarının kalıbında *("H3 …")*; konsolda ve özet
  tablosunda bu okunuyor. Taban yok: dosya safetensors, başlığıyla doğrulanıyor.
- **`CIVITAI_H3`'ten DaSiWa'nın satırı çıkıyor.** Motion Booster ve Mystic kalıyor.
- Yorum yok — defterin kod hücreleri yalnız bölüm başlığı taşıyor.
- **Disk tahmini değişmiyor:** DaSiWa 20.967.669.168, Eros 20.970.414.464 bayt; H3'ün `37` GiB'ı yerinde.
- **Tavan:** Eros'un satırı DaSiWa'nınkinden ~15 karakter uzun;
  `test_the_notebook_stays_well_under_what_the_tools_can_read` yeşil kalmalı. Kalmazsa satır
  kısaltılmaz, durulup sorulur — tavanı yükseltmek bir karar *(testin kendi sözü)*.
- **Repo herkese açık:** HF'nin model API'si 24 Eylül'de `"gated": false`, `"private": false` dedi —
  indirme token istemiyor. İleride kapanırsa `hf_fetch` HF'nin kendi cevabını basıyor
  *(`H3 Eros Max beta5: HF TenStrip/10Eros-Max/… — …`)*, sebep uydurulmadan.

## Belgeler — tarandı, değişen yok

- **README:** `VIDEO_H3 (~37 GiB)`, `CIVITAI_COOKIE` ve `HF_TOKEN` satırları H3'ün modelini anmıyor ve
  doğru kalıyor — H3 koşusu Mystic'i yine aynasız Civitai'den indiriyor, çerez yine gerekiyor.
- **Defterin markdown hücreleri:** giriş hücresi ve *"Modeller — … Civitai'dekiler önce HF
  aynasından"* başlığı H3'ün modelini anmıyor.
- **`docs/`:** DaSiWa'yı H3'ün modeli diye anan yerler tarihli spec'ler, planlar ve yol haritaları
  *(m242, m243, m310–m312, m327, v5 ve v7)* — tarih, dokunulmuyor.
  `collab-toolbox/video_experiments/minimax-h3/` başka aracın kendi denemesi; o da.
- **Kod:** `MIRRORLESS`'in yorumu *("while the user tries it (madde 328)")* doğru kalıyor. Üreticinin
  `DaSiWa_SeedControl`'ü ve defterin `ComfyUI-DaSiWa-Nodes`'u düğüm paketinin adı, model değil;
  fotoğrafın DaSiWa Illustrious'u ayrı bir model. `test_colab_downloads.py`'deki `3314686`'lar
  indirme kodunun örnek numaraları.

## Değişmeyen

Üretici, video prompt'unun yazıcısı, ekran, `MIRRORLESS`, Mystic'in defter satırı, örnekleyici
*(euler/simple, 8 adım)*, disk tahmini, README. Derlenecek bir şey yok.

## Bitti sayılır

Dört test satırı yeşil — defterin tavan testi dahil, `skip` / `xfail` yok; kod, grafikler, defter,
spec ve plan tek commit.
