# v14 Görev 26 — Kuyruk panelinin görsel hizalaması: UYGULAMA döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `c342b0a` ile kırmızı duran on testi yeşile çevirmek — başlığın ayracı ve üçüncü hâli,
sayının rengi, duraklatılırken nokta, tamamlandı cümlesi, hata kartının yazısı ve doğduğu an,
beklerken boşaltma.

**Architecture:** Tek dosya: `QueuePanel.jsx`. Motor açılmıyor.

**Tech Stack:** React 18, vitest; Vite build.

**Spec:** [uygulama turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-26-kuyruk-hizalamasi-uygulama-design.md)

## Global Constraints

- **Test yazılmıyor.** Testler `c342b0a`'da.
- **Derlenmiş çıktı bu commit'e giriyor.**
- Yorumlar **İngilizce** ve **neden**i söylüyor; ekran metni **Türkçe**.
- Commit mesajında **çift tırnak yok**, ve **amend yok**.
- Komut: dört satır, birebir, boru yok.

## File Structure

| Dosya | İşlem |
|---|---|
| `frontend/.../photo_generation/QueuePanel.jsx` | yedi fark |
| `frontend/dist/**` | derlenir |

---

### Task 1: Tür kartı — başlık ve sayı

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/QueuePanel.jsx`

- [ ] **Step 1: Başlığın üç hâlini yaz**

`KindCard` içinde, `missing` zaten hesaplanıyor:

```jsx
        <Note size={12} style={{ color: alive ? "var(--ink-2)" : "var(--ink-3)" }}>
          {/* Three states, three words (Fark 41). "sırada" says a turn is coming; a kind with no
              producer cannot have one until something lands on the machine. */}
          {kind.title} — {alive ? "üretiliyor" : missing ? "bekliyor" : "sırada"}
        </Note>
```

- [ ] **Step 2: Sayının rengini duruma bağla**

```jsx
        {/* The accent stays on the heading row, where the dot is: three numbers in the same loud
            colour made the panel one big counter and said nothing about which one is moving
            (Fark 42). */}
        <Mono size={26} style={{ color: alive ? "var(--ink)" : "var(--ink-3)" }}>{owed}</Mono>
```

- [ ] **Step 3: Koş**

Run: `npm test --prefix queen-editor/frontend`
Expected: üç başlık testi ve sayı testi yeşil.

---

### Task 2: Koşu kartı — duraklatılırken ve bitince

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/QueuePanel.jsx`

- [ ] **Step 1: `DOT.pausing`'i soluklaştır**

```jsx
  // Still beating while the pause is on its way -- the engine is still turning -- but no longer in
  // the colour that means work is flowing (Fark 43).
  pausing: { color: "var(--ink-3)", alive: true },
```

- [ ] **Step 2: Başlığın rengine duraklatılıyor hâlini ekle**

```jsx
          <Mono size={12} style={{ color: state === "stopped" ? "var(--danger)"
            : state === "done" ? "var(--ok)"
            : state === "pausing" ? "var(--ink-3)" : "var(--ink-2)" }}>{TITLE[state]}</Mono>
```

- [ ] **Step 3: Tamamlandı cümlesini soluklaştır**

```jsx
        {state === "done" ? (
          // Good news only: what failed has a card of its own, and one sentence cannot carry both.
          // The heading is what carries the news; this line is a fact under it (Fark 44).
          <Note size={12} style={{ color: "var(--ink-3)" }}>{job.done} kare üretildi</Note>
```

- [ ] **Step 4: Koş**

Run: `npm test --prefix queen-editor/frontend`
Expected: nokta ve tamamlandı testleri yeşil.

---

### Task 3: Hata kartı ve boşaltma

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/QueuePanel.jsx`

- [ ] **Step 1: Kartın doğma koşulunu daralt, düğmenin yazısını kısalt**

```jsx
      {/* Its own card, outside the run's -- and only once the queue is through (Fark 46): a total
          that is still growing is not a total, and every red frame is already red in the gallery
          with a Tekrar dene of its own. */}
      {failed > 0 && state === "done" && (
```

...ve düğmenin içi:

```jsx
            <Icon.Regen /> Tekrar dene
```

- [ ] **Step 2: `canClear`'a bekleme hâlini ekle**

```jsx
  // The queue can only be emptied when nothing is being rendered: a frame in flight has no line in
  // the log yet, so it would read as owed and get pulled out from underneath the worker. A queue
  // waiting for a producer has nothing in hand either, so the way out belongs there too (Fark 47).
  const canClear = (paused || halted || abandoned || Boolean(waitingFor)) && owed > 0;
```

- [ ] **Step 3: Koş**

Run: `npm test --prefix queen-editor/frontend`
Expected: 547'nin 547'si yeşil.

---

---

### Koşuda çıkan tuzak

**Başlığı başka bir dosyadaki test de okuyormuş.** `SidePanel.test.jsx`'in
`swaps the panel when another icon is pressed` testi, kuyruk panelinin açıldığını
`"Foto · üretiliyor"` metninden doğruluyordu — bir kablolama testi, ama kanıtı komşunun metni.
Ayraç değişince düştü ve tireye çevrildi.

Kırmızı tur bunu listelemeliydi: bir ekran metni değişecekse o metin **bütün** test dosyalarında
aranır, yalnız kendi dosyasında değil.

---

### Task 4: Dört komut, derleme, commit

- [ ] **Step 1: Dört komutu da koş**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Expected: 384 / 474 / 709 / 547, hepsi yeşil.

- [ ] **Step 2: Derle**

```
npm run build --prefix queen-editor/frontend
```

- [ ] **Step 3: Yol haritasının 27. satırını işaretle ve sayacı ilerlet**

`**Durum:** 25/31` → `**Durum:** 26/31`; 27. satırın **İş** hücresi `✅` ile başlar ve 47–49.
kararlar satıra not düşer. **26. satır işaretlenmiyor** — o madde kullanıcının kararını bekliyor.

- [ ] **Step 4: Commit**

```bash
git add docs/superpowers/specs/2026-08-21-queen-editor-v14-gorev-26-kuyruk-hizalamasi-uygulama-design.md docs/superpowers/plans/2026-08-21-queen-editor-v14-gorev-26-uygulama.md docs/superpowers/plans/2026-08-20-queen-editor-v14-roadmap.md queen-editor/frontend/src queen-editor/frontend/dist
git commit -m @'
feat(queen-editor): the queue panel finds its tones
'@
```

Çift tırnak yok, amend yok.
