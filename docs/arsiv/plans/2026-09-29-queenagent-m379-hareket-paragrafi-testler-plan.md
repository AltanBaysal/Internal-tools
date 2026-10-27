# Madde 379 — Hareket paragrafı · test turu planı

> **Ajan için:** Bu plan tek oturumda, sırayla uygulanır. Adımlar `- [ ]` ile işaretlenir.

**Amaç:** CODE-STANDARD'ın hareket paragrafının bugünü söylemesini isteyen iki testi yazmak, ve
kaldırılan kuralı adıyla taşıyan dört testi bugünün doğrusuna çevirmek.

**Mimari:** Testler `app.css.test.js`'te — hareketin kilidi orada. CODE-STANDARD.md dosyadan okunur
(`read("../CODE-STANDARD.md")`; vitest `queen-agent/frontend`'te koşar, dosyanın öteki okumaları da
`process.cwd()`'ye göre).

**Teknoloji:** vitest, `node:fs`.

**Spec:** [test turunun spec'i](../specs/2026-09-29-queenagent-m379-hareket-paragrafi-testler-design.md)

## Genel kısıtlar

- Yalnız `queen-agent/frontend/src/shared/app.css.test.js` değişir; CSS ve CODE-STANDARD.md bu turda
  değişmez.
- Hiçbir test susturulmaz (`.skip`, `.todo`).
- Testler CLAUDE.md'deki dört satırla, olduğu gibi ve paralel koşulur.
- Kod, yorum ve test adları İngilizce.

---

### Görev 1: Paragrafı bugüne bağlayan testler, ve kuralı taşıyan testlerin çevrilişi

**Dosyalar:**
- Değişir: `queen-agent/frontend/src/shared/app.css.test.js:55-83`

- [ ] **Adım 1: Kuralı taşıyan dört testi çevir.** 55–83. satırlar şununla değişir:

```js
// app.css holds the two animations every surface shares: the fade and the three dots' blink. What
// arrives fades in; nothing that has been laid out rises or slides into place.
test("app.css holds the fade and the blink", () => {
  expect(APP).toContain("@keyframes fadeIn");
  expect(APP).toContain("@keyframes blink");
  expect(APP).not.toContain("@keyframes riseIn");
  expect(APP).not.toContain("@keyframes slideIn");
});

test("app.css's keyframes change opacity and move nothing", () => {
  // Not sideways, not upwards: an element that has been laid out stays where it was put.
  const frames = APP.slice(APP.indexOf("@keyframes"));
  expect(frames).not.toContain("transform");
});

test("every fade stays inside the band", () => {
  const durations = [...WORKSPACE.matchAll(/animation: ([\w-]+) ([\d.]+)s/g)];
  expect(durations.length).toBeGreaterThan(0);
  for (const [, name, seconds] of durations) {
    // The three dots and the spinner never settle, so they have no band to stay inside.
    if (name === "blink" || name === "msg-spin") continue;
    expect(Number(seconds)).toBeLessThanOrEqual(0.22);
  }
});

test("the rail folds by its width", () => {
  expect(WORKSPACE).toContain("transition: width 220ms ease");
});
```

- [ ] **Adım 2: İki yeni testi ekle**, Adım 1'in bloğunun hemen altına:

```js
// Madde 379: the standard's paragraph on motion says what moves today and forbids nothing. Read
// from the file, so an animation added without a word there fails here instead of leaving the
// paragraph untrue -- the animation itself is never refused.
const STANDARD = read("../CODE-STANDARD.md");

test("the standard names every keyframe the frontend defines", () => {
  const names = [...`${APP}${WORKSPACE}`.matchAll(/@keyframes ([\w-]+)/g)].map(([, name]) => name);
  expect(names.length).toBeGreaterThan(0);
  for (const name of names) expect(STANDARD).toContain(`\`${name}\``);
});

test("the standard forbids no animation, and calls no motion the only one", () => {
  expect(STANDARD).not.toContain("never invents");
  expect(STANDARD).not.toContain("The only motion");
});
```

- [ ] **Adım 3: Dört satırı paralel koş.**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: `npm test --prefix queen-agent/frontend`'te iki kırmızı — "the standard names every
keyframe the frontend defines" (`` `msg-spin` `` yok) ve "the standard forbids no animation, and calls
no motion the only one" (`never invents` var). Çevrilen dört test yeşil. Öteki üç süit koşudan
öncekiyle aynı.

- [ ] **Adım 4: Kırmızı hâliyle commit et** — spec, bu plan ve test dosyası:

```
git add docs/specs/2026-09-29-queenagent-m379-hareket-paragrafi-testler-design.md docs/plans/2026-09-29-queenagent-m379-hareket-paragrafi-testler-plan.md queen-agent/frontend/src/shared/app.css.test.js
git commit -m <mesaj>
```

Mesaj: `test: Madde 379 -- the standard names every keyframe and forbids none, red until the
paragraph tells today` ve son satırı `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
