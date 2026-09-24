# Madde 324 — Eksik satırı, uygulama turunun planı

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*. Dört test satırını
> koordinatör koşar; commit onun.

**Hedef:** `8adc8de5`'in dokuz kırmızı testi yeşile, gerisi yeşil kalarak.

**Spec:** [m324 uygulama turu](../specs/2026-09-24-queen-editor-m324-eksik-satiri-uygulama-design.md)

## Her yere geçerli kurallar

- Testlere ve dist'e dokunulmuyor. `queue_references.py`'de yalnız cümlenin satırı değişiyor;
  `ReferencePanel.jsx`'te yalnız bileşenin başı.
- Yorum İngilizce ve yalnız bugün doğru olanı söylüyor.

---

## Görev 1: `list_producers.py` — video satırının yeni alanı

Docstring'e bir cümle, video dalına bir satır:

```python
def list_producers(groups, files, video_model=""):
    """`video_model` is the notebook's pick. The video row names it, because the panel cannot know
    which model the notebook installed any other way (madde 247). It also says whether that model
    makes video from the reference pool: only H3 has such a mode (madde 302), and the video panel
    says so before the press (madde 324) -- read from here, not from the name, which is a word for
    the box."""
    ...
        if kind == VIDEO:
            row["model"] = video_model_name(video_model)
            row["reads_references"] = video_model == "h3"
```

## Görev 2: `queue_references.py` — boş havuz cümlesi

Yalnız cümlenin satırı:

```python
            "Havuzda referans yok — önce en az bir referans ekle.")
```

## Görev 3: `ReferencePanel.jsx` — her cevap ekrana

Bileşenin docstring'inin son paragrafı, imzası ve ilk satırları:

```jsx
/**
 * The project's reference pool, in the middle in place of the cards while the video panel is on
 * Referanstan (madde 318).
 *
 * It asks for its own pool rather than being handed one: it is where the pool changes, and the
 * answer carries the limits it heads its rows with -- so the numbers are never written down twice
 * (madde 298 owns them). Every answer is handed up as well (onPool): the video panel's missing line
 * reads the same pool (madde 324).
 */
export default function ReferencePanel({ project, onPool = () => {} }) {
  const [pool, showPool] = useState({ references: [], limits: {} });
  // Only the server's answers go up: the empty stand-in above is the wait, not the pool.
  const setPool = (answer) => {
    showPool(answer);
    onPool(answer);
  };
```

`setPool`'un dört çağrı yeri değişmiyor.

## Görev 4: `ProjectScreen.jsx` — havuzu ekran tutuyor

`poolShown`'ın altına:

```jsx
  // The pool's last answer from the server, or null until one came (madde 324). The pool in the
  // middle is where it changes, and the video panel's missing line has to hear that at once. Kept
  // while the pool is closed: nothing on this screen changes it then, and opening it reads it again.
  const [pool, setPool] = useState(null);
```

`<ReferencePanel project={project} onPool={setPool} />`; `SidePanel`'e `pool={pool}`.

## Görev 5: `SidePanel.jsx` — geçiriyor

İmzaya `pool` *(`poolShown`'ın yanına)*; `LayerPanel`'e `pool={pool}`.

## Görev 6: `LayerPanel.jsx` — satır ve kilitler

`NO_VARIANTS`'ın altına:

```js
// What stops a run from the pool, said before the press (madde 324). The server's own sentences
// (queue_references.py), word for word: the line shows the refusal a press would get.
const H3_ONLY = "Referanstan üretim için H3 gerekiyor — bu oturumda başka bir video modeli kurulu.";
const NO_REFERENCES = "Havuzda referans yok — önce en az bir referans ekle.";
```

`refusalOf`'un altına:

```js
/** What the line above the button says on Referanstan, or null (madde 324).
 *
 * The app's order, one sentence at a time: the model, then the pool. A preview of the server's own
 * refusals, never a rule (FOUNDATION 4): what has not answered yet -- the producers, the pool --
 * says nothing, and the press goes. With no video producer there is no wrong model: the install card
 * at the top says what is missing. One reference of any kind is enough.
 */
function poolRefusal(producer, pool) {
  if (producer?.installed && !producer.reads_references) return H3_ONLY;
  if (pool && !pool.references.length) return NO_REFERENCES;
  return null;
}
```

İmzaya `pool` *(`poolShown`'ın yanına)*. `missingProducer`'ın altına:

```js
  // Referanstan's line, and nothing on Kareden: the frame form answers after the press.
  const missingLine = fromPool ? poolRefusal(producer, pool) : null;
```

Varyant satırıyla düğme bloğunun arasına:

```jsx
      {missingLine && (
        // Above the button it stops, in the ordinary ink: a state of the session, said before the
        // press rather than after it.
        <Note size={12} style={{ color: "var(--ink-2)", textAlign: "center" }}>{missingLine}</Note>
      )}
```

Düğme ve yorumu:

```jsx
        {/* On Kareden nothing the user could fill in locks this: an empty field is answered after
            the press, in the card below (Fark 27). What locks it is one request in flight -- and
            the producer, which is the design's own exception: not a field but an engine that is
            not here yet, and the card at the top of the panel says so. Referanstan says what it
            lacks before the press instead (madde 324): whatever the line above says, and a prompt
            box with nothing in it. */}
        <button type="button" className="wf-btn wf-btn--hl"
                disabled={submitting || missingProducer || busyElsewhere
                          || (fromPool && (Boolean(missingLine) || !prompts.trim()))}
                onClick={handleAdd}
                style={{ justifyContent: "center", padding: "10px 12px", fontSize: 14 }}>
```

## Görev 7: Denetim ve teslim

- [ ] `soldaki panele` hiçbir kaynakta kalmadı *(Grep)*.
- [ ] `ReferencePanel.jsx`'in `setPool` çağrı yerleri dokunulmamış *(diff)*.
- [ ] Koordinatöre dönüş: değişen dosyalar, spec'in dikte etmediği kararlar, emin olunmayanlar.
