# v14 Görev 16 — Panel hata dili: UYGULAMA döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Test döngüsünün bıraktığı 13 kırmızıyı yeşile döndürmek: dört sebep, kırmızı kart, kırmızı
varyant kutusu, kilidi kalkmış buton.

**Architecture:** Tek dosya. Cümleler `WORDS`'e, sıra bir modül fonksiyonuna, cevap butonun altındaki
tek yuvaya giriyor.

**Tech Stack:** React 18, vite.

**Spec:** [uygulama turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-16-panel-hata-dili-uygulama-design.md)

## Global Constraints

- **Test dosyaları bu döngüde değişmiyor.**
- Yorumlar **İngilizce**; ekran metni **Türkçe**.
- Commit mesajında **çift tırnak yok**, ve **amend yok**.
- Komut: dört satır, birebir, boru yok.
- **`dist` bu commit'te derleniyor.**
- Commit **yeşil gider**.
- Hiçbir cümlenin sonunda `— üretilecek bir şey yok` yok.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `.../photo_generation/LayerPanel.jsx` | cümleler, sıra, buton, kart, kutu | altı değişiklik |
| `frontend/dist/` | not defterinin okuduğu çıktı | derlenir |

---

### Task 1: Cümleler ve sıra

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/LayerPanel.jsx`

**Interfaces:**
- Produces: `refusalOf(words, can, scope, scoped, variants) -> string | null`.

- [ ] **Step 1: `WORDS`'ün boş cümlesini üçe böl**

`video` bloğunda `empty` satırı şununla değişiyor:

```js
    // Why a press found nothing to do. Three of them, because the panel can be empty for three
    // different reasons and one sentence for all of them is what sent the user here (İstek 4.3).
    // noBase is what this layer hangs on: for a video that is the frame's own picture.
    noBase: "Henüz üretilmiş kare yok.",
    chosenNoBase: "Seçili karelerin fotoğrafı henüz üretilmedi.",
    allHeld: "Tüm karelerin videosu var.",
```

`audio` bloğunda:

```js
    // A sound hangs on a video, not on a photo -- so an empty project reads this one here, and it
    // is the nearer thing that is missing.
    noBase: "Videosu olan kare yok.",
    chosenNoBase: "Seçili karelerin videosu henüz üretilmedi.",
    allHeld: "Tüm karelerin sesi var.",
```

- [ ] **Step 2: Dördüncü cümle ve fonksiyon**

`acceptsVariants`'ın altına:

```js
// The one reason that belongs to no layer: the box is on both panels and says the same thing.
const NO_VARIANTS = "Varyant sayısı girilmedi — en az 1 yaz.";

/** Why this press cannot go to the queue, or null when it can.
 *
 * Read in the order a person would: the box in front of them first, then whether the project holds
 * anything this layer could ever hang on, then what they picked, then the scope's own answer.
 *
 * `can` is every frame this layer could be hung on at all -- empty means the layer underneath is
 * missing, which is a different sentence from "they all have one already". That difference is the
 * whole point: one sentence for every empty scope is what made the panel blame frames for having
 * videos when what they were missing was pictures (İstek 4.3).
 *
 * No dead branch: for a video `can` is the produced frames themselves, so its noBase is exactly
 * "nothing is produced yet"; for a sound it is the frames holding a video, and its noBase says so.
 */
function refusalOf(words, can, scope, scoped, variants) {
  if (variants === "") return NO_VARIANTS;
  if (scoped.length) return null;
  if (!can.length) return words.noBase;
  if (scope === "selected") return words.chosenNoBase;
  return words.allHeld;
}
```

---

### Task 2: Panelin cevabı

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/LayerPanel.jsx`

- [ ] **Step 1: Sebebin durduğu yer**

`const [added, setAdded] = useState(null);` satırının altına:

```js
  // Why the last press went nowhere, or null. The green card's opposite number and it lives in the
  // same slot: one press, one answer.
  const [refused, setRefused] = useState(null);
```

- [ ] **Step 2: Sebep ne zaman siliniyor**

`linkingClosed` etkisinin altına:

```js
  // A reason belongs to the press that produced it: the frames it counted, the scope it named and
  // the number it read. Move any of the three and it becomes a stale answer standing under a button
  // about to be pressed again. The gallery's selection is in here too -- picking other frames over
  // there is exactly such a move. A press changes none of the three, so the answer stays up.
  useEffect(() => { setRefused(null); }, [chosen, scope, variants]);
```

- [ ] **Step 3: Basış önce sorar**

```js
  function handleAdd() {
    const why = refusalOf(words, can, scope, scoped, variants);
    if (why) {
      setAdded(null);
      clearTimeout(fade.current);
      setRefused(why);
      return;
    }
    setSubmitting(true);
    setAdded(null);
    clearTimeout(fade.current);
    const sent = mode;
    onQueue(scope === "selected" ? inSelection.map((frame) => frame.file) : null, Number(variants),
            sent)
      .then((body) => {
        if (body && typeof body.added === "number") {
          setAdded({ count: body.added, mode: sent });
          fade.current = setTimeout(() => setAdded(null), CONFIRM_MS);
        }
      })
      .finally(() => setSubmitting(false));
  }
```

---

### Task 3: Buton, kart ve kutu

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/LayerPanel.jsx`

- [ ] **Step 1: Varyant kutusu**

`onBlur` satırı siliniyor, biçime kırmızı çerçeve giriyor:

```jsx
        <input
          className="wf-input"
          type="number"
          min={1}
          max={MAX_VARIANTS}
          value={variants}
          onChange={(e) => { if (acceptsVariants(e.target.value)) setVariants(e.target.value); }}
          /* Red while it is empty, and it stays empty: the silent reset to 1 on the way out is what
             kept the box from ever showing it (Fark 29). What the emptiness means is said when the
             button is pressed. */
          style={{ width: 56, textAlign: "center", fontSize: 13,
                   ...(variants === "" ? { borderColor: "var(--danger)" } : {}) }}
        />
```

- [ ] **Step 2: Butonun kilidi**

```jsx
        {/* Nothing the user could fill in locks this: an empty field is answered after the press,
            in the card below (Fark 27). What is left is one request in flight -- and the producer,
            which is the design's own exception: it is not a field, it is an engine that is not
            here yet, and the card at the top of the panel says so. */}
        <button type="button" className="wf-btn wf-btn--hl"
                disabled={submitting || missingProducer} onClick={handleAdd}
                style={{ justifyContent: "center", padding: "10px 12px", fontSize: 14 }}>
```

- [ ] **Step 3: Kırmızı kart, ve boş cümlenin gidişi**

Butonun altındaki blok:

```jsx
        {added !== null ? (
          <div className="wf-stroke"
               style={{ padding: "8px 10px", display: "flex", alignItems: "center", gap: 8,
                        borderColor: "var(--ok)", background: "var(--ok-bg)" }}>
            <Note size={12} style={{ color: "var(--ok)" }}>✓</Note>
            <Note size={12} style={{ color: "var(--ok)" }}>
              {added.count} {nounOf(added.mode, words.noun)} kuyruğa eklendi
            </Note>
          </div>
        ) : refused ? (
          // The green card's red twin: the same box in the same place, the other colour. The mark
          // is its own part for the reason the green one's is -- it carries the answer at a glance
          // and does not wrap onto the sentence's second line.
          <div className="wf-stroke"
               style={{ padding: "8px 10px", display: "flex", alignItems: "center", gap: 8,
                        borderColor: "var(--danger)", background: "var(--danger-bg)" }}>
            <Note size={12} style={{ color: "var(--danger)" }}>✕</Note>
            <Note size={12} style={{ color: "var(--danger)" }}>{refused}</Note>
          </div>
        ) : owed ? (
          // The copy warning takes the mode's tail, never its head: the mode is already named in
          // what comes out, so what is given up is an echo of the marked row just above.
          <Note size={12} style={{ color: "var(--ink-3)", textAlign: "center" }}>
            {owed} {said.noun} üretilecek — {copies
              ? `${words.held} ${copies} kare için yeniler kopya kare olur, eskisi durur.`
              : said.tail}
          </Note>
        ) : null}
```

Son daldaki boş-kapsam cümlesi tümüyle gidiyor: basılmadan önce panel sakin.

- [ ] **Step 4: Dört komutu koştur**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Expected: dördü de yeşil — 384 / 474 / 694 / 467.

---

### Task 4: Derlenmiş çıktı ve yeşil commit

- [ ] **Step 1: Derle**

Run: `npm run build --prefix queen-editor/frontend`

- [ ] **Step 2: Yol haritasını işaretle**

16. maddenin **İş** hücresi ✅ ile başlar, sayaç `15/31` → `16/31`.

- [ ] **Step 3: Commit**

```bash
git add queen-editor docs/superpowers
git commit -F - <<'EOF'
feat(queen-editor): the layer panel says which reason it means

The panel had one sentence for every empty scope, so with unproduced frames selected it told
the user their frames already had videos. What they were missing was pictures. It now works
out which of four things is true and says that one, and the sound panel answers in its own
terms -- what is missing under a sound is a video, so an empty project there reads that no
frame has a video rather than that none is produced.

The order is the order a person looks in: the box in front of them, then whether the project
holds anything this layer could hang on at all, then what they picked, then the scope's own
answer. Which frames a layer could ever hang on and which are left to do are two different
questions, and keeping them apart is what makes four sentences out of one.

The button no longer locks for anything the user could fill in. It is pressed, and the
answer arrives under it as the green card's red twin. The producer is the one thing still
holding it: not a field but an engine that is not here yet, which is the design's own
exception and which the card at the top of the panel already explains.

The variant box turns red while it is empty and stays empty -- the silent reset to 1 on the
way out was what kept it from ever showing that. A reason leaves as soon as the frames, the
scope or the count move under it, the gallery's own selection included; it was an answer to
one press, and those three are what that press read.

dist built in this commit.

Four suites green.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** spec'in altı bölümü Task 1 (sebep fonksiyonu, cümleler), Task 2 (silinme anı,
basış), Task 3 (buton, kart, kutu).

**Tip tutarlılığı:** `refusalOf` her yolda ya bir dize ya `null` döndürüyor; `refused` state'i aynı
iki değeri taşıyor ve render'da doğruluk sınamasıyla okunuyor.

**Kontrol edilen tuzak:** silme etkisinin bağımlılıkları. `mode` içinde **yok** — hiçbir sebep moddan
söz etmiyor, ve içinde olsaydı mod satırına basmak cevabı sebepsiz silerdi.

**Kontrol edilen tuzak 2:** `chosen` referansı. `selected` prop'u galeri tarafında bir state
dizisi, yani seçim değişmediği sürece aynı nesne — etki her render'da yeniden koşmuyor.

**Kontrol edilen tuzak 3:** `handleAdd` reddederken `setSubmitting` çağırmıyor. Çağırsaydı buton
hiç yola çıkmayan bir istek için kilitlenirdi.

**Kontrol edilen tuzak 4:** `onBlur` kalkınca `Number("")` sıfır oluyor ve tahmin satırı
kayboluyor — istenen bu: kutu boşken tahmin edilecek bir şey yok, ve sebebi basış söylüyor.

**Değişmeyen:** `GeneratePanel.jsx`, `eligible`, `neighbours`, `acceptsVariants`.
