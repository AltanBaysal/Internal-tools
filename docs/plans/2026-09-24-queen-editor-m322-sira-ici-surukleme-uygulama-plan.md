# Madde 322 — Sıranın içinde sürükleme, uygulama turunun planı

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*. Takımı ve commit'i
> orkestratör koşuyor *(yol haritası, Kol A)*.

**Hedef:** `5ec2322d`'nin üç kırmızı testi yeşile dönüyor; `Ekle` kartının bekçisi yeşil kalıyor.

**Spec:** [m322 uygulama turu](../specs/2026-09-24-queen-editor-m322-sira-ici-surukleme-uygulama-design.md)

## Her yere geçerli kurallar

- Yorum **İngilizce**, yalnız bugün doğru olanı söylüyor. Testlere dokunulmaz.
- **Dist derlenmez** — Kol A'nın kuralı; birleşme commit'i derler.
- Kol B'nin `ReferencePanel.jsx` satırlarına *(bileşen docstring'i, imza, havuzun `useState`'i)*
  dokunulmaz.
- Tek dosya: `queen-editor/frontend/src/features/photo_generation/ReferencePanel.jsx`.

---

## Görev 1: Görünüşün iki ölçüsü

`ADD`'in ardına:

```jsx
// The gallery's own lift for the tile in flight (Gallery.jsx, DRAGGED -- the design's .dragged).
const DRAGGED = { transform: "rotate(-3deg) scale(1.04) translate(14px, -10px)",
                  filter: "drop-shadow(0 12px 24px rgba(0,0,0,.55))", zIndex: 5,
                  position: "relative" };
// Where the tile in flight would land: the tile under the pointer gives its place to the gallery's
// dashed slot, drawn over its face at the face's own size (the design's .rv-tile.is-over::before).
const SLOT = { position: "absolute", top: 0, left: 0, width: 144, height: 108,
               border: "2px dashed var(--accent)", borderRadius: "var(--r-sm)",
               background: "var(--bg-3)", boxSizing: "border-box" };
```

## Görev 2: `Tile`

İmza, kök `div` ve alttaki iki satır; yüzler, numara ve × olduğu gibi.

```jsx
function Tile({ project, row, lifted, open, onRemove, onDragStart, onDragOver, onDrop,
                onDragEnd }) {
  const url = referenceUrl(project, row.name);
  // Under the slot the words keep their place unseen, so the row keeps its height.
  const unseen = open ? { visibility: "hidden" } : null;
  return (
    // Draggable from the start, not after a hold: the browser decides at mousedown whether a press
    // may become a drag, so a tile armed later is never a drag source at all (the gallery's own
    // lesson).
    <div style={lifted ? { ...TILE, ...DRAGGED } : TILE} data-reference={row.name} draggable
         onDragStart={onDragStart}
         onDragOver={onDragOver}
         onDrop={onDrop}
         onDragEnd={onDragEnd}>
```

```jsx
      <Note size={11} style={{ color: "var(--ink-3)", overflow: "hidden",
                               textOverflow: "ellipsis", whiteSpace: "nowrap", ...unseen }}>
        {row.name}
      </Note>
      {row.seconds != null && (
        <Note size={11} style={{ color: "var(--ink-2)", ...unseen }}>{ran(row.seconds)}</Note>
      )}
      {/* Last, so it stands over the face, the number and the ×. */}
      {open && <div style={SLOT} />}
    </div>
```

## Görev 3: Bileşenin sürüklemesi

`drag` ref'i ve yorumu, altına iki state:

```jsx
  // What is being dragged. A ref and not state: a drop has to read what the drag start wrote
  // however the browser batched the two.
  const drag = useRef(null);
  // What the drag draws, the gallery's way: the tile in flight, and the tile whose place opened
  // under the pointer. Names, because a row is keyed by them.
  const [lifted, setLifted] = useState(null);
  const [over, setOver] = useState(null);
```

`handlePick`'ten sonra, `handleDrop`'tan önce:

```jsx
  function handleDragStart(kind, name) {
    drag.current = { kind, name };
    setLifted(name);
  }

  /** Only a tile of the dragged one's own row opens a place (madde 322). Anywhere else the default
   * stands, so the browser shows no drop and never fires one -- another row, and the Ekle card,
   * which listens to no drag at all. */
  function handleDragOver(kind, name, event) {
    if (drag.current?.kind !== kind) return;
    event.preventDefault();
    setOver(name);
  }

  /** Dropped or let go, the drag is over: nothing is lifted and no place is open. */
  function endDrag() {
    drag.current = null;
    setLifted(null);
    setOver(null);
  }
```

`handleDrop`'un ilk satırları:

```jsx
    const dragged = drag.current;
    endDrag();
    if (!dragged || dragged.kind !== kind) return;
```

Sıranın kutuları:

```jsx
              {rows.map((row, index) => (
                <Tile key={row.name} project={project} row={row} onRemove={handleRemove}
                      lifted={lifted === row.name}
                      // The tile in flight opens nothing over itself: that place is its own.
                      open={over === row.name && lifted !== row.name}
                      onDragStart={() => handleDragStart(kind, row.name)}
                      onDragOver={(event) => handleDragOver(kind, row.name, event)}
                      onDrop={() => handleDrop(kind, index)}
                      onDragEnd={endDrag} />
              ))}
```

## Görev 4: Koşu ve yeşil commit *(orkestratör)*

- [ ] Dört satır yeşil. - [ ] `feat(m322): …` — spec, plan ve kod tek commit; dist yok.
