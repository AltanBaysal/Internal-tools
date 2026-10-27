# Madde 320 — Sıranın kendi `Ekle` kartı, uygulama turunun planı

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*.

**Hedef:** `1bf92234`'ün kırmızı testleri yeşile dönüyor.

**Spec:** [m320 uygulama turu](../specs/2026-09-24-queen-editor-m320-ekle-karti-uygulama-design.md)

## Her yere geçerli kurallar

- Yorum **İngilizce**; arayüz metni tasarımdan harfi harfine. Testlere dokunulmaz.
- **Dist derlenmez** — Kol A'nın kuralı; birleşme commit'i derler.

---

## Görev 1: Sunucu

`add_references.py` — sınıfın docstring'i ve `row`:

```python
class UnknownReference(Exception):
    """A file the pool cannot read, or one picked into another kind's row (message is
    user-facing)."""
```

```python
def add_references(store, pool, orders, clips, project, files, row=None):
    """`files` is [(the name the browser sent, the bytes)].

    `row` is the kind of the row whose Ekle card the files were picked from (madde 320). The user
    asked for them in that row, so a file of another kind is refused there rather than quietly filed
    under its own. Without a row, each file goes to its own kind's.
    """
```

Döngüde, tanınmayan dosyanın reddinden hemen sonra, ad çözülmeden:

```python
        if row is not None and kind != row:
            raise UnknownReference(f"{name} {references.SAID[row]} yuvasına giremez — "
                                   f"bu dosya {references.SAID[kind]}.")
```

`reference_routes.py`:

```python
            # The form's kind is the row the files were picked into (madde 320).
            return pool(add_references(project, files, row=request.form.get("kind")))
```

## Görev 2: `api.js`

```js
// A form rather than JSON, and no Content-Type of ours: multipart carries a boundary, and only the
// browser knows what it wrote. The kind is the row whose Ekle card picked the files: the server
// holds them to it (madde 320).
export async function uploadReferences(project, files, kind) {
  const form = new FormData();
  for (const file of files) form.append("files", file);
  form.append("kind", kind);
```

## Görev 3: `ReferencePanel.jsx` ve `app.css`

`ROWS` — her sıraya `accept` ve `picker`:

```jsx
// The three rows, in the order the pool is read in. The words are the user's; the keys are H3's
// own labels, which is what the server answers with. `accept` only narrows the browser's picker --
// it can be switched to every file, and which row a file may go in is the server's to say
// (FOUNDATION 4).
const ROWS = [
  { kind: "picture", title: "Fotoğraflar", Glyph: PhotoGlyph, accept: "image/*",
    picker: "fotoğraf ekle" },
  { kind: "video", title: "Videolar", Glyph: VideoGlyph, accept: "video/*", picker: "video ekle" },
  { kind: "audio", title: "Sesler", Glyph: SoundGlyph, accept: "audio/*", picker: "ses ekle" },
];
```

`ADD`'e `cursor: "pointer"`. `Tile`'ın ardına:

```jsx
/** A row's way in, after its last reference until the row holds all it may: a press opens a picker
 * for this row's kind, one file at a time (madde 320).
 *
 * Not a label around the input: a label's words name what it holds, and every card says Ekle while
 * each picker is named for its own kind. The input stands after the card, not inside it: the click
 * the card hands the input would bubble back into the card's own handler. */
function AddCard({ kind, accept, picker, uploading, onPick }) {
  const input = useRef(null);
  return (
    <>
      <div data-add={kind} style={ADD} onClick={() => input.current.click()}>
        {uploading === kind
          ? <><span className="qe-spinner" aria-hidden="true" /> Yükleniyor…</>
          : <><PlusGlyph size={14} /> Ekle</>}
      </div>
      {/* Any file on its way holds every card: two in flight would each be weighed against a pool
          without the other. */}
      <input ref={input} type="file" accept={accept} aria-label={picker}
             disabled={uploading !== null} style={{ display: "none" }} onChange={onPick} />
    </>
  );
}
```

Panelde:

```jsx
  // The kind of the row whose file is on its way, or null.
  const [uploading, setUploading] = useState(null);
```

`handlePick(kind, event)` — `setBusy` yerine `setUploading(kind)` / `setUploading(null)`, ve
`uploadReferences(project, files, kind)`. `busy` yalnız silmenin.

`PANEL`'in ilk çocuğu ret kartı:

```jsx
      {/* Above the rows: where the eye is when a pick comes back refused. */}
      {error && <StatusErrorCard text={error} />}
```

Sıranın sonunda, 319'un kartının yerine:

```jsx
              {rows.length < (pool.limits[kind] ?? 0) && (
                <AddCard kind={kind} accept={accept} picker={picker} uploading={uploading}
                         onPick={(event) => handlePick(kind, event)} />
              )}
```

Ortak `Ekle` label'ı ve alttaki `StatusErrorCard` siliniyor.

`app.css` — `.qe-spinner`'ın yorumu:

```css
/* What turns inside a press still in flight -- Ekleniyor… on the add buttons, Yükleniyor… on the
   reference pool's Ekle card: a ring with one quarter cut out. Ours, not the design system's --
   hence the qe- prefix. */
```

## Görev 4: Koşu ve yeşil commit

- [ ] Dört satır yeşil. - [ ] `feat(m320): …` — spec, plan ve kod tek commit; dist yok.
