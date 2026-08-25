# v14 Görev 25 — Uyarı kendi kartına geçiyor: UYGULAMA döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `22db8af` ile kırmızı duran sekiz testi yeşile çevirmek — tür kartı kendi üreticisini
söylüyor, koşu kartı kurulum düğmesini bırakıyor, `producerReady` panelin içine iniyor.

**Architecture:** Ön yüzde üç dosya: `QueuePanel.jsx`, `SidePanel.jsx`, `ProjectScreen.jsx`. Motor
açılmıyor.

**Tech Stack:** React 18, vitest; Vite build.

**Spec:** [uygulama turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-25-uretici-uyarisi-uygulama-design.md)

## Global Constraints

- **Test yazılmıyor.** Testler `22db8af`'te.
- **Derlenmiş çıktı bu commit'e giriyor.**
- Yorumlar **İngilizce** ve **neden**i söylüyor; ekran metni **Türkçe**.
- Commit mesajında **çift tırnak yok**, ve **amend yok**.
- Komut: dört satır, birebir, boru yok.

## File Structure

| Dosya | İşlem |
|---|---|
| `frontend/.../photo_generation/QueuePanel.jsx` | tür kartı üreticisini söyler, koşu kartı düğmesini bırakır, `producerReady` içeride hesaplanır |
| `frontend/.../photo_generation/SidePanel.jsx` | `producerReady` imzadan çıkar, `producers` satırları geçer |
| `frontend/.../photo_generation/ProjectScreen.jsx` | `waitingFor` / `producerReady` hesabı ve yorumu çıkar |
| `frontend/dist/**` | derlenir |

---

### Task 1: `QueuePanel.jsx` — tür kartının kendi sözü

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/QueuePanel.jsx`

**Interfaces:**
- Consumes: `producers` prop'u — `{ id, name, installed, note }` satırları ya da `null`.
- Produces: `producerReady` artık dışarıdan gelmiyor; `SidePanel` onu vermeyi bırakıyor.

- [ ] **Step 1: `KindCard`'ı üretici satırıyla genişlet**

```jsx
// One kind's share of the queue. The card the engine has in hand is the one worth looking at; the
// rest wait their turn and step back rather than compete with it -- unless they have something to
// say, and a warning written at .55 is a warning nobody reads (Fark 38).
function KindCard({ layer, owed, alive, producer, onInstall }) {
  const kind = KINDS[layer];
  const missing = Boolean(producer) && !producer.installed;
  return (
    <div data-kind={layer} className="wf-stroke"
         style={{ padding: "10px 12px", display: "flex", flexDirection: "column", gap: 8,
                  ...(alive ? { borderColor: "var(--accent)" }
                    : missing ? {} : { opacity: 0.55 }) }}>
```

...başlık ve sayı satırları olduğu gibi, sonra kapanıştan önce:

```jsx
      {missing && (
        // The answer has been in hand since startup -- what is installed cannot change while the
        // app is up -- so there is no reason to keep it until the engine reaches this kind. The
        // producer is not named again: the card's own heading already says which one this is.
        <>
          <Note size={12} style={{ color: "var(--ink-2)" }}>Üretici kurulu değil.</Note>
          {/* Kur installs nothing (FOUNDATION 9): it writes the one sentence the app can answer
              with onto that producer's row, and the sentence belongs where the button is. */}
          {producer.note && (
            <Note size={12} style={{ color: "var(--ink-3)" }}>{producer.note}</Note>
          )}
          <Btn sm hl onClick={() => onInstall(layer)} style={{ justifyContent: "center" }}>Kur</Btn>
        </>
      )}
```

- [ ] **Step 2: İmzaya `producers` ekle, `producerReady`'yi çıkar**

```jsx
export default function QueuePanel({ job, error, errorField, busyElsewhere, project, stopping,
                                     queue, failures, producers, onStop, onResume, onCancel,
                                     onRetryAll, onInstall }) {
```

- [ ] **Step 3: `producerReady`'yi `waitingFor`'un altında hesapla**

```jsx
  // Nothing on this screen starts work by itself -- not a queue a dead session left owing frames,
  // and not one that stopped for a producer that has since arrived (user's decision, 2026-08-13).
  // A machine that starts rendering while nobody is looking is the one thing the user asked us to
  // stop doing. What is owed is still owed: the queue lives on disk, and this is the button that
  // carries it on. It is offered only once the producer is really here, because resuming without
  // it would stop at the same frame. Read from the rows the panel already has rather than taken as
  // a second-hand answer: one rule, one owner.
  const producerReady = Boolean(waitingFor)
    && (producers || []).some((row) => row.id === waitingFor && row.installed);
```

- [ ] **Step 4: Kartlara satırı ver**

```jsx
      {cards.map((card) => (
        <KindCard key={card.layer} layer={card.layer} owed={card.owed}
                  producer={(producers || []).find((row) => row.id === card.layer)}
                  onInstall={onInstall}
                  // Only while the run is really flowing, and only for the kind whose job the
                  // worker has in hand. A plan written before jobs had types is a photo job.
                  alive={running && !stopping
                         && (job.current?.type || "photo") === card.layer} />
      ))}
```

- [ ] **Step 5: Koşu kartından kurulum düğmesini çıkar**

`waiting` dalının `producerReady ? ... : ...` üçlüsünde ikinci koldaki `<Btn hl onClick={() =>
onInstall(waitingFor)}>` ve üstündeki yorum siliniyor; kalan tek satır:

```jsx
            ) : (
              <Note size={12} style={{ color: "var(--ink-3)" }}>
                Üretici kurulduktan sonra kuyruğu sen sürdürürsün.
              </Note>
            )}
```

- [ ] **Step 6: `PRODUCER_NAME` sözlüğünü sil**

Tek kullanıcısı gitti.

- [ ] **Step 7: Koş**

Run: `npm test --prefix queen-editor/frontend`
Expected: `SidePanel`'in kablolama testi dışında hepsi yeşil.

---

### Task 2: `SidePanel.jsx` — satırları geçir

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/SidePanel.jsx`

- [ ] **Step 1: İmzadan `producerReady`'yi çıkar**

```jsx
export default function SidePanel({ job, error, errorField, busyElsewhere, settings, project,
                                    stopping, queue, failures, models, modelsError, producers,
                                    frames, selected, onQueueLayer,
                                    onGenerate, onStop, onResume,
                                    onCancel, onClearError, onRetryAll }) {
```

- [ ] **Step 2: `QueuePanel` çağrısını değiştir**

```jsx
          <QueuePanel job={job} error={error} errorField={errorField}
                      busyElsewhere={busyElsewhere} project={project} stopping={stopping}
                      queue={queue} failures={failures} onStop={onStop} onResume={onResume}
                      onCancel={onCancel} onRetryAll={onRetryAll}
                      producers={producers?.producers || null}
                      onInstall={producers?.install} />
```

- [ ] **Step 3: Koş**

Run: `npm test --prefix queen-editor/frontend`
Expected: 541'in 541'i yeşil.

---

### Task 3: `ProjectScreen.jsx` — hesap ve yorum gider

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/ProjectScreen.jsx`

- [ ] **Step 1: `waitingFor` / `producerReady` bloğunu sil**

Üstündeki paragraf da gidiyor: iki cümlesi de artık `QueuePanel`'de, açıkladıkları düğmenin
yanında.

- [ ] **Step 2: `SidePanel` çağrısından `producerReady={producerReady}` satırını çıkar**

- [ ] **Step 3: Koş**

Run: `npm test --prefix queen-editor/frontend`
Expected: 541 yeşil.

---

---

### Koşuda çıkan tuzak

**Solma testi kendi kurgusundan düştü.** `leaves the card that has something to say readable`
foto kartını "sırada bekleyen" örneği sanmıştı; oysa `renderPanel`'in varsayılan koşan işi `current`
taşımıyor ve *türü olmayan iş foto işidir* — yani foto kartı o testte **canlı**, ve canlı kart da
solmuyor. Karşılaştırma kartı video ile değiştirildi.

Kırmızı tur bunu yakalayamazdı: test o an zaten kırmızıydı ve `''` ile `'0.55'`'in hangisinin
beklendiği ancak uygulama gelince görülüyor. Kaydı buraya düşüyor — düzeltme testin kendi
yanlışıydı, uygulamanın değil.

---

### Task 4: Dört komut, derleme, commit

- [ ] **Step 1: Dört komutu da koş**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Expected: 384 / 474 / 709 / 541, hepsi yeşil.

- [ ] **Step 2: Derle**

```
npm run build --prefix queen-editor/frontend
```

- [ ] **Step 3: Yol haritasının 25. satırını işaretle ve sayacı ilerlet**

`**Durum:** 24/31` → `**Durum:** 25/31`; 25. satırın **İş** hücresi `✅` ile başlar ve 46. karar
satıra not düşer.

- [ ] **Step 4: Commit**

```bash
git add docs/superpowers/specs/2026-08-21-queen-editor-v14-gorev-25-uretici-uyarisi-uygulama-design.md docs/superpowers/plans/2026-08-21-queen-editor-v14-gorev-25-uygulama.md docs/superpowers/plans/2026-08-20-queen-editor-v14-roadmap.md queen-editor/frontend/src queen-editor/frontend/dist
git commit -m @'
feat(queen-editor): the kind card says which producer is missing
'@
```

Çift tırnak yok, amend yok.
