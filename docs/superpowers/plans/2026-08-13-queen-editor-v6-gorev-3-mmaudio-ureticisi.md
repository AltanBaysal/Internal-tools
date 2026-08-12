# Görev 3 — MMAudio üreticisi · Uygulama planı

> **Ajanlar için:** GEREKLİ ALT BECERİ: bu planı superpowers:executing-plans ile uygula.

**Amaç:** Ses üretimini ComfyUI grafiğinden alıp süreç içinde koşan MMAudio'ya vermek, defterin
ayarlarıyla birebir.

**Tasarım:** [spec](../specs/2026-08-13-queen-editor-v6-gorev-3-mmaudio-ureticisi-design.md)

## Genel kısıtlar

- `torch`/`mmaudio` import'u **fonksiyon içinde** — modül seviyesinde import takımı çökertir.
- Üretici portunun imzası değişmez: `generate(prompt, negative, seed, model="", source=None)`,
  dönüş `(ad, bayt)`.
- Test: `python -m pytest queen-editor -q`. Ön yüz değişmiyor.

---

### Task 1: Parçalama kuralı

**Dosyalar:**
- Oluştur: `queen-editor/backend/features/photo_generation/domain/audio_chunks.py`
- Test: `queen-editor/backend/tests/test_audio_chunks.py`

**Arayüz:** `chunks(total, target=8.0, maximum=10.0) -> [(start, duration), ...]`

- [ ] **Adım 1: Düşen testleri yaz** — 8 sn tek parça; 10 sn tek parça (sınır dahil); 24 sn üç
      parça; 20 sn iki parça; parçaların toplamı süreye eşit.
- [ ] **Adım 2: Koş, düştüklerini gör**
- [ ] **Adım 3: Kuralı yaz** — defterin `calculate_chunks`'ı:
      `n = max(ceil(total/maximum), round(total/target), 1)`, eşit bölüm.
- [ ] **Adım 4: Koş, geçtiklerini gör**

---

### Task 2: ffmpeg tarafı

**Dosyalar:**
- Oluştur: `queen-editor/backend/features/photo_generation/data/ffmpeg_audio.py`
- Test: `queen-editor/backend/tests/test_ffmpeg_audio.py`

**Arayüz:** `FfmpegAudio(run=None, ffmpeg="ffmpeg", ffprobe="ffprobe")` —
`duration(path)`, `cut(src, start, dur, target)`, `join(parts, target, fade_ms)`.

`cut` her zaman 25 fps + 720p + CFR uygular; tek parçalık videoda da aynı komut kullanılır
(`start=0`, tüm süre), böylece iki ayrı yol bakılmaz.

- [ ] **Adım 1: Düşen testleri yaz** — `duration` ffprobe çıktısını float döndürür; `cut`
      komutunda `-ss`, `-t`, `fps=25,scale=-2:720`, `-an` var; `join` tek parçada kopyalar, çok
      parçada `acrossfade` zinciri kurar; hata ffmpeg'in son satırıyla gelir.
- [ ] **Adım 2: Koş, düştüklerini gör**
- [ ] **Adım 3: Yaz** — `ffmpeg_video_exporter.py`'nin `_ffmpeg_run` deseni birebir.
- [ ] **Adım 4: Koş, geçtiklerini gör**

---

### Task 3: Üretici

**Dosyalar:**
- Oluştur: `queen-editor/backend/features/photo_generation/data/mmaudio_generator.py`
- Test: `queen-editor/backend/tests/test_mmaudio_generator.py`

**Arayüz:** `MMAudioGenerator(sampler, ffmpeg, tmp_dir=None)`; `sampler.render(video_path, prompt,
negative, seed, duration) -> bytes` (wav).

- [ ] **Adım 1: Düşen testleri yaz** — kaynak yoksa `RuntimeError("Ses için kaynak video
      verilmedi")`; örnekleyiciye prompt/negatif/seed doğru gider; boş negatif sabiti kullanır,
      dolu negatif kazanır; 5 sn video tek çağrı; 24 sn video üç çağrı ve `join` çağrılır;
      dönüş `("<ad>.wav", bayt)`; hata hâlinde geçici klasör silinir.
- [ ] **Adım 2: Koş, düştüklerini gör**
- [ ] **Adım 3: Yaz**
- [ ] **Adım 4: Koş, geçtiklerini gör**

---

### Task 4: Örnekleyici (dış dünya)

**Dosyalar:**
- Oluştur: `queen-editor/backend/features/photo_generation/data/mmaudio_sampler.py`

Testi yok *(spec karar 7)*: torch ve mmaudio bu makinede yok, sahte bir torch yazmak kendi
sahtemizi test etmek olurdu.

- [ ] **Adım 1: Yaz** — ilk `render` çağrısında import + ağırlık yükleme, sonra saklama.
      Defterin model yükleme hücresi birebir: `get_my_mmaudio` + `load_file(nsfw)` +
      `FeaturesUtils`, `float16`, `large_44k`.
- [ ] **Adım 2: Tam takımı koş** — yeni dosya hiçbir testi kırmamalı (import edilmiyor).
- [ ] **Adım 3: Commit**
