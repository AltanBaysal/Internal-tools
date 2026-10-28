# Madde 234 · Detayda silinen kareden sonra gidilen yönde kalınır — uygulama turunun tasarımı

**Tarih:** 17 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md) ·
**Testler:** [test turu](2026-09-17-queen-editor-m234-silince-yon-korunur-testler-design.md)

## Kullanıcıdan gereken

Hiçbir şey.

## Tasarım

[`PhotoDetail.jsx`](../../../queen-editor/frontend/src/features/photo_generation/PhotoDetail.jsx)
kareyi değiştiren son basışın yönünü bir **`useRef`**'te tutuyor. State değil, çünkü yön ekranda
hiçbir şeyi değiştirmiyor, yalnız silmenin nereye gideceğini söylüyor.

- Ekrandaki iki ok ve iki tuş bugün `navigate`'i dört ayrı yerde çağırıyor. Dördü tek bir `step`
  fonksiyonundan geçer, o da yönü yazıp adrese gider. Böylece yönü yazmayı unutan bir kapı kalmaz.
- `handleRemove` geriye gidiliyorsa `previous || next`, değilse bugünkü `next || previous` seçer.
- Silme sonrası geçiş yönü **değiştirmez**, yani art arda silmek aynı yönde ilerler.
- Ref sayfayla yaşıyor. Oklar sayfayı yeniden kurmadığı için yön kareler arasında korunuyor.
  Galeriden yeniden açılan detay yeni bir sayfa, yönü de bugünkü gibi ileri başlıyor.

FOUNDATION 4'e uygun: bu bir kural değil, sayfanın kendi gezinmesi, ve sunucunun bilmesi gereken
hiçbir şey yok.

## Bu turda değişen

Yalnız `PhotoDetail.jsx` ve derlenmiş `dist/`.
