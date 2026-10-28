# Madde 312 — Yüksek hız, indirme özeti ve hücre süreleri, implementasyon turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 2/2 — kod, takım yeşile döner.
**Turun testleri:** [m312 test turu](2026-09-23-queen-editor-m312-hiz-ve-sureler-testler-design.md),
`4524b104` ile kırmızı commit'lendi.

**Kullanıcıdan gereken:** yok.

## `colab/downloads.py`

- **Yüksek hız:** `hf_fetch`, `huggingface_hub`'ı import etmeden önce
  `os.environ["HF_XET_HIGH_PERFORMANCE"] = "1"` yazıyor. HF'nin belgesine göre değişkenler import
  anında okunuyor, ve defterde kütüphaneyi ilk import eden `hf_fetch`. Aynaya yükleme de ondan sonra
  geliyor, yani yükleme de bu ayarla çalışıyor. Değer koşulsuz `1`, çünkü ayar her koşuda açık.
- **Satırlar:** `_landed` konsol satırını basıyor ve `(etiket, bayt, saniye)` döndürüyor. `fetch` ile
  `hf_fetch` bunu döndürüyor; yerinde duran dosyanın erken dönüşü `None`. `civitai_fetch` aynadan
  inişte `hf_fetch`'in satırını, düşüşte `fetch`'in satırını döndürüyor. Yükleme satıra girmiyor.
- **`download_summary(rows)`:** `None`'ları atıyor. Hiç satır kalmazsa tek `log` satırı basıyor:
  `İndirme özeti: bu koşuda inen dosya yok`. Satır varsa başlık `İndirme özeti:`, altında satırlar,
  en altta `Toplam` geliyor. Toplam boyutların ve sürelerin toplamı; hızı toplam boyut bölü toplam
  süre, yani ortalama. Toplam süre indirmelerin süresi. Yüklemeler ve yoklamalar dahil hücrenin kendi
  süresi, sayacın satırında. Etiket sütunu en uzun etikete göre hizalı. Süreyi `_duration` yazıyor:
  `1 dk 40 sn`, bir dakikanın altında `20 sn`.

## Defter

- **CONFIG:** hücre `# === Cell timer ===` bölümüyle açılıyor, `# === CONFIG ===`'dan önce. Bölüm
  yalnız `time` ile `IPython.get_ipython`'u kullanıyor:
  - `_cell_began` hücrenin başladığı anı tutuyor.
  - `cell_elapsed()` o andan beri geçen süreyi `1 dk 50 sn` biçiminde veriyor.
  - `_cell_ended` `⏱️ Hücre … sürdü` satırını basıyor.
  - Kancalar `pre_run_cell` ve `post_run_cell`'e takılmadan önce aynı adlı eski kancalar sökülüyor.
  - Bölüm `_cell_began()` ile bitiyor: kanca takıldığında CONFIG zaten başlamıştı, CONFIG'in kendi
    süresi de sayılsın diye.
- **Yardımcılar:** import satırına `download_summary` ekleniyor.
- **Modeller:** `landed = []` HF döngüsünden önce açılıyor, ve üç döngü de `landed.append(…)` yapıyor.
  Klasör listesinden sonra, son iki `log`'dan önce `download_summary(landed)` geliyor.
- **Flask:** `🔗 Queen Editor` satırının hemen üstüne `print(f"✓ Link {cell_elapsed()}'de hazır")`.

**Süre biçimi iki yerde duruyor:** `cell_elapsed` ile `_duration` aynı `dk / sn` biçimini yazıyor.
Sayaç klondan önce çalıştığı için modülü import edemiyor; iki satırlık kopya onun bedeli.

## CODE-STANDARD

`## Notebook code (colab/)` bölümüne bir paragraf ekleniyor: defterin hücrede kalan tek kodu sayaç,
ve sebebi. Defter kod hücrelerinde yorum taşımadığı için bunu kod söyleyemiyor.

## Bitti sayılır

Dört test satırı koşulur ve dördü de yeşil. Defter 29.000 karakter tavanının altında kalır.
