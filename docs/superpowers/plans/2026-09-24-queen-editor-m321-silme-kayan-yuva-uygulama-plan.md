# Madde 321 — × hemen siliyor, uygulama turunun planı

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*. Takımı ve commit'i
> orkestratör koşuyor *(yol haritası, Kol A)*.

**Hedef:** `f311de83`'ün kırmızı testleri yeşile dönüyor.

**Spec:** [m321 uygulama turu](../specs/2026-09-24-queen-editor-m321-silme-kayan-yuva-uygulama-design.md)

## Her yere geçerli kurallar

- Yorum **İngilizce**, yalnız bugün doğru olanı söylüyor. Testlere dokunulmaz.
- **Dist derlenmez** — Kol A'nın kuralı; birleşme commit'i derler.
- Kol B'nin `ReferencePanel.jsx` satırlarına *(bileşen docstring'i, imza, havuzun `useState`'i)*
  dokunulmaz; `queue_references.py`'da boş havuz cümlesine dokunulmaz.

---

## Görev 1: Havuzun kuralı — `references.py`

`placed`'ın gövdesi ve docstring'i:

```python
def placed(order, rows):
    """The pool with each reference's slot on it -- its place inside its own kind, counting from 1.

    `order` is {kind: [name, …]}, the sequence the user dragged. Only names whose file is in the pool
    are counted, so the slots are dense from 1: a name the order still holds after its file went --
    one deleted by hand in Drive -- stands in no slot, and the ones after it move up (madde 321).
    That is the numbering H3 reads, since it packs the references tight and numbers them by order:
    a prompt's <Picture 2> is the second picture that is really there.

    A file the order has never heard of waits at the end, among those by name: that is a fresh
    upload, and it is also what a pool with no stored order at all reads as.
    """
    out = []
    for kind in LIMITS:
        held = {row["name"]: row for row in rows if row["kind"] == kind}
        sequence = [name for name in order.get(kind, []) if name in held]
        unheard = sorted(name for name in held if name not in sequence)
        for slot, name in enumerate(sequence + unheard, start=1):
            out.append({**held[name], "slot": slot})
    return out
```

`gaps` bütünüyle siliniyor.

## Görev 2: Kullanım durumları

`remove_reference.py` — modül docstring'i ve sıranın yazılması:

```python
"""Take one reference out of the project's pool. Returns the pool as it now stands.

The name leaves the order with its file, so the ones after it move up and their slot numbers change
(madde 321) -- which is what a prompt's <Picture N> means from then on, because H3 packs the
references tight and numbers them by order. A name left in the order would not show as a hole (the
pool counts only what is there), but a file uploaded under it later would slip back into its old
place rather than join the end of its row.

A name the pool does not have is not an error: another tab can get there first, and deleting twice
has to end where deleting once ends.
"""
```

```python
    pool.delete(project, name)
    orders.write(project, {kind: [one for one in names if one != name]
                           for kind, names in orders.read(project).items()})
    return list_references(store, pool, orders, project)
```

`list_references.py` — modül docstring'inin son paragrafı:

```python
Every row also says which slot it stands in: its place in its own kind's row, counting from 1 with
no hole (madde 300, 321).
```

`save_reference_order.py` — modül docstring'inin ikinci paragrafı:

```python
The sequence is filtered against what the pool really holds before it is stored, the way the
gallery's own order is (save_order): the server writes only names it can see itself, so a stale tab
cannot leave ghosts in the file. A ghost would not show -- the pool counts only what is there -- but
a file uploaded under its name later would slip into its old place rather than join the end of its
row (madde 321).
```

Bugünkü ikinci ve üçüncü paragrafın yerine; `That filter is also how a gap closes …` gidiyor.

`queue_references.py` — modül docstring'inin ilk paragrafı:

```python
Two things stop a run before it starts (madde 302), and the app says which: the engine that can read
references is not installed, or the pool is empty. Both are the app's to count -- H3 complains into
a Colab log the user never opens, and about an empty pool it would not complain at all.
```

Boş havuz reddinin hemen altındaki `open_kinds = references.gaps(held)` bloğu *(yorum ve
`Havuzda boş yuva var` reddiyle)* siliniyor.

## Görev 3: Veri ve kapı

`reference_order_store.py` — modül docstring'inin ilk paragrafı:

```python
A document of its own beside the folder, because it answers what the folder cannot: which slot each
reference stands in (madde 300). The folder says what exists; this says in what order. A name can
outlive its file here -- one deleted by hand in Drive -- and it then stands in no slot (madde 321).
```

`reference_routes.py`:

```python
            # Four refusals, one answer: the run cannot start, and the sentence is the difference.
```

## Görev 4: Ekran

`api.js`:

```js
// The order a drag made, per kind. The whole row goes down because a slot is a place in a sequence
// (madde 300).
```

`ReferencePanel.jsx`:

- `ConfirmModal` importu, `HOLE` ve yorumu, `slotted` ve docstring'i siliniyor. `ADD` ölçülerini
  kendi üstüne alıyor:

```jsx
// The card after a row's last reference is where a file goes in: dashed, because nothing is
// there yet.
const ADD = { width: 144, height: 108, border: "1px dashed var(--border)",
              background: "var(--bg-2)", borderRadius: "var(--r-sm)", boxSizing: "border-box",
              display: "flex", alignItems: "center", justifyContent: "center", gap: 6,
              fontSize: 12, color: "var(--ink-3)" };
```

- `asking` ve `busy` state'leri siliniyor.
- `handleDrop`:

```jsx
  /** Where the drag ends: the row is rebuilt as a sequence, and the whole of it goes down.
   *
   * The slots are not sent -- a place in the list IS the slot.
   */
  async function handleDrop(kind, index) {
    const dragged = drag.current;
    drag.current = null;
    if (!dragged || dragged.kind !== kind) return;
    const names = pool.references.filter((row) => row.kind === kind).map((row) => row.name);
    const from = names.indexOf(dragged.name);
    const placed = names.filter((name) => name !== dragged.name);
    placed.splice(index, 0, dragged.name);
    if (from === -1 || placed.join() === names.join()) return;
```

- `handleRemove`:

```jsx
  /** × is the whole delete. No window asks first: the user's call in madde 321, since a reference
   * is a copy they put back with one Ekle. What comes back is the pool with the ones after it
   * moved up. */
  async function handleRemove(name) {
    try {
      setPool(await removeReference(project, name));
      // The next pick or delete clears a refusal (madde 320).
      setError(null);
    } catch (err) {
      setError(err.message);
    }
  }
```

- Sıra satırları, delik dalı olmadan:

```jsx
            <div style={TILES}>
              {rows.map((row, index) => (
                <Tile key={row.name} project={project} row={row} onRemove={handleRemove}
                      onDragStart={() => { drag.current = { kind, name: row.name }; }}
                      onDrop={() => handleDrop(kind, index)} />
              ))}
```

- `ConfirmModal` bloğu siliniyor.

## Görev 5: Koşu ve yeşil commit *(orkestratör)*

- [ ] Dört satır yeşil. - [ ] `feat(m321): …` — spec, plan ve kod tek commit; dist yok.
