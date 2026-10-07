# Madde 306 — Ok tuşları, test turunun planı

**Spec:** [m306 test turu](../specs/2026-09-21-queen-editor-m306-ok-tuslari-testler-design.md)

Tek test dosyası: `PhotoDetail.test.jsx`. Kaynak koda dokunulmuyor.

## Adımlar

1. Üç test: kutudan gelen iki ok ve Escape, ve kutunun dışından bir ok.
2. Tuş **kutunun kendisine** gönderiliyor — `fireEvent.keyDown(kutu, …)`. Olay pencereye kadar
   yükseliyor, ve dinleyicinin göreceği şey `event.target`: gerçekte de öyle oluyor.
3. **Dört test satırı koşulur.**

## Beklenen kırmızı

İki test: dinleyici bugün odağa hiç bakmıyor. Kutu dışındaki bekçi bugün de yeşil.
