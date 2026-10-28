# Madde 85 · Tur 1 (testler) — Plan

**Tasarım:** [2026-08-26-queenagent-m85-cagri-karti-geriye-oturur-testler-design.md](../specs/2026-08-26-queenagent-m85-cagri-karti-geriye-oturur-testler-design.md)
**Bu turda kod yazılmaz.** Yalnız testler; tur kırmızı commit'lenir.
**Test komutları (değişmez, ikisi de) — ayrı ayrı koşulur:**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

**İki renk:** zemin `var(--surface)` → `#f4efe7` · metin `var(--ink)` → `var(--muted)`.
**Tek dosya:** `workspace.css.test.js`.

---

## Sıra

### 1. `workspace.css.test.js` — iki yeni test

84'ün `only the handle offers to be pressed` testinin **altına**, o dokunulmadan:

```js
test("a call card sits back rather than forward", () => {
  // The file card is lit brighter than the page because it is a door and has to come forward. A
  // call opens nothing, so its fill goes under the page's own tone instead of above it -- and the
  // tone is the softest one the palette already holds rather than a new one.
  expect(rule(".tool-call")).toContain("background: #f4efe7");
  expect(rule(".tool-call")).not.toContain("var(--surface)");
  expect(rule(".tool-calls__handle")).toContain("background: #f4efe7");
  expect(rule(".tool-calls__handle")).not.toContain("var(--surface)");
});

test("a call reads in the stopped line's voice", () => {
  // The measure the owner named: the same grey as the word under an answer that was cut short.
  expect(rule(".tool-call__head")).toContain("color: var(--muted)");
  expect(rule(".tool-call__head")).not.toContain("var(--ink)");
  expect(rule(".tool-calls__summary")).toContain("color: var(--muted)");
  expect(rule(".tool-calls__summary")).not.toContain("var(--ink)");
});
```

İkisi de kırmızı: bugün dört kuralın hepsi 84'ün bıraktığı hâlde — zeminler `var(--surface)`,
metinler `var(--ink)`.

**Kırmızı okunur.** `rule()` dört seçiciyi de buluyor *(hepsi bugün var)*, yani düşen şey
`toContain` — beklenen ile bulunan yan yana basılıyor, `TypeError` değil.

## Beklenen kırmızı

| Nerede | Kaç |
|---|---|
| `workspace.css.test.js` | 2 |

Arka uçta değişiklik yok: bugünkü **2 failed, 430 passed** aynen kalır.

Ön yüzde bugün **505 passed**. İki yeni testle toplam **507**, ve **2 failed, 505 passed** beklenir.

## Bilerek yapılmayanlar

- **Kod yazılmaz.** `workspace.css` bu turda açılmıyor.
- **`dist` derlenmez.** Kaynak değişmiyor.
- **`ChatScreen.test.jsx` açılmaz.** Davranış değişmiyor; 84'ün on üç çağrı testi yerinde ve yeşil
  kalmalı.
- **84'ün iskelet testleri değiştirilmez.** Kenarlık, köşe, genişlik ve imleç aynen duruyor — bu
  madde onlara dokunmuyor, yalnız iki renge dokunuyor.
- **`Stopped` testine dokunulmaz.** Ölçünün kendisi o.
