# v11 Görev 5 — kare köşeleri yeniden dağıtılır: TEST döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Beş test; hepsi kırmızı. Kod bu döngüde değişmiyor.

**Architecture:** Dört test satır içi konumları okuyor (gerçek doğrulama), biri stil dosyasının
metnini okuyor (kuralın silinmesine karşı bekçi).

**Tech Stack:** vitest + @testing-library/react, jsdom, Node `fs` (stil dosyasını okumak için).

**Tasarım:** [test spec'i](../specs/2026-08-13-queen-editor-v11-gorev-5-testler-design.md)

## Global Constraints

- **Kod değişmiyor.** `Gallery.jsx`, `frame_status.jsx`, `app.css` bu commit'te olduğu gibi kalır.
- **Kırmızı bırakılır.**
- Test adları ve yorumlar **İngilizce**.
- Commit mesajında **çift tırnak yok**.
- Test komutu: `npm test --prefix queen-editor/frontend`

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `.../photo_generation/Gallery.test.jsx` | köşelerin kime ait olduğu | 1 test yeniden yazılır, 4 test eklenir |

---

### Task 1: Köşeleri yaz

**Files:**
- Test: `queen-editor/frontend/src/features/photo_generation/Gallery.test.jsx`

**Interfaces:**
- Consumes: `renderGallery()`, `tileOf()`, `checkOf()`, `pillOf()`, `MIXED`, `FRAMES`.
- Produces: `.qe-badge` sınıfı — implementasyonun uyacağı ad.

- [ ] **Step 1: Etiketin köşesini iddia eden testi yeniden yaz**

Mevcut *"keeps the pill in a corner of its own, so hovering a frame moves nothing in it"* testinin
yerine:

```js
  it("puts the state pill in the top left, where the design asks for it", () => {
    // It used to sit at the bottom because the select ring owned this corner and appeared under
    // the pointer, so the pill had to get out of the way. The ring moved to the other side
    // (2026-08-13), and the corner is the pill's again.
    renderGallery({ frames: MIXED, current: "3_a", running: true });

    expect(pillOf("4_a.png").style.top).toBe("6px");
    expect(pillOf("4_a.png").style.left).toBe("6px");
    expect(pillOf("4_a.png").style.bottom).toBe("");
  });
```

- [ ] **Step 2: Dört testi aynı describe'a ekle**

```js
  const badgeOf = (name) => tileOf(name).querySelector(".qe-badge");

  it("puts the select ring in the top right, opposite the pill", () => {
    renderGallery({ frames: MIXED, current: "3_a", running: true });

    expect(checkOf("4_a.png").style.top).toBe("6px");
    expect(checkOf("4_a.png").style.right).toBe("6px");
    expect(checkOf("4_a.png").style.left).toBe("");
  });

  it("leaves the order badge in the top right and gives it a name to be hidden by", () => {
    // The ring lands on the badge's corner, so one of them has to give way. The badge does -- what
    // is being looked at while picking frames is the pictures, not the numbering.
    renderGallery({ frames: MIXED, current: "3_a", running: true });

    expect(badgeOf("4_a.png").style.top).toBe("6px");
    expect(badgeOf("4_a.png").style.right).toBe("6px");
  });

  it("hides the number wherever the stylesheet shows the ring", () => {
    // A text check, and it says so: jsdom applies no stylesheet, so this catches the rule being
    // deleted, not the rule being wrong. The ring appears on hover and in selection mode, and the
    // number has to leave in both -- otherwise they sit on top of each other.
    const css = readFileSync(new URL("../../shared/app.css", import.meta.url), "utf-8");

    expect(css).toMatch(/\.qe-tile:hover \.qe-badge/);
    expect(css).toMatch(/\.qe-tile--selecting \.qe-badge/);
  });

  it("does not move the pill when the selection mode opens", () => {
    // The whole point of the new layout: something appearing is not something moving, so nothing
    // in the card shifts under the pointer.
    renderGallery({ frames: MIXED, current: null });
    const before = pillOf("4_a.png").style.top;

    fireEvent.click(checkOf("4_a.png"));

    expect(pillOf("4_a.png").style.top).toBe(before);
    expect(pillOf("4_a.png").style.top).toBe("6px");
  });
```

J5 `MIXED` kullanıyor çünkü `FRAMES`'in üçü de üretilmiş kare ve üretilmiş karenin etiketi yok —
okunacak bir şey olmazdı. İki iddia birlikte anlamlı: birincisi kımıldamadığını, ikincisi doğru
köşede kımıldamadığını söylüyor.

- [ ] **Step 3: Import'u ekle**

Dosyanın başına:

```js
import { readFileSync } from "node:fs";
```

- [ ] **Step 4: Beşinin de düştüğünü gör**

Run: `npm test --prefix queen-editor/frontend`
Expected: 5 düşen. Konum testleri `expected '' to be '6px'` diyor; CSS testi eşleşme bulamıyor;
`badgeOf` testi `Cannot read properties of null` diyor — o da beklenen, sınıf henüz yok.

---

### Task 2: Kırmızıyı doğrula ve commit'le

- [ ] **Step 1: Tam ön yüz takımı**

Run: `npm test --prefix queen-editor/frontend`
Expected: 318 + 4 = 322; 5 düşen, 317 geçen.

- [ ] **Step 2: Kaynak koda dokunulmadığını doğrula**

Run: `git status --short`
Expected: yalnız `Gallery.test.jsx` ve `docs/superpowers`.

- [ ] **Step 3: Commit**

```bash
git add queen-editor/frontend/src docs/superpowers
git commit -F - <<'EOF'
test(queen-editor): give each corner of a card one owner

THESE FIVE TESTS FAIL ON PURPOSE. The fix is the next commit.

The design puts the state pill in the top left. The code had moved it to the
bottom because the select ring owned that corner and appeared under the pointer,
so the pill had to jump out of the way -- movement inside a card the user only
pointed at. The ring goes to the opposite corner instead, and the order badge,
whose corner that is, leaves whenever the ring arrives: while picking frames one
looks at pictures, not at numbering.

Four tests read inline positions, which is real. The fifth reads the stylesheet
as text, and says so in its own comment: jsdom applies no stylesheet, so it
catches the rule being deleted and not the rule being wrong. The alternative --
hiding the number from JavaScript -- would have made half of it testable and
split one behaviour across two mechanisms, since the hover half can only live in
CSS anyway.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** J1→Task 1 Step 1 · J2, J3, J4, J5→Step 2. Eksik yok.

**Ad tutarlılığı:** `.qe-badge` sınıf adı hem `badgeOf()` seçicisinde hem CSS testinin aradığı
kurallarda geçiyor; implementasyon üçünü de aynı adla karşılamak zorunda.

**Kırılganlık:** CSS testi `import.meta.url`'e göre yol çözüyor; test dosyası
`src/features/photo_generation/` altında, stil `src/shared/app.css`, yani `../../shared/app.css`
doğru. Dosya taşınırsa test yolu bulamaz ve bunu yüksek sesle söyler — sessizce geçmez.
