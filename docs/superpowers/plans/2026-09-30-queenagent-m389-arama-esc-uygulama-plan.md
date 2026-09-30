# Madde 389 — Sohbet aramasında Esc yalnız aramayı boşaltır · uygulama planı

> **Ajan için:** Bu plan tek oturumda, sırayla uygulanır. Adımlar `- [ ]` ile işaretlenir.

**Amaç:** `Search chats`'te yazı varken Esc aramayı boşaltsın ve orada dursun; açık dosya açık kalsın.

**Mimari:** Kutunun `onKeyDown`'ı, Esc'te yazı varsa `event.stopPropagation()` çağırır. React 18
olayları kök düğümde dinlediği için yerel olay `window`'a ulaşmaz ve `App.jsx`'in dinleyicisi basışı
görmez. Kutu boşsa olaya dokunulmaz.

**Teknoloji:** React 18, vitest, jsdom.

**Spec:** [uygulama turunun spec'i](../specs/2026-09-30-queenagent-m389-arama-esc-uygulama-design.md)

## Genel kısıtlar

- Yalnız `queen-agent/frontend/src/features/workspace/Sidebar.jsx` değişir. `dist` derlenmez.
- Hiçbir test susturulmaz; testler değişmez.
- Testler CLAUDE.md'deki dört satırla, olduğu gibi ve paralel koşulur.
- Kod ve yorum İngilizce; yorum nedenini söyler.

---

### Görev 1: Esc kutuda durur

**Dosyalar:**
- Değişir: `queen-agent/frontend/src/features/workspace/Sidebar.jsx` — `onKeyDown` ve üstündeki yorum.

- [ ] **Adım 1: `onKeyDown`'ı değiştir.** Bugün:

```jsx
  // The keys are the design's: Enter opens the first match -- the server lists the most recent
  // first -- and hands its reply box the focus; Escape empties the box. Escape is the field's own,
  // as a message being edited has it.
  const onKeyDown = (event) => {
    if (event.key === "Enter") {
      if (shown.length) onOpenChat(shown[0].id, { focusReply: true });
    } else if (event.key === "Escape") setQuery("");
  };
```

Olacak:

```jsx
  // The keys are the design's: Enter opens the first match -- the server lists the most recent
  // first -- and hands its reply box the focus; Escape empties the box. Emptying it is that press's
  // whole work, so it goes no further: App's listener on the window would also shut the open file
  // (Madde 389). An empty box has nothing to empty, and Escape goes on to what App closes next.
  const onKeyDown = (event) => {
    if (event.key === "Enter") {
      if (shown.length) onOpenChat(shown[0].id, { focusReply: true });
    } else if (event.key === "Escape" && query) {
      event.stopPropagation();
      setQuery("");
    }
  };
```

- [ ] **Adım 2: Dört satırı paralel koş.**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: dördü de yeşil; `npm test --prefix queen-agent/frontend`'te test turunun kırmızısı ("Escape
in Search chats empties the search and leaves the open file open") geçer.

- [ ] **Adım 3: Commit et** — spec, bu plan ve `Sidebar.jsx`:

```
git add docs/superpowers/specs/2026-09-30-queenagent-m389-arama-esc-uygulama-design.md docs/superpowers/plans/2026-09-30-queenagent-m389-arama-esc-uygulama-plan.md queen-agent/frontend/src/features/workspace/Sidebar.jsx
git commit -m <mesaj>
```

Mesaj: `feat: Madde 389 -- Escape in Search chats empties the search and stops there` ve son satırı
`Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
