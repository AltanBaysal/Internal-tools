# Madde 13 — Markdown ve balon ölçeği · Uygulama Planı

**Tasarım belgesi:** [2026-08-17-queenagent-m13-markdown-design.md](../specs/2026-08-17-queenagent-m13-markdown-design.md)
**Test komutu (değişmez):** `python -m pytest queenagent -q; npm test --prefix queenagent/frontend`

İki commit: **önce yalnız testler** (kırmızı gider), sonra uygulama. Arka uca dokunulmuyor —
sunucu ham metni göndermeye devam ediyor.

---

## Adım 1 — Testler (kırmızı commit)

**Yeni `shared/markdown.test.js`** — ayrıştırıcı, React'siz:
- her blok türü tanınır: başlık düzeyleri, kod çiti + dil, iki liste türü, tablo, alıntı, çizgi,
  paragraf.
- `#####` başlık sayılmaz, paragraf olur.
- iç içe liste maddenin altına iner.
- kapanmamış çit metnin sonunda kapanır.
- satır içi: kalın, eğik, üstü çizili, kod, bağlantı; iç içe geçme; kod içindeki `**` ham kalır.
- `javascript:` hedefi bağlantı olmaz.
- paragraf içindeki tek satır sonu `break` belirteci olur.

**Yeni `features/workspace/Markdown.test.jsx`** — çizim: `<h1>`, `<strong>`, `<em>`, `<del>`,
`<code>`, `<pre>`, `<ul>/<ol>`, `<table>` ile `<th>`, `<blockquote>`, `<hr>`, `<a href … target>`.

**`ChatScreen.test.jsx`** — cevap biçimli, kullanıcı balonu ham, akan metin biçimli.

**`workspace.css.test.js`** — balon ölçeği (19.5/17/14.5), `.msg__text` artık `pre-wrap` yazmaz,
`.md pre` yazar.

**Ölçülen kırmızı:** 2 dosya hiç yüklenmiyor (`markdown.js` ve `Markdown.jsx` yok) + 6 test.
ChatScreen'in "kullanıcının yazdığı ham kalır" testi **ilk koşuda yeşil geldi** — balon zaten ham
metin çiziyor. Doğrusu da bu: o test yeni bir davranış istemiyor, çizici gelirken balonun ona
kapılmamasını bekliyor.

---

## Adım 2 — Uygulama

1. `shared/markdown.js` — `parseBlocks` + `parseInline`.
2. `features/workspace/Markdown.jsx` — bloklar → React öğeleri.
3. `ChatScreen.jsx` — `.msg__text` içindeki iki yerde (kayıtlı cevap, akan metin) `<Markdown>`.
   Kullanıcı balonuna dokunulmaz.
4. `workspace.css` — `.md` blok stilleri, balon ölçeği, `.msg__text`'ten `white-space` kalkar.

### Kapanış denetimi

- `grep "white-space: pre-wrap"` → yalnız `.msg__bubble` ve `.md pre`.
- `grep dangerouslySetInnerHTML` → boş.

---

## Risk

Ayrıştırıcının kenar durumları. Kapsam kapalı olduğu için en kötü sonuç çizilmemek: tanınmayan
sözdizimi ham metin olarak kalır.
