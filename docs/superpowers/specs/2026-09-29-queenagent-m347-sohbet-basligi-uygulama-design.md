# Madde 347 — Sohbet başlığında yalnız sohbetin adı · uygulama turu

**Kaynak:** [yol haritasının 347'si](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md) (v9-2d);
tasarımın 152'si ve 168'i. Testler [test turunda](2026-09-29-queenagent-m347-sohbet-basligi-testler-design.md)
yazıldı ve kırmızı commit'lendi.

**Kullanıcıdan gereken:** hiçbir şey.

## Ne değişir

**`ChatScreen.jsx`** — başlıkta yalnız `<span className="chat__title">{chat.title}</span>` kalır; `←`
düğmesi ve `.chat__slash` kalkar. Tasarımın `chat/index.html`'i başlığı böyle çiziyor. Ekran projenin
adını başka hiçbir yerde okumadığı için `project` özelliği de kalkar.

**`App.jsx`** — `ChatScreen`'e `project={project}` verilmez: artık okuyan yok. Projenin adını `Bar`
çiziyor ve ona verilen `project` yerinde kalır.

**`workspace.css`** — `.chat__slash` kuralı kalkar, çünkü onu çizen yok. `.back.back--inline` kalır:
açık dosyanın `←`'i (`FilePanel.jsx`) hâlâ taşıyor. `.reader__bar > .back`'in yorumu, sohbet başlığının
da `back--inline` taşıdığını söylüyor; bu artık doğru değil, ve yorum bugünü söyleyecek biçimde kısalır.

## Neye dokunulmaz

- `onBack` ve sohbet yüklenirken duran tek başına `← back`: bu maddenin değil, v9-2l'nin *(355)*.
- `ChatScreen.test.jsx`'teki öteki testlerin `project={PROJECT}`'i: ekran onu artık okumuyor ve
  zararsız; aynı dosyaya bu dalgada 348 ve 349 da yazıyor, ve yüz satırlık bir temizlik onların
  birleştirmesini boşuna zorlar. Yeni iki test onu bilerek veriyor: verilse de adın çizilmediğini
  tutuyorlar.
- `.chat__header`'ın ölçüleri: tasarımınkiyle aynı (`padding: 16px 32px`, alt çizgi).
- CODE-STANDARD'ın tabloları: dosya eklenmiyor, silinmiyor.

## Nasıl görülür

CLAUDE.md'deki dört satır yeşil: queen-agent'ın ön ucu 695 test. Tarayıcıda bir sohbet açılınca
başlıkta yalnız sohbetin adı var; projenin adı üst çubuğun ortasında.

Adım adım dökümü [uygulama turunun planında](../plans/2026-09-29-queenagent-m347-sohbet-basligi-uygulama-plan.md).
