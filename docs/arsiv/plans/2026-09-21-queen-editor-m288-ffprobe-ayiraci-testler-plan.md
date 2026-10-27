# Madde 288 · `sound()`'un ffprobe ayıracı — test turunun planı

**Spec:** [test turu](../specs/2026-09-21-queen-editor-m288-ffprobe-ayiraci-testler-design.md) ·
**Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md)

## Adımlar

**1 · `sound()`'un komutunu birebir okuyan test.** Tek parçalı bir birleştirme koşulur, ve
`sound_calls(run)`'ın ilk çağrısı **tam liste** olarak karşılaştırılır:
`["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries",
"stream=sample_rate,channel_layout", "-of", "csv=p=0", "a.mp4"]`. Olgu 1 — kırmızı.

**2 · `size()`'ın komutunu birebir okuyan bekçi testi.** Aynı biçimde, `csv=s=x:p=0` ile. Olgu 2 —
doğuştan yeşil, ve spec'te sebebi yazılı.

**3 · `FakeRun`'ın cevabı yeni ayıraca döner.** `sounds` sözlüğünü veren üç testte `"48000:stereo"`
→ `"48000,stereo"`, `"44100:mono"` → `"44100,mono"`; ikizin kendi kodu değişmiyor, yalnız
konuştuğu biçim. Olgu 3 — sessizlik yazan iki test kırmızıya döner, hepsi-sesli testi yeşil kalır.

**4 · Takım:** dört satır paralel. Kırmızı yalnız queen-editor arka ucunda, ve **üç** tane.

**5 · Commit** (kırmızı).
