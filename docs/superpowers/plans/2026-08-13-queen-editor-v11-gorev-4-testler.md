# v11 Görev 4 — seçim kalkınca halkalar da kalkar: TEST döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Dört test eklemek; ikisi kırmızı, ikisi yeşil. Kod bu döngüde değişmiyor.

**Architecture:** Testler seçim modunu karonun sınıfından okuyor — CSS'in halkayı gösterirken
dayandığı sınıf. Seçimin boşalmasının iki yolu (kareyi bırakmak, listeyi boşaltan düğme) ayrı ayrı
sınanıyor.

**Tech Stack:** vitest + @testing-library/react, jsdom.

**Tasarım:** [test spec'i](../specs/2026-08-13-queen-editor-v11-gorev-4-testler-design.md)

## Global Constraints

- **Kod değişmiyor.** `Gallery.jsx` bu commit'te olduğu gibi kalır; `dist/` yeniden derlenmez.
- **Kırmızı bırakılır.**
- Test adları ve yorumlar **İngilizce**; ekrandan okunan metinler Türkçe.
- Commit mesajında **çift tırnak yok**.
- Test komutu: `npm test --prefix queen-editor/frontend`

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `.../photo_generation/Gallery.test.jsx` | seçim modunun ne zaman açık olduğu | 4 test eklenir, 1 yorum düzeltilir |

---

### Task 1: Modun seçimle başlayıp seçimle bittiğini yaz

**Files:**
- Test: `queen-editor/frontend/src/features/photo_generation/Gallery.test.jsx`

**Interfaces:**
- Consumes: `renderGallery()`, `tileOf()`, `checkOf()`, `photoOf()`, `FRAMES`.
- Produces: yok.

- [ ] **Step 1: Yanlışlaşan yorumu düzelt**

`"takes the bar away when the selection is emptied"` testinde:

```js
    fireEvent.click(photoOf("1_a.png"));  // deselect: the bar goes, and so does the mode
```

İddia değişmiyor — çubuğun gitmesi hâlâ doğru. Değişen, satırın neden orada olduğunu anlatan cümle.

- [ ] **Step 2: Dört testi seçim describe'ının sonuna ekle**

```js
  // The mode is the selection: rings on the cards while there is one, nothing while there is not.
  // It used to outlive the selection, which left a gallery covered in rings and a bar that had
  // already gone -- no way to tell whether a selection was still open (2026-08-13).
  const inSelectMode = () => document.querySelectorAll(".qe-tile--selecting").length;

  it("puts the cards in selection mode as soon as one is picked", () => {
    renderGallery();

    fireEvent.click(checkOf("1_a.png"));

    expect(inSelectMode()).toBe(FRAMES.length);
  });

  it("takes the cards out of selection mode when the last one is let go", () => {
    renderGallery();
    fireEvent.click(checkOf("1_a.png"));

    fireEvent.click(checkOf("1_a.png"));

    expect(inSelectMode()).toBe(0);
  });

  it("takes the cards out of selection mode on cancel", () => {
    renderGallery();
    fireEvent.click(checkOf("1_a.png"));

    fireEvent.click(screen.getByText("Vazgeç"));

    expect(inSelectMode()).toBe(0);
  });

  it("takes the cards out of selection mode when the whole list is emptied", () => {
    // Emptying the selection has two doors -- letting the last card go, and the button that clears
    // the list -- and they are different lines of code.
    renderGallery();
    fireEvent.click(checkOf("1_a.png"));
    fireEvent.click(screen.getByText("Tümünü seç"));

    fireEvent.click(screen.getByText("Tümünü seç"));

    expect(inSelectMode()).toBe(0);
  });
```

`inSelectMode()` sınıfı sayıyor: mod açıkken her karo o sınıfı taşıyor, kapalıyken hiçbiri.

- [ ] **Step 3: İkisinin düştüğünü, ikisinin geçtiğini gör**

Run: `npm test --prefix queen-editor/frontend`
Expected: `"takes the cards out of selection mode when the last one is let go"` ve
`"...when the whole list is emptied"` düşer (`expected 3 to be 0`); ötekiler geçer.

---

### Task 2: Kırmızıyı doğrula ve commit'le

- [ ] **Step 1: Tam ön yüz takımı**

Run: `npm test --prefix queen-editor/frontend`
Expected: 314 + 4 = 318; 2 düşen, 316 geçen.

- [ ] **Step 2: Kaynak koda dokunulmadığını doğrula**

Run: `git status --short`
Expected: yalnız `Gallery.test.jsx` ve `docs/superpowers`.

- [ ] **Step 3: Commit**

```bash
git add queen-editor/frontend/src docs/superpowers
git commit -F - <<'EOF'
test(queen-editor): make the selection mode end with the selection

TWO OF THESE FOUR TESTS FAIL ON PURPOSE. The fix is the next commit.

Letting the last selected card go empties the selection, and the bar goes with
it -- but the mode stays open, so every card keeps its ring and nothing on
screen says whether a selection is still being made. That was a deliberate
choice, written into a test comment as the mode stays open, the bar goes. Using
it showed it was the wrong one.

Two tests fail: emptying the selection by letting the last card go, and by the
button that clears the list -- two different lines of code, so two tests. Two
pass already, and are here so the fix cannot take the whole mode away instead:
one card picked still puts every card in the mode, and cancel still ends it.

The tests read the class the stylesheet keys the rings off, not the rings: jsdom
applies no stylesheet. A wrong class means a wrong ring; a right class with
broken CSS is a gap these tests cannot close.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** H1→birinci test · H2→ikinci · H3→üçüncü · H4→dördüncü · yanlışlaşan yorum→Task 1
Step 1. Eksik yok.

**Beklenen kırmızı sayısı:** 2. Diğer ikisinin geçmesi spec'te gerekçeli — implementasyonun modu
tümden kaldırarak "düzeltmesini" engelliyorlar.

**Kırılganlık:** `inSelectMode()` `document.querySelectorAll` ile sayıyor; `renderGallery` her testte
tek galeri kuruyor, dolayısıyla sayım o galeriye ait. Birden çok galeri kuran bir test yazılırsa bu
yardımcı yanıltır — bugün öyle bir test yok.
