# Madde 379 — Hareket paragrafı · uygulama turu planı

> **Ajan için:** Bu plan tek oturumda, sırayla uygulanır. Adımlar `- [ ]` ile işaretlenir.

**Amaç:** CODE-STANDARD'ın hareket paragrafını bugünü söyler ve yasak koymaz hâle getirmek; kaldırılan
kuralı ya da eski bir kullanımı söyleyen üç CSS yorumunu düzeltmek.

**Mimari:** Yalnız metin: bir Markdown paragrafı ve üç CSS yorumu. Kod davranışı değişmez.

**Teknoloji:** Markdown, CSS yorumları.

**Spec:** [uygulama turunun spec'i](../specs/2026-09-29-queenagent-m379-hareket-paragrafi-uygulama-design.md)

## Genel kısıtlar

- CODE-STANDARD.md'de yalnız `shared/app.css` ile başlayan paragraf değişir; `trash/` satırına
  (353'ün) dokunulmaz.
- CSS'te yalnız yorumlar değişir; hiçbir kural, değer ya da seçici değişmez.
- `dist` derlenmez.
- Testler CLAUDE.md'deki dört satırla, olduğu gibi ve paralel koşulur.

---

### Görev 1: Paragraf ve üç yorum

**Dosyalar:**
- Değişir: `queen-agent/CODE-STANDARD.md:106-109`
- Değişir: `queen-agent/frontend/src/shared/app.css:77-78`
- Değişir: `queen-agent/frontend/src/features/workspace/workspace.css:821-822` ve `:893`
- Test: `queen-agent/frontend/src/shared/app.css.test.js` (test turunda yazıldı, değişmez)

- [ ] **Adım 1: Paragrafı değiştir.** `queen-agent/CODE-STANDARD.md` 106–109:

```markdown
`shared/app.css` owns the colour variables, the radii, the focus ring and the two keyframes every
surface shares: `fadeIn`, an opacity fade, and `blink`, which pulses the three dots and the loading
skeleton. A component never writes its own focus outline. `features/workspace/workspace.css` holds
`msg-spin`, the spinner's turn — on the live row, the loading file list and a chat that is opening —
and the transitions: the sidebar and the rail fold by their width, and a message's edit pencil fades
in. The accent `--accent` marks the primary action and nothing else.
```

- [ ] **Adım 2: `app.css`'in keyframe yorumunu değiştir** (77–78):

```css
/* Shared by every surface: an opacity fade, and the pulse of the three dots and the loading
   skeleton. Neither moves anything -- an element that has been laid out stays where it was put. */
```

- [ ] **Adım 3: `.rail`'in yorumundan yanlış cümleyi sil** (`workspace.css` 821–822):

```css
/* Always open rather than a toggle: what already exists stays in view while the user asks for
   more. */
```

- [ ] **Adım 4: `.rail__head--still`'in yorumunu değiştir** (`workspace.css` 893):

```css
/* Folded because the shell has no room for both (FileRail's `foldedByWidth`): the strip has nowhere
   to open into, so the heading is a label rather than a button. */
```

- [ ] **Adım 5: Dört satırı paralel koş.**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: dördü de yeşil; test turunun iki kırmızısı ("the standard names every keyframe the
frontend defines", "the standard forbids no animation, and calls no motion the only one") geçer.

- [ ] **Adım 6: Commit et** — spec, bu plan, CODE-STANDARD.md, `app.css`, `workspace.css`.

Mesaj: `docs: Madde 379 -- the motion paragraph tells today and forbids nothing, and the still
heading says who uses it` ve son satırı `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
