# Madde 381 — Panelin kenarını çekmek yazı seçmez · test turu planı

> **Ajan için:** Bu plan tek oturumda, sırayla uygulanır. Adımlar `- [ ]` ile işaretlenir.

**Amaç:** Kenara basışın tarayıcının varsayılanını — yazı seçmeye başlamayı — durdurduğunu isteyen iki
testi yazmak: listenin kenarı ve açık dosyanın kenarı.

**Mimari:** Testler `FileRail.test.jsx`'te, Madde 356'nın bloğunun altında. `fireEvent.mouseDown`,
`dispatchEvent`'in dönüşünü verir: varsayılanı durdurulan olayda `false`. Testing Library'nin
`mouseDown`'ı zaten `cancelable: true` olarak gönderilir.

**Teknoloji:** vitest, jsdom, Testing Library.

**Spec:** [test turunun spec'i](../specs/2026-09-30-queenagent-m381-kenar-yazi-secmez-testler-design.md)

## Genel kısıtlar

- Yalnız `queen-agent/frontend/src/features/workspace/FileRail.test.jsx` değişir; `FileRail.jsx` bu
  turda değişmez.
- Hiçbir test susturulmaz (`.skip`, `.todo`).
- Testler CLAUDE.md'deki dört satırla, olduğu gibi ve paralel koşulur.
- Kod, yorum ve test adları İngilizce.

---

### Görev 1: Kenara basış yazı seçmeye başlamaz

**Dosyalar:**
- Değişir: `queen-agent/frontend/src/features/workspace/FileRail.test.jsx` — "while the reader's edge
  is being pulled the rail says so" testinin hemen altı.

- [ ] **Adım 1: İki testi ekle:**

```jsx
// Madde 381: the browser's own answer to a press-and-drag is to select text, and the pointer leaves
// the 6px grip on the first frame -- so every message, card and composer it crossed turned blue. A
// selection only ever starts on the press, so a press that refuses it keeps the whole drag clean,
// wherever the pointer goes and wherever it is let go.
test("pressing the list's grip starts no text selection", () => {
  render(<FileRail files={FILES} width={320} onResize={vi.fn()} />);
  expect(fireEvent.mouseDown(screen.getByRole("separator"), { clientX: 500 })).toBe(false);
});

test("pressing the reader's grip starts no text selection either", () => {
  render(<FileRail files={FILES} width={320} onResize={vi.fn()} reading={READING} />);
  expect(fireEvent.mouseDown(screen.getByRole("separator"), { clientX: 500 })).toBe(false);
});
```

- [ ] **Adım 2: Dört satırı paralel koş.**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: `npm test --prefix queen-agent/frontend`'te iki kırmızı — ikisi de `expected true to be
false`. Öteki üç süit koşudan öncekiyle aynı.

- [ ] **Adım 3: Kırmızı hâliyle commit et** — spec, bu plan ve test dosyası:

```
git add docs/superpowers/specs/2026-09-30-queenagent-m381-kenar-yazi-secmez-testler-design.md docs/superpowers/plans/2026-09-30-queenagent-m381-kenar-yazi-secmez-testler-plan.md queen-agent/frontend/src/features/workspace/FileRail.test.jsx
git commit -m <mesaj>
```

Mesaj: `test(queen-agent): Madde 381 red -- pressing the rail's grip starts no text selection` ve son
satırı `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
