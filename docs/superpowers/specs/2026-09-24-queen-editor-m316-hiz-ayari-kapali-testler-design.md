# Madde 316 — HF'nin yüksek hız ayarı şimdilik kapanıyor, test turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 1/2 — yalnız testler, kırmızı commit'lenir.

**Kullanıcıdan gereken — yok.** Deneme kullanıcının, iş bittikten sonra.

## Bugün ne oluyor

`hf_fetch`, `huggingface_hub`'ı import etmeden önce `HF_XET_HIGH_PERFORMANCE`'ı `1` yapıyor
*(madde 312)*. Ayar açıkken ilk denemede HF'nin parça sunucusu 429 döndü ve koşu düştü; kapalıyken
iki tam koşuda 429 hiç gelmedi. 312'nin testi ayarın açıldığını tutuyor:
`test_hugging_face_s_downloader_is_taken_in_high_performance_mode`.

## Kural

**`hf_fetch` yüksek hız ayarına dokunmuyor.** Ortamda ne yazıyorsa o kalıyor; yeni bir Colab
makinesinde onu kimse yazmadığı için `hf_xet` kendi varsayılanıyla, 312'den önceki gibi iniyor. Ayar
313'le geri gelir — o, 429 çözülene kadar backlog'da.

## Yazılacak test

### `test_colab_downloads.py` — koşularak

1. **HF'nin indiricisi yüksek hız ayarı açılmadan alınıyor** — ortamda `HF_XET_HIGH_PERFORMANCE=0`
   varken `hf_fetch` bir dosya indiriyor; ardından değişken hâlâ `0`.

**Değişen:** `test_hugging_face_s_downloader_is_taken_in_high_performance_mode` yerini 1'e bırakıyor —
aynı soru, ters cevap.

**Bekçiler, bugün de yeşil:** indirme testlerinin kalanı — satırlar, özet tablosu, ayna, Civitai;
hiçbiri ayara bakmıyor.

## Bitti sayılır

Dört test satırı koşulur; `queen-editor` pytest kırmızı — yalnız 1.
