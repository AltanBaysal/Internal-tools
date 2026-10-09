# Uzun hata metni: İMPLEMENTASYON döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `f85d8f3`'teki kırmızıyı yeşile çevirmek.

**Architecture:** Bir yeni ortak bileşen, iki kullanım yeri, bir panel stili.

**Tech Stack:** React 18, vitest, Vite build.

**Tasarım:** [implementasyon spec'i](../specs/2026-08-14-queen-editor-hata-karti-uygulama-design.md)

## Global Constraints

- **Testler değişmiyor.** `f85d8f3`'teki yedi test sözleşme.
- Yorum ve commit mesajı **İngilizce**.
- **`dist/` aynı commit'te** yeniden derlenir.
- Commit mesajında **çift tırnak yok**.
- Komutlar: `npm test --prefix queen-editor/frontend` · `npm run build --prefix queen-editor/frontend`

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `src/shared/RawOutput.jsx` | ham çıktının kutusu ve kopyalanması | **yeni** |
| `src/shared/StatusErrorCard.jsx` | uygulama geneli hata kartı | ham blok devreder |
| `.../photo_generation/QueuePanel.jsx` | durdu kartı | cümle ayrılır, çıktı kutuya girer |
| `.../photo_generation/SidePanel.jsx` | yan panel sütunu | dikeyde kayar |

---

### Task 1: Kutu

**Files:**
- Create: `queen-editor/frontend/src/shared/RawOutput.jsx`

**Interfaces:**
- Produces: `RawOutput({ text })` — adlandırılmış dışa aktarım.

- [ ] **Step 1: Dosyayı yaz**

```jsx
import { useEffect, useRef, useState } from "react";

import { Btn, Mono } from "../vendor/kit.jsx";

// About five lines of it: enough for the line that usually carries the answer, short enough that a
// sixty line failure cannot push what is under it off the panel.
// display: block is load-bearing and no test can see it -- the kit's Mono is a span, and max-height
// and overflow do not apply to an inline box at all. Without it the style is written, the browser
// ignores it, and the suite stays green while the box grows without end.
const BOX = { display: "block", maxHeight: 90, overflowY: "auto", overflowX: "hidden",
              whiteSpace: "pre-wrap", wordBreak: "break-word", color: "var(--ink-3)" };
// Long enough to be read without looking away, short enough that the button is a button again
// before it is next needed.
const SAID_MS = 2500;

/** The service's own output, folded rather than cut.
 *
 * The repo rule is that an error prints what the command or the service actually said, and a
 * sixty line answer is what that sometimes means. Nothing is dropped: the whole text is here,
 * inside its own ceiling, and one press puts it on the clipboard.
 */
export function RawOutput({ text }) {
  const [said, setSaid] = useState(null);
  const fade = useRef(null);

  useEffect(() => () => clearTimeout(fade.current), []);

  function copy() {
    clearTimeout(fade.current);
    // Written straight from the press, not from a microtask after it: the clipboard is granted to
    // a user gesture, and a browser may refuse a write that arrives even a tick late. The try is
    // for the other half -- with no clipboard object at all the call throws where it stands, while
    // a refused permission rejects instead, and the user needs the same answer either way.
    let landing;
    try {
      landing = navigator.clipboard.writeText(text);
    } catch (absent) {
      landing = Promise.reject(absent);
    }
    Promise.resolve(landing)
      .then(() => setSaid("Kopyalandı"))
      .catch(() => setSaid("Kopyalanamadı"))
      .finally(() => { fade.current = setTimeout(() => setSaid(null), SAID_MS); });
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
      <Mono data-raw size={10} style={BOX}>{text}</Mono>
      <Btn sm onClick={copy} style={{ alignSelf: "flex-start" }}>{said || "Kopyala"}</Btn>
    </div>
  );
}
```

- [ ] **Step 2: Koş**

Run: `npm test --prefix queen-editor/frontend -- src/shared/RawOutput.test.jsx`
Expected: 4 geçen.

---

### Task 2: İki kullanım yeri

**Files:**
- Modify: `queen-editor/frontend/src/shared/StatusErrorCard.jsx`
- Modify: `queen-editor/frontend/src/features/photo_generation/QueuePanel.jsx`

- [ ] **Step 1: `StatusErrorCard` kutuyu devralır**

`Mono` import'u artık gerekmiyorsa çıkar; `raw` bloğu:

```jsx
      {raw && <RawOutput text={raw} />}
```

ve tepeye `import { RawOutput } from "./RawOutput.jsx";`

- [ ] **Step 2: `QueuePanel` hatayı ikiye ayırır**

`describeError`'ın altına:

```js
/** The engine's own error: the rule's sentence, then the service's answer under it.
 *
 * Two things that are read differently -- one is a sentence, the other is evidence -- so they are
 * drawn differently. A one line error has no evidence to fold and gets no box.
 */
function splitReason(text) {
  const nl = text.indexOf("\n");
  return nl < 0 ? { said: text, raw: "" }
    : { said: text.slice(0, nl), raw: text.slice(nl + 1) };
}
```

`errorInfo`'nun yanına:

```js
  const stopped = halted && job.error ? splitReason(job.error) : null;
```

ve bugünkü blok:

```jsx
        {halted && job.error && (
          <Mono size={10} style={{ color: "var(--ink-3)", whiteSpace: "pre-wrap" }}>
            {job.error}
          </Mono>
        )}
```

şununla değişir:

```jsx
        {stopped && (
          <>
            <Mono size={10} style={{ color: "var(--ink-3)", whiteSpace: "pre-wrap" }}>
              {stopped.said}
            </Mono>
            {stopped.raw && <RawOutput text={stopped.raw} />}
          </>
        )}
```

Tepeye `import { RawOutput } from "../../shared/RawOutput.jsx";`

- [ ] **Step 3: Koş**

Run: `npm test --prefix queen-editor/frontend -- src/shared src/features/photo_generation/QueuePanel.test.jsx`
Expected: hepsi yeşil.

---

### Task 3: Panel kayar

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/SidePanel.jsx`

- [ ] **Step 1: `PANEL`'in taşma kuralı**

```js
  overflow: "hidden",
```

şununla değişir:

```js
  // Vertical only: a panel that scrolls sideways would be madde 107's own rule broken from the
  // inside. What made this necessary was an error long enough to push the buttons under it out of
  // reach -- with nowhere to scroll, they were simply gone.
  overflowY: "auto",
  overflowX: "hidden",
```

- [ ] **Step 2: Tam takım**

Run: `npm test --prefix queen-editor/frontend`
Expected: 331 geçen, 0 düşen.

---

### Task 4: Derle ve commit'le

- [ ] **Step 1: Derle**

Run: `npm run build --prefix queen-editor/frontend`

- [ ] **Step 2: Commit**

```bash
git add queen-editor/frontend/src queen-editor/frontend/dist docs/superpowers
git commit -F - <<'EOF'
feat(queen-editor): fold a long error instead of letting it take the panel

The seven tests from the previous commit go green.

The service's own output now lives in a box of its own: the whole of it, under
a ceiling of about five lines, with one press to put it on the clipboard. It
is folded, never cut -- an error prints what the service actually said, and
sixty lines is sometimes what that means.

Two places use it. The queue panel's stopped card splits the engine's error
where the engine joined it, so the rule's sentence stays a sentence and only
the evidence is folded away. StatusErrorCard hands its raw text over as well;
it is drawn on three screens and carried the same unbounded block.

The panel itself now scrolls vertically. The box alone would have answered
today's failure, but the panel could not scroll at all, so anything long
enough put what was under it out of reach rather than below the fold.

One line no test can defend: the box is display block. The kit's Mono is a
span, and max-height and overflow do not apply to an inline box -- without it
the style is written, the browser ignores it, and the suite stays green while
the box grows without end. Its comment says so.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** kutu → Task 1 · iki kullanım → Task 2 · panel → Task 3 · `dist/` → Task 4.

**Kontrol edilen tuzak:** `display: block`. Testin göremediği tek satır; hem spec'te hem kodda
yorumu var, çünkü ancak yazılı gerekçe onu bir sonraki sadeleştirmeden korur.

**Kontrol edilen bağ:** `QueuePanel`'in bugünkü tek satırlık hata testi
(`Bağlantı hatası — sunucuya ulaşılamadı`) satır sonu taşımıyor, yani `splitReason` `raw: ""`
döndürür ve kutu çizilmez — o test olduğu gibi yeşil kalır.

**Kontrol edilen import:** `StatusErrorCard` `Mono`'yu yalnız `raw` için kullanıyordu; devredince
import öksüz kalır ve silinir. `Note`, `Icon`, `Btn` duruyor.

**Testin yakaladığı hata:** ilk yazışta kopyalama `Promise.resolve().then(() => writeText(...))`
ile başlıyordu ve `writeText` basış anında değil bir mikrogörev sonra çağrılıyordu. Test bunu
düşürdü; sebebi de gerçekti — pano bir kullanıcı jestine verilen izin, geç gelen yazma
reddedilebilir. Kırmızı testin, kodun zihin modelini miras almadığında ne yakaladığının örneği.

**Bildirilen fark:** `stopped` satırı `halted`'dan **sonra** durur; `errorInfo`'nun yanına konsaydı
`halted` henüz tanımlı olmadığı için ReferenceError verirdi. Plan yazılırken bu gözden kaçtı,
uygulamada düzeltildi.
