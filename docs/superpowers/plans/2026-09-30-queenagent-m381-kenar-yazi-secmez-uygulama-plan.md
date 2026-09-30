# Madde 381 — Panelin kenarını çekmek yazı seçmez · uygulama turu planı

> **Ajan için:** Bu plan tek oturumda, sırayla uygulanır. Adımlar `- [ ]` ile işaretlenir.

**Amaç:** Kenara basış tarayıcının yazı seçmesini başlatmasın; test turunun iki kırmızı testi yeşile
dönsün.

**Mimari:** `Grip`'in `onMouseDown`'ı `event.preventDefault()` çağırır. Aynı `Grip` listede de açık
dosyada da durduğu için tek değişiklik ikisini birden kapsar.

**Teknoloji:** React 18, vitest.

**Spec:** [uygulama turunun spec'i](../specs/2026-09-30-queenagent-m381-kenar-yazi-secmez-uygulama-design.md)

## Genel kısıtlar

- Yalnız `queen-agent/frontend/src/features/workspace/FileRail.jsx` değişir; testler ve CSS değişmez.
- `dist` bu koşuda derlenmez; koşuyu birleştiren oturum derler.
- Testler CLAUDE.md'deki dört satırla, olduğu gibi ve paralel koşulur.
- Kod ve yorum İngilizce; yorum nedeni söyler.

---

### Görev 1: Basış seçimi başlatmaz

**Dosyalar:**
- Değişir: `queen-agent/frontend/src/features/workspace/FileRail.jsx` — `Grip`'in `onMouseDown`'ı.

- [ ] **Adım 1: `onMouseDown`'ı şöyle yaz:**

```jsx
      onMouseDown={(event) => {
        // The browser's own answer to a press-and-drag is to select every text the pointer crosses,
        // and a selection only ever starts on the press -- refused here, none starts for the whole
        // drag, wherever the pointer goes or is let go (Madde 381).
        event.preventDefault();
        // Nothing dragged yet means the stylesheet's width is the one on screen, so that is where
        // this drag starts from.
        drag.current = { x: event.clientX, width: width ?? DEFAULT_RAIL_WIDTH };
        onDrag(true);
      }}
```

- [ ] **Adım 2: Dört satırı paralel koş.**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: dördü de yeşil; queen-agent frontend'inde 819 test.

- [ ] **Adım 3: Commit et** — spec, bu plan ve `FileRail.jsx`:

```
git add docs/superpowers/specs/2026-09-30-queenagent-m381-kenar-yazi-secmez-uygulama-design.md docs/superpowers/plans/2026-09-30-queenagent-m381-kenar-yazi-secmez-uygulama-plan.md queen-agent/frontend/src/features/workspace/FileRail.jsx
git commit -m <mesaj>
```

Mesaj: `feat: Madde 381 -- pulling the rail's edge selects no text on the page` ve son satırı
`Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
