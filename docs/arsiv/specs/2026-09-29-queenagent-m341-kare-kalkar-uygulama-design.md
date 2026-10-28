# Madde 341 — Yanıp sönen kare kalkar · uygulama turu

**Kaynak:** [yol haritasının 341'i](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md) (v9-2g);
tasarımın 156'sı. **Testler:** [test turunun spec'i](2026-09-29-queenagent-m341-kare-kalkar-testler-design.md).

**Kullanıcıdan gereken:** hiçbir şey.

## Ne değişir

Kareyi yalnız süren cevap istiyordu; o istemeyince kareye ait her şey gider:

- **`ChatScreen.jsx`:** `<Markdown text={streamingText} caret />` → `<Markdown text={streamingText} />`.
  Tek satır: 344 aynı dosyayı bölüyor, birleştirmede taşınacak iz küçük kalsın.
- **`Markdown.jsx`:** `Caret` bileşeni, `caret` özelliği ve `blockList` ile `block`'un `caret`
  girdisi kalkar. Kareye yer açmak için var olan sarmalar da gider: çizginin ve tablonun `Fragment`'i
  — çizgi yalnız `<hr>`, tablo yalnız kaydırıcısı olur —, ve kullanılmayan `Fragment` içe aktarması.
  Kareyi anlatan üç yorum gider; tablonun kaydırıcısını anlatan yorum kalır.
- **`workspace.css`:** `.caret` kuralı ve yorumu kalkar. `blink` animasyonu `shared/app.css`'te
  kalır: üç nokta onu kullanıyor.

## Değişmeyenler

- **Üç nokta:** ilk parça gelene kadar yanıp söner; tasarımın 156'sı yalnız kareyi kaldırıyor.
- **Süren satır** (`Pondering…`) ve biten cevabın çizimi.
- **FOUNDATION.md ve CODE-STANDARD.md:** dosya eklenmiyor ya da silinmiyor, tablolar değişmez;
  `shared/app.css`'in iki animasyonu hâlâ iki.

## Nasıl görülür

Dört satır yeşil: queen-agent'ın ön ucu 643 test, queen-editor'ün arka ucu 377'nin bilinen iki
kırmızısıyla. Tarayıcıda: bir soru gönderilince cevap gelirken yazının sonunda kare yok, altında
`Pondering…` gibi kelime dönüyor. `dist` burada derlenmez: koşuyu yöneten Claude birleştirirken
derler.

Adım adım dökümü [uygulama turunun planında](../plans/2026-09-29-queenagent-m341-kare-kalkar-uygulama-plan.md).
