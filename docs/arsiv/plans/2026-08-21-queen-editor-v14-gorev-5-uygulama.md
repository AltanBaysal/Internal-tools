# v14 Görev 5 — Sonrakine bağla ardışık seçim istiyor: UYGULAMA döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Test döngüsünün kırmızı bıraktığı üç testi yeşile döndürmek: dağınık seçimde bağlama
seçeneği kapansın, altında sebebi yazsın, ve seçiliyken seçim dağılırsa mod Standart'a düşsün.

**Architecture:** Tek dosya. Kuralın kendisi modül seviyesinde saf bir fonksiyon (`neighbours`);
bileşen onu iki yerde okuyor — satırı kapatmak ve modu düşürmek için.

**Tech Stack:** React 18, vite.

**Spec:** [uygulama turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-5-ardisik-secim-uygulama-design.md)

## Global Constraints

- **Test dosyaları bu döngüde değişmiyor.**
- Yorumlar **İngilizce**; ekran metni **Türkçe**.
- Commit mesajında **çift tırnak yok**, ve **amend yok**.
- Komut: dört satır, birebir, boru yok.
- **`dist` bu commit'te derleniyor.**
- Commit **yeşil gider**.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `frontend/src/features/photo_generation/LayerPanel.jsx` | ardışıklık kuralı ve sonucu | `neighbours`, `ModeRow` disabled, sebep satırı, efekt |
| `frontend/dist/` | not defterinin okuduğu çıktı | derlenir |

---

### Task 1: Kuralın kendisi

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/LayerPanel.jsx`

**Interfaces:**
- Produces: `neighbours(frames, chosen) -> boolean`. Task 2 ve Task 3 okuyor.

- [ ] **Step 1: Sabiti ve fonksiyonu yaz**

`acceptsVariants`'ın altına:

```jsx
// Why linking closes when the chosen frames are scattered. Says the reason rather than the remedy:
// what to do about it is visible in the gallery, why it matters is not.
const SCATTERED_REASON = "Zincir ancak bitişik karelerde kapanır — arada seçilmemiş kare var.";

/** Do the chosen frames sit together in the gallery, with nothing unchosen between them?
 *
 * Measured against the whole gallery rather than the frames this layer could be hung on: the engine
 * reads a linked video's target from the gallery's own sequence, so a frame standing in between is
 * a real hole in the chain whatever state it is in.
 *
 * max - min + 1 === count, so no sorting: a run of positions with no gap is exactly as wide as it
 * is long. An id the gallery does not hold -- a frame deleted while it was selected -- contributes
 * no position and is not counted, so it cannot make a solid run look broken.
 */
function neighbours(frames, chosen) {
  const places = (frames || []).reduce(
    (found, frame, index) => (chosen.includes(frame.id) ? [...found, index] : found), []);
  if (places.length < 2) return true;   // one frame has nothing to skip over
  return Math.max(...places) - Math.min(...places) + 1 === places.length;
}
```

- [ ] **Step 2: Takımı koştur**

Run: `npm test --prefix queen-editor/frontend`
Expected: değişen bir şey yok — fonksiyonu henüz kimse çağırmıyor. Üç kırmızı duruyor.

---

### Task 2: Kapanan satır ve sebebi

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/LayerPanel.jsx`

**Interfaces:**
- Consumes: Task 1'in `neighbours`'ı.

- [ ] **Step 1: ModeRow disabled alsın**

```jsx
function ModeRow({ label, active, disabled, onPick }) {
  return (
    <button type="button" onClick={onPick} disabled={disabled}
            className="wf-stroke"
            style={{ display: "flex", alignItems: "center", padding: "8px 10px", background: "none",
                     cursor: disabled ? "default" : "pointer",
                     borderColor: active ? "var(--accent)" : "var(--border)",
                     opacity: disabled ? 0.4 : active ? 1 : 0.4, width: "100%" }}>
      <Note size={12} style={{ color: "var(--ink-2)" }}>{label}</Note>
    </button>
  );
}
```

Saydamlık sırası `ScopeRow`'unkiyle aynı: kapalı olan da seçili olmayan da 0.4, ama koşul önce
kapalıyı soruyor — kapalı ve seçili bir satır, seçili gibi parlak durmamalı.

- [ ] **Step 2: Kapanma koşulunu hesapla**

`scoped` ve `owed`'ın yanına:

```jsx
  // Only on the selection's own scope: "Videosu olmayanlar" is scattered by nature -- what sits
  // between its members already has a video -- and each of its frames still has a real next.
  const linkingClosed = scope === "selected" && !neighbours(frames, chosen);
```

- [ ] **Step 3: Satırı ve sebebi çiz**

```jsx
      {layer === "video" && (
        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          <Mono size={11} style={LABEL}>Üretim modu</Mono>
          {MODES.map((one) => (
            <ModeRow key={one.id} label={one.label} active={mode === one.id}
                     disabled={one.id === LINKED && linkingClosed}
                     onPick={() => setMode(one.id)} />
          ))}
          {linkingClosed && (
            // Under the row it closed, in the ordinary ink: a closed option is a rule, not a fault.
            <Note size={12} style={{ color: "var(--ink-3)" }}>{SCATTERED_REASON}</Note>
          )}
        </div>
      )}
```

`LINKED` `production_modes.js`'ten geliyor; import satırı `{ LINKED, MODES, STANDARD }` olur ve o
dosya `LINKED`'i dışa verir:

```js
export const STANDARD = "standard";
export const LINKED = "linked";

export const MODES = [
  { id: STANDARD, label: "Standart" },
  { id: "loop", label: "Loop" },
  { id: LINKED, label: "Sonrakine bağla" },
];
```

Kimliği ad olarak dışa vermek, panelin `"linked"` dizesini kendi içinde ikinci kez yazmasını
önlüyor.

- [ ] **Step 4: Takımı koştur**

Run: `npm test --prefix queen-editor/frontend`
Expected: 1. ve 2. test yeşile döner. 6. hâlâ kırmızı: satır kapanıyor ama seçili kalıyor.

---

### Task 3: Kapanan seçenek seçili kalamaz

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/LayerPanel.jsx`

- [ ] **Step 1: Efekti yaz**

Kapsamı seçime uyduran `useEffect`'in altına:

```jsx
  // A row nobody can click must not keep going to the queue. Written as an effect rather than a
  // correction during render: what changed is a prop from the gallery, and the panel never hears a
  // second click to put itself right.
  useEffect(() => {
    if (linkingClosed) setMode((picked) => (picked === LINKED ? STANDARD : picked));
  }, [linkingClosed]);
```

Güncelleyici biçim (`setMode((picked) => ...)`) çünkü efekt `mode`'a bağımlı değil: bağımlı olsaydı
her mod değişiminde yeniden koşar ve okuduğu şey kendi yazdığı şey olurdu.

- [ ] **Step 2: Dört komutu koştur**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Expected: dördü de yeşil.

---

### Task 4: Derlenmiş çıktı ve yeşil commit

- [ ] **Step 1: Derle**

Run: `npm run build --prefix queen-editor/frontend`

- [ ] **Step 2: Yol haritasını işaretle**

5. maddenin **İş** hücresi ✅ ile başlar, sayaç `4/31` → `5/31`.

- [ ] **Step 3: Commit**

```bash
git add queen-editor docs/superpowers
git commit -F - <<'EOF'
feat(queen-editor): linking closes when the chosen frames are scattered

The chain only closes if the chosen frames sit together in the gallery. With a hole in
the middle it is two pieces, each ending on a frame nobody picked -- so the option shuts
and one line under it says why.

Neighbouring is max - min + 1 === count over the positions the chosen ids hold in the
gallery: a run with no gap is exactly as wide as it is long, so nothing has to be
sorted. An id the gallery no longer holds contributes no position, so a frame deleted
while it was selected cannot make a solid run look broken. Measured against the whole
gallery, because that is the sequence the engine reads a target from.

Only on the selection scope. On every-frame-with-no-video the option stays open: that
set is scattered by nature and each of its frames still has a real next.

A closed option cannot stay picked, so the mode falls back to plain. An effect rather
than a correction during render: what changed is a prop from the gallery.

dist built in this commit.

Four suites green.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** spec'in dört parçası (`neighbours`, `ModeRow` disabled, sebep satırı, efekt)
sırayla Task 1, 2, 2 ve 3'te.

**Tip tutarlılığı:** `neighbours(frames, chosen)` iki yerde de aynı argümanlarla — biri satırı
kapatıyor, biri modu düşürüyor, ve ikisi de aynı `linkingClosed` değerini okuyor, yani kural iki
kez hesaplanmıyor.

**Kontrol edilen tuzak:** `places.length < 2` kontrolü hem tek kareyi hem hiç seçim olmamasını
kapsıyor. Yalnız `=== 1` yazılsaydı boş seçim `Math.max()` çağrısına düşer ve `-Infinity` üretirdi.

**Kontrol edilen tuzak 2:** efekt yalnız `linkingClosed`'a bağımlı. `mode`'u da bağımlılığa
koymak, kullanıcı bağlama seçtiği anda efektin yeniden koşup onu geri alması demekti — koşul
doğruyken bile.

**Kontrol edilen tuzak 3:** `disabled` koşulu `one.id === LINKED` diyor, sırayla bir indekse değil.
Liste sırası bir gün değişirse indeks yanlış satırı kapatırdı.

**Kontrol edilen kapsam:** 6. test `onQueue`'nun kapsamına da bakıyor (`["2_a.png", "0_a.png"]`).
Efekt yalnız modu düşürüyor, seçime dokunmuyor — ve testin o yarısı bunun nöbeti.
