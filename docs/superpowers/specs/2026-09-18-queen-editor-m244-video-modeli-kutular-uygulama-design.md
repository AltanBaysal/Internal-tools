# Madde 244 · Defterde video yine bir kutu, modeli altında — uygulama turunun tasarımı

**Tarih:** 18 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md) ·
**Testler:** [test turu](2026-09-18-queen-editor-m244-video-modeli-kutular-testler-design.md), commit `3eb75988`

## Kullanıcıdan gereken

Hiçbir şey.

## Tasarım

Ne olacağı test turunun spec'inde yazılı. Burada yalnız nereye gittiği var.

**`queeneditor.ipynb`:**
- **CONFIG:**
  - `INSTALL_VIDEO` yeniden bir kutu.
  - Fotoğraf modellerinin altında `---` ayracı ve **Video modelleri** başlığı, içinde `VIDEO_WAN`
    ve `VIDEO_H3`.
  - Fotoğrafın kontrolünün yanına iki kontrol giriyor.
  - `VIDEO_MODEL = ("wan" if VIDEO_WAN else "h3") if INSTALL_VIDEO else ""`.
  - Üreticiler satırında H3'ün T4 bilgisi yok.
- **Modeller hücresi:** Listeler, disk hesabı ve özet `VIDEO_MODEL == "wan"` / `"h3"` ile
  okuyor.
- **Flask ortamı:** `"QE_VIDEO_MODEL": VIDEO_MODEL`. Değer zaten küçük harfli ve boş olabiliyor.
- **Giriş:** 3. adım kutuları anlatıyor.

**`README.md`:** Run bölümü `VIDEO_WAN` / `VIDEO_H3`'ü anıyor. H3'ün T4 bilgisi çıkıyor.

Uygulamanın kodu değişmiyor.

## Bu turda değişen

Defter, README ve yol haritasında 244'ün işareti. Testlere dokunulmuyor.
