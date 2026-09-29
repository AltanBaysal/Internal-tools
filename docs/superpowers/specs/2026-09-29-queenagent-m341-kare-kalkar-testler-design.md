# Madde 341 — Yanıp sönen kare kalkar · test turu

**Kaynak:** [yol haritasının 341'i](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md) (v9-2g);
tasarımcının v3 roadmap'inin 156'sı — *"yazıyor efektini kaldır, yanan sönen kareyi; yazıda zaten
pondering vs gibi şeyler döndürüyoruz, Claude Code gibi, gerek yok"* (kullanıcı, 28 Eylül). Tasarımın
`BEHAVIOUR.md`'si: sayfada kare yok, uygulama hâlâ çiziyor (`Markdown.jsx`, `Caret`).

**Kullanıcıdan gereken:** hiçbir şey.

## Ne kanıtlanacak

Cevap gelirken yazının sonunda kare çizilmez: süren cevabın yazısı, gelen metinden başka hiçbir şey
taşımaz. Süren satırdaki kelime (`Pondering…`) ve ilk parça gelene kadar yanıp sönen üç nokta yerinde
kalır — tasarımın 156'sı yalnız kareyi kaldırıyor.

## Testler ne tutar, ne tutmaz

**Tutar** — `ChatScreen.test.jsx`'teki *"only the text still arriving carries a caret"* testinin
yerine tek test: süren cevap `Here it` iken, süren mesajın `.md`'si yalnız `<p>Here it</p>`. Bu,
kareyi sınıf adından bağımsız tutar: yazının sonunda metinden başka bir şey çizilirse kırmızı olur.

**Silinenler** — kaldırılan şeyi anlatan testler:

- `Markdown.test.jsx`'teki kare testleri (`drawStreaming` ve yorumuyla birlikte sekiz test):
  `caret` özelliği uygulama turunda kalkıyor; onu anlatan test ölü test olur. *"a finished answer
  carries no caret"* de gider: özellik kalkınca hiçbir yol kare çizemez, test hiçbir şey tutmaz.
- `workspace.css.test.js`'teki *"the caret is the design's block and borrows the dots' blink"*:
  kural uygulama turunda kalkıyor. Yerine bir yokluk testi yazılmaz — davranışı ChatScreen'in testi
  tutuyor, ve kuralın yokluğunu kilitlemek ölçü değil, bir iz olur.

**Tutmaz:** üç noktayı ve süren satırı — mevcut testleri zaten tutuyor, ve bu madde onlara dokunmuyor.

## Bu turda yazılmayanlar

- `Markdown.jsx`, `ChatScreen.jsx` ve `workspace.css` değişmez; uygulama turunda.
- `dist` derlenmez: koşuyu yöneten Claude birleştirirken derler.

## Nasıl görülür

CLAUDE.md'deki dört satır. `npm test --prefix queen-agent/frontend` bir kırmızı verir — yeni test,
çünkü paragrafın sonunda bugün `<span class="caret">` var. queen-editor'ün arka ucu 377'nin bilinen
iki kırmızısıyla kalır; öteki süitler yeşil. Kırmızı hâliyle commit edilir.

Adım adım dökümü [test turunun planında](../plans/2026-09-29-queenagent-m341-kare-kalkar-testler-plan.md).
