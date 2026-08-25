# v14 Görev 14 — Detaydan dönünce galerinin yerinde durması: TEST döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Galerinin bırakıldığı yerde durmasını altı testle yazmak ve kırmızı commit etmek. Kaynak
kodda tek satır değişmiyor.

**Architecture:** Üç dosya, iki konu. Kayma yeri kendi kancasında ve ekranın kendisinde; resimlerin
hatırlanması karonun kendi dosyasında.

**Tech Stack:** React 18 + vitest + @testing-library/react.

**Spec:** [test turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-14-galerinin-yeri-testler-design.md)

## Global Constraints

- **Bu tur yalnız test yazar.** `frontend/src` altındaki kaynak dosyalar değişmiyor.
- Test adları ve yorumlar **İngilizce**; ekran metni **Türkçe**.
- Commit mesajında **çift tırnak yok**, ve **amend yok**.
- Komut: dört satır, birebir, boru yok.
- `skip` / `xfail` yok.
- Henüz olmayan adlar: `features/photo_generation/useKeptScroll.js` (`useKeptScroll`),
  `shared/shown_pictures.js` (`shownPictures`), ve kaydırma kutusundaki `data-scroll`.
  İlk ikisi yeni test dosyalarının başında içe aktarıldığı için **o dosyalar toplanamıyor**;
  vitest bunu dosya başına yapar, yani öbür takım dosyaları koşmaya devam ediyor.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `.../photo_generation/useKeptScroll.test.jsx` | kayma yerinin belleği | **yeni**, 3 test |
| `.../photo_generation/TileImage.test.jsx` | gösterilmiş resim | 2 test + `beforeEach` |
| `.../photo_generation/ProjectScreen.test.jsx` | ekranın kendisi | 1 test |

---

### Task 1: Kayma yerinin belleği

**Files:**
- Create: `queen-editor/frontend/src/features/photo_generation/useKeptScroll.test.jsx`

**Interfaces:**
- Consumes: `useKeptScroll(project) -> ref` — henüz yok. Döndürdüğü ref kaydırma kutusuna takılıyor;
  kanca kutunun `scrollTop`'unu sökülürken saklıyor, kurulurken geri koyuyor.

- [ ] **Step 1: Dosyayı yaz**

```jsx
import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { useKeptScroll } from "./useKeptScroll.js";

// A box standing in for the gallery's scroll container: the hook only ever asks it for scrollTop
// and gives it back, so nothing else about it matters. jsdom keeps the value it is given -- it does
// no layout, so there is nothing to clamp it against.
function Box({ project }) {
  return <div data-box ref={useKeptScroll(project)} />;
}

const boxOf = () => document.querySelector("[data-box]");

describe("useKeptScroll", () => {
  it("starts a gallery it has never seen at the top", () => {
    render(<Box project="hiç görülmemiş" />);

    expect(boxOf().scrollTop).toBe(0);
  });

  it("brings the box back to where it was left", () => {
    const first = render(<Box project="düğün" />);
    boxOf().scrollTop = 640;

    first.unmount();
    render(<Box project="düğün" />);

    // The whole of the item: what the user left is what they come back to.
    expect(boxOf().scrollTop).toBe(640);
  });

  it("keeps one project's place out of another's", () => {
    const first = render(<Box project="nikah" />);
    boxOf().scrollTop = 320;
    first.unmount();

    render(<Box project="kına" />);

    expect(boxOf().scrollTop).toBe(0);
  });
});
```

- [ ] **Step 2: Takımı koştur**

Run: `npm test --prefix queen-editor/frontend`
Expected: dosya toplanamıyor — `useKeptScroll.js` yok.

---

### Task 2: Gösterilmiş resim

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/TileImage.test.jsx`

**Interfaces:**
- Consumes: `shared/shown_pictures.js`'in `shownPictures` kümesi — henüz yok.

- [ ] **Step 1: İçe aktarma ve temizlik**

`fileUrl` içe aktarmasının altına:

```jsx
import { shownPictures } from "../../shared/shown_pictures.js";
```

ve `beforeEach` satırı ikisini de temizliyor:

```jsx
beforeEach(() => {
  queue.forget();
  // A picture that has been on screen once is remembered for the session, so a suite whose tests
  // all name the same file has to start each of them from nothing.
  shownPictures.clear();
});
```

- [ ] **Step 2: İki testi yaz**

Dosyanın son testinin altına:

```jsx
  it("keeps a picture it has already shown when the tile is built again", () => {
    const view = stubObserver();
    const first = render(<TileImage project="düğün" file="1_a.png" />);
    view.near();
    grant();
    fireEvent.load(picture());
    first.unmount();

    stubObserver();
    render(<TileImage project="düğün" file="1_a.png" />);

    // Neither gate again: not the viewport, not the queue. The bytes are in the browser's cache,
    // so what the second wait would cost is the picture blinking off the screen (İstek 1.2).
    expect(sourceOf()).toBe(fileUrl("düğün", "1_a.png"));
    expect(queue.waiting).toHaveLength(1);
  });

  it("does not remember a picture that never arrived", () => {
    const view = stubObserver();
    const first = render(<TileImage project="düğün" file="1_a.png" />);
    view.near();
    grant();
    fireEvent.error(picture());
    first.unmount();

    stubObserver();
    render(<TileImage project="düğün" file="1_a.png" />);

    expect(sourceOf()).toBeNull();
  });
```

- [ ] **Step 3: Takımı koştur**

Run: `npm test --prefix queen-editor/frontend`
Expected: bu dosya da toplanamıyor — `shown_pictures.js` yok.

---

### Task 3: Ekranın kendisi

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/ProjectScreen.test.jsx`

**Interfaces:**
- Consumes: kaydırma kutusundaki `data-scroll` — henüz yok.

- [ ] **Step 1: Testi yaz**

Dosyanın sonuna, yeni bir blok olarak:

```jsx
describe("ProjectScreen — coming back to where the gallery was", () => {
  const boxOf = () => document.querySelector("[data-scroll]");

  it("opens the gallery at the place the screen was left at", () => {
    const first = renderScreen("kayma");
    boxOf().scrollTop = 640;

    first.unmount();
    renderScreen("kayma");

    // The list was already remembered across mounts; this is the other half of standing still.
    expect(boxOf().scrollTop).toBe(640);
  });
});
```

- [ ] **Step 2: Dört komutu koştur**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Expected: queen-agent'ın ikisi yeşil (384 / 474), queen-editor python yeşil (694). queen-editor
frontend'de iki dosya toplanamıyor ve `ProjectScreen.test.jsx`'te 1 kırmızı.

---

### Task 4: Kırmızı commit

- [ ] **Step 1: Commit**

```bash
git add queen-editor docs/superpowers
git commit -F - <<'EOF'
test(queen-editor): the gallery stands still while a frame is looked at

Six tests for what a step in and out of a frame's page must not cost. The scroll box comes
back to the place it was left at, and it is kept per project, so one gallery's place is
never another's. A gallery nobody has scrolled opens at the top.

A picture that has already been on screen is drawn at once when its tile is built again --
neither gate, not the viewport and not the queue. The bytes are in the browser's cache
either way; what the second wait costs is the photos blinking off the screen, which is what
the user reported. A picture that never arrived is not remembered: there is nothing to keep.

The list itself was already remembered across mounts, so nothing here touches it. What was
missing was the other half of standing still.

Two of the three files import modules that do not exist yet, so those two do not collect.
vitest does that per file, so the rest of the suite still runs.

queen-agent green (384 / 474). queen-editor python green (694). Frontend: one red and two
files that do not collect.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** spec'in altı testi Task 1 (1–3), Task 2 (4–5), Task 3 (6).

**Tip tutarlılığı:** `useKeptScroll(project)` her yerde bir ref döndürüyor ve doğrudan bir düğüme
takılıyor; `shownPictures` her yerde bir `Set`.

**Kontrol edilen tuzak:** 4 numaralı test ikinci kurulumda `queue.waiting`'in **büyümediğini** de
ölçüyor. Yalnız `src`'ye bakmak, karonun sırayı beklemeden çizilip yine de bir bilet almasını
kaçırırdı — o bilet, gerçekten bekleyen bir karonun sırasını yerdi.

**Kontrol edilen tuzak 2:** 4 ve 5 numara ikinci kurulumdan önce gözlemciyi yeniden kuruyor:
`stubObserver` her çağrıda yeni bir sınıf koyuyor ve `view.near()` sonuncusunu sürüyor.

**Kontrol edilen tuzak 3:** 3 numaralı test iki **farklı** proje kullanıyor, ve ikisi de öbür
testlerin adlarından ayrı — bellek modül düzeyinde ve dosya boyunca yaşıyor.

**Kontrol edilen tuzak 4:** `ProjectScreen.test.jsx`'in kendi notu zaten diyor ki galeri mount'lar
arasında hatırlanıyor, o yüzden test kimsenin kullanmadığı bir proje adı alıyor.
