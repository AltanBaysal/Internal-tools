# Madde 343 — Çemberin sözü, ve dolmanın önceden duyurusu · uygulama turu

**Kaynak:** [yol haritasının 343'ü (v9-2i)](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md);
[test turunun spec'i](2026-09-29-queenagent-m343-cember-sozu-testler-design.md) — neyin kanıtlandığı
ve dörtte beşin neden ön uçta durduğu orada. Kırmızı testler `c715bbda`'da.

**Kullanıcıdan gereken:** hiçbir şey.

## Ne değişir

**`queen-agent/frontend/src/features/workspace/ContextGauge.jsx`** — iki sayıyı aynı yerden okur,
ama cümlesi ve yanındaki yazı değişir:

- **Yüzde tamsayılarla hesaplanır:** `Math.floor(sent * 100 / ceiling)`, sonra en az 1, en çok 100.
  `sent / ceiling * 100` değil: `0.82 * 100` gibi kayan noktalı bir çarpım 81.999…'a düşüp aşağı
  yuvarlanınca 81 derdi. `sent` ve `ceiling` token sayısı, yani tamsayı; `sent * 100 / ceiling`'in
  tam bölündüğü yerde sonuç tam.
- **Cümle:** yüzde 100'se `This chat is full`, değilse `This chat is N% full`; çemberin `title`'ı ve
  `aria-label`'ı, bugünkü gibi aynı değişken.
- **Yanındaki yazı:** yüzde 80 ile 99 arasındaysa çemberin kardeşi bir
  `<span className="context-gauge__words" aria-hidden="true">N% full</span>`. Bileşen bir fragment
  döner; ikisini `Composer.jsx`'in `.composer__gauge`'i sarar, ve Composer değişmez.
- **Eşik bir sabit, `NEARLY_FULL = 80`**, yüzde olarak — yüzdeyle karşılaştırıldığı için. Tavanın payı,
  kopyası değil; tavan sunucudan sayıyla birlikte geliyor. Yorumu bunu ve eşiğin yalnız neyin
  gösterildiğine karar verdiğini söyler.
- **`--filled` değişmez:** `Math.min(sent / ceiling, 1)`, çizim için; yazı için ayrı yüzde. Çember
  tam payla dolar, yazı aşağı yuvarlanmış sayıyı söyler — tasarımdaki gibi.

**`queen-agent/frontend/src/features/workspace/workspace.css`** — yalnız 343'ün kuralları:

- `.composer__gauge`'e `gap: 6px`.
- `.context-gauge`'in hemen altına yeni kural `.context-gauge__words`: `font-family: var(--font-mono)`,
  `font-size: 11.5px`, `color: #6b6259`, `white-space: nowrap` — tasarımın `kit.css`'indeki kural;
  `nowrap`, `80% full` dar bir ayakta iki satıra bölünmesin diye.

## Değişmeyenler

- **Sunucu:** `context.sent` ve `context.ceiling` aynı; neyin ölçüldüğü 337'nin.
- **ChatScreen.jsx ve Composer.jsx:** çember aynı iki sayıyla beslenir, aynı yuvaya girer.
- **CODE-STANDARD'ın tabloları:** yeni dosya yok.
- **`dist`:** yöneten birleştirirken derler.

## Nasıl görülür

CLAUDE.md'deki dört satır, paralel: `npm test --prefix queen-agent/frontend` yeşile döner, 659 test;
queen-agent'ın arka ucu 933 yeşil; queen-editor 377'nin bilinen iki kırmızısıyla ve ön ucu yeşil.

Tarayıcıda: 40.000'i geçmiş bir sohbette yazma kutusunun sol altında çemberin yanında `N% full`;
çemberin üstüne gelince `This chat is N% full`.

Adım adım dökümü [uygulama turunun planında](../plans/2026-09-29-queenagent-m343-cember-sozu-uygulama-plan.md).
