# Madde 85 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-26-queenagent-m85-cagri-karti-geriye-oturur-uygulama-design.md](../specs/2026-08-26-queenagent-m85-cagri-karti-geriye-oturur-uygulama-design.md)
**Testler:** commit `77f706f` — **2 kırmızı**, ikisi de stil kilidinde.
**Test komutları (değişmez, ikisi de) — ayrı ayrı koşulur:**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

**Tek dosya:** `workspace.css`. `ChatScreen.jsx` açılmıyor — davranış değişmiyor.
**`dist` bu turda derlenir ve aynı commit'e girer.**

---

## Sıra

### 1. `workspace.css` — `.tool-calls`'un üstündeki yoruma bir cümle

Bugünkü yorum *"bir kayıt silik olmak zorunda değil"* diyor ve doğru kalıyor. Eklenen şey ışığın
neden dosya kartından ayrıştığı:

```css
/* What the turn did before it spoke, behind one door. Madde 78's rule holds and is written into the
   markup: the handle is a button because it opens something, a call is not because a step already
   taken opens nothing, and neither carries the accent. What 84 dropped is the unspoken half of that
   rule -- that a record has to be faint. It does not: it can sit in a bordered box and still be
   nothing to press.
   The light is where these part company with the file card. That one is a door and is lit brighter
   than the page so it comes forward; these open nothing, so their fill goes under the page's own
   tone and their words read at the stopped line's weight. */
```

### 2. `workspace.css` — tutamak

`.tool-calls__handle` içinde tek satır:

```css
  background: #f4efe7;
```

`var(--surface)` yerine. Kuralın kalanı — `display`, `align-items`, `gap`, `width`, `max-width`,
`border`, `border-radius`, `padding`, `font-family`, `text-align`, `cursor` — **değişmiyor**.

`.tool-calls__handle:hover` da değişmiyor: `border-color: #d9d0c3`.

### 3. `workspace.css` — tutamağın metni

`.tool-calls__summary` içinde tek satır:

```css
  color: var(--muted);
```

`var(--ink)` yerine. `flex`, `min-width`, `font-family`, `font-size`, `overflow`, `text-overflow`,
`white-space` **değişmiyor**.

`.tool-calls__chevron` zaten `var(--muted)` — açılmıyor.

### 4. `workspace.css` — çağrı kartı

`.tool-call` içinde tek satır:

```css
  background: #f4efe7;
```

`var(--surface)` yerine. Kuralın kalanı — `max-width: 340px`, `border: 1px solid var(--line)`,
`border-radius: 12px`, `padding: 11px 14px`, `animation: fadeIn 0.2s ease both` ve gerisi —
**değişmiyor**. 84'ün `a call is drawn on the card the repo already has` testi bunları soruyor ve
yeşil kalmalı.

**İmleç eklenmiyor.** 84'ün kilidi `rule(".tool-call")` içinde `cursor` **aramıyor**.

### 5. `workspace.css` — kartın başlığı

`.tool-call__head` içinde tek satır:

```css
  color: var(--muted);
```

`var(--ink)` yerine. `flex: 1`, `min-width: 0`, `overflow`, `text-overflow`, `white-space`
**değişmiyor** — başlığı sonuçtan ayıran şey artık renk değil, yer, ve o yeri bu dört satır
kuruyor.

`.tool-call__outcome` zaten `var(--muted)` — açılmıyor.

### 6. `dist` derlenir

```
npm run build --prefix queen-agent/frontend
```

Kaynakla **aynı commit'e** giriyor; `test_dist_is_committed.py` bunu zorluyor.

## Beklenen yeşil

Arka uçta **2 failed, 430 passed** — ikisi defterin dalı, bu maddeyle ilgisiz.
Ön yüzde **507 passed**, kırmızı yok.

## Bilerek yapılmayanlar

- **`ChatScreen.jsx` açılmaz.** Tek satır davranış değişmiyor.
- **84'ün iskeleti değiştirilmez.** Kenarlık, köşe, genişlik, iç boşluk, animasyon, imleç, hover.
- **`--surface` için bir değişken açılmaz.** Bu deponun eşiği bir kullanım değil; `#ede6dc`,
  `#f0e7de` ve `#d9d0c3` de ham yazılı.
- **`.file-card--selected` değiştirilmez.** Aynı tonu paylaşıyorlar ama bağımsız kararlar: biri
  değişirse öteki değişmek zorunda değil.
- **Dosya kartı karartılmaz.** O bir kapı; parlak kalıyor, ve ayrışan çağrı kartı.
- **Testlere dokunulmaz.** Bir test kod yazılırken düzeltiliyorsa kırmızı yanlış yerdeydi; o zaman
  durulur ve söylenir.
