# Madde 285 · Ekran V6 diyecek — uygulama turunun tasarımı

**Tarih:** 21 Eylül 2026 · **Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md) ·
**Test turu:** [tasarımı](2026-09-21-queen-editor-m285-surum-testler-design.md)

## Kullanıcıdan gereken

Hiçbir şey.

## Çivilenmiş olgunun istediği kod

**Tek satır:** `version.js`'te `VERSION = "V6"`. Sayıyı tutan tek yer o, ve dört ekran onu
çiziyor.

**Hiçbir test değişmiyor**, ve bu test turunun kazancı: başlık artık modülün değerini arıyor, yani
sayı değişince test onunla birlikte değişiyor. Sayının kendisi hiçbir yerde sabit değil *(248)*.

**`frontend/dist/` aynı commit'te yeniden build'leniyor** — defter depoyu klonluyor ve hiçbir şey
build etmiyor *(FOUNDATION 3)*; build'siz bir commit Colab'da eski başlığı gösterir.

## Bu turda değişen

- `frontend/src/shared/version.js`: sayı.
- `frontend/dist/`: yeniden build.
