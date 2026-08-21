# v14 Görev 24 — Proje ekranının hizalaması: UYGULAMA döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `c7a8ce2` ile kırmızı duran sekiz testi yeşile çevirmek — çöp yıkıcı standarda, kalem
`ghost`'a, pencere tek ölçüye, liste kendi kutusuna, onay yeni söz sırasına.

**Architecture:** Ön yüzde dört dosya: `ProjectCard.jsx`, `ProjectsScreen.jsx`, `NameModal.jsx`,
`app.css`. Motor açılmıyor.

**Tech Stack:** React 18, vitest; Vite build.

**Spec:** [uygulama turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-24-proje-ekrani-uygulama-design.md)

## Global Constraints

- **Test yazılmıyor.** Testler `c7a8ce2`'de. Bir test ancak kendi yanlışı yüzünden düşerse
  düzeltilir, ve düzeltmesi de bu planın kaydına girer.
- **Derlenmiş çıktı bu commit'e giriyor** — defter klonluyor, derlemiyor.
- Yorumlar **İngilizce** ve **neden**i söylüyor; ekran metni **Türkçe**.
- Commit mesajında **çift tırnak yok**, ve **amend yok**.
- Komut: dört satır, birebir, boru yok.

## File Structure

| Dosya | İşlem |
|---|---|
| `frontend/.../projects/ProjectCard.jsx` | iki düğme kitin varyantlarına geçer |
| `frontend/.../projects/NameModal.jsx` | `width` parametresi düşer, 380 içeride |
| `frontend/.../projects/ProjectsScreen.jsx` | ekran 100vh, liste kutusu + bant, onayın söz sırası, iki `width` çağrısı |
| `frontend/src/shared/app.css` | `.qe-thin-scroll` |
| `frontend/dist/**` | derlenir |

---

### Task 1: `ProjectCard.jsx` — iki düğme

**Files:**
- Modify: `queen-editor/frontend/src/features/projects/ProjectCard.jsx`

**Interfaces:**
- Consumes: `Btn` (`sm`, `icon`, `ghost` bayrakları), `Icon.Pencil`, `Icon.Trash`.
- Produces: `aria-label` değerleri değişmiyor — testler onlardan buluyor.

- [ ] **Step 1: Yıkıcı kalıbı dosyanın başına al**

`ProjectCard` içinde, bileşenin üstüne:

```jsx
// Red text, red border, no fill -- the app-wide destructive standard. The design's own texts
// disagreed here (the rules document counts project delete among its examples, the card drawing
// shows a bare icon); the difference list's first decision settled it for the rules document.
const DANGER = { color: "var(--danger)", borderColor: "var(--danger)", background: "none" };
```

- [ ] **Step 2: İki düğmeyi kitin varyantlarına çevir**

```jsx
      {/* Two icon buttons, 4px apart (Fark 5). The bin wears the destructive standard and the
          pencil wears ghost -- transparent line, same box, so the two sit level; border:none took
          a pixel off every side and shifted them against each other. The pencil stays bare on
          purpose (karar 43): a red frame is a mark, and it only marks while what sits beside it
          has none. Neither carries a word -- the one the standard asks for is on the delete
          confirm, where there is room for it. */}
      <div style={{ position: "absolute", top: 10, right: 10, display: "flex", gap: 4 }}>
        <Btn sm icon ghost aria-label="Projeyi yeniden adlandır" onClick={onRename}>
          <Icon.Pencil />
        </Btn>
        <Btn sm icon aria-label="Projeyi sil" onClick={onDelete} style={DANGER}>
          <Icon.Trash />
        </Btn>
      </div>
```

- [ ] **Step 3: Koş**

Run: `npm test --prefix queen-editor/frontend`
Expected: çöp ve kalem testleri yeşil; kalan altı kırmızı.

---

### Task 2: `NameModal.jsx` — ölçü pencerenin

**Files:**
- Modify: `queen-editor/frontend/src/features/projects/NameModal.jsx`

- [ ] **Step 1: Parametreyi düşür**

```jsx
// Both windows carry the same form -- the same label, the same box, the same two buttons -- so
// there is one measure and it is the window's own (Fark 6). It was the caller's while the two were
// expected to differ.
const WIDTH = 380;

export default function NameModal({ title, value = "", submitLabel, busyLabel,
                                    onCancel, onSubmit }) {
```

- [ ] **Step 2: Kartın stilinde kullan**

```jsx
        style={{ width: WIDTH, padding: 20, display: "flex", flexDirection: "column", gap: 12 }}
```

- [ ] **Step 3: Başlıktaki yorumu düzelt**

`its heading, its opening value, its words and its measure come from whoever opened it` →
`its heading, its opening value and its words come from whoever opened it`.

- [ ] **Step 4: Koş**

Run: `npm test --prefix queen-editor/frontend`
Expected: `NameModal`'ın ölçü testi yeşil; ekranın yeni proje ölçüsü testi de yeşil, çünkü
`width={400}` artık okunmuyor.

---

### Task 3: `ProjectsScreen.jsx` — kutu, bant, söz sırası

**Files:**
- Modify: `queen-editor/frontend/src/features/projects/ProjectsScreen.jsx`

- [ ] **Step 1: Bandın stilini yaz**

`CENTERED`'ın altına:

```jsx
// The foot of the list dissolving into the page rather than being cut off (Fark 8). It sits over
// the box rather than in it -- inside, it would scroll away with the cards -- and it takes no
// clicks, so the card underneath still opens.
const FADE = {
  position: "absolute", left: 0, right: 0, bottom: 0, height: 40,
  background: "linear-gradient(rgba(15, 15, 16, 0), var(--bg))",
  pointerEvents: "none",
};
// Two rows of four. The design gives a count rather than a measurement, and a count is also what
// the screen can act on: nothing here reads the layout (karar 45).
const FITS = 8;
```

- [ ] **Step 2: Kalabalığı türet**

`const [busy, setBusy] = useState(false);` satırının altına:

```jsx
  const crowded = projects.length > FITS;
```

- [ ] **Step 3: Ekranı bir ekran boyuna indir ve gövdeyi sar**

`minHeight: "100vh"` → `height: "100vh"`, ve gövde:

```jsx
      {/* The header stays put and the projects move under it, the way the app's other four screens
          are built (karar 44). minHeight:0 is what lets the box be shorter than its grid: a flex
          child defaults to min-height:auto and would grow instead of scrolling. */}
      <div style={{ flex: 1, position: "relative", minHeight: 0 }}>
        <div data-list className="qe-thin-scroll"
             style={{ height: "100%", overflowY: "auto", padding: "24px 32px",
                      boxSizing: "border-box" }}>
```

...eski gövdenin içeriği olduğu gibi... ve kapanışta:

```jsx
        </div>
        {crowded && <div data-fade style={FADE} />}
      </div>
```

- [ ] **Step 4: İki `width` çağrısını kaldır**

`<NameModal title="Yeni proje" ... width={400} .../>` ve `... width={380} .../>` → ikisinden de
`width` düşüyor. Yeni proje penceresinin başındaki `400` gerekçesi de gidiyor; yerine ölçünün neden
artık verilmediğini söyleyen tek satır.

- [ ] **Step 5: Onayın cümle sırasını çevir**

```jsx
          // What is running stops first, then what goes with the folder (Fark 9). The server
          // really does stop the production before the folder goes (madde 1).
          body={"Çalışan üretim durdurulur, kuyruktaki işler atılır. İçindeki tüm kareler — "
                + "fotoğraf, video ve ses dosyalarıyla birlikte — kalıcı olarak silinir. "
                + "Bu işlem geri alınamaz."}
```

- [ ] **Step 6: Koş**

Run: `npm test --prefix queen-editor/frontend`
Expected: `qe-thin-scroll` sınıfını isteyen test dışında hepsi yeşil — sınıf henüz `app.css`'te
yok ama testin baktığı `className`, dolayısıyla o da yeşil olur. Sekizin sekizi yeşil.

---

### Task 4: `app.css` — ince tutamak

**Files:**
- Modify: `queen-editor/frontend/src/shared/app.css`

- [ ] **Step 1: Kuralı yaz**

Dosyanın sonuna:

```css
/* The list's own handle instead of the window's (Fark 8). Only the WebKit pseudo-elements are
   written: the app runs in Colab's output frame, which is Chrome. A box with nothing to scroll
   draws no handle at all, which is what makes the mark appear only once the list has outgrown its
   area -- there is no condition to write. The track stays transparent so no groove is drawn down
   the edge of a list that fits. */
.qe-thin-scroll::-webkit-scrollbar {
  width: 6px;
}
.qe-thin-scroll::-webkit-scrollbar-track {
  background: transparent;
}
.qe-thin-scroll::-webkit-scrollbar-thumb {
  background: var(--border-strong);
  border-radius: 3px;
}
.qe-thin-scroll::-webkit-scrollbar-thumb:hover {
  background: var(--border-active);
}
```

---

### Task 5: Dört komut, derleme, commit

- [ ] **Step 1: Dört komutu da koş**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Expected: 384 / 474 / 709 / 533, hepsi yeşil.

- [ ] **Step 2: Derle**

```
npm run build --prefix queen-editor/frontend
```

- [ ] **Step 3: Yol haritasının 24. satırını işaretle ve sayacı ilerlet**

`**Durum:** 23/31` → `**Durum:** 24/31`; 24. satırın **İş** hücresi `✅` ile başlar ve fark 5'in
kararı satıra not düşer.

- [ ] **Step 4: Commit**

```bash
git add docs/superpowers/specs/2026-08-21-queen-editor-v14-gorev-24-proje-ekrani-uygulama-design.md docs/superpowers/plans/2026-08-21-queen-editor-v14-gorev-24-uygulama.md docs/superpowers/plans/2026-08-20-queen-editor-v14-roadmap.md queen-editor/frontend/src queen-editor/frontend/dist
git commit -m @'
feat(queen-editor): the projects screen finds its measures
'@
```

Çift tırnak yok, amend yok.
