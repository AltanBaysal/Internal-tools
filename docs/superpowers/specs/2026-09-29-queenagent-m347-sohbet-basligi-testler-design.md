# Madde 347 — Sohbet başlığında yalnız sohbetin adı · test turu

**Kaynak:** [yol haritasının 347'si](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md) (v9-2d);
tasarımcının v3 roadmap'inin 152'si — *"inside project daha basit olabilir, proje adı tek bir merkezi
yerde yazsa yeter zaten"* (kullanıcı, 28 Eylül) — ve 168'i: *"Sohbet başlığında yalnız sohbetin adı
(`←` ve proje adı yok)."* Tasarımın `chat/index.html`'i başlığa yalnız `.chat__title` koyuyor; projenin
adı 338'den beri üst çubukta, ve oradaki `Exit project` projeden çıkışın yolu.

**Kullanıcıdan gereken:** hiçbir şey.

## Ne kanıtlanacak

Sohbet açıkken başlıkta yalnız sohbetin adı var: `←` düğmesi, projenin adı ve aradaki `/` yok.

## Testler ne tutar, ne tutmaz

**Tutar** — `ChatScreen.test.jsx`'te iki eski testin yerine iki test:

- *"the breadcrumb names the project and the chat"* yerine: başlığın bütün yazısı sohbetin adı —
  `.chat__header`'ın `textContent`'i tam olarak `Write the intro`. Proje adı, `←` ya da `/` başlıkta
  kalırsa kırmızı olur.
- *"the way back to the project stays"* yerine: başlıkta hiçbir düğme yok, ve ekranın hiçbir yerinde
  projenin adı yazmıyor. Ekran ona proje verilse bile adını çizmez — ad çubuğun.

**Değişenler** — `App.test.jsx`'te sohbet başlığındaki `← Old`'a basıp proje ekranına giden üç test:
*"the sidebar folds away and comes back…"*, *"opening a file unfolds the rail…"* ve *"a skill picked in
a chat does not ride into a chat born on the project screen"*. Dertleri başlığın düğmesi değil, proje
ekranına geçmek; o düğme kalkınca oraya çubuğun `Exit project`'iyle giderler — bugün `/` tek projeli
testlerde `/p/p1`'e iner. Bu turda da yeşil kalırlar.

**Tutmaz:** `.chat__slash` kuralının yokluğu — 341'in kararıyla, bir kuralın yokluğunu kilitlemek bir
iz olur; davranışı ChatScreen'in testi tutuyor. Sohbet yüklenirken duran tek başına `← back` da bu
maddenin değil *(v9-2l)*: onu anlatan testlere dokunulmaz.

## Bu turda yazılmayanlar

- `ChatScreen.jsx`, `App.jsx` ve `workspace.css` değişmez; uygulama turunda.
- `dist` derlenmez: koşuyu yöneten Claude birleştirirken derler.

## Nasıl görülür

CLAUDE.md'deki dört satır. `npm test --prefix queen-agent/frontend` iki kırmızı verir — iki yeni test,
çünkü başlıkta bugün `← Thesis research / Write the intro` var. Öteki süitler yeşil. Kırmızı hâliyle
commit edilir.

Adım adım dökümü [test turunun planında](../plans/2026-09-29-queenagent-m347-sohbet-basligi-testler-plan.md).
