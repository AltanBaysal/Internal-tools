# Madde 283 · Tekli çıktılar kendi klasörüne — test turunun planı

**Spec:** [test turu](../specs/2026-09-21-queen-editor-m283-klasorler-testler-design.md) ·
**Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md)

## Adımlar

**1 · `ExportStore` ikizi `make_videos_dir(folder)`'ı yazıyor** — tekli modun yazdığı yer,
`f"{folder}/video"`.

**2 · Tekli export'un hedeflerini söyleyen mevcut testler `video/` altına taşınıyor** — sayı ve
sıra aynı, yol değişiyor. Olgu 1, 4.

**3 · Olgu 2:** store'un kendi testinde klasör adı `foto`.

**4 · Olgu 5'in testi:** tekli export hiçbir şey silmiyor — bugün de öyle, ve uygulama turunda
koşul moda bağlanmazsa kırmızıya döner.

**5 · Olgu 3, 6, 7:** mevcut testler zaten tutuyor; dokunulmuyor.

**6 · Takım:** dört satır paralel. Kırmızı yalnız queen-editor arka ucunda.

**7 · Commit** (kırmızı).
