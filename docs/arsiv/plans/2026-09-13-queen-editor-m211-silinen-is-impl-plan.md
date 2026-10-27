# Madde 211 · Silinen işin satırı kalıyor — uygulama turunun planı

**Spec:** [uygulama turu](../specs/2026-09-13-queen-editor-m211-silinen-is-uygulama-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

Kırmızı `91bc4e5`'te. Bu tur `queue.py`'ı değiştirir; teste dokunulmaz.

## Adımlar

**1 · `_latest_per_frame` yazılır**, `open_jobs`'un hemen üstüne. Aldığı liste tek türe ait iş
satırları; döndürdüğü, her kare için yalnız **son** satır, ve **planın kendi sırasında** — o karenin
son satırının durduğu yerde.

Sözü neden var: durum (kare, katman) başına tek hücre, plan ise o çift için birden çok satır
taşıyabiliyor; hücre açılınca hepsi birden açılıyor, ve en eskisi — yani atılmış olanı — sıranın
başına geçiyor.

**2 · `open_jobs` onu kullanır.** Tür süzgecinin hemen ardında, `fresh`/`requeued` ayrımından önce:
ayrım durumu okuyor, ve okunacak satır zaten teke inmiş olmalı.

**3 · Takım koşulur**, dördü de:

```
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

Üç kırmızı yeşile döner. **Okunacak iki şey:** 14 Ağustos'un üç çivisi ayakta kalmalı, ve
`test_only_one_video_is_made_after_the_first_was_dropped` yeşil kalmalı — düzeltme yeni satırı öne
almakla yetinseydi o düşerdi.

`test_frame_queue.py`'daki sıralama çivileri de bu adımda konuşur: sıra değişmemeli.

**4 · Yeşil commit'lenir.** `dist` yok — ön yüz değişmiyor.

## Değişen dosya

`queen-editor/backend/features/photo_generation/domain/queue.py`.
