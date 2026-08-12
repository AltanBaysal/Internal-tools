# Görev 9 — Tür kartları ve panel düzeni · Uygulama Planı

> **Çalıştıran ajan için:** GEREKLİ ALT BECERİ: superpowers:executing-plans.

**Amaç:** Kuyruk paneli tür başına kart çizer; sayı vurgu rengine döner; başlık "Kuyruk" olur ve
"Kuyruğu boşalt" panelin dibine iner.

**Mimari:** `useGeneration` `pending` (dosya adı dizisi) yerine `queue` (`[{layer, owed}]`) üretir.
`QueuePanel` bu listeden kart çizer; koşunun kendi hâlleri ayrı bir kartta kalır.

**Yığın:** React 18 + Vite · vitest + jsdom. Arka uca dokunulmaz.

**Spec:** [Görev 9 tasarımı](../specs/2026-08-12-queen-editor-v5-gorev-9-tur-kartlari-design.md)

## Global kısıtlar

- **Full TDD:** önce kırmızı test.
- Katman anahtarları arka ucun sözcükleri: `photo` · `video` · `audio`; tür sırası da onun sırası.
- Dil ayrımı: yorum/test adı/commit **İngilizce**, kullanıcı metni **Türkçe**.
- Test komutları: `npm test --prefix queen-editor/frontend -- --run` ·
  `python -m pytest queen-editor -q` · derleme `npm run build --prefix queen-editor/frontend`.
- **Tek commit**, görevin sonunda, `dist/` ile birlikte.

---

### Görev 1: Kuyruk tür başına sayılır

**Dosyalar:**
- Değiştir: `queen-editor/frontend/src/features/photo_generation/useGeneration.js:196-215`
- Test: `queen-editor/frontend/src/features/photo_generation/useGeneration.test.jsx`

**Arayüzler:**
- Üretir: `queue` — `[{ layer, owed }]`, üretim sırasında (`photo` → `video` → `audio`), yalnız
  `owed > 0` olan türler. `pending` kalkar.

- [ ] **Adım 1: Testleri yaz (kırmızı test)**

`useGeneration.test.jsx` — `pending` bekleyen üç testi `queue`ya çevir ve birini ekle:

```jsx
  it("counts what is owed for each kind of job, not one lump", async () => {
    getStatus.mockResolvedValue({ ...RUNNING, current: { id: "P0_0" } });
    listFrames.mockResolvedValue([
      { id: "P0_0", file: "P0_0.png", status: "pending" },
      { id: "P1_0", file: "P1_0.png", status: "pending" },
      { id: "P2_0", file: "P2_0.png", status: "pending" },
    ]);

    const { result } = renderHook(() => useGeneration("düğün"));
    await settle();

    // The one the worker holds is being made, not waiting.
    expect(result.current.queue).toEqual([{ layer: "photo", owed: 2 }]);
  });

  it("counts the half-done job again once the queue is paused", async () => {
    getStatus.mockResolvedValue({ status: "paused", project: "düğün" });
    listFrames.mockResolvedValue([
      { id: "P0_0", file: "P0_0.png", status: "pending" },
      { id: "P1_0", file: "P1_0.png", status: "pending" },
      { id: "P2_0", file: "P2_0.png", status: "pending" },
    ]);

    const { result } = renderHook(() => useGeneration("düğün"));
    await settle();

    expect(result.current.current).toBeNull();
    expect(result.current.queue).toEqual([{ layer: "photo", owed: 3 }]);
  });

  it("leaves out a kind with nothing owed", async () => {
    getStatus.mockResolvedValue({ status: "idle" });
    listFrames.mockResolvedValue([{ id: "P0_0", file: "P0_0.png", status: "done" }]);

    const { result } = renderHook(() => useGeneration("düğün"));
    await settle();

    expect(result.current.queue).toEqual([]);
  });
```

Var olan "leaves the frame being rendered out of the waiting count" testi yukarıdaki ilk testin
kendisidir — eskisi silinir.

- [ ] **Adım 2: Koş, kırmızıyı gör**

Koş: `npm test --prefix queen-editor/frontend -- --run`
Beklenen: `result.current.queue` tanımsız.

- [ ] **Adım 3: Sayımı yaz**

`useGeneration.js` — `pending` bloğunun yerine:

```js
// The order the engine works in: it finishes one kind before it starts the next, so the cards are
// drawn in this sequence too. The words are the server's own (layers.PHOTO / VIDEO / AUDIO).
const KINDS = ["photo", "video", "audio"];
```

ve dönüş öncesinde:

```js
  // What the queue still owes, kind by kind. The frame being rendered has no line on disk either,
  // so the gallery draws it as pending too -- it is not waiting, it is being made, and it comes out
  // of the count. Pause puts it back: the worker stops reporting it and the half-done job is owed
  // again.
  //
  // Today every owed job is a photo job, because the gallery is the only place this can be read
  // from. When video and audio jobs join the queue the server will count them; the panel does not
  // change, because a card is drawn from this list either way.
  const owedPhotos = shown
    .filter((frame) => frame.status === "pending" && frame.file !== current).length;
  const owedByKind = { photo: owedPhotos, video: 0, audio: 0 };
  const queue = KINDS
    .map((layer) => ({ layer, owed: owedByKind[layer] }))
    .filter((card) => card.owed > 0);
```

Dönüşte `pending` yerine `queue` verilir.

- [ ] **Adım 4: Koş, yeşili gör**

Koş: `npm test --prefix queen-editor/frontend -- --run`
Beklenen: `useGeneration.test.jsx` PASS; `QueuePanel`/`ProjectScreen`/`SidePanel` testleri hâlâ
kendi `pending` prop'larıyla koştukları için PASS.

---

### Görev 2: Panel tür kartı çizer

**Dosyalar:**
- Değiştir: `queen-editor/frontend/src/features/photo_generation/QueuePanel.jsx`
- Test: `queen-editor/frontend/src/features/photo_generation/QueuePanel.test.jsx`

**Arayüzler:**
- Tüketir: `queue` — `[{ layer, owed }]` (Görev 1).

- [ ] **Adım 1: Testleri yaz (kırmızı test)**

`QueuePanel.test.jsx` — `renderPanel`'in varsayılanı `pending` yerine `queue` alır:

```jsx
      queue={[{ layer: "photo", owed: 2 }]}
```

ve `pending` geçen her çağrı `queue`ya çevrilir (`pending: ["7_a.png", "8_a.png"]` →
`queue: [{ layer: "photo", owed: 2 }]`, `pending: []` → `queue: []`).

"a flowing queue" bloğuna:

```jsx
  it("draws the kind's own card and no run card of its own", () => {
    renderPanel();

    expect(screen.getByText("üretiliyor")).toBeTruthy();
    expect(screen.getByText("2")).toBeTruthy();
    expect(screen.getByText("kare bekliyor")).toBeTruthy();
    expect(screen.queryByText("Üretiliyor")).toBeNull();
  });

  it("draws one card per kind, in the order the engine works in", () => {
    renderPanel({ queue: [{ layer: "video", owed: 3 }, { layer: "photo", owed: 1 }] });

    const cards = [...document.querySelectorAll("[data-kind]")].map((c) => c.dataset.kind);
    expect(cards).toEqual(["photo", "video"]);
  });

  it("counts jobs rather than frames for the layers that do not open one", () => {
    renderPanel({ queue: [{ layer: "photo", owed: 1 }, { layer: "video", owed: 3 }] });

    expect(screen.getByText("kare bekliyor")).toBeTruthy();
    expect(screen.getByText("iş bekliyor")).toBeTruthy();
  });

  it("leaves only the kind the worker is on alive", () => {
    renderPanel({ job: { ...RUNNING, current: { id: "P0_0", type: "photo" } },
                  queue: [{ layer: "photo", owed: 1 }, { layer: "video", owed: 3 }] });

    const alive = [...document.querySelectorAll("[data-kind]")]
      .filter((card) => card.querySelector(".qe-dot--alive"))
      .map((card) => card.dataset.kind);
    expect(alive).toEqual(["photo"]);
  });
```

"a paused queue" bloğuna:

```jsx
  it("puts the queue's own card beside the run's, each answering its own question", () => {
    renderPanel({ job: PAUSED, queue: [{ layer: "photo", owed: 3 }] });

    expect(screen.getByText("Duraklatıldı")).toBeTruthy();
    expect(screen.getByText("sırada")).toBeTruthy();
    expect(screen.getByText("3")).toBeTruthy();
  });
```

ve panelin dibi:

```jsx
  it("keeps the destructive button at the foot of the panel", () => {
    renderPanel({ job: PAUSED, queue: [{ layer: "photo", owed: 2 }] });

    const clear = screen.getByText("Kuyruğu boşalt");
    const resume = screen.getByText("Devam et");
    expect(resume.compareDocumentPosition(clear) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
  });
```

`"counts the cut frame back in and offers the way out"` testindeki `"Duraklatıldı"` iddiası kalır.

- [ ] **Adım 2: Koş, kırmızıyı gör**

Koş: `npm test --prefix queen-editor/frontend -- --run`
Beklenen: `queue` prop'u okunmadığı için sayı kartı boş; birçok FAIL.

- [ ] **Adım 3: Paneli yaz**

`QueuePanel.jsx` — tür kartı ve sözlükler dosyanın başına:

```jsx
// The order the engine works in, and what a card of each kind counts. A photo job opens a new
// frame, so counting frames is right there; a video or audio job produces a layer of a frame that
// already exists, which is why those count jobs instead (madde 34/35).
const KINDS = {
  photo: { title: "Foto", unit: "kare bekliyor" },
  video: { title: "Video", unit: "iş bekliyor" },
  audio: { title: "Ses", unit: "iş bekliyor" },
};
const KIND_ORDER = ["photo", "video", "audio"];

function KindCard({ layer, owed, alive }) {
  const kind = KINDS[layer];
  return (
    <div data-kind={layer} className="wf-stroke"
         style={{ padding: "10px 12px", display: "flex", flexDirection: "column", gap: 8,
                  // The card the engine is on is the one worth looking at; the rest wait their
                  // turn and step back rather than compete with it.
                  ...(alive ? { borderColor: "var(--accent)" } : { opacity: 0.55 }) }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <span aria-hidden="true" className={alive ? "qe-dot qe-dot--alive" : "qe-dot"}
              style={{ background: alive ? "var(--accent)" : "var(--ink-3)" }} />
        <Note size={12} style={{ color: alive ? "var(--ink-2)" : "var(--ink-3)" }}>
          {kind.title} · {alive ? "üretiliyor" : "sırada"}
        </Note>
      </div>
      <div style={{ display: "flex", alignItems: "baseline", gap: 8 }}>
        {/* The biggest number on the screen wears the accent colour, like every other counter. */}
        <Mono size={26} style={{ color: "var(--accent)" }}>{owed}</Mono>
        <Note size={13} style={{ color: "var(--ink-2)" }}>{kind.unit}</Note>
      </div>
    </div>
  );
}
```

İmza ve türetmeler:

```jsx
export default function QueuePanel({ job, error, errorField, busyElsewhere, project, stopping,
                                     queue, failures, onStop, onResume, onCancel,
                                     onShowFailures }) {
```

```jsx
  const cards = KIND_ORDER
    .map((layer) => (queue || []).find((card) => card.layer === layer))
    .filter(Boolean);
  const owed = cards.reduce((total, card) => total + card.owed, 0);
```

`state` hesabı aynen kalır. Kartların çizimi, koşu kartının önüne:

```jsx
      {cards.map((card) => (
        <KindCard key={card.layer} layer={card.layer} owed={card.owed}
                  // Only while the run is really flowing, and only for the kind whose job the
                  // worker has in hand. A plan written before jobs had types is a photo job.
                  alive={running && !stopping
                         && (job.current?.type || "photo") === card.layer} />
      ))}
```

Koşu kartı yalnız düz akmayan hâllerde çizilir ve büyük sayısını bırakır:

```jsx
      {state !== "running" && (
        <div className="wf-stroke" style={{ padding: "10px 12px", display: "flex",
                                            flexDirection: "column", gap: 8 }}>
          … bugünkü içerik, ancak "kare bekliyor" öbeği olmadan …
        </div>
      )}
```

Yani bugünkü kartın gövdesinden `state === "done"` ve `state === "empty"` dalları aynen kalır,
üçüncü daldaki büyük sayı öbeği silinir. Hata satırı, `busyElsewhere` satırı ve `job.error` satırı
yerinde kalır.

"Kuyruğu boşalt" ana butondan sonra, esneyen boşlukla:

```jsx
      {canClear && <div style={{ flex: 1, minHeight: 8 }} />}
```

- [ ] **Adım 4: Koş, yeşili gör**

Koş: `npm test --prefix queen-editor/frontend -- --run`

---

### Görev 3: Panelin adı ve besleyicileri

**Dosyalar:**
- Değiştir: `queen-editor/frontend/src/features/photo_generation/SidePanel.jsx`
- Değiştir: `queen-editor/frontend/src/features/photo_generation/ProjectScreen.jsx:24`, `:45-48`,
  `:98`
- Test: `SidePanel.test.jsx`, `ProjectScreen.test.jsx`

- [ ] **Adım 1: Başlık testini yaz (kırmızı test)**

`SidePanel.test.jsx`'teki "names the open panel above it":

```jsx
    fireEvent.click(screen.getByLabelText("Kuyruğu takip et"));

    expect(screen.getByRole("heading", { name: "Kuyruk" })).toBeTruthy();
```

- [ ] **Adım 2: Koş, kırmızıyı gör**

Koş: `npm test --prefix queen-editor/frontend -- --run`

- [ ] **Adım 3: Şeridin adı ile başlığı ayır**

`SidePanel.jsx` — panel satırı ikinci bir alan alır; `title` şeridin ipucu, `heading` başlık:

```jsx
// Adding a panel later means adding a row here -- the rail is drawn from this list, not from three
// hard-coded buttons. The id is the layer's own word, so it matches both the glyph's name and what
// the server calls that kind of job. `title` is what the rail's icon is called; `heading` is what
// the open panel is called, and the queue is the one place the design gives those two different
// words.
const PANELS = [
  { id: "photo", title: "Fotoğraf üret" },
  { id: "queue", title: "Kuyruğu takip et", heading: "Kuyruk" },
  { id: "agent", title: "AI agent" },
];
```

```jsx
        <h2 style={{ margin: 0 }}>
          <Mono size={11} style={LABEL}>{current.heading || current.title}</Mono>
        </h2>
```

`SidePanel` `pending` yerine `queue` alır ve `QueuePanel`'e geçirir.

- [ ] **Adım 4: Proje ekranını çevir**

`ProjectScreen.jsx`:

```jsx
  const { job, frames, error, errorField, stopping, queue, failures, current,
```

```jsx
    if (!queue.length) return;
```

```jsx
  }, [project, mine, job.status, queue.length, resume]);
```

```jsx
                   stopping={stopping} queue={queue} failures={failures}
```

- [ ] **Adım 5: Koş, yeşili gör**

Koş: `npm test --prefix queen-editor/frontend -- --run`
`ProjectScreen.test.jsx` kendi sahte hook'unu kullanıyorsa oradaki `pending` de `queue`ya çevrilir.

---

### Görev 4: Kapanış

- [ ] **Adım 1: İki takımı da koş**

Koş: `npm test --prefix queen-editor/frontend -- --run`
Koş: `python -m pytest queen-editor -q` → 376 PASS (arka uca dokunulmadı)

- [ ] **Adım 2: Derle**

Koş: `npm run build --prefix queen-editor/frontend`

- [ ] **Adım 3: Tek commit**

```bash
git add -A
git commit -F - <<'MSG'
feat(queen-editor): the queue counts each kind of work on its own card

One card and one number worked while photos were the only thing in the queue.
The moment video and audio jobs join it, a single lump hides the two things
worth knowing: how much of each is left, and which kind the engine is on.

So the panel draws a card per kind, in the order the engine works in, and the
card the worker is on is the live one. The number moves onto those cards and
takes the accent colour every other counter already wears; what is left of the
old card says only what the run itself is doing, which is nothing at all while
work is flowing.

The photo card still counts frames, because a photo job opens one. The video
and audio cards count jobs, because theirs do not -- they add a layer to a
frame that already exists.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
MSG
```

## Öz denetim

**1. Spec kapsaması:** Karar 1 (birim sözcüğü) → Görev 2'nin `KINDS` sözlüğü ve testi; karar 2
(sayı tür kartında) → Görev 2 Adım 3; karar 3 (`queue` prop'u) → Görev 1 + 3; karar 4 (hangi kart
canlı) → Görev 2'nin `alive` testi; karar 5 (vurgu rengi) → `KindCard`; karar 6 (gerisi Görev 10)
→ koşu kartının içeriğine dokunulmuyor. Panel başlığı (madde 40) Görev 3, dip buton (41) Görev 2.

**2. Yer tutucu taraması:** Görev 2 Adım 3'te koşu kartının gövdesi "bugünkü içerik" diye anılıyor
— bu yer tutucu değil, **dokunulmayacak** kodun tarifi; değişen tek şey büyük sayı öbeğinin
silinmesi ve sarmalayıcının koşulu.

**3. Tür tutarlılığı:** `queue` elemanı her yerde `{layer, owed}`; `KIND_ORDER` ile
`useGeneration`'ın `KINDS` dizisi aynı üç sözcük ve aynı sıra; `data-kind` değeri `layer` ile
birebir.
