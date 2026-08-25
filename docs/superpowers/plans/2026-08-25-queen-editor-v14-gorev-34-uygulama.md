# v14 Görev 34 — Açık panel geri dönüşte yerinde kalır: UYGULAMA döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Önceki commit'in iki kırmızı testini yeşile döndürmek, iki tutucuyu yeşil bırakarak.

**Architecture:** Tek dosya, üç ekleme: modül seviyesinde proje anahtarlı bir depo, başlangıcı
okuyan küçük bir fonksiyon, ve değişimi yazan bir effect. Bileşenin dışa açık yüzü değişmiyor.

**Tech Stack:** React 18, Vite, Vitest + jsdom.

**Spec:** [Görev 34 uygulama spec'i](../specs/2026-08-25-queen-editor-v14-gorev-34-uygulama-design.md)

## Global Constraints

- **Test dosyası değişmiyor.** `SidePanel.test.jsx` bir önceki commit'te ne yazıldıysa o kalır.
- **Depo `has()` ile sorulur.** Kapalı sütun `null`, "hatırlanmıyor" da `null`; `?? "photo"` yazmak
  kullanıcının bilerek kapattığı sütunu her dönüşte açardı.
- **Depo proje anahtarlı.**
- **Yeni prop yok.** `ProjectScreen` ve `App` bu döngüde hiç açılmıyor.
- **`shownProject` benzeri bir ref eklenmiyor** — gerekçesi spec'te; test edilmeyen kod olurdu.
- Dil: kod ve yorumlar **İngilizce**; commit mesajı **İngilizce**; belgeler **Türkçe**.
- Commit mesajında **çift tırnak yok**.
- Test: `npm test --prefix queen-editor/frontend` · Derleme:
  `npm run build --prefix queen-editor/frontend` · **`dist` aynı commit'e girer.**

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `queen-editor/frontend/src/features/photo_generation/SidePanel.jsx` | sağ sütun ve hangi panelin açık olduğu | depo + başlangıç + yazan effect |

Tek dosya. Depo, onu okuyan tek bileşenin yanında duruyor — `useKeptScroll`'un `KEPT`'i ve
`useModels`'in yuvası da öyle. Ayrı bir modüle çıkarmak, tek tüketicisi olan bir şeyi paylaşılıyor
gibi göstermek olurdu.

---

### Task 1: Depo, başlangıç ve yazan effect

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/SidePanel.jsx`

**Interfaces:**
- Consumes: `SidePanel`'in bugün zaten aldığı `project` prop'u ve `useState`/`useEffect`.
- Produces: dışarıya hiçbir şey. Depo dosyanın içinde kalır; `SidePanel`'in prop listesi
  değişmez. Testlerin gördüğü tek şey sütunun hangi panelle doğduğu.

- [ ] **Step 1: `useEffect`'i içe al**

Dosyanın ilk satırı bugün:

```jsx
import { useState } from "react";
```

Yerine:

```jsx
import { useEffect, useState } from "react";
```

- [ ] **Step 2: Depoyu ve başlangıcı yaz**

`const PANELS = [...]` dizisinin **üstüne**, `GLYPH` sabitinin altına:

```jsx
// Which panel each project's column was last showing. Opening a frame's detail replaces the whole
// project screen, so this component is torn down and built again on every step in and out; without
// this the column would reopen on the form every time (madde 34). Keyed by project: which panel is
// being watched is the user's work in one project, never a fact about the app.
//
// Memory only, like the gallery's own stores: a reload opens the column on the form again.
const REMEMBERED = new Map();

// Where a mount starts. Asked with has() rather than read with a fallback, because a closed column
// is null and so is having nothing remembered -- `?? "photo"` here would reopen a column the user
// closed on purpose, which is this item's own mistake in the other direction.
function opening(project) {
  return REMEMBERED.has(project) ? REMEMBERED.get(project) : "photo";
}
```

- [ ] **Step 3: Başlangıcı depodan al ve değişimi yaz**

Bugünkü hâli:

```jsx
  // Which panel is open is this column's own business: neither the project screen nor the server
  // has a reason to know it. null means none of them -- pressing the open panel's own icon closes
  // it and gives the width back to the gallery, the way a code editor's side bar behaves.
  const [open, setOpen] = useState("photo");
  const toggle = (id) => setOpen((shown) => (shown === id ? null : id));
  const current = PANELS.find((panel) => panel.id === open);
```

Yerine:

```jsx
  // Which panel is open is this column's own business: neither the project screen nor the server
  // has a reason to know it. null means none of them -- pressing the open panel's own icon closes
  // it and gives the width back to the gallery, the way a code editor's side bar behaves.
  const [open, setOpen] = useState(() => opening(project));
  const toggle = (id) => setOpen((shown) => (shown === id ? null : id));
  const current = PANELS.find((panel) => panel.id === open);

  // Whatever the column becomes is what a later mount starts from -- closed included. One effect
  // rather than a write inside toggle: that one is a functional update, and a store written from
  // inside it would be a side effect where there must be none.
  useEffect(() => {
    REMEMBERED.set(project, open);
  }, [project, open]);
```

- [ ] **Step 4: Takımın tamamen yeşil olduğunu gör**

Run: `npm test --prefix queen-editor/frontend`

Expected: **0 failed**, 573 tests. Özellikle:

- `SidePanel.test.jsx` **23 tests, 0 failed** — iki kırmızı yeşile döndü, iki tutucu yeşil kaldı.
- `App.test.jsx`, `ProjectScreen.test.jsx`, `QueuePanel.test.jsx` 31–33'ten yeşil.

Tutuculardan biri düşerse dur ve sebebini oku: *still opens on the form panel…* düşerse depo `null`
ile başlatılmış, *opens another project on its own default* düşerse anahtar unutulmuş demektir.

---

### Task 2: Derle, doğrula, commit'le

**Files:**
- Değişiklik yok; bu görev derleme, doğrulama ve kayıt.

- [ ] **Step 1: Ön yüzü derle**

Run: `npm run build --prefix queen-editor/frontend`

Expected: hatasız biter ve `queen-editor/frontend/dist/` tazelenir.

- [ ] **Step 2: Arka yüz takımının da yeşil olduğunu gör**

Run: `python -m pytest queen-editor -q`

Expected: **711 passed.** Bu döngü arka yüze hiç dokunmuyor; koşulma sebebi CLAUDE.md'nin iki sabit
satırı.

- [ ] **Step 3: Değişen her şeyi gör**

Run: `git status --short`

Expected: `SidePanel.jsx`, `dist/` altındakiler ve `docs/superpowers` altındaki iki yeni belge.
`SidePanel.test.jsx` bu listede **olmamalı.**

- [ ] **Step 4: Commit**

```bash
git add queen-editor/frontend/src queen-editor/frontend/dist docs/superpowers
git commit -F - <<'EOF'
feat(queen-editor): the column comes back on the panel it was left on

Watching the queue and then looking at a frame cost the panel: coming back, the
column was on the photo form again whatever had been open. The address swaps the
whole screen, React drops the state of a component that no longer exists, and
the new instance opened on its default.

The column now starts from what this project's column was last showing. Closed
is kept too -- a user who closed it gave that width to the gallery on purpose.
That is also where the store could go wrong quietly, because a closed column is
null and so is having nothing remembered: the store is asked with has, never
read with a fallback, or the one column the user meant to shut would be the one
that always reopened.

Keyed by project: which panel is being watched is the user's work in one
project. Memory only, like the six stores before it -- a reload opens the column
on the form again.

No guard against the project changing under a live column, unlike the two hooks
that carry one. Reaching another project means going through the project list,
and that screen tears this one down; the column never stays up across two
projects. Their guard exists because the wrong record would have been shown and
then saved. Here the worst case is a stale panel.

This is the seventh store of the run and the last of the four items the tour
opened. What is left of them is the typed text, which is item 35.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:**

| Spec'te ne diyor | Planda nerede |
|---|---|
| Depo modül seviyesinde, proje anahtarlı | Task 1 Step 2 |
| Başlangıç depodan | Task 1 Step 3 |
| Kapalı `null` tuzağı → `has()` | Task 1 Step 2'nin `opening()` fonksiyonu ve yorumu |
| Değişimi effect yazar | Task 1 Step 3 |
| `shownProject` ref'i yok | Global Constraints ve commit mesajı |
| Ömür bellek kadar | Task 1 Step 2'nin yorumu |
| Derlenmiş çıktı aynı commit'te | Task 2 |

Spec'te olup planda karşılığı olmayan madde yok.

**Yer tutucu yok:** Her adımda çalıştırılacak gerçek kod ve gerçek komut var.

**Ad tutarlılığı:** `REMEMBERED` ve `opening()` yalnız bu dosyada geçiyor ve iki adımda aynı yazımla
kullanılıyor. `opening()` adı `useProjectSettings`'in aynı işi yapan fonksiyonuyla bilerek aynı —
iki dosyada aynı soruyu soran iki fonksiyonun aynı adı taşıması, okuyanın ikisini bir kalıp olarak
görmesini sağlıyor. `REMEMBERED` de öyle; ikisi ayrı modülde durduğu için çakışmıyorlar.

**Bilerek dışarıda:** `PhotoDetail` ve `ExportScreen`. İkisinin de sağ sütunu yok, dolayısıyla
hatırlayacakları bir panel de yok.
