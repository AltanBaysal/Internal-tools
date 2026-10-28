# Madde 399 — Ayrıntılar bölümü, implementasyon turunun planı

> **Koşum:** bu oturumda, satır satır. Takımı ve commit'i maddeyi koşan ajan yapıyor
> *(yol haritası, Dalga 1)*.

**Hedef:** `83211eb3`'ün 29 kırmızı testi yeşile döner, öteki testler yeşil kalır.

**Spec:** [m399 implementasyon turu](../specs/2026-09-30-queen-editor-m399-ayrintilar-uygulama-design.md)

## Her yere geçerli kurallar

- Tek dosya: `queen-editor/frontend/src/features/photo_generation/PhotoDetail.jsx`. Testlere
  dokunulmaz; `dist` yapılmaz.
- Yorum İngilizce, neden'i söyler; ekrandaki söz *"Ayrıntılar"*.

---

## Görev 1: Sarma kuralı ve bölüm bileşeni

`Field`'ın ardına:

```jsx
// How the frame's facts sit: side by side while they fit, wrapping on the 16 of the column's
// rhythm (Fark 91). The counter's group and the details' rows are drawn by the same rule.
const FACTS = { display: "flex", flexWrap: "wrap", columnGap: 24, rowGap: 16 };

// The row the frame's facts fold behind (madde 399): the owner found the column crowded, so what
// made the frame waits under one press. The column's own label face with the kit's caret and no box
// around it -- a heading that opens, not a button that does something.
function Details({ shown, onToggle, children }) {
  return (
    <div data-group="details" style={{ display: "flex", flexDirection: "column", gap: 12 }}>
      <button type="button" aria-expanded={shown} onClick={onToggle}
              style={{ display: "flex", alignItems: "center", gap: 6, background: "none",
                       border: "none", padding: 0, cursor: "pointer", width: "100%",
                       color: "var(--ink-3)" }}>
        <Mono size={10} style={LABEL}>Ayrıntılar</Mono>
        {/* Down while closed, up while open: where the facts are, and where they go. */}
        <span data-caret style={{ display: "flex", transition: "transform .12s",
                                  transform: shown ? "rotate(180deg)" : undefined }}>
          <Icon.Down />
        </span>
      </button>
      {shown && <div style={FACTS}>{children}</div>}
    </div>
  );
}
```

## Görev 2: Hâl

`const [open, setOpen] = useState("photo");`'un ardına:

```jsx
  // Whether the frame's facts are unfolded. The user's press rather than the frame's: the arrows
  // and the tabs leave it as it was, so walking a run of frames with them open costs one press.
  const [unfolded, setUnfolded] = useState(false);
```

Kare değişince çalışan effect'in yorumunda *"The open tab is the one thing that stays."* →
*"The open tab stays, and so does the details fold (madde 399), which was never the frame's."*

## Görev 3: Sütun

`data-group="info"` grubu yalnız *Sıra*'yı tutar ve `FACTS`'i kullanır; *Dosya adı*, *Model*,
*LoRA*, *Üretim modu* — koşulları ve yorumlarıyla, olduğu gibi — `Details`'ın içine taşınır:

```jsx
            {/* What the frame is. No group heading and no rule under it: the split from what can be
                made of it is where the eye rests, not a line it reads (Fark 91). */}
            <div data-group="info" style={FACTS}>
              {/* The same number the tile carries: … */}
              <Field label="Sıra" value={`${frames.length - index} / ${frames.length}`} />
            </div>

            <Details shown={unfolded} onToggle={() => setUnfolded((was) => !was)}>
              {/* The frame's own name, … (bugünkü yorum) */}
              <Field label={produced ? "Dosya adı" : "Dosya adı (planlanan)"} … />
              {open === "photo" && madeWith && ( … <Field label="Model" … /> )}
              {open === "photo" && madeWith && laidOver && <Field label="LoRA" … />}
              {open === "video" && madeIn && ( … <Field label="Üretim modu" … /> )}
            </Details>
```

## Görev 4: Koşu ve commit

- [ ] Dört satır, paralel — dördü de yeşil.
- [ ] `feat(queen-editor): 399 -- …`.
