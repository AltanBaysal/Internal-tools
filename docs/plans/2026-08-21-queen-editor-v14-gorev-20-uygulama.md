# v14 Görev 20 — Sekmelerin ayrılması: UYGULAMA döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Test döngüsünün bıraktığı 2 kırmızıyı yeşile döndürmek: şeride 8 piksel boşluk, düğmelere
kendi köşeleri.

**Architecture:** Tek dosya, tek bileşen. Üç satır ve iki yorum.

**Tech Stack:** React 18, vite.

**Spec:** [uygulama turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-20-sekme-ayrimi-uygulama-design.md)

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
| `.../photo_generation/PhotoDetail.jsx` | sekme şeridi | üç satır, iki yorum |
| `frontend/dist/` | not defterinin okuduğu çıktı | derlenir |

---

### Task 1: Şerit ve düğmeler

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/PhotoDetail.jsx`

**Interfaces:**
- Produces: `data-strip` — sekme şeridi; boşluğu buradan okunuyor.

- [ ] **Step 1: Şeridin yorumu**

```js
// Madde 73's strip: three tabs over the stage, 8px apart so each reads as its own (Fark 85). A
// layer the frame does not have stays disabled rather than hidden -- the user sees what a frame
// could still become.
```

- [ ] **Step 2: `STRIP`**

```js
const STRIP = { position: "absolute", top: 16, left: "50%", transform: "translateX(-50%)",
                display: "flex", gap: 8, zIndex: 2 };
```

- [ ] **Step 3: `LayerTabs`**

```jsx
function LayerTabs({ open, has, onOpen }) {
  return (
    <div data-strip style={STRIP}>
      {TABS.map(({ id, label, Glyph }) => (
        <button key={id} type="button" disabled={!has[id]}
                aria-current={open === id ? "page" : undefined}
                onClick={() => onOpen(id)} className="wf-stroke"
                style={{ display: "flex", alignItems: "center", gap: 4, padding: "4px 10px",
                         background: "var(--bg-2)", cursor: has[id] ? "pointer" : "default",
                         opacity: has[id] ? 1 : 0.35,
                         color: open === id ? "var(--accent)" : "var(--ink-3)",
                         borderColor: open === id ? "var(--accent)" : "var(--border)" }}>
          {Glyph && <Glyph size={10} />}
          <Mono size={10}>{label}</Mono>
        </button>
      ))}
    </div>
  );
}
```

Değişen: `data-strip`, `index` parametresi gitti, `marginLeft` satırı ve yorumu gitti. Yarıçap
eklenmiyor — `wf-stroke` onu zaten veriyor.

- [ ] **Step 4: Dört komutu koştur**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Expected: dördü de yeşil — 384 / 474 / 694 / 484.

---

### Task 2: Derlenmiş çıktı ve yeşil commit

- [ ] **Step 1: Derle**

Run: `npm run build --prefix queen-editor/frontend`

- [ ] **Step 2: Yol haritasını işaretle**

20. maddenin **İş** hücresi ✅ ile başlar, sayaç `19/31` → `20/31`.

- [ ] **Step 3: Commit**

```bash
git add queen-editor docs/superpowers
git commit -F - <<'EOF'
feat(queen-editor): the layer tabs come apart

Eight pixels between them and nothing pulling one onto the next. The corner radius needed
nothing added -- the stroke class has always drawn it, and what hid it was two rounded
corners meeting on the same pixel.

The gap is the strip's, not the buttons'. Three buttons have two gaps between them, and a
margin writes a number three times to produce two of them.

Which tab is open still shows the way it always did: the word and the outline both turn
accent. Both of those are colour, and the design forbids a mark, not a colour -- an
underline or a dot is what it means by a mark. So nothing about the open tab changes here;
only the geometry does.

dist built in this commit.

Four suites green.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** spec'in üç bölümü Task 1'in üç adımı (2, 3, 1 sırasıyla).

**Tip tutarlılığı:** `data-strip` testin aradığı adla birebir aynı.

**Kontrol edilen tuzak:** `index` silinirken `key` unutulmuyor — `key={id}` `index`'ten gelmiyordu,
`id`'den geliyor.

**Kontrol edilen tuzak 2:** `marginLeft` tamamen siliniyor, `0`'a çekilmiyor. Test `""` bekliyor;
`marginLeft: 0` `"0px"` yazardı ve `Foto` bugün tam olarak onu yazıyor.

**Kontrol edilen tuzak 3:** `STRIP` başka hiçbir yerde okunmuyor — `gap`'i yalnız bu şeride
yazılıyor.

**Değişmeyen:** açık sekmenin rengi, pasif sekmenin hâli, ikonlar, sahne, sağ sütun.
