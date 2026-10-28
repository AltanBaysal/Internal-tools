# v14 Görev 19 — Her sekme yalnız kendi katmanını gösterir: UYGULAMA döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Test döngüsünün bıraktığı 6 kırmızıyı yeşile döndürmek: üst grup iki satıra, prompt tek
kutuya, bekleyen kutunun satırı ortaya.

**Architecture:** Tek dosya, ve değişikliğin tamamı silme.

**Tech Stack:** React 18, vite.

**Spec:** [uygulama turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-19-sekme-kendi-katmani-uygulama-design.md)

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
| `.../photo_generation/PhotoDetail.jsx` | üst grup, prompt kutusu, bekleyen kutu | beş değişiklik |
| `frontend/dist/` | not defterinin okuduğu çıktı | derlenir |

---

### Task 1: Bekleyen kutunun tek satırı

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/PhotoDetail.jsx`

- [ ] **Step 1: `TextBlock`'un ipucu**

```jsx
// Prompt and negative are the same block twice: both take an equal share of whatever the two small
// fields leave behind, and each scrolls inside itself so a long negative cannot squeeze the prompt.
//
// `hint` is what an empty box says when the emptiness has a reason -- a layer nobody has written
// the words for yet (madde 81). It is centred while a real prompt is not: a prompt is read from the
// left, an absence is a notice and stands in the middle of the box (Fark 92). Without a hint an
// empty box says "—", because an empty negative is an answer of its own.
function TextBlock({ label, text, hint }) {
  const empty = !text;
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 6, flex: 1, minHeight: 0 }}>
      <Mono size={10} style={LABEL}>{label}</Mono>
      <div className="wf-stroke" style={{ flex: 1, minHeight: 0, overflowY: "auto", padding: 10 }}>
        {/* The box is drawn even with nothing in it: a box that came and went with the frame would
            make the column jump between frames -- and an empty one reads as a prompt somebody
            deleted, which is the whole reason the hint exists. */}
        <Note size={12} style={{ color: empty ? "var(--ink-4)" : "var(--ink-2)", display: "block",
                                 lineHeight: 1.6,
                                 ...(empty && hint ? { textAlign: "center" } : {}) }}>
          {empty ? (hint || "—") : text}
        </Note>
      </div>
    </div>
  );
}
```

---

### Task 2: Üst grup

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/PhotoDetail.jsx`

**Interfaces:**
- Produces: `data-field` — üst gruptaki bir satırın başlığı.

- [ ] **Step 1: `Field` bir işaret alıyor**

```jsx
function Field({ label, value, muted }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
      <Mono size={10} data-field style={LABEL}>{label}</Mono>
      <Mono size={13} style={{ color: muted ? "var(--ink-4)" : "var(--ink)" }}>{value}</Mono>
    </div>
  );
}
```

- [ ] **Step 2: Satırlar**

```jsx
              {/* The same number the tile carries: the badge counts up from the bottom, so walking
                  down the gallery with › walks the counter down with it. */}
              <Field label="Sıra" value={`${frames.length - index} / ${frames.length}`} />
              {/* The frame's own name, on every tab. The design took this row away too; it was put
                  back because the page's header carries the project's name and not the frame's, so
                  this is the only place the identity appears at all (karar 23). The layers' own
                  file names are what really went. With nothing on disk yet the name is a plan. */}
              <Field label={produced ? "Dosya adı" : "Dosya adı (planlanan)"}
                     value={(frame.layers || {}).photo || frame.file}
                     muted={!produced} />
```

`Üretim modu` satırı olduğu gibi kalıyor.

- [ ] **Step 3: `shown` siliniyor, `LAYER_WORD` adını ve kaynağını değiştiriyor**

```js
  \ Every layer up to the open one: the column shows their file names, then the open layer's own
  // prompt, then the ones under it (madde 75).
  const shown = LAYER_ORDER.slice(0, LAYER_ORDER.indexOf(open) + 1);
```

`LAYER_ORDER` kalıyor — `has` onu okuyor.

`LAYER_WORD` **silinmiyor**: üçüncü bir okuyucusu var, silinemeyen bir katmanın cümlesi
(`Video silinemedi`). Sütuna ait olmaktan çıktığı için adı ve kaynağı değişiyor — üç kelimeyi ikinci
kez yazmak yerine sekmelerin kendi etiketlerinden türüyor:

```js
// What a layer is called inside a sentence. Read off the tabs rather than written a second time:
// the window that says a video could not be deleted and the tab it was deleted from must not end up
// calling the same layer two different things.
const LAYER_LABEL = Object.fromEntries(TABS.map((row) => [row.id, row.label]));
```

ve `handleRemoveLayer` içindeki satır `LAYER_LABEL`'i okuyor.

---

### Task 3: Tek prompt kutusu

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/PhotoDetail.jsx`

- [ ] **Step 1: Döngü yerine tek kutu**

```jsx
            {/* The open layer's own prompt, and nothing under it: what a layer was made from is no
                longer this page's to show (madde 87). */}
            {holds ? (
              <PromptBox label="Prompt" value={typed} changed={changed}
                         onChange={(text) => setWords((kept) => ({ ...kept, [open]: text }))} />
            ) : (
              <TextBlock label="Prompt"
                         text={(frame.prompts || {})[open]
                               ?? (open === "photo" ? frame.prompt : "")}
                         // A layer still in the queue has no words yet, and nobody typed the
                         // missing ones. Not the photo's: those words are the user's own, so a
                         // notice about a prompt nobody has written would be false there.
                         hint={openState === "pending" && open !== "photo"
                           ? "Prompt yok — üretim sırası geldiğinde eklenecek."
                           : null} />
            )}
```

- [ ] **Step 2: Dört komutu koştur**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Expected: dördü de yeşil — 384 / 474 / 694 / 481.

---

### Task 4: Derlenmiş çıktı ve yeşil commit

- [ ] **Step 1: Derle**

Run: `npm run build --prefix queen-editor/frontend`

- [ ] **Step 2: Yol haritasını işaretle**

19. maddenin **İş** hücresi ✅ ile başlar, sayaç `18/31` → `19/31`.

- [ ] **Step 3: Commit**

```bash
git add queen-editor docs/superpowers
git commit -F - <<'EOF'
feat(queen-editor): a tab shows its own layer and stops there

The column drew every layer up to the open tab -- their file names in the top group, their
prompts stacked underneath. The reason was that a user might want to see what a layer was
made from, and that reason was withdrawn. The line holding the idea is gone and both of its
readers with it, so this change is almost entirely deletion.

Two rows are left above. The frame's own name is one of them, which is where the design was
overruled: the page's header carries the project's name and not the frame's, so this row is
the only place on screen where the frame says who it is. It reads the same on every tab now
-- its label used to change depending on whether a second name stood beside it.

A box waiting for its layer keeps a line so nobody reads the emptiness as a deletion, and
the line is centred: a prompt is read from the left, a notice stands in the middle. It no
longer names who will write the words. The photo tab never shows it -- a photo's words are
the user's own, and saying nobody has written them yet would be false there.

dist built in this commit.

Four suites green.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** spec'in dört bölümü Task 2 (1, 2), Task 3 (3), Task 1 (4).

**Tip tutarlılığı:** `PromptBox`'un `onChange`'i artık `open`'ı yazıyor, döngünün `layer`'ını
değil — ikisi de aynı değerdi ama biri artık yok.

**Kontrol edilen tuzak:** ortalama yalnız **boş ve ipuçlu** kutuya uygulanıyor. Her boş kutuya
uygulansaydı boş bir negatif prompt'un "—" işareti de ortaya kayardı, ve o bir bildirim değil bir
cevap.

**Kontrol edilen tuzak 2:** ad satırının etiketi artık `shown.length` okumuyor. O koşul "yanımda
başka satır var mı" demekti ve başka satır kalmadı.

**Kontrol edilen tuzak 3:** `LAYER_ORDER` silinmiyor — `has` sekmelerin hangisinin açılacağını
ondan okuyor.

**Koşuda çıkan tuzak 4:** `LAYER_WORD` iki değil **üç** yerde okunuyordu; üçüncüsü sütunda değil,
silinemeyen katmanın cümlesindeydi. Sabiti silmek o satırı çalışma anında düşürdü ve testi kırdı.
Bir sabiti silmeden önce adı aranır — ilk aramam tanımı görüp kullanımlarını görmemişti. Sabit
kaldı, adı ve kaynağı düzeltildi.

**Değişmeyen:** sekme şeridi, oynatıcı, silme düğmeleri, yeniden üret formu, negatif prompt.
