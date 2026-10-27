# Madde 318 — Havuz ortada, uygulama turunun planı

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*.

**Hedef:** `d8a1190a`'nın kırmızı testleri yeşile dönüyor.

**Spec:** [m318 uygulama turu](../specs/2026-09-24-queen-editor-m318-havuz-ortada-uygulama-design.md)

## Her yere geçerli kurallar

- Yorum **İngilizce**, yalnız bugün doğru olanı söyler; arayüz metni tasarımdan harfi harfine.
- Testlere dokunulmaz. Kaynakla `dist/` aynı commit'te.

---

## Görev 1: `LayerPanel.jsx`

İmza `poolShown`, `onShowPool` alıyor. Sekmenin tıklaması:

```jsx
onClick={() => { setSource(one.id); onShowPool(one.id === FROM_POOL); }}
```

Durumun altında:

```jsx
  // The pool in the middle belongs to this panel's Referanstan tab: when the panel goes -- closed,
  // or another one opened -- the cards come back.
  useEffect(() => () => { if (layer === "video") onShowPool(false); }, []);
```

`Referanslar` bloğu:

```jsx
        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          <Mono size={11} data-label style={LABEL}>Referanslar</Mono>
          {/* One button, one place: it swaps the middle between the pool and the cards. */}
          <button type="button" className="wf-btn wf-btn--sm" style={{ alignSelf: "flex-start" }}
                  onClick={() => onShowPool(!poolShown)}>
            {poolShown ? "Referansları kapat" : "Referansları aç"}
          </button>
        </div>
```

## Görev 2: `SidePanel.jsx`

İmzaya `poolShown`, `onShowPool = () => {}`; `LayerPanel`'e `key={open}`, `poolShown={poolShown}`,
`onShowPool={onShowPool}`, ve yorum: iki katman, iki panel.

## Görev 3: `ProjectScreen.jsx`

`poolOpen` ve sol sütun gidiyor. Yerine:

```jsx
  // Whether the middle shows the reference pool instead of the cards (madde 318). The video panel's
  // Referanstan tab says so, and its one button; the screen only holds the answer.
  const [poolShown, setPoolShown] = useState(false);
```

Orta:

```jsx
        <div data-scroll ref={box} style={{ flex: 1, minWidth: 0, overflowY: "auto" }}>
          {poolShown && <ReferencePanel project={project} />}
          {/* Hidden rather than taken down: the gallery keeps its own selection. */}
          <div hidden={poolShown}>
            <Gallery … />
          </div>
        </div>
```

`SidePanel`'e `poolShown={poolShown} onShowPool={setPoolShown}`.

## Görev 4: `ReferencePanel.jsx`

- `onClose` ve başlık satırı *(`Referanslar` + `×`)* gidiyor.
- `PANEL`:

```jsx
// The pool in the middle, in place of the cards: the design's own room around it.
const PANEL = {
  padding: "24px 32px 48px",
  display: "flex",
  flexDirection: "column",
  gap: 14,
};
```

- Belge yorumu: *"The project's reference pool, in the middle in place of the cards while the video
  panel is on Referanstan (madde 318)."*

## Görev 5: Koşu, dist ve yeşil commit

- [ ] **Adım 1: Dört satırı koş** — dördü de yeşil.
- [ ] **Adım 2: Dist** — `npm run build --prefix queen-editor/frontend`.
- [ ] **Adım 3: Yeşil commit** — `feat(m318): …`.
