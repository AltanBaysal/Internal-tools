# Madde 253 · Kodlama GPU'ya geçecek — uygulama turunun planı

**Spec:** [uygulama turu](../specs/2026-09-21-queen-editor-m253-gpu-kodlama-uygulama-design.md) ·
**Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md)

## Adımlar

**1 · Sabitler:** `_ENCODE` → `_GPU_ENCODE` ve `_CPU_ENCODE`.

**2 · `_encoder()`:** ffmpeg'e bir kez sor, cevabı sakla, soramazsa CPU'da kal. Olgu 1, 2, 3, 5.

**3 · İki çağrı:** `piece()` ve `merge()` sabiti değil `_encoder()`'ı kullanıyor.

**4 · Takım:** dört satır paralel. Beklenen: hepsi yeşil.

**5 · Commit** (yeşil). Ardından 255, ve ölçüm geldiğinde 256'nın açılıp açılmayacağı.
