# Madde 359 — Projelerde arama · uygulama turu

**Kaynak:** [test turunun spec'i](2026-09-29-queenagent-m359-projelerde-arama-testler-design.md) ve
kırmızı commit'i `b4ffbd05` — D1–D9 `AllProjectsScreen.test.jsx`'te, C7 ve C8
`workspace.css.test.js`'te. Kararlar orada; burada yalnız nasıl kurulduğu.

**Kullanıcıdan gereken:** hiçbir şey.

## Ne değişir

**`AllProjectsScreen.jsx`** — tek dosyada, yeni dosya yok:

1. **Aramanın durumu** ekranın `useState("")`'i. Adrese yazılmaz, sunucuya gitmez; ekran kapanıp
   açılınca boş başlar (test spec'i, Karar 8).
2. **Eşleşme** dosyanın içinde küçük bir `fold(text)`: `normalize("NFD")`, birleşen işaretlerin
   (`\p{M}`) atılması, `toLowerCase()`. Proje adı `fold(name).includes(fold(query.trim()))` ise
   gösterilir — tasarımın `data.js`'indeki `named`'in aynısı. Ayrı bir modüle çıkmaz: tek kullanıcısı
   bu ekran. Sohbet araması (365) kendi yerinde aynısını isterse o gün paylaşılır.
3. **Kutu** başlık satırının altında `<div className="all-projects__tools">` içinde
   `<input type="text" className="all-projects__search" placeholder="Search projects"
   aria-label="Search projects" autoFocus>`. Çerçevenin parçası: yüklenirken de çizilir. `autoFocus`
   odağı ekranın açıldığı anda verir, liste gelince bir daha vermez (test spec'i, Karar 6).
4. **Gövdenin sırası:** yüklenirken hiçbir şey; hiç proje yoksa `No projects yet.`; arama hiçbirini
   bulmadıysa `No projects match "<kırpılmış arama>".` (aynı `.all-projects__empty`); yoksa
   `Pinned` ve `Recent` bölümleri, bulunanlardan. Bölüm boşsa `Section` onu zaten çizmiyor.
5. **Baştaki yorum** aramayı artık "sonraki maddeler" arasında saymaz.

**`workspace.css`** — `.all-projects__head`'in altına tasarımın `kit.css`'inden iki kural:
`.all-projects__tools` (flex, ortada hizalı, `gap: 16px`, `margin: 0 0 28px`) ve
`.all-projects__search` (`flex: 1`, `min-width: 0`, `var(--line)` çerçeve, `var(--radius-control)`,
`padding: 8px 12px`, `var(--surface)` zemin, yazı ailesi miras, `13.5px`, `var(--ink)`). Odak
çizgisi yazılmaz — `app.css`'in.

## Değişmeyenler

Sunucu, App, sıra (sunucunun), `countOf`, satırlar. Enter / Esc yok (test spec'i, Karar 7).

## Nasıl görülür

Dört satır paralel, dördü de yeşil. `dist` derlenmez — Claude derler.

Adım adım dökümü [uygulama planında](../plans/2026-09-29-queenagent-m359-projelerde-arama-uygulama-plan.md).
