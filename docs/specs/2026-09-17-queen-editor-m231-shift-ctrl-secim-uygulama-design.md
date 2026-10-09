# Madde 231 · Galeride Shift ile aralık, Ctrl ile tek tek seçim — uygulama turunun tasarımı

**Tarih:** 17 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md) ·
**Testler:** [test turu](2026-09-17-queen-editor-m231-shift-ctrl-secim-testler-design.md)

## Kullanıcıdan gereken

Hiçbir şey.

## Ne değişiyor

Yalnız `Gallery.jsx`:

- **Çapa bir `useRef`.** Ekranda hiçbir şey çizmiyor, yani değişmesi yeniden çizim istemiyor.
- **Tek bir `press(fid, event)`** üç basma yolunun hepsini karşılıyor: halka, kart ve kartın bağlantısı.
  - Shift varsa, seçim açıksa ve çapa galerideyse: çapadan tıklanan karta kadar olan kimlikler
    galerinin sırasıyla alınıyor, worker'ın tuttuğu çıkarılıyor, ve seçimde olmayanlar ekleniyor.
    Çapa yerinde kalıyor.
  - Öteki her durumda: çapa bu kart oluyor ve kart bugünkü `toggle` ile ekleniyor ya da çıkarılıyor.
    Ctrl'ün işi tam bu, ayrı bir dalı yok.
- **Kartın `onClick`'i** artık yalnız seçim açıkken değil, tuşlardan biri basılıyken de `press`
  çağırıyor.
- **Bağlantı** tuşlardan biri basılıyken detayı açmıyor.
- **Halka** olayı `press`'e geçiriyor, böylece halkaya Shift ile basmak da aralık seçiyor.

Tuşlar: `shiftKey`, `ctrlKey` ve Mac için `metaKey`.
