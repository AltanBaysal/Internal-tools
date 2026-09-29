# Madde 379 — CODE-STANDARD'ın hareket paragrafı yalnız bugünü anlatır · test turu

**Kaynak:** [yol haritasının 379'u](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md) — 340'ın
subagent'ı buldu; `.rail__head--still` yorumunu 350'ninki. Karar kullanıcının, 29 Eylül: "Kural
kalksın, paragraf yalnız bugünkü durumu anlatsın."

**Kullanıcıdan gereken:** hiçbir şey. Madde hizalı; kod değişmez.

## Bugün ne doğru

Frontend'in iki stil dosyası var, ve hareket şunlar:

- `shared/app.css`: `@keyframes fadeIn` (opaklık) ve `@keyframes blink` (üç nokta, iskelet).
- `features/workspace/workspace.css`: `@keyframes msg-spin` — bir dönüş; canlı satırın spinner'ı
  (`.msg__spinner`), ve `Spinner.jsx`'in `.spinner`'ı: dosya listesi yüklenirken ve sohbet açılırken.
- Geçişler, hepsi `workspace.css`'te: kenar çubuğu (`.sidebar`, 351) ve rail (`.rail`) genişlikleriyle
  katlanır, 220ms; rail sürüklenirken geçiş kapanır (`.rail--dragging`); mesajın kalemi opaklıkla
  belirir (`.msg__edit`).

CODE-STANDARD'ın paragrafı "iki keyframe", "üçüncü animasyon icat edilmez" ve "fade olmayan tek hareket
rail'in genişliği" diyor — üçü de yanlış.

## Ne kanıtlanacak

1. **Paragraf, frontend'in tanımladığı her keyframe'i adıyla söyler.** Test iki stil dosyasındaki her
   `@keyframes <ad>`'ı bulur ve CODE-STANDARD.md'de `` `<ad>` ``'ı arar. Bugün `msg-spin` orada yok:
   kırmızı. Yarın biri dördüncü bir animasyon eklerse test onu yasaklamaz — yalnız paragrafın
   söylemesini ister, ve paragraf bugünü anlatmaya devam eder.
2. **Paragraf yasak koymaz ve eski yanlışı söylemez.** CODE-STANDARD.md'de `never invents` ve
   `The only motion` geçmez. Bugün ikisi de geçiyor: kırmızı.

Testler `app.css.test.js`'e girer — hareketin kilidi orada. CODE-STANDARD.md'yi, arka ucun
`test_pin_archive.py`'sinin tablosu okuduğu gibi dosyadan okurlar.

## Kaldırılan kuralı taşıyan testler

`app.css.test.js`'te dört test, adıyla ve yorumuyla kaldırılan kuralı söylüyor. Onlar bugünün doğrusuna
çevrilir; tasarımın gerçeğini tutan iddialar kalır:

- **"there is one fade and one blink, and nothing else"** ve üstündeki yorum ("Motion is a fade …
  and nothing else", "only one animation name survives") → app.css'in fade'i ve blink'i tuttuğunu
  söyler. `riseIn` ve `slideIn` yokluğu kalır: tasarımda yerleşmiş bir öğe kaymaz, yükselmez.
  **`@keyframes spin` yokluğu gider:** bugün tasarımın bir spinner'ı var, ve o satır "dönen bir şey
  yok" demekti — kaldırılan kuralın kendisi.
- **"no keyframe moves anything"** yalnız app.css'e bakıyor, ama adı her keyframe'i kapsıyor, ve
  `msg-spin` `transform` ile döner. Ad dürüstleşir: app.css'in keyframe'leri yalnız opaklığı
  değiştirir. İddia aynı kalır.
- **"every animation stays inside the band"**: bant — fade'lerin 140–220ms'si — tasarımın gerçeği ve
  kalır. Ama deseni `(\w+)` `msg-spin`'i tirede kaçırıyor; spinner bugün testten kazayla geçiyor.
  Desen tireli adları da okur, ve `msg-spin` `blink` gibi adıyla ve nedeniyle atlanır: ikisi de hiç
  durmaz. `animation: spin` yokluğu gider — yukarıdakiyle aynı neden.
- **"the rail's width transition is the one motion that is not a fade"** → ad, rail'in genişliğiyle
  katlandığını söyler; iddia aynı kalır. Kenar çubuğunun genişliği `workspace.css.test.js`'in 351
  testinde zaten tutuluyor.

Bu dört değişiklik bugün de yeşil — kod değişmiyor, yalnız adlar ve yorumlar bugünü söylüyor.

## Testler ne tutmaz

`.rail__head--still`'in yorumu: bir yorum; doğruluğu testle değil okunarak görülür. Uygulama turunda
düzelir. Paragrafın cümleleri de tek tek tutulmaz — test yalnız her keyframe'in adını ve yasağın
yokluğunu ister; gerisini paragrafı okuyan görür.

## Bu turda yazılmayanlar

- CODE-STANDARD.md, `app.css`, `workspace.css` değişmez; uygulama turunda.
- `dist` derlenmez: kaynak değişmiyor, yalnız testler ve belgeler.

## Nasıl görülür

CLAUDE.md'deki dört satır, paralel. `npm test --prefix queen-agent/frontend` iki yeni testte kırmızı
verir; çevrilen dört test yeşil kalır. Öteki üç süit değişmez. Kırmızı hâliyle commit edilir.

Adım adım dökümü
[test turunun planında](../plans/2026-09-29-queenagent-m379-hareket-paragrafi-testler-plan.md).
