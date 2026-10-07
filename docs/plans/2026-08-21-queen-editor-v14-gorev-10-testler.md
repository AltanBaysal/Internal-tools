# v14 Görev 10 — Toplu kart taşıma: TEST döngüsü (test planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Seçimin sürüklemeye katılmasını tarif eden dokuz testi yazmak ve kırmızı bırakmak.

**Architecture:** Tek test dosyası, tek yeni blok. Beş karelik bir galeri, çünkü üç kare dağınık bir
seçimin arasında kalan kartları göstermeye yetmiyor.

**Tech Stack:** vitest, @testing-library/react.

**Spec:** [test turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-10-toplu-tasima-testler-design.md)

## Global Constraints

- **Yalnız test dosyası değişiyor.** `Gallery.jsx` bu turda el değmeden kalıyor.
- **`skip` / `xfail` yok.**
- Test adları ve yorumları **İngilizce**; ekranda aranan metinler **Türkçe**.
- Commit mesajında **çift tırnak yok**, ve **amend yok**.
- Komutlar dört satır, birebir, boru yok.
- **`dist` bu turda derlenmiyor.**
- **Mevcut sürükleme testleri değişmiyor.** Tek kartın kuralı aynı kalıyor; değişirse uygulama
  yanlış genellemiş demektir.

## Galerinin yönü ve beklenen sonuçlar

`FIVE = [4_a, 3_a, 2_a, 1_a, 0_a]` — galeri en yeniden eskiye. Kural: taşınanlar çıkarılır, blok
`to` indeksinden başlayacak şekilde yerleştirilir.

| Seçim | Sürüklenen → hedef | Sonuç |
|---|---|---|
| 4_a, 3_a | 4_a → 2_a (`to`=2) | `2_a, 1_a, 4_a, 3_a, 0_a` |
| 0_a sonra 4_a | 4_a → 2_a (`to`=2) | `3_a, 2_a, 4_a, 0_a, 1_a` |
| 4_a, 2_a, 0_a | 4_a → 3_a (`to`=1) | `3_a, 4_a, 2_a, 0_a, 1_a` |
| 4_a, 3_a | 0_a → 2_a (`to`=2) | `4_a, 3_a, 0_a, 2_a, 1_a` |
| 4_a, 3_a | 3_a → 4_a (`to`=0) | değişmiyor — çağrı yok |

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `frontend/src/features/photo_generation/Gallery.test.jsx` | galerinin nöbeti | bir blok, dokuz test |

---

### Task 1: Bloğun kendisi

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/Gallery.test.jsx`

**Interfaces:**
- Consumes: `done`, `tileOf`, `checkOf`, `dragTile`, `renderGallery` — hepsi dosyanın tepesinde.

- [ ] **Step 1: Bloğu yaz**

`Gallery ordering` bloğunun hemen altına:

```jsx
describe("Gallery — dragging a selection", () => {
  // Five, not three: a scattered selection needs cards left standing between its members, and with
  // three there is only one such card.
  const FIVE = [done("4_a.png"), done("3_a.png"), done("2_a.png"), done("1_a.png"),
                done("0_a.png")];

  function selectAll(...names) {
    names.forEach((name) => fireEvent.click(checkOf(name)));
  }

  it("takes the whole selection along when one of its cards is dragged", () => {
    const onReorder = vi.fn();
    renderGallery({ frames: FIVE, onReorder });
    selectAll("4_a.png", "3_a.png");

    dragTile("4_a.png", "2_a.png");

    expect(onReorder).toHaveBeenCalledWith(["2_a", "1_a", "4_a", "3_a", "0_a"]);
  });

  it("keeps the block in the gallery's order, not the order it was clicked in", () => {
    // The selection is a list of presses; the sequence is the gallery's. Reading the presses would
    // reverse a block whenever the user picked its cards from the bottom up.
    const onReorder = vi.fn();
    renderGallery({ frames: FIVE, onReorder });
    selectAll("0_a.png", "4_a.png");

    dragTile("4_a.png", "2_a.png");

    expect(onReorder).toHaveBeenCalledWith(["3_a", "2_a", "4_a", "0_a", "1_a"]);
  });

  it("gathers a scattered selection where it was dropped and closes the gap behind it", () => {
    const onReorder = vi.fn();
    renderGallery({ frames: FIVE, onReorder });
    selectAll("4_a.png", "2_a.png", "0_a.png");

    dragTile("4_a.png", "3_a.png");

    expect(onReorder).toHaveBeenCalledWith(["3_a", "4_a", "2_a", "0_a", "1_a"]);
  });

  it("moves only the card that was dragged when it is not in the selection", () => {
    const onReorder = vi.fn();
    renderGallery({ frames: FIVE, onReorder });
    selectAll("4_a.png", "3_a.png");

    dragTile("0_a.png", "2_a.png");

    expect(onReorder).toHaveBeenCalledWith(["4_a", "3_a", "0_a", "2_a", "1_a"]);
  });

  it("leaves the selection where it was when an unselected card is dragged", () => {
    renderGallery({ frames: FIVE });
    selectAll("4_a.png", "3_a.png");

    dragTile("0_a.png", "2_a.png");

    expect(screen.getByText("2 seçili")).toBeTruthy();
  });

  it("lets a card be picked up at all while frames are selected", () => {
    // Until now dragging was switched off for the whole gallery as soon as anything was selected,
    // which is the reason the sequence could not be moved without breaking the selection first.
    renderGallery({ frames: FIVE });
    selectAll("4_a.png");

    expect(tileOf("4_a.png").getAttribute("draggable")).toBe("true");
  });

  it("puts the dragged look on every card in the block", () => {
    renderGallery({ frames: FIVE });
    selectAll("4_a.png", "3_a.png");

    fireEvent.dragStart(tileOf("4_a.png"));

    expect(tileOf("3_a.png").style.transform).toContain("rotate(-3deg)");
    expect(tileOf("2_a.png").style.transform).toBe("");
  });

  it("adds nothing to the screen while the block is moving", () => {
    // No count badge, no stack, no ghost card: the design asks for the single-card effect applied
    // to the selection and nothing more.
    renderGallery({ frames: FIVE });
    selectAll("4_a.png", "3_a.png");
    const before = document.querySelectorAll("[data-tile]").length;

    fireEvent.dragStart(tileOf("4_a.png"));

    expect(document.querySelectorAll("[data-tile]").length).toBe(before);
  });

  it("does not go to the server when the block lands where it already was", () => {
    // from and to differ here -- the second card of the block was dropped on the first -- and the
    // sequence still comes out unchanged. Comparing indices would miss it.
    const onReorder = vi.fn();
    renderGallery({ frames: FIVE, onReorder });
    selectAll("4_a.png", "3_a.png");

    dragTile("3_a.png", "4_a.png");

    expect(onReorder).not.toHaveBeenCalled();
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

Expected: üç takım yeşil. queen-editor'ün ön yüzünde **altı kırmızı** — 1, 2, 3, 6, 7 ve 9.

Doğuştan yeşil olan üçü ve sebepleri:

| Test | Neden bugün de geçiyor |
|---|---|
| 4 · seçili olmayan kart yalnız gidiyor | Bugünkü tek kart kuralı zaten bunu yapıyor. |
| 5 · seçim bozulmuyor | Sürükleme bugün de seçime dokunmuyor. |
| 8 · ekrana karo eklenmiyor | Bugün eklenen bir şey yok; nöbeti blok doğduktan sonra başlıyor. |

**`draggable`'ın testi engellemediğine dikkat:** `fireEvent.dragStart` sentetik olay üretiyor ve
jsdom `draggable="false"` olsa da işleyiciyi çağırıyor. Yani bu testler bugünkü **mantığı** ölçüyor,
tarayıcının sürüklemeye izin verip vermediğini değil. Onu ölçen tek test 6, ve o özniteliğe bakıyor.

---

### Task 2: Kırmızıyı commit et

- [ ] **Step 1: Sayıyı oku**

Ön yüzde 6 kırmızı, 3 doğuştan yeşil — yukarıdaki tabloya göre.

- [ ] **Step 2: Commit**

```bash
git add queen-editor docs/superpowers
git commit -F - <<'EOF'
test(queen-editor): a selected card carries the rest of the selection with it

Dragging is switched off for the whole gallery the moment anything is selected, so a
sequence can only be moved card by card -- and its own order is lost on the way. These
tests hand the selection to the drag: picking up one of its cards moves all of them, as
one block, in the gallery's own order.

A scattered selection lands side by side where it was dropped and the cards between it
close the gap. An unselected card still goes alone and leaves the selection untouched.

The block is the single card's rule with more than one element: everything moving is
lifted out, then put back starting at the slot's index. Written that way so the existing
single-card behaviour is not a special case of anything -- it stays exactly what it was.

The order the block keeps is the gallery's, not the order its cards were clicked in.

Nothing new is drawn: the dragged look spreads to the block, the slot indicator does not
change, and the number of tiles on screen stays what it was.

Going to the server is decided by comparing the sequence rather than the indices -- with
a block, dropping its second card on its first changes nothing and the two indices still
differ.

Six red. Three are born green: an unselected card already goes alone and already leaves
the selection be, and nothing is added to the screen today because there is no block
yet. Their watch starts once there is one.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** spec'in dokuz testi tek blokta, sırayla. 1. karar (bloğun genellemesi) 1–4.
testlerin beklenen dizilerinde; 4. karar 9. testte; 5. karar 7. testte; 7. karar 8. testte.

**Tip tutarlılığı:** `onReorder` her testte kimlik dizisi alıyor (`"4_a"`, uzantısız), bugünkü
sürükleme testlerindeki gibi. `dragTile` dosya adıyla çağrılıyor, çünkü karolar öyle bulunuyor.

**Kontrol edilen tuzak:** 2. test seçimi ters sırada tıklıyor. Yalnız düz sırada seçen testler,
`selected`'i olduğu gibi kullanan bir uygulamada da geçerdi.

**Kontrol edilen tuzak 2:** 7. test hem seçili bir kardeşin efekti aldığını hem seçili olmayanın
almadığını ölçüyor. Yalnız birincisi, efekti bütün karolara uygulayan bir uygulamada da geçerdi.

**Kontrol edilen tuzak 3:** 3. testin hedefi (`3_a`) seçili **değil**. Hedefi seçili bir karta
vermek, "boşluğu kapatan kartlar" iddiasını ölçemezdi.

**Kontrol edilen tuzak 4:** 4. ve 5. testler ayrı. Birleştirilseydi, seçimi temizleyip yine de doğru
sırayı bildiren bir uygulama yarı yeşil kalırdı.

**Değişmeyen:** `Gallery ordering` bloğunun iki sürükleme testi olduğu gibi duruyor. Uygulama turu
onları kırarsa, tek kartın kuralı yanlış genellenmiş demektir.
