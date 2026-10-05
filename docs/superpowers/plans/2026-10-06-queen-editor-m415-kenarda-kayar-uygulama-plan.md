# Madde 415 — Kart sürüklenirken galeri kenarda kayar, uygulama turunun planı

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*. Commit kendi dalında;
> `dist` kurulmaz — birleştirmede koşu kurar.

**Hedef:** Galerinin kutusu, üstünde sürüklenen kart kenarına yaklaşınca o yöne kayar; havuz açıkken
kaymaz. Test turunun beş testi yeşil.

**Yaklaşım:** `ProjectScreen`'in `data-scroll` kutusuna bir `onDragOver`: imlecin yüksekliği kutunun
kenarlarından 80 px'ten yakınsa `scrollTop` 20 px o yöne. Durum ve zamanlayıcı yok.

**Araçlar:** React 18, vitest + jsdom.

**Spec:** [m415 uygulama turu](../specs/2026-10-06-queen-editor-m415-kenarda-kayar-uygulama-design.md)
· [m415 test turu](../specs/2026-10-06-queen-editor-m415-kenarda-kayar-testler-design.md)

## Her yere geçerli kurallar

- Kod ve yorumlar İngilizce; yorum nedenini söyler.
- Testler dört satırla koşulur, paralel, yazıldığı gibi; testlere dokunulmaz.
- Kenar `EDGE = 80`, adım `STEP = 20`.

---

## Görev 1: `ProjectScreen.jsx` — kutu kenarda kayar

**Dosya:** Değiştir: `queen-editor/frontend/src/features/photo_generation/ProjectScreen.jsx`
**Test:** `ProjectScreen.test.jsx` — *the gallery scrolls while a card is held at its edge (madde 415)*,
test turunda yazıldı.

- [ ] **Adım 1: `HINT`'in arkasına, modülün düzeyinde.**

```jsx
// A card dragged near an edge of the gallery's box carries the box with it, a step at a time
// (madde 415). The browser repeats dragover while a drag is held still, so the box goes on moving
// for as long as the card stays at the edge -- and nothing is left running once the drag ends.
// Measured from the box's own edges on screen: the header's foot and the window's.
const EDGE = 80;
const STEP = 20;

function scrollAtEdge(event) {
  const box = event.currentTarget;
  const { top, bottom } = box.getBoundingClientRect();
  if (event.clientY < top + EDGE) box.scrollTop -= STEP;
  else if (event.clientY > bottom - EDGE) box.scrollTop += STEP;
}
```

- [ ] **Adım 2: `data-scroll` kutusu dinler** — havuz açıkken değil:

```jsx
        {/* The artboard can clip its gallery because it is a fixed-height frame; a real page
            has to scroll, otherwise most of a 48-photo run is unreachable. Over the cards only:
            the pool's rows were left as they are (madde 415). */}
        <div data-scroll ref={box} onDragOver={poolShown ? undefined : scrollAtEdge}
             style={{ flex: 1, minWidth: 0, overflowY: "auto" }}>
```

## Görev 2: Koşu — yeşil, commit

- [ ] **Adım 1: Dört satırı koş**, paralel, yazıldığı gibi:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: dört satır yeşil; `queen-editor` vitest'inde test turunun beş testi yeşil.

- [ ] **Adım 2: Commit** — kod, uygulama spec'i ve bu plan:

```powershell
git add docs/superpowers/specs/2026-10-06-queen-editor-m415-kenarda-kayar-uygulama-design.md docs/superpowers/plans/2026-10-06-queen-editor-m415-kenarda-kayar-uygulama-plan.md queen-editor/frontend/src/features/photo_generation/ProjectScreen.jsx
git commit -m @'
feat(queen-editor): 415 -- the gallery scrolls while a card is held at its edge

The gallery's box weighs every dragover against its own edges: within 80 px of the bottom it moves
down 20 px, within 80 px of the top up. The browser repeats dragover while a drag is held still,
so the box keeps moving while the card stays there and stops with the drag -- no timer, nothing
left running. Not while the reference pool is open: its rows stay as they are.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
